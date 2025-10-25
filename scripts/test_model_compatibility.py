#!/usr/bin/env python3
"""
OpenHands Model Compatibility Test Suite

Tests multiple OpenRouter models with predefined tasks to build empirical data
on model compatibility and performance.

Usage:
    uv run python scripts/test_model_compatibility.py
    uv run python scripts/test_model_compatibility.py --model openrouter/deepseek/deepseek-chat
    uv run python scripts/test_model_compatibility.py --registry  # Test all models in registry
"""

import argparse
import asyncio
import json
import os

# Add project root to path
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pydantic import SecretStr

# Load environment variables from .env file
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agent_orchestration.openhands_integration import (
    OpenHandsClient,
    OpenHandsConfig,
)
from src.agent_orchestration.openhands_integration.config import (
    get_model_registry,
)


@dataclass
class TaskDefinition:
    """Definition of a test task."""

    id: str
    description: str
    expected_outcome: str
    success_criteria: list[str]
    timeout_seconds: float
    quality_evaluator: Callable[[str], float]


@dataclass
class TestResult:
    """Result of executing a task with a model."""

    task_id: str
    model: str
    success: bool
    execution_time: float
    quality_score: float
    output: str
    error: str | None
    metadata: dict


# Quality Evaluators


def evaluate_trivial_task(output: str) -> float:
    """Evaluate Task 1: Return 'Hello, World!'"""
    output_lower = output.lower()
    if "hello" in output_lower and "world" in output_lower:
        if "hello, world" in output_lower or "hello world" in output_lower:
            return 1.0  # Exact match
        return 0.8  # Contains both words
    if "hello" in output_lower or "world" in output_lower:
        return 0.5  # Contains one word
    return 0.0  # No match


def evaluate_simple_task(output: str) -> float:
    """Evaluate Task 2: Calculate 1+1 and explain"""
    output_lower = output.lower()
    has_answer = "2" in output or "two" in output_lower
    has_explanation = len(output) > 20  # Simple heuristic for explanation

    if has_answer and has_explanation:
        return 1.0  # Correct answer + explanation
    if has_answer:
        return 0.7  # Correct answer only
    if has_explanation:
        return 0.3  # Explanation only
    return 0.0  # No answer


def evaluate_moderate_task(output: str) -> float:
    """Evaluate Task 3: Write Python function with type hints and docstring"""
    output_lower = output.lower()
    has_function = "def " in output_lower
    has_type_hints = "->" in output or ":" in output
    has_docstring = '"""' in output or "'''" in output or "docstring" in output_lower

    if has_function and has_type_hints and has_docstring:
        return 1.0  # All requirements met
    if has_function and has_type_hints:
        return 0.8  # Function + type hints
    if has_function and has_docstring:
        return 0.8  # Function + docstring
    if has_function:
        return 0.5  # Function only
    return 0.0  # No function


def evaluate_complex_task(output: str) -> float:
    """Evaluate Task 4: Analyze code and suggest improvements"""
    output_lower = output.lower()
    suggestion_keywords = [
        "type hint",
        "docstring",
        "naming",
        "improve",
        "suggest",
        "add",
        "consider",
    ]

    suggestion_count = sum(
        1 for keyword in suggestion_keywords if keyword in output_lower
    )

    if suggestion_count >= 3:
        return 1.0  # Multiple specific suggestions
    if suggestion_count >= 1:
        return 0.7  # 1-2 specific suggestions
    if len(output) > 50:
        return 0.4  # Generic suggestions
    return 0.0  # No suggestions


# Task Definitions

