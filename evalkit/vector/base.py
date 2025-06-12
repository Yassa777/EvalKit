from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

class VectorStore(ABC):
    """Base class for vector store implementations."""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the vector store with configuration."""
        pass
    
    @abstractmethod
    async def add_vectors(
        self,
        vectors: np.ndarray,
        metadata: List[Dict[str, Any]],
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add vectors to the store with metadata."""
        pass
    
    @abstractmethod
    async def search(
        self,
        query_vector: np.ndarray,
        k: int = 10,
        filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        pass
    
    @abstractmethod
    async def delete_vectors(self, ids: List[str]) -> None:
        """Delete vectors by their IDs."""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get performance and usage metrics."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all vectors from the store."""
        pass

class VectorStoreFactory:
    """Factory for creating vector store instances."""
    
    _stores = {}
    
    @classmethod
    def register(cls, store_type: str, store_class: type) -> None:
        """Register a vector store implementation."""
        cls._stores[store_type] = store_class
    
    @classmethod
    def create(cls, store_type: str, config: Dict[str, Any]) -> VectorStore:
        """Create a vector store instance."""
        if store_type not in cls._stores:
            raise ValueError(f"Unknown vector store type: {store_type}")
        
        store = cls._stores[store_type]()
        return store 