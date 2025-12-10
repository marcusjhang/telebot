"""
Activity logging API routes.
"""
from typing import Optional, Dict, Any
from decimal import Decimal
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.services.log_service import log_water, log_carbs, log_exercise
from app.dependencies import get_db, get_current_user


router = APIRouter(prefix="/api/v1/logs", tags=["logs"])


@router.post("/water")
async def log_water_intake(
    delta: float,
    message_id: Optional[int] = None,
    source: str = "bot",
    metadata: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add/decrease water intake.
    
    Args:
        delta: Change in water bottles (can be negative)
        message_id: Telegram message ID
        source: Source of the log ('bot' or 'web')
        metadata: Additional metadata
        idempotency_key: Optional idempotency key for deduplication
    """
    # TODO: Implement idempotency check with Redis
    # For now, use callback_query_id as idempotency key
    
    result = await log_water(
        db=db,
        user_id=current_user.id,
        delta=Decimal(str(delta)),
        message_id=message_id,
        callback_query_id=idempotency_key,
        source=source,
        metadata=metadata
    )
    
    # TODO: Queue broadcast notification
    
    return result


@router.post("/carbs")
async def log_carb_intake(
    delta: float,
    subtype: Optional[str] = None,
    portions: Optional[float] = None,
    message_id: Optional[int] = None,
    source: str = "bot",
    metadata: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add/decrease carb intake.
    
    Args:
        delta: Change in carb portions (can be negative)
        subtype: Type of carb ('meal', 'snack', 'custom')
        portions: Calculated portions
        message_id: Telegram message ID
        source: Source of the log ('bot' or 'web')
        metadata: Additional metadata
        idempotency_key: Optional idempotency key for deduplication
    """
    result = await log_carbs(
        db=db,
        user_id=current_user.id,
        delta=Decimal(str(delta)),
        subtype=subtype,
        portions=Decimal(str(portions)) if portions else None,
        message_id=message_id,
        callback_query_id=idempotency_key,
        source=source,
        metadata=metadata
    )
    
    # TODO: Queue broadcast notification
    
    return result


@router.post("/exercise")
async def log_exercise_session(
    delta: int,
    message_id: Optional[int] = None,
    source: str = "bot",
    metadata: Optional[Dict[str, Any]] = None,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add/decrease exercise sessions.
    
    Args:
        delta: Change in exercise sessions (can be negative)
        message_id: Telegram message ID
        source: Source of the log ('bot' or 'web')
        metadata: Additional metadata
        idempotency_key: Optional idempotency key for deduplication
    """
    result = await log_exercise(
        db=db,
        user_id=current_user.id,
        delta=delta,
        week_start_day=current_user.week_start_day,
        message_id=message_id,
        callback_query_id=idempotency_key,
        source=source,
        metadata=metadata
    )
    
    # TODO: Queue broadcast notification
    
    return result

