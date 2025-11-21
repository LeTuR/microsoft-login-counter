"""Contract test for HTTP CONNECT detection to login.microsoftonline.com."""
import pytest
from unittest.mock import Mock


@pytest.mark.contract
class TestConnectDetection:
    """Contract test for detecting Microsoft login CONNECT requests."""

    def test_is_microsoft_login_connect_with_valid_host(self):
        """Contract: is_microsoft_login_connect returns True for login.microsoftonline.com."""
        # Import the function to test (will fail until implemented)
        from src.proxy.detector import is_microsoft_login_connect

        # Create mock flow with login.microsoftonline.com
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('login.microsoftonline.com', 443)

        # Contract: Should return True for Microsoft login host
        result = is_microsoft_login_connect(mock_flow)
        assert result is True

    def test_is_microsoft_login_connect_with_subdomain(self):
        """Contract: is_microsoft_login_connect returns True for *.login.microsoftonline.com."""
        from src.proxy.detector import is_microsoft_login_connect

        # Create mock flow with subdomain
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('tenant.login.microsoftonline.com', 443)

        # Contract: Should return True for subdomains
        result = is_microsoft_login_connect(mock_flow)
        assert result is True

    def test_is_microsoft_login_connect_with_non_microsoft_host(self):
        """Contract: is_microsoft_login_connect returns False for non-Microsoft hosts."""
        from src.proxy.detector import is_microsoft_login_connect

        # Create mock flow with different host
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('google.com', 443)

        # Contract: Should return False for non-Microsoft hosts
        result = is_microsoft_login_connect(mock_flow)
        assert result is False

    def test_is_microsoft_login_connect_with_similar_host(self):
        """Contract: is_microsoft_login_connect returns False for similar but different hosts."""
        from src.proxy.detector import is_microsoft_login_connect

        # Create mock flow with similar host
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('login-microsoftonline.com', 443)

        # Contract: Should return False for non-exact matches
        result = is_microsoft_login_connect(mock_flow)
        assert result is False

    def test_is_microsoft_login_connect_with_none_server_conn(self):
        """Contract: is_microsoft_login_connect handles None server_conn gracefully."""
        from src.proxy.detector import is_microsoft_login_connect

        # Create mock flow with no server connection
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = None

        # Contract: Should return False when no server connection
        result = is_microsoft_login_connect(mock_flow)
        assert result is False

    def test_is_microsoft_login_connect_function_signature(self):
        """Contract: is_microsoft_login_connect accepts single flow argument."""
        from src.proxy.detector import is_microsoft_login_connect
        import inspect

        # Verify function signature
        sig = inspect.signature(is_microsoft_login_connect)
        params = list(sig.parameters.keys())

        # Contract: Function should accept single parameter (flow)
        assert len(params) == 1
        assert params[0] == 'flow'

    def test_is_microsoft_login_connect_returns_boolean(self):
        """Contract: is_microsoft_login_connect returns boolean type."""
        from src.proxy.detector import is_microsoft_login_connect

        # Create mock flow
        mock_flow = Mock()
        mock_flow.client_conn = Mock()
        mock_flow.client_conn.address = ('127.0.0.1', 54321)
        mock_flow.server_conn = Mock()
        mock_flow.server_conn.address = ('login.microsoftonline.com', 443)

        # Contract: Return type must be boolean
        result = is_microsoft_login_connect(mock_flow)
        assert isinstance(result, bool)
