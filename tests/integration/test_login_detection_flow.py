"""Integration test for end-to-end login detection flow."""
import pytest
import tempfile
import os
from unittest.mock import Mock
from datetime import datetime, timezone

from src.proxy.addon import LoginDetectorAddon
from src.storage.database import Database
from src.storage.repository import Repository


@pytest.mark.integration
class TestLoginDetectionFlow:
    """Integration test for proxy → detector → database flow."""

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

    @pytest.fixture
    def addon(self, temp_db):
        """Create LoginDetectorAddon with temporary database."""
        return LoginDetectorAddon(database_path=temp_db, callback_timeout=60)

    def test_http_connect_to_microsoft_login_tracks_session(self, addon, temp_db):
        """Test HTTP CONNECT to Microsoft login URL tracks session."""
        # Create mock flow for CONNECT to login.microsoftonline.com
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('login.microsoftonline.com', 443)

        # Call http_connect handler
        addon.http_connect(mock_flow)

        # Verify session is tracked
        session_key = '127.0.0.1:54321'
        assert addon.session_tracker.is_active(session_key) is True

    def test_http_connect_to_non_microsoft_does_not_track(self, addon, temp_db):
        """Test HTTP CONNECT to non-Microsoft host does not track session."""
        # Create mock flow for CONNECT to different host
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('example.com', 443)

        # Call http_connect handler
        addon.http_connect(mock_flow)

        # Verify session is NOT tracked
        session_key = '127.0.0.1:54321'
        assert addon.session_tracker.is_active(session_key) is False

    def test_oauth_callback_after_connect_records_login_event(self, addon, temp_db):
        """Test OAuth callback within timeout window records login event."""
        # Step 1: CONNECT to Microsoft login
        connect_flow = Mock()
        connect_flow.client_conn = Mock()
        connect_flow.client_conn.address = ('127.0.0.1', 54321)
        connect_flow.server_conn = Mock()
        connect_flow.server_conn.address = ('login.microsoftonline.com', 443)

        addon.http_connect(connect_flow)

        # Step 2: OAuth callback request from same client
        callback_flow = Mock()
        callback_flow.client_conn = Mock()
        callback_flow.client_conn.address = ('127.0.0.1', 54321)
        callback_flow.request = Mock()
        callback_flow.request.url = 'https://app.com/callback?code=AUTH_CODE'
        callback_flow.response = None

        addon.request(callback_flow)

        # Verify login event was recorded
        repo = Repository(temp_db)
        count = repo.get_total_count()
        assert count == 1

        # Verify event details
        start = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2030, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        events = repo.get_events_by_date_range(start, end)

        assert len(events) == 1
        assert events[0].detected_via == 'oauth_callback'

    def test_oauth_callback_without_prior_connect_does_not_record(self, addon, temp_db):
        """Test OAuth callback without prior CONNECT does not record event."""
        # OAuth callback request without prior CONNECT
        callback_flow = Mock()
        callback_flow.client_conn = Mock()
        callback_flow.client_conn.address = ('127.0.0.1', 54321)
        callback_flow.request = Mock()
        callback_flow.request.url = 'https://app.com/callback?code=AUTH_CODE'
        callback_flow.response = None

        addon.request(callback_flow)

        # Verify NO login event was recorded
        repo = Repository(temp_db)
        count = repo.get_total_count()
        assert count == 0

    def test_regular_request_after_connect_does_not_record(self, addon, temp_db):
        """Test regular (non-OAuth) request after CONNECT does not record event."""
        # Step 1: CONNECT to Microsoft login
        connect_flow = Mock()
        connect_flow.client_conn = Mock()
        connect_flow.client_conn.address = ('127.0.0.1', 54321)
        connect_flow.server_conn = Mock()
        connect_flow.server_conn.address = ('login.microsoftonline.com', 443)

        addon.http_connect(connect_flow)

        # Step 2: Regular (non-OAuth) request
        regular_flow = Mock()
        regular_flow.client_conn = Mock()
        regular_flow.client_conn.address = ('127.0.0.1', 54321)
        regular_flow.request = Mock()
        regular_flow.request.url = 'https://app.com/home'
        regular_flow.response = None

        addon.request(regular_flow)

        # Verify NO login event was recorded
        repo = Repository(temp_db)
        count = repo.get_total_count()
        assert count == 0

    def test_multiple_logins_from_different_clients(self, addon, temp_db):
        """Test multiple login events from different clients are recorded independently."""
        # Client 1: CONNECT and callback
        connect1 = Mock()
        connect1.client_conn = Mock()
        connect1.client_conn.address = ('127.0.0.1', 11111)
        connect1.server_conn = Mock()
        connect1.server_conn.address = ('login.microsoftonline.com', 443)
        addon.http_connect(connect1)

        callback1 = Mock()
        callback1.client_conn = Mock()
        callback1.client_conn.address = ('127.0.0.1', 11111)
        callback1.request = Mock()
        callback1.request.url = 'https://app.com/callback?code=CODE1'
        callback1.response = None
        addon.request(callback1)

        # Client 2: CONNECT and callback
        connect2 = Mock()
        connect2.client_conn = Mock()
        connect2.client_conn.address = ('127.0.0.1', 22222)
        connect2.server_conn = Mock()
        connect2.server_conn.address = ('login.microsoftonline.com', 443)
        addon.http_connect(connect2)

        callback2 = Mock()
        callback2.client_conn = Mock()
        callback2.client_conn.address = ('127.0.0.1', 22222)
        callback2.request = Mock()
        callback2.request.url = 'https://app.com/auth?state=STATE2'
        callback2.response = None
        addon.request(callback2)

        # Verify both events recorded
        repo = Repository(temp_db)
        count = repo.get_total_count()
        assert count == 2

    def test_session_cleanup_after_callback(self, addon, temp_db):
        """Test session is removed after successful callback match."""
        # CONNECT to Microsoft login
        connect_flow = Mock()
        connect_flow.client_conn = Mock()
        connect_flow.client_conn.address = ('127.0.0.1', 54321)
        connect_flow.server_conn = Mock()
        connect_flow.server_conn.address = ('login.microsoftonline.com', 443)

        addon.http_connect(connect_flow)

        session_key = '127.0.0.1:54321'
        assert addon.session_tracker.is_active(session_key) is True

        # OAuth callback
        callback_flow = Mock()
        callback_flow.client_conn = Mock()
        callback_flow.client_conn.address = ('127.0.0.1', 54321)
        callback_flow.request = Mock()
        callback_flow.request.url = 'https://app.com/callback?code=CODE'
        callback_flow.response = None

        addon.request(callback_flow)

        # Session should be removed after match
        assert addon.session_tracker.is_active(session_key) is False

    def test_addon_initialization_creates_database_connection(self, temp_db):
        """Test LoginDetectorAddon initializes database connection."""
        addon = LoginDetectorAddon(database_path=temp_db, callback_timeout=30)

        assert addon.repository is not None
        assert addon.session_tracker is not None
        assert addon.session_tracker.timeout == 30

    def test_end_to_end_flow_with_redirect_detection(self, addon, temp_db):
        """Test end-to-end flow with 302 redirect containing OAuth callback."""
        # CONNECT to Microsoft login
        connect_flow = Mock()
        connect_flow.client_conn = Mock()
        connect_flow.client_conn.address = ('127.0.0.1', 54321)
        connect_flow.server_conn = Mock()
        connect_flow.server_conn.address = ('login.microsoftonline.com', 443)

        addon.http_connect(connect_flow)

        # Request with 302 redirect to callback URL
        redirect_flow = Mock()
        redirect_flow.client_conn = Mock()
        redirect_flow.client_conn.address = ('127.0.0.1', 54321)
        redirect_flow.request = Mock()
        redirect_flow.request.url = 'https://login.microsoftonline.com/authorize'
        redirect_flow.response = Mock()
        redirect_flow.response.status_code = 302
        redirect_flow.response.headers = {'Location': 'https://app.com/callback?code=ABC'}

        addon.request(redirect_flow)

        # Verify login event recorded
        repo = Repository(temp_db)
        count = repo.get_total_count()
        assert count == 1