TASKS = [
    TaskDefinition(
        id="task1_trivial",
        description="Return the string 'Hello, World!'",
        expected_outcome="Agent returns exactly 'Hello, World!' or similar greeting",
        success_criteria=[
            "Task completes without errors",
            "Response contains 'Hello' and 'World'",
        ],
        timeout_seconds=60.0,
        quality_evaluator=evaluate_trivial_task,
    ),
    TaskDefinition(
        id="task2_simple",
        description="Calculate the sum of 1+1 and explain the result",
        expected_outcome="Agent calculates 1+1=2 and provides explanation",
        success_criteria=[
            "Task completes without errors",
            "Response contains '2' or 'two'",
            "Response includes explanation",
        ],
        timeout_seconds=90.0,
        quality_evaluator=evaluate_simple_task,
    ),
    TaskDefinition(
        id="task3_moderate",
        description="Write a simple Python function that adds two numbers with type hints and a docstring",
        expected_outcome="Agent generates valid Python function with type hints and docstring",
        success_criteria=[
            "Task completes without errors",
            "Response contains Python function",
            "Function has type hints",
            "Function has docstring",
        ],
        timeout_seconds=120.0,
        quality_evaluator=evaluate_moderate_task,
    ),
    TaskDefinition(
        id="task4_complex",
        description="Analyze this code snippet and suggest improvements: `def calc(a,b): return a+b`",
        expected_outcome="Agent analyzes code and suggests improvements",
        success_criteria=[
            "Task completes without errors",
            "Response identifies improvement opportunities",
            "Suggestions are actionable",
        ],
        timeout_seconds=180.0,
        quality_evaluator=evaluate_complex_task,
    ),
]


