from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from evalkit.db.database import get_db
from evalkit.db.models import Interaction, Evaluation
from evalkit.core.config import settings
from evalkit.api.schemas import (
    InteractionCreate,
    InteractionResponse,
    EvaluationCreate,
    EvaluationResponse,
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post(
    f"{settings.API_V1_STR}/interactions",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_interaction(
    interaction: InteractionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new interaction record."""
    db_interaction = Interaction(
        query=interaction.query,
        response=interaction.response,
        metadata=interaction.metadata,
        latency_ms=interaction.latency_ms,
        cost_usd=interaction.cost_usd,
    )
    db.add(db_interaction)
    await db.commit()
    await db.refresh(db_interaction)
    return db_interaction

@app.get(
    f"{settings.API_V1_STR}/interactions",
    response_model=List[InteractionResponse]
)
async def list_interactions(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all interactions."""
    result = await db.execute(
        select(Interaction)
        .offset(skip)
        .limit(limit)
        .order_by(Interaction.created_at.desc())
    )
    return result.scalars().all()

@app.post(
    f"{settings.API_V1_STR}/evaluations",
    response_model=EvaluationResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_evaluation(
    evaluation: EvaluationCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new evaluation record."""
    # Verify interaction exists
    interaction = await db.get(Interaction, evaluation.interaction_id)
    if not interaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interaction not found"
        )
    
    db_evaluation = Evaluation(
        interaction_id=evaluation.interaction_id,
        evaluator_type=evaluation.evaluator_type,
        score=evaluation.score,
        metrics=evaluation.metrics,
        notes=evaluation.notes,
    )
    db.add(db_evaluation)
    await db.commit()
    await db.refresh(db_evaluation)
    return db_evaluation

@app.get(
    f"{settings.API_V1_STR}/evaluations",
    response_model=List[EvaluationResponse]
)
async def list_evaluations(
    interaction_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List evaluations, optionally filtered by interaction_id."""
    query = select(Evaluation)
    if interaction_id:
        query = query.where(Evaluation.interaction_id == interaction_id)
    
    result = await db.execute(
        query
        .offset(skip)
        .limit(limit)
        .order_by(Evaluation.created_at.desc())
    )
    return result.scalars().all() 