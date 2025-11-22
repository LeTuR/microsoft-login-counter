# Research: Auto-Refresh Statistics Grid

**Feature**: 004-statistics-refresh
**Date**: 2025-11-22
**Status**: Complete

## Overview

This document consolidates technical research for implementing auto-refresh functionality for the statistics grid. The feature will enable the dashboard statistics cards (Today, This Week, This Month, All Time) to update automatically every 5 seconds, matching the existing graph auto-refresh behavior.

## Research Questions & Findings

### 1. API Endpoint Design for Statistics

**Question**: Should we create a new `/api/statistics` endpoint or extend the existing `/` route?

**Decision**: Create new `/api/statistics` endpoint

**Rationale**:
- Separation of concerns: `/` returns HTML (full page render), `/api/statistics` returns JSON (data only)
- Follows existing pattern from `/api/graph-data` endpoint
- Enables future API usage (mobile app, CLI tools) without HTML overhead
- Cleaner caching strategies for API vs page responses

**Alternatives Considered**:
- **Extend `/` to detect JSON requests**: Rejected because it conflates page rendering with API logic, making testing harder
- **Reuse `/api/graph-data` with statistics**: Rejected because graph data and statistics are distinct concerns with different refresh patterns

**Implementation Notes**:
- Endpoint path: `GET /api/statistics`
- Returns JSON representation of `LoginStatistics` object
- Reuses existing `compute_statistics()` function from `src/dashboard/stats.py`
- Response format mirrors the structure passed to `index.html` template

---

### 2. JavaScript Auto-Refresh Pattern

**Question**: What's the best pattern for implementing auto-refresh in JavaScript?

**Decision**: Use `setInterval()` polling pattern matching `graph.js`

**Rationale**:
- Already proven in the codebase (`graph.js` uses this pattern successfully)
- Simple and reliable for 5-second intervals
- No additional dependencies required
- Works in background tabs (per clarification decision)
- Easy to synchronize with graph refresh by using shared interval

**Alternatives Considered**:
- **WebSocket / Server-Sent Events**: Rejected per spec "Out of Scope" section - adds complexity for minimal benefit at 5-second intervals
- **RequestAnimationFrame**: Rejected because this isn't an animation use case, and RAF pauses in background tabs
- **Service Workers**: Rejected as over-engineered for simple polling

**Implementation Notes**:
```javascript
// Pattern from graph.js lines 195-205
let statsRefreshInterval = null;

function startStatsAutoRefresh() {
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
    }

    statsRefreshInterval = setInterval(() => {
        loadStatistics(true); // true = silent update
    }, 5000);
}
```

---

### 3. DOM Update Strategy (Avoiding Flickering)

**Question**: How should we update statistics values without causing visual flickering?

**Decision**: Direct DOM element updates with CSS transition smoothing

**Rationale**:
- Flickering occurs when elements are removed/re-added to DOM
- Direct `.textContent` updates on existing elements are smooth
- CSS transitions can smooth number changes if desired
- No framework needed (React/Vue would be overkill)

**Alternatives Considered**:
- **Full innerHTML replacement**: Rejected because it causes flicker and loses element references
- **Virtual DOM diffing**: Rejected as over-engineered; we're updating 4 numbers
- **Opacity fade transitions**: Considered but not necessary for simple number updates

**Implementation Notes**:
```javascript
// Update existing DOM elements directly
document.querySelector('.stat-card:nth-child(1) .stat-value').textContent = stats.today_count;
document.querySelector('.stat-card:nth-child(2) .stat-value').textContent = stats.week_count;
// etc.
```

**Best Practice**: Cache DOM element references on page load to avoid repeated `querySelector` calls:
```javascript
const statElements = {
    today: document.querySelector('.stat-card:nth-child(1) .stat-value'),
    week: document.querySelector('.stat-card:nth-child(2) .stat-value'),
    month: document.querySelector('.stat-card:nth-child(3) .stat-value'),
    total: document.querySelector('.stat-card:nth-child(4) .stat-value')
};
```

---

### 4. Error Handling Strategy

**Question**: How should the frontend handle API errors during refresh?

**Decision**: Silently retain last known values, log errors to console, retry on next cycle

**Rationale**:
- Per spec FR-003: "retain last known statistics values and retrying indefinitely"
- No user-facing error messages needed for transient failures
- Console logging aids debugging without disrupting UX
- Statistics endpoint is local backend (not external API), so failures should be rare

**Alternatives Considered**:
- **Display error banner**: Rejected as too disruptive for transient network issues
- **Exponential backoff**: Rejected per clarification decision (retry indefinitely at 5s interval)
- **Stop refreshing after N failures**: Rejected per clarification decision

**Implementation Notes**:
```javascript
async function loadStatistics(silentUpdate = false) {
    try {
        const response = await fetch('/api/statistics');

        if (!response.ok) {
            console.error('Statistics API error:', response.status);
            return; // Keep last known values
        }

        const stats = await response.json();
        updateStatisticsDOM(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Keep last known values, retry on next cycle
    }
}
```

---

### 5. API Response Format

