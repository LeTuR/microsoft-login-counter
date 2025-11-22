"""Data models for login events and statistics."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


@dataclass
class LoginEvent:
    """Represents a single Microsoft login event."""
    
    id: Optional[int]
    timestamp: str  # ISO 8601 UTC: "2025-11-21T14:30:00Z"
    unix_timestamp: int  # Unix epoch seconds
    detected_via: str  # "connect_sequence", "http_redirect", "oauth_callback"
    
    @classmethod
    def create(cls, detected_via: str) -> 'LoginEvent':
        """
        Create a new LoginEvent with current timestamp.
        
        Args:
            detected_via: Detection method string
            
        Returns:
            New LoginEvent instance
        """
        now = datetime.utcnow()
        return cls(
            id=None,  # Will be assigned by database
            timestamp=now.strftime('%Y-%m-%dT%H:%M:%SZ'),
            unix_timestamp=int(now.timestamp()),
            detected_via=detected_via
        )


@dataclass
class LoginStatistics:
    """Aggregated login statistics for different time periods."""
    
    today_count: int
    week_count: int
    month_count: int
    total_count: int
    period_start: datetime
    period_end: datetime
    first_event: Optional[datetime] = None
    last_event: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'today_count': self.today_count,
            'week_count': self.week_count,
            'month_count': self.month_count,
            'total_count': self.total_count,
            'period_start': self.period_start.isoformat() + 'Z',
            'period_end': self.period_end.isoformat() + 'Z',
            'first_event': self.first_event.isoformat() + 'Z' if self.first_event else None,
            'last_event': self.last_event.isoformat() + 'Z' if self.last_event else None
        }


class TimePeriod(Enum):
    """Time period filter options."""

    LAST_24H = "24h"
    LAST_7D = "7d"
    LAST_30D = "30d"
    ALL_TIME = "all"


@dataclass
class TimePeriodFilter:
    """Time period filter for graph data queries."""

    period: TimePeriod
    start_date: datetime
    end_date: datetime


@dataclass
class GraphDataPoint:
    """Aggregated data point for graph visualization."""

    bucket: str
    count: int
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'bucket': self.bucket,
            'count': self.count,
            'timestamp': self.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
