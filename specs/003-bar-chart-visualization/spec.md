# Feature Specification: Bar Chart Visualization for Daily Login Trends

**Feature Branch**: `003-bar-chart-visualization`
**Created**: 2025-11-22
**Status**: Draft
**Input**: User description: "I think a bar chart per day might be more visible and clear than a line chart"

## Clarifications

### Session 2025-11-22

- Q: Should days with zero login events be shown as zero-height bars or completely omitted from the chart? → A: Show zero-height bars (or minimal height like 1px) for days with no logins, making the time continuum visible
- Q: What is the maximum number of bars the chart should render before requiring weekly aggregation or pagination to maintain performance? → A: 90 bars maximum (3 months daily, then weekly)
- Q: What color scheme should be used for the bars? → A: Gradient blue scale - Lighter blue for lower counts, darker blue for higher counts

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Daily Login Counts with Bar Chart (Priority: P1)

Users need to see their Microsoft login events visualized as a bar chart showing daily login counts, making it easier to compare volumes across different days and identify patterns at a glance.

**Why this priority**: This is the core change requested - replacing the line chart with a bar chart for improved visibility and clarity. Bar charts excel at showing discrete daily values, making day-to-day comparisons more intuitive than line charts, especially when login counts vary significantly between days.

**Independent Test**: Generate login events across multiple days with varying counts (e.g., 5 logins on Monday, 2 on Tuesday, 10 on Wednesday), visit the dashboard, and verify that a bar chart displays with distinct bars for each day showing the correct heights corresponding to login counts.

**Acceptance Scenarios**:

1. **Given** I have login events recorded across 7 days with different daily counts, **When** I visit the dashboard, **Then** I see a bar chart with one bar per day showing the login count for each day
2. **Given** I hover over a bar on the chart, **When** the cursor is over the bar, **Then** I see a tooltip showing the date and exact number of logins for that day
3. **Given** I have login events spanning multiple weeks, **When** I view the bar chart, **Then** each bar represents one day and bars are clearly separated for easy comparison
4. **Given** I have zero login events for certain days within a date range, **When** I view the bar chart, **Then** those days show bars at zero height (or minimal height) to maintain visual continuity of the time range

---

### User Story 2 - Maintain Time Period Filtering with Bar Chart (Priority: P2)

Users want to continue using the existing time period filters (Last 24H, 7 Days, 30 Days, All Time) with the bar chart, allowing them to focus on relevant timeframes while benefiting from the improved bar chart visualization.

**Why this priority**: The time period filtering functionality is already implemented and provides significant value. Maintaining this feature with the new bar chart ensures users don't lose existing functionality while gaining better visualization.

**Independent Test**: Record login events across 60 days, click the "Last 7 Days" filter button, and verify the bar chart updates to show only the past 7 days' worth of bars with accurate daily counts.

**Acceptance Scenarios**:

1. **Given** I have login events from the past 60 days, **When** I click the "Last 7 Days" filter, **Then** the bar chart updates to show 7 bars representing each of the past 7 days
2. **Given** I am viewing the "Last 30 Days" filter, **When** I switch to "All Time", **Then** the bar chart expands to show all recorded login events grouped by day
3. **Given** I select a time period filter, **When** auto-refresh triggers with new login events, **Then** the filter remains active and the bar chart updates with the new data
4. **Given** I select "Last 24H" filter, **When** viewing the chart, **Then** the bars represent hourly aggregation instead of daily to show more granular data

---

### User Story 3 - Responsive Bar Chart on Mobile Devices (Priority: P3)

Users accessing the dashboard from mobile devices need the bar chart to remain readable and interactive on smaller screens, with appropriate sizing and touch-friendly interactions.

**Why this priority**: Mobile responsiveness is important for accessibility but is less critical than the core visualization change. The existing responsive design can be adapted for bar charts.

**Independent Test**: Open the dashboard on a mobile device with a 375px screen width, verify that the bar chart displays properly with readable bars, and confirm that tapping on bars shows tooltips.

**Acceptance Scenarios**:

1. **Given** I access the dashboard on a mobile device, **When** I view the bar chart, **Then** the bars are appropriately sized and the chart fits within the viewport without horizontal scrolling
2. **Given** I am viewing the bar chart on mobile, **When** I tap on a bar, **Then** I see the tooltip with date and count information
3. **Given** I have many days of data visible on mobile, **When** viewing the chart, **Then** the X-axis labels are rotated or abbreviated to prevent overlap

---

### Edge Cases

