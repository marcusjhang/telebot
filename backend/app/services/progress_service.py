"""
Progress service for calculating user progress and streaks.
"""
from datetime import date, timedelta
from typing import Dict, Any, List
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.log import DailyLog, WeeklyLog
from app.models.goal import Goal
from app.services.goal_service import get_active_goal
from app.services.log_service import get_or_create_daily_log
from app.utils.date_helpers import get_week_bounds


async def calculate_streaks(user_id: int, db: AsyncSession) -> Dict[str, int]:
    """
    Calculate consecutive days meeting goals.
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        Dict with water_days, carb_days, combined_days streaks
    """
    # Get last 30 days of logs
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    query = select(DailyLog).where(
        DailyLog.user_id == user_id,
        DailyLog.log_date >= start_date,
        DailyLog.log_date <= end_date
    ).order_by(DailyLog.log_date.desc())
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    water_streak = 0
    carb_streak = 0
    combined_streak = 0
    
    for log in logs:  # Already ordered desc (today first)
        # Get goal for this date
        goal = await get_active_goal(db, user_id, log.log_date)
        
        if not goal:
            break
        
        water_met = log.water_bottles >= goal.daily_water_bottles
        carb_met = log.carb_portions <= goal.daily_carb_max_portions
        
        # Calculate days difference from today
        days_diff = (end_date - log.log_date).days
        
        # Water streak
        if water_met and water_streak == days_diff:
            water_streak += 1
        
        # Carb streak
        if carb_met and carb_streak == days_diff:
            carb_streak += 1
        
        # Combined streak (both met)
        if water_met and carb_met and combined_streak == days_diff:
            combined_streak += 1
    
    return {
        "water_days": water_streak,
        "carb_days": carb_streak,
        "combined_days": combined_streak
    }


async def get_today_progress(user_id: int, db: AsyncSession, week_start_day: int = 1) -> Dict[str, Any]:
    """
    Get today's progress summary.
    
    Args:
        user_id: User ID
        db: Database session
        week_start_day: Week start day (0=Sunday, 1=Monday)
        
    Returns:
        Dict with today's progress including water, carbs, exercise, and streaks
    """
    today = date.today()
    
    # Get today's log
    daily_log = await get_or_create_daily_log(db, user_id, today)
    
    # Get current goal
    goal = await get_active_goal(db, user_id, today)
    
    if not goal:
        # Return default values if no goal
        goal_water = Decimal('3.0')
        goal_carbs = Decimal('4.0')
        goal_exercise = 6
    else:
        goal_water = goal.daily_water_bottles
        goal_carbs = goal.daily_carb_max_portions
        goal_exercise = goal.weekly_exercise_sessions
    
    # Get weekly exercise
    week_start, _ = get_week_bounds(today, week_start_day)
    weekly_query = select(WeeklyLog).where(
        WeeklyLog.user_id == user_id,
        WeeklyLog.week_start_date == week_start
    )
    weekly_result = await db.execute(weekly_query)
    weekly_log = weekly_result.scalar_one_or_none()
    weekly_exercise = weekly_log.exercise_sessions if weekly_log else 0
    
    # Calculate streaks
    streaks = await calculate_streaks(user_id, db)
    
    # Build response
    water_current = float(daily_log.water_bottles)
    water_goal = float(goal_water)
    water_remaining = max(0.0, water_goal - water_current)
    water_percentage = (water_current / water_goal * 100) if water_goal > 0 else 0
    
    carbs_current = float(daily_log.carb_portions)
    carbs_goal = float(goal_carbs)
    carbs_remaining = max(0.0, carbs_goal - carbs_current)
    carbs_percentage = (carbs_current / carbs_goal * 100) if carbs_goal > 0 else 0
    
    exercise_remaining = max(0, goal_exercise - weekly_exercise)
    exercise_percentage = (weekly_exercise / goal_exercise * 100) if goal_exercise > 0 else 0
    
    return {
        "date": today.isoformat(),
        "water": {
            "current": water_current,
            "goal": water_goal,
            "remaining": water_remaining,
            "percentage": round(water_percentage, 1),
            "goal_met": water_current >= water_goal
        },
        "carbs": {
            "current": carbs_current,
            "goal": carbs_goal,
            "remaining": carbs_remaining,
            "percentage": round(carbs_percentage, 1),
            "over_limit": carbs_current > carbs_goal
        },
        "exercise": {
            "today": daily_log.exercise_sessions,
            "weekly_total": weekly_exercise,
            "weekly_goal": goal_exercise,
            "remaining": exercise_remaining,
            "percentage": round(exercise_percentage, 1)
        },
        "streaks": streaks
    }

