"""
Pydantic schemas for request/response validation.
"""
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserStats
from app.schemas.goal import GoalCreate, GoalUpdate, GoalResponse
from app.schemas.log import (
    DailyLogCreate,
    DailyLogUpdate,
    DailyLogResponse,
    WeeklyLogCreate,
    WeeklyLogUpdate,
    WeeklyLogResponse,
    DailyProgressResponse,
    WeeklyProgressResponse,
)
from app.schemas.event import EventCreate, EventResponse, EventSummary
from app.schemas.notification import NotificationCreate, NotificationUpdate, NotificationResponse
from app.schemas.auth import TelegramAuthData, TokenResponse, TokenData

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserStats",
    # Goal
    "GoalCreate",
    "GoalUpdate",
    "GoalResponse",
    # Log
    "DailyLogCreate",
    "DailyLogUpdate",
    "DailyLogResponse",
    "WeeklyLogCreate",
    "WeeklyLogUpdate",
    "WeeklyLogResponse",
    "DailyProgressResponse",
    "WeeklyProgressResponse",
    # Event
    "EventCreate",
    "EventResponse",
    "EventSummary",
    # Notification
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    # Auth
    "TelegramAuthData",
    "TokenResponse",
    "TokenData",
]