**Question**: What structure should the `/api/statistics` JSON response follow?

**Decision**: Flat object with snake_case fields matching Python `LoginStatistics` dataclass

**Rationale**:
- Consistency with existing backend Python naming conventions
- Simple flat structure (no nested objects needed)
- Easier to serialize from existing `LoginStatistics` object
- JavaScript can easily consume snake_case JSON

**Alternatives Considered**:
- **camelCase for JavaScript**: Rejected to maintain consistency with Python backend; conversion adds complexity
- **Nested structure by time period**: Rejected as unnecessary; flat structure is clearer

**Response Schema**:
```json
{
    "today_count": 5,
    "week_count": 23,
    "month_count": 67,
    "total_count": 420,
    "first_event": "2025-11-15T10:30:00Z",
    "last_event": "2025-11-22T14:22:00Z",
    "period_start": "2025-11-01",
    "period_end": "2025-11-30"
}
```

**Note**: Timestamps use ISO 8601 format for consistency with existing `/api/graph-data` endpoint.

---

### 6. Synchronization Between Graph and Statistics Refresh

**Question**: Should graph and statistics refresh be synchronized or independent?

**Decision**: Independent but aligned intervals (both 5 seconds)

**Rationale**:
- Independent intervals are simpler to implement (no shared state needed)
- Both using 5-second intervals ensures they stay roughly synchronized
- If one refresh fails, the other continues unaffected
- Slight timing drift (<1s) is acceptable and won't be noticeable to users

**Alternatives Considered**:
- **Single shared interval**: Rejected because it couples two independent concerns
- **Master/slave relationship**: Rejected as over-engineered; no benefit over aligned intervals

**Implementation Notes**:
- `graph.js` manages graph refresh interval
- `stats.js` manages statistics refresh interval
- Both use `setInterval(..., 5000)`
- Both start on `DOMContentLoaded` event

---

### 7. Testing Strategy

**Question**: How should we test the auto-refresh functionality?

**Decision**: Backend integration/contract tests + manual frontend testing

**Rationale**:
- Backend API testable with pytest (contract tests, integration tests)
- Frontend behavior (no flickering, smooth updates) best verified manually in browser
- Project doesn't have JavaScript unit test infrastructure (Jasmine/Jest not set up)
- Per constitution: "Test what matters" - manual testing is pragmatic for this feature

**Test Coverage Plan**:

**Backend Tests** (pytest):
- **Contract Test**: Verify `/api/statistics` response schema matches specification
- **Integration Test**: Verify end-to-end flow (DB → Repository → compute_statistics → JSON response)
- **Unit Test**: Verify statistics calculation across day/week/month boundaries
- **Error Test**: Verify graceful handling when database is unavailable

**Frontend Tests** (manual browser testing):
- Verify statistics update every 5 seconds without page reload
- Verify no visual flickering during updates
- Verify all 4 statistics update simultaneously (atomic updates)
- Verify statistics continue updating in background tab
- Verify statistics retain last known values when API call fails (test by stopping backend)
- Verify Day/Week/Month counts update correctly when crossing time boundaries

**Alternatives Considered**:
- **Add Jest for JavaScript unit tests**: Rejected as over-investment for ~50 lines of simple polling code
- **Selenium/Playwright E2E tests**: Rejected as too heavy for this feature scope

---

## Technology Summary

### Backend Stack
- **Framework**: Flask (existing)
- **Language**: Python 3.11+
- **Data Access**: Repository pattern with SQLite
- **Testing**: pytest (integration, contract, unit tests)

### Frontend Stack
- **Language**: JavaScript ES6+ (vanilla, no frameworks)
- **HTTP Client**: Fetch API (native browser support)
- **DOM Manipulation**: Direct element updates via `querySelector`
- **Timer**: `setInterval()` for polling
- **Testing**: Manual browser testing

### Integration Points
- **API Endpoint**: `GET /api/statistics` (new)
- **Existing Functions**: `compute_statistics()` from `src/dashboard/stats.py`
- **Existing Pattern**: Auto-refresh pattern from `src/dashboard/static/graph.js`

---

## Key Decisions Summary

| Decision Area | Choice | Rationale |
|---------------|--------|-----------|
| API Design | New `/api/statistics` endpoint | Separates API from HTML rendering, follows existing pattern |
| Refresh Pattern | `setInterval()` polling | Proven in codebase, simple, reliable |
| DOM Updates | Direct `.textContent` updates | Avoids flickering, no framework needed |
| Error Handling | Silent retry with console logging | Follows spec requirement for indefinite retry |
| Response Format | Flat JSON with snake_case | Matches Python backend conventions |
| Synchronization | Independent aligned intervals | Simple and decoupled |
| Testing | Backend pytest + manual frontend | Pragmatic, tests what matters |

---

## Open Questions

**None** - All technical decisions finalized.

---

## Next Steps

Proceed to **Phase 1: Design & Contracts** to generate:
1. `data-model.md` - Data structures for API response
2. `contracts/` - OpenAPI specification for `/api/statistics` endpoint
3. `quickstart.md` - Developer guide for implementing the feature
