#!/usr/bin/env python3
"""
Investigate OpenRouter's available models and their actual IDs.

This script queries OpenRouter's /models endpoint to get the definitive list
of available models, then analyzes which ones are free and their correct IDs.

Usage:
    uv run python scripts/investigate_openrouter_models.py
"""

import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"

# Models we tried to test
ATTEMPTED_MODELS = [
    "google/gemma-2-9b-it:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "microsoft/phi-3-small-128k-instruct:free",
    "microsoft/phi-3-medium-128k-instruct:free",
    "alibaba/qwen-3-32b-instruct:free",
    "alibaba/qwen-3-72b-instruct:free",
    "nvidia/nemotron-4-340b-instruct:free",
    "meta-llama/llama-3.3-70b-instruct:free",
    "meta-llama/llama-3.2-90b-vision-instruct:free",
    "mistralai/mistral-nemo-12b-instruct-2407:free",
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
                "X-Title": "TTA-OpenRouter-Models-Investigation",
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


def analyze_models(models):
    """Analyze available models and categorize them."""
    if not models:
        print("❌ No models returned")
        return

    print("\n" + "=" * 100)
    print("OPENROUTER AVAILABLE MODELS ANALYSIS")
    print("=" * 100)

    # Categorize models
    free_models = []
    paid_models = []
    model_families = {}

    for model in models:
        model_id = model.get("id", "")
        pricing = model.get("pricing", {})
        prompt_price = pricing.get("prompt", 0)
        completion_price = pricing.get("completion", 0)

        # Extract family from model ID
        if "/" in model_id:
            family = model_id.split("/")[0]
        else:
            family = "unknown"

        if family not in model_families:
            model_families[family] = {"free": [], "paid": []}

        # Determine if free
        is_free = prompt_price == 0 and completion_price == 0

        if is_free:
            free_models.append(model_id)
            model_families[family]["free"].append(model_id)
        else:
            paid_models.append(model_id)
            model_families[family]["paid"].append(model_id)

    print(f"\n📊 SUMMARY")
    print(f"Total Models: {len(models)}")
    print(f"Free Models: {len(free_models)}")
    print(f"Paid Models: {len(paid_models)}")
    print(f"Model Families: {len(model_families)}")

    # Show free models by family
    print(f"\n🆓 FREE MODELS BY FAMILY")
    print("=" * 100)
    for family in sorted(model_families.keys()):
        free_count = len(model_families[family]["free"])
        paid_count = len(model_families[family]["paid"])
        if free_count > 0:
            print(f"\n{family.upper()} ({free_count} free, {paid_count} paid):")
            for model_id in sorted(model_families[family]["free"]):
                print(f"  ✅ {model_id}")

    # Check which attempted models are available
    print(f"\n🔍 ATTEMPTED MODELS STATUS")
    print("=" * 100)
    available_attempted = []
    unavailable_attempted = []

    for attempted in ATTEMPTED_MODELS:
        # Remove :free suffix for comparison
        attempted_base = attempted.replace(":free", "")
        found = False

        for model_id in free_models:
            if model_id == attempted_base or model_id == attempted:
                available_attempted.append((attempted, model_id))
                found = True
                break

        if not found:
            unavailable_attempted.append(attempted)

    print(f"\n✅ AVAILABLE ({len(available_attempted)}):")
    for attempted, actual in available_attempted:
        print(f"  {attempted} → {actual}")

    print(f"\n❌ UNAVAILABLE ({len(unavailable_attempted)}):")
    for attempted in unavailable_attempted:
        print(f"  {attempted}")

    # Look for similar models
    print(f"\n🔎 SIMILAR MODELS FOUND")
    print("=" * 100)
    for attempted in unavailable_attempted:
        attempted_base = attempted.replace(":free", "").lower()
        similar = []

        for model_id in free_models:
            model_lower = model_id.lower()
            # Check if any part matches
            if any(part in model_lower for part in attempted_base.split("/")):
                similar.append(model_id)

        if similar:
            print(f"\n{attempted}:")
            for model_id in similar:
                print(f"  → {model_id}")

    # Save detailed results
    output_file = Path("openrouter_models_analysis.json")
    with open(output_file, "w") as f:
        json.dump(
            {
                "total_models": len(models),
                "free_models_count": len(free_models),
                "paid_models_count": len(paid_models),
                "free_models": sorted(free_models),
                "model_families": {
                    family: {
                        "free": sorted(model_families[family]["free"]),
                        "paid": sorted(model_families[family]["paid"]),
                    }
                    for family in sorted(model_families.keys())
                },
                "attempted_models": ATTEMPTED_MODELS,
                "available_attempted": available_attempted,
                "unavailable_attempted": unavailable_attempted,
            },
            f,
            indent=2,
        )

    print(f"\n✅ Detailed results saved to: {output_file}")
    print("=" * 100 + "\n")

    return {
        "free_models": free_models,
        "model_families": model_families,
        "available_attempted": available_attempted,
        "unavailable_attempted": unavailable_attempted,
    }


def main():
    """Main investigation."""
    print("\n" + "=" * 100)
    print("INVESTIGATING OPENROUTER AVAILABLE MODELS")
    print("=" * 100)
    print(f"Start Time: {__import__('datetime').datetime.now().isoformat()}\n")

    print("📡 Querying OpenRouter /models endpoint...")
    models = get_available_models()

    if models:
        print(f"✅ Retrieved {len(models)} models from OpenRouter")
        analyze_models(models)
    else:
        print("❌ Failed to retrieve models")


if __name__ == "__main__":
    main()

