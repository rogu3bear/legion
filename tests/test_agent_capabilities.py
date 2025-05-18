from legion.agents.contracts import AGENT_CONTRACTS
from legion.orchestrator.capability_indexer import get_capabilities


def test_capability_mapping_matches_contracts():
    mapping = get_capabilities()
    for agent_name, contract in AGENT_CONTRACTS.items():
        assert set(mapping[agent_name]) == set(contract.__abstractmethods__)

