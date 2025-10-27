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
    print("🔑 Testing OpenRouter API Connection")
    print("=" * 50)

    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY environment variable not set")
        print("💡 Run: ./testing/extended_evaluation/setup_api_key.sh")
        return False

    if api_key.startswith("sk-or-v1-placeholder"):
        print("⚠️  Using placeholder API key - this will fail")
        print("💡 Set your real OpenRouter API key to test connection")
        return False

    print(f"✅ API Key found: {api_key[:12]}...")

    # Test API connection
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://tta-storytelling.com",
        "X-Title": "TTA Extended Session Evaluation",
    }

    try:
        print("\n🌐 Testing API connection...")
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
                        print("✅ API connection successful")
                        print("✅ Llama 3.3 8B Instruct model available")
                        print(f"   Model ID: {llama_model['id']}")
                        print(
                            f"   Context Length: {llama_model.get('context_length', 'Unknown')}"
                        )

                        # Check pricing
                        pricing = llama_model.get("pricing", {})
                        if (
                            pricing.get("prompt") == "0"
                            and pricing.get("completion") == "0"
                        ):
                            print("✅ Model is free tier")
                        else:
                            print(
                                f"💰 Pricing - Prompt: ${pricing.get('prompt', 'Unknown')}, Completion: ${pricing.get('completion', 'Unknown')}"
                            )

                        return True
                    else:
                        print("❌ Llama 3.3 8B Instruct model not found")
                        print("Available models with 'llama' in name:")
                        for model in models:
                            if "llama" in model.get("id", "").lower():
                                print(f"   - {model['id']}")
                        return False

                else:
                    print(f"❌ API request failed: {response.status}")
                    error_text = await response.text()
                    print(f"Error: {error_text}")
                    return False

    except TimeoutError:
        print("❌ API request timed out")
        print("💡 Check your internet connection")
        return False
    except Exception as e:
        print(f"❌ API request failed: {e}")
        return False


async def test_simple_completion():
    """Test a simple completion request."""
    print("\n🧪 Testing Simple Completion")
    print("=" * 50)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key.startswith("sk-or-v1-placeholder"):
        print("⚠️  Skipping completion test - need real API key")
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
        print("📤 Sending test completion request...")
        async with aiohttp.ClientSession() as session, session.post(
            url, headers=headers, json=payload, timeout=30
        ) as response:
            if response.status == 200:
                data = await response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    print("✅ Completion successful!")
                    print(f"📝 Response: {content}")

                    # Check usage stats
                    usage = data.get("usage", {})
                    if usage:
                        print("📊 Token usage:")
                        print(f"   Prompt tokens: {usage.get('prompt_tokens', 0)}")
                        print(
                            f"   Completion tokens: {usage.get('completion_tokens', 0)}"
                        )
                        print(f"   Total tokens: {usage.get('total_tokens', 0)}")

                    return True
                else:
                    print("❌ No completion in response")
                    print(f"Response: {data}")
                    return False

            else:
                print(f"❌ Completion request failed: {response.status}")
                error_text = await response.text()
                print(f"Error: {error_text}")
                return False

    except TimeoutError:
        print("❌ Completion request timed out")
        return False
    except Exception as e:
        print(f"❌ Completion request failed: {e}")
        return False


async def main():
    """Run all connection tests."""
    print("🚀 OpenRouter Connection Test for TTA Extended Evaluation")
    print("=" * 70)

    # Test 1: Basic API connection
    connection_ok = await test_openrouter_connection()

    # Test 2: Simple completion (only if connection works)
    completion_ok = False
    if connection_ok:
        completion_ok = await test_simple_completion()

    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)

    if connection_ok:
        print("✅ OpenRouter API connection: PASSED")
    else:
        print("❌ OpenRouter API connection: FAILED")

    if completion_ok:
        print("✅ Llama 3.3 8B completion: PASSED")
    elif connection_ok:
        print("❌ Llama 3.3 8B completion: FAILED")
    else:
        print("⚠️  Llama 3.3 8B completion: SKIPPED (connection failed)")

    if connection_ok and completion_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Ready to run TTA Extended Evaluation with Llama 3.3 8B")
        print("\nNext steps:")
        print(
            "1. python testing/run_extended_evaluation.py --mode quick-sample --config testing/configs/production_extended_evaluation.yaml"
        )
        print(
            "2. python testing/run_extended_evaluation.py --mode comprehensive --config testing/configs/production_extended_evaluation.yaml"
        )
        return True
    else:
        print("\n❌ TESTS FAILED")
        print("💡 Fix the issues above before running extended evaluation")
        if not connection_ok:
            print("💡 Make sure you have a valid OpenRouter API key")
            print("💡 Run: ./testing/extended_evaluation/setup_api_key.sh")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
