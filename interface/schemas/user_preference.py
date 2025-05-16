"""Pydantic schemas for User Preferences."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Shared properties
class UserPreferenceBase(BaseModel):
    theme: Optional[str] = Field(
        "dark", description="Preferred UI theme ('dark' or 'light')."
    )
    notifications_enabled: Optional[bool] = Field(
        True, description="Whether UI notifications are enabled."
    )


# Properties to receive via API on creation (if needed, usually defaults are used)
class UserPreferenceCreate(UserPreferenceBase):
    """Schema used for creating user preferences (typically uses defaults)."""

    pass


# Properties to receive via API on update
class UserPreferenceUpdate(UserPreferenceBase):
    """Schema used for updating user preferences. Fields are optional."""

    theme: Optional[str] = Field(None, description="New UI theme ('dark' or 'light').")
    notifications_enabled: Optional[bool] = Field(
        None, description="New notification setting."
    )


# Properties shared by models stored in DB
class UserPreferenceInDBBase(UserPreferenceBase):
    user_id: int = Field(
        ..., description="The ID of the user these preferences belong to."
    )
    model_config = ConfigDict(from_attributes=True)


# Properties to return to client
class UserPreference(UserPreferenceInDBBase):
    """Schema for returning user preferences via the API."""

    pass


# Properties stored in DB
class UserPreferenceInDB(UserPreferenceInDBBase):
    """Schema representing user preferences as stored in the database."""

    pass
