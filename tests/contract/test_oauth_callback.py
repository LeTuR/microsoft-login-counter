"""Contract test for OAuth callback pattern matching."""
import pytest
from unittest.mock import Mock


@pytest.mark.contract
class TestOAuthCallback:
    """Contract test for detecting OAuth/OIDC callback responses."""

    def test_is_oauth_callback_with_code_parameter(self):
        """Contract: is_oauth_callback returns True for URLs with code= parameter."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with OAuth callback URL
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/callback?code=AUTH_CODE&state=STATE_VALUE'

        # Contract: Should return True for code parameter
        result = is_oauth_callback(mock_flow)
        assert result is True

    def test_is_oauth_callback_with_state_parameter(self):
        """Contract: is_oauth_callback returns True for URLs with state= parameter."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with state parameter only
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/auth?state=STATE_VALUE&code=AUTH_CODE'

        # Contract: Should return True for state parameter
        result = is_oauth_callback(mock_flow)
        assert result is True

    def test_is_oauth_callback_with_callback_path(self):
        """Contract: is_oauth_callback returns True for /callback path."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with /callback path
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/callback'

        # Contract: Should return True for /callback path
        result = is_oauth_callback(mock_flow)
        assert result is True

    def test_is_oauth_callback_with_auth_path(self):
        """Contract: is_oauth_callback returns True for /auth path."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with /auth path
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/auth'

        # Contract: Should return True for /auth path
        result = is_oauth_callback(mock_flow)
        assert result is True

    def test_is_oauth_callback_with_oauth_callback_path(self):
        """Contract: is_oauth_callback returns True for /oauth/callback path."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with /oauth/callback path
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/oauth/callback?code=ABC'

        # Contract: Should return True for OAuth callback path
        result = is_oauth_callback(mock_flow)
        assert result is True

    def test_is_oauth_callback_with_regular_url(self):
        """Contract: is_oauth_callback returns False for regular URLs."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with regular URL
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/home'

        # Contract: Should return False for non-callback URLs
        result = is_oauth_callback(mock_flow)
        assert result is False

    def test_is_oauth_callback_with_none_request(self):
        """Contract: is_oauth_callback handles None request gracefully."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with no request
        mock_flow = Mock()
        mock_flow.request = None

        # Contract: Should return False when no request
        result = is_oauth_callback(mock_flow)
        assert result is False

    def test_is_oauth_callback_function_signature(self):
        """Contract: is_oauth_callback accepts single flow argument."""
        from src.proxy.detector import is_oauth_callback
        import inspect

        # Verify function signature
        sig = inspect.signature(is_oauth_callback)
        params = list(sig.parameters.keys())

        # Contract: Function should accept single parameter (flow)
        assert len(params) == 1
        assert params[0] == 'flow'

    def test_is_oauth_callback_returns_boolean(self):
        """Contract: is_oauth_callback returns boolean type."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/callback?code=ABC'

        # Contract: Return type must be boolean
        result = is_oauth_callback(mock_flow)
        assert isinstance(result, bool)

    def test_is_oauth_callback_with_302_redirect(self):
        """Contract: is_oauth_callback detects OAuth redirects (302 status)."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with redirect response
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/redirect'
        mock_flow.response = Mock()
        mock_flow.response.status_code = 302
        mock_flow.response.headers = {'Location': 'https://example.com/callback?code=ABC'}

        # Contract: Should detect OAuth callback in redirect Location header
        result = is_oauth_callback(mock_flow)
        assert result is True

    def test_is_oauth_callback_with_regular_302_redirect(self):
        """Contract: is_oauth_callback returns False for non-OAuth redirects."""
        from src.proxy.detector import is_oauth_callback

        # Create mock flow with non-OAuth redirect
        mock_flow = Mock()
        mock_flow.request = Mock()
        mock_flow.request.url = 'https://example.com/page'
        mock_flow.response = Mock()
        mock_flow.response.status_code = 302
        mock_flow.response.headers = {'Location': 'https://example.com/home'}

        # Contract: Should return False for regular redirects
        result = is_oauth_callback(mock_flow)
        assert result is False
