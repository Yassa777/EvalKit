from typing import Dict, Any
from evalkit.vector.base import VectorStore
from evalkit.vector.faiss_store import FAISSVectorStore
from evalkit.vector.pgvector_store import PGVectorStore
from evalkit.config import settings

def create_vector_store() -> VectorStore:
    """Create vector store instance based on configuration."""
    if settings.VECTOR_STORE_TYPE == "faiss":
        return FAISSVectorStore()
    elif settings.VECTOR_STORE_TYPE == "pgvector":
        return PGVectorStore()
    else:
        raise ValueError(f"Unsupported vector store type: {settings.VECTOR_STORE_TYPE}") 