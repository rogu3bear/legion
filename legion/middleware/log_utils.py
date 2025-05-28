import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def write_echo_log(event: str, **props: Any) -> str:
    """Write a structured Echo log entry.

    Parameters
    ----------
    event:
        Event name (e.g. ``"Retry"`` or ``"FallbackTriggered"``).
    props:
        Additional properties to include in the log. ``trace_id`` will be
        generated if not supplied.

    Returns
    -------
    str
        The trace_id used for the log entry.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    trace_id = props.get("trace_id")
    if trace_id is None:
        trace_id = hashlib.sha256(f"{timestamp}-{event}".encode()).hexdigest()
        props["trace_id"] = trace_id

    log_record: Dict[str, Any] = {
        "agent": "middleware",
        "event": event,
        "trace_id": trace_id,
    }
    log_record.update(props)

    log_dir = Path("logs/echo")
    log_dir.mkdir(parents=True, exist_ok=True)
    file_path = log_dir / f"{timestamp}_middleware_{trace_id}.json"
    with open(file_path, "w", encoding="utf-8") as fh:
        json.dump(log_record, fh)
    return trace_id
