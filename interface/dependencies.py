"""Common FastAPI dependencies."""

import enum
from typing import Callable, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from interface.core import security
from interface.core.config import settings
from interface.crud import crud_user
from interface.db.session import SessionLocal
from interface.models.user import User


# Define Roles
class UserRole(str, enum.Enum):
    VIEWER = "viewer"
    AGENT_OPERATOR = "agent_operator"
    ADMIN = "admin"


# OAuth2PasswordBearer points to the *future* endpoint that provides the token
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a SQLAlchemy database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """Dependency to get the current user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED
        detail="Could not validate credentials"
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = security.decode_token(token)
        if payload is None:
            raise credentials_exception
        username_val = payload.get("sub")
        if username_val is None or not isinstance(username_val, str):
            raise credentials_exception
        username: str = username_val
    except (JWTError, ValidationError) as e:
        raise credentials_exception from e

    user = crud_user.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Dependency to get the current active user."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Dependency to ensure the user is an active superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def require_role(required_role: UserRole) -> Callable[[User], User]:
    """Dependency factory to require a specific user role."""

    def _require_role(current_user: User = Depends(get_current_active_user)) -> User:
        # Superusers implicitly have all roles
        if current_user.is_superuser:
            return current_user

        # TODO: More granular role hierarchy could be implemented here
        # For now, check if the user has the *exact* required role.
        # If a hierarchy is needed (e.g., ADMIN > AGENT_OPERATOR > VIEWER)
        # this logic needs expansion.
        if current_user.role != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN
                detail=f"User does not have the required '{required_role.value}' role"
            )
        return current_user

    return _require_role


# Example usage for specific roles (can be used directly in endpoint dependencies)
def require_admin_role(user: User = Depends(require_role(UserRole.ADMIN))) -> User:
    return user


def require_agent_operator_role(
    user: User = Depends(require_role(UserRole.AGENT_OPERATOR))
) -> User:
    return user


def require_viewer_role(user: User = Depends(require_role(UserRole.VIEWER))) -> User:
    # Note: Usually you just need get_current_active_user for viewer-level access
    return user
