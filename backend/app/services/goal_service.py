"""
Goal service for managing user goals.
"""
from datetime import date
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.goal import Goal


async def get_active_goal(db: AsyncSession, user_id: int, target_date: date = None) -> Optional[Goal]:
    """
    Get active goal for a specific date.
    Returns the latest goal where effective_from <= target_date.
    
    Args:
        db: Database session
        user_id: User ID
        target_date: Date to get goal for (defaults to today)
        
    Returns:
        Goal or None if not found
    """
    if target_date is None:
        target_date = date.today()
    
    query = select(Goal).where(
        Goal.user_id == user_id,
        Goal.effective_from <= target_date
    ).order_by(Goal.effective_from.desc()).limit(1)
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_goal(
    db: AsyncSession,
    user_id: int,
    daily_water_bottles: Decimal,
    daily_carb_max_portions: Decimal,
    weekly_exercise_sessions: int,
    effective_from: date = None
) -> Goal:
    """
    Create a new goal.
    
    Args:
        db: Database session
        user_id: User ID
        daily_water_bottles: Daily water goal in bottles
        daily_carb_max_portions: Daily carb limit in portions
        weekly_exercise_sessions: Weekly exercise goal
        effective_from: Date when goal becomes effective (defaults to today)
        
    Returns:
        Created goal
    """
    if effective_from is None:
        effective_from = date.today()
    
    goal = Goal(
        user_id=user_id,
        daily_water_bottles=daily_water_bottles,
        daily_carb_max_portions=daily_carb_max_portions,
        weekly_exercise_sessions=weekly_exercise_sessions,
        effective_from=effective_from
    )
    
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    
    return goal


async def get_goal_history(db: AsyncSession, user_id: int) -> List[Goal]:
    """
    Get all historical goals for a user.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        List of goals ordered by effective_from DESC
    """
    query = select(Goal).where(
        Goal.user_id == user_id
    ).order_by(Goal.effective_from.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

