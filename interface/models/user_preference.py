"""SQLAlchemy model for User Preferences."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from interface.db.base import Base  # Assuming Base is correctly importable


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    theme = Column(String(50), default="dark", nullable=False)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    # Add other preferences as needed

    # Define relationship back to User (optional but good practice)
    user = relationship("User", back_populates="preferences")


# Add back_populates to User model if needed:
# In interface/models/user.py:
# from sqlalchemy.orm import relationship
# preferences = relationship("UserPreference", back_populates="user", uselist=False) # uselist=False for one-to-one