- When viewing time periods exceeding 90 days, the system automatically switches to weekly aggregation to maintain performance, with each bar representing one week's total login count
- Days with extremely high login counts (outliers) are displayed with bars that scale appropriately without making other bars too small to see
- Bar colors scale along a gradient from lighter blue (minimum count in the visible range) to darker blue (maximum count in the visible range), automatically adjusting when the filter or data changes
- When switching from line chart to bar chart, the transition happens smoothly without UI flicker or layout shifts
- Days with zero login events are shown as zero-height bars (or minimal visible height) to maintain visual continuity and prevent confusion about missing data
- When multiple logins occur on the same day, they are automatically summed and displayed as a single bar for that day

## Requirements *(mandatory)*

### Functional Requirements

**Bar Chart Visualization**:
- **FR-001**: System MUST display an interactive bar chart on the dashboard showing login events with dates on X-axis and login counts on Y-axis, replacing the current line chart
- **FR-002**: System MUST group login events by day and display one bar per day representing the total login count for that day
- **FR-003**: System MUST show tooltips when users hover over (or tap on mobile) bars, displaying the date and login count for that day
- **FR-004**: Bars MUST be visually distinct from each other with appropriate spacing to allow easy comparison between days
- **FR-005**: System MUST use a gradient blue color scheme where bar colors scale from lighter blue (lower login counts) to darker blue (higher login counts) to visually indicate relative activity levels
- **FR-016**: System MUST display zero-height bars (or minimal visible height) for days with zero login events to maintain visual continuity of the time range

**Time Aggregation**:
- **FR-006**: System MUST use daily aggregation as the primary view, showing one bar per day
- **FR-007**: When "Last 24H" filter is active, system MUST switch to hourly aggregation showing one bar per hour
- **FR-008**: When viewing time periods exceeding 90 days, system MUST switch to weekly aggregation showing one bar per week to maintain performance and readability

**Integration with Existing Features**:
- **FR-009**: System MUST maintain compatibility with existing time period filters (24H, 7D, 30D, All Time)
- **FR-010**: System MUST continue auto-refreshing the bar chart every 5 seconds with new login data
- **FR-011**: System MUST update the bar chart smoothly during auto-refresh without destroying and recreating the entire chart (silent updates)
- **FR-012**: System MUST maintain the existing empty state behavior when no login data exists

**Responsiveness**:
- **FR-013**: Bar chart MUST remain functional and readable on mobile devices with screen widths down to 320px
- **FR-014**: On mobile devices, bars MUST be touch-friendly with adequate size for tapping (minimum 44px touch target height)
- **FR-015**: X-axis labels MUST adjust (rotate, abbreviate, or skip labels) on small screens to prevent overlap

### Key Entities

- **Daily Login Aggregate**: Represents the total count of login events for a specific calendar day, used as the value for each bar in the chart
- **Time Period Filter**: Represents the user's selected time range (24h, 7d, 30d, all) for filtering bar chart data, affects aggregation level (hourly vs daily vs weekly)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can view a bar chart representation of daily login trends within 1 second of loading the dashboard (when data exists)
- **SC-002**: Each day with login events is represented by a visually distinct bar that users can immediately identify and compare with other days
- **SC-003**: Users can hover over or tap on any bar to see detailed information (date and count) via tooltip
- **SC-004**: Bar chart updates within 1 second when switching between time period filters
- **SC-005**: Bar chart remains readable and interactive on mobile devices with screen widths down to 320px
- **SC-006**: Day-to-day comparison is 40% faster/easier for users compared to the previous line chart (measured by user testing or task completion time)
- **SC-007**: Auto-refresh continues to work smoothly with bar chart updates occurring every 5 seconds without visual disruption
- **SC-008**: Bar chart renders and remains interactive with up to 90 daily bars without performance degradation, automatically switching to weekly aggregation for longer periods
- **SC-009**: Users can visually distinguish between high-activity and low-activity days at a glance through the gradient color scaling from light to dark blue

### Assumptions

- The existing aggregation logic in the backend (`get_aggregated_graph_data`) can be reused with minimal changes
- Chart.js library (already integrated) supports bar chart rendering with similar configuration to line charts
- The existing responsive design patterns will work for bar charts with minor CSS adjustments
- Users prefer discrete day-by-day visualization over trend lines for this use case
- The existing time period filters provide sufficient granularity; no new filter periods are needed

### Out of Scope

- Stacked bar charts showing multiple data dimensions (only single dimension: login count per day)
- Horizontal bar charts (vertical bars only)
- Animated transitions between bars when data updates (static height changes are acceptable)
- Customizable bar colors or chart themes
- Side-by-side comparison views (e.g., bar chart and line chart toggle)
- Export functionality for bar chart data
- Historical comparison overlays (e.g., comparing this week's bars to last week's)
