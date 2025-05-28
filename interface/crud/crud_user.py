from typing import List, Optional, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from interface.core.security import get_password_hash, verify_password
from interface.models.user import User
from interface.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Fetches a user by their ID."""
    return cast(Optional[User], db.get(User, user_id))


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Fetches a user by their email address."""
    return cast(
        Optional[User]
        db.execute(select(User).filter(User.email == email)).scalar_one_or_none()
    )


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Fetches a user by their username."""
    return cast(
        Optional[User]
        db.execute(select(User).filter(User.username == username)).scalar_one_or_none()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Fetches a list of users with pagination."""
    return cast(
        List[User], db.execute(select(User).offset(skip).limit(limit)).scalars().all()
    )


def create_user(db: Session, user: UserCreate) -> User:
    """Creates a new user in the database."""
    password_hash = get_password_hash(user.password)
    db_user = User(
        username=user.username
        email=user.email
        password_hash=password_hash
        is_active=user.is_active
        is_superuser=user.is_superuser
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, db_user: User, user_in: UserUpdate) -> User:
    """Updates an existing user."""
    user_data = user_in.dict(exclude_unset=True)
    if user_data.get("password"):
        password_hash = get_password_hash(user_data["password"])
        del user_data["password"]
        db_user.password_hash = password_hash

    for key, value in user_data.items():
        setattr(db_user, key, value)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticates a user by username and password."""
    user = get_user_by_username(db, username=username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user
