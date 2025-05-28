import sys
import unittest
from pathlib import Path
from unittest import mock

# Add the project root to the Python path to ensure imports work correctly
sys.path.insert(0, str(Path(__file__).parent.parent))

from legion.orchestrator import AgentLoadError, Orchestrator


class MockOrchestrator(Orchestrator):
    """A mock Orchestrator that skips agent initialization in __init__."""

    def __init__(self, state_manager=None, llm_client=None):
        # Skip the parent __init__ and do a minimal setup
        self.agents = {}
        self._agent_instances = {}
        self.state_manager = state_manager
        self.llm_client = llm_client
        self.config = {}
        self.agent_channel_ids = {}


class TestOrchestratorLoadAgent(unittest.TestCase):
    """Test cases for the Orchestrator.load_agent method."""

    def setUp(self):
        """Set up test fixtures before each test."""
        # Create a mock state manager and LLM client
        self.mock_state_manager = mock.MagicMock()
        self.mock_llm_client = mock.MagicMock()

        # Create the mock orchestrator without full initialization
        self.orchestrator = MockOrchestrator(
            state_manager=self.mock_state_manager, llm_client=self.mock_llm_client
        )

        # Set up test configs
        self.orchestrator.config = {
            "architect": {
                "name": "architect"
                "class": "ArchitectAgent"
                "prompt": "Test prompt"
                "channel_id": 123
            }
            "therapist": {
                "name": "therapist"
                "class": "TherapistAgent"
                "prompt": "Test prompt"
                "channel_id": 456
            }
        }

    @mock.patch("importlib.import_module")
    def test_successful_load(self, mock_import):
        """Test that load_agent successfully loads and returns an agent instance."""
        # Create a mock agent class and instance
        mock_agent_class = mock.MagicMock()
        mock_agent = mock.MagicMock()
        mock_agent_class.return_value = mock_agent

        # Configure the mock module
        mock_module = mock.MagicMock()
        mock_module.ArchitectAgent = mock_agent_class
        mock_import.return_value = mock_module

        # Call the method under test
        agent = self.orchestrator.load_agent("architect")

        # Verify results
        self.assertEqual(agent, mock_agent)
        mock_import.assert_called_once_with("legion.agents.python.architect")
        mock_agent_class.assert_called_once_with(
            orchestrator=self.orchestrator, llm_client=self.mock_llm_client
        )

    @mock.patch("importlib.import_module")
    def test_caching_behavior(self, mock_import):
        """Test that two calls to load_agent return the same instance (from cache)."""
        # Create a mock agent class and instance
        mock_agent_class = mock.MagicMock()
        mock_agent = mock.MagicMock()
        mock_agent_class.return_value = mock_agent

        # Configure the mock module with all needed agent classes
        mock_module = mock.MagicMock()
        mock_module.ArchitectAgent = mock_agent_class
        mock_import.return_value = mock_module

        # First call to load_agent
        agent1 = self.orchestrator.load_agent("architect")

        # Second call to load_agent
        agent2 = self.orchestrator.load_agent("architect")

        # Verify results
        self.assertIs(agent1, agent2)  # Same object identity
        mock_import.assert_called_once()  # Import only called once
        mock_agent_class.assert_called_once()  # Constructor only called once

    def test_unknown_key(self):
        """Test that load_agent raises KeyError for unknown agent keys."""
        with self.assertRaises(KeyError) as context:
            self.orchestrator.load_agent("nonexistent")

        self.assertIn("Unknown agent key: nonexistent", str(context.exception))

    @mock.patch("importlib.import_module")
    def test_import_failure(self, mock_import):
        """Test that load_agent raises AgentLoadError when import fails."""
        # Make import_module raise ImportError
        mock_import.side_effect = ImportError("Module not found")

        with self.assertRaises(AgentLoadError) as context:
            self.orchestrator.load_agent("architect")

        self.assertIn(
            "Failed to import module for agent 'architect'", str(context.exception)
        )

    @mock.patch("importlib.import_module")
    def test_class_not_found(self, mock_import):
        """Test that load_agent raises AgentLoadError when the agent class is not found."""
        # Configure a mock module without the expected class
        mock_module = mock.MagicMock(spec=[])
        mock_import.return_value = mock_module

        with self.assertRaises(AgentLoadError) as context:
            self.orchestrator.load_agent("architect")

        self.assertIn("Failed to get class 'ArchitectAgent'", str(context.exception))

    @mock.patch("importlib.import_module")
    def test_instantiation_failure(self, mock_import):
        """Test that load_agent raises AgentLoadError when instantiation fails."""
        # Create a mock agent class that raises an exception when instantiated
        mock_agent_class = mock.MagicMock(side_effect=Exception("Initialization error"))

        # Configure the mock module
        mock_module = mock.MagicMock()
        mock_module.ArchitectAgent = mock_agent_class
        mock_import.return_value = mock_module

        with self.assertRaises(AgentLoadError) as context:
            self.orchestrator.load_agent("architect")

        self.assertIn("Failed to instantiate agent 'architect'", str(context.exception))

    @mock.patch("importlib.import_module")
    def test_ci_smoke_check(self, mock_import):
        """Test all agent keys in the config to verify they can be loaded without error."""
        # Create a mock agent class and instance
        mock_agent_class = mock.MagicMock()
        mock_agent = mock.MagicMock()
        mock_agent_class.return_value = mock_agent

        # Configure the mock module with all needed agent classes
        mock_module = mock.MagicMock()
        mock_module.ArchitectAgent = mock_agent_class
        mock_module.TherapistAgent = mock_agent_class
        mock_import.return_value = mock_module

        # Test all agent keys in the config
        for agent_key in self.orchestrator.config:
            # This should complete without error for the smoke check to pass
            agent = self.orchestrator.load_agent(agent_key)
            self.assertIsNotNone(agent)


if __name__ == "__main__":
    unittest.main()
