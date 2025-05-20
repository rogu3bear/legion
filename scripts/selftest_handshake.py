import hmac
from legion.state_repo import StateRepo
from tests.stubs.fakeredis_stub import StrictRedis


def main() -> None:
    repo = StateRepo(StrictRedis())
    secret = "secret"
    resp = repo.initiate_handshake("agent1", "worker", ["do"])
    challenge = resp["challenge_token"]
    signature = hmac.new(secret.encode(), challenge.encode(), "sha256").hexdigest()
    token = repo.complete_handshake("agent1", signature, secret)
    agent = repo.get_agent("agent1")
    assert token
    assert agent["role"] == "worker"
    assert agent["caps"] == ["do"]
    print("[HANDSHAKE TEST] PASS")


if __name__ == "__main__":
    main()
