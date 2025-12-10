"""
User service for user management operations.
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.models.user import User
from app.models.goal import Goal
from app.schemas.user import UserCreate, UserUpdate


async def create_or_update_user(
    db: AsyncSession,
    telegram_user_id: int,
    username: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None
) -> User:
    """
    Create or update user by telegram_user_id (upsert).
    Creates default goals if new user.
    
    Args:
        db: Database session
        telegram_user_id: Telegram user ID
        username: Telegram username
        first_name: User's first name
        last_name: User's last name
        
    Returns:
        User: Created or updated user
    """
    # Upsert user
    stmt = insert(User).values(
        telegram_user_id=telegram_user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        last_active=datetime.utcnow()
    ).on_conflict_do_update(
        index_elements=['telegram_user_id'],
        set_={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'last_active': datetime.utcnow()
        }
    ).returning(User)
    
    result = await db.execute(stmt)
    user = result.scalar_one()
    
    # Check if user has goals
    goal_query = select(Goal).where(
        Goal.user_id == user.id,
        Goal.effective_from <= date.today()
    ).order_by(Goal.effective_from.desc()).limit(1)
    
    goal_result = await db.execute(goal_query)
    existing_goal = goal_result.scalar_one_or_none()
    
    if not existing_goal:
        # Create default goals
        from app.services.goal_service import create_goal
        await create_goal(
            db=db,
            user_id=user.id,
            daily_water_bottles=3.0,
            daily_carb_max_portions=4.0,
            weekly_exercise_sessions=6,
            effective_from=date.today()
        )
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def get_user_by_telegram_id(db: AsyncSession, telegram_user_id: int) -> Optional[User]:
    """
    Get user by telegram_user_id.
    
    Args:
        db: Database session
        telegram_user_id: Telegram user ID
        
    Returns:
        User or None if not found
    """
    query = select(User).where(User.telegram_user_id == telegram_user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get user by internal user ID.
    
    Args:
        db: Database session
        user_id: Internal user ID
        
    Returns:
        User or None if not found
    """
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def update_user_preferences(
    db: AsyncSession,
    user_id: int,
    broadcast_opt_out: Optional[bool] = None,
    recap_enabled: Optional[bool] = None,
    week_start_day: Optional[int] = None
) -> User:
    """
    Update user preferences.
    
    Args:
        db: Database session
        user_id: User ID
        broadcast_opt_out: Whether to opt out of broadcasts
        recap_enabled: Whether daily recap is enabled
        week_start_day: Week start day (0=Sunday, 1=Monday)
        
    Returns:
        Updated user
    """
    update_data = {}
    if broadcast_opt_out is not None:
        update_data['broadcast_opt_out'] = broadcast_opt_out
    if recap_enabled is not None:
        update_data['recap_enabled'] = recap_enabled
    if week_start_day is not None:
        update_data['week_start_day'] = week_start_day
    
    if update_data:
        stmt = update(User).where(User.id == user_id).values(**update_data).returning(User)
        result = await db.execute(stmt)
        user = result.scalar_one()
        await db.commit()
        await db.refresh(user)
        return user
    
    return await get_user_by_id(db, user_id)


async def get_broadcast_recipients(
    db: AsyncSession,
    exclude_user_id: Optional[int] = None
) -> List[User]:
    """
    Get all users who haven't opted out of broadcasts.
    
    Args:
        db: Database session
        exclude_user_id: Optional user ID to exclude
        
    Returns:
        List of users
    """
    query = select(User).where(
        User.is_active == True,
        User.broadcast_opt_out == False
    )
    
    if exclude_user_id:
        query = query.where(User.telegram_user_id != exclude_user_id)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_all_users(db: AsyncSession) -> List[User]:
    """
    Get all users from database.

    Args:
        db: Database session

    Returns:
        List of all users
    """
    query = select(User).order_by(User.id)
    result = await db.execute(query)
    return result.scalars().all()
