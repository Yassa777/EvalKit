from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
import time

from evalkit.db.database import get_db
from evalkit.vector.base import VectorStore

class PGVectorStore(VectorStore):
    """PostgreSQL pgvector implementation."""
    
    def __init__(self):
        self.dimension = None
        self.table_name = "vectors"
        self.metadata_table = "vector_metadata"
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize pgvector store."""
        self.dimension = config.get("dimension", 1536)
        self.table_name = config.get("table_name", "vectors")
        self.metadata_table = config.get("metadata_table", "vector_metadata")
        
        async with get_db() as db:
            # Enable pgvector extension
            await db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            
            # Create vectors table
            await db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id SERIAL PRIMARY KEY,
                    embedding vector({self.dimension}),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create metadata table
            await db.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {self.metadata_table} (
                    id SERIAL PRIMARY KEY,
                    vector_id INTEGER REFERENCES {self.table_name}(id),
                    metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create index for similarity search
            await db.execute(text(f"""
                CREATE INDEX IF NOT EXISTS {self.table_name}_embedding_idx 
                ON {self.table_name} 
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100)
            """))
            
            await db.commit()
    
    async def add_vectors(
        self,
        vectors: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add vectors to the store."""
        if len(vectors) != len(metadata):
            raise ValueError("Number of vectors must match number of metadata entries")
        
        async with get_db() as db:
            vector_ids = []
            for i, (vector, meta) in enumerate(zip(vectors, metadata)):
                # Insert vector
                result = await db.execute(
                    text(f"""
                        INSERT INTO {self.table_name} (embedding)
                        VALUES (:embedding)
                        RETURNING id
                    """),
                    {"embedding": vector.tolist()}
                )
                vector_id = result.scalar()
                
                # Insert metadata
                await db.execute(
                    text(f"""
                        INSERT INTO {self.metadata_table} (vector_id, metadata)
                        VALUES (:vector_id, :metadata)
                    """),
                    {
                        "vector_id": vector_id,
                        "metadata": meta
                    }
                )
                
                vector_ids.append(str(vector_id))
            
            await db.commit()
            return vector_ids
    
    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        start_time = time.time()
        
        async with get_db() as db:
            # Build the query
            query = f"""
                WITH vector_matches AS (
                    SELECT 
                        v.id,
                        v.embedding <=> :query_vector as distance
                    FROM {self.table_name} v
                    ORDER BY v.embedding <=> :query_vector
                    LIMIT :k
                )
                SELECT 
                    vm.id,
                    vm.distance,
                    m.metadata
                FROM vector_matches vm
                JOIN {self.metadata_table} m ON m.vector_id = vm.id
            """
            
            # Add filter criteria if provided
            if filter_criteria:
                query += " WHERE "
                conditions = []
                for key, value in filter_criteria.items():
                    conditions.append(f"m.metadata->>'{key}' = :{key}")
                query += " AND ".join(conditions)
            
            # Execute query
            result = await db.execute(
                text(query),
                {
                    "query_vector": query_vector.tolist(),
                    "k": k,
                    **filter_criteria or {}
                }
            )
            
            rows = result.fetchall()
            search_time = time.time() - start_time
            
            return [
                {
                    "id": str(row[0]),
                    "distance": float(row[1]),
                    "metadata": row[2],
                    "search_time": search_time
                }
                for row in rows
            ]
    
    async def delete_vectors(self, ids: List[str]) -> None:
        """Delete vectors by their IDs."""
        if not ids:
            return
        
        async with get_db() as db:
            # Delete metadata first (due to foreign key constraint)
            await db.execute(
                text(f"""
                    DELETE FROM {self.metadata_table}
                    WHERE vector_id = ANY(:ids)
                """),
                {"ids": [int(id_) for id_ in ids]}
            )
            
            # Delete vectors
            await db.execute(
                text(f"""
                    DELETE FROM {self.table_name}
                    WHERE id = ANY(:ids)
                """),
                {"ids": [int(id_) for id_ in ids]}
            )
            
            await db.commit()
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get store metrics."""
        async with get_db() as db:
            # Get vector count
            result = await db.execute(
                text(f"SELECT COUNT(*) FROM {self.table_name}")
            )
            vector_count = result.scalar()
            
            # Get metadata count
            result = await db.execute(
                text(f"SELECT COUNT(*) FROM {self.metadata_table}")
            )
            metadata_count = result.scalar()
            
            # Get index size
            result = await db.execute(
                text(f"""
                    SELECT pg_size_pretty(pg_relation_size('{self.table_name}_embedding_idx'))
                """)
            )
            index_size = result.scalar()
            
            return {
                "total_vectors": vector_count,
                "metadata_count": metadata_count,
                "index_size": index_size,
                "dimension": self.dimension
            }
    
    async def clear(self) -> None:
        """Clear all vectors from the store."""
        async with get_db() as db:
            await db.execute(text(f"TRUNCATE {self.metadata_table} CASCADE"))
            await db.execute(text(f"TRUNCATE {self.table_name} CASCADE"))
            await db.commit() 