# Quickstart Guide: Auto-Refresh Statistics Grid

**Feature**: 004-statistics-refresh
**Branch**: `004-statistics-refresh`
**Date**: 2025-11-22

## Overview

This guide walks developers through implementing the auto-refresh statistics grid feature. The implementation follows test-first development (TDD) principles per the project constitution.

## Prerequisites

- Branch `004-statistics-refresh` checked out
- Python 3.11+ environment activated
- All dependencies installed (`pip install -r requirements.txt`)
- pytest available for running tests
- Understanding of existing codebase structure

## Implementation Phases

### Phase 1: Backend API Endpoint (Test-First)

#### Step 1.1: Write Contract Tests

Create `/tests/contract/test_statistics_api.py`:

```python
"""Contract tests for /api/statistics endpoint."""
import pytest
from src.dashboard.app import create_app

def test_statistics_endpoint_returns_200():
    """Test that /api/statistics returns 200 OK."""
    # Setup
    app = create_app('data/test_logins.db')
    client = app.test_client()

    # Execute
    response = client.get('/api/statistics')

    # Assert
    assert response.status_code == 200
    assert response.content_type == 'application/json'

def test_statistics_response_schema():
    """Test that /api/statistics response matches contract schema."""
    # Setup
    app = create_app('data/test_logins.db')
    client = app.test_client()

    # Execute
    response = client.get('/api/statistics')
    data = response.get_json()

    # Assert - Required fields
    assert 'today_count' in data
    assert 'week_count' in data
    assert 'month_count' in data
    assert 'total_count' in data
    assert 'period_start' in data
    assert 'period_end' in data

    # Assert - Field types
    assert isinstance(data['today_count'], int)
    assert isinstance(data['week_count'], int)
    assert isinstance(data['month_count'], int)
    assert isinstance(data['total_count'], int)
    assert isinstance(data['period_start'], str)
    assert isinstance(data['period_end'], str)

    # Assert - Non-negative counts
    assert data['today_count'] >= 0
    assert data['week_count'] >= 0
    assert data['month_count'] >= 0
    assert data['total_count'] >= 0
```

**Run tests** (should FAIL):
```bash
pytest tests/contract/test_statistics_api.py -v
```

#### Step 1.2: Implement API Endpoint

Edit `src/dashboard/routes.py`, add after the `graph_data()` function:

```python
@app.route('/api/statistics')
def statistics():
    """
    Get current login statistics.

    Returns:
        JSON response with login counts for today/week/month/all-time
    """
    stats = get_statistics()

    if stats is None:
        return jsonify({'error': 'Internal server error'}), 500

    return jsonify(stats.to_dict()), 200
```

**Run tests** (should PASS):
```bash
pytest tests/contract/test_statistics_api.py -v
```

#### Step 1.3: Write Integration Tests

Create `/tests/integration/test_statistics_endpoint.py`:

```python
"""Integration tests for statistics endpoint end-to-end flow."""
import pytest
from datetime import datetime, timezone
from src.dashboard.app import create_app
from src.storage.repository import Repository
from src.storage.models import LoginEvent

@pytest.fixture
def test_db_with_events(tmp_path):
    """Create test database with sample events."""
    db_path = tmp_path / "test_stats.db"
    repo = Repository(str(db_path))

    # Insert sample events
    event1 = LoginEvent.create('test_method')
    event2 = LoginEvent.create('test_method')
    repo.insert_login_event(event1)
    repo.insert_login_event(event2)

    repo.close()
    return str(db_path)

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
```

**Run tests**:
```bash
pytest tests/integration/test_statistics_endpoint.py -v
```

---

### Phase 2: Frontend Auto-Refresh (Manual Testing)

#### Step 2.1: Create JavaScript Auto-Refresh Module

Create `src/dashboard/static/stats.js`:

```javascript
/**
 * Statistics auto-refresh functionality
 * Polls /api/statistics every 5 seconds and updates the DOM
 */

let statsRefreshInterval = null;
let statElements = null;

/**
 * Load statistics from API and update DOM
 *
 * @param {boolean} silentUpdate - If true, update without logging (for auto-refresh)
 */
async function loadStatistics(silentUpdate = false) {
    try {
        const response = await fetch('/api/statistics');

        if (!response.ok) {
            console.error('Statistics API error:', response.status);
            return; // Keep last known values
        }

        const stats = await response.json();

        if (!silentUpdate) {
            console.log('Statistics loaded:', stats);
        }

        updateStatisticsDOM(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Keep last known values, retry on next cycle
    }
}

/**
 * Update statistics values in the DOM
 *
 * @param {Object} stats - Statistics data from API
 */
function updateStatisticsDOM(stats) {
    if (!statElements) {
        console.error('Stat elements not initialized');
        return;
    }

    // Update each statistic card value
    statElements.today.textContent = stats.today_count;
    statElements.week.textContent = stats.week_count;
    statElements.month.textContent = stats.month_count;
    statElements.total.textContent = stats.total_count;
}

/**
 * Cache DOM element references for statistics cards
 */
function cacheStatElements() {
    statElements = {
        today: document.querySelector('.stat-card:nth-child(1) .stat-value'),
        week: document.querySelector('.stat-card:nth-child(2) .stat-value'),
        month: document.querySelector('.stat-card:nth-child(3) .stat-value'),
        total: document.querySelector('.stat-card:nth-child(4) .stat-value')
    };

    // Validate all elements found
    const missing = Object.entries(statElements)
        .filter(([key, el]) => !el)
        .map(([key]) => key);

    if (missing.length > 0) {
        console.error('Missing stat elements:', missing);
        return false;
    }

    return true;
}

/**
 * Start auto-refresh interval
 */
function startStatsAutoRefresh() {
    // Clear existing interval
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
    }

    // Auto-refresh every 5 seconds (matches graph refresh interval)
    statsRefreshInterval = setInterval(() => {
        loadStatistics(true); // Silent update
    }, 5000);

    console.log('Statistics auto-refresh started (5s interval)');
}

/**
 * Initialize statistics refresh on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Only run if we're on the stats page
    const statsContainer = document.querySelector('.stats-grid');
    if (!statsContainer) {
        return; // Not on stats page
    }

    // Cache DOM element references
    if (!cacheStatElements()) {
        console.error('Failed to initialize statistics refresh - missing DOM elements');
        return;
    }

    // Start auto-refresh
    startStatsAutoRefresh();

    console.log('Statistics refresh initialized');
});
```

