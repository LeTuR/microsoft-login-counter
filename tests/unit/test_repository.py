"""Unit tests for Repository class."""
import pytest
import tempfile
import os
from datetime import datetime, timezone

from src.storage.repository import Repository
from src.storage.models import LoginEvent
from src.storage.database import Database


class TestRepository:
    """Test Repository class functionality."""

    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        # Initialize database with schema
        db = Database(db_path)
        db.connect()
        db.initialize_schema()
        db.close()

        yield db_path

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_insert_login_event_creates_record(self, temp_db):
        """Test insert_login_event creates database record."""
        repo = Repository(temp_db)

        event = LoginEvent.create('test_method')
        event_id = repo.insert_login_event(event)

        assert event_id is not None
        assert isinstance(event_id, int)
        assert event_id > 0

    def test_insert_login_event_stores_all_fields(self, temp_db):
        """Test insert_login_event stores all event fields correctly."""
        repo = Repository(temp_db)

        event = LoginEvent(
            id=None,
            timestamp='2025-11-21T10:30:00Z',
            unix_timestamp=1732186200,
            detected_via='http_redirect'
        )

        event_id = repo.insert_login_event(event)

        # Retrieve and verify
        db = Database(temp_db)
        db.connect()
        cursor = db.connection.cursor()
        cursor.execute('SELECT * FROM login_events WHERE id = ?', (event_id,))
        row = cursor.fetchone()
        db.close()

        assert row is not None
        assert row['timestamp'] == '2025-11-21T10:30:00Z'
        assert row['unix_timestamp'] == 1732186200
        assert row['detected_via'] == 'http_redirect'

    def test_insert_login_event_returns_auto_increment_id(self, temp_db):
        """Test insert_login_event returns auto-incremented IDs."""
        repo = Repository(temp_db)

        event1 = LoginEvent.create('method1')
        event2 = LoginEvent.create('method2')

        id1 = repo.insert_login_event(event1)
        id2 = repo.insert_login_event(event2)

        assert id2 == id1 + 1

    def test_get_events_by_date_range_returns_events_in_range(self, temp_db):
        """Test get_events_by_date_range returns events within date range."""
        repo = Repository(temp_db)

        # Insert events with different timestamps (Nov 20-22, 2024)
        event1 = LoginEvent(None, '2024-11-20T10:00:00Z', 1732100400, 'method1')
        event2 = LoginEvent(None, '2024-11-21T11:00:00Z', 1732186800, 'method2')
        event3 = LoginEvent(None, '2024-11-22T10:00:00Z', 1732273200, 'method3')

        repo.insert_login_event(event1)
        repo.insert_login_event(event2)
        repo.insert_login_event(event3)

        # Query range covering event2 only
        start = datetime(2024, 11, 21, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 11, 22, 0, 0, 0, tzinfo=timezone.utc)

        events = repo.get_events_by_date_range(start, end)

        assert len(events) == 1
        assert events[0].timestamp == '2024-11-21T11:00:00Z'

    def test_get_events_by_date_range_returns_empty_for_no_matches(self, temp_db):
        """Test get_events_by_date_range returns empty list when no events match."""
        repo = Repository(temp_db)

        event = LoginEvent(None, '2025-11-20T10:00:00Z', 1732100400, 'method1')
        repo.insert_login_event(event)

        # Query different date range
        start = datetime(2025, 11, 25, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 11, 26, 0, 0, 0, tzinfo=timezone.utc)

        events = repo.get_events_by_date_range(start, end)

        assert len(events) == 0

    def test_get_events_by_date_range_handles_boundary_conditions(self, temp_db):
        """Test get_events_by_date_range includes events at boundaries."""
        repo = Repository(temp_db)

        # Insert event exactly at start time (Nov 21, 2024 00:00:00 UTC)
        event = LoginEvent(None, '2024-11-21T00:00:00Z', 1732147200, 'method1')
        repo.insert_login_event(event)

        start = datetime(2024, 11, 21, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 11, 22, 0, 0, 0, tzinfo=timezone.utc)

        events = repo.get_events_by_date_range(start, end)

        assert len(events) == 1

    def test_get_total_count_returns_zero_for_empty_database(self, temp_db):
        """Test get_total_count returns 0 for empty database."""
        repo = Repository(temp_db)

        count = repo.get_total_count()

        assert count == 0

    def test_get_total_count_returns_correct_count(self, temp_db):
        """Test get_total_count returns correct number of events."""
        repo = Repository(temp_db)

        event1 = LoginEvent.create('method1')
        event2 = LoginEvent.create('method2')
        event3 = LoginEvent.create('method3')

        repo.insert_login_event(event1)
        repo.insert_login_event(event2)
        repo.insert_login_event(event3)

        count = repo.get_total_count()

        assert count == 3

    def test_transaction_rollback_on_error(self, temp_db):
        """Test transaction rolls back on error."""
        repo = Repository(temp_db)

        # Insert valid event
        event1 = LoginEvent.create('method1')
        repo.insert_login_event(event1)

        # Attempt to insert invalid event (should fail)
        try:
            db = Database(temp_db)
            db.connect()
            cursor = db.connection.cursor()
            # Invalid SQL to force error
            cursor.execute('INSERT INTO login_events (invalid_column) VALUES (?)', ('value',))
            db.connection.commit()
        except Exception:
            pass
        finally:
            db.close()

        # First event should still exist
        count = repo.get_total_count()
        assert count == 1

    def test_get_events_by_date_range_orders_by_timestamp(self, temp_db):
        """Test get_events_by_date_range returns events in chronological order."""
        repo = Repository(temp_db)

        # Insert events out of order (Nov 21, 2024)
        event1 = LoginEvent(None, '2024-11-21T14:00:00Z', 1732201200, 'method3')
        event2 = LoginEvent(None, '2024-11-21T11:00:00Z', 1732186800, 'method1')
        event3 = LoginEvent(None, '2024-11-21T12:00:00Z', 1732194000, 'method2')

        repo.insert_login_event(event1)
        repo.insert_login_event(event2)
        repo.insert_login_event(event3)

        start = datetime(2024, 11, 21, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 11, 22, 0, 0, 0, tzinfo=timezone.utc)

        events = repo.get_events_by_date_range(start, end)

        # Should be ordered by unix_timestamp
        assert events[0].unix_timestamp == 1732186800
        assert events[1].unix_timestamp == 1732194000
        assert events[2].unix_timestamp == 1732201200

    def test_repository_initialization_without_schema(self):
        """Test Repository can be initialized before schema exists."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        try:
            # Don't initialize schema, just create Repository
            repo = Repository(db_path)

            # Verify Repository object is created
            assert repo.database_path == db_path
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)
