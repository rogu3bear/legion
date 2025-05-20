"""Minimal integration smoke test.

Launch orchestrator if available and send a health_ping via ZMQ.
"""

import logging

try:
    from legion.orchestrator.main import start_app  # type: ignore
except Exception:  # pragma: no cover - orchestrator missing

    def start_app():  # type: ignore
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
    sock.bind("tcp://127.0.0.1:7808")
    sock.send_json({"type": "health_ping"})
    sock.close()
    ctx.term()


if __name__ == "__main__":  # pragma: no cover
    main()
