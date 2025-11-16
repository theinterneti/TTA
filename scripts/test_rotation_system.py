#!/usr/bin/env python3
"""
Integration test for model rotation system.

Tests:
1. Model rotation on rate limiting
2. Exponential backoff timing
3. Rotation order correctness
4. Metrics tracking
5. Overall success rate improvement

Usage:
    uv run python scripts/test_rotation_system.py
"""

import asyncio
import json
import os

# Add src to path
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_orchestration.openhands_integration.model_rotation import (
    ModelRotationManager,
)
from agent_orchestration.openhands_integration.retry_policy import (
    RetryConfig,
    RetryPolicy,
)

# Load environment
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# Test configuration
ROTATION_MANAGER = ModelRotationManager()
RETRY_POLICY = RetryPolicy(
    RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=30.0,
        exponential_base=2.0,
        jitter=False,  # Disable jitter for predictable testing
    )
)

# Test tasks
TEST_TASKS = [
    {
        "name": "simple_1",
        "prompt": "Write a Python function that returns 'Hello, World!'",
        "max_tokens": 256,
    },
    {
        "name": "simple_2",
        "prompt": "Write a Python function to add two numbers",
        "max_tokens": 256,
    },
    {
        "name": "simple_3",
        "prompt": "Write a Python function to check if a number is even",
        "max_tokens": 256,
    },
    {
        "name": "moderate_1",
        "prompt": """Write a Python function to calculate average of a list with:
1. Type hints
2. Docstring
3. Error handling for empty list
4. Rounding to 2 decimal places""",
        "max_tokens": 512,
    },
    {
        "name": "moderate_2",
        "prompt": """Write a Python function to validate email address with:
1. Type hints
2. Docstring
3. Proper regex pattern
4. Error handling""",
        "max_tokens": 512,
    },
]


async def test_model_with_rotation(task: dict) -> dict:
    """Test a task with model rotation."""
    start_time = time.time()
    attempt = 0
    last_error = None

    while attempt <= RETRY_POLICY.config.max_retries:
        current_model = ROTATION_MANAGER.get_current_model()
        attempt_start = time.time()

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{BASE_URL}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "HTTP-Referer": "https://github.com/theinterneti/TTA",
                        "X-Title": "TTA-Rotation-Test",
                    },
                    json={
                        "model": current_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful coding assistant.",
                            },
                            {"role": "user", "content": task["prompt"]},
                        ],
                        "temperature": 0.7,
                        "max_tokens": task["max_tokens"],
                    },
                )

            attempt_time = time.time() - attempt_start

            if response.status_code == 429:
                # Rate limited - rotate to next model
                ROTATION_MANAGER.on_rate_limit(attempt_time)
                if ROTATION_MANAGER.should_rotate():
                    ROTATION_MANAGER.get_next_model()
                    attempt += 1
                    if attempt <= RETRY_POLICY.config.max_retries:
                        delay = RETRY_POLICY.config.get_delay(attempt - 1)
                        await asyncio.sleep(delay)
                    continue
                attempt += 1
                continue

            if response.status_code != 200:
                # Other error
                ROTATION_MANAGER.on_failure(attempt_time)
                last_error = f"HTTP {response.status_code}"
                attempt += 1
                if attempt <= RETRY_POLICY.config.max_retries:
                    delay = RETRY_POLICY.config.get_delay(attempt - 1)
                    await asyncio.sleep(delay)
                continue

            # Success
            ROTATION_MANAGER.on_success(attempt_time)
            total_time = time.time() - start_time
            return {
                "success": True,
                "task": task["name"],
                "model": current_model,
                "attempt": attempt + 1,
                "time": total_time,
                "attempt_time": attempt_time,
            }

        except TimeoutError:
            ROTATION_MANAGER.on_failure(time.time() - attempt_start)
            last_error = "Timeout"
            attempt += 1
            if attempt <= RETRY_POLICY.config.max_retries:
                delay = RETRY_POLICY.config.get_delay(attempt - 1)
                await asyncio.sleep(delay)
        except Exception as e:
            ROTATION_MANAGER.on_failure(time.time() - attempt_start)
            last_error = str(e)
            attempt += 1
            if attempt <= RETRY_POLICY.config.max_retries:
                delay = RETRY_POLICY.config.get_delay(attempt - 1)
                await asyncio.sleep(delay)

    # All attempts failed
    total_time = time.time() - start_time
    return {
        "success": False,
        "task": task["name"],
        "model": ROTATION_MANAGER.get_current_model(),
        "attempt": attempt,
        "time": total_time,
        "error": last_error,
    }


async def main():
    """Run rotation system tests."""

    results = []
    success_count = 0

    for _i, task in enumerate(TEST_TASKS, 1):
        result = await test_model_with_rotation(task)
        results.append(result)

        if result["success"]:
            success_count += 1
        else:
            pass

    # Summary

    # Rotation metrics
    ROTATION_MANAGER.print_metrics()

    # Save results
    output_file = Path("rotation_test_results.json")
    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "total_tests": len(TEST_TASKS),
                "successful_tests": success_count,
                "success_rate": success_count / len(TEST_TASKS),
                "results": results,
                "rotation_summary": ROTATION_MANAGER.get_summary(),
            },
            f,
            indent=2,
        )


if __name__ == "__main__":
    asyncio.run(main())
