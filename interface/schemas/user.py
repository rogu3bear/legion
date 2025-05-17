"""User related schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# Shared properties
class UserBase(BaseModel):
    username: str = Field(..., description="Unique username for the user.")
    email: EmailStr = Field(..., description="Unique email address for the user.")
    is_active: bool = Field(
        True, description="Indicates if the user account is active."
    )
    is_superuser: bool = Field(
        False, description="Indicates if the user has administrative privileges."
    )


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(..., description="User's password (will be hashed).")


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = Field(
        None, description="Optional new password (will be hashed if provided)."
    )


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int = Field(..., description="Unique identifier for the user.")
    created_at: datetime = Field(
        ..., description="Timestamp when the user was created."
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the user was last updated."
    )

    class Config:
        orm_mode = True
        from_attributes = True  # Added for newer Pydantic versions


# Additional properties to return via API
class User(UserInDBBase):
    """Schema for returning user information via the API."""

    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    """Schema representing a user object as stored in the database."""

    hashed_password: str = Field(
        ..., description="Hashed password stored in the database."
    )
