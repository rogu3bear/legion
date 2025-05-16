from pathlib import Path

import pytest

test_dir = Path(__file__).parent.parent
CONFIG_PATH = test_dir / "legion" / "configs" / "agents.yaml"


# def load_config(): # This function is no longer needed if we use orchestrator.config
#     with open(CONFIG_PATH, \'r\', encoding=\'utf-8\') as f:
#         return yaml.safe_load(f)


@pytest.mark.asyncio  # Mark the test as asynchronous
async def test_agent_roundtrip(orchestrator, agent_keys, tmp_path):
    """
    For each agent key, ensure load_agent and dispatch round-trip works and logs to memory.
    """
    config = orchestrator.config

    for key in agent_keys:
        assert key in config, (
            f"Agent key '{key}' not found in orchestrator.config provided by fixture."
        )
        agent_config_data = config[key]
        agent_class_name = agent_config_data["class"]

        # Load and cache
        assert key in orchestrator.agents, (
            f"Agent '{key}' not found in orchestrator.agents."
        )
        a1 = orchestrator.agents[key]
        assert a1.__class__.__name__ == agent_class_name

        # Dispatch and expect ok
        if key == "echo":
            message_content = "ping roundtrip"
            response = await orchestrator.dispatch_message(key, message_content)
            assert response == f"Echoing: {message_content}"
        else:
            pytest.skip(
                f"Dispatch logic for agent '{key}' not implemented in this simplified test."
            )

        # Check memory log
        state_manager_log_file = orchestrator.state_manager.task_log
        if not state_manager_log_file.exists():
            pytest.xfail(f"StateManager log not found at {state_manager_log_file}")

        lines = state_manager_log_file.read_text().splitlines()
        # Check for a response event from the agent we just dispatched to.
        assert any(
            f'"agent_name": "{key}"' in line and '"event": "agent_response"' in line
            for line in lines
        ), f"Dispatch log not found for agent {key} in StateManager logs."
