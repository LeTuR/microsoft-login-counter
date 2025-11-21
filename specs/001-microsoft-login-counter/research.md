# Research: Microsoft Login Event Counter

**Feature**: 001-microsoft-login-counter
**Date**: 2025-11-21
**Purpose**: Resolve technical uncertainties and establish implementation decisions

## Research Questions

### 1. Implementation Approach: Browser Extension vs Alternatives

**Question**: Should we build a browser extension, proxy, or standalone application?

**Decision**: Browser Extension (Edge/Chrome compatible)

**Rationale**:
- **Browser Extension Advantages**:
  - Native access to browser APIs for URL monitoring (webNavigation, webRequest)
  - Built-in persistent storage (chrome.storage.local, IndexedDB)
  - No network proxy configuration required (user-friendly)
  - Automatic updates via browser extension store
  - Cross-platform (Windows, macOS, Linux) through browser
  - Secure sandbox environment

- **Proxy Disadvantages**:
  - Requires system-level configuration
  - May interfere with corporate proxies/VPNs
  - SSL/TLS interception complexity
  - More security/privacy concerns

- **Standalone App Disadvantages**:
  - Cannot reliably detect browser-based authentication
  - Would require browser automation (brittle)
  - More complex deployment and updates

**Alternatives Considered**:
- Network proxy: Rejected due to configuration complexity and SSL interception issues
- Standalone desktop app: Rejected due to inability to monitor browser activity reliably
- Web service with browser agent: Rejected due to privacy concerns (external data transmission)

**Impact**: Determines entire architecture, deployment model, and development stack

---

### 2. Language/Version: JavaScript vs TypeScript

**Question**: Use vanilla JavaScript or TypeScript for browser extension development?

**Decision**: TypeScript 5.x with strict mode

**Rationale**:
- **Type safety** prevents runtime errors in date/time calculations (critical for statistics accuracy)
- Better **IDE support** for browser extension APIs
- **Maintainability** for time-based logic and data transformations
- Minimal overhead (compiles to JS, no runtime cost)
- Industry standard for modern browser extensions

**Alternatives Considered**:
- Vanilla JavaScript: Rejected due to lack of type safety for critical time calculations
- Flow: Rejected due to declining adoption and tooling support

**Impact**: Development workflow, build process, testing strategy

---

### 3. Primary Dependencies: Web Extensions API

**Question**: Which browser APIs and libraries are needed?

**Decision**:
- **Browser APIs** (native, no external dependencies):
  - `chrome.webNavigation` or `chrome.webRequest` for URL monitoring
  - `chrome.storage.local` for persistent data (up to 10MB quota)
  - `chrome.alarms` for periodic cleanup/maintenance

- **Build/Dev Tools**:
  - TypeScript compiler
  - Web Extension Polyfill (for cross-browser compatibility)
  - esbuild or webpack for bundling

- **Testing Dependencies**:
  - Jest + ts-jest for unit tests
  - @types/chrome for TypeScript definitions
  - webextension-polyfill-ts for cross-browser testing

**Rationale**:
- **Minimize external dependencies** (Pragmatic Simplicity principle)
- Use native browser APIs instead of heavy frameworks
- No UI framework needed (vanilla JS/HTML for simple popup)
- No date library needed (native Date API sufficient for time period calculations)

**Alternatives Considered**:
- React/Vue for popup UI: Rejected as over-engineering for simple statistics display
- date-fns/moment.js: Rejected as unnecessary (native Date API handles our needs)
- External analytics libraries: Rejected due to privacy concerns

**Impact**: Bundle size, performance, complexity, security surface

---

### 4. Storage: chrome.storage vs IndexedDB

**Question**: Which storage API for persistent login event data?

**Decision**: chrome.storage.local (primary) with IndexedDB fallback for large datasets

**Rationale**:
- **chrome.storage.local advantages**:
  - Automatically synced to disk
  - Survives browser restarts
  - Simple key-value API
  - 10MB quota (sufficient for ~50,000 events at 200 bytes each)
  - No permissions beyond "storage"

- **When to use IndexedDB**:
  - Only if user accumulates > 10MB of events (unlikely for years of use)
  - Provides unlimited storage with user permission
  - Better query performance for large datasets

**Implementation Strategy**:
- Start with chrome.storage.local
- Monitor storage usage
- Prompt for IndexedDB migration if approaching quota
- Keep data model identical for easy migration

**Alternatives Considered**:
- localStorage: Rejected (synchronous, blocks UI, limited quota)
- IndexedDB only: Rejected (more complex API, unnecessary for typical usage)
- chrome.storage.sync: Rejected (limited to 102KB, would sync sensitive login data across devices)

**Impact**: Data access patterns, quota management, migration strategy

---

### 5. Testing Framework: Jest vs Alternatives

**Question**: Which testing framework for browser extension tests?

**Decision**: Jest 29.x with chrome-mock for browser API mocking

**Rationale**:
- **Jest advantages**:
  - Built-in TypeScript support via ts-jest
  - Excellent mocking capabilities (critical for browser APIs)
  - Snapshot testing for data structures
  - Code coverage out of the box
  - Fast parallel test execution
  - Wide adoption and documentation

- **Browser API Mocking**:
  - Use jest.mock() for chrome.* APIs
  - Create test fixtures for webNavigation events
  - Mock storage APIs with in-memory implementations

