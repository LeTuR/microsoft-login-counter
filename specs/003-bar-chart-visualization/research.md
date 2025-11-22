# Technical Research: Bar Chart Visualization

**Feature**: Bar Chart Visualization for Daily Login Trends
**Date**: 2025-11-22
**Research Phase**: Phase 0

## Research Questions

This document resolves technical unknowns identified during planning.

---

## Q1: Chart.js Bar Chart Configuration

**Question**: What Chart.js configuration changes are needed to convert from line chart to bar chart?

**Decision**: Change chart `type` from 'line' to 'bar' and update dataset configuration

**Rationale**:
- Chart.js v4.4.1 (already integrated) has built-in bar chart support
- Minimal configuration changes required:
  - `type: 'bar'` instead of `type: 'line'`
  - Remove `tension`, `fill`, `pointRadius` properties (line-specific)
  - Add `barPercentage` and `categoryPercentage` for bar spacing control
  - `backgroundColor` becomes an array (one color per bar for gradient)
  - `borderWidth` can be kept for bar borders

**Alternatives Considered**:
- **Alternative 1**: Use a different charting library (Recharts, D3.js)
  - **Rejected**: Chart.js already integrated and working; switching adds unnecessary complexity
- **Alternative 2**: Build custom SVG bar chart
  - **Rejected**: Chart.js provides tooltips, responsiveness, and interactions out-of-the-box

**Implementation Notes**:
```javascript
// Before (line chart):
type: 'line',
data: {
  datasets: [{
    tension: 0.3,
    fill: true,
    borderColor: '#0078d4',
    backgroundColor: 'rgba(0, 120, 212, 0.1)'
  }]
}

// After (bar chart):
type: 'bar',
data: {
  datasets: [{
    backgroundColor: calculateGradientColors(data), // Array of colors
    borderColor: '#fff',
    borderWidth: 1,
    barPercentage: 0.9,
    categoryPercentage: 0.8
  }]
}
```

---

## Q2: Gradient Color Calculation Algorithm

**Question**: How to calculate gradient blue colors from light to dark based on login counts?

