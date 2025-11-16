#!/usr/bin/env python3
"""
Test OpenRouter API Connection for Llama 3.3 8B Instruct

Simple test to verify OpenRouter API key and model access before running
full extended evaluation.
"""

import asyncio
import os
import sys
from pathlib import Path

import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


async def test_openrouter_connection():
    """Test basic OpenRouter API connection."""

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return False

    if api_key.startswith("sk-or-v1-placeholder"):
        return False

    # Test API connection
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://tta-storytelling.com",
        "X-Title": "TTA Extended Session Evaluation",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("data", [])

                    # Look for Llama 3.3 8B model
                    llama_model = None
                    for model in models:
                        if "llama-3.3-8b-instruct" in model.get("id", ""):
                            llama_model = model
                            break

                    if llama_model:
                        # Check pricing
                        pricing = llama_model.get("pricing", {})
                        if (
                            pricing.get("prompt") == "0"
                            and pricing.get("completion") == "0"
                        ):
                            pass
                        else:
                            pass

                        return True
                    for model in models:
                        if "llama" in model.get("id", "").lower():
                            pass
                    return False

                await response.text()
                return False

    except TimeoutError:
        return False
    except Exception:
        return False


async def test_simple_completion():
    """Test a simple completion request."""

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("sk-or-v1-placeholder"):
        return False

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://tta-storytelling.com",
        "X-Title": "TTA Extended Session Evaluation",
    }

    payload = {
        "model": "meta-llama/llama-3.3-8b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please respond with exactly: 'TTA Extended Evaluation Test Successful'",
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7,
    }

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.post(url, headers=headers, json=payload, timeout=30) as response,
        ):
            if response.status == 200:
                data = await response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    data["choices"][0]["message"]["content"]

                    # Check usage stats
                    usage = data.get("usage", {})
                    if usage:
                        pass

                    return True
                return False

            await response.text()
            return False

    except TimeoutError:
        return False
    except Exception:
        return False


async def main():
    """Run all connection tests."""

    # Test 1: Basic API connection
    connection_ok = await test_openrouter_connection()

    # Test 2: Simple completion (only if connection works)
    completion_ok = False
    if connection_ok:
        completion_ok = await test_simple_completion()

    # Summary

    if connection_ok:
        pass
    else:
        pass

    if completion_ok or connection_ok:
        pass
    else:
        pass

    if connection_ok and completion_ok:
        return True
    if not connection_ok:
        pass
    return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
