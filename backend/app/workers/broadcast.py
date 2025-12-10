"""
RQ worker for sending broadcast notifications.
"""
import logging
import asyncio
from telebot import TeleBot

from app.config import settings
from app.database import AsyncSessionLocal
from app.services.user_service import get_user_by_id, get_broadcast_recipients

logger = logging.getLogger(__name__)

# Initialize bot for worker
bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)


def send_broadcast(user_id: int, event_type: str, delta: float, new_total: float):
    """
    Worker function to send broadcasts (runs in RQ worker process).
    This is a synchronous function called by RQ.
    
    Args:
        user_id: Internal user ID (not telegram_user_id)
        event_type: Type of event ('water', 'carbs', 'exercise')
        delta: Change amount
        new_total: New total after change
    """
    
    async def _send():
        async with AsyncSessionLocal() as db:
            # Get sender info
            sender = await get_user_by_id(user_id, db)
            if not sender:
                logger.error(f"User {user_id} not found")
                return
            
            # Get all active users (broadcast_opt_out = false)
            recipients = await get_broadcast_recipients(
                exclude_user_id=sender.telegram_user_id,
                db=db
            )
            
            # Build message
            emoji_map = {"water": "💧", "carbs": "🍽️", "exercise": "🏃"}
            emoji = emoji_map.get(event_type, "📊")
            
            action = "added" if delta > 0 else "removed"
            message = f"{emoji} {sender.first_name} just {action} {abs(delta)} {event_type}! (Total: {new_total})"
            
            # Send to all recipients
            success_count = 0
            for recipient in recipients:
                try:
                    bot.send_message(recipient["telegram_user_id"], message)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to send broadcast to {recipient['telegram_user_id']}: {e}")
            
            logger.info(f"Broadcast sent to {success_count}/{len(recipients)} users")
    
    # Run async function in sync context
    asyncio.run(_send())

