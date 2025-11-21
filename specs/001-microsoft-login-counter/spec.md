# Feature Specification: Microsoft Login Event Counter

**Feature Branch**: `001-microsoft-login-counter`
**Created**: 2025-11-21
**Status**: Draft
**Input**: User description: "I want to count the amount of time I have to sign in into microsoft but it should not be a browser extension since company policy does not allows install custom externsion. It should be a proxy or an equivalent solution."

## Clarifications

### Session 2025-11-21

- Q: Should logins within a short time window (e.g., 30 seconds) be deduplicated? → A: Count every authentication separately (no deduplication)

### Session 2025-11-21 (Update)

- **Constraint Added**: Solution MUST NOT be a browser extension due to company policy restrictions. Solution must be a proxy-based or equivalent approach that does not require browser extension installation.
- Q: How should users access the login statistics and history dashboard? → A: Web dashboard served by proxy - Users access via http://localhost:port or proxy-assigned URL in any browser
- Q: What network traffic pattern should the proxy use to detect a successful Microsoft login? → A: Detect HTTP 302 redirect responses from login.microsoftonline.com to the callback URL with success parameters
- Q: How should login event data be persisted locally? → A: SQLite database file - Embedded SQL database with transactions and indexing
- Q: Should the proxy perform deep TLS/HTTPS inspection, or use a lighter approach? → A: HTTP metadata only - Monitor redirect patterns without decrypting HTTPS payloads (observe status codes and headers)
- Q: What level of logging and observability should the proxy provide? → A: Basic operational logs - Log authentication detections, database operations, errors, and proxy lifecycle events

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Detect and Count Login Events via Proxy (Priority: P1)

As a user who frequently authenticates with Microsoft services, I want the system to automatically detect each time I log in through the Microsoft authentication portal via a proxy or network-level solution and increment a counter, so I can see how often I need to re-authenticate without installing a browser extension.

**Why this priority**: This is the core MVP functionality. Detecting and counting login events through network traffic is the fundamental requirement without which the feature provides no value. Must work without browser extensions due to company policy.

**Independent Test**: Can be fully tested by configuring the proxy, logging in to Microsoft services multiple times, and verifying that each authentication event increments the login counter without requiring any browser extension.

**Acceptance Scenarios**:

1. **Given** the proxy is running and configured, **When** I successfully authenticate via login.microsoftonline.com, **Then** the system detects the login event through network traffic and increments the login counter by 1
2. **Given** I have logged in 5 times today through the proxy, **When** I view the counter, **Then** I see a count of 5 logins
3. **Given** I log in multiple times in rapid succession, **When** each authentication completes, **Then** each login is counted separately
4. **Given** the system is tracking my logins through the proxy, **When** I authenticate via login.microsoftonline.com, **Then** the timestamp of that login event is recorded

---

### User Story 2 - View Login Frequency Statistics (Priority: P2)

As a user, I want to view statistics showing how many times I've logged in over different time periods (daily, weekly, monthly), so I can understand my authentication frequency patterns.

**Why this priority**: After capturing login counts (P1), users need to see aggregated statistics to make the data meaningful and actionable.

**Independent Test**: Can be tested by performing multiple logins across different days and then viewing statistics that correctly aggregate counts by day, week, and month.

**Acceptance Scenarios**:

1. **Given** I have logged in multiple times over several days, **When** I navigate to the proxy's web dashboard in my browser, **Then** I see my login count for today, this week, and this month
2. **Given** I logged in 3 times today and 10 times this week, **When** I view the web dashboard, **Then** I see "Today: 3 logins" and "This week: 10 logins"
3. **Given** I am viewing the web dashboard, **When** I look at monthly data, **Then** I see the total number of logins for the current month
4. **Given** I have no logins recorded yet, **When** I open the web dashboard, **Then** I see zero counts for all time periods with a clear message indicating no data

---

### User Story 3 - View Login Event History (Priority: P3)

As a user, I want to view a list of all my past login events with their timestamps, so I can see exactly when I authenticated and identify patterns or anomalies.

