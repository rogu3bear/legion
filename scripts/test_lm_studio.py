#!/usr/bin/env python3
"""
Test LM Studio OpenAI-compatible endpoint for /v1/chat/completions.
"""

import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

# pick up configured base URL
base = os.getenv("OPENAI_API_BASE", "http://127.0.0.1:1234")
model = os.getenv("OPENAI_MODEL", "meta-llama-3.1-8b-instruct")
api_key = os.getenv("OPENAI_API_KEY", "lm-studio")

# Determine correct endpoint to avoid double '/v1'
if base.rstrip("/").endswith("/v1"):
    endpoint = "/chat/completions"
else:
    endpoint = "/v1/chat/completions"
url = base.rstrip("/") + endpoint
headers = {
    "Content-Type": "application/json"
    "Authorization": f"Bearer {api_key}"
}
data = {
    "model": model
    "messages": [{"role": "user", "content": "Hello, are you working?"}]
}

print(f"Testing LM Studio endpoint: {url}")
print(f"Model: {model}")
print(f"API Key: {api_key}")

try:
    resp = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
    print(f"Status code: {resp.status_code}")
    print("Raw response:")
    print(resp.text)
    try:
        j = resp.json()
        if "choices" in j:
            print("\nSUCCESS: 'choices' field found in response.")
        else:
            print(
                "\nERROR: 'choices' field NOT found in response! Check LM Studio model and config."
            )
    except Exception as e:
        print(f"\nERROR: Could not parse JSON: {e}")
except Exception as e:
    print(f"Request failed: {e}")
