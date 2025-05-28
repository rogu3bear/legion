"""
Interface models package - exposes all model classes for FastAPI endpoints.
"""

from .agent import Agent
from .user import User
from .user_preference import UserPreference

__all__ = [
    "Agent"
    "User", 
    "UserPreference"
] 