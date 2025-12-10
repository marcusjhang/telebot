"""
Bot polling script for development.
Run this in a separate terminal: python -m app.bot.polling
"""
import logging
from app.bot.handlers import bot
from app.config import settings

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting bot in polling mode (development)...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        # Remove webhook if set
        bot.remove_webhook()
        
        # Start polling
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot polling error: {e}", exc_info=True)

