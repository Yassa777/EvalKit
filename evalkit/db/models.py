from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Interaction(Base):
    """Model for storing user interactions with LLM features."""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    latency_ms = Column(Float, nullable=True)
    cost_usd = Column(Float, nullable=True)
    user_feedback = Column(Integer, nullable=True)  # -1 for thumbs down, 1 for thumbs up
    evaluations = relationship("Evaluation", back_populates="interaction")

class Evaluation(Base):
    """Model for storing evaluations of interactions."""
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=False)
    evaluator_type = Column(String(50), nullable=False)  # "human", "gpt-4", etc.
    score = Column(Float, nullable=False)
    metrics = Column(JSON, nullable=False, default=dict)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    interaction = relationship("Interaction", back_populates="evaluations")

class GoldenDataset(Base):
    """Model for storing golden dataset entries."""
    __tablename__ = "golden_datasets"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    query = Column(Text, nullable=False)
    expected_response = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

class VectorStore(Base):
    """Model for storing vector store configurations and benchmarks."""
    __tablename__ = "vector_stores"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)  # "faiss", "qdrant", "pgvector"
    config = Column(JSON, nullable=False, default=dict)
    metrics = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 