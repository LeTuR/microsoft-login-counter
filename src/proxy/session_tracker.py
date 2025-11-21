"""Session tracking for correlating CONNECT requests with OAuth callbacks."""
import time
from typing import Dict


class SessionTracker:
    """Track active sessions with timestamp-based expiration."""

    def __init__(self, timeout: int = 60):
        """
        Initialize SessionTracker.

        Args:
            timeout: Session timeout in seconds (default: 60)
        """
        self.timeout = timeout
        self.sessions: Dict[str, float] = {}

    def track_session(self, session_key: str):
        """
        Track a new session or update existing session timestamp.

        Args:
            session_key: Unique identifier for the session (e.g., "IP:PORT")
        """
        self.sessions[session_key] = time.time()

    def is_active(self, session_key: str) -> bool:
        """
        Check if a session is active (exists and not expired).

        Args:
            session_key: Session identifier to check

        Returns:
            True if session is active and not expired, False otherwise
        """
        if session_key not in self.sessions:
            return False

        timestamp = self.sessions[session_key]
        current_time = time.time()

        # Check if session expired
        if current_time - timestamp > self.timeout:
            return False

        return True

    def remove_session(self, session_key: str):
        """
        Remove a tracked session.

        Args:
            session_key: Session identifier to remove
        """
        if session_key in self.sessions:
            del self.sessions[session_key]

    def cleanup_expired(self):
        """Remove all expired sessions from tracking."""
        current_time = time.time()
        expired_keys = [
            key for key, timestamp in self.sessions.items()
            if current_time - timestamp > self.timeout
        ]

        for key in expired_keys:
            del self.sessions[key]

    def get_active_count(self) -> int:
        """
        Get count of active (non-expired) sessions.

        Returns:
            Number of active sessions
        """
        self.cleanup_expired()
        return len(self.sessions)
