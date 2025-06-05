from sqlalchemy import create_engine

# from sqlalchemy.ext.declarative import declarative_base # Old way
from sqlalchemy.orm import DeclarativeBase  # New way

from interface.core.config import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,
    connect_args={"check_same_thread": False}
    if settings.SQLALCHEMY_DATABASE_URI.startswith("sqlite")
    else {},
)


# Base = declarative_base() # Old way
class Base(DeclarativeBase):  # New way
    pass


# Import all models here for Alembic autogenerate support
# Import models to register them with the Base class
try:
    from interface.models.user import User  # noqa
    from interface.models.agent import Agent  # noqa
    from interface.models.user_preference import UserPreference  # noqa
    from memory.db.models import Conversation, Directive  # noqa
except ImportError:
    pass
