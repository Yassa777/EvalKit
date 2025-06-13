from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str = Field(
        default="postgresql://postgres:postgres@localhost:5432/evalkit",
        env="DATABASE_URL"
    )
    
    # OpenAI settings
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    
    # Vector store settings
    VECTOR_STORE_TYPE: str = Field(default="faiss", env="VECTOR_STORE_TYPE")
    VECTOR_STORE_PATH: str = Field(default="data/vector_store", env="VECTOR_STORE_PATH")
    VECTOR_DIMENSION: int = Field(default=1536, env="VECTOR_DIMENSION")
    
    # PGVector settings
    PGVECTOR_TABLE_NAME: str = Field(default="vectors", env="PGVECTOR_TABLE_NAME")
    PGVECTOR_METADATA_TABLE: str = Field(default="vector_metadata", env="PGVECTOR_METADATA_TABLE")
    PGVECTOR_INDEX_LISTS: int = Field(default=100, env="PGVECTOR_INDEX_LISTS")
    
    # Evaluation settings
    EVALUATION_CRITERIA: Dict[str, float] = Field(
        default={
            "relevance": 0.4,
            "coherence": 0.3,
            "completeness": 0.3
        }
    )
    
    # Monitoring settings
    PROMETHEUS_PORT: int = Field(default=9090, env="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(default=3000, env="GRAFANA_PORT")
    
    # API settings
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=4, env="API_WORKERS")
    
    # Dashboard settings
    DASHBOARD_PORT: int = Field(default=8501, env="DASHBOARD_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

def get_vector_store_config() -> Dict[str, Any]:
    """Get vector store configuration based on type."""
    if settings.VECTOR_STORE_TYPE == "faiss":
        return {
            "path": settings.VECTOR_STORE_PATH,
            "dimension": settings.VECTOR_DIMENSION
        }
    elif settings.VECTOR_STORE_TYPE == "pgvector":
        return {
            "dimension": settings.VECTOR_DIMENSION,
            "table_name": settings.PGVECTOR_TABLE_NAME,
            "metadata_table": settings.PGVECTOR_METADATA_TABLE,
            "index_lists": settings.PGVECTOR_INDEX_LISTS
        }
    else:
        raise ValueError(f"Unsupported vector store type: {settings.VECTOR_STORE_TYPE}") 