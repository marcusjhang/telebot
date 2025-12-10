"""
Notification model for broadcast notification queue.
Supports broadcasts, daily recaps, and weekly recaps.
"""
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_type = Column(String(50), nullable=False)  # 'broadcast', 'recap', 'weekly_recap'
    payload = Column(JSON, nullable=False)  # Notification data
    target_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # NULL for broadcast
    status = Column(String(20), nullable=False, default='pending')  # 'pending', 'sent', 'failed'
    scheduled_for = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status}, target_user={self.target_user_id})>"

