"""Capability-based agent routing map management."""

from collections import defaultdict
from typing import Dict, Iterable, List, Optional

from interface.schemas.agent import AgentStatusInfo

# Module-level routing table: capability -> list of agent names
_CAPABILITY_ROUTING: Dict[str, List[str]] = {}

# Function-tag to agent mapping for direct routing
_FUNCTION_TAG_ROUTING: Dict[str, str] = {
    # Echo agent functions
    "echo_task": "echo",
    "log_payload": "echo",

    # Metrics agent functions
    "record_counter": "metrics",
    "record_gauge": "metrics",
    "record_histogram": "metrics",
    "get_metrics": "metrics",

    # Therapist agent functions
    "validate_intent": "therapist",
    "analyze_task": "therapist",
    "provide_feedback": "therapist",

    # Ping agent functions
    "ping": "ping",

    # Healthcheck agent functions
    "health_check": "healthcheck",

    # Architect agent functions
    "design_system": "architect",
    "review_architecture": "architect",

    # UX Designer agent functions
    "design_ui": "ux_designer",
    "review_ux": "ux_designer",
}


def rebuild_routing_map(
    agent_statuses: Iterable[AgentStatusInfo],
) -> Dict[str, List[str]]:
    """Build the routing map from agent status information."""
    capability_map: Dict[str, List[str]] = defaultdict(list)

    for agent in agent_statuses:
        for capability in agent.capabilities:
            if agent.name not in capability_map[capability]:
                capability_map[capability].append(agent.name)

    for agents in capability_map.values():
        agents.sort()

    global _CAPABILITY_ROUTING
    _CAPABILITY_ROUTING = dict(capability_map)
    return _CAPABILITY_ROUTING


def get_agents_for(capability: str) -> List[str]:
    """Return a list of agents that support the given capability."""
    return list(_CAPABILITY_ROUTING.get(capability, []))


def get_all_capabilities() -> Dict[str, List[str]]:
    """Get the full capability routing table."""
    return {cap: list(agents) for cap, agents in _CAPABILITY_ROUTING.items()}


def get_agent_for_function_tag(function_tag: str) -> Optional[str]:
    """Return the agent name that handles the given function_tag."""
    return _FUNCTION_TAG_ROUTING.get(function_tag)


def add_function_tag_mapping(function_tag: str, agent_name: str) -> None:
    """Add a new function_tag -> agent mapping."""
    _FUNCTION_TAG_ROUTING[function_tag] = agent_name


def remove_function_tag_mapping(function_tag: str) -> bool:
    """Remove a function_tag mapping. Returns True if it existed."""
    return _FUNCTION_TAG_ROUTING.pop(function_tag, None) is not None


def get_all_function_tags() -> Dict[str, str]:
    """Get the full function-tag routing table."""
    return dict(_FUNCTION_TAG_ROUTING)
