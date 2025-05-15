"""Tests for Authentication and User Preference API endpoints."""

from typing import Dict

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from interface import crud
from interface.api.v1 import schemas
from interface.core.config import settings
from tests.utils import (
    random_email,
    random_lower_string,
)


# --- Test User Registration ---
def test_register_user(client: TestClient, db: Session) -> None:
    """Test user registration."""
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    data = {"username": username, "email": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    assert r.status_code == 201
    created_user = r.json()
    assert created_user["username"] == username
    assert created_user["email"] == email
    assert "id" in created_user
    # Check user exists in DB
    user_in_db = crud.get_user_by_username(db, username=username)
    assert user_in_db
    assert user_in_db.username == username


def test_register_existing_username(client: TestClient, db: Session) -> None:
    """Test registration with an existing username."""
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    # Create initial user
    user_in = schemas.UserCreate(username=username, email=email, password=password)
    crud.create_user(db=db, user=user_in)
    # Attempt to register again
    data = {"username": username, "email": random_email(), "password": password}
    r = client.post(f"{settings.API_V1_STR}/auth/register", json=data)
    assert r.status_code == 400
    assert "Username already registered" in r.json()["detail"]


# --- Test User Login ---
def test_login_access_token(client: TestClient, db: Session) -> None:
    """Test getting an access token via form data."""
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        username=username, email=random_email(), password=password
    )
    crud.create_user(db=db, user=user_in)

    login_data = {"username": username, "password": password}
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert r.status_code == 200
    tokens = r.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_incorrect_password(client: TestClient, db: Session) -> None:
    """Test login with incorrect password."""
    username = random_lower_string()
    password = random_lower_string()
    user_in = schemas.UserCreate(
        username=username, email=random_email(), password=password
    )
    crud.create_user(db=db, user=user_in)

    login_data = {"username": username, "password": "wrongpassword"}
    r = client.post(f"{settings.API_V1_STR}/auth/login", data=login_data)
    assert r.status_code == 401
    assert "Incorrect username or password" in r.json()["detail"]


# --- Test Get Current User (/me) ---
def test_get_current_user(
    client: TestClient, normal_user_token_headers: Dict[str, str]
) -> None:
    """Test getting the current user."""
    r = client.get(f"{settings.API_V1_STR}/auth/me", headers=normal_user_token_headers)
    assert r.status_code == 200
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert "email" in current_user  # Check PII is included by default


# --- Test Logout ---
def test_logout(client: TestClient, normal_user_token_headers: Dict[str, str]) -> None:
    """Test the placeholder logout endpoint."""
    r = client.post(
        f"{settings.API_V1_STR}/auth/logout", headers=normal_user_token_headers
    )
    assert r.status_code == 200
    assert r.json() == {"message": "Logout successful. Please discard your token."}


# --- Test User Preferences ---
def test_get_user_preferences(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """Test getting user preferences (should create defaults if none exist)."""
    r = client.get(
        f"{settings.API_V1_STR}/auth/me/preferences", headers=normal_user_token_headers
    )
    assert r.status_code == 200
    preferences = r.json()
    assert preferences["theme"] == "dark"  # Default value
    assert preferences["notifications_enabled"] is True  # Default value
    assert "user_id" in preferences


def test_update_user_preferences(
    client: TestClient, normal_user_token_headers: Dict[str, str], db: Session
) -> None:
    """Test updating user preferences."""
    # First, ensure preferences exist (get endpoint creates them)
    client.get(
        f"{settings.API_V1_STR}/auth/me/preferences", headers=normal_user_token_headers
    )

    update_data = {"theme": "light", "notifications_enabled": False}
    r = client.put(
        f"{settings.API_V1_STR}/auth/me/preferences",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert r.status_code == 200
    updated_preferences = r.json()
    assert updated_preferences["theme"] == "light"
    assert updated_preferences["notifications_enabled"] is False

    # Verify in DB
    user_r = client.get(
        f"{settings.API_V1_STR}/auth/me", headers=normal_user_token_headers
    )
    user_id = user_r.json()["id"]
    db_prefs = crud.get_user_preference(db, user_id=user_id)
    assert db_prefs
    assert db_prefs.theme == "light"
    assert db_prefs.notifications_enabled is False
