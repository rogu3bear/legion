import hmac
import unittest

from legion.state_repo import StateRepo
from tests.stubs.fakeredis_stub import StrictRedis


class StateRepoHandshakeTests(unittest.TestCase):
    def setUp(self):
        self.redis = StrictRedis()
        self.repo = StateRepo(self.redis)
        self.secret = "secret"

    def test_full_handshake(self):
        resp = self.repo.initiate_handshake("a1", "worker", ["do"])
        challenge = resp["challenge_token"]
        signed = hmac.new(
            self.secret.encode(), challenge.encode(), "sha256"
        ).hexdigest()
        token = self.repo.complete_handshake("a1", signed, self.secret)
        self.assertTrue(token)
        agent = self.repo.get_agent("a1")
        self.assertEqual(agent["role"], "worker")
        self.assertEqual(agent["caps"], ["do"])


if __name__ == "__main__":
    unittest.main()
