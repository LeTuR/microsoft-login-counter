# Data Model: Bar Chart Visualization

**Feature**: Bar Chart Visualization for Daily Login Trends
**Date**: 2025-11-22
**Phase**: Phase 1 - Design

## Overview

This feature reuses the existing data model from feature 002-dashboard-graphs with no database schema changes. The bar chart visualization consumes the same API response structure but interprets the data differently on the frontend.

---

## Existing Data Model (No Changes)

### GraphDataPoint

**Source**: `src/storage/models.py` (existing)

**Purpose**: Represents a single aggregated time bucket with login count

**Fields**:
- `bucket` (str): Time bucket label (e.g., "2025-11-22", "2025-11-22 14:00:00", "2025-W47")
- `count` (int): Number of login events in this bucket
- `timestamp` (datetime): UTC timestamp of bucket start

**Serialization**:
```python
def to_dict(self) -> dict:
    return {
        "bucket": self.bucket,
        "count": self.count,
        "timestamp": self.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
    }
```

**Validation Rules**:
- `count` >= 0 (zero for days with no logins)
- `bucket` format matches aggregation level (daily: YYYY-MM-DD, hourly: YYYY-MM-DD HH:00:00, weekly: YYYY-W##)
- `timestamp` always in UTC

**State Transitions**: N/A (immutable value object)

---

### TimePeriodFilter

**Source**: `src/storage/models.py` (existing)

**Purpose**: Represents user-selected time range filter

**Fields**:
- `period` (TimePeriod enum): One of "24h", "7d", "30d", "all"
- `start_date` (datetime): UTC start of time range
- `end_date` (datetime): UTC end of time range (typically now)

**Validation Rules**:
- `start_date` <= `end_date`
- `period` must be valid TimePeriod enum value

**State Transitions**: N/A (immutable value object)

---

### GraphDataResponse

**Source**: `src/storage/models.py` (existing)

**Purpose**: Complete API response for graph data endpoint

**Fields**:
- `data_points` (List[GraphDataPoint]): Aggregated data points
- `period` (str): Selected period filter ("24h", "7d", "30d", "all")
- `aggregation_level` (str): Applied aggregation ("hour", "day", "week")
- `total_events` (int): Sum of all counts
- `date_range` (dict): `{"start": ISO8601, "end": ISO8601}`

**Serialization**:
```python
def to_dict(self) -> dict:
    return {
        "dataPoints": [dp.to_dict() for dp in self.data_points],
        "period": self.period,
        "aggregationLevel": self.aggregation_level,
        "totalEvents": self.total_events,
        "dateRange": self.date_range
    }
```

**Validation Rules**:
- `total_events` == sum of all `data_points[].count`
- `data_points` ordered chronologically by timestamp
- `aggregation_level` in ["hour", "day", "week"]

---

## Frontend Data Structures (New for Bar Chart)

### BarChartConfig

**Location**: `src/dashboard/static/graph.js` (new interface, not a class)

**Purpose**: Configuration object for Chart.js bar chart initialization

**Structure**:
```javascript
{
  type: 'bar',
  data: {
    labels: Date[],              // X-axis timestamps (Date objects)
    datasets: [{
      label: 'Login Events',
      data: number[],             // Y-axis counts
      backgroundColor: string[],  // Gradient colors (one per bar)
      borderColor: '#fff',
      borderWidth: 1,
      barPercentage: 0.9,        // Bar width (90% of available space)
      categoryPercentage: 0.8    // Category width (80% of axis space)
    }]
  },
  options: {
    // Chart.js options (responsive, tooltips, scales, etc.)
  }
}
```

**Validation Rules**:
- `labels.length` == `data.length` == `backgroundColor.length`
- `backgroundColor` array contains valid RGB color strings
- `barPercentage` and `categoryPercentage` between 0 and 1

---

### GradientColorCalculator

**Location**: `src/dashboard/static/graph.js` (new function)

**Purpose**: Calculate gradient blue colors based on login count range

**Input**:
```javascript
{
  dataPoints: [
    { bucket: string, count: number, timestamp: string },
    ...
  ]
}
```

**Output**:
```javascript
[
  "rgb(173, 216, 230)", // Light blue for lowest count
  "rgb(86, 138, 168)",  // Medium blue
  "rgb(0, 61, 107)",    // Dark blue for highest count
  ...
]
```

**Algorithm**:
1. Extract counts: `counts = dataPoints.map(p => p.count)`
2. Find range: `min = Math.min(...counts)`, `max = Math.max(...counts)`
3. For each count:
   - Normalize: `normalized = (count - min) / (max - min)` (0 to 1)
   - Interpolate RGB: `color = lightBlue + (darkBlue - lightBlue) * normalized`
   - Format: `rgb(r, g, b)`

**Edge Cases**:
- All counts equal (max == min): Return array of medium blue (#0078d4)
- Zero counts: Map to lightest blue (#add8e6)
- Single data point: Return medium blue

**Performance**: O(n) where n = number of bars (max 90), ~1ms execution time

---

## Data Flow

### Bar Chart Rendering Flow

```
1. User visits dashboard OR filter changes OR auto-refresh triggers
   ↓
2. fetch('/api/graph-data?period=7d')
   ↓
3. GraphDataResponse { dataPoints: [...], aggregationLevel: 'day', ... }
   ↓
4. Frontend: renderGraph(data, silentUpdate=false)
   ↓
5. Extract labels (timestamps) and counts from dataPoints
   ↓
6. calculateGradientColors(dataPoints) → color array
   ↓
7. Create/update Chart.js bar chart with:
   - type: 'bar'
   - data: { labels, datasets: [{ data: counts, backgroundColor: colors }] }
   - options: { responsive, tooltips, scales }
   ↓
8. Chart.js renders bar chart with gradient colors
   ↓
9. User interaction: hover → tooltip shows date + count
```

### Auto-Refresh Update Flow

```
1. setInterval (5 seconds) triggers loadGraphData(period, silentUpdate=true)
   ↓
2. fetch('/api/graph-data?period=' + currentPeriod)
   ↓
3. GraphDataResponse { dataPoints: [...] } (may include new events)
   ↓
4. Frontend: renderGraph(data, silentUpdate=true)
   ↓
5. calculateGradientColors(dataPoints) → new color array
   ↓
6. chartInstance.data.labels = newLabels
   chartInstance.data.datasets[0].data = newCounts
   chartInstance.data.datasets[0].backgroundColor = newColors
   ↓
7. chartInstance.update('none') → smooth update, no animation
```

---

## Testing Strategy

### Unit Tests

**Test File**: `tests/unit/test_gradient.py` (new)

**Coverage**:
- `test_gradient_two_values()`: Verify light→dark interpolation
- `test_gradient_single_value()`: All same count returns medium blue
- `test_gradient_zero_values()`: Zero maps to lightest blue
- `test_gradient_large_range()`: 0 to 1000 count range
- `test_gradient_rgb_format()`: Output is valid "rgb(r, g, b)" string
- `test_gradient_performance()`: 90 bars calculated in < 5ms

**Test File**: `tests/unit/test_aggregation.py` (existing, no changes needed)

**Existing Coverage** (already tests bar chart data source):
- GraphDataPoint serialization
- determine_aggregation_level() with 90-day threshold
- get_aggregated_graph_data() query logic

---

### Integration Tests

**Test File**: `tests/integration/test_bar_rendering.py` (new)

**Coverage**:
- `test_bar_chart_renders_with_gradient()`: End-to-end bar chart with gradient colors
- `test_zero_height_bars_visible()`: Days with 0 logins show zero-height bars
- `test_90_day_threshold_weekly_aggregation()`: > 90 days triggers weekly bars
- `test_gradient_updates_on_filter_change()`: Colors recalculate when switching periods
- `test_mobile_bar_touch_targets()`: Bars meet 44px minimum on 320px screen
- `test_auto_refresh_gradient_update()`: Silent update recalculates gradient

---

### Contract Tests

**Test File**: `tests/contract/test_graph_api.py` (existing, verify compatibility)

**Coverage**:
- Verify `/api/graph-data` response structure unchanged
- Bar chart can consume existing GraphDataResponse format
- No breaking changes to API contract

---

## Database Schema

**Changes**: NONE

The existing `login_events` table schema remains unchanged:

```sql
CREATE TABLE login_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,           -- ISO 8601 UTC format
    unix_timestamp INTEGER NOT NULL,   -- Unix epoch seconds
    detected_via TEXT NOT NULL         -- Detection method
);
```

---

## Migration Notes

**From Line Chart to Bar Chart**:

1. **No data migration needed**: Same data source (`/api/graph-data` endpoint)
2. **Frontend changes only**: Modify `graph.js` Chart.js configuration
3. **Backward compatibility**: API response format unchanged
4. **Graceful upgrade**: Users see bar chart on next page load

**Rollback Strategy**:
- Revert `graph.js` to previous version (change `type: 'bar'` back to `type: 'line'`)
- No database rollback needed (no schema changes)

---

## Performance Considerations

**Gradient Calculation Complexity**: O(n) where n = number of bars
- Best case: n = 1 (single bar) → ~0.1ms
- Typical case: n = 30 (30-day view) → ~0.5ms
- Worst case: n = 90 (90-day threshold) → ~1ms
- No performance impact on 5-second auto-refresh

**Memory Footprint**: Minimal increase
- Color array: 90 strings × ~15 bytes = ~1.35 KB
- Negligible impact on browser memory

**Chart.js Rendering**: No change from line chart
- Same rendering engine
- Bar chart may be slightly faster than line chart (no curve calculations)

---

## Dependencies

**Existing** (No new dependencies):
- Chart.js v4.4.1 (frontend)
- date-fns adapter for Chart.js (frontend)
- Flask 3.0.0+ (backend)
- SQLite3 (database)

**Browser Compatibility**:
- Modern browsers with ES6 support (Chrome 60+, Firefox 55+, Safari 11+, Edge 79+)
- Chart.js v4.4.1 browser support matches existing line chart

---

## Summary

**Data Model Changes**: NONE
- Reuses existing GraphDataPoint, TimePeriodFilter, GraphDataResponse
- No database schema changes
- No new API endpoints

**New Frontend Structures**:
- BarChartConfig (Chart.js configuration object)
- GradientColorCalculator (color interpolation function)

**Testing Coverage**:
- New unit tests for gradient calculation
- New integration tests for bar chart rendering
- Existing contract tests verify API compatibility

**Risk**: LOW
- No breaking changes to data model or API
- Frontend-only modifications
- Existing aggregation logic reused
