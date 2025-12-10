"""
Pydantic schemas for Notification model.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any


class NotificationBase(BaseModel):
    """Base notification schema"""
    notification_type: str = Field(..., pattern="^(broadcast|recap|weekly_recap)$")
    payload: Dict[str, Any]


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    target_user_id: Optional[int] = None
    scheduled_for: Optional[datetime] = None


class NotificationUpdate(BaseModel):
    """Schema for updating notification status"""
    status: str = Field(..., pattern="^(pending|sent|failed)$")
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response"""
    id: int
    target_user_id: Optional[int]
    status: str
    scheduled_for: Optional[datetime]
    sent_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

