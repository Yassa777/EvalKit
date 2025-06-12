import faiss
import numpy as np
from typing import List, Dict, Any, Optional
import time
from .base import VectorStore

class FAISSStore(VectorStore):
    """FAISS vector store implementation."""
    
    def __init__(self):
        self.index = None
        self.metadata = {}
        self.dimension = None
        self.metric = None
    
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize FAISS index with configuration."""
        self.dimension = config.get("dimension", 1536)  # Default for OpenAI embeddings
        self.metric = config.get("metric", "l2")
        
        # Create the index
        if self.metric == "l2":
            self.index = faiss.IndexFlatL2(self.dimension)
        elif self.metric == "ip":  # Inner product (cosine similarity)
            self.index = faiss.IndexFlatIP(self.dimension)
        else:
            raise ValueError(f"Unsupported metric: {self.metric}")
        
        # If GPU is available and requested
        if config.get("use_gpu", False):
            try:
                res = faiss.StandardGpuResources()
                self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
            except Exception as e:
                print(f"Failed to use GPU: {e}")
    
    async def add_vectors(
        self,
        vectors: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add vectors to the FAISS index."""
        if self.index is None:
            raise RuntimeError("FAISS index not initialized")
        
        if len(vectors) != len(metadata):
            raise ValueError("Number of vectors must match number of metadata entries")
        
        # Generate IDs if not provided
        if ids is None:
            ids = [str(i) for i in range(self.index.ntotal, self.index.ntotal + len(vectors))]
        
        # Add vectors to index
        self.index.add(vectors)
        
        # Store metadata
        for i, id_ in enumerate(ids):
            self.metadata[id_] = metadata[i]
        
        return ids
    
    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        if self.index is None:
            raise RuntimeError("FAISS index not initialized")
        
        # Ensure query vector is 2D
        if query_vector.ndim == 1:
            query_vector = query_vector.reshape(1, -1)
        
        # Search
        start_time = time.time()
        distances, indices = self.index.search(query_vector, k)
        search_time = time.time() - start_time
        
        # Prepare results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue
                
            # Convert index to ID
            id_ = str(idx)
            if id_ not in self.metadata:
                continue
            
            result = {
                "id": id_,
                "distance": float(distance),
                "metadata": self.metadata[id_],
                "search_time": search_time
            }
            results.append(result)
        
        return results
    
    async def delete_vectors(self, ids: List[str]) -> None:
        """Delete vectors by their IDs."""
        # FAISS doesn't support direct deletion, so we need to rebuild the index
        if not ids:
            return
        
        # Get all current vectors
        all_vectors = faiss.vector_to_array(self.index.get_xb())
        all_metadata = self.metadata.copy()
        
        # Clear current index
        self.index = None
        await self.initialize({"dimension": self.dimension, "metric": self.metric})
        
        # Rebuild index without deleted vectors
        new_vectors = []
        new_metadata = {}
        
        for i, id_ in enumerate(all_metadata.keys()):
            if id_ not in ids:
                new_vectors.append(all_vectors[i])
                new_metadata[id_] = all_metadata[id_]
        
        if new_vectors:
            await self.add_vectors(
                np.array(new_vectors),
                list(new_metadata.values()),
                list(new_metadata.keys())
            )
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get FAISS index metrics."""
        if self.index is None:
            return {"status": "not_initialized"}
        
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "metric": self.metric,
            "is_gpu": hasattr(self.index, "gpu_index"),
            "metadata_count": len(self.metadata)
        }
    
    async def clear(self) -> None:
        """Clear all vectors from the store."""
        self.index = None
        self.metadata = {}
        await self.initialize({"dimension": self.dimension, "metric": self.metric}) 