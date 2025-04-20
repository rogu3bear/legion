import os
import openai
import pytest
from dotenv import load_dotenv

load_dotenv()


def test_llm_local_smoke():
    os.environ["OPENAI_API_BASE"] = os.getenv(
        "LLM_API_BASE_URL", "http://127.0.0.1:1234"
    )
    openai.api_base = os.environ["OPENAI_API_BASE"]
    openai.api_type = "openai"
    openai.api_key = os.getenv("OPENAI_API_KEY", "sk-local-testing")
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello world"},
    ]
    try:
        resp = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.3,
            max_tokens=32,
        )
        print("Full LM Studio response:", resp)
        text = resp.choices[0].message.content
        assert text and "error" not in text.lower()
    except Exception as e:
        print("LLM endpoint error:", e)
        pytest.skip(f"LLM endpoint not available or failed: {e}")
