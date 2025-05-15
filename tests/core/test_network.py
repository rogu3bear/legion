"""Tests for network utilities."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from legion.core.utils.network import fetch_with_retries


@patch("requests.get")
def test_fetch_with_retries_success(mock_get):
    """Test successful fetch after no retries."""
    mock_response = MagicMock(spec=requests.Response)
    mock_response.raise_for_status.return_value = None
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    response = fetch_with_retries("http://example.com")
    assert response == mock_response
    mock_get.assert_called_once_with("http://example.com")


@patch("requests.get")
@patch("time.sleep", return_value=None)  # Avoid actual sleep
def test_fetch_with_retries_fail_then_success(mock_sleep, mock_get):
    """Test successful fetch after one retry."""
    mock_success_response = MagicMock(spec=requests.Response)
    mock_success_response.raise_for_status.return_value = None
    mock_success_response.status_code = 200

    mock_get.side_effect = [
        requests.exceptions.Timeout("Timeout"),
        mock_success_response,
    ]

    response = fetch_with_retries("http://example.com", retries=3, delay=0.1)
    assert response == mock_success_response
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(0.1)


@patch("requests.get")
@patch("time.sleep", return_value=None)  # Avoid actual sleep
def test_fetch_with_retries_all_fail(mock_sleep, mock_get):
    """Test fetch fails after all retries."""
    mock_get.side_effect = requests.exceptions.RequestException("Failed")

    with pytest.raises(requests.exceptions.RequestException):
        fetch_with_retries("http://example.com", retries=3, delay=0.1)

    assert mock_get.call_count == 3
    assert mock_sleep.call_count == 2  # Sleeps between retries
