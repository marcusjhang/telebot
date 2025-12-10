"""
User management API routes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import User
from app.services.user_service import (
    create_or_update_user,
    update_user_preferences,
    get_broadcast_recipients
)
from app.dependencies import get_db, get_current_user, verify_bot_token


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_bot_token)
):
    """
    Create or update user (idempotent).
    Requires bot token authentication.
    """
    user = await create_or_update_user(
        db=db,
        telegram_user_id=user_data.telegram_user_id,
        username=user_data.username,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user profile.
    Requires user JWT authentication.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user preferences.
    Requires user JWT authentication.
    """
    user = await update_user_preferences(
        db=db,
        user_id=current_user.id,
        broadcast_opt_out=user_data.broadcast_opt_out,
        recap_enabled=user_data.recap_enabled,
        week_start_day=user_data.week_start_day
    )
    return user


@router.get("/broadcast-recipients")
async def get_broadcast_recipient_list(
    exclude_user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(verify_bot_token)
):
    """
    Get all users who haven't opted out of broadcasts.
    Requires bot token authentication (internal use only).
    """
    users = await get_broadcast_recipients(db, exclude_user_id)
    
    return [
        {
            "telegram_user_id": u.telegram_user_id,
            "first_name": u.first_name,
            "username": u.username
        }
        for u in users
    ]

