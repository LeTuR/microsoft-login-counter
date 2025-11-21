"""Unit tests for detector functions."""
import pytest
from unittest.mock import Mock

from src.proxy.detector import is_microsoft_login_connect, is_oauth_callback


class TestIsMicrosoftLoginConnect:
    """Test is_microsoft_login_connect function."""

    def test_returns_true_for_exact_match(self):
        """Test returns True for exact login.microsoftonline.com match."""
        mock_flow = Mock()
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('login.microsoftonline.com', 443)

        assert is_microsoft_login_connect(mock_flow) is True

    def test_returns_true_for_subdomain(self):
        """Test returns True for subdomains like tenant.login.microsoftonline.com."""
        mock_flow = Mock()
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('tenant-123.login.microsoftonline.com', 443)

        assert is_microsoft_login_connect(mock_flow) is True

    def test_returns_false_for_different_host(self):
        """Test returns False for non-Microsoft hosts."""
        mock_flow = Mock()
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('example.com', 443)

        assert is_microsoft_login_connect(mock_flow) is False

    def test_returns_false_for_similar_host(self):
        """Test returns False for similar but different hosts."""
        mock_flow = Mock()
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('login-microsoftonline.com', 443)

        assert is_microsoft_login_connect(mock_flow) is False

    def test_returns_false_for_none_server_conn(self):
        """Test returns False when server_conn is None."""
        mock_flow = Mock()
        mock_flow.server_conn = None

        assert is_microsoft_login_connect(mock_flow) is False

    def test_returns_false_for_none_address(self):
        """Test returns False when server address is None."""
        mock_flow = Mock()
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = None

        assert is_microsoft_login_connect(mock_flow) is False

    def test_handles_different_ports(self):
        """Test works with different ports (not just 443)."""
        mock_flow = Mock()
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('login.microsoftonline.com', 8443)

        assert is_microsoft_login_connect(mock_flow) is True


class TestIsOAuthCallback:
    """Test is_oauth_callback function."""

    def test_returns_true_for_code_parameter(self):
        """Test returns True for URL with code= parameter."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://app.com/callback?code=AUTH_CODE'
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is True

    def test_returns_true_for_state_parameter(self):
        """Test returns True for URL with state= parameter."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://app.com/auth?state=STATE_VALUE'
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is True

    def test_returns_true_for_callback_path(self):
        """Test returns True for /callback path."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://app.com/callback'
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is True

    def test_returns_true_for_auth_path(self):
        """Test returns True for /auth path."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://app.com/auth'
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is True

    def test_returns_true_for_oauth_callback_path(self):
        """Test returns True for /oauth/callback path."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://app.com/oauth/callback'
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is True

    def test_returns_false_for_regular_url(self):
        """Test returns False for non-callback URLs."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://app.com/home'
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is False

    def test_returns_false_for_none_request(self):
        """Test returns False when request is None."""
        mock_flow = Mock()
        mock_flow.request = None
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is False

    def test_returns_true_for_redirect_with_code(self):
        """Test returns True for 302 redirect with code in Location header."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://login.com/authorize'
        mock_flow.response = Mock()
        mock_flow.response.status_code = 302
        mock_flow.response.headers = {'Location': 'https://app.com/callback?code=ABC'}

        assert is_oauth_callback(mock_flow) is True

    def test_returns_false_for_redirect_without_oauth_pattern(self):
        """Test returns False for 302 redirect without OAuth patterns."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://site.com/page'
        mock_flow.response = Mock()
        mock_flow.response.status_code = 302
        mock_flow.response.headers = {'Location': 'https://site.com/home'}

        assert is_oauth_callback(mock_flow) is False

    def test_handles_missing_location_header(self):
        """Test handles 302 redirect with missing Location header."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://site.com/page'
        mock_flow.response = Mock()
        mock_flow.response.status_code = 302
        mock_flow.response.headers = {}

        assert is_oauth_callback(mock_flow) is False

    def test_case_insensitive_parameter_matching(self):
        """Test parameter matching is case insensitive."""
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://app.com/auth?CODE=ABC&STATE=123'
        mock_flow.response = None

        assert is_oauth_callback(mock_flow) is True
