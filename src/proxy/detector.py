"""Detection functions for Microsoft login patterns."""
from typing import Any
from urllib.parse import urlparse, parse_qs


def is_microsoft_login_connect(flow: Any) -> bool:
    """
    Check if HTTP CONNECT request is to Microsoft login domain.

    Args:
        flow: mitmproxy flow object with server_conn

    Returns:
        True if CONNECT is to login.microsoftonline.com or subdomain, False otherwise
    """
    if flow.server_conn is None:
        return False

    if flow.server_conn.address is None:
        return False

    host = flow.server_conn.address[0]

    # Check for exact match or subdomain
    if host == 'login.microsoftonline.com':
        return True

    if host.endswith('.login.microsoftonline.com'):
        return True

    return False


def is_oauth_callback(flow: Any) -> bool:
    """
    Check if request is an OAuth/OIDC callback.

    Detects:
    - URLs with code= or state= parameters
    - Paths containing /callback or /auth
    - 302 redirects to callback URLs

    Args:
        flow: mitmproxy flow object with request and optional response

    Returns:
        True if request matches OAuth callback pattern, False otherwise
    """
    if flow.request is None:
        return False

    # Check request URL for OAuth patterns
    if _has_oauth_pattern(flow.request.url):
        return True

    # Check for 302 redirect with OAuth callback in Location header
    if flow.response is not None:
        if flow.response.status_code == 302:
            location = flow.response.headers.get('Location', '')
            if location and _has_oauth_pattern(location):
                return True

    return False


def is_interactive_login(flow: Any) -> bool:
    """
    Check if this is an interactive login (user entering credentials).

    Interactive logins are characterized by:
    - /authorize endpoint (user consent flow)
    - response_type=code (authorization code flow)
    - Presence of nonce/state (new session)

    Args:
        flow: mitmproxy flow object

    Returns:
        True if this is an interactive login, False otherwise
    """
    if not flow.request:
        return False

    try:
        url = flow.request.url
        parsed = urlparse(url)
        path_lower = parsed.path.lower()

        # Check for /authorize endpoint (interactive user consent)
        if '/oauth2/v2.0/authorize' in path_lower or '/oauth2/authorize' in path_lower:
            query_params = parse_qs(parsed.query)

            # Must have response_type=code (authorization code flow, not silent token refresh)
            if 'response_type' in query_params:
                response_type = query_params['response_type'][0].lower()
                if 'code' in response_type:
                    return True

        return False

    except Exception:
        return False


def _has_oauth_pattern(url: str) -> bool:
    """
    Check if URL contains OAuth callback patterns.

    Args:
        url: URL to check

    Returns:
        True if URL has OAuth patterns, False otherwise
    """
    try:
        parsed = urlparse(url)

        # Check for OAuth parameters (case insensitive)
        query_params = parse_qs(parsed.query.lower())
        if 'code' in query_params or 'state' in query_params:
            return True

        # Check for callback paths
        path_lower = parsed.path.lower()
        if '/callback' in path_lower or '/auth' in path_lower:
            return True

        # Check for OAuth authorize endpoint (interactive login)
        if '/oauth2/v2.0/authorize' in path_lower or '/oauth2/authorize' in path_lower:
            return True

    except Exception:
        return False

    return False
