#!/usr/bin/env python3
"""
Systematically discover all available free models on OpenRouter.

This script:
1. Queries OpenRouter's /models endpoint to get all available models
2. For each model, tries with :free suffix
3. Tests each model with a simple task
4. Documents which ones actually work

Usage:
    uv run python scripts/discover_all_free_models.py
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

# Simple test task
TEST_TASK = {
    "prompt": "Write a Python function that returns 'Hello, World!'",
    "max_tokens": 256,
}


def get_available_models():
    """Query OpenRouter's /models endpoint to get available models."""
    if not API_KEY:
        print("❌ API key not set")
        return None

    try:
        response = httpx.get(
            f"{BASE_URL}/models",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "HTTP-Referer": "https://github.com/theinterneti/TTA",
                "X-Title": "TTA-OpenRouter-Model-Discovery",
            },
            timeout=30.0,
        )

        if response.status_code != 200:
            print(f"❌ Failed to get models: HTTP {response.status_code}")
            return None

        data = response.json()
        return data.get("data", [])

    except Exception as e:
        print(f"❌ Error querying models: {e}")
        return None


async def test_model_with_free_suffix(model_id: str) -> dict:
    """Test if a model works with :free suffix."""
    if not API_KEY:
        return {"model": model_id, "success": False, "error": "API key not set"}

    # Try with :free suffix
    test_model_id = f"{model_id}:free"
    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "HTTP-Referer": "https://github.com/theinterneti/TTA",
                    "X-Title": "TTA-OpenRouter-Model-Discovery",
                },
                json={
                    "model": test_model_id,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful coding assistant.",
                        },
                        {"role": "user", "content": TEST_TASK["prompt"]},
                    ],
                    "temperature": 0.7,
                    "max_tokens": TEST_TASK["max_tokens"],
                },
            )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            return {
                "model": model_id,
                "model_with_suffix": test_model_id,
                "success": True,
                "time": elapsed,
            }
        if response.status_code == 429:
            return {
                "model": model_id,
                "model_with_suffix": test_model_id,
                "success": False,
                "error": "Rate limited (HTTP 429)",
                "time": elapsed,
            }
        if response.status_code == 404:
            return {
                "model": model_id,
                "model_with_suffix": test_model_id,
                "success": False,
                "error": "Not found (HTTP 404)",
                "time": elapsed,
            }
        return {
            "model": model_id,
            "model_with_suffix": test_model_id,
            "success": False,
            "error": f"HTTP {response.status_code}",
            "time": elapsed,
        }

    except asyncio.TimeoutError:
        return {
            "model": model_id,
            "model_with_suffix": test_model_id,
            "success": False,
            "error": "Timeout",
            "time": time.time() - start_time,
        }
    except Exception as e:
        return {
            "model": model_id,
            "model_with_suffix": test_model_id,
            "success": False,
            "error": str(e),
            "time": time.time() - start_time,
        }


async def main():
    """Main discovery process."""
    print("\n" + "=" * 100)
    print("DISCOVERING ALL AVAILABLE FREE MODELS ON OPENROUTER")
    print("=" * 100)
    print(f"Start Time: {datetime.now().isoformat()}\n")

    # Get all models
    print("📡 Querying OpenRouter /models endpoint...")
    all_models = get_available_models()

    if not all_models:
        print("❌ Failed to get models")
        return

    print(f"✅ Retrieved {len(all_models)} models from OpenRouter\n")

    # Group by family
    models_by_family = {}
    for model in all_models:
        model_id = model.get("id", "")
        if "/" in model_id:
            family = model_id.split("/")[0]
        else:
            family = "unknown"

        if family not in models_by_family:
            models_by_family[family] = []
        models_by_family[family].append(model_id)

    print("📊 Models by family:")
    for family in sorted(models_by_family.keys()):
        print(f"  {family}: {len(models_by_family[family])} models")

    # Test models with :free suffix
    print("\n🧪 Testing models with :free suffix...")
    print("=" * 100)

    results = []
    successful = []
    failed = []

    # Test a sample from each family
    for family in sorted(models_by_family.keys()):
        family_models = models_by_family[family]
        print(f"\n{family.upper()} ({len(family_models)} models):")

        # Test first 3 models from each family
        for model_id in family_models[:3]:
            result = await test_model_with_free_suffix(model_id)
            results.append(result)

            if result["success"]:
                successful.append(model_id)
                print(f"  ✅ {model_id} - {result['time']:.2f}s")
            else:
                failed.append(model_id)
                print(f"  ❌ {model_id} - {result['error']}")

    # Summary
    print("\n" + "=" * 100)
    print("DISCOVERY RESULTS SUMMARY")
    print("=" * 100)
    print(f"Total Models Tested: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")

    if successful:
        print("\n✅ WORKING FREE MODELS:")
        for model_id in sorted(successful):
            print(f"  {model_id}:free")

    # Save results
    output_file = Path("free_models_discovery_results.json")
    with open(output_file, "w") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "total_models_in_catalog": len(all_models),
                "models_tested": len(results),
                "successful": successful,
                "failed": failed,
                "results": results,
            },
            f,
            indent=2,
        )

    print(f"\n✅ Results saved to: {output_file}")
    print("=" * 100 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
