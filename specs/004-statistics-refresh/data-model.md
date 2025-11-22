# Data Model: Auto-Refresh Statistics Grid

**Feature**: 004-statistics-refresh
**Date**: 2025-11-22

## Overview

This document defines the data structures used for the auto-refresh statistics feature. The feature primarily reuses existing data models from the codebase, with the API endpoint exposing a JSON representation of the `LoginStatistics` entity.

## Entities

### LoginStatistics (Existing)

**Location**: `src/storage/models.py` (lines 38-61)
**Purpose**: Aggregated login statistics for different time periods
**Usage**: Computed by `compute_statistics()` function, returned by `/api/statistics` endpoint

**Fields**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `today_count` | integer | Yes | Number of login events today (current day UTC) | >= 0 |
| `week_count` | integer | Yes | Number of login events this week (Monday-Sunday) | >= 0 |
| `month_count` | integer | Yes | Number of login events this month (calendar month) | >= 0 |
| `total_count` | integer | Yes | Total number of login events all-time | >= 0 |
| `period_start` | ISO 8601 datetime (UTC) | Yes | Start of current day period (midnight UTC) | Valid datetime |
| `period_end` | ISO 8601 datetime (UTC) | Yes | End of current day period (23:59:59.999 UTC) | Valid datetime |
| `first_event` | ISO 8601 datetime (UTC) | No | Timestamp of first login event ever recorded | Valid datetime or null |
| `last_event` | ISO 8601 datetime (UTC) | No | Timestamp of most recent login event | Valid datetime or null |

**Relationships**: None (value object)

**State Transitions**: Immutable (recomputed on each API request)

**Example JSON**:
```json
{
    "today_count": 5,
    "week_count": 23,
    "month_count": 67,
    "total_count": 420,
    "period_start": "2025-11-22T00:00:00Z",
    "period_end": "2025-11-22T23:59:59.999999Z",
    "first_event": "2025-11-15T10:30:00Z",
    "last_event": "2025-11-22T14:22:00Z"
}
```

**Serialization**:
- Python dataclass uses existing `.to_dict()` method (lines 50-61)
- Datetime fields serialized to ISO 8601 format with 'Z' suffix (UTC)
- Optional fields serialize to `null` when absent

**Validation Rules** (from spec requirements):
1. Time-based counts (`today_count`, `week_count`, `month_count`) MUST use server-provided timestamps (FR-004)
2. All counts MUST be non-negative integers
3. `period_start` MUST be before or equal to `period_end`
4. If `first_event` exists, it MUST be before or equal to `last_event`
5. `total_count` MUST be >= `month_count` >= `week_count` (logically)

---

## No New Entities Required

This feature does **not** introduce new data models. It exclusively uses the existing `LoginStatistics` dataclass that was created for the initial dashboard implementation.

**Rationale**: The feature is a presentation-layer enhancement (auto-refresh) rather than a new business capability. The statistics calculation logic (`compute_statistics()`) and data structure already exist and are sufficient.

---

## API Response Format

### GET /api/statistics

**Response Body** (JSON):

Directly returns `LoginStatistics.to_dict()` output:

```json
{
    "today_count": 5,
    "week_count": 23,
    "month_count": 67,
    "total_count": 420,
    "period_start": "2025-11-22T00:00:00Z",
    "period_end": "2025-11-22T23:59:59.999999Z",
    "first_event": "2025-11-15T10:30:00Z",
    "last_event": "2025-11-22T14:22:00Z"
}
```

**Status Codes**:
- `200 OK`: Successfully computed and returned statistics
- `500 Internal Server Error`: Database error or computation failure

**Error Response** (500):
```json
{
    "error": "Internal server error"
}
```

---

## Frontend Data Consumption

### JavaScript Representation

The JavaScript frontend consumes the JSON response directly without transformation:

```javascript
// Response parsed from fetch('/api/statistics')
const stats = {
    today_count: 5,
    week_count: 23,
    month_count: 67,
    total_count: 420,
    period_start: "2025-11-22T00:00:00Z",
    period_end: "2025-11-22T23:59:59.999999Z",
    first_event: "2025-11-15T10:30:00Z",
    last_event: "2025-11-22T14:22:00Z"
};
```

**Fields Used for Display**:
- `today_count` → "Today" statistic card
- `week_count` → "This Week" statistic card
- `month_count` → "This Month" statistic card
- `total_count` → "All Time" statistic card

**Fields Not Displayed** (but present in response):
- `period_start`, `period_end`: Not shown to users (spec: "Out of Scope - Displaying 'last updated' timestamp")
- `first_event`, `last_event`: Already displayed in "Details" section from initial page load (not auto-refreshed)

---

## Time Period Calculations

### Period Definitions

**Today**: Current calendar day in UTC timezone
- Start: `00:00:00.000000 UTC`
- End: `23:59:59.999999 UTC`
- Resets at midnight UTC

**This Week**: Current ISO week (Monday = start, Sunday = end)
- Start: Monday `00:00:00.000000 UTC`
- End: Sunday `23:59:59.999999 UTC`
- Resets at midnight UTC on Monday

**This Month**: Current calendar month in UTC
- Start: 1st day of month `00:00:00.000000 UTC`
- End: Last day of month `23:59:59.999999 UTC`
- Resets at midnight UTC on 1st of month

**All Time**: No time filter
- Counts all events in database since first recorded event

### Calculation Functions (Existing)

**Location**: `src/storage/time_utils.py`

- `get_day_bounds(reference_time)` → (day_start, day_end)
- `get_week_bounds(reference_time)` → (week_start, week_end)
- `get_month_bounds(reference_time)` → (month_start, month_end)

These functions are already implemented and tested. No changes required.

---

## Data Flow

```
1. JavaScript: setInterval() triggers every 5 seconds
2. JavaScript: fetch('/api/statistics')
3. Flask: Route handler calls get_statistics()
4. Python: compute_statistics(repository)
5. Python: Query database for each time period
6. Python: Construct LoginStatistics dataclass
7. Python: Return LoginStatistics.to_dict() as JSON
8. JavaScript: Parse JSON response
9. JavaScript: Update DOM elements with new counts
10. Repeat every 5 seconds
```

---

## Data Integrity Requirements

From spec functional requirements:

**FR-002: Atomic Updates**
- All statistics (`today_count`, `week_count`, `month_count`, `total_count`) MUST update together
- Implementation: Single API call returns all counts in one JSON object
- Frontend: Updates all DOM elements sequentially (fast enough to appear atomic)

**FR-004: Server-Time Based Calculations**
- Time boundaries calculated using server's current UTC time
- `reference_time` parameter in `compute_statistics()` defaults to `datetime.now(timezone.utc)`
- Prevents client clock skew issues

**FR-003: Error Handling**
- On API error (500 status or network failure):
  - JavaScript retains last known statistics values (does not update DOM)
  - Console logs error for debugging
  - Retries on next 5-second cycle indefinitely

---

## Summary

**Existing Models Reused**: `LoginStatistics` (no modifications)
**New Models Created**: None
**API Contract**: JSON representation of `LoginStatistics.to_dict()`
**Validation**: Non-negative counts, datetime ordering, server-time calculation
**Frontend Consumption**: Direct snake_case JSON, no transformation needed
