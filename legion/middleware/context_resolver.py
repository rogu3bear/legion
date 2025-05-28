import os
import logging
from typing import Optional, Dict

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None

from legion.ports import get_port

from .log_utils import write_echo_log

logger = logging.getLogger(__name__)

REDIS_PORT = int(os.getenv("REDIS_PORT", get_port("redis") or 7600))
if redis is not None:
    try:
        _redis = redis.Redis(host="localhost", port=REDIS_PORT, decode_responses=True)
    except Exception as exc:  # pragma: no cover - connection optional
        logger.warning("Redis unavailable: %s", exc)
        _redis = None
else:  # pragma: no cover - dependency missing
    _redis = None


def count_tokens(prompt: str) -> int:
    """Rudimentary token counter based on whitespace."""
    return len(prompt.split())


def calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of ``text``."""
    if not text:
        return 0.0
    import math

    freq: Dict[str, int] = {}
    for char in text:
        freq[char] = freq.get(char, 0) + 1
    length = len(text)
    entropy = -sum((c / length) * math.log2(c / length) for c in freq.values())
    return round(entropy, 2)


async def resolve_prompt(prompt: str, context_key: str) -> Dict[str, Optional[str]]:
    """Resolve context and determine LM Studio fallback requirements."""
    token_count = count_tokens(prompt)
    entropy = calculate_entropy(prompt)

    context = _redis.get(context_key) if _redis else None

    fallback_enabled = os.getenv("THERAPIST_FALLBACK_ENABLED", "false").lower() == "true"
    use_lmstudio = False
    if (context is None and fallback_enabled) or token_count > 3200:
        use_lmstudio = True
        write_echo_log(
            "FallbackTriggered",
            token_count=token_count,
            entropy=entropy,
            fallback_model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF",
            used_lmstudio=True,
        )
    return {
        "context": context,
        "use_lmstudio": use_lmstudio,
        "token_count": token_count,
        "entropy": entropy,
    }
