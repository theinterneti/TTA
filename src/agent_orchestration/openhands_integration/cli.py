"""
CLI interface for OpenHands integration.

Provides:
- Command-line interface for running OpenHands tasks
- Task submission, monitoring, and result retrieval
- Metrics and statistics reporting
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

import click

from .config import OpenHandsConfig, OpenHandsIntegrationConfig, get_model_by_preset
from .execution_engine import ExecutionEngine
from .model_selector import TaskRequirements
from .task_queue import QueuedTask, TaskPriority

logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug: bool) -> None:
    """OpenHands integration CLI."""
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


@cli.command()
@click.option(
    "--task-type", required=True, help="Task type (unit_test, refactor, etc.)"
)
@click.option("--description", required=True, help="Task description")
@click.option("--target-file", type=click.Path(), help="Target file path")
@click.option(
    "--priority",
    type=click.Choice(["low", "normal", "high", "critical"]),
    default="normal",
    help="Task priority",
)
@click.option("--quality-threshold", type=float, default=0.7, help="Quality threshold")
@click.option(
    "--complexity",
    type=click.Choice(["simple", "moderate", "complex"]),
    default="moderate",
    help="Task complexity",
)
def submit_task(
    task_type: str,
    description: str,
    target_file: str | None,
    priority: str,
    quality_threshold: float,
    complexity: str,
) -> None:
    """Submit a task for execution."""
    try:
        # Load configuration
        integration_config = OpenHandsIntegrationConfig.from_env()
        # Use DeepSeek as default (more reliable than Gemini free tier)
        model_id = integration_config.custom_model_id or get_model_by_preset(
            "deepseek-v3"
        )
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=model_id,
            workspace_path=integration_config.workspace_root,
        )

        # Create task
        priority_map = {
            "low": TaskPriority.LOW,
            "normal": TaskPriority.NORMAL,
            "high": TaskPriority.HIGH,
            "critical": TaskPriority.CRITICAL,
        }

        task = QueuedTask(
            task_type=task_type,
            description=description,
            target_file=Path(target_file) if target_file else None,
            priority=priority_map[priority],
            metadata={
                "category": task_type,
                "complexity": complexity,
                "quality_threshold": quality_threshold,
            },
        )

        # Create engine and submit (don't stop engine - let it run)
        engine = ExecutionEngine(config)

        async def run():
            # Load existing tasks from persistence
            await engine.queue.load_from_file()
            # Submit new task
            task_id = await engine.queue.enqueue(task)
            # Save to persistence file
            await engine.queue.save_to_file()
            click.echo(f"Task submitted: {task_id}")

        asyncio.run(run())

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--task-id", required=True, help="Task ID")
def get_status(task_id: str) -> None:
    """Get task status."""
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        # Use DeepSeek as default (more reliable than Gemini free tier)
        model_id = integration_config.custom_model_id or get_model_by_preset(
            "deepseek-v3"
        )
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=model_id,
            workspace_path=integration_config.workspace_root,
        )
        engine = ExecutionEngine(config)

        async def run():
            task = await engine.get_task_status(task_id)
            if task:
                click.echo(json.dumps(task.to_dict(), indent=2, default=str))
            else:
                click.echo(f"Task {task_id} not found", err=True)
                sys.exit(1)

        asyncio.run(run())

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def queue_stats() -> None:
    """Get queue statistics."""
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        # Use DeepSeek as default (more reliable than Gemini free tier)
        model_id = integration_config.custom_model_id or get_model_by_preset(
            "deepseek-v3"
        )
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=model_id,
            workspace_path=integration_config.workspace_root,
        )
        engine = ExecutionEngine(config)

        async def run():
            stats = await engine.get_queue_stats()
            click.echo(json.dumps(stats, indent=2))

        asyncio.run(run())

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def metrics() -> None:
    """Get metrics summary."""
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        # Use DeepSeek as default (more reliable than Gemini free tier)
        model_id = integration_config.custom_model_id or get_model_by_preset(
            "deepseek-v3"
        )
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=model_id,
            workspace_path=integration_config.workspace_root,
        )
        engine = ExecutionEngine(config)

        summary = engine.get_metrics_summary()
        click.echo(json.dumps(summary, indent=2))

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--workers", type=int, default=5, help="Number of worker tasks")
@click.option("--duration", type=int, default=60, help="Duration in seconds")
def run_engine(workers: int, duration: int) -> None:
    """Run execution engine."""
    try:
        integration_config = OpenHandsIntegrationConfig.from_env()
        # Use DeepSeek as default (more reliable than Gemini free tier)
        model_id = integration_config.custom_model_id or get_model_by_preset(
            "deepseek-v3"
        )
        config = OpenHandsConfig(
            api_key=integration_config.api_key,
            model=model_id,
            workspace_path=integration_config.workspace_root,
        )
        engine = ExecutionEngine(config, max_concurrent_tasks=workers)

        async def run():
            await engine.start()
            click.echo(f"Engine running with {workers} workers for {duration}s")
            await asyncio.sleep(duration)
            await engine.stop()
            click.echo("Engine stopped")

        asyncio.run(run())

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--task-type", required=True, help="Task type")
@click.option(
    "--complexity",
    type=click.Choice(["simple", "moderate", "complex"]),
    default="moderate",
)
@click.option("--quality-threshold", type=float, default=0.7)
def select_model(task_type: str, complexity: str, quality_threshold: float) -> None:
    """Select optimal model for task."""
    try:
        from .model_selector import ModelSelector, TaskCategory

        selector = ModelSelector()

        # Map task type to category
        category_map = {
            "unit_test": TaskCategory.UNIT_TEST,
            "refactor": TaskCategory.REFACTORING,
            "document": TaskCategory.DOCUMENTATION,
            "generate": TaskCategory.CODE_GENERATION,
            "analyze": TaskCategory.ANALYSIS,
        }

        category = category_map.get(task_type, TaskCategory.CODE_GENERATION)

        requirements = TaskRequirements(
            category=category,
            complexity=complexity,
            quality_threshold=quality_threshold,
        )

        model = selector.select_model(requirements)
        if model:
            click.echo(f"Selected model: {model.name}")
            click.echo(f"  ID: {model.model_id}")
            click.echo(f"  Latency: {model.avg_latency_ms:.0f}ms")
            click.echo(f"  Quality: {model.quality_score:.1f}/5.0")
            click.echo(f"  Success rate: {model.success_rate * 100:.1f}%")
        else:
            click.echo("No suitable model found", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
