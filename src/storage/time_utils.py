"""Time utility functions for period calculations."""
from datetime import datetime, timezone, timedelta
from typing import Tuple


def get_day_bounds(dt: datetime = None) -> Tuple[datetime, datetime]:
    """
    Get start and end of day in UTC.
    
    Args:
        dt: Reference datetime (default: now in UTC)
        
    Returns:
        Tuple of (day_start, day_end) as UTC datetimes
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    day_start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    
    return day_start, day_end


def get_week_bounds(dt: datetime = None) -> Tuple[datetime, datetime]:
    """
    Get start and end of week in UTC (Monday to Sunday per ISO 8601).
    
    Args:
        dt: Reference datetime (default: now in UTC)
        
    Returns:
        Tuple of (week_start, week_end) as UTC datetimes
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Get Monday of current week (weekday(): Monday=0, Sunday=6)
    days_since_monday = dt.weekday()
    week_start = dt.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=7)
    
    return week_start, week_end


def get_month_bounds(dt: datetime = None) -> Tuple[datetime, datetime]:
    """
    Get start and end of month in UTC.
    
    Args:
        dt: Reference datetime (default: now in UTC)
        
    Returns:
        Tuple of (month_start, month_end) as UTC datetimes
    """
    if dt is None:
        dt = datetime.now(timezone.utc)
    
    # Ensure UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    month_start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Get first day of next month
    if month_start.month == 12:
        next_month = month_start.replace(year=month_start.year + 1, month=1)
    else:
        next_month = month_start.replace(month=month_start.month + 1)
    
    month_end = next_month
    
    return month_start, month_end
