"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, Field
from typing import Optional


class TelegramAuthData(BaseModel):
    """Schema for Telegram Login Widget authentication data"""
    id: int = Field(..., description="Telegram user ID")
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int = Field(..., description="Unix timestamp of authentication")
    hash: str = Field(..., description="HMAC-SHA256 signature")


class TokenResponse(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class TokenData(BaseModel):
    """Schema for decoded JWT token data"""
    telegram_user_id: int
    exp: Optional[int] = None

