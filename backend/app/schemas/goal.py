"""
Pydantic schemas for Goal model.
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal


class GoalBase(BaseModel):
    """Base goal schema"""
    daily_water_bottles: Decimal = Field(default=Decimal("3.0"), gt=0, decimal_places=1)
    daily_carb_max_portions: Decimal = Field(default=Decimal("4.0"), gt=0, decimal_places=1)
    weekly_exercise_sessions: int = Field(default=6, gt=0)


class GoalCreate(GoalBase):
    """Schema for creating a new goal"""
    effective_from: date


class GoalUpdate(BaseModel):
    """Schema for updating goals"""
    daily_water_bottles: Decimal | None = Field(default=None, gt=0, decimal_places=1)
    daily_carb_max_portions: Decimal | None = Field(default=None, gt=0, decimal_places=1)
    weekly_exercise_sessions: int | None = Field(default=None, gt=0)


class GoalResponse(GoalBase):
    """Schema for goal response"""
    id: int
    user_id: int
    effective_from: date
    created_at: datetime
    
    class Config:
        from_attributes = True

