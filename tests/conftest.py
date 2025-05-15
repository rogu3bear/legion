import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class DummyOrch:
    def __init__(self):
        self.name = "dummy"
        self.agent_channel_ids = {}
        self.call_directive = lambda *a, **k: None
        self.send_to_therapist = lambda *a, **k: None

        # Add other methods/attributes that test_agents.py might expect
        # For example, if it tries to access orchestrator.client.user.id for logging:
        class DummyUser:
            def __init__(self, id_val=12345):
                self.id = id_val
                self.display_name = "DummyUser"

        class DummyClient:
            def __init__(self):
                self.user = DummyUser()

        self.client = DummyClient()  # Add a dummy client
        self.get_alert_subscribers = lambda: []  # Add dummy get_alert_subscribers


# You can also make it a fixture if preferred
@pytest.fixture
def dummy_orchestrator():
    return DummyOrch()
