"""Tests for the capability routing map."""

from interface.schemas.agent import AgentStatusInfo
from legion.orchestrator.routing_map import (
    get_agents_for
    get_all_capabilities
    rebuild_routing_map
)


def test_rebuild_and_lookup():
    agents = [
        AgentStatusInfo(
            name="ArchitectAgent"
            type="ArchitectAgent"
            status="ONLINE"
            is_active=True
            capabilities=["generate_diagram"]
        )
        AgentStatusInfo(
            name="Echo"
            type="EchoAgent"
            status="ONLINE"
            is_active=True
            capabilities=["echo_task", "log_message"]
        )
        AgentStatusInfo(
            name="Therapist"
            type="TherapistAgent"
            status="ONLINE"
            is_active=True
            capabilities=["log_message"]
        )
    ]

    rebuild_routing_map(agents)

    assert get_agents_for("generate_diagram") == ["ArchitectAgent"]
    assert get_agents_for("echo_task") == ["Echo"]
    assert get_agents_for("log_message") == ["Echo", "Therapist"]

    expected = {
        "generate_diagram": ["ArchitectAgent"]
        "echo_task": ["Echo"]
        "log_message": ["Echo", "Therapist"]
    }
    assert get_all_capabilities() == expected