class ModelTestRunner:
    """Executes tasks with different models and collects results."""

    def __init__(self, api_key: str):
        self.api_key = SecretStr(api_key)
        self.results: list[TestResult] = []

    async def execute_task(self, model: str, task: TaskDefinition) -> TestResult:
        """Execute a single task with a specific model."""
        print(f"\n  Testing {task.id} with {model}...")

        start_time = time.time()

        try:
            # Create configuration
            config = OpenHandsConfig(
                api_key=self.api_key,
                model=model,
                base_url="https://openrouter.ai/api/v1",
                workspace_path=Path.cwd() / "openhands_workspace",
                timeout_seconds=task.timeout_seconds,
            )

            # Create client
            client = OpenHandsClient(config)

            # Execute task
            result = await client.execute_task(task.description)

            execution_time = time.time() - start_time

            # Evaluate quality
            quality_score = task.quality_evaluator(result.output)

            return TestResult(
                task_id=task.id,
                model=model,
                success=result.success,
                execution_time=execution_time,
                quality_score=quality_score,
                output=result.output[:500],  # Truncate for report
                error=result.error,
                metadata={},
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_str = str(e)

            # Classify error
            metadata = {}
            if "rate limit" in error_str.lower() or "429" in error_str:
                metadata["error_type"] = "rate_limit"
            elif (
                "content policy" in error_str.lower()
                or "moderation" in error_str.lower()
            ):
                metadata["error_type"] = "content_moderation"
                metadata["incompatible"] = True
            elif (
                "LLM Provider NOT provided" in error_str
                or "not a valid model ID" in error_str
            ):
                metadata["error_type"] = "config_error"
                metadata["incompatible"] = True
            elif "developer instruction" in error_str.lower():
                metadata["error_type"] = "no_system_prompts"
                metadata["incompatible"] = True
            else:
                metadata["error_type"] = "unknown"

            return TestResult(
                task_id=task.id,
                model=model,
                success=False,
                execution_time=execution_time,
                quality_score=0.0,
                output="",
                error=error_str[:500],  # Truncate for report
                metadata=metadata,
            )

    async def test_model(
        self, model: str, tasks: list[TaskDefinition]
    ) -> list[TestResult]:
        """Test a model with all tasks."""
        print(f"\n🧪 Testing model: {model}")
        results = []

        for task in tasks:
            result = await self.execute_task(model, task)
            results.append(result)
            self.results.append(result)

            # Print result
            status = "✅" if result.success else "❌"
            print(
                f"    {status} {task.id}: {result.execution_time:.1f}s, quality: {result.quality_score:.2f}"
            )
            if result.error:
                print(f"       Error: {result.error[:100]}...")

        return results


class ReportGenerator:
    """Generates JSON and Markdown reports from test results."""

    def generate_json(self, results: list[TestResult]) -> dict:
        """Generate JSON report."""
        # Group results by model
        models_data = {}
        for result in results:
            if result.model not in models_data:
                models_data[result.model] = []
            models_data[result.model].append(result)

        # Calculate per-model metrics
        models_metrics = {}
        for model, model_results in models_data.items():
            successful = [r for r in model_results if r.success]
            models_metrics[model] = {
                "total_tasks": len(model_results),
                "successful_tasks": len(successful),
                "success_rate": len(successful) / len(model_results)
                if model_results
                else 0.0,
                "avg_execution_time": sum(r.execution_time for r in successful)
                / len(successful)
                if successful
                else 0.0,
                "avg_quality_score": sum(r.quality_score for r in successful)
                / len(successful)
                if successful
                else 0.0,
                "rate_limit_hits": sum(
                    1
                    for r in model_results
                    if r.metadata.get("error_type") == "rate_limit"
                ),
                "error_count": len([r for r in model_results if not r.success]),
            }

        return {
            "test_run": {
                "date": datetime.now().isoformat(),
                "models_tested": len(models_data),
                "tasks_executed": len(results),
                "overall_success_rate": sum(1 for r in results if r.success)
                / len(results)
                if results
                else 0.0,
            },
            "models": models_metrics,
            "tasks": [asdict(r) for r in results],
        }

    def generate_markdown(self, results: list[TestResult]) -> str:
        """Generate Markdown report."""
        # Group results by model
        models_data = {}
        for result in results:
            if result.model not in models_data:
                models_data[result.model] = []
            models_data[result.model].append(result)

        # Calculate metrics
        json_data = self.generate_json(results)

        # Build markdown
        lines = [
            "# OpenHands Model Compatibility Test Results",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Models Tested:** {json_data['test_run']['models_tested']}  ",
            f"**Tasks Executed:** {json_data['test_run']['tasks_executed']}  ",
            f"**Overall Success Rate:** {json_data['test_run']['overall_success_rate']:.1%}",
            "",
            "---",
            "",
            "## Summary",
            "",
            "| Model | Success Rate | Avg Time (s) | Avg Quality | Status |",
            "|-------|--------------|--------------|-------------|--------|",
        ]

        for model, metrics in json_data["models"].items():
            success_rate = f"{metrics['success_rate']:.1%}"
            avg_time = (
                f"{metrics['avg_execution_time']:.1f}"
                if metrics["avg_execution_time"] > 0
                else "-"
            )
            avg_quality = (
                f"{metrics['avg_quality_score']:.2f}"
                if metrics["avg_quality_score"] > 0
                else "-"
            )

            # Determine status
            if metrics["success_rate"] >= 0.75:
                status = "✅ Working"
            elif metrics["rate_limit_hits"] > 0:
                status = "⚠️ Rate Limited"
            else:
                status = "❌ Not Compatible"

            lines.append(
                f"| {model} | {success_rate} | {avg_time} | {avg_quality} | {status} |"
            )

        lines.extend(
            [
                "",
                "---",
                "",
                "## Detailed Results",
                "",
            ]
        )

        # Detailed results per model
        for model, model_results in models_data.items():
            metrics = json_data["models"][model]

            lines.extend(
                [
                    f"### {model}",
                    "",
                    "**Performance:**",
                    f"- Success Rate: {metrics['success_rate']:.1%} ({metrics['successful_tasks']}/{metrics['total_tasks']} tasks)",
                    f"- Average Execution Time: {metrics['avg_execution_time']:.1f} seconds",
                    f"- Average Quality Score: {metrics['avg_quality_score']:.2f}/1.0",
                    f"- Rate Limit Hits: {metrics['rate_limit_hits']}",
                    f"- Errors: {metrics['error_count']}",
                    "",
                    "**Task Results:**",
                ]
            )

            for result in model_results:
                status = "✅ Success" if result.success else "❌ Failed"
                lines.append(
                    f"- {result.task_id}: {status} ({result.execution_time:.1f}s, quality: {result.quality_score:.2f})"
                )
                if result.error:
                    lines.append(f"  - Error: {result.error[:100]}...")

            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "## Recommendations",
                "",
            ]
        )

        # Find best model
        best_model = max(
            json_data["models"].items(), key=lambda x: x[1]["success_rate"]
        )
        if best_model[1]["success_rate"] > 0:
            lines.extend(
                [
                    f"**Recommended Model:** `{best_model[0]}`",
                    f"- Success Rate: {best_model[1]['success_rate']:.1%}",
                    f"- Average Quality: {best_model[1]['avg_quality_score']:.2f}/1.0",
                    "",
                ]
            )

        # List incompatible models
        incompatible = [
            m
            for m, metrics in json_data["models"].items()
            if metrics["success_rate"] == 0
        ]
        if incompatible:
            lines.extend(
                [
                    "**Incompatible Models:**",
                ]
            )
            for model in incompatible:
                lines.append(f"- `{model}` - Not compatible with OpenHands integration")
            lines.append("")

        lines.extend(
            [
                "---",
                "",
                "**Generated by:** OpenHands Model Compatibility Test Suite  ",
                "**Script:** `scripts/test_model_compatibility.py`  ",
                "**Design:** `docs/openhands/model-compatibility-test-suite-design.md`",
            ]
        )

        return "\n".join(lines)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Test OpenHands model compatibility")
    parser.add_argument("--model", help="Test specific model only")
    parser.add_argument("--tasks", help="Comma-separated task IDs to run")
    parser.add_argument(
        "--registry",
        action="store_true",
        help="Test all models in the registry (WARNING: May incur API costs)",
    )
    args = parser.parse_args()

    # Get API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY environment variable not set")
        print("   Get your API key from: https://openrouter.ai/keys")
        return 1

    # Determine models to test
    if args.registry:
        # Load all models from registry
        registry = get_model_registry()
        if not registry:
            print("❌ Error: Could not load model registry")
            print("   Check that free_models_registry.yaml exists and is valid")
            return 1

        models = list(registry.models.keys())
        print(f"⚠️  WARNING: Testing {len(models)} models from registry")
        print("   This may incur significant API costs!")
        print("   Press Ctrl+C within 5 seconds to cancel...")
        try:
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n❌ Cancelled by user")
            return 0

    elif args.model:
        models = [args.model]
    else:
        models = [
            "openrouter/deepseek/deepseek-chat",  # Known working
            "openrouter/qwen/qwen3-coder:free",  # May be rate-limited
        ]

    # Determine tasks to run
    if args.tasks:
        task_ids = args.tasks.split(",")
        tasks = [t for t in TASKS if t.id in task_ids]
    else:
        tasks = TASKS

    print("🚀 OpenHands Model Compatibility Test Suite")
    print(f"   Models: {len(models)}")
    print(f"   Tasks: {len(tasks)}")

    # Run tests
    runner = ModelTestRunner(api_key)

    async def run_tests():
        for model in models:
            await runner.test_model(model, tasks)

    asyncio.run(run_tests())

    # Generate reports
    print("\n📊 Generating reports...")
    generator = ReportGenerator()

    # JSON report
    json_data = generator.generate_json(runner.results)
    json_path = Path("docs/openhands/model-compatibility-results.json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2)
    print(f"   ✅ JSON report: {json_path}")

    # Markdown report
    markdown_content = generator.generate_markdown(runner.results)
    markdown_path = Path("docs/openhands/model-compatibility-results.md")
    with open(markdown_path, "w") as f:
        f.write(markdown_content)
    print(f"   ✅ Markdown report: {markdown_path}")

    # Print summary
    print("\n📈 Summary:")
    print(f"   Models tested: {json_data['test_run']['models_tested']}")
    print(f"   Tasks executed: {json_data['test_run']['tasks_executed']}")
    print(
        f"   Overall success rate: {json_data['test_run']['overall_success_rate']:.1%}"
    )

    print("\n📖 View reports:")
    print(f"   - JSON: {json_path}")
    print(f"   - Markdown: {markdown_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
