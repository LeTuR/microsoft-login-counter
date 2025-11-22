# Quickstart: Bar Chart Visualization

**Feature**: Bar Chart Visualization for Daily Login Trends
**Date**: 2025-11-22
**Target Audience**: Developers implementing this feature

## Overview

This feature converts the existing line chart to a bar chart with gradient blue colors (light to dark based on login volume). The change is **frontend-only** with minimal code modifications.

---

## What You're Building

### Before (Line Chart)
- Continuous line connecting data points
- Single blue color (#0078d4)
- Good for showing trends over time

### After (Bar Chart)
- Distinct bars for each day
- Gradient blue colors (light = fewer logins, dark = more logins)
- Better for day-to-day comparison

---

## Key Files to Modify

### 1. `src/dashboard/static/graph.js`

**Primary Changes**:
```javascript
// Change chart type (line ~115)
chartInstance = new Chart(ctx, {
-   type: 'line',
+   type: 'bar',
    data: {
        labels: labels,
        datasets: [{
            label: 'Login Events',
            data: counts,
-           borderColor: '#0078d4',
-           backgroundColor: 'rgba(0, 120, 212, 0.1)',
-           borderWidth: 2,
-           fill: true,
-           tension: 0.3,
-           pointRadius: 4,
+           backgroundColor: calculateGradientColors(dataPoints), // New function
+           borderColor: '#fff',
+           borderWidth: 1,
+           barPercentage: 0.9,
+           categoryPercentage: 0.8
        }]
    },
    // ... options remain mostly the same
});
```

**New Function to Add**:
```javascript
/**
 * Calculate gradient blue colors for bars based on login counts
 * @param {Array} dataPoints - Array of {bucket, count, timestamp}
 * @returns {Array} Array of RGB color strings
 */
function calculateGradientColors(dataPoints) {
    const counts = dataPoints.map(p => p.count);
    const min = Math.min(...counts);
    const max = Math.max(...counts);

    // Edge case: all counts equal
    if (max === min) {
        return dataPoints.map(() => '#0078d4');
    }

    const lightBlue = { r: 173, g: 216, b: 230 }; // #add8e6
    const darkBlue = { r: 0, g: 61, b: 107 };     // #003d6b

    return counts.map(count => {
        const normalized = (count - min) / (max - min);
        const r = Math.round(lightBlue.r + (darkBlue.r - lightBlue.r) * normalized);
        const g = Math.round(lightBlue.g + (darkBlue.g - lightBlue.g) * normalized);
        const b = Math.round(lightBlue.b + (darkBlue.b - lightBlue.b) * normalized);
        return `rgb(${r}, ${g}, ${b})`;
    });
}
```

**Update Silent Refresh** (line ~133):
```javascript
if (silentUpdate && chartInstance) {
    chartInstance.data.labels = labels;
    chartInstance.data.datasets[0].data = counts;
+   chartInstance.data.datasets[0].backgroundColor = calculateGradientColors(dataPoints);
    chartInstance.update('none');
    return;
}
```

---

### 2. `src/dashboard/static/style.css` (Optional)

**Potential Bar Chart Styles** (only if needed for visual polish):
```css
/* Bar chart specific styles (if needed) */
.graph-container canvas {
    /* Chart.js handles most styling automatically */
}

/* Zero-height bar indicator (optional enhancement) */
.chartjs-render-monitor {
    /* Add subtle visual cue for zero bars if desired */
}
```

**Note**: Most styling is handled by Chart.js configuration. CSS changes are optional.

---

### 3. `src/dashboard/templates/index.html` (No Changes Expected)

The HTML remains unchanged. The canvas element and container work identically for both line and bar charts:

```html
<!-- Existing structure - no modifications needed -->
<div class="graph-container">
    <canvas id="loginTrendsChart"></canvas>
</div>
```

---

## Implementation Checklist

### Phase 1: Preparation
- [ ] Read existing `graph.js` to understand current line chart implementation
- [ ] Review Chart.js v4.4.1 bar chart documentation
- [ ] Understand gradient color calculation algorithm (research.md)

### Phase 2: Write Tests First (TDD)
- [ ] Write unit tests for `calculateGradientColors()` function
  - Test two values (light→dark)
  - Test all same values (medium blue)
  - Test zero values (lightest blue)
  - Test large range (0 to 1000)
  - Test RGB format validity
- [ ] Write integration tests for bar chart rendering
  - End-to-end with gradient
  - Zero-height bars visible
  - 90-day threshold weekly aggregation
  - Mobile touch targets (44px minimum)
- [ ] Verify tests **FAIL** (no implementation yet)

### Phase 3: Implementation
- [ ] Add `calculateGradientColors()` function to `graph.js`
- [ ] Change Chart.js `type` from 'line' to 'bar'
- [ ] Update dataset configuration:
  - Remove line-specific properties (`tension`, `fill`, `pointRadius`)
  - Add bar-specific properties (`barPercentage`, `categoryPercentage`)
  - Set `backgroundColor` to gradient array
- [ ] Update silent refresh to recalculate gradient colors
- [ ] Test manually in browser (visual verification)

### Phase 4: Verification
- [ ] Run unit tests → all pass
- [ ] Run integration tests → all pass
- [ ] Run contract tests → verify API compatibility
- [ ] Manual testing:
  - Desktop: Gradient colors visible, bars distinct
  - Mobile: Touch targets ≥ 44px, responsive
  - Zero days: Zero-height bars present
  - > 90 days: Weekly aggregation, gradient still works
  - Auto-refresh: Smooth update, gradient recalculates

---

## Testing Commands

```bash
# Unit tests (gradient calculation)
pytest tests/unit/test_gradient.py -v

# Integration tests (bar chart rendering)
pytest tests/integration/test_bar_rendering.py -v

# Contract tests (API compatibility)
pytest tests/contract/test_graph_api.py -v

# All tests
pytest tests/ -v
```

---

## Development Workflow

### 1. Start Dashboard
```bash
# Terminal 1: Start Flask dashboard
python src/dashboard/run.py

# Terminal 2: Start mitmproxy (if testing login detection)
mitmproxy -s src/proxy/addon.py
```

### 2. Generate Test Data
```bash
# Insert sample login events for testing
python -c "
from src.storage.repository import Repository
from src.storage.models import LoginEvent
from datetime import datetime, timedelta

repo = Repository('data/logins.db')
base = datetime(2025, 11, 15, 10, 0, 0)

# Insert 30 days of varying login counts
for day in range(30):
    count = (day % 10) + 1  # Varies 1-10 logins per day
    for i in range(count):
        timestamp = base + timedelta(days=day, hours=i)
        event = LoginEvent(
            id=None,
            timestamp=timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            unix_timestamp=int(timestamp.timestamp()),
            detected_via='oauth_callback'
        )
        repo.insert_login_event(event)
repo.close()
"
```

### 3. Visual Verification
1. Open http://localhost:5000 in browser
2. Check bar chart renders with gradient colors
3. Verify light blue (low counts) to dark blue (high counts)
4. Hover over bars → tooltips work
5. Click filters (24H, 7D, 30D, All) → gradient recalculates
6. Open DevTools → Mobile view → bars meet 44px touch target
7. Wait 5 seconds → auto-refresh updates smoothly

---

## Common Issues & Solutions

### Issue 1: Bars Not Showing
**Symptom**: Canvas renders but no bars visible
**Solution**:
- Check browser console for Chart.js errors
- Verify `data` array has values
- Ensure `backgroundColor` array has same length as `data`

### Issue 2: Gradient Not Working
**Symptom**: All bars same color
**Solution**:
- Check `calculateGradientColors()` is being called
- Verify `min` and `max` are calculated correctly
- Log RGB values to console for debugging

### Issue 3: Zero Bars Not Visible
**Symptom**: Days with 0 logins show no bar
**Solution**:
- Chart.js renders zero-height bars automatically
- Tooltip should still work on hover
- Optional: Add CSS for visual indicator

### Issue 4: Silent Update Flickering
**Symptom**: Chart flashes during auto-refresh
**Solution**:
- Ensure `chartInstance.update('none')` is called (no animation)
- Verify gradient recalculation happens before `update()`

---

## Performance Optimization

**Gradient Calculation**:
- Complexity: O(n) where n = number of bars
- Max bars: 90 (daily aggregation threshold)
- Typical execution: < 1ms
- **No optimization needed** (fast enough for 5-second refresh)

**Chart.js Rendering**:
- Bar charts may render faster than line charts (no curve calculations)
- Responsiveness: maintained by `maintainAspectRatio: false`
- Memory: negligible increase (~1.35 KB for color array)

---

## Rollback Instructions

If bar chart needs to be reverted to line chart:

1. **Revert `graph.js`**:
   ```bash
   git checkout main -- src/dashboard/static/graph.js
   ```

2. **Or manually change**:
   - `type: 'bar'` → `type: 'line'`
   - Remove `calculateGradientColors()` function
   - Restore line chart dataset properties

3. **Test**:
   ```bash
   # Verify line chart works
   open http://localhost:5000
   ```

**Time**: < 5 minutes
**Risk**: None (no database changes)

---

## Next Steps After Implementation

1. **Code Review**: Verify TDD workflow followed, tests pass
2. **Documentation**: Update README if bar chart changes user-facing behavior
3. **Deployment**: No special deployment steps (static file change)
4. **Monitoring**: Check browser console for errors post-deploy

---

## References

- **Research**: [research.md](./research.md) - Technical decisions and alternatives
- **Data Model**: [data-model.md](./data-model.md) - Data structures and flow
- **API Contract**: [contracts/COMPAT.md](./contracts/COMPAT.md) - API compatibility
- **Chart.js Docs**: https://www.chartjs.org/docs/4.4.1/charts/bar.html
- **Spec**: [spec.md](./spec.md) - Feature requirements and user stories

---

## Summary

**Effort**: ~2-4 hours (including testing)
**Files Changed**: 1 primary (`graph.js`), 0-1 optional (`style.css`)
**Tests**: 2 new files (unit + integration)
**Risk**: LOW (frontend-only, no breaking changes)
**Deployment**: Single static file update

**Core Change**: Chart type + gradient color calculation
**Complexity**: Minimal (reuses existing Chart.js infrastructure)
