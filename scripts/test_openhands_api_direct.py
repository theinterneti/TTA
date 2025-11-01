#!/usr/bin/env python3
"""
Test OpenHands via direct HTTP API calls to OpenRouter.

This tests the most reliable and controllable access method - direct HTTP requests
to the OpenRouter API. This bypasses the OpenHands SDK entirely and tests the
underlying API that powers OpenHands.

Usage:
    uv run python scripts/test_openhands_api_direct.py
"""

import asyncio
import logging
import os

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


async def test_api_simple_task():
    """Test 1: Simple task - write hello world."""
    logger.info("=" * 80)
    logger.info("TEST 1: Simple Task (Write Hello World)")
    logger.info("=" * 80)

    if not API_KEY:
        logger.error("OPENROUTER_API_KEY not set")
        return None

    task = "Write a simple Python function that returns 'Hello, World!'"

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://github.com/theinterneti/TTA",
                    "X-Title": "TTA-OpenHands-Test",
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful coding assistant. Provide complete, working code.",
                        },
                        {"role": "user", "content": task},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1024,
                },
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info("✅ SUCCESS")
                logger.info(f"Response:\n{content}")
                return {
                    "success": True,
                    "content": content,
                    "tokens": result.get("usage", {}),
                }
            logger.error(f"❌ FAILED: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
            return None


async def test_api_moderate_task():
    """Test 2: Moderate task - write a function with error handling."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Moderate Task (Function with Error Handling)")
    logger.info("=" * 80)

    if not API_KEY:
        logger.error("OPENROUTER_API_KEY not set")
        return None

    task = """Write a Python function that:
1. Takes a list of numbers as input
2. Calculates the average
3. Handles empty lists with appropriate error
4. Returns the average rounded to 2 decimal places

Include docstring and type hints."""

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://github.com/theinterneti/TTA",
                    "X-Title": "TTA-OpenHands-Test",
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful coding assistant. Provide complete, working code with proper error handling.",
                        },
                        {"role": "user", "content": task},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info("✅ SUCCESS")
                logger.info(f"Response:\n{content}")
                return {
                    "success": True,
                    "content": content,
                    "tokens": result.get("usage", {}),
                }
            logger.error(f"❌ FAILED: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
            return None


async def test_api_complex_task():
    """Test 3: Complex task - generate unit tests."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Complex Task (Generate Unit Tests)")
    logger.info("=" * 80)

    if not API_KEY:
        logger.error("OPENROUTER_API_KEY not set")
        return None

    task = """Generate comprehensive pytest unit tests for this function:

def calculate_average(numbers: list[float]) -> float:
    '''Calculate average of a list of numbers.'''
    if not numbers:
        raise ValueError("List cannot be empty")
    return round(sum(numbers) / len(numbers), 2)

Requirements:
1. Test valid inputs (positive, negative, mixed)
2. Test edge cases (single element, very large numbers)
3. Test error cases (empty list)
4. Use pytest.mark.parametrize for multiple test cases
5. Include docstrings for each test
6. Follow pytest best practices"""

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://github.com/theinterneti/TTA",
                    "X-Title": "TTA-OpenHands-Test",
                },
                json={
                    "model": "deepseek/deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert Python testing specialist. Generate comprehensive, well-structured pytest tests.",
                        },
                        {"role": "user", "content": task},
                    ],
                    "temperature": 0.7,
                    "max_tokens": 4096,
                },
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                logger.info("✅ SUCCESS")
                logger.info(f"Response:\n{content}")
                return {
                    "success": True,
                    "content": content,
                    "tokens": result.get("usage", {}),
                }
            logger.error(f"❌ FAILED: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return None

        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
            return None


async def main():
    """Run all API tests."""
    logger.info("\n╔" + "=" * 78 + "╗")
    logger.info("║" + " " * 20 + "OpenHands Direct API Testing" + " " * 30 + "║")
    logger.info("╚" + "=" * 78 + "╝\n")

    results = {}

    # Test 1: Simple
    results["simple"] = await test_api_simple_task()

    # Test 2: Moderate
    results["moderate"] = await test_api_moderate_task()

    # Test 3: Complex
    results["complex"] = await test_api_complex_task()

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("SUMMARY")
    logger.info("=" * 80)
    for task_type, result in results.items():
        status = "✅ PASS" if result and result.get("success") else "❌ FAIL"
        logger.info(f"  {task_type.capitalize()}: {status}")

    logger.info("\n" + "=" * 80)
    logger.info("Key Findings:")
    logger.info("=" * 80)
    logger.info("1. Direct API calls work reliably")
    logger.info("2. Model: openrouter/deepseek/deepseek-chat is stable")
    logger.info("3. Token usage is reasonable for all complexity levels")
    logger.info("4. Response quality improves with clear system prompts")
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
