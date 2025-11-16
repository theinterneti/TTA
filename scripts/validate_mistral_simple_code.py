#!/usr/bin/env python3
"""
Phase 1 Validation Test: Mistral Small + Simple Code Generation

Purpose: Validate that Mistral Small + Direct API works reliably for simple code generation
Target: >90% success rate, 1.6s avg execution time, 4.7/5 quality

Test Configuration:
- Model: mistralai/mistral-small-3.2-24b-instruct:free
- Access: Direct API (OpenRouter)
- Task: Simple code generation (< 50 lines)
- Iterations: 10 tests
- Metrics: Success rate, execution time, token usage, quality score
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Configuration
BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "mistralai/mistral-small-3.2-24b-instruct:free"
API_KEY = os.getenv("OPENROUTER_API_KEY")

# Simple code generation tasks (< 50 lines)
SIMPLE_TASKS = [
    {
        "id": "hello_world",
        "prompt": "Write a Python function that prints 'Hello, World!' and returns the string.",
        "max_tokens": 256,
    },
    {
        "id": "add_function",
        "prompt": "Write a Python function named 'add' that takes two numbers and returns their sum.",
        "max_tokens": 256,
    },
    {
        "id": "is_even",
        "prompt": "Write a Python function that checks if a number is even. Return True if even, False if odd.",
        "max_tokens": 256,
    },
    {
        "id": "reverse_string",
        "prompt": "Write a Python function that reverses a string and returns it.",
        "max_tokens": 256,
    },
    {
        "id": "factorial",
        "prompt": "Write a Python function that calculates the factorial of a number.",
        "max_tokens": 256,
    },
    {
        "id": "fibonacci",
        "prompt": "Write a Python function that returns the nth Fibonacci number.",
        "max_tokens": 256,
    },
    {
        "id": "list_sum",
        "prompt": "Write a Python function that sums all numbers in a list.",
        "max_tokens": 256,
    },
    {
        "id": "max_value",
        "prompt": "Write a Python function that finds the maximum value in a list.",
        "max_tokens": 256,
    },
    {
        "id": "count_vowels",
        "prompt": "Write a Python function that counts the number of vowels in a string.",
        "max_tokens": 256,
    },
    {
        "id": "is_palindrome",
        "prompt": "Write a Python function that checks if a string is a palindrome.",
        "max_tokens": 256,
    },
]


def assess_quality(content: str) -> int:
    """Assess quality of generated code (1-5 stars)."""
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

    return min(5, score)


async def run_validation_test(task: dict) -> dict:
    """Run a single validation test."""
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://github.com/theinterneti/TTA",
                    "X-Title": "TTA-OpenHands-Validation",
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful Python coding assistant. Write clean, well-documented code.",
                        },
                        {"role": "user", "content": task["prompt"]},
                    ],
                    "temperature": 0.7,
                    "max_tokens": task["max_tokens"],
                },
            )

        elapsed = time.time() - start_time

        if response.status_code != 200:
            return {
                "task_id": task["id"],
                "success": False,
                "error": f"HTTP {response.status_code}",
                "elapsed": elapsed,
                "tokens": 0,
                "quality": 0,
            }

        data = response.json()
        content = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        quality = assess_quality(content)

        return {
            "task_id": task["id"],
            "success": True,
            "elapsed": elapsed,
            "tokens": usage.get("total_tokens", 0),
            "input_tokens": usage.get("prompt_tokens", 0),
            "output_tokens": usage.get("completion_tokens", 0),
            "quality": quality,
            "content_length": len(content),
        }

    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "task_id": task["id"],
            "success": False,
            "error": str(e),
            "elapsed": elapsed,
            "tokens": 0,
            "quality": 0,
        }


async def main():
    """Run validation tests."""
    if not API_KEY:
        return

    # Run tests
    results = []
    for _i, task in enumerate(SIMPLE_TASKS, 1):
        result = await run_validation_test(task)
        results.append(result)

        if result["success"]:
            pass
        else:
            pass

    # Calculate statistics
    successful = sum(1 for r in results if r["success"])
    success_rate = (successful / len(results)) * 100

    avg_time = (
        sum(r["elapsed"] for r in results if r["success"]) / successful
        if successful > 0
        else 0
    )
    avg_tokens = (
        sum(r["tokens"] for r in results if r["success"]) / successful
        if successful > 0
        else 0
    )
    avg_quality = (
        sum(r["quality"] for r in results if r["success"]) / successful
        if successful > 0
        else 0
    )

    # Validation criteria

    # Overall result
    all_pass = success_rate >= 90 and avg_time < 3 and avg_quality >= 4.5

    # Save results
    report = {
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "task_count": len(SIMPLE_TASKS),
        "success_rate": success_rate,
        "successful_tests": successful,
        "avg_time": avg_time,
        "avg_tokens": avg_tokens,
        "avg_quality": avg_quality,
        "validation_pass": all_pass,
        "results": results,
    }

    with open("validation_results.json", "w") as f:
        json.dump(report, f, indent=2)


if __name__ == "__main__":
    asyncio.run(main())
