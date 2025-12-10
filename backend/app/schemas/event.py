"""
Pydantic schemas for Event model.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any


class EventBase(BaseModel):
    """Base event schema"""
    event_type: str = Field(..., pattern="^(water|carb|exercise)$")
    delta: Decimal = Field(..., decimal_places=1)
    subtype: Optional[str] = Field(None, pattern="^(meal|snack|custom)?$")
    portions: Optional[Decimal] = Field(None, decimal_places=1)


class EventCreate(EventBase):
    """Schema for creating an event"""
    message_id: Optional[int] = None
    callback_query_id: Optional[str] = None
    source: str = Field(default="bot", pattern="^(bot|web)$")
    metadata: Optional[Dict[str, Any]] = None


class EventResponse(EventBase):
    """Schema for event response"""
    id: int
    user_id: int
    occurred_at: datetime
    message_id: Optional[int]
    callback_query_id: Optional[str]
    source: str
    metadata: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class EventSummary(BaseModel):
    """Schema for event summary/analytics"""
    event_type: str
    total_count: int
    total_delta: Decimal
    avg_delta: Decimal
    
    class Config:
        from_attributes = True

