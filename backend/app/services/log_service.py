"""
Log service for managing daily/weekly logs and events.
"""
from datetime import date, datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.models.log import DailyLog, WeeklyLog
from app.models.event import Event
from app.utils.date_helpers import get_week_bounds


async def get_or_create_daily_log(db: AsyncSession, user_id: int, log_date: date) -> DailyLog:
    """
    Get or create daily log for a specific date.
    
    Args:
        db: Database session
        user_id: User ID
        log_date: Date for the log
        
    Returns:
        DailyLog
    """
    # Try to get existing log
    query = select(DailyLog).where(
        DailyLog.user_id == user_id,
        DailyLog.log_date == log_date
    )
    result = await db.execute(query)
    daily_log = result.scalar_one_or_none()
    
    if daily_log is None:
        # Create new log
        daily_log = DailyLog(
            user_id=user_id,
            log_date=log_date,
            water_bottles=Decimal('0'),
            carb_portions=Decimal('0'),
            exercise_sessions=0
        )
        db.add(daily_log)
        await db.flush()
    
    return daily_log


async def get_or_create_weekly_log(db: AsyncSession, user_id: int, week_start_date: date) -> WeeklyLog:
    """
    Get or create weekly log for a specific week.
    
    Args:
        db: Database session
        user_id: User ID
        week_start_date: Monday of the week
        
    Returns:
        WeeklyLog
    """
    # Try to get existing log
    query = select(WeeklyLog).where(
        WeeklyLog.user_id == user_id,
        WeeklyLog.week_start_date == week_start_date
    )
    result = await db.execute(query)
    weekly_log = result.scalar_one_or_none()
    
    if weekly_log is None:
        # Create new log
        weekly_log = WeeklyLog(
            user_id=user_id,
            week_start_date=week_start_date,
            exercise_sessions=0
        )
        db.add(weekly_log)
        await db.flush()
    
    return weekly_log


