import unittest
from legion.registration import RegistrationService

class FakeRedis:
    def __init__(self):
        self.store = {}
        self.lists = {}
    def set(self, key, value):
        self.store[key] = value
    def get(self, key):
        return self.store.get(key)
    def rpush(self, key, value):
        self.lists.setdefault(key, []).append(value)

class HandshakeTests(unittest.TestCase):
    def setUp(self):
        self.redis = FakeRedis()
        self.service = RegistrationService(host="", port=0)
        self.service.client = self.redis

    def test_successful_handshake(self):
        resp1 = self.service.handle({"phase": "INITIAL_REQUEST", "agent_id": "a1", "capabilities": []})
        challenge = resp1["challenge_token"]
        expected_sig = self.service.secret.encode()
        import hmac
        signed = hmac.new(expected_sig, challenge.encode(), "sha256").hexdigest()
        resp2 = self.service.handle({"phase": "AUTH_RESPONSE", "agent_id": "a1", "signed_challenge": signed})
        self.assertEqual(resp2["status"], "registered")

    def test_bad_signature(self):
        self.service.handle({"phase": "INITIAL_REQUEST", "agent_id": "a2", "capabilities": []})
        resp = self.service.handle({"phase": "AUTH_RESPONSE", "agent_id": "a2", "signed_challenge": "bad"})
        self.assertIn("error", resp)

if __name__ == "__main__":
    unittest.main()
