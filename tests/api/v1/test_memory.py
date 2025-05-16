# tests/api/v1/test_memory.py

# Removed unused imports: AsyncMock, patch, pytest, HTTPException, settings, MemorySearchResponse
# from unittest.mock import AsyncMock, patch
# import pytest
# from fastapi import HTTPException  # Import HTTPException
from fastapi.testclient import TestClient

# Assuming your FastAPI app instance is created in interface.main
# Adjust the import path if necessary
from interface.main import app

# from interface.core.config import settings # Import settings
# from interface.schemas.memory import MemorySearchResponse # Import response model

client = TestClient(app)

# --- Mock Responses ---
# Added newline at end of file
