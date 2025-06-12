from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EvalKit"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./evalkit.db"
    DB_ECHO: bool = False
    
    # Vector Store
    DEFAULT_VECTOR_STORE: str = "faiss"
    VECTOR_DIMENSION: int = 1536  # Default for OpenAI embeddings
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Metrics
    ENABLE_METRICS: bool = True
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

settings = get_settings() 