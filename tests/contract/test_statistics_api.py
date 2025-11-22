"""Contract tests for /api/statistics endpoint."""
import pytest
import tempfile
import os
from src.dashboard.app import create_app
from src.storage.repository import Repository


@pytest.fixture
def test_app():
    """Create a test Flask app with a temporary database."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    # Initialize database schema
    repo = Repository(db_path)
    db = repo._get_db()
    db.initialize_schema()
    repo.close()

    # Create Flask app
    app = create_app(db_path)

    yield app

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


def test_statistics_endpoint_returns_200(test_app):
    """Test that /api/statistics returns 200 OK with JSON content-type."""
    # Setup
    client = test_app.test_client()

    # Execute
    response = client.get('/api/statistics')

    # Assert
    assert response.status_code == 200
    assert 'application/json' in response.content_type


def test_statistics_response_schema(test_app):
    """Test that /api/statistics response matches contract schema."""
    # Setup
    client = test_app.test_client()

    # Execute
    response = client.get('/api/statistics')
    data = response.get_json()

    # Assert - Required fields exist
    assert 'today_count' in data
    assert 'week_count' in data
    assert 'month_count' in data
    assert 'total_count' in data
    assert 'period_start' in data
    assert 'period_end' in data

    # Assert - Field types are correct
    assert isinstance(data['today_count'], int)
    assert isinstance(data['week_count'], int)
    assert isinstance(data['month_count'], int)
    assert isinstance(data['total_count'], int)
    assert isinstance(data['period_start'], str)
    assert isinstance(data['period_end'], str)


def test_statistics_counts_are_non_negative(test_app):
    """Test that all count fields are non-negative integers."""
    # Setup
    client = test_app.test_client()

    # Execute
    response = client.get('/api/statistics')
    data = response.get_json()

    # Assert - All counts >= 0
    assert data['today_count'] >= 0
    assert data['week_count'] >= 0
    assert data['month_count'] >= 0
    assert data['total_count'] >= 0


def test_statistics_timestamps_are_iso8601(test_app):
    """Test that timestamp fields are valid ISO 8601 strings."""
    # Setup
    client = test_app.test_client()

    # Execute
    response = client.get('/api/statistics')
    data = response.get_json()

    # Assert - period_start and period_end are ISO 8601 strings
    assert isinstance(data['period_start'], str)
    assert isinstance(data['period_end'], str)

    # Verify format contains 'T' and ends with 'Z' (ISO 8601 UTC format)
    assert 'T' in data['period_start']
    assert data['period_start'].endswith('Z')
    assert 'T' in data['period_end']
    assert data['period_end'].endswith('Z')

    # Optional fields (first_event, last_event) should be null or ISO 8601
    if data.get('first_event') is not None:
        assert isinstance(data['first_event'], str)
        assert 'T' in data['first_event']
        assert data['first_event'].endswith('Z')

    if data.get('last_event') is not None:
        assert isinstance(data['last_event'], str)
        assert 'T' in data['last_event']
        assert data['last_event'].endswith('Z')