**Why this priority**: Nice to have for detailed analysis and troubleshooting. Core value is delivered by counting (P1) and statistics (P2).

**Independent Test**: Can be tested by performing several logins and then viewing a chronological list showing the timestamp of each login event.

**Acceptance Scenarios**:

1. **Given** I have logged in multiple times, **When** I navigate to the login history page on the web dashboard, **Then** I see a chronological list of login events with their timestamps
2. **Given** I am viewing the login history page on the web dashboard, **When** I look at each entry, **Then** I see the date and time when each login occurred
3. **Given** I have many login events, **When** I scroll through the history on the web dashboard, **Then** I can view all past logins without performance issues
4. **Given** I have no login events yet, **When** I open the history page on the web dashboard, **Then** I see a message indicating no login events have been recorded

---

### Edge Cases

- **Rapid successive logins**: Each authentication is counted separately without deduplication. If a user logs in via 3 tabs simultaneously, all 3 count as distinct events (see FR-012)
- **Failed authentication attempts**: Only successful authentications are counted. Failed login attempts are not tracked (see Assumption 6)
- **Page refresh during authentication**: If the authentication page is refreshed mid-flow without completing authentication, it does not increment the counter. Only completed authentications count.
- **System clock changes**: Timestamps are stored in UTC and converted to user's local timezone for display. Clock changes do not affect historical timestamps.
- **Data persistence**: The SQLite database file persists all data across proxy restarts. Deleting the database file or filesystem corruption will result in loss of historical login event data. Users should back up the database file if needed.
- **Network interruption during authentication**: If network connection is lost during authentication, the event is only counted if authentication successfully completes. Partial authentications are not counted.
- **Proxy bypass**: If the user bypasses the proxy or uses a different network path, login events will not be detected. The system assumes all Microsoft authentication traffic flows through the configured proxy.
- **HTTPS/TLS traffic**: The proxy monitors HTTP metadata (status codes, redirect headers) without decrypting HTTPS payloads. No custom certificate trust is required, preserving end-to-end encryption.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST automatically detect when a user successfully completes authentication via login.microsoftonline.com by monitoring HTTP 302 redirect responses to callback URLs with success parameters
- **FR-002**: System MUST operate as a proxy or equivalent network-level solution that does not require browser extension installation
- **FR-003**: System MUST increment a counter by 1 for each detected login event
- **FR-004**: System MUST record the timestamp (date and time) for each login event
- **FR-005**: System MUST persist all login event data in a local SQLite database file with transaction support to ensure data survives proxy restarts or system reboots
- **FR-006**: System MUST display the total number of login events for the current day
- **FR-007**: System MUST display the total number of login events for the current week
- **FR-008**: System MUST display the total number of login events for the current month
- **FR-009**: System MUST provide a chronological history view showing all past login events with timestamps
- **FR-014**: System MUST provide a web-based dashboard interface accessible via HTTP (e.g., http://localhost:port) served by the proxy itself
- **FR-015**: Dashboard MUST be accessible from any browser without requiring additional software installation
- **FR-010**: System MUST NOT track session duration or how long users remain logged in
- **FR-011**: System MUST NOT track user activity after authentication completes
- **FR-012**: System MUST count every authentication event separately without deduplication, even if multiple logins occur within seconds of each other
- **FR-013**: System MUST NOT require installation of browser extensions or browser modifications that violate company policy
- **FR-016**: System MUST detect authentication events by monitoring HTTP metadata (status codes, headers) WITHOUT decrypting HTTPS payloads
- **FR-017**: System MUST NOT perform man-in-the-middle TLS decryption or require users to trust custom CA certificates
- **FR-018**: System MUST maintain operational logs recording proxy lifecycle events (startup, shutdown), authentication detections, database operations, and errors
- **FR-019**: Logs MUST be stored locally and accessible for troubleshooting (e.g., "why wasn't my login counted?")

### Key Entities

- **Login Event**: Represents a single successful authentication via login.microsoftonline.com. Key attributes include event timestamp and event ID.
- **Login Statistics**: Aggregated counts of login events grouped by time period (daily, weekly, monthly). Includes period start date, period end date, and login count.
- **Operational Log Entry**: Records proxy operations including lifecycle events (startup/shutdown), authentication detection events, database operations (writes/queries), and error conditions. Includes timestamp, log level (INFO/ERROR), and message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Login events are detected and counted within 2 seconds of authentication completion through proxy traffic inspection
- **SC-002**: Login count accuracy is 100% - every successful authentication increments the counter exactly once
- **SC-003**: Statistics correctly aggregate login counts by day, week, and month with 100% accuracy
- **SC-004**: Users can view login history spanning at least 90 days without performance degradation
- **SC-005**: Login event data persists across proxy restarts with 100% data integrity (no lost events)
- **SC-006**: Users can immediately understand their login frequency within 10 seconds of viewing statistics
- **SC-007**: The proxy adds less than 100ms latency to authentication requests - login process completes with negligible performance impact
- **SC-008**: System operates without requiring browser extension installation, meeting company policy requirements

## Assumptions

1. **Scope**: The system only tracks authentication events at login.microsoftonline.com. It does NOT track:
   - Session duration (how long the user stays logged in)
   - Logout events
   - User activity after authentication
   - Which specific Microsoft services are accessed

2. **Authentication Detection**: A "login event" occurs when the user successfully completes authentication at login.microsoftonline.com. The system detects this by monitoring HTTP 302 redirect responses from login.microsoftonline.com to application callback URLs, which include success parameters indicating completed authentication (following standard OAuth/OIDC patterns).

3. **Counting Granularity**: Each distinct authentication flow completion counts as one login event. If a user opens multiple tabs or windows requiring authentication, each authentication counts separately.

4. **Time Periods**:
   - "Today" = current calendar day (midnight to midnight in user's local timezone)
   - "This week" = current calendar week (Monday to Sunday)
   - "This month" = current calendar month (1st to last day)

5. **Data Storage**: All login event data is stored locally on the device running the proxy in a SQLite database file. No data is transmitted to external servers. The database uses transactions to ensure data integrity and supports efficient querying for time-based statistics. Data persists indefinitely unless the user manually deletes the database file.

6. **Failed Attempts**: Only successful authentications are counted. Failed login attempts (incorrect password, canceled authentication, etc.) are not tracked.

7. **Implementation Approach**: The solution MUST be implemented as a proxy or equivalent network-level solution. Browser extensions are explicitly excluded due to company policy restrictions. The solution operates at the network layer to intercept and analyze traffic to login.microsoftonline.com.

8. **Privacy**: The system only records that a login event occurred and when. The proxy monitors HTTP metadata (status codes and redirect headers) without decrypting HTTPS payloads, preserving end-to-end encryption. No tracking of:
   - User credentials or passwords
   - Authentication tokens or session data
   - User activity or behavior
   - Personal information beyond the fact that authentication occurred
   - Encrypted HTTPS payload contents

9. **Network Configuration**: Users can configure their browser or system to route traffic through the proxy. The proxy must be running on the local machine or accessible network location.

10. **TLS/HTTPS Handling**: The proxy monitors HTTP-level metadata (status codes, headers) without decrypting HTTPS payloads. No man-in-the-middle TLS decryption is performed, eliminating the need for custom CA certificates and preserving end-to-end encryption security. Authentication detection relies on observable redirect patterns in the HTTP layer.

11. **Company Policy Compliance**: The solution does not require installation of browser extensions or modifications that would violate company security policies. The proxy approach is assumed to be acceptable under company policy. The non-invasive HTTP metadata monitoring approach avoids security concerns associated with TLS decryption.

12. **Observability**: The proxy maintains basic operational logs to support troubleshooting. Logs include proxy lifecycle events (startup/shutdown), successful authentication detections with timestamps, database write/read operations, and any errors encountered. Logs are stored locally (e.g., text file or rotating log files) and do not transmit data externally. Log verbosity is balanced for single-user operational needs without excessive detail.
