"""Capability-based agent routing map management."""

from collections import defaultdict
from typing import Dict, Iterable, List

from interface.schemas.agent import AgentStatusInfo

# Module-level routing table: capability -> list of agent names
_CAPABILITY_ROUTING: Dict[str, List[str]] = {}


def rebuild_routing_map(
    agent_statuses: Iterable[AgentStatusInfo]
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
