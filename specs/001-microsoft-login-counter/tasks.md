---

description: "Task list for Microsoft Login Event Counter implementation"
---

# Tasks: Microsoft Login Event Counter

**Input**: Design documents from `/specs/001-microsoft-login-counter/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md

**Tests**: Following constitution principle I (Test-First Development), tests are included and MUST be written first before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Browser Extension**: `extension/` at repository root
- **Tests**: `tests/` at repository root
- Paths shown below assume browser extension structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize Node.js project with package.json (TypeScript 5.x, Jest 29.x, esbuild)
- [ ] T002 [P] Create TypeScript configuration in tsconfig.json with strict mode enabled
- [ ] T003 [P] Create Jest configuration in jest.config.js with ts-jest and chrome mocks
- [ ] T004 [P] Install dependencies: typescript, @types/chrome, jest, ts-jest, esbuild, webextension-polyfill
- [ ] T005 Create extension directory structure per plan.md (extension/, extension/background/, extension/popup/, extension/storage/, extension/lib/)
- [ ] T006 Create tests directory structure (tests/contract/, tests/integration/, tests/unit/)
- [ ] T007 [P] Create manifest.json in extension/ with Manifest V3, permissions (storage, webNavigation), and host_permissions for login.microsoftonline.com
- [ ] T008 [P] Create .gitignore to exclude node_modules/, dist/, and build artifacts
- [ ] T009 [P] Create build scripts in package.json (build, build:watch, test, test:watch)
- [ ] T010 [P] Set up esbuild configuration for bundling TypeScript to extension dist/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 Create LoginEvent type definition in extension/lib/types.ts per data-model.md (id, timestamp, url, detected_at fields)
- [ ] T012 [P] Create StorageMetadata type definition in extension/lib/types.ts per data-model.md
- [ ] T013 [P] Create LoginStatistics type definition in extension/lib/types.ts per data-model.md
- [ ] T014 Implement StorageManager class in extension/storage/storage-manager.ts with chrome.storage.local wrapper methods (get, set, clear, getBytesInUse)
- [ ] T015 [P] Implement date utility functions in extension/lib/date-utils.ts (startOfDay, endOfDay, startOfWeek, endOfWeek, startOfMonth, endOfMonth with Monday week start)
- [ ] T016 [P] Create chrome API mocks in tests/setup/chrome-mocks.ts for storage.local and webNavigation APIs
- [ ] T017 Configure Jest to load chrome API mocks globally in jest.config.js setupFiles

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Detect and Count Login Events (Priority: P1) 🎯 MVP

**Goal**: Automatically detect Microsoft authentication events at login.microsoftonline.com and increment a counter

**Independent Test**: Log in to Microsoft services multiple times and verify each authentication increments the counter

### Tests for User Story 1 ⚠️ WRITE TESTS FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Contract test for webNavigation.onCompleted listener in tests/contract/url-detection.test.ts (verify event structure, URL filtering for login.microsoftonline.com)
- [ ] T019 [P] [US1] Contract test for storage.local API in tests/contract/storage-api.test.ts (verify get/set/clear methods, quota handling)
- [ ] T020 [P] [US1] Unit test for isLoginSuccess function in tests/unit/login-detector.test.ts (verify URL pattern matching for oauth2 authorize/token endpoints)
- [ ] T021 [P] [US1] Unit test for LoginEvent creation and validation in tests/unit/login-event.test.ts (verify UUID generation, timestamp validation, URL validation)
- [ ] T022 [P] [US1] Unit test for cooldown logic in tests/unit/login-detector.test.ts (verify 1-second deduplication prevents redirect-induced duplicates)
- [ ] T023 [US1] Integration test for end-to-end login counting in tests/integration/login-counting.test.ts (mock webNavigation event → storage write → verify event persisted)

### Implementation for User Story 1

- [ ] T024 [P] [US1] Implement isLoginSuccess function in extension/background/login-detector.ts (detect oauth2/v2.0/authorize and oauth2/v2.0/token URL patterns)
- [ ] T025 [P] [US1] Implement createLoginEvent function in extension/background/login-detector.ts (generate UUID, capture timestamp, validate URL)
- [ ] T026 [US1] Implement cooldown mechanism in extension/background/login-detector.ts (track lastLoginTime, reject events within 1 second)
- [ ] T027 [US1] Implement chrome.webNavigation.onCompleted listener in extension/background/login-detector.ts (filter frameId=0, apply URL filter, call isLoginSuccess, create and store events)
- [ ] T028 [US1] Implement storeLoginEvent method in extension/storage/storage-manager.ts (append to loginEvents array, update metadata, handle quota errors)
- [ ] T029 [US1] Implement getLoginEvents method in extension/storage/storage-manager.ts (retrieve all events, return empty array if none exist)
- [ ] T030 [US1] Implement chrome.runtime.onInstalled listener in extension/background/login-detector.ts (initialize storage on first install with empty loginEvents array and metadata)
- [ ] T031 [US1] Add error handling and logging in extension/background/login-detector.ts (log detection events, storage errors, validation failures)

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently - login events are detected, counted, and stored

---

## Phase 4: User Story 2 - View Login Frequency Statistics (Priority: P2)

**Goal**: Display aggregated statistics showing login counts for today, this week, and this month

**Independent Test**: Perform multiple logins across different days, open extension popup, verify statistics correctly aggregate counts by day/week/month

### Tests for User Story 2 ⚠️ WRITE TESTS FIRST

- [ ] T032 [P] [US2] Unit test for computeStatistics function in tests/unit/statistics.test.ts (verify today/thisWeek/thisMonth counts with various event dates)
- [ ] T033 [P] [US2] Unit test for date-utils functions in tests/unit/date-utils.test.ts (verify startOfDay, startOfWeek with Monday, startOfMonth calculations)
- [ ] T034 [P] [US2] Unit test for empty state handling in tests/unit/statistics.test.ts (verify zero counts and empty message when no events)
- [ ] T035 [US2] Integration test for popup statistics display in tests/integration/popup-statistics.test.ts (mock stored events → call computeStatistics → verify DOM displays correct counts)

### Implementation for User Story 2

- [ ] T036 [P] [US2] Implement computeStatistics function in extension/lib/statistics.ts (filter events by time periods, return today/thisWeek/thisMonth/total counts)
- [ ] T037 [P] [US2] Create popup HTML structure in extension/popup/popup.html (sections for today/week/month counts, empty state message)
- [ ] T038 [P] [US2] Create popup CSS styling in extension/popup/popup.css (simple, readable layout for statistics display)
- [ ] T039 [US2] Implement popup.js in extension/popup/popup.js (load events from storage, call computeStatistics, render counts to DOM, handle empty state)
- [ ] T040 [US2] Add event listener for DOMContentLoaded in extension/popup/popup.js to trigger statistics loading
- [ ] T041 [US2] Implement formatPeriodLabel function in extension/popup/popup.js (format "Today", "This Week", "This Month" with date ranges)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - events are counted AND statistics are displayed

---

## Phase 5: User Story 3 - View Login Event History (Priority: P3)

**Goal**: Display chronological list of all past login events with timestamps

**Independent Test**: Perform several logins, open extension popup history view, verify chronological list shows timestamp for each login event

### Tests for User Story 3 ⚠️ WRITE TESTS FIRST

- [ ] T042 [P] [US3] Unit test for formatLoginEvent function in tests/unit/history.test.ts (verify timestamp formatting to user-friendly date/time)
- [ ] T043 [P] [US3] Unit test for history view empty state in tests/unit/history.test.ts (verify message when no events exist)
- [ ] T044 [P] [US3] Unit test for history pagination/limiting in tests/unit/history.test.ts (verify only last 100 events loaded for performance)
- [ ] T045 [US3] Integration test for history view rendering in tests/integration/history-view.test.ts (mock stored events → render history list → verify chronological order and timestamps)

### Implementation for User Story 3

- [ ] T046 [P] [US3] Add history section to extension/popup/popup.html (list container, empty state message)
- [ ] T047 [P] [US3] Add history view CSS in extension/popup/popup.css (list styling, scrollable container for many events)
- [ ] T048 [US3] Implement formatLoginEvent function in extension/popup/popup.js (convert Unix timestamp to local date/time string)
- [ ] T049 [US3] Implement renderHistory function in extension/popup/popup.js (load last 100 events, sort chronologically, create list items with formatted timestamps)
- [ ] T050 [US3] Add tab navigation in extension/popup/popup.html and popup.js (switch between statistics view and history view)
- [ ] T051 [US3] Handle empty history state in extension/popup/popup.js (show "No login events recorded yet" message)

**Checkpoint**: All user stories should now be independently functional - events detected, statistics displayed, history viewable

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T052 [P] Add extension icon in extension/icons/ (16x16, 48x48, 128x128 PNG files)
- [ ] T053 [P] Update manifest.json with extension name, description, version, and icon paths
- [ ] T054 [P] Add UUID generation library or implement UUID v4 function in extension/lib/uuid.ts
- [ ] T055 [P] Implement IndexedDB fallback in extension/storage/storage-manager.ts (for quota exceeded scenarios, per data-model.md migration strategy)
- [ ] T056 [P] Add storage quota monitoring in extension/background/login-detector.ts (check getBytesInUse, warn at 80% quota)
- [ ] T057 [P] Add error boundary/handling for popup in extension/popup/popup.js (graceful degradation if storage fails)
- [ ] T058 [P] Add loading state indicators in extension/popup/popup.html and popup.js (show "Loading..." while fetching data)
- [ ] T059 [P] Implement data export functionality in extension/popup/popup.js (export events to CSV per spec clarification)
- [ ] T060 [P] Add UTC to local timezone conversion helper in extension/lib/date-utils.ts (per edge case resolution in spec.md)
- [ ] T061 [P] Create README.md in repository root with quickstart instructions, installation steps, and usage guide
- [ ] T062 Run all tests to verify full system functionality (npm test)
- [ ] T063 Build extension for distribution (npm run build)
- [ ] T064 Manual testing: Load extension in Edge, test all user stories end-to-end
- [ ] T065 Verify constitution compliance: Tests written first, integration tests exist, complexity justified

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Technically independent, but builds UI on top of US1's stored data
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Technically independent, but builds UI on top of US1's stored data

### Within Each User Story

- Tests (T018-T023 for US1) MUST be written and FAIL before implementation (T024-T031)
- Background script before popup UI
- Core logic before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002-T004, T007-T010)
- All Foundational tasks marked [P] can run in parallel (T012-T013, T015-T016)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel (T018-T022 for US1)
- Within each story, models/utilities marked [P] can run in parallel
- Polish tasks (T052-T061) are mostly independent and can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all contract tests for User Story 1 together:
Task T018: "Contract test for webNavigation.onCompleted listener in tests/contract/url-detection.test.ts"
Task T019: "Contract test for storage.local API in tests/contract/storage-api.test.ts"

# Launch all unit tests for User Story 1 together:
Task T020: "Unit test for isLoginSuccess function in tests/unit/login-detector.test.ts"
Task T021: "Unit test for LoginEvent creation in tests/unit/login-event.test.ts"
Task T022: "Unit test for cooldown logic in tests/unit/login-detector.test.ts"

# After tests fail, launch parallel implementation tasks:
Task T024: "Implement isLoginSuccess function in extension/background/login-detector.ts"
Task T025: "Implement createLoginEvent function in extension/background/login-detector.ts"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T017) - CRITICAL: blocks all stories
3. Complete Phase 3: User Story 1 (T018-T031)
   - Write tests first (T018-T023)
   - Verify tests FAIL
   - Implement (T024-T031)
   - Verify tests PASS
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Load extension in Edge and verify login detection works

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP COMPLETE!**
3. Add User Story 2 → Test independently → Statistics view added
4. Add User Story 3 → Test independently → History view added
5. Add Polish → Final improvements
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T018-T031)
   - Developer B: User Story 2 (T032-T041)
   - Developer C: User Story 3 (T042-T051)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **CRITICAL**: Verify tests FAIL before implementing (TDD principle)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Follow constitution: test-first, pragmatic simplicity, focus on critical paths
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Browser extension must be manually loaded in Edge for testing (see quickstart.md)