async def log_water(
    db: AsyncSession,
    user_id: int,
    delta: Decimal,
    message_id: Optional[int] = None,
    callback_query_id: Optional[str] = None,
    source: str = "bot",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log water intake change.
    
    Args:
        db: Database session
        user_id: User ID
        delta: Change in water bottles (can be negative)
        message_id: Telegram message ID
        callback_query_id: Telegram callback query ID for idempotency
        source: Source of the log ('bot' or 'web')
        metadata: Additional metadata
        
    Returns:
        Dict with success, new_total, goal, remaining, date
    """
    log_date = date.today()
    
    # Get or create daily log
    daily_log = await get_or_create_daily_log(db, user_id, log_date)
    
    # Calculate new total
    new_total = daily_log.water_bottles + delta
    # Clamp to 0 minimum
    new_total = max(Decimal('0'), new_total)
    
    # Update daily log
    daily_log.water_bottles = new_total
    
    # Create event record
    event = Event(
        user_id=user_id,
        event_type='water',
        delta=delta,
        occurred_at=datetime.utcnow(),
        message_id=message_id,
        callback_query_id=callback_query_id,
        source=source,
        metadata=metadata
    )
    db.add(event)
    
    await db.commit()
    await db.refresh(daily_log)
    
    # Get current goal
    from app.services.goal_service import get_active_goal
    goal = await get_active_goal(db, user_id, log_date)
    goal_value = goal.daily_water_bottles if goal else Decimal('3.0')
    
    return {
        "success": True,
        "new_total": float(new_total),
        "goal": float(goal_value),
        "remaining": float(max(Decimal('0'), goal_value - new_total)),
        "date": log_date.isoformat()
    }


async def log_carbs(
    db: AsyncSession,
    user_id: int,
    delta: Decimal,
    subtype: Optional[str] = None,
    portions: Optional[Decimal] = None,
    message_id: Optional[int] = None,
    callback_query_id: Optional[str] = None,
    source: str = "bot",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log carb intake change.

    Args:
        db: Database session
        user_id: User ID
        delta: Change in carb portions (can be negative)
        subtype: Type of carb ('meal', 'snack', 'custom')
        portions: Calculated portions
        message_id: Telegram message ID
        callback_query_id: Telegram callback query ID for idempotency
        source: Source of the log ('bot' or 'web')
        metadata: Additional metadata

    Returns:
        Dict with success, new_total, goal, remaining, over_limit, date
    """
    log_date = date.today()

    # Get or create daily log
    daily_log = await get_or_create_daily_log(db, user_id, log_date)

    # Calculate new total
    new_total = daily_log.carb_portions + delta
    # Clamp to 0 minimum
    new_total = max(Decimal('0'), new_total)

    # Update daily log
    daily_log.carb_portions = new_total

    # Create event record
    event = Event(
        user_id=user_id,
        event_type='carb',
        delta=delta,
        subtype=subtype,
        portions=portions or delta,
        occurred_at=datetime.utcnow(),
        message_id=message_id,
        callback_query_id=callback_query_id,
        source=source,
        metadata=metadata
    )
    db.add(event)

    await db.commit()
    await db.refresh(daily_log)

    # Get current goal
    from app.services.goal_service import get_active_goal
    goal = await get_active_goal(db, user_id, log_date)
    goal_value = goal.daily_carb_max_portions if goal else Decimal('4.0')

    over_limit = new_total > goal_value

    return {
        "success": True,
        "new_total": float(new_total),
        "goal": float(goal_value),
        "remaining": float(max(Decimal('0'), goal_value - new_total)),
        "over_limit": over_limit,
        "date": log_date.isoformat()
    }


async def log_exercise(
    db: AsyncSession,
    user_id: int,
    delta: int,
    week_start_day: int = 1,
    message_id: Optional[int] = None,
    callback_query_id: Optional[str] = None,
    source: str = "bot",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log exercise session change.

    Args:
        db: Database session
        user_id: User ID
        delta: Change in exercise sessions (can be negative)
        week_start_day: Week start day (0=Sunday, 1=Monday)
        message_id: Telegram message ID
        callback_query_id: Telegram callback query ID for idempotency
        source: Source of the log ('bot' or 'web')
        metadata: Additional metadata

    Returns:
        Dict with success, new_total, weekly_goal, remaining, week_start, date
    """
    log_date = date.today()

    # Get week bounds
    week_start, week_end = get_week_bounds(log_date, week_start_day)

    # Get or create daily log
    daily_log = await get_or_create_daily_log(db, user_id, log_date)

    # Get or create weekly log
    weekly_log = await get_or_create_weekly_log(db, user_id, week_start)

    # Calculate new totals
    new_daily_total = daily_log.exercise_sessions + delta
    new_daily_total = max(0, new_daily_total)

    new_weekly_total = weekly_log.exercise_sessions + delta
    new_weekly_total = max(0, new_weekly_total)

    # Update logs
    daily_log.exercise_sessions = new_daily_total
    weekly_log.exercise_sessions = new_weekly_total

    # Create event record
    event = Event(
        user_id=user_id,
        event_type='exercise',
        delta=Decimal(str(delta)),
        occurred_at=datetime.utcnow(),
        message_id=message_id,
        callback_query_id=callback_query_id,
        source=source,
        metadata=metadata
    )
    db.add(event)

    await db.commit()
    await db.refresh(weekly_log)

    # Get current goal
    from app.services.goal_service import get_active_goal
    goal = await get_active_goal(db, user_id, log_date)
    goal_value = goal.weekly_exercise_sessions if goal else 6

    return {
        "success": True,
        "new_total": new_weekly_total,
        "weekly_goal": goal_value,
        "remaining": max(0, goal_value - new_weekly_total),
        "week_start": week_start.isoformat(),
        "date": log_date.isoformat()
    }

