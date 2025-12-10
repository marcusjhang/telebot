"""
Event model for detailed audit trail and analytics.
Tracks all water, carb, and exercise events with metadata.
"""
from sqlalchemy import Column, Integer, BigInteger, ForeignKey, String, Numeric, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(20), nullable=False)  # 'water', 'carb', 'exercise'
    delta = Column(Numeric(5, 1), nullable=False)  # Can be negative for decreases
    subtype = Column(String(20), nullable=True)  # 'meal', 'snack', 'custom' for carbs
    portions = Column(Numeric(5, 1), nullable=True)  # Calculated portions for carbs
    occurred_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    message_id = Column(BigInteger, nullable=True)  # Telegram message ID for idempotency
    callback_query_id = Column(String(255), nullable=True, index=True)  # For deduplication
    source = Column(String(20), nullable=False, default='bot')  # 'bot' or 'web'
    metadata = Column(JSON, nullable=True)  # Extra data (e.g., quick button used)
    
    def __repr__(self):
        return f"<Event(id={self.id}, user_id={self.user_id}, type={self.event_type}, delta={self.delta}, occurred_at={self.occurred_at})>"

