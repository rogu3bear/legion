"""Minimal integration smoke test.

Launch orchestrator if available and send a health_ping via ZMQ.
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path for settings import
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.settings.ports import get_port

try:
    from legion.orchestrator.main import start_app
except Exception:  # pragma: no cover - orchestrator missing
    def start_app() -> None:
        logging.info("orchestrator stub running")

try:
    import zmq
except Exception:  # pragma: no cover - optional dependency
    class _FakeCtx:
        def socket(self, *_args, **_kwargs):
            class _Sock:
                def bind(self, *_a, **_k):
                    pass
                def send_json(self, *_a, **_k):
                    pass
                def close(self):
                    pass
            return _Sock()

        def term(self):
            pass

    class zmq:
        class Context:
            @staticmethod
            def instance():
                return _FakeCtx()
        PUB = 0


def main() -> None:
    start_app()
    ctx = zmq.Context.instance()
    sock = ctx.socket(zmq.PUB)
    # Use new settings helper for port management
    port = get_port("ORCHESTRATOR_ZMQ_PUB", 7608)
    sock.bind(f"tcp://127.0.0.1:{port}")
    sock.send_json({"type": "health_ping"})
    sock.close()
    ctx.term()


if __name__ == "__main__":  # pragma: no cover
    main()
