# Feature Specification: Auto-Refresh Statistics Grid

**Feature Branch**: `004-statistics-refresh`
**Created**: 2025-11-22
**Status**: Clarified
**Input**: User description: "Graph ui is refreshing properly but not the statistics numbers in the grid"

## User Scenarios & Testing

### User Story 1 - View Real-Time Statistics Without Manual Refresh (Priority: P1)

As a user viewing the dashboard, I want to see the statistics grid (Today, This Week, This Month, All Time counts) update automatically without needing to reload the page, so that I can monitor login activity in real-time alongside the already auto-refreshing graph.

**Why this priority**: This is the core issue - users currently have to manually refresh the page to see updated statistics, while the graph updates automatically every 5 seconds. This creates a confusing user experience where half the dashboard is live and half is stale.

**Independent Test**: Open the dashboard, wait for new login events to be recorded (either naturally or by triggering test logins), and verify that the statistics cards (Today, Week, Month, Total counts) update automatically within 5 seconds to reflect the new data, matching the auto-refresh behavior of the graph.

**Acceptance Scenarios**:

1. **Given** the dashboard is open and displaying current statistics, **When** a new login event occurs and 5 seconds pass, **Then** the "Today" count increments automatically without page reload
2. **Given** the dashboard shows statistics from yesterday, **When** the clock rolls over to a new day at midnight and the next refresh cycle occurs, **Then** the "Today" count resets to the current day's count
3. **Given** multiple statistics cards are displayed, **When** the auto-refresh cycle runs, **Then** all cards update simultaneously with consistent data (no partial updates)
4. **Given** the user is viewing the dashboard for an extended period, **When** multiple 5-second refresh cycles occur, **Then** all statistics continue updating correctly without memory leaks or performance degradation

---

### Edge Cases

- What happens when the statistics API request fails during auto-refresh? (Statistics should remain at last known values, with indefinite retry on every 5-second cycle)
- What happens if the user's system clock is incorrect or changes during viewing? (Use server-provided timestamps for accuracy)
- What happens during very high-volume periods when counts change rapidly between refresh cycles? (Show the latest server-side counts at each 5-second interval)
- What happens if the dashboard loses focus (user switches tabs)? (Continue refreshing in background regardless of tab focus status)

## Requirements

### Functional Requirements

- **FR-001**: System MUST auto-refresh all statistics cards (Today, This Week, This Month, All Time) at the same 5-second interval as the graph UI
- **FR-002**: System MUST update all statistics simultaneously in a single atomic operation to prevent displaying inconsistent data
- **FR-003**: System MUST handle API errors gracefully by retaining last known statistics values and retrying indefinitely on every 5-second cycle without backoff or retry limits
- **FR-004**: System MUST recalculate time-based statistics (Today, This Week, This Month) using current server time to handle day/week/month boundaries correctly
- **FR-005**: Auto-refresh MUST not cause visual flickering or jarring UI updates that distract users from monitoring the dashboard
- **FR-006**: System MUST maintain refresh synchronization between graph and statistics (both update from the same refresh trigger)

### Key Entities

- **Statistics Snapshot**: Represents the current login counts at a point in time, including today_count, week_count, month_count, total_count, and timestamp metadata

## Success Criteria

### Measurable Outcomes

- **SC-001**: Statistics grid updates within 5 seconds of new login events being recorded, matching the graph refresh interval
- **SC-002**: Users can monitor dashboard continuously for 30+ minutes without needing manual page refresh to see current data
- **SC-003**: Statistics updates complete in under 200ms to maintain responsive UI feel
- **SC-004**: Zero visual flickering or layout shifts occur during statistics updates
- **SC-005**: Statistics remain accurate across day/week/month boundaries without manual intervention

## Assumptions

- The existing auto-refresh mechanism for the graph (5-second interval) will be reused for statistics refresh
- The statistics API endpoint (`/`) or a new dedicated endpoint provides fresh statistics data on each request
- The auto-refresh will continue in background regardless of whether the dashboard tab has focus
- Statistics updates should be atomic - all counts update together or none update (no partial refresh state)

## Dependencies

- Existing auto-refresh infrastructure from the graph visualization feature (003-bar-chart-visualization)
- Existing statistics calculation logic in the backend (compute_statistics function)
- Dashboard already displays statistics grid with Today/Week/Month/Total counts

## Out of Scope

- Changing the 5-second refresh interval (this is established by the graph feature)
- Adding user controls to pause/resume auto-refresh
- Implementing WebSocket or Server-Sent Events for real-time push updates
- Adding animation or transition effects to count changes
- Displaying "last updated" timestamp to users
- Implementing differential updates (only updating counts that changed)

## Clarifications

### Session 2025-11-22

**Q1: Tab Focus Behavior** - Should auto-refresh pause when the dashboard tab loses focus?
**Decision**: Continue refreshing in background regardless of tab focus status
**Rationale**: Provides best user experience as users can switch away and return to see fresh data immediately. The 5-second interval is already conservative for resource usage, and modern browsers handle background tabs efficiently.

**Q2: Error Recovery Retry Strategy** - Should the system implement a maximum retry limit or backoff strategy when statistics API calls fail repeatedly?
**Decision**: Retry indefinitely on every 5-second cycle (no backoff)
**Rationale**: Since the refresh interval is already conservative (5 seconds), and the statistics endpoint is a local backend service (not an external API), temporary failures should be rare and brief. Indefinite retries ensure the dashboard recovers immediately when the backend becomes available again without delaying recovery through backoff or retry limits.
