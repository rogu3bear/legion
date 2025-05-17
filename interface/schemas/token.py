"""Token related schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str = Field(..., description="The JWT access token.")
    token_type: str = Field(
        "bearer", description="The type of token (typically 'bearer')."
    )
    # refresh_token: Optional[str] = Field(None, description="Optional refresh token.") # Add if implementing refresh tokens


class TokenPayload(BaseModel):
    """Schema for the data encoded within the JWT token."""

    sub: Optional[str] = Field(
        None, description="Subject of the token (usually the username)."
    )


# This might not be strictly necessary if TokenPayload covers the needed data
class TokenData(BaseModel):
    """Schema for data extracted from the token during validation."""

    username: Optional[str] = Field(
        None, description="Username extracted from the token payload."
    )
