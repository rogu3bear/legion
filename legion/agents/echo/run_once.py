"""Simple echo consumer used in CI to verify ZMQ messaging."""

from __future__ import annotations

import argparse
import asyncio
import json

try:  # pragma: no cover - handle missing pyzmq in minimal env
    import zmq
    import zmq.asyncio as zmq_asyncio
except Exception:  # pragma: no cover - stub fallback
    import types

    zmq = types.SimpleNamespace(SUB=0)
    zmq_asyncio = None

try:  # pragma: no cover
    import redis
except Exception:  # pragma: no cover
    redis = None

from legion.ports import LEGION_PORT_MAP


async def run_once(redis_client=None, context=None, sub_addr=None, *, stub=False):
    if redis_client is None:
        if stub:
            from tests.stubs.fakeredis_stub import StrictRedis

            redis_client = StrictRedis()
        else:
            if redis is None:
                raise RuntimeError("Redis not available")
            redis_client = redis.StrictRedis(decode_responses=True)

    if context is None:
        ctx_cls = getattr(zmq_asyncio, "Context", None)
        if ctx_cls is None or not hasattr(ctx_cls, "instance"):
            # Stubbed zmq, just log a placeholder message
            placeholder = {"event": "stub"}
            redis_client.rpush("echo:log", json.dumps(placeholder))
            return placeholder
        ctx = ctx_cls.instance()
    else:
        ctx = context

    address = sub_addr or f"tcp://127.0.0.1:{LEGION_PORT_MAP['zmq_sub']}"
    sub = ctx.socket(getattr(zmq, "SUB", 0))
    sub.connect(address)
    if hasattr(sub, "subscribe"):
        sub.subscribe("")
    msg = await sub.recv_json()
    redis_client.rpush("echo:log", json.dumps(msg))
    if hasattr(sub, "close"):
        sub.close()
    return msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stub", action="store_true", help="use stub redis")
    args = parser.parse_args()
    asyncio.run(run_once(stub=args.stub))


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()
