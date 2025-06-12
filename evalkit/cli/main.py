import asyncio
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from evalkit.db.database import get_db
from evalkit.db.models import Interaction, Evaluation
from evalkit.core.config import settings

app = typer.Typer()
console = Console()

@app.command()
def evaluate(
    dataset: str = typer.Option(..., help="Name of the golden dataset to evaluate against"),
    model: str = typer.Option("gpt-4", help="Model to use for evaluation"),
    limit: int = typer.Option(100, help="Maximum number of interactions to evaluate"),
):
    """Run evaluations against a golden dataset."""
    console.print(f"[bold blue]Running evaluations using {model} against {dataset} dataset[/]")
    
    async def run_evaluations():
        async with get_db() as db:
            # Get interactions to evaluate
            interactions = await db.execute(
                select(Interaction)
                .limit(limit)
                .order_by(Interaction.created_at.desc())
            )
            interactions = interactions.scalars().all()
            
            with Progress() as progress:
                task = progress.add_task("[cyan]Evaluating...", total=len(interactions))
                
                for interaction in interactions:
                    # TODO: Implement actual evaluation logic
                    # This is a placeholder for the evaluation process
                    score = 0.8  # Example score
                    
                    evaluation = Evaluation(
                        interaction_id=interaction.id,
                        evaluator_type=model,
                        score=score,
                        metrics={"example": "metric"},
                        notes="Example evaluation"
                    )
                    db.add(evaluation)
                    await db.commit()
                    
                    progress.update(task, advance=1)
    
    asyncio.run(run_evaluations())
    console.print("[bold green]Evaluation complete![/]")

@app.command()
def list_interactions(
    limit: int = typer.Option(10, help="Maximum number of interactions to show"),
    with_evaluations: bool = typer.Option(False, help="Show evaluation results"),
):
    """List recent interactions."""
    async def show_interactions():
        async with get_db() as db:
            interactions = await db.execute(
                select(Interaction)
                .limit(limit)
                .order_by(Interaction.created_at.desc())
            )
            interactions = interactions.scalars().all()
            
            table = Table(title="Recent Interactions")
            table.add_column("ID", style="cyan")
            table.add_column("Query", style="green")
            table.add_column("Created", style="blue")
            table.add_column("Feedback", style="yellow")
            
            if with_evaluations:
                table.add_column("Evaluations", style="magenta")
            
            for interaction in interactions:
                row = [
                    str(interaction.id),
                    interaction.query[:50] + "..." if len(interaction.query) > 50 else interaction.query,
                    interaction.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    str(interaction.user_feedback) if interaction.user_feedback else "None"
                ]
                
                if with_evaluations:
                    evaluations = await db.execute(
                        select(Evaluation)
                        .where(Evaluation.interaction_id == interaction.id)
                    )
                    eval_scores = [f"{e.evaluator_type}: {e.score:.2f}" for e in evaluations.scalars().all()]
                    row.append("\n".join(eval_scores) if eval_scores else "None")
                
                table.add_row(*row)
            
            console.print(table)
    
    asyncio.run(show_interactions())

@app.command()
def metrics(
    days: int = typer.Option(7, help="Number of days to show metrics for"),
):
    """Show evaluation metrics."""
    async def show_metrics():
        async with get_db() as db:
            # TODO: Implement actual metrics calculation
            # This is a placeholder for the metrics display
            table = Table(title=f"Evaluation Metrics (Last {days} days)")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Average Score", "0.85")
            table.add_row("Total Evaluations", "150")
            table.add_row("Success Rate", "92%")
            
            console.print(table)
    
    asyncio.run(show_metrics())

if __name__ == "__main__":
    app() 