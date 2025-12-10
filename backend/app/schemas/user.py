"""
Pydantic schemas for User model.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema with common fields"""
    telegram_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating user preferences"""
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    broadcast_opt_out: Optional[bool] = None
    recap_enabled: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    timezone: str = "Asia/Singapore"
    broadcast_opt_out: bool
    recap_enabled: bool
    week_start_day: int
    created_at: datetime
    last_active: datetime
    is_active: bool
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserStats(BaseModel):
    """Schema for user statistics"""
    user_id: int
    current_streak: int
    longest_streak: int
    total_days_logged: int
    water_goal_met_days: int
    carb_goal_met_days: int
    
    class Config:
        from_attributes = True

