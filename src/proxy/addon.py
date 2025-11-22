"""Mitmproxy addon for detecting Microsoft login events."""
import logging
from typing import Any

from mitmproxy import http

from src.proxy.detector import is_microsoft_login_connect, is_oauth_callback, is_interactive_login
from src.proxy.session_tracker import SessionTracker
from src.storage.repository import Repository
from src.storage.models import LoginEvent

logger = logging.getLogger(__name__)


class LoginDetectorAddon:
    """Mitmproxy addon that detects and records Microsoft login events."""

    def __init__(self, database_path: str, callback_timeout: int = 60):
        """
        Initialize LoginDetectorAddon.

        Args:
            database_path: Path to SQLite database for storing events
            callback_timeout: Session timeout in seconds for callback correlation
        """
        self.repository = Repository(database_path)
        self.session_tracker = SessionTracker(timeout=callback_timeout)
        self.recorded_sessions = {}  # Track recently recorded sessions to avoid duplicates
        self.dedup_window = 10  # Don't record same session twice within 10 seconds
        logger.info(f"LoginDetectorAddon initialized with database: {database_path}")

    def http_connect(self, flow: http.HTTPFlow):
        """
        Handle HTTP CONNECT requests.

        Tracks sessions that connect to Microsoft login domains.

        Args:
            flow: mitmproxy HTTP flow object
        """
        # Check if this is a CONNECT to Microsoft login domain
        if is_microsoft_login_connect(flow):
            # Get client session key
            client_addr = flow.client_conn.address
            session_key = f"{client_addr[0]}:{client_addr[1]}"

            # Track this session
            self.session_tracker.track_session(session_key)
            logger.info(f"✓ Tracked Microsoft login CONNECT from {session_key}")

    def request(self, flow: http.HTTPFlow):
        """
        Handle HTTP requests.

        Tracks Microsoft login requests and detects OAuth patterns.

        Args:
            flow: mitmproxy HTTP flow object
        """
        if not flow.request:
            return

        # Get client session key
        client_addr = flow.client_conn.address
        session_key = f"{client_addr[0]}:{client_addr[1]}"

        # Check if this is a request to Microsoft login domain
        if (hasattr(flow.request, 'host') and
            isinstance(flow.request.host, str) and
            flow.request.host and
            (flow.request.host == 'login.microsoftonline.com' or
             flow.request.host.endswith('.login.microsoftonline.com'))):
            # Track this session
            self.session_tracker.track_session(session_key)
            logger.info(f"✓ Tracked Microsoft login request from {session_key}")

        # Check for OAuth callback
        if is_oauth_callback(flow):
            logger.info(f"OAuth callback detected from {session_key}, URL: {flow.request.url}")

            if self.session_tracker.is_active(session_key):
                # Check if we already recorded this session recently (deduplication)
                import time
                current_time = time.time()

                if session_key in self.recorded_sessions:
                    last_recorded = self.recorded_sessions[session_key]
                    if current_time - last_recorded < self.dedup_window:
                        logger.info(f"Skipping duplicate login event for {session_key} (within {self.dedup_window}s window)")
                        return

                # Record login event
                self._record_login_event('oauth_callback')

                # Mark this session as recorded
                self.recorded_sessions[session_key] = current_time

                # Remove session after successful match
                self.session_tracker.remove_session(session_key)

                logger.info(f"✓ Recorded OAuth callback login event for session {session_key}")

                # Cleanup old recorded sessions (keep dict from growing indefinitely)
                self._cleanup_recorded_sessions(current_time)
            else:
                logger.info(f"OAuth callback from {session_key} but no active session found")

        # Check for INTERACTIVE login (user entering credentials)
        elif is_interactive_login(flow):
            logger.info(f"Interactive login detected from {session_key}, URL: {flow.request.url}")

            if self.session_tracker.is_active(session_key):
                # Check if we already recorded this session recently (deduplication)
                import time
                current_time = time.time()

                if session_key in self.recorded_sessions:
                    last_recorded = self.recorded_sessions[session_key]
                    if current_time - last_recorded < self.dedup_window:
                        logger.info(f"Skipping duplicate login event for {session_key} (within {self.dedup_window}s window)")
                        return

                # Record login event
                self._record_login_event('interactive_login')

                # Mark this session as recorded
                self.recorded_sessions[session_key] = current_time

                # Remove session after successful match
                self.session_tracker.remove_session(session_key)

                logger.info(f"✓ Recorded interactive login event for session {session_key}")

                # Cleanup old recorded sessions (keep dict from growing indefinitely)
                self._cleanup_recorded_sessions(current_time)
            else:
                logger.info(f"Interactive login from {session_key} but no active session found")

    def _record_login_event(self, detected_via: str):
        """
        Record a login event to the database.

        Args:
            detected_via: Detection method string
        """
        event = LoginEvent.create(detected_via)
        event_id = self.repository.insert_login_event(event)
        logger.debug(f"Inserted login event with ID {event_id}")

    def _cleanup_recorded_sessions(self, current_time: float):
        """
        Remove old entries from recorded_sessions to prevent memory growth.

        Args:
            current_time: Current timestamp
        """
        # Remove sessions older than dedup_window
        expired = [
            key for key, timestamp in self.recorded_sessions.items()
            if current_time - timestamp > self.dedup_window
        ]
        for key in expired:
            del self.recorded_sessions[key]
