"""
Service layer for business logic.
"""
from app.services.user_service import (
    create_or_update_user,
    get_user_by_telegram_id,
    get_user_by_id,
    update_user_preferences,
    get_broadcast_recipients
)
from app.services.goal_service import (
    get_active_goal,
    create_goal,
    get_goal_history
)
from app.services.log_service import (
    get_or_create_daily_log,
    get_or_create_weekly_log,
    log_water,
    log_carbs,
    log_exercise
)
from app.services.progress_service import (
    calculate_streaks,
    get_today_progress
)
from app.services.notification_service import (
    queue_broadcast,
    queue_daily_recap,
    queue_weekly_recap
)

__all__ = [
    # User service
    "create_or_update_user",
    "get_user_by_telegram_id",
    "get_user_by_id",
    "update_user_preferences",
    "get_broadcast_recipients",
    # Goal service
    "get_active_goal",
    "create_goal",
    "get_goal_history",
    # Log service
    "get_or_create_daily_log",
    "get_or_create_weekly_log",
    "log_water",
    "log_carbs",
    "log_exercise",
    # Progress service
    "calculate_streaks",
    "get_today_progress",
    # Notification service
    "queue_broadcast",
    "queue_daily_recap",
    "queue_weekly_recap",
]
