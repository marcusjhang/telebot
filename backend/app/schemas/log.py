"""
Pydantic schemas for DailyLog and WeeklyLog models.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal


class DailyLogBase(BaseModel):
    """Base daily log schema"""
    log_date: date
    water_bottles: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=1)
    carb_portions: Decimal = Field(default=Decimal("0"), ge=0, decimal_places=1)
    exercise_sessions: int = Field(default=0, ge=0)


class DailyLogCreate(DailyLogBase):
    """Schema for creating a daily log"""
    pass


class DailyLogUpdate(BaseModel):
    """Schema for updating a daily log"""
    water_bottles: Decimal | None = Field(default=None, ge=0, decimal_places=1)
    carb_portions: Decimal | None = Field(default=None, ge=0, decimal_places=1)
    exercise_sessions: int | None = Field(default=None, ge=0)


class DailyLogResponse(DailyLogBase):
    """Schema for daily log response"""
    id: int
    user_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WeeklyLogBase(BaseModel):
    """Base weekly log schema"""
    week_start_date: date
    exercise_sessions: int = Field(default=0, ge=0)


class WeeklyLogCreate(WeeklyLogBase):
    """Schema for creating a weekly log"""
    pass


class WeeklyLogUpdate(BaseModel):
    """Schema for updating a weekly log"""
    exercise_sessions: int | None = Field(default=None, ge=0)


class WeeklyLogResponse(WeeklyLogBase):
    """Schema for weekly log response"""
    id: int
    user_id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DailyProgressResponse(BaseModel):
    """Schema for daily progress with goals"""
    log_date: date
    water_bottles: Decimal
    water_goal: Decimal
    water_progress: float  # Percentage
    carb_portions: Decimal
    carb_goal: Decimal
    carb_progress: float  # Percentage
    exercise_sessions: int
    
    class Config:
        from_attributes = True


class WeeklyProgressResponse(BaseModel):
    """Schema for weekly progress with goals"""
    week_start_date: date
    exercise_sessions: int
    exercise_goal: int
    exercise_progress: float  # Percentage
    
    class Config:
        from_attributes = True

