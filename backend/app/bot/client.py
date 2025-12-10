"""
Bot API client for calling backend services.
This module provides a simple interface for bot handlers to interact with the backend.
"""
import logging
import asyncio
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import date

from app.database import AsyncSessionLocal
from app.services import (
    user_service,
    goal_service,
    log_service,
    progress_service,
    notification_service
)

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async functions in sync context"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(coro)


class BotAPIClient:
    """Client for bot to call backend services"""

    def create_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update user (sync wrapper)"""
        return run_async(self._create_user(telegram_user_id, username, first_name, last_name))

    async def _create_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update user"""
        async with AsyncSessionLocal() as db:
            user = await user_service.create_or_update_user(
                db=db,
                telegram_user_id=telegram_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            return {
                "id": user.id,
                "telegram_user_id": user.telegram_user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name
            }
    
    def log_water(
        self,
        telegram_user_id: int,
        delta: float,
        message_id: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log water intake (sync wrapper)"""
        return run_async(self._log_water(telegram_user_id, delta, message_id, idempotency_key))

    async def _log_water(
        self,
        telegram_user_id: int,
        delta: float,
        message_id: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log water intake"""
        async with AsyncSessionLocal() as db:
            # Get user
            user = await user_service.get_user_by_telegram_id(db, telegram_user_id)
            if not user:
                raise ValueError("User not found")
            
            # Log water
            result = await log_service.log_water(
                db=db,
                user_id=user.id,
                delta=Decimal(str(delta)),
                message_id=message_id,
                callback_query_id=idempotency_key,
                source="bot"
            )
            
            return {
                "new_total": float(result["current"]),
                "goal": float(result["goal"]),
                "remaining": float(result["remaining"]),
                "goal_met": result["goal_met"]
            }
    
    def log_carbs(
        self,
        telegram_user_id: int,
        delta: float,
        subtype: Optional[str] = None,
        message_id: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log carb intake (sync wrapper)"""
        return run_async(self._log_carbs(telegram_user_id, delta, subtype, message_id, idempotency_key))

    async def _log_carbs(
        self,
        telegram_user_id: int,
        delta: float,
        subtype: Optional[str] = None,
        message_id: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log carb intake"""
        async with AsyncSessionLocal() as db:
            # Get user
            user = await user_service.get_user_by_telegram_id(db, telegram_user_id)
            if not user:
                raise ValueError("User not found")
            
            # Log carbs
            result = await log_service.log_carbs(
                db=db,
                user_id=user.id,
                delta=Decimal(str(delta)),
                subtype=subtype,
                portions=None,  # Will be calculated from delta
                message_id=message_id,
                callback_query_id=idempotency_key,
                source="bot"
            )
            
            return {
                "new_total": float(result["current"]),
                "goal": float(result["goal"]),
                "remaining": float(result["remaining"]),
                "over_limit": result["over_limit"]
            }
    
    def log_exercise(
        self,
        telegram_user_id: int,
        delta: int,
        message_id: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log exercise session (sync wrapper)"""
        return run_async(self._log_exercise(telegram_user_id, delta, message_id, idempotency_key))

    async def _log_exercise(
        self,
        telegram_user_id: int,
        delta: int,
        message_id: Optional[int] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log exercise session"""
        async with AsyncSessionLocal() as db:
            # Get user
            user = await user_service.get_user_by_telegram_id(db, telegram_user_id)
            if not user:
                raise ValueError("User not found")
            
            # Log exercise
            result = await log_service.log_exercise(
                db=db,
                user_id=user.id,
                delta=delta,
                week_start_day=user.week_start_day,
                message_id=message_id,
                callback_query_id=idempotency_key,
                source="bot"
            )
            
            return {
                "new_total": result["weekly_total"],
                "weekly_goal": result["weekly_goal"],
                "remaining": result["remaining"],
                "week_start": str(result["week_start"]),
                "week_end": str(result["week_end"])
            }
    
    def get_today_progress(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get today's progress (sync wrapper)"""
        return run_async(self._get_today_progress(telegram_user_id))

    async def _get_today_progress(self, telegram_user_id: int) -> Dict[str, Any]:
        """Get today's progress"""
        async with AsyncSessionLocal() as db:
            # Get user
            user = await user_service.get_user_by_telegram_id(db, telegram_user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get progress
            progress = await progress_service.get_today_progress(
                user_id=user.id,
                db=db,
                week_start_day=user.week_start_day
            )
            
            return progress


# Global client instance
api_client = BotAPIClient()

