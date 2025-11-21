"""Unit tests for Database connection and schema initialization."""
import sqlite3
import tempfile
import os
from pathlib import Path
import pytest

from src.storage.database import Database


class TestDatabase:
    """Test Database class functionality."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        yield db_path

        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    def test_database_initialization(self, temp_db_path):
        """Test database file is created on initialization."""
        db = Database(temp_db_path)
        assert db.database_path == temp_db_path
        assert db.connection is None

    def test_database_directory_creation(self):
        """Test database directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, 'subdir', 'test.db')
            db = Database(db_path)

            # Directory should be created
            assert os.path.exists(os.path.dirname(db_path))

    def test_connect_establishes_connection(self, temp_db_path):
        """Test connect() establishes database connection."""
        db = Database(temp_db_path)
        conn = db.connect()

        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        assert db.connection is conn

        db.close()

    def test_connect_returns_existing_connection(self, temp_db_path):
        """Test connect() returns existing connection if already connected."""
        db = Database(temp_db_path)
        conn1 = db.connect()
        conn2 = db.connect()

        assert conn1 is conn2

        db.close()

    def test_connection_row_factory_configured(self, temp_db_path):
        """Test connection uses Row factory for dict-like access."""
        db = Database(temp_db_path)
        conn = db.connect()

        assert conn.row_factory is sqlite3.Row

        db.close()

    def test_initialize_schema_creates_tables(self, temp_db_path):
        """Test initialize_schema() creates required tables."""
        db = Database(temp_db_path)
        db.connect()
        db.initialize_schema()

        cursor = db.connection.cursor()

        # Check login_events table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='login_events'
        """)
        assert cursor.fetchone() is not None

        # Check proxy_metadata table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='proxy_metadata'
        """)
        assert cursor.fetchone() is not None

        db.close()

    def test_initialize_schema_creates_index(self, temp_db_path):
        """Test initialize_schema() creates required indexes."""
        db = Database(temp_db_path)
        db.connect()
        db.initialize_schema()

        cursor = db.connection.cursor()

        # Check index on login_events.unix_timestamp exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='index' AND name='idx_login_events_unix_time'
        """)
        assert cursor.fetchone() is not None

        db.close()

    def test_initialize_schema_inserts_metadata(self, temp_db_path):
        """Test initialize_schema() inserts schema_version metadata."""
        db = Database(temp_db_path)
        db.connect()
        db.initialize_schema()

        cursor = db.connection.cursor()

        # Check schema_version exists in proxy_metadata
        cursor.execute("""
            SELECT value FROM proxy_metadata WHERE key='schema_version'
        """)
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == '1.0.0'

        db.close()

    def test_initialize_schema_idempotent(self, temp_db_path):
        """Test initialize_schema() can be called multiple times safely."""
        db = Database(temp_db_path)
        db.connect()

        # Initialize twice
        db.initialize_schema()
        db.initialize_schema()

        cursor = db.connection.cursor()

        # Tables should still exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='login_events'
        """)
        assert cursor.fetchone() is not None

        db.close()

    def test_close_closes_connection(self, temp_db_path):
        """Test close() closes database connection."""
        db = Database(temp_db_path)
        db.connect()

        assert db.connection is not None

        db.close()

        assert db.connection is None

    def test_context_manager_connect(self, temp_db_path):
        """Test context manager establishes connection."""
        with Database(temp_db_path) as db:
            assert db.connection is not None

    def test_context_manager_commits_on_success(self, temp_db_path):
        """Test context manager commits transaction on success."""
        with Database(temp_db_path) as db:
            db.initialize_schema()
            cursor = db.connection.cursor()
            cursor.execute("""
                INSERT INTO login_events (timestamp, unix_timestamp, detected_via)
                VALUES ('2025-11-21T10:00:00Z', 1732186800, 'test')
            """)

        # Verify data was committed
        db2 = Database(temp_db_path)
        db2.connect()
        cursor = db2.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM login_events")
        count = cursor.fetchone()[0]
        assert count == 1
        db2.close()

    def test_context_manager_rollbacks_on_exception(self, temp_db_path):
        """Test context manager rolls back transaction on exception."""
        db = Database(temp_db_path)
        db.connect()
        db.initialize_schema()
        db.close()

        try:
            with Database(temp_db_path) as db:
                cursor = db.connection.cursor()
                cursor.execute("""
                    INSERT INTO login_events (timestamp, unix_timestamp, detected_via)
                    VALUES ('2025-11-21T10:00:00Z', 1732186800, 'test')
                """)
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Verify data was NOT committed (rolled back)
        db2 = Database(temp_db_path)
        db2.connect()
        cursor = db2.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM login_events")
        count = cursor.fetchone()[0]
        assert count == 0
        db2.close()

    def test_context_manager_closes_connection(self, temp_db_path):
        """Test context manager closes connection on exit."""
        db = Database(temp_db_path)

        with db:
            assert db.connection is not None

        assert db.connection is None

    def test_tilde_expansion_in_path(self):
        """Test ~ is expanded to home directory in database path."""
        db = Database("~/test.db")
        expanded_path = os.path.expanduser("~/test.db")

        assert db.database_path == expanded_path
