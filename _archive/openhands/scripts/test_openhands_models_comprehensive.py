#!/usr/bin/env python3
"""

# Logseq: [[TTA.dev/_archive/Openhands/Scripts/Test_openhands_models_comprehensive]]
Comprehensive test of free models via OpenRouter API.

Tests multiple free models to establish baseline capabilities and performance.
Models tested:
- deepseek/deepseek-chat
- deepseek/deepseek-r1
- google/gemini-flash-1.5-8b
- meta-llama/llama-3.3-70b-instruct
- mistralai/mistral-small-3.2-24b-instruct:free
- qwen/qwen3-coder:free

Usage:
    uv run python scripts/test_openhands_models_comprehensive.py
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# Models to test
MODELS = [
    "deepseek/deepseek-chat",
    "deepseek/deepseek-r1",
    "google/gemini-flash-1.5-8b",
    "meta-llama/llama-3.3-70b-instruct",
    "mistralai/mistral-small-3.2-24b-instruct:free",
    "qwen/qwen3-coder:free",
]

# Test tasks
TASKS = {
    "simple": {
        "description": "Simple code generation",
        "prompt": "Write a Python function that returns 'Hello, World!'",
        "max_tokens": 1024,
    },
    "moderate": {
        "description": "Function with error handling",
        "prompt": """Write a Python function to calculate average of a list with:
1. Type hints
2. Docstring
3. Error handling for empty list
4. Rounding to 2 decimal places""",
        "max_tokens": 2048,
    },
    "complex": {
        "description": "Generate unit tests",
        "prompt": """Generate comprehensive pytest tests for this function:

def calculate_average(numbers: list[float]) -> float:
    if not numbers:
        raise ValueError("List cannot be empty")
    return round(sum(numbers) / len(numbers), 2)

Requirements:
1. Test valid inputs (positive, negative, mixed)
2. Test edge cases (single element, large numbers)
3. Test error cases (empty list)
4. Use pytest.mark.parametrize
5. Include docstrings""",
        "max_tokens": 4096,
    },
}


async def test_model(model: str, task_key: str, task_data: dict) -> dict:
    """Test a single model with a task."""
    logger.info(f"Testing {model} with {task_key}...")

    if not API_KEY:
        logger.error("OPENROUTER_API_KEY not set")
        return {"success": False, "error": "API key not set"}

    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://github.com/theinterneti/TTA",
                    "X-Title": "TTA-OpenHands-Model-Test",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful coding assistant. Provide complete, working code.",
                        },
                        {"role": "user", "content": task_data["prompt"]},
                    ],
                    "temperature": 0.7,
                    "max_tokens": task_data["max_tokens"],
                },
            )

            execution_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})

                # Quality assessment
                quality_score = assess_quality(content, task_key)

                return {
                    "success": True,
                    "model": model,
                    "task": task_key,
                    "execution_time": execution_time,
                    "tokens_used": usage.get("total_tokens", 0),
                    "input_tokens": usage.get("prompt_tokens", 0),
                    "output_tokens": usage.get("completion_tokens", 0),
                    "quality_score": quality_score,
                    "content_length": len(content),
                    "content_preview": content[:200],
                }
            return {
                "success": False,
                "model": model,
                "task": task_key,
                "error": f"HTTP {response.status_code}",
                "error_detail": response.text[:200],
            }

    except Exception as e:
        return {
            "success": False,
            "model": model,
            "task": task_key,
            "error": str(e),
        }


def assess_quality(content: str, task_key: str) -> int:
    """Assess quality of generated content (1-5 stars)."""
    score = 3  # Default

    # Check for code blocks
    if "```" in content or "def " in content:
        score += 1

    # Check for docstrings
    if '"""' in content or "'''" in content:
        score += 1

    # Check for type hints
    if "->" in content or ": " in content:
        score += 1

    # Check for error handling
    if "try" in content or "except" in content or "raise" in content:
        score += 1

    # Check for tests (if test task)
    if task_key == "complex" and ("@pytest" in content or "def test_" in content):
        score += 1

    return min(5, score)


async def main():
    """Run comprehensive model tests."""
    logger.info("\n╔" + "=" * 78 + "╗")
    logger.info(
        "║" + " " * 15 + "OpenHands Free Models Comprehensive Test" + " " * 23 + "║"
    )
    logger.info("╚" + "=" * 78 + "╝\n")

    results = []

    # Test each model with each task
    for model in MODELS:
        logger.info(f"\n{'=' * 80}")
        logger.info(f"Testing Model: {model}")
        logger.info(f"{'=' * 80}")

        for task_key, task_data in TASKS.items():
            result = await test_model(model, task_key, task_data)
            results.append(result)

            if result["success"]:
                logger.info(
                    f"  ✅ {task_key}: {result['execution_time']:.1f}s, "
                    f"{result['tokens_used']} tokens, "
                    f"Quality: {result['quality_score']}/5"
                )
            else:
                logger.info(f"  ❌ {task_key}: {result.get('error', 'Unknown error')}")

            # Rate limiting - wait between requests
            await asyncio.sleep(2)

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)

    # Group by model
    by_model = {}
    for result in results:
        model = result.get("model", "unknown")
        if model not in by_model:
            by_model[model] = []
        by_model[model].append(result)

    # Print summary by model
    for model, model_results in by_model.items():
        successful = sum(1 for r in model_results if r["success"])
        total = len(model_results)
        avg_time = sum(
            r.get("execution_time", 0) for r in model_results if r["success"]
        ) / max(1, successful)
        avg_tokens = sum(
            r.get("tokens_used", 0) for r in model_results if r["success"]
        ) / max(1, successful)
        avg_quality = sum(
            r.get("quality_score", 0) for r in model_results if r["success"]
        ) / max(1, successful)

        logger.info(f"\n{model}:")
        logger.info(f"  Success Rate: {successful}/{total}")
        logger.info(f"  Avg Time: {avg_time:.1f}s")
        logger.info(f"  Avg Tokens: {avg_tokens:.0f}")
        logger.info(f"  Avg Quality: {avg_quality:.1f}/5")

    # Save results to JSON
    output_file = Path("openhands_model_test_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"\n✅ Results saved to {output_file}")

    logger.info("\n" + "=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
