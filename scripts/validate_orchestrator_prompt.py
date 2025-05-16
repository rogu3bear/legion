#!/usr/bin/env python3
"""
Validate the Orchestrator prompt template by sending a test message to a local LLM (LMStudio) and printing the raw response.

Usage:
  pip install openai
  # Ensure LMSTUDIO_API_URL is set in .env or environment
  python scripts/validate_orchestrator_prompt.py

  # Or override the API endpoint:
  python scripts/validate_orchestrator_prompt.py --api-base http://127.0.0.1:1234/v1
"""
import os
import json
import openai
import argparse
from dotenv import load_dotenv

# Parse command line arguments
parser = argparse.ArgumentParser(description="Validate the Orchestrator prompt template with a local LLM.")
parser.add_argument("--api-base", help="Override the LLM API base URL (default: from LMSTUDIO_API_URL env var)")
args = parser.parse_args()

# Load .env file for LMSTUDIO_API_URL
load_dotenv()

# Setup OpenAI client to point to LMStudio
API_BASE = args.api_base if args.api_base else os.getenv("LMSTUDIO_API_URL")
if not API_BASE:
    raise RuntimeError("LMSTUDIO_API_URL environment variable is not set. Please define it in your .env file or environment, or use --api-base.")

client = openai.OpenAI(base_url=API_BASE, api_key="lm-studio") # api_key can be anything for LM Studio

# Read the orchestrator prompt template
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # Assuming scripts is one level down from project root
template_path = os.path.join(project_root, "legion", "prompts", "orchestrator.md")

if not os.path.exists(template_path):
    raise FileNotFoundError(f"Orchestrator prompt template not found at: {template_path}")

with open(template_path, "r", encoding="utf-8") as f:
    system_prompt = f.read()

# Build chat messages
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Plan a health check for the entire system."}
]

# Call Local LLM (LMStudio)
print(f"Sending request to LLM at {API_BASE}...")
try:
    response = client.chat.completions.create(
        model="local-model", # Model name doesn't matter for LM Studio, but it's required by the API
        messages=messages,
        temperature=0.2,
    )
    # Extract and print the assistant's reply
    assistant_msg = response.choices[0].message.content
    print("Assistant's reply:")
    print(assistant_msg)
except openai.APIConnectionError as e:
    print(f"Error connecting to LLM at {API_BASE}: {e}")
    print("Please ensure LMStudio is running and the API server is enabled.")
except Exception as e:
    print(f"An unexpected error occurred: {e}") 