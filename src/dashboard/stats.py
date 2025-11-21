"""Statistics computation for login events."""
from datetime import datetime, timezone
from typing import Optional

from src.storage.repository import Repository
from src.storage.models import LoginStatistics
from src.storage.time_utils import get_day_bounds, get_week_bounds, get_month_bounds


def compute_statistics(repository: Repository, reference_time: Optional[datetime] = None) -> LoginStatistics:
    """
    Compute login statistics for different time periods.

    Args:
        repository: Repository instance for database access
        reference_time: Reference time for period calculation (default: now UTC)

    Returns:
        LoginStatistics with counts for today/week/month/total
    """
    if reference_time is None:
        reference_time = datetime.now(timezone.utc)

    # Get time period boundaries
    day_start, day_end = get_day_bounds(reference_time)
    week_start, week_end = get_week_bounds(reference_time)
    month_start, month_end = get_month_bounds(reference_time)

    # Query events for each period
    today_events = repository.get_events_by_date_range(day_start, day_end)
    week_events = repository.get_events_by_date_range(week_start, week_end)
    month_events = repository.get_events_by_date_range(month_start, month_end)

    # Get total count
    total_count = repository.get_total_count()

    # Get first and last event timestamps
    all_events = repository.get_events_by_date_range(
        datetime(2000, 1, 1, tzinfo=timezone.utc),
        datetime(2100, 1, 1, tzinfo=timezone.utc)
    )

    first_event = None
    last_event = None

    if all_events:
        first_event = datetime.fromisoformat(all_events[0].timestamp.replace('Z', '+00:00'))
        last_event = datetime.fromisoformat(all_events[-1].timestamp.replace('Z', '+00:00'))

    return LoginStatistics(
        today_count=len(today_events),
        week_count=len(week_events),
        month_count=len(month_events),
        total_count=total_count,
        period_start=day_start,
        period_end=day_end,
        first_event=first_event,
        last_event=last_event
    )