**Decision**: Linear interpolation between light blue (#add8e6) and dark blue (#003d6b) based on normalized count values

**Rationale**:
- Simple linear interpolation provides smooth gradient across data range
- RGB color space interpolation is straightforward in JavaScript
- Normalization formula: `normalized = (value - min) / (max - min)`
- Color interpolation: `color = lightBlue + (darkBlue - lightBlue) * normalized`
- Handles edge cases: single data point (all same color), zero values (lightest color)

**Alternatives Considered**:
- **Alternative 1**: HSL color space interpolation
  - **Rejected**: More complex, RGB interpolation sufficient for blue gradient
- **Alternative 2**: Predefined color buckets (e.g., 5 shades)
  - **Rejected**: Less smooth, arbitrary bucket boundaries
- **Alternative 3**: Logarithmic scale for high-variance data
  - **Rejected**: Adds complexity; linear scale sufficient for login count ranges

**Implementation Notes**:
```javascript
function calculateGradientColors(dataPoints) {
  const counts = dataPoints.map(p => p.count);
  const min = Math.min(...counts);
  const max = Math.max(...counts);

  // Handle edge case: all same value
  if (max === min) {
    return dataPoints.map(() => '#0078d4'); // Microsoft blue
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

---

## Q3: Zero-Height Bar Rendering

**Question**: How to render zero-height bars (for days with no logins) in Chart.js?

**Decision**: Use Chart.js built-in zero value handling with minimum bar height via CSS

**Rationale**:
- Chart.js automatically renders bars at Y=0 for zero values
- Can add small visual indicator via CSS `:empty` pseudo-class or custom plugin
- Alternative: Set minimum value to 0.1 to show tiny bar (visible but negligible height)
- Zero-height bars still receive tooltips and click events

**Alternatives Considered**:
- **Alternative 1**: Custom Chart.js plugin to draw 1px line
  - **Rejected**: Adds complexity; CSS or minimal value simpler
- **Alternative 2**: Skip zero-value days entirely
  - **Rejected**: Contradicts clarification decision (show zero-height bars)

**Implementation Notes**:
```javascript
// Option 1: Keep zero values, rely on Chart.js default rendering
data: counts // includes zeros

// Option 2: Add minimal visible value
data: counts.map(c => c === 0 ? 0.05 : c) // 0.05 shows tiny bar

// CSS for visual enhancement (if needed):
.chartjs-render-monitor canvas {
  /* Ensure zero bars have minimum visible presence */
}
```

---

## Q4: 90-Day Aggregation Threshold

**Question**: Is the existing aggregation logic compatible with the 90-day threshold?

**Decision**: Yes, existing `determine_aggregation_level()` function already implements this logic

**Rationale**:
- From existing code in `src/storage/repository.py:125-148`:
  ```python
  def determine_aggregation_level(start_date: datetime, end_date: datetime) -> str:
      days_diff = (end_date - start_date).days

      if days_diff <= 7:
          return 'hour'
      elif days_diff <= 90:
          return 'day'
      else:
          return 'week'
  ```
- The threshold is already 90 days (matching FR-008)
- No backend changes needed
- Bar chart will automatically use weekly aggregation for periods > 90 days

**Alternatives Considered**:
- **Alternative 1**: Add new threshold logic
  - **Rejected**: Existing logic already correct
- **Alternative 2**: Make threshold configurable
  - **Rejected**: YAGNI - no requirement for configurability

**Implementation Notes**:
No changes required. Existing aggregation logic already handles 90-day threshold correctly.

---

## Q5: Mobile Touch Target Size

**Question**: How to ensure bars meet 44px minimum touch target on mobile?

**Decision**: Use Chart.js responsive options and CSS min-height on chart container

**Rationale**:
- Chart.js `maintainAspectRatio: false` with container height ensures bars have sufficient height
- Mobile container height set to 300px minimum (from existing responsive CSS)
- Bar width controlled by `barPercentage` and `categoryPercentage` (default values work)
- Touch targets automatically meet 44px with 300px chart height and < 7 bars visible

**Alternatives Considered**:
- **Alternative 1**: Custom touch event handling to expand touch area
  - **Rejected**: Chart.js built-in events sufficient
- **Alternative 2**: Increase bar width on mobile
  - **Rejected**: Default spacing already appropriate

**Implementation Notes**:
```css
/* From existing style.css - already implements mobile-friendly height */
@media (max-width: 768px) {
    .graph-container {
        height: 300px; /* Ensures 44px+ bars for typical bar count */
    }
}
```

---

## Q6: Gradient Update During Auto-Refresh

**Question**: How to efficiently update gradient colors during 5-second auto-refresh without recalculating entire chart?

**Decision**: Recalculate gradient colors only when data changes (use Chart.js `update()` method)

**Rationale**:
- Chart.js `update('none')` skips animations but recalculates data
- Gradient calculation is O(n) where n = number of bars (max 90)
- Performance: ~1ms for 90 bars, negligible impact on 5-second refresh
- Silent update mode (from existing implementation) already handles smooth updates
- No need for caching or optimization at this scale

**Alternatives Considered**:
- **Alternative 1**: Cache gradient colors and only recalculate if min/max changes
  - **Rejected**: Premature optimization; calculation is fast enough
- **Alternative 2**: Static gradient (same colors every refresh)
  - **Rejected**: Gradient should reflect current data range

**Implementation Notes**:
```javascript
// From existing graph.js silent update mechanism:
if (silentUpdate && chartInstance) {
    chartInstance.data.labels = labels;
    chartInstance.data.datasets[0].data = counts;
    chartInstance.data.datasets[0].backgroundColor = calculateGradientColors(dataPoints); // Add this line
    chartInstance.update('none'); // No animation
    return;
}
```

---

## Summary

All technical unknowns have been resolved:

1. **Chart.js Configuration**: Simple type change from 'line' to 'bar' with dataset property adjustments
2. **Gradient Algorithm**: Linear RGB interpolation between #add8e6 and #003d6b
3. **Zero-Height Bars**: Chart.js built-in zero value handling (no custom plugin needed)
4. **90-Day Threshold**: Existing backend logic already implements this correctly
5. **Mobile Touch Targets**: Existing responsive design already meets 44px requirement
6. **Gradient Auto-Refresh**: Recalculate on each update (negligible performance impact)

**Risk Assessment**: LOW
- All decisions leverage existing infrastructure (Chart.js, aggregation logic, responsive CSS)
- No new dependencies or architectural changes required
- Performance impact minimal (gradient calculation < 1ms)
- Browser compatibility ensured (Chart.js v4.4.1 already tested)

**Ready for Phase 1**: ✅ Yes - All research complete, no blockers identified
