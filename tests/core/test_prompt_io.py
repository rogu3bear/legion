"""Tests for core prompt I/O utility functions."""

from pathlib import Path
from unittest.mock import patch

import pytest

from core.utils.prompt_io import (
    PROMPT_FILE_EXTENSION,
    PROMPTS_DIR,
    get_prompt_file_path,
    load_prompt,
    prompt_exists,
    save_prompt,
)


class TestPromptIO:
    """Test cases for prompt I/O utility functions."""

    def test_load_prompt_success(self):
        """Test successful prompt loading."""
        mock_content = "# Test Agent Prompt\nThis is a test prompt."

        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", return_value=mock_content):

            result = load_prompt("test_agent")

        assert result == mock_content

    def test_load_prompt_file_not_found(self):
        """Test prompt loading when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError) as exc_info:
                load_prompt("nonexistent_agent")

        assert "Prompt file not found for agent: nonexistent_agent" in str(exc_info.value)

    def test_load_prompt_read_error(self):
        """Test prompt loading when file read fails."""
        with patch("pathlib.Path.exists", return_value=True), \
             patch("pathlib.Path.read_text", side_effect=PermissionError("Access denied")):

            with pytest.raises(IOError) as exc_info:
                load_prompt("test_agent")

        assert "Failed to read prompt for agent: test_agent" in str(exc_info.value)

    def test_save_prompt_success(self):
        """Test successful prompt saving."""
        test_content = "# Updated Prompt\nThis is updated content."

        with patch("pathlib.Path.mkdir") as mock_mkdir, \
             patch("pathlib.Path.write_text") as mock_write:

            save_prompt("test_agent", test_content)

            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_write.assert_called_once_with(test_content, encoding='utf-8')

    def test_save_prompt_write_error(self):
        """Test prompt saving when write fails."""
        test_content = "# Test Content"

        with patch("pathlib.Path.mkdir"), \
             patch("pathlib.Path.write_text", side_effect=PermissionError("Access denied")):

            with pytest.raises(IOError) as exc_info:
                save_prompt("test_agent", test_content)

        assert "Failed to save prompt for agent: test_agent" in str(exc_info.value)

    def test_prompt_exists_true(self):
        """Test prompt_exists returns True when file exists."""
        with patch("pathlib.Path.exists", return_value=True):
            result = prompt_exists("test_agent")

        assert result is True

    def test_prompt_exists_false(self):
        """Test prompt_exists returns False when file doesn't exist."""
        with patch("pathlib.Path.exists", return_value=False):
            result = prompt_exists("test_agent")

        assert result is False

    def test_get_prompt_file_path(self):
        """Test get_prompt_file_path returns correct path."""
        expected_path = PROMPTS_DIR / f"test_agent{PROMPT_FILE_EXTENSION}"
        result = get_prompt_file_path("test_agent")

        assert result == expected_path
        assert isinstance(result, Path)

    def test_constants(self):
        """Test that constants are set correctly."""
        assert Path("legion/prompts") == PROMPTS_DIR
        assert PROMPT_FILE_EXTENSION == ".md"

    def test_file_path_construction(self):
        """Test that file paths are constructed correctly."""
        agent_name = "doctor"
        expected_path = Path("legion/prompts/doctor.md")

        result = get_prompt_file_path(agent_name)

        assert result == expected_path
