"""Security related utilities (hashing, JWT)."""

from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ALGORITHM = settings.ALGORITHM
SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Creates a JWT access token.

    Args:
        subject: The subject of the token (e.g., user ID or username).
        expires_delta: Optional timedelta for token expiry.
                       Defaults to ACCESS_TOKEN_EXPIRE_MINUTES.

    Returns:
        The encoded JWT access token.
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password.

    Args:
        plain_password: The plain text password.
        hashed_password: The hashed password from storage.

    Returns:
        True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a plain text password using bcrypt.

    Args:
        password: The plain text password.

    Returns:
        The hashed password.
    """
    return pwd_context.hash(password)


def decode_token(token: str) -> dict | None:
    """Decodes a JWT token.

    Args:
        token: The JWT token string.

    Returns:
        The decoded payload as a dictionary, or None if decoding fails.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
