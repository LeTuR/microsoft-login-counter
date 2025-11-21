"""Repository for login event database operations."""
from datetime import datetime
from typing import List
import logging

from src.storage.database import Database
from src.storage.models import LoginEvent

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
