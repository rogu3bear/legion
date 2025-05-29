"""Prometheus metrics FastAPI service."""
from __future__ import annotations

from fastapi import FastAPI, Response
from prometheus_client import REGISTRY, generate_latest
from legion.ports import get_port
import uvicorn

app = FastAPI()

@app.get("/metrics", response_class=Response)
def metrics() -> Response:
    data = generate_latest(REGISTRY)
    return Response(content=data, media_type="text/plain")


def main() -> None:
    port = get_port("metrics") or 7606
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":  # pragma: no cover
    main()
