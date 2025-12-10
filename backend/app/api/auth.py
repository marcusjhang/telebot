"""
Authentication API routes.
"""
import hmac
import hashlib
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import TelegramAuthData, TokenResponse
from app.services.user_service import create_or_update_user
from app.utils.auth import create_jwt_token
from app.dependencies import get_db
from app.config import settings


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/telegram", response_model=TokenResponse)
async def telegram_auth(data: TelegramAuthData, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user via Telegram Login Widget.
    
    Verifies the Telegram hash and creates/updates user in database.
    Returns JWT token for API access.
    """
    # 1. Verify hash
    check_data = {k: v for k, v in data.dict().items() if k != "hash" and v is not None}
    check_string = "\n".join([f"{k}={v}" for k, v in sorted(check_data.items())])
    secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
    calculated_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
    
    if calculated_hash != data.hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication data"
        )
    
    # 2. Check auth_date (within 24 hours)
    if datetime.now().timestamp() - data.auth_date > 86400:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication data expired"
        )
    
    # 3. Create or update user
    user = await create_or_update_user(
        db=db,
        telegram_user_id=data.id,
        username=data.username,
        first_name=data.first_name,
        last_name=data.last_name
    )
    
    # 4. Generate JWT
    token = create_jwt_token(user.telegram_user_id)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user={
            "id": user.id,
            "telegram_user_id": user.telegram_user_id,
            "username": user.username,
            "first_name": user.first_name
        }
    )

