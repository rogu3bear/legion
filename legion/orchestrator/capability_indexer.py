"""Utilities for exposing agent capabilities."""

from typing import Dict, List

from legion.agents.contracts import AGENT_CONTRACTS


def get_capabilities() -> Dict[str, List[str]]:
    """Return mapping of agent names to capability method names."""

    capabilities: Dict[str, List[str]] = {}
    for agent_name, contract in AGENT_CONTRACTS.items():
        capabilities[agent_name] = sorted(contract.__abstractmethods__)
    return capabilities
