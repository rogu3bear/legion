"""Agent model for storing Legion agent configurations and state.

This module defines the Agent model which represents an AI agent in the Legion system.
Each agent has a unique configuration, state tracking, and activity history.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.orm import Session

from .base import BaseModel


class Agent(BaseModel):
    """Model for storing agent configurations and runtime state.

    Attributes:
        id: Unique identifier for the agent
        name: Unique name/identifier for the agent
        description: Human-readable description of the agent's purpose
        model: Name of the underlying AI model (e.g., 'gpt-4')
        temperature: Sampling temperature for model responses
        max_tokens: Maximum tokens per model response
        is_active: Whether the agent is currently active
        config: Additional configuration parameters as JSON
        created_at: Timestamp when agent was created
        last_active: Timestamp of agent's last activity
    """

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(500))
    model = Column(String(100), nullable=False)
    temperature = Column(Integer, default=0.7)
    max_tokens = Column(Integer, default=2000)
    is_active = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Index for faster lookups by name
    __table_args__ = (Index("ix_agents_name", "name"),)

    def __repr__(self) -> str:
        """String representation of Agent instance."""
        return f"<Agent(name='{self.name}', model='{self.model}', active={self.is_active})>"

    @classmethod
    def get_by_name(cls, session: Session, name: str) -> Optional["Agent"]:
        """Get agent by name.

        Args:
            session: Database session
            name: Agent name to look up

        Returns:
            Optional[Agent]: Agent instance if found, None otherwise
        """
        return session.query(cls).filter(cls.name == name).first()

    @classmethod
    def get_active(cls, session: Session) -> List["Agent"]:
        """Get all active agents.

        Args:
            session: Database session

        Returns:
            List[Agent]: List of active agent instances
        """
        return session.query(cls).filter(cls.is_active == True).all()

    def update_activity(self, session: Session) -> None:
        """Update agent's last_active timestamp.

        Args:
            session: Database session
        """
        self.last_active = datetime.utcnow()
        session.add(self)
        session.commit()

    def update_config(self, session: Session, config_updates: Dict[str, Any]) -> None:
        """Update agent's configuration.

        Args:
            session: Database session
            config_updates: Dictionary of configuration updates
        """
        if self.config is None:
            self.config = {}
        self.config.update(config_updates)
        session.add(self)
        session.commit()

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary containing all agent attributes
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "is_active": self.is_active,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
        }
