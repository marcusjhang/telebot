"""
Goal model for tracking user goals with effective dates.
Allows goal changes over time.
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class Goal(Base):
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    daily_water_bottles = Column(Numeric(4, 1), nullable=False, default=3.0)
    daily_carb_max_portions = Column(Numeric(4, 1), nullable=False, default=4.0)
    weekly_exercise_sessions = Column(Integer, nullable=False, default=6)
    effective_from = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint('daily_water_bottles > 0', name='check_water_positive'),
        CheckConstraint('daily_carb_max_portions > 0', name='check_carb_positive'),
        CheckConstraint('weekly_exercise_sessions > 0', name='check_exercise_positive'),
        UniqueConstraint('user_id', 'effective_from', name='uq_user_effective_from'),
    )
    
    def __repr__(self):
        return f"<Goal(id={self.id}, user_id={self.user_id}, water={self.daily_water_bottles}, carbs={self.daily_carb_max_portions}, exercise={self.weekly_exercise_sessions})>"

