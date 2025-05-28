import asyncio
import json


class Response:
    def __init__(self, status_code: int, body: bytes) -> None:
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body.decode())


class TestClient:
    """Minimal ASGI test client using only stdlib."""

    def __init__(self, app):
        self.app = app

    def _run(self, method: str, path: str, payload=None):
        body = json.dumps(payload).encode() if payload is not None else b""
        scope = {
            "type": "http"
            "method": method
            "path": path
            "query_string": b""
            "headers": []
        }
        messages = []

        async def send(msg):
            messages.append(msg)

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        asyncio.get_event_loop().run_until_complete(self.app(scope, receive, send))
        status = next(m["status"] for m in messages if m["type"] == "http.response.start")
        body_bytes = b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body")
        return Response(status, body_bytes)

    def post(self, path, json=None):
        return self._run("POST", path, payload=json)

    def get(self, path):
        return self._run("GET", path)
