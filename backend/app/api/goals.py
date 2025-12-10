"""
Goals management API routes.
"""
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.goal import GoalCreate, GoalResponse
from app.models.user import User
from app.services.goal_service import get_active_goal, create_goal, get_goal_history
from app.dependencies import get_db, get_current_user


router = APIRouter(prefix="/api/v1/goals", tags=["goals"])


@router.get("", response_model=GoalResponse)
async def get_current_goal(
    effective_date: Optional[date] = Query(None, description="Date to get goal for (defaults to today)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current active goal for a specific date.
    Returns the latest goal where effective_from <= query_date.
    """
    target_date = effective_date or date.today()
    goal = await get_active_goal(db, current_user.id, target_date)
    
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No goal found for this date"
        )
    
    return goal


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_new_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new goal (effective from specified date).
    """
    # Validate effective_from is not in the past (except today)
    effective_from = goal_data.effective_from or date.today()
    if effective_from < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="effective_from cannot be in the past"
        )
    
    # Validate max limits
    if goal_data.daily_water_bottles > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="daily_water_bottles cannot exceed 20"
        )
    if goal_data.daily_carb_max_portions > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="daily_carb_max_portions cannot exceed 20"
        )
    if goal_data.weekly_exercise_sessions > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="weekly_exercise_sessions cannot exceed 30"
        )
    
    goal = await create_goal(
        db=db,
        user_id=current_user.id,
        daily_water_bottles=goal_data.daily_water_bottles,
        daily_carb_max_portions=goal_data.daily_carb_max_portions,
        weekly_exercise_sessions=goal_data.weekly_exercise_sessions,
        effective_from=effective_from
    )
    
    return goal


@router.get("/history", response_model=List[GoalResponse])
async def get_goal_history_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all historical goals ordered by effective_from DESC.
    """
    goals = await get_goal_history(db, current_user.id)
    return goals

