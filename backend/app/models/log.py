"""
Log models for daily and weekly aggregations.
DailyLog: Tracks water, carbs, and exercise per day
WeeklyLog: Tracks exercise sessions per week
"""
from sqlalchemy import Column, Integer, ForeignKey, Numeric, Date, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    log_date = Column(Date, nullable=False)  # In user's timezone (always Singapore)
    water_bottles = Column(Numeric(5, 1), nullable=False, default=0)
    carb_portions = Column(Numeric(5, 1), nullable=False, default=0)
    exercise_sessions = Column(Integer, nullable=False, default=0)  # Daily exercise count
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint('water_bottles >= 0', name='check_water_non_negative'),
        CheckConstraint('carb_portions >= 0', name='check_carb_non_negative'),
        CheckConstraint('exercise_sessions >= 0', name='check_exercise_non_negative'),
        UniqueConstraint('user_id', 'log_date', name='uq_user_log_date'),
    )
    
    def __repr__(self):
        return f"<DailyLog(id={self.id}, user_id={self.user_id}, date={self.log_date}, water={self.water_bottles}, carbs={self.carb_portions}, exercise={self.exercise_sessions})>"


class WeeklyLog(Base):
    __tablename__ = "weekly_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    week_start_date = Column(Date, nullable=False)  # Monday of the week
    exercise_sessions = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        CheckConstraint('exercise_sessions >= 0', name='check_weekly_exercise_non_negative'),
        UniqueConstraint('user_id', 'week_start_date', name='uq_user_week_start'),
    )
    
    def __repr__(self):
        return f"<WeeklyLog(id={self.id}, user_id={self.user_id}, week={self.week_start_date}, exercise={self.exercise_sessions})>"

