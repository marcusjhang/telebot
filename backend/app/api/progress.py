"""
Progress and analytics API routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.progress_service import get_today_progress
from app.dependencies import get_db, get_current_user


router = APIRouter(prefix="/api/v1/progress", tags=["progress"])


@router.get("/today")
async def get_today_progress_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get today's progress summary including water, carbs, exercise, and streaks.
    """
    progress = await get_today_progress(
        user_id=current_user.id,
        db=db,
        week_start_day=current_user.week_start_day
    )
    return progress

