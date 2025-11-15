#!/usr/bin/env python3
"""
Test alternative model IDs for OpenRouter free tier.

Some models may have different naming conventions or versions available.
This script tests alternative IDs for models that failed in the first round.

Models to test:
- google/gemma-2-27b-it:free (Gemma 2 27B)
- google/gemma-3-9b-it:free (Gemma 3 if available)
- microsoft/phi-4:free (Phi-4 if available)
- alibaba/qwen-3-14b-instruct:free (Qwen 3 14B)
- alibaba/qwen-3-110b-instruct:free (Qwen 3 110B)
- alibaba/qwen-3-coder-32b-instruct:free (Qwen 3 Coder)
- nvidia/nemotron-4-340b-instruct:free (alternative format)
- mistralai/mistral-7b-instruct-v0.3:free (Mistral 7B)
- mistralai/mistral-8x7b-instruct-v0.1:free (Mistral MoE)
- meta-llama/llama-3.1-70b-instruct:free (Llama 3.1 70B)

Usage:
    uv run python scripts/test_alternative_model_ids.py
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# Alternative model IDs to test
ALTERNATIVE_MODELS = [
    "google/gemma-2-27b-it:free",
    "google/gemma-3-9b-it:free",
    "microsoft/phi-4:free",
    "alibaba/qwen-3-14b-instruct:free",
    "alibaba/qwen-3-110b-instruct:free",
    "alibaba/qwen-3-coder-32b-instruct:free",
    "nvidia/nemotron-4-340b-instruct:free",
    "mistralai/mistral-7b-instruct-v0.3:free",
    "mistralai/mistral-8x7b-instruct-v0.1:free",
    "meta-llama/llama-3.1-70b-instruct:free",
]

# Test tasks
TASKS = {
    "simple": {
        "description": "Simple code generation",
        "prompt": "Write a Python function that returns 'Hello, World!'",
        "max_tokens": 256,
    },
    "moderate": {
        "description": "Function with error handling",
        "prompt": """Write a Python function to calculate average of a list with:
1. Type hints
2. Docstring
3. Error handling for empty list
4. Rounding to 2 decimal places""",
        "max_tokens": 512,
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
        "max_tokens": 1024,
    },
}


def assess_quality(content: str) -> int:
    """Assess quality of generated code (1-5 stars)."""
    score = 3  # Default
    if "```" in content or "def " in content:
        score += 1
    if '"""' in content or "'''" in content:
        score += 1
    if "->" in content or ": " in content:
        score += 1
    if "try" in content or "except" in content or "raise" in content:
        score += 1
    return min(5, score)


async def test_model(model: str, task_key: str, task_data: dict) -> dict:
    """Test a single model with a task."""
    if not API_KEY:
        return {
            "success": False,
            "error": "API key not set",
            "model": model,
            "task": task_key,
        }

    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://github.com/theinterneti/TTA",
                    "X-Title": "TTA-OpenHands-Alternative-Models-Test",
                },
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful coding assistant.",
                        },
                        {"role": "user", "content": task_data["prompt"]},
                    ],
                    "temperature": 0.7,
                    "max_tokens": task_data["max_tokens"],
                },
            )

        elapsed = time.time() - start_time

        if response.status_code == 429:
            return {
                "success": False,
                "error": "Rate limited (HTTP 429)",
                "model": model,
                "task": task_key,
                "time": elapsed,
            }

        if response.status_code == 404:
            return {
                "success": False,
                "error": "Model not found (HTTP 404)",
                "model": model,
                "task": task_key,
                "time": elapsed,
            }

        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "model": model,
                "task": task_key,
                "time": elapsed,
            }

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {})

        return {
            "success": True,
            "model": model,
            "task": task_key,
            "time": elapsed,
            "tokens": {
                "input": tokens.get("prompt_tokens", 0),
                "output": tokens.get("completion_tokens", 0),
                "total": tokens.get("total_tokens", 0),
            },
            "quality": assess_quality(content),
            "content_length": len(content),
        }

    except TimeoutError:
        return {
            "success": False,
            "error": "Timeout",
            "model": model,
            "task": task_key,
            "time": time.time() - start_time,
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "model": model,
            "task": task_key,
            "time": time.time() - start_time,
        }


async def main():
    """Run alternative model tests."""

    results = []
    test_count = 0
    success_count = 0

    for model in ALTERNATIVE_MODELS:
        for task_key, task_data in TASKS.items():
            test_count += 1
            result = await test_model(model, task_key, task_data)
            results.append(result)

            if result["success"]:
                success_count += 1
            else:
                pass

    # Summary

    # Per-model summary
    model_stats = {}
    for result in results:
        model = result["model"]
        if model not in model_stats:
            model_stats[model] = {
                "success": 0,
                "total": 0,
                "times": [],
                "qualities": [],
            }
        model_stats[model]["total"] += 1
        if result["success"]:
            model_stats[model]["success"] += 1
            model_stats[model]["times"].append(result["time"])
            model_stats[model]["qualities"].append(result["quality"])

    for model, stats in model_stats.items():
        100 * stats["success"] / stats["total"]
        sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
        (sum(stats["qualities"]) / len(stats["qualities"]) if stats["qualities"] else 0)

    # Save results
    output_file = Path("alternative_models_test_results.json")
    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "models_tested": ALTERNATIVE_MODELS,
                "tasks": list(TASKS.keys()),
                "total_tests": test_count,
                "successful_tests": success_count,
                "results": results,
                "model_stats": {
                    model: {
                        "success_rate": stats["success"] / stats["total"],
                        "avg_time": sum(stats["times"]) / len(stats["times"])
                        if stats["times"]
                        else 0,
                        "avg_quality": sum(stats["qualities"]) / len(stats["qualities"])
                        if stats["qualities"]
                        else 0,
                    }
                    for model, stats in model_stats.items()
                },
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    asyncio.run(main())
