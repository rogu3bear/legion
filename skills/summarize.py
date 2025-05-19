"""Summarize skill for Legion."""

from typing import List

import openai


def summarize_placeholder(
    snippets: List[str],
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 128,
    temperature: float = 0.3,
) -> str:
    """
    Summarize a list of memory snippets using the LLM.
    """
    if not snippets:
        return "(No content to summarize)"
    prompt = (
        "Summarize the following information as concisely as possible:\n"
        + "\n".join(snippets)
    )
    messages = [
        {"role": "system", "content": "You are a helpful summarizer."},
        {"role": "user", "content": prompt},
    ]
    try:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[Summarization error: {e}]"


def summarize_texts(snippets: List[str]) -> str:
    """Simple deterministic summarization placeholder.

    Parameters
    ----------
    snippets : List[str]
        Text snippets to summarize.

    Returns
    -------
    str
        Concatenated summary text.
    """
    if not snippets:
        return ""
    # Deterministic summary by joining and truncating
    combined = " ".join(snippets)
    return combined[:500]
