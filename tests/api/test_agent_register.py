import unittest
from fastapi import FastAPI
import interface.api.v1.endpoints.agent as agent_ep
from tests.stubs.testclient import TestClient
from tests.stubs.fakeredis_stub import StrictRedis
from legion.state_repo import StateRepo


class AgentRegisterTests(unittest.TestCase):
    def setUp(self):
        self.redis = StrictRedis()
        self.repo = StateRepo(self.redis)
        agent_ep.state_repo = self.repo
        app = FastAPI()
        app.include_router(agent_ep.router)
        self.client = TestClient(app)

    def test_register_and_status(self):
        resp = self.client.post(
            "/agent/register",
            json={"id": "a1", "role": "worker", "caps": ["do"]},
        )
        self.assertEqual(resp.status_code, 200)
        token = resp.json()["token"]
        self.assertTrue(token)
        resp2 = self.client.get("/agent/a1/status")
        self.assertEqual(resp2.status_code, 200)
        data = resp2.json()
        self.assertEqual(data["id"], "a1")
        self.assertEqual(data["role"], "worker")
        self.assertIn("up_time", data)


if __name__ == "__main__":
    unittest.main()
