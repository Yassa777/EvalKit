import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from evalkit.db.database import get_db
from evalkit.db.models import Interaction, Evaluation, GoldenDataset
from evalkit.core.config import settings

st.set_page_config(
    page_title="EvalKit Dashboard",
    page_icon="📊",
    layout="wide"
)

async def get_metrics_data(days: int = 7):
    """Fetch metrics data from database."""
    async with get_db() as db:
        # Get interaction counts
        interactions = await db.execute(
            select(Interaction)
            .where(Interaction.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        interactions = interactions.scalars().all()
        
        # Get evaluation data
        evaluations = await db.execute(
            select(Evaluation)
            .where(Evaluation.created_at >= datetime.utcnow() - timedelta(days=days))
        )
        evaluations = evaluations.scalars().all()
        
        return interactions, evaluations

def create_metrics_dashboard():
    """Create the main metrics dashboard."""
    st.title("EvalKit Dashboard")
    
    # Date range selector
    days = st.sidebar.slider("Time Range (days)", 1, 30, 7)
    
    # Fetch data
    interactions, evaluations = asyncio.run(get_metrics_data(days))
    
    # Convert to DataFrames
    interactions_df = pd.DataFrame([
        {
            "date": i.created_at.date(),
            "query": i.query,
            "response": i.response,
            "latency": i.latency_ms,
            "cost": i.cost_usd,
            "feedback": i.user_feedback
        }
        for i in interactions
    ])
    
    evaluations_df = pd.DataFrame([
        {
            "date": e.created_at.date(),
            "score": e.score,
            "evaluator": e.evaluator_type,
            "metrics": e.metrics
        }
        for e in evaluations
    ])
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Interactions",
            len(interactions),
            f"{len(interactions) - len(interactions_df[interactions_df['date'] == interactions_df['date'].max()])} from last period"
        )
    
    with col2:
        avg_score = evaluations_df["score"].mean() if not evaluations_df.empty else 0
        st.metric(
            "Average Score",
            f"{avg_score:.2f}",
            f"{evaluations_df['score'].std():.2f} std"
        )
    
    with col3:
        avg_latency = interactions_df["latency"].mean() if not interactions_df.empty else 0
        st.metric(
            "Avg Latency",
            f"{avg_latency:.0f}ms",
            f"{interactions_df['latency'].std():.0f}ms std"
        )
    
    with col4:
        total_cost = interactions_df["cost"].sum() if not interactions_df.empty else 0
        st.metric(
            "Total Cost",
            f"${total_cost:.2f}",
            f"${total_cost/days:.2f}/day"
        )
    
    # Create charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution
        if not evaluations_df.empty:
            fig = px.histogram(
                evaluations_df,
                x="score",
                nbins=20,
                title="Score Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Latency over time
        if not interactions_df.empty:
            fig = px.line(
                interactions_df.groupby("date")["latency"].mean().reset_index(),
                x="date",
                y="latency",
                title="Average Latency Over Time"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Recent interactions
    st.subheader("Recent Interactions")
    if not interactions_df.empty:
        st.dataframe(
            interactions_df.sort_values("date", ascending=False).head(10),
            use_container_width=True
        )
    
    # Evaluation metrics
    st.subheader("Evaluation Metrics")
    if not evaluations_df.empty:
        metrics_df = pd.DataFrame([
            {
                "date": e["date"],
                "metric": k,
                "value": v
            }
            for e in evaluations_df.to_dict("records")
            for k, v in e["metrics"].items()
        ])
        
        fig = px.box(
            metrics_df,
            x="metric",
            y="value",
            title="Evaluation Metrics Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    create_metrics_dashboard()

if __name__ == "__main__":
    main() 