#### Step 2.2: Load Script in Template

Edit `src/dashboard/templates/index.html`, add after the graph.js script tag (line 82):

```html
<script src="{{ url_for('static', filename='graph.js') }}"></script>
<script src="{{ url_for('static', filename='stats.js') }}"></script>
```

---

### Phase 3: Manual Testing Checklist

#### Test 3.1: Auto-Refresh Functionality

1. Start the application: `python3 src/main.py`
2. Open dashboard: `http://localhost:8081`
3. Open browser DevTools Console
4. Verify console message: "Statistics refresh initialized"
5. Wait 5 seconds
6. Verify console shows fetch requests to `/api/statistics` every 5 seconds
7. Trigger a new login event (use the proxy)
8. Verify statistics cards update within 5 seconds without page reload

**Expected**: Statistics update automatically every 5 seconds

#### Test 3.2: No Visual Flickering

1. Open dashboard
2. Watch statistics cards for 30 seconds
3. Observe number updates during refresh cycles

**Expected**: Numbers change smoothly without flickering or layout shifts

#### Test 3.3: Error Handling

1. Open dashboard
2. Note current statistics values
3. Stop the Flask backend (Ctrl+C)
4. Wait 10 seconds (2 refresh cycles)
5. Check browser console for error messages
6. Verify statistics retain last known values (don't show "undefined" or "null")
7. Restart Flask backend
8. Verify statistics resume updating within 5 seconds

**Expected**: Graceful error handling, silent retry, immediate recovery

#### Test 3.4: Background Tab Behavior

1. Open dashboard
2. Note current statistics
3. Switch to another browser tab (dashboard loses focus)
4. Wait 30 seconds
5. Switch back to dashboard tab
6. Check if statistics are current

**Expected**: Statistics continue refreshing in background (per clarification decision)

#### Test 3.5: Atomic Updates

1. Open dashboard
2. Open DevTools Network tab
3. Watch for `/api/statistics` requests
4. Observe all 4 statistics cards during updates

**Expected**: All cards update together (no partial updates visible)

---

## Verification

### Final Acceptance Criteria Checklist

From `spec.md`:

- [ ] **AS-1**: "Today" count increments automatically within 5 seconds when new login occurs
- [ ] **AS-2**: "Today" count resets correctly at midnight UTC boundary
- [ ] **AS-3**: All statistics cards update simultaneously (no partial updates)
- [ ] **AS-4**: Statistics continue updating correctly for 30+ minutes without memory leaks

### Success Criteria Verification

- [ ] **SC-001**: Statistics update within 5 seconds of new login events
- [ ] **SC-002**: Users can monitor dashboard for 30+ minutes without manual refresh
- [ ] **SC-003**: Statistics updates complete in under 200ms (check Network tab timing)
- [ ] **SC-004**: Zero visual flickering or layout shifts during updates
- [ ] **SC-005**: Statistics accurate across day/week/month boundaries

### All Tests Passing

```bash
# Run full test suite
pytest -v

# Expected: All tests pass, including new contract and integration tests
```

---

## Troubleshooting

### Issue: Statistics not updating

**Check**:
1. Browser console for JavaScript errors
2. Network tab shows `/api/statistics` requests every 5 seconds
3. Responses return 200 status with valid JSON
4. DOM element selectors match actual HTML structure

**Fix**: Verify `stats.js` is loaded and `cacheStatElements()` finds all elements

### Issue: "Missing stat elements" console error

**Check**: HTML template has exactly 4 `.stat-card` elements in correct order

**Fix**: Ensure `index.html` structure matches expected DOM selectors

### Issue: Statistics showing "undefined"

**Check**: API response includes all required fields

**Fix**: Verify `/api/statistics` endpoint returns complete `LoginStatistics.to_dict()` object

---

## Next Steps

After completing this quickstart:

1. Run `/speckit.tasks` to generate detailed implementation tasks
2. Follow task-by-task implementation workflow
3. Commit changes with test-first approach (tests, then implementation, then commit)
4. Verify all constitution compliance gates before PR

## References

- **Specification**: `specs/004-statistics-refresh/spec.md`
- **Implementation Plan**: `specs/004-statistics-refresh/plan.md`
- **Data Model**: `specs/004-statistics-refresh/data-model.md`
- **API Contract**: `specs/004-statistics-refresh/contracts/api-statistics.openapi.yaml`
- **Constitution**: `.specify/memory/constitution.md`
