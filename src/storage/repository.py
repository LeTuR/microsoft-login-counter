"""Repository for login event database operations."""
from datetime import datetime
from typing import List
import logging

from src.storage.database import Database
from src.storage.models import LoginEvent, TimePeriodFilter, GraphDataPoint

logger = logging.getLogger(__name__)


class Repository:
    """Repository for managing login events in the database."""

    def __init__(self, database_path: str):
        """
        Initialize Repository with database path.

        Args:
            database_path: Path to SQLite database file
        """
        self.database_path = database_path
        self._db = None

    def _get_db(self) -> Database:
        """Get or create database connection."""
        if self._db is None:
            self._db = Database(self.database_path)
            self._db.connect()
        return self._db

    def insert_login_event(self, event: LoginEvent) -> int:
        """
        Insert a login event into the database.

        Args:
            event: LoginEvent to insert

        Returns:
            Auto-generated event ID

        """
        db = self._get_db()
        cursor = db.connection.cursor()

        cursor.execute(
            """
            INSERT INTO login_events (timestamp, unix_timestamp, detected_via)
            VALUES (?, ?, ?)
            """,
            (event.timestamp, event.unix_timestamp, event.detected_via)
        )

        db.connection.commit()
        event_id = cursor.lastrowid

        logger.info(f"Inserted login event: id={event_id}, detected_via={event.detected_via}")

        return event_id

    def get_events_by_date_range(self, start: datetime, end: datetime) -> List[LoginEvent]:
        """
        Get login events within a date range.

        Args:
            start: Start datetime (inclusive)
            end: End datetime (exclusive)

        Returns:
            List of LoginEvent objects in chronological order
        """
        db = self._get_db()
        cursor = db.connection.cursor()

        # Convert datetime to Unix timestamp
        start_ts = int(start.timestamp())
        end_ts = int(end.timestamp())

        cursor.execute(
            """
            SELECT id, timestamp, unix_timestamp, detected_via
            FROM login_events
            WHERE unix_timestamp >= ? AND unix_timestamp < ?
            ORDER BY unix_timestamp ASC
            """,
            (start_ts, end_ts)
        )

        rows = cursor.fetchall()

        events = [
            LoginEvent(
                id=row['id'],
                timestamp=row['timestamp'],
                unix_timestamp=row['unix_timestamp'],
                detected_via=row['detected_via']
            )
            for row in rows
        ]

        return events

    def get_total_count(self) -> int:
        """
        Get total count of all login events.

        Returns:
            Total number of events in database
        """
        db = self._get_db()
        cursor = db.connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM login_events")
        count = cursor.fetchone()[0]

        return count

    def close(self):
        """Close database connection."""
        if self._db is not None:
            self._db.close()
            self._db = None


def determine_aggregation_level(start_date: datetime, end_date: datetime) -> str:
    """
    Determine appropriate aggregation level based on date range.

    Aggregation rules (updated for bar chart):
    - ≤90 days: Daily buckets
    - >90 days: Weekly buckets

    Args:
        start_date: Start of time period (UTC)
        end_date: End of time period (UTC)

    Returns:
        Aggregation level: "day" or "week"
    """
    days_diff = (end_date - start_date).days

    if days_diff <= 90:
        return 'day'
    else:
        return 'week'


def get_aggregated_graph_data(database_path: str, time_filter: TimePeriodFilter) -> List[GraphDataPoint]:
    """
    Query login_events with aggregation based on time period.

    Implements two-tier density-based aggregation:
    - Daily: For recent data (≤90 days)
    - Weekly: For long ranges (>90 days)

    Args:
        database_path: Path to SQLite database
        time_filter: TimePeriodFilter with start_date, end_date, and period

    Returns:
        List of GraphDataPoint objects with aggregated counts
    """
    # 1. Determine aggregation level
    aggregation = determine_aggregation_level(time_filter.start_date, time_filter.end_date)

    if aggregation == 'day':
        sql_format = '%Y-%m-%d'
    else:  # 'week'
        sql_format = '%Y-W%W'

    # 2. Execute aggregation query
    db = Database(database_path)
    db.connect()

    query = """
        SELECT strftime(?, timestamp) as bucket,
               COUNT(*) as count,
               MIN(timestamp) as bucket_start
        FROM login_events
        WHERE timestamp >= ? AND timestamp <= ?
        GROUP BY bucket
        ORDER BY bucket
    """

    cursor = db.connection.cursor()
    cursor.execute(
        query,
        [
            sql_format,
            time_filter.start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
            time_filter.end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
        ]
    )

    rows = cursor.fetchall()
    db.close()

    # 3. Convert to GraphDataPoint objects
    data_points = [
        GraphDataPoint(
            bucket=row['bucket'],
            count=row['count'],
            timestamp=datetime.strptime(row['bucket_start'], '%Y-%m-%dT%H:%M:%SZ')
        )
        for row in rows
    ]

    logger.info(f"Retrieved {len(data_points)} aggregated data points (level={aggregation}, period={time_filter.period.value})")

    return data_points
