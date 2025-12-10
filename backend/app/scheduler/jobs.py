"""
APScheduler jobs for daily/weekly resets and recap notifications.
"""
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

from app.config import settings
from app.database import AsyncSessionLocal
from app.services import user_service, progress_service, goal_service, log_service

logger = logging.getLogger(__name__)

# Singapore timezone
sg_tz = pytz.timezone("Asia/Singapore")

# Initialize scheduler
scheduler = AsyncIOScheduler(timezone=sg_tz)


async def get_all_active_users():
    """Get all active users from database"""
    async with AsyncSessionLocal() as db:
        users = await user_service.get_all_users(db)
        return [
            {
                "id": user.id,
                "telegram_user_id": user.telegram_user_id,
                "first_name": user.first_name,
                "recap_enabled": user.recap_enabled,
                "timezone": user.timezone
            }
            for user in users
        ]


async def send_daily_recap(user_id: int, telegram_user_id: int, first_name: str):
    """
    Send end-of-day summary to user.
    
    Args:
        user_id: Database user ID
        telegram_user_id: Telegram user ID
        first_name: User's first name
    """
    try:
        # Import bot here to avoid circular imports
        from app.bot.handlers import bot
        
        # Get yesterday's progress
        yesterday = (datetime.now(sg_tz) - timedelta(days=1)).date()
        
        async with AsyncSessionLocal() as db:
            progress = await progress_service.get_day_progress(db, user_id, yesterday)
        
        water_emoji = "✅" if progress["water"]["goal_met"] else "❌"
        carb_emoji = "✅" if not progress["carbs"]["over_limit"] else "❌"
        
        message = f"""
🌙 Daily Recap - {yesterday.strftime('%b %d, %Y')}

{water_emoji} Water: {progress["water"]["current"]}/{progress["water"]["goal"]} bottles
{carb_emoji} Carbs: {progress["carbs"]["current"]}/{progress["carbs"]["goal"]} portions
🏃 Exercise: {progress["exercise"]["today"]} sessions

Keep it up, {first_name}! 💪
        """.strip()
        
        bot.send_message(telegram_user_id, message)
        logger.info(f"Sent daily recap to user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send daily recap to user {user_id}: {e}", exc_info=True)


async def send_weekly_recap(user_id: int, telegram_user_id: int, first_name: str):
    """
    Send end-of-week exercise summary.
    
    Args:
        user_id: Database user ID
        telegram_user_id: Telegram user ID
        first_name: User's first name
    """
    try:
        # Import bot here to avoid circular imports
        from app.bot.handlers import bot
        
        # Get last week's data (Monday to Sunday)
        today = datetime.now(sg_tz).date()
        last_week_start = today - timedelta(days=today.weekday() + 7)  # Last Monday
        
        async with AsyncSessionLocal() as db:
            # Get weekly log
            weekly_log = await log_service.get_weekly_log(db, user_id, last_week_start)
            
            # Get goal for that week
            goal = await goal_service.get_active_goal(db, user_id, last_week_start)
        
        exercise_sessions = weekly_log.exercise_sessions if weekly_log else 0
        goal_sessions = goal.weekly_exercise_sessions
        
        emoji = "✅" if exercise_sessions >= goal_sessions else "❌"
        
        message = f"""
📅 Weekly Recap - Week of {last_week_start.strftime('%b %d, %Y')}

{emoji} Exercise: {exercise_sessions}/{goal_sessions} sessions

{"🎉 Goal achieved!" if emoji == "✅" else "Keep pushing next week! 💪"}
        """.strip()
        
        bot.send_message(telegram_user_id, message)
        logger.info(f"Sent weekly recap to user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to send weekly recap to user {user_id}: {e}", exc_info=True)


async def daily_reset_job():
    """
    Daily reset job - runs at 00:05 Singapore time.
    Sends daily recap notifications to users who have it enabled.
    """
    logger.info("Running daily reset job...")
    
    try:
        users = await get_all_active_users()
        
        sent_count = 0
        for user in users:
            try:
                # Send daily recap if enabled
                if user["recap_enabled"]:
                    await send_daily_recap(
                        user["id"],
                        user["telegram_user_id"],
                        user["first_name"]
                    )
                    sent_count += 1
                    
            except Exception as e:
                logger.error(f"Failed daily reset for user {user['id']}: {e}")
        
        logger.info(f"Daily reset job completed. Sent {sent_count} recaps.")

    except Exception as e:
        logger.error(f"Daily reset job failed: {e}", exc_info=True)


async def weekly_reset_job():
    """
    Weekly reset job - runs at Monday 00:10 Singapore time.
    Sends weekly recap notifications to all users.
    """
    logger.info("Running weekly reset job...")

    try:
        users = await get_all_active_users()

        sent_count = 0
        for user in users:
            try:
                await send_weekly_recap(
                    user["id"],
                    user["telegram_user_id"],
                    user["first_name"]
                )
                sent_count += 1

            except Exception as e:
                logger.error(f"Failed weekly reset for user {user['id']}: {e}")

        logger.info(f"Weekly reset job completed. Sent {sent_count} recaps.")

    except Exception as e:
        logger.error(f"Weekly reset job failed: {e}", exc_info=True)


async def refresh_monthly_stats():
    """
    Refresh materialized view for monthly stats.
    Runs daily at 01:00 Singapore time.
    """
    logger.info("Refreshing monthly stats...")

    try:
        async with AsyncSessionLocal() as db:
            # Refresh materialized view concurrently (non-blocking)
            await db.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_stats")
            await db.commit()

        logger.info("Monthly stats refreshed successfully")

    except Exception as e:
        logger.error(f"Failed to refresh monthly stats: {e}", exc_info=True)


def setup_jobs():
    """
    Setup all scheduled jobs.
    Call this during application startup.
    """
    logger.info("Setting up scheduled jobs...")

    # Daily reset at 00:05 Singapore time
    scheduler.add_job(
        daily_reset_job,
        CronTrigger(hour=0, minute=5, timezone=sg_tz),
        id="daily_reset",
        replace_existing=True,
        name="Daily Reset & Recap"
    )
    logger.info("✓ Scheduled: Daily reset at 00:05 SGT")

    # Weekly reset at Monday 00:10 Singapore time
    scheduler.add_job(
        weekly_reset_job,
        CronTrigger(day_of_week='mon', hour=0, minute=10, timezone=sg_tz),
        id="weekly_reset",
        replace_existing=True,
        name="Weekly Reset & Recap"
    )
    logger.info("✓ Scheduled: Weekly reset at Monday 00:10 SGT")

    # Monthly stats refresh at 01:00 Singapore time
    scheduler.add_job(
        refresh_monthly_stats,
        CronTrigger(hour=1, minute=0, timezone=sg_tz),
        id="refresh_monthly_stats",
        replace_existing=True,
        name="Refresh Monthly Stats"
    )
    logger.info("✓ Scheduled: Monthly stats refresh at 01:00 SGT")

    logger.info("All scheduled jobs configured")


def start_scheduler():
    """
    Start the scheduler.
    Call this during application startup.
    """
    if not scheduler.running:
        setup_jobs()
        scheduler.start()
        logger.info("🚀 Scheduler started successfully")
    else:
        logger.warning("Scheduler is already running")


def shutdown_scheduler():
    """
    Shutdown the scheduler gracefully.
    Call this during application shutdown.
    """
    if scheduler.running:
        scheduler.shutdown(wait=True)
        logger.info("Scheduler shut down successfully")
    else:
        logger.warning("Scheduler is not running")

