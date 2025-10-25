#!/usr/bin/env python3
"""Test OpenRouter API key validity."""

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
load_dotenv(env_file)

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    print("❌ OPENROUTER_API_KEY not found in .env")
    sys.exit(1)

print(f"✅ API key loaded: {api_key[:20]}...{api_key[-10:]} ({len(api_key)} chars)")
print(f"   Format: {'ysk-or-v1-' if api_key.startswith('ysk-or-v1-') else 'UNKNOWN'}")

# Test 1: Simple chat completion
print("\n" + "=" * 80)
print("Test 1: Simple Chat Completion")
print("=" * 80)

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://github.com/theinterneti/TTA",
    "X-Title": "TTA-OpenHands-Integration",
}
payload = {
    "model": "deepseek/deepseek-chat",
    "messages": [{"role": "user", "content": "Say hello in exactly 3 words"}],
    "max_tokens": 20,
}

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ API key is VALID and working!")
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            print(f"   Response: {data['choices'][0]['message']['content']}")
    elif response.status_code == 401:
        print("\n❌ API key is INVALID or EXPIRED")
        print("   Please generate a new key at: https://openrouter.ai/keys")
    else:
        print(f"\n⚠️  Unexpected status code: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Request failed: {e}")
    sys.exit(1)

# Test 2: Try with free model
print("\n" + "=" * 80)
print("Test 2: Free Model (deepseek-v3:free)")
print("=" * 80)

payload["model"] = "deepseek/deepseek-v3:free"

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text[:500]}")
    
    if response.status_code == 200:
        print("\n✅ Free model works!")
    elif response.status_code == 401:
        print("\n❌ Still getting 401 with free model")
    else:
        print(f"\n⚠️  Status: {response.status_code}")
        
except Exception as e:
    print(f"\n❌ Request failed: {e}")

print("\n" + "=" * 80)
print("Summary")
print("=" * 80)
print("If you see 401 errors above, your API key is invalid/expired.")
print("Generate a new key at: https://openrouter.ai/keys")
print("Then update OPENROUTER_API_KEY in .env file")

