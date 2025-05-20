"""CRUD operations for User Preferences."""

from typing import Optional, cast

from interface import models, schemas
from sqlalchemy.orm import Session


def get_user_preference(db: Session, user_id: int) -> Optional[models.UserPreference]:
    """Get user preferences by user ID."""
    return cast(
        Optional[models.UserPreference],
        (
            db.query(models.UserPreference)
            .filter(models.UserPreference.user_id == user_id)
            .first()
        ),
    )


def create_user_preference(
    db: Session, user_id: int, preferences: schemas.UserPreferenceCreate
) -> models.UserPreference:
    """Create new user preferences (or update if they exist)."""
    db_prefs = get_user_preference(db, user_id=user_id)
    if db_prefs:
        # If prefs somehow already exist, update them instead of creating
        # Cast is safe here because db_prefs existence implies update_user_preference will find it and return UserPreference
        return cast(
            models.UserPreference,
            update_user_preference(db, user_id=user_id, preferences_update=preferences),
        )

    db_prefs = models.UserPreference(**preferences.model_dump(), user_id=user_id)
    db.add(db_prefs)
    db.commit()
    db.refresh(db_prefs)
    return db_prefs


def update_user_preference(
    db: Session, user_id: int, preferences_update: schemas.UserPreferenceUpdate
) -> Optional[models.UserPreference]:
    """Update existing user preferences."""
    db_prefs = get_user_preference(db, user_id=user_id)
    if not db_prefs:
        return None

    update_data = preferences_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_prefs, key, value)

    db.add(db_prefs)
    db.commit()
    db.refresh(db_prefs)
    return db_prefs
