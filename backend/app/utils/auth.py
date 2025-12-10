"""
Authentication utilities for JWT token management.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.config import settings


def create_jwt_token(telegram_user_id: int) -> str:
    """
    Generate JWT token for user.
    
    Args:
        telegram_user_id: Telegram user ID to encode in token
        
    Returns:
        Encoded JWT token string
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(telegram_user_id),
        "exp": expire
    }
    return jwt.encode(to_encode, settings.API_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_jwt_token(token: str) -> int:
    """
    Verify JWT and return telegram_user_id.
    
    Args:
        token: JWT token string
        
    Returns:
        telegram_user_id extracted from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.API_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        telegram_user_id_str: Optional[str] = payload.get("sub")
        if telegram_user_id_str is None:
            raise credentials_exception
        telegram_user_id = int(telegram_user_id_str)
        return telegram_user_id
    except (JWTError, ValueError):
        raise credentials_exception

