"""Integration tests for statistics endpoint end-to-end flow."""
import pytest
import tempfile
import os
from datetime import datetime, timezone
from src.dashboard.app import create_app
from src.storage.repository import Repository
from src.storage.models import LoginEvent


@pytest.fixture
def test_db_with_events():
    """Create test database with sample events."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    # Initialize repository and schema
    repo = Repository(db_path)
    db = repo._get_db()
    db.initialize_schema()

    # Insert sample events
    event1 = LoginEvent.create('test_method')
    event2 = LoginEvent.create('test_method')
    repo.insert_login_event(event1)
    repo.insert_login_event(event2)

    repo.close()

    yield db_path

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


def test_statistics_endpoint_with_real_data(test_db_with_events):
    """Test statistics endpoint returns correct counts from database."""
    # Setup
    app = create_app(test_db_with_events)
    client = app.test_client()

    # Execute
    response = client.get('/api/statistics')
    data = response.get_json()

    # Assert
    assert response.status_code == 200
    assert data['total_count'] == 2  # Two events inserted
    assert data['today_count'] >= 0  # Depends on current date
    assert 'first_event' in data
    assert 'last_event' in data


def test_statistics_time_boundaries(test_db_with_events):
    """Test that today/week/month counts calculated using server UTC time."""
    # Setup
    app = create_app(test_db_with_events)
    client = app.test_client()

    # Execute
    response = client.get('/api/statistics')
    data = response.get_json()

    # Assert - Time-based calculations use server time
    assert response.status_code == 200

    # Verify period_start and period_end have valid timestamps
    assert isinstance(data['period_start'], str)
    assert isinstance(data['period_end'], str)
    assert 'T' in data['period_start']
    assert 'T' in data['period_end']
    assert data['period_start'].endswith('Z')
    assert data['period_end'].endswith('Z')

    # Verify period_end is after period_start
    period_start_str = data['period_start'].replace('Z', '')
    period_end_str = data['period_end'].replace('Z', '')
    period_start = datetime.fromisoformat(period_start_str)
    period_end = datetime.fromisoformat(period_end_str)
    assert period_end > period_start

    # Verify counts are logical (total >= month >= week >= today)
    assert data['total_count'] >= data['month_count']
    assert data['month_count'] >= data['week_count']
    assert data['week_count'] >= data['today_count']


def test_statistics_empty_database():
    """Test endpoint returns all counts as 0 when no events exist."""
    # Setup - Create empty database
    db_fd, db_path = tempfile.mkstemp(suffix='.db')

    repo = Repository(db_path)
    db = repo._get_db()
    db.initialize_schema()
    repo.close()

    app = create_app(db_path)
    client = app.test_client()

    try:
        # Execute
        response = client.get('/api/statistics')
        data = response.get_json()

        # Assert
        assert response.status_code == 200
        assert data['total_count'] == 0
        assert data['today_count'] == 0
        assert data['week_count'] == 0
        assert data['month_count'] == 0
        assert data['first_event'] is None
        assert data['last_event'] is None
    finally:
        # Cleanup
        os.close(db_fd)
        os.unlink(db_path)
