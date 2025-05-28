#!/usr/bin/env bash
set - e

python << "PY"
import time
from tests.stubs.fakeredis_stub import StrictRedis
from legion.agents.echo import EchoAgent, EchoEvent
from interface.api.v1.endpoints import echo as echo_ep

r = StrictRedis()
agent = EchoAgent(redis_url="redis://localhost")
agent._redis = r
for i in range(10):
    evt = EchoEvent(
        timestamp=time.time(),
        level="info" if i % 2 == 0 else "debug",
        agent_id=f"a{i % 3}",
        payload={"i": i},
    )
    agent.record(evt)

echo_ep.get_redis_client = lambda: r
res = echo_ep.search_echo(level="info", limit=5)
assert len(res["events"]) == 5
for ev in res["events"]:
    assert ev["level"] == "info"
print("Echo self-test passed")
PY