**Testing Strategy**:
1. **Unit Tests** (Jest):
   - Date/time calculations
   - Statistics aggregation logic
   - Data transformations

2. **Integration Tests** (Jest + mocked chrome APIs):
   - Login detection → storage → statistics flow
   - Storage persistence across "restarts"

3. **Contract Tests** (Manual + automated):
   - Verify URL patterns match real login.microsoftonline.com
   - Storage API contracts
   - Test with actual browser (Playwright for E2E if needed)

**Alternatives Considered**:
- Mocha/Chai: Rejected (more setup, less integrated tooling)
- Jasmine: Rejected (declining adoption)
- Playwright only: Rejected (slow for unit tests, good for E2E supplement)

**Impact**: Test execution speed, CI/CD integration, developer experience

---

### 6. Login Detection: webNavigation vs webRequest

**Question**: Which API to detect successful authentication at login.microsoftonline.com?

**Decision**: chrome.webNavigation with URL pattern matching

**Rationale**:
- **webNavigation advantages**:
  - Fires on navigation completion (after authentication succeeds)
  - Provides full URL including redirects
  - Less performance overhead than webRequest
  - Easier permission justification to users

- **Detection Strategy**:
  1. Listen for `onCompleted` events
  2. Match URL pattern: `https://login.microsoftonline.com/*`
  3. Check for success indicators in URL (redirect codes, tokens)
  4. Deduplicate rapid events via 1-second cooldown (practical deduplication, not violating spec)

**URL Patterns to Detect**:
```
https://login.microsoftonline.com/*/oauth2/v2.0/authorize*
https://login.microsoftonline.com/common/oauth2/authorize*
```

Success indicators:
- Redirect to `code=` parameter (authorization code flow)
- Redirect away from login.microsoftonline.com
- HTTP 302/303 redirects

**Alternatives Considered**:
- webRequest: Rejected (more overhead, requires broader permissions)
- Content scripts: Rejected (may not work on login.microsoftonline.com due to CSP)
- Polling storage/cookies: Rejected (unreliable, high overhead)

**Impact**: Detection accuracy, false positive rate, performance, permissions

---

### 7. Time Period Calculations: Week Start Day

**Question**: Should week start on Sunday or Monday?

**Decision**: Monday (ISO 8601 standard)

**Rationale**:
- Matches spec assumption 4: "This week" = current calendar week (Monday to Sunday)
- ISO 8601 standard (international)
- Consistent with business/corporate calendars
- Microsoft 365 defaults to Monday start

**Implementation**:
```typescript
function getWeekStart(date: Date): Date {
  const day = date.getDay();
  const diff = (day === 0 ? -6 : 1) - day; // Monday = 1
  return new Date(date.setDate(date.getDate() + diff));
}
```

**Impact**: Statistics aggregation logic, user expectations

---

### 8. Performance Optimization: Event Throttling

**Question**: How to prevent duplicate counting from rapid URL changes?

**Decision**: 1-second event cooldown (practical deduplication)

**Rationale**:
- Authentication flows involve multiple redirects within milliseconds
- Single login generates 3-5 navigation events
- 1-second cooldown consolidates these into single count
- Does not violate spec (which says "no deduplication" for separate user actions)
- This is practical handling of browser implementation detail, not user-facing behavior

**Implementation**:
```typescript
let lastLoginTime = 0;
const COOLDOWN_MS = 1000;

function onNavigationCompleted(details) {
  const now = Date.now();
  if (now - lastLoginTime < COOLDOWN_MS) {
    return; // Ignore rapid redirect
  }

  if (isLoginSuccess(details.url)) {
    recordLoginEvent(now);
    lastLoginTime = now;
  }
}
```

**Alternatives Considered**:
- No throttling: Rejected (would count same login 3-5 times)
- Longer cooldown (5s): Rejected (might miss legitimate rapid logins)
- URL-based deduplication: Rejected (complex, fragile)

**Impact**: Count accuracy, user experience, spec compliance

---

## Summary of Decisions

| Area | Decision | Key Reason |
|------|----------|------------|
| **Implementation** | TypeScript browser extension | Native browser APIs, user-friendly, secure |
| **Language** | TypeScript 5.x strict | Type safety for time calculations |
| **Storage** | chrome.storage.local | Simple, sufficient quota, automatic persistence |
| **Testing** | Jest + chrome-mock | Best TypeScript support, excellent mocking |
| **Detection** | webNavigation API | Completion events, less overhead, clear permissions |
| **Week Start** | Monday (ISO 8601) | Matches spec, international standard |
| **Throttling** | 1-second cooldown | Prevents redirect-induced duplicates |

## Technical Stack Summary

**Resolved Technical Context**:
- **Language/Version**: TypeScript 5.x (strict mode)
- **Primary Dependencies**: chrome.webNavigation, chrome.storage, webextension-polyfill
- **Storage**: chrome.storage.local (10MB quota, IndexedDB fallback if needed)
- **Testing**: Jest 29.x + ts-jest + chrome API mocks
- **Target Platform**: Edge/Chrome browser (Manifest V3)
- **Build Tools**: TypeScript compiler, esbuild for bundling

All NEEDS CLARIFICATION items from Technical Context have been resolved.
