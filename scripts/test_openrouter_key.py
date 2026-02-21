#!/usr/bin/env python3
"""Test OpenRouter API key validity."""

# Logseq: [[TTA.dev/Scripts/Test_openrouter_key]]

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
    sys.exit(1)


# Test 1: Simple chat completion

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

    if response.status_code == 200:
        data = response.json()
        if "choices" in data and len(data["choices"]) > 0:
            pass
    elif response.status_code == 401:
        pass
    else:
        pass

except Exception:
    sys.exit(1)

# Test 2: Try with free model

payload["model"] = "deepseek/deepseek-v3:free"

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code in {200, 401}:
        pass
    else:
        pass

except Exception:
    pass
