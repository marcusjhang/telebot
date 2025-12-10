"""
User model for storing Telegram user profiles and preferences.
All users are hardcoded to Asia/Singapore timezone.
"""
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    timezone = Column(String(50), nullable=False, default="Asia/Singapore")
    broadcast_opt_out = Column(Boolean, default=False, nullable=False)
    recap_enabled = Column(Boolean, default=True, nullable=False)
    week_start_day = Column(Integer, default=1, nullable=False)  # 0=Sunday, 1=Monday
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_active = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_user_id={self.telegram_user_id}, username={self.username})>"

