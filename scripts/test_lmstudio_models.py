import requests

LMSTUDIO_API = "http://127.0.0.1:1234/v1"


def list_models():
    resp = requests.get(f"{LMSTUDIO_API}/models")
    resp.raise_for_status()
    return resp.json()


def _completion_helper(model, prompt, image=None):
    data = {
        "model": model
        "messages": [{"role": "user", "content": prompt}]
    }
    if image:
        # Vision models use OpenAI's image input format
        data["messages"][0]["content"] = [
            {"type": "text", "text": prompt}
            {"type": "image_url", "image_url": {"url": image}}
        ]
    resp = requests.post(f"{LMSTUDIO_API}/chat/completions", json=data)
    resp.raise_for_status()
    return resp.json()


def main():
    print("Listing models...")
    models = list_models()
    print(models)

    print("\nTesting text model...")
    result = _completion_helper("meta-llama-3.1-8b-instruct", "Say hello from Legion!")
    print(result)

    print("\nTesting vision model (text only)...")
    result = _completion_helper("llama-3.2-11b-vision-instruct", "Describe this image:")
    print(result)

    # Vision test (replace with a real image URL if needed)
    print("\nTesting vision model (with dummy image)...")
    # Using a placeholder image URL (should be accessible by LM Studio)
    image_url = "https://placekitten.com/256/256"
    result = _completion_helper(
        "llama-3.2-11b-vision-instruct", "What do you see?", image=image_url
    )
    print(result)


def test_text_model():
    result = _completion_helper("meta-llama-3.1-8b-instruct", "Say hello from Legion!")
    assert "choices" in result


if __name__ == "__main__":
    main()
