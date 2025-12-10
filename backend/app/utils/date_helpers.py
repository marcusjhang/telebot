"""
Date and time utility functions.
"""
from datetime import date, timedelta
from typing import Tuple


def get_week_bounds(target_date: date, week_start_day: int = 1) -> Tuple[date, date]:
    """
    Get week start and end dates for a given date.
    
    Args:
        target_date: The date to find the week for
        week_start_day: 0=Sunday, 1=Monday (default)
        
    Returns:
        Tuple of (week_start, week_end)
        
    Example:
        >>> get_week_bounds(date(2025, 12, 10), week_start_day=1)
        (date(2025, 12, 9), date(2025, 12, 15))  # Monday to Sunday
    """
    # Calculate days since the week start day
    # weekday() returns 0=Monday, 6=Sunday
    days_since_start = (target_date.weekday() - week_start_day) % 7
    week_start = target_date - timedelta(days=days_since_start)
    week_end = week_start + timedelta(days=6)
    
    return week_start, week_end


def get_singapore_date() -> date:
    """
    Get current date in Singapore timezone (UTC+8).
    
    Note: Since all users are hardcoded to Asia/Singapore timezone,
    this is a simple helper for consistency.
    
    Returns:
        Current date in Singapore timezone
    """
    from datetime import datetime, timezone, timedelta
    
    # Singapore is UTC+8
    singapore_tz = timezone(timedelta(hours=8))
    return datetime.now(singapore_tz).date()

