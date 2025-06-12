from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class InteractionBase(BaseModel):
    """Base schema for interaction data."""
    query: str
    response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: Optional[float] = None
    cost_usd: Optional[float] = None

class InteractionCreate(InteractionBase):
    """Schema for creating a new interaction."""
    pass

class InteractionResponse(InteractionBase):
    """Schema for interaction response."""
    id: int
    created_at: datetime
    user_feedback: Optional[int] = None

    class Config:
        from_attributes = True

class EvaluationBase(BaseModel):
    """Base schema for evaluation data."""
    interaction_id: int
    evaluator_type: str
    score: float = Field(ge=0.0, le=1.0)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None

class EvaluationCreate(EvaluationBase):
    """Schema for creating a new evaluation."""
    pass

class EvaluationResponse(EvaluationBase):
    """Schema for evaluation response."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GoldenDatasetBase(BaseModel):
    """Base schema for golden dataset data."""
    name: str
    query: str
    expected_response: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GoldenDatasetCreate(GoldenDatasetBase):
    """Schema for creating a new golden dataset entry."""
    pass

class GoldenDatasetResponse(GoldenDatasetBase):
    """Schema for golden dataset response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VectorStoreBase(BaseModel):
    """Base schema for vector store data."""
    name: str
    type: str
    config: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)

class VectorStoreCreate(VectorStoreBase):
    """Schema for creating a new vector store configuration."""
    pass

class VectorStoreResponse(VectorStoreBase):
    """Schema for vector store response."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 