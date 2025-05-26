"""
Tests for prompt management functionality including file locking.
"""

import threading
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from core.utils.file_operations import (
    get_all_prompts,
    list_available_agents,
    load_prompt,
    save_prompt,
)


class TestPromptOperations:
    """Test prompt CRUD operations and file locking."""

    def setup_method(self):
        """Set up test environment."""
        # Use test directory for prompts
        self.test_prompts_dir = Path("test_prompts")
        self.test_prompts_dir.mkdir(exist_ok=True)

        # Patch PROMPTS_DIR to use test directory
        self.prompts_dir_patcher = patch('core.utils.file_operations.PROMPTS_DIR', self.test_prompts_dir)
        self.prompts_dir_patcher.start()

    def teardown_method(self):
        """Clean up test environment."""
        self.prompts_dir_patcher.stop()

        # Clean up test files
        if self.test_prompts_dir.exists():
            for file in self.test_prompts_dir.glob("*.md"):
                file.unlink()
            self.test_prompts_dir.rmdir()

    def test_save_and_load_prompt_happy_path(self):
        """Test successful prompt save and load."""
        agent_name = "test_agent"
        content = "You are a helpful test agent."

        # Save prompt
        result = save_prompt(agent_name, content)
        assert result is True

        # Load prompt
        loaded_content = load_prompt(agent_name)
        assert loaded_content == content

    def test_load_nonexistent_prompt(self):
        """Test loading a prompt that doesn't exist."""
        result = load_prompt("nonexistent_agent")
        assert result is None

    def test_list_available_agents(self):
        """Test listing available agents."""
        # Create test prompts
        save_prompt("agent1", "Content 1")
        save_prompt("agent2", "Content 2")

        agents = list_available_agents()
        assert "agent1" in agents
        assert "agent2" in agents
        assert len(agents) == 2

    def test_get_all_prompts(self):
        """Test getting all prompts as dictionary."""
        # Create test prompts
        save_prompt("agent1", "Content 1")
        save_prompt("agent2", "Content 2")

        all_prompts = get_all_prompts()
        assert all_prompts["agent1"] == "Content 1"
        assert all_prompts["agent2"] == "Content 2"
        assert len(all_prompts) == 2

    def test_concurrent_write_conflict(self):
        """Test that concurrent writes result in proper conflict handling."""
        agent_name = "concurrent_test_agent"

        # Mock portalocker to simulate lock conflict
        with patch('core.utils.file_operations.portalocker') as mock_portalocker:
            # Create a proper LockException class
            class MockLockException(Exception):
                pass

            mock_portalocker.LockException = MockLockException
            mock_portalocker.lock.side_effect = MockLockException("Lock exception")
            mock_portalocker.LOCK_EX = 1
            mock_portalocker.LOCK_NB = 2

            # Should raise HTTPException with 409 status
            with pytest.raises(HTTPException) as exc_info:
                save_prompt(agent_name, "test content")

            assert exc_info.value.status_code == 409
            assert "currently being modified" in str(exc_info.value.detail)

    def test_concurrent_writes_with_threading(self):
        """Test actual concurrent writes using threading."""
        agent_name = "threading_test_agent"
        content1 = "Content from thread 1"
        content2 = "Content from thread 2"

        results = []
        exceptions = []

        def write_prompt(content, result_list, exception_list):
            try:
                result = save_prompt(agent_name, content)
                result_list.append(result)
            except Exception as e:
                exception_list.append(e)

        # Start two threads attempting to write simultaneously
        thread1 = threading.Thread(target=write_prompt, args=(content1, results, exceptions))
        thread2 = threading.Thread(target=write_prompt, args=(content2, results, exceptions))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

        # At least one should succeed, and if there's a conflict, should get proper exception
        assert len(results) >= 1 or len(exceptions) >= 1

        # Check final content exists
        final_content = load_prompt(agent_name)
        assert final_content is not None
        assert final_content in [content1, content2]

    def test_save_prompt_creates_directory(self):
        """Test that save_prompt creates the prompts directory if it doesn't exist."""
        # Remove test directory
        if self.test_prompts_dir.exists():
            for file in self.test_prompts_dir.glob("*.md"):
                file.unlink()
            self.test_prompts_dir.rmdir()

        # Save prompt should create directory
        result = save_prompt("test_agent", "test content")
        assert result is True
        assert self.test_prompts_dir.exists()

    def test_save_prompt_file_error(self):
        """Test save_prompt handles file system errors gracefully."""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = save_prompt("test_agent", "test content")
            assert result is False

    def test_load_prompt_file_error(self):
        """Test load_prompt handles file system errors gracefully."""
        # Create a prompt file first
        save_prompt("test_agent", "test content")

        # Mock read_text to raise an exception
        with patch.object(Path, 'read_text', side_effect=PermissionError("Permission denied")):
            result = load_prompt("test_agent")
            assert result is None
