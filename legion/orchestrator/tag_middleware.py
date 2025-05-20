from functools import wraps
from typing import Any, Callable, Dict, Iterable, List, Optional

CORE_TAG = "\ud83d\udd11[Core]"


def tag_payload(
    tags: Optional[Iterable[str]] = None,
) -> Callable[[Callable[..., Dict[str, Any]]], Callable[..., Dict[str, Any]]]:
    """Decorator to attach tags to a payload before calling the wrapped function."""

    provided_tags = list(tags) if tags else []

    def decorator(func: Callable[[Dict[str, Any]], Dict[str, Any]]):
        @wraps(func)
        def wrapper(
            payload: Dict[str, Any], *args: Any, **kwargs: Any
        ) -> Dict[str, Any]:
            combined: List[str] = [CORE_TAG]
            combined.extend(provided_tags)
            existing = payload.get("tags", [])
            if isinstance(existing, list):
                combined.extend(existing)
            else:
                combined.append(str(existing))
            payload["tags"] = combined
            return func(payload, *args, **kwargs)

        return wrapper

    return decorator
