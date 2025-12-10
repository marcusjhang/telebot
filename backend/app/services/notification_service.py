"""
Notification service for managing broadcast and recap notifications.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.config import settings

logger = logging.getLogger(__name__)

# Initialize Redis and RQ
try:
    from redis import Redis
    from rq import Queue

    redis_conn = Redis.from_url(settings.REDIS_URL)
    broadcast_queue = Queue('broadcasts', connection=redis_conn)
    DEBOUNCE_WINDOW = 60  # seconds
except ImportError:
    logger.warning("RQ not installed, broadcasts will be disabled")
    redis_conn = None
    broadcast_queue = None
    DEBOUNCE_WINDOW = 60


async def queue_broadcast(
    db: AsyncSession,
    user_id: int,
    event_type: str,
    delta: float,
    new_total: float,
    metadata: Optional[Dict[str, Any]] = None
) -> Optional[Notification]:
    """
    Queue a broadcast notification with RQ for background processing.

    Uses burst collapsing: if the same user logs multiple events within 1 minute,
    only the latest event is broadcast to prevent spam.

    Args:
        db: Database session
        user_id: User ID who triggered the event
        event_type: Type of event ('water', 'carb', 'exercise')
        delta: Change amount
        new_total: New total value
        metadata: Additional metadata

    Returns:
        Created notification (or None if RQ not available)
    """
    if not broadcast_queue or not redis_conn:
        logger.warning("Broadcast queue not available, skipping broadcast")
        return None

    try:
        # Create debounce key
        debounce_key = f"broadcast_debounce:{user_id}:{event_type}"

        # Check if there's a pending broadcast for this user+event
        existing_job_id = redis_conn.get(debounce_key)

        if existing_job_id:
            # Cancel the existing job (it will be replaced)
            try:
                from rq.job import Job
                existing_job = Job.fetch(existing_job_id.decode(), connection=redis_conn)
                existing_job.cancel()
                logger.info(f"Cancelled previous broadcast job {existing_job_id} (burst collapse)")
            except:
                pass  # Job may have already completed

        # Queue new broadcast with delay
        job = broadcast_queue.enqueue_in(
            timedelta=DEBOUNCE_WINDOW,  # Wait 60 seconds before sending
            func='app.workers.broadcast.send_broadcast',
            user_id=user_id,
            event_type=event_type,
            delta=float(delta),
            new_total=float(new_total),
            job_timeout='5m'
        )

        # Store job ID for debouncing
        redis_conn.setex(debounce_key, DEBOUNCE_WINDOW + 10, job.id)

        logger.info(f"Queued broadcast job {job.id} for user {user_id} (debounced {DEBOUNCE_WINDOW}s)")

        # Also create notification record for tracking
        payload = {
            "user_id": user_id,
            "event_type": event_type,
            "delta": float(delta),
            "new_total": float(new_total),
            "job_id": job.id,
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

    except Exception as e:
        logger.error(f"Failed to queue broadcast: {e}", exc_info=True)
        return None


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

