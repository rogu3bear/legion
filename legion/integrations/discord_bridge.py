"""Simple Discord bridge stub."""

import argparse
import asyncio
import json
import os
from typing import Any, Dict

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    redis = None


def _get_client() -> "redis.StrictRedis | None":
    if redis is None:
        return None
    try:
        port = int(os.getenv("REDIS_PORT", "7810"))
        return redis.StrictRedis(host="localhost", port=port, decode_responses=True)
    except Exception:
        return None


def read_metrics() -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {}
    try:
        raw = client.get("metrics:latest")
    except Exception:
        return {}
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def format_embed(metrics: Dict[str, Any]) -> Dict[str, Any]:
    desc_lines = [f"Queue: {metrics.get('queue_depth', 0)}"]
    ages = metrics.get("agent_heartbeat_age", {})
    if ages:
        age_str = ", ".join(f"{k}:{v}s" for k, v in ages.items())
        desc_lines.append(f"Agents: {age_str}")
    payload = {
        "content": None,
        "embeds": [
            {
                "title": "Metrics Update",
                "description": "\\n".join(desc_lines),
                "color": 5814783,
            }
        ],
    }
    return payload


def post_to_discord(msg: str) -> None:
    """Pretend to send a message to Discord."""
    print(f"[discord] {msg}")


async def run_once() -> None:
    metrics = read_metrics()
    embed = format_embed(metrics)
    post_to_discord(json.dumps(embed))


async def main(interval: int = 60) -> None:
    while True:
        await run_once()
        await asyncio.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    args = parser.parse_args()
    if args.once:
        asyncio.run(run_once())
    else:
        asyncio.run(main())
