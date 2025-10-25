#!/usr/bin/env python3
"""
Expanded model testing for OpenHands integration - Phase 2.

Tests additional free models on OpenRouter to expand coverage and identify
best models for rotation strategy.

Models tested (in addition to Phase 1):
- deepseek/deepseek-chat-v3.1:free (new)
- deepseek/deepseek-r1-0528-qwen3-8b:free (new)
- meta-llama/llama-3.1-8b-instruct:free (new)
- google/gemini-2.0-flash-exp:free (new)
- mistralai/mistral-large-2411:free (new)

Usage:
    uv run python scripts/test_openhands_expanded_models.py
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

# Additional models to test (Phase 2 expansion)
EXPANDED_MODELS = [
    "deepseek/deepseek-chat-v3.1:free",
    "deepseek/deepseek-r1-0528-qwen3-8b:free",
    "meta-llama/llama-3.1-8b-instruct:free",
    "google/gemini-2.0-flash-exp:free",
    "mistralai/mistral-large-2411:free",
]

# Test tasks (same as Phase 1 comprehensive)
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
                    "X-Title": "TTA-OpenHands-Expanded-Model-Test",
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

    except asyncio.TimeoutError:
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
    """Run expanded model tests."""
    print("\n" + "=" * 80)
    print("Phase 2: Expanded Model Coverage Testing")
    print("=" * 80)
    print(f"Models: {len(EXPANDED_MODELS)}")
    print(f"Tasks: {len(TASKS)}")
    print(f"Total Tests: {len(EXPANDED_MODELS) * len(TASKS)}")
    print(f"Start Time: {datetime.now().isoformat()}\n")

    results = []
    test_count = 0
    success_count = 0

    for model in EXPANDED_MODELS:
        print(f"\n📦 Testing: {model}")
        for task_key, task_data in TASKS.items():
            test_count += 1
            result = await test_model(model, task_key, task_data)
            results.append(result)

            if result["success"]:
                success_count += 1
                print(
                    f"  ✅ {task_key:10} | {result['time']:6.2f}s | "
                    f"{result['tokens']['total']:4} tokens | ⭐ {result['quality']}/5"
                )
            else:
                print(f"  ❌ {task_key:10} | {result['error']}")

    # Summary
    print("\n" + "=" * 80)
    print("PHASE 2 RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {test_count}")
    print(
        f"Successful: {success_count}/{test_count} ({100 * success_count / test_count:.1f}%)"
    )
    print(f"Failed: {test_count - success_count}")

    # Per-model summary
    print("\n📊 Per-Model Summary:")
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
        success_rate = 100 * stats["success"] / stats["total"]
        avg_time = sum(stats["times"]) / len(stats["times"]) if stats["times"] else 0
        avg_quality = (
            sum(stats["qualities"]) / len(stats["qualities"])
            if stats["qualities"]
            else 0
        )
        print(
            f"  {model:50} | "
            f"Success: {stats['success']}/{stats['total']} ({success_rate:5.1f}%) | "
            f"Avg Time: {avg_time:6.2f}s | "
            f"Avg Quality: {avg_quality:3.1f}/5"
        )

    # Save results
    output_file = Path("expanded_model_test_results.json")
    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "models_tested": EXPANDED_MODELS,
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

    print(f"\n✅ Results saved to: {output_file}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
