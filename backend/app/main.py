"""
Main FastAPI application with bot webhook integration.
"""
import os
import logging
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine
from app.api import auth, users, goals, logs, progress

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


@app.on_event("startup")
async def startup():
    """
    Initialize services on startup.
    """
    logger.info(f"Starting application in {settings.ENVIRONMENT} mode")
    logger.info(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    
    # TODO: Initialize bot and set webhook in production
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

