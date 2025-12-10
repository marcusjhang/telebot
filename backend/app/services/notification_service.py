"""
Notification service for managing broadcast and recap notifications.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def queue_broadcast(
    db: AsyncSession,
    user_id: int,
    event_type: str,
    delta: float,
    new_total: float,
    metadata: Optional[Dict[str, Any]] = None
) -> Notification:
    """
    Queue a broadcast notification.
    
    Args:
        db: Database session
        user_id: User ID who triggered the event
        event_type: Type of event ('water', 'carb', 'exercise')
        delta: Change amount
        new_total: New total value
        metadata: Additional metadata
        
    Returns:
        Created notification
    """
    payload = {
        "user_id": user_id,
        "event_type": event_type,
        "delta": delta,
        "new_total": new_total,
        **(metadata or {})
    }
    
    notification = Notification(
        notification_type='broadcast',
        payload=payload,
        target_user_id=None,  # Broadcast to all
        status='pending'
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def queue_daily_recap(
    db: AsyncSession,
    user_id: int,
    scheduled_for: datetime
) -> Notification:
    """
    Queue a daily recap notification for a specific user.
    
    Args:
        db: Database session
        user_id: User ID
        scheduled_for: When to send the recap
        
    Returns:
        Created notification
    """
    payload = {
        "user_id": user_id,
        "recap_type": "daily"
    }
    
    notification = Notification(
        notification_type='recap',
        payload=payload,
        target_user_id=user_id,
        status='pending',
        scheduled_for=scheduled_for
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification


async def queue_weekly_recap(
    db: AsyncSession,
    user_id: int,
    scheduled_for: datetime
) -> Notification:
    """
    Queue a weekly recap notification for a specific user.
    
    Args:
        db: Database session
        user_id: User ID
        scheduled_for: When to send the recap
        
    Returns:
        Created notification
    """
    payload = {
        "user_id": user_id,
        "recap_type": "weekly"
    }
    
    notification = Notification(
        notification_type='weekly_recap',
        payload=payload,
        target_user_id=user_id,
        status='pending',
        scheduled_for=scheduled_for
    )
    
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    
    return notification

