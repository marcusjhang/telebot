"""
Main FastAPI application with bot webhook integration.
"""
import os
import logging
import telebot
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine
from app.api import auth, users, goals, logs, progress

# Import bot (this will initialize handlers)
try:
    from app.bot.handlers import bot
    BOT_AVAILABLE = True
except Exception as e:
    logging.error(f"Failed to import bot: {e}")
    bot = None
    BOT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Telebot Tracker API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.WEB_APP_URL,
        "http://localhost:3000",  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(goals.router)
app.include_router(logs.router)
app.include_router(progress.router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Railway.
    """
    checks = {
        "api": "healthy",
        "database": "unknown",
    }
    
    # Check database
    try:
        from app.database import AsyncSessionLocal
        from sqlalchemy import text
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = f"unhealthy: {str(e)}"
    
    status_code = 200 if all(v == "healthy" for v in checks.values()) else 503
    return checks


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "name": "Telebot Tracker API",
        "version": "1.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT
    }


@app.post("/webhook")
async def webhook_handler(request: Request):
    """
    Telegram webhook endpoint.
    Receives updates from Telegram and processes them with the bot.
    """
    if not BOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bot not available")

    try:
        # Verify webhook secret if configured
        if settings.TELEGRAM_WEBHOOK_SECRET:
            secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret_token != settings.TELEGRAM_WEBHOOK_SECRET:
                raise HTTPException(status_code=403, detail="Invalid secret token")

        # Get update from request
        update_dict = await request.json()
        update = telebot.types.Update.de_json(update_dict)

        # Process update
        bot.process_new_updates([update])

        return {"ok": True}

    except Exception as e:
        logger.error(f"Error processing webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.on_event("startup")
async def startup():
    """
    Initialize services on startup.
    """
    logger.info(f"Starting application in {settings.ENVIRONMENT} mode")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")

    # Initialize bot webhook in production
    if BOT_AVAILABLE and settings.ENVIRONMENT == "production" and settings.TELEGRAM_WEBHOOK_URL:
        try:
            webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/webhook"
            bot.remove_webhook()
            bot.set_webhook(
                url=webhook_url,
                secret_token=settings.TELEGRAM_WEBHOOK_SECRET if settings.TELEGRAM_WEBHOOK_SECRET else None
            )
            logger.info(f"Webhook set to {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}", exc_info=True)

    # Start polling in development
    elif BOT_AVAILABLE and settings.ENVIRONMENT == "development":
        logger.info("Development mode: Use polling manually or via separate process")
        # Note: Don't start polling here as it blocks the event loop
        # Run polling in a separate process: python -m app.bot.polling

    # TODO: Start scheduler for daily/weekly recaps


@app.on_event("shutdown")
async def shutdown():
    """
    Cleanup on shutdown.
    """
    await engine.dispose()
    logger.info("Application shutdown complete")


# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.ENVIRONMENT == "development"
    )

