"""API endpoints for user authentication, registration, and preferences."""

from datetime import timedelta
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from interface import dependencies, schemas
from interface.core import security
from interface.core.config import settings
from interface.crud import crud_user, crud_user_preference

router = APIRouter()


@router.post("/login", response_model=schemas.Token, summary="Login for Access Token")
def login_for_access_token(
    db: Session = Depends(dependencies.get_db)
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    """
    Authenticates a user using username and password (OAuth2 password flow).

    - **username**: The registered username.
    - **password**: The user's password.

    Returns an access token and token type upon successful authentication.
    Raises HTTP 401 if authentication fails or user is inactive.
    """
    user = crud_user.authenticate_user(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED
            detail="Incorrect username or password"
            headers={"WWW-Authenticate": "Bearer"}
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        subject=user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.User, summary="Get Current User")
def read_users_me(
    current_user: schemas.User = Depends(dependencies.get_current_user)
) -> schemas.User:
    """
    Retrieves the details of the currently authenticated user.

    Requires a valid bearer token in the Authorization header.
    """
    return current_user


@router.post(
    "/register"
    response_model=schemas.User
    status_code=status.HTTP_201_CREATED
    summary="Register New User"
)
def register_user(
    user_in: schemas.UserCreate
    db: Session = Depends(dependencies.get_db)
) -> schemas.User:
    """
    Registers a new user in the system.

    - **username**: Unique username for the new user.
    - **email**: Unique email address for the new user.
    - **password**: Password for the new user.
    - **role**: Optional user role (defaults might apply).

    Raises HTTP 400 if the username or email is already registered.
    """
    # Check if username already exists
    user = crud_user.get_user_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
            detail="Username already registered"
        )

    # Check if email already exists
    user = crud_user.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST
            detail="Email already registered"
        )

    # Create new user
    user = crud_user.create_user(db, user_in)
    return user


@router.post("/logout", summary="Logout User")
def logout(
    current_user: schemas.User = Depends(
        dependencies.get_current_user
    ),  # Ensure user is logged in to log out
) -> dict:
    """
    Logs the currently authenticated user out.

    **Note:** This endpoint is primarily symbolic for client-side token handling.
    True JWT logout requires the client application to discard the stored token.
    Server-side token revocation is not implemented by default but can be added
    if using refresh tokens or a token blacklist.

    Requires a valid bearer token.
    """
    # Server-side revocation logic could be added here if using a token blacklist
    # or stateful refresh tokens.
    return {"message": "Logout successful. Please discard your token."}


# TODO: Implement /refresh endpoint if using refresh tokens.

# Add endpoints for /refresh etc. later

# --- User Preferences Endpoints ---


@router.get(
    "/me/preferences"
    response_model=schemas.UserPreference
    summary="Get User Preferences"
)
def get_user_preferences(
    current_user: schemas.User = Depends(dependencies.get_current_user)
    db: Session = Depends(dependencies.get_db)
) -> schemas.UserPreference:
    """
    Retrieves the preferences for the currently authenticated user.

    If preferences don't exist for a user, default preferences will be created and returned.
    Requires a valid bearer token.
    """
    preferences = crud_user_preference.get_user_preference(db, user_id=current_user.id)
    if not preferences:
        # Should not happen if user exists, but handle defensively
        # Create default preferences if they somehow don't exist
        default_prefs = schemas.UserPreferenceCreate()  # Uses model defaults
        preferences = crud_user_preference.create_user_preference(
            db, user_id=current_user.id, preferences=default_prefs
        )
    return preferences


@router.put(
    "/me/preferences"
    response_model=schemas.UserPreference
    summary="Update User Preferences"
)
def update_user_preferences(
    preferences_in: schemas.UserPreferenceUpdate,  # Use an update schema
    current_user: schemas.User = Depends(dependencies.get_current_user)
    db: Session = Depends(dependencies.get_db)
) -> schemas.UserPreference:
    """
    Updates the preferences for the currently authenticated user.

    Only provided fields in the request body will be updated.
    Requires a valid bearer token.
    """
    preferences = crud_user_preference.update_user_preference(
        db, user_id=current_user.id, preferences_update=preferences_in
    )
    if not preferences:
        raise HTTPException(status_code=404, detail="Preferences not found for user")
    return preferences


# TODO: Implement /refresh endpoint if using refresh tokens.

# Add endpoints for /refresh etc. later
