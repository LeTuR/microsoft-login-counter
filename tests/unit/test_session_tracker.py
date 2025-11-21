"""Unit tests for SessionTracker class."""
import pytest
import time
from datetime import datetime, timedelta

from src.proxy.session_tracker import SessionTracker


class TestSessionTracker:
    """Test SessionTracker class functionality."""

    def test_initialization(self):
        """Test SessionTracker initializes with correct timeout."""
        tracker = SessionTracker(timeout=60)
        assert tracker.timeout == 60

    def test_track_session_adds_new_session(self):
        """Test track_session adds a new session."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-123')

        assert 'session-123' in tracker.sessions

    def test_track_session_updates_timestamp(self):
        """Test track_session updates timestamp for existing session."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-123')
        first_timestamp = tracker.sessions['session-123']

        time.sleep(0.1)
        tracker.track_session('session-123')
        second_timestamp = tracker.sessions['session-123']

        assert second_timestamp > first_timestamp

    def test_is_active_returns_true_for_recent_session(self):
        """Test is_active returns True for recently tracked session."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-123')

        assert tracker.is_active('session-123') is True

    def test_is_active_returns_false_for_unknown_session(self):
        """Test is_active returns False for unknown session."""
        tracker = SessionTracker(timeout=60)

        assert tracker.is_active('unknown-session') is False

    def test_is_active_returns_false_for_expired_session(self):
        """Test is_active returns False for expired session."""
        tracker = SessionTracker(timeout=1)  # 1 second timeout
        tracker.track_session('session-123')

        time.sleep(1.5)  # Wait for expiration

        assert tracker.is_active('session-123') is False

    def test_remove_session_deletes_session(self):
        """Test remove_session deletes a tracked session."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-123')

        tracker.remove_session('session-123')

        assert 'session-123' not in tracker.sessions

    def test_remove_session_handles_unknown_session(self):
        """Test remove_session handles unknown session without error."""
        tracker = SessionTracker(timeout=60)

        # Should not raise exception
        tracker.remove_session('unknown-session')

    def test_cleanup_expired_removes_old_sessions(self):
        """Test cleanup_expired removes sessions older than timeout."""
        tracker = SessionTracker(timeout=1)
        tracker.track_session('old-session')

        time.sleep(1.5)
        tracker.track_session('new-session')

        tracker.cleanup_expired()

        assert 'old-session' not in tracker.sessions
        assert 'new-session' in tracker.sessions

    def test_cleanup_expired_keeps_active_sessions(self):
        """Test cleanup_expired keeps sessions within timeout window."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-1')
        tracker.track_session('session-2')
        tracker.track_session('session-3')

        tracker.cleanup_expired()

        assert len(tracker.sessions) == 3

    def test_get_active_count_returns_correct_count(self):
        """Test get_active_count returns number of active sessions."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-1')
        tracker.track_session('session-2')
        tracker.track_session('session-3')

        assert tracker.get_active_count() == 3

    def test_get_active_count_excludes_expired_sessions(self):
        """Test get_active_count excludes expired sessions."""
        tracker = SessionTracker(timeout=1)
        tracker.track_session('old-session')

        time.sleep(1.5)
        tracker.track_session('new-session')

        # Call cleanup to remove expired
        tracker.cleanup_expired()

        assert tracker.get_active_count() == 1

    def test_multiple_sessions_independent(self):
        """Test multiple sessions tracked independently."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-A')
        tracker.track_session('session-B')
        tracker.track_session('session-C')

        assert tracker.is_active('session-A') is True
        assert tracker.is_active('session-B') is True
        assert tracker.is_active('session-C') is True

    def test_default_timeout_is_60_seconds(self):
        """Test SessionTracker defaults to 60 second timeout."""
        tracker = SessionTracker()

        assert tracker.timeout == 60

    def test_sessions_stored_as_unix_timestamps(self):
        """Test session timestamps are stored as Unix timestamps."""
        tracker = SessionTracker(timeout=60)
        tracker.track_session('session-123')

        timestamp = tracker.sessions['session-123']

        # Should be a float representing Unix epoch time
        assert isinstance(timestamp, (int, float))
        assert timestamp > 1700000000  # Sanity check (after 2023)
