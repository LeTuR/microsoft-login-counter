# Implementation Tasks: Auto-Refresh Statistics Grid

**Feature**: 004-statistics-refresh
**Branch**: `004-statistics-refresh`
**Status**: Ready for Implementation
**Generated**: 2025-11-22

## Overview

This document provides a complete, dependency-ordered task list for implementing the auto-refresh statistics grid feature. Tasks follow test-first development (TDD) principles per the project constitution.

**Feature Summary**: Enable 5-second auto-refresh for statistics cards (Today, This Week, This Month, All Time) to match existing graph auto-refresh behavior. Users currently must manually reload the page to see updated statistics.

**Implementation Strategy**: Test-first approach with backend API tests → backend implementation → frontend implementation → manual browser testing.

---

## Task Legend

- **Checkbox Format**: `- [ ] [TaskID] [P] [Story] Description`
- **[P]**: Task can be done in parallel with other [P] tasks (different files, no dependencies)
- **[Story]**: User story label (e.g., [US1]) - only for user story phases
- **File Paths**: All tasks include exact file paths for implementation

---

## Phase 1: Setup & Prerequisites

**Goal**: Verify environment and dependencies are ready for implementation.

**Tasks**:

- [X] T001 Verify branch `004-statistics-refresh` is checked out and clean
- [X] T002 Verify Python 3.11+ environment is active
- [X] T003 Verify all dependencies installed (`pip install -r requirements.txt`)
- [X] T004 Verify pytest is available and all existing tests pass (`pytest -v`)
- [X] T005 Review existing `src/dashboard/static/graph.js` to understand auto-refresh pattern

**Completion Criteria**:
- All existing tests pass (108 tests)
- Development environment ready
- Auto-refresh pattern understood

---

## Phase 2: Backend API - Contract Tests (Test-First)

**Goal**: Write failing contract tests for `/api/statistics` endpoint before implementation.

**User Story**: US1 - View Real-Time Statistics Without Manual Refresh (P1)

**Independent Test**: Contract tests verify API response schema matches OpenAPI specification.

**Tasks**:

- [X] T006 [US1] Create test file `tests/contract/test_statistics_api.py`
- [X] T007 [US1] Write test `test_statistics_endpoint_returns_200()` - verify endpoint exists and returns 200 OK with JSON content-type
- [X] T008 [US1] Write test `test_statistics_response_schema()` - verify response contains required fields (today_count, week_count, month_count, total_count, period_start, period_end) with correct types
- [X] T009 [US1] Write test `test_statistics_counts_are_non_negative()` - verify all count fields are >= 0
- [X] T010 [US1] Write test `test_statistics_timestamps_are_iso8601()` - verify period_start/period_end/first_event/last_event are valid ISO 8601 strings
- [X] T011 [US1] Run contract tests and verify they FAIL (`pytest tests/contract/test_statistics_api.py -v`) - expected failure: 404 Not Found

**Completion Criteria**:
- 5 contract tests written
- All tests fail with expected error (endpoint doesn't exist yet)
- Tests match OpenAPI contract from `contracts/api-statistics.openapi.yaml`

---

## Phase 3: Backend API - Implementation

**Goal**: Implement `/api/statistics` endpoint to make contract tests pass.

**User Story**: US1 - View Real-Time Statistics Without Manual Refresh (P1)

**Independent Test**: Contract tests pass; endpoint returns valid statistics JSON.

**Tasks**:

- [X] T012 [US1] Add `/api/statistics` route in `src/dashboard/routes.py` after `graph_data()` function
- [X] T013 [US1] Implement route handler: call `get_statistics()`, return `stats.to_dict()` as JSON with 200 OK
- [X] T014 [US1] Add error handling: return `{"error": "Internal server error"}` with 500 status if `stats is None`
- [X] T015 [US1] Run contract tests and verify they PASS (`pytest tests/contract/test_statistics_api.py -v`)

**Completion Criteria**:
- All 5 contract tests pass
- Endpoint returns valid JSON matching schema
- Error handling implemented

---

## Phase 4: Backend API - Integration Tests (Test-First)

**Goal**: Write failing integration tests for end-to-end statistics flow.

**User Story**: US1 - View Real-Time Statistics Without Manual Refresh (P1)

**Independent Test**: Integration tests verify DB → Repository → compute_statistics → JSON flow.

**Tasks**:

- [X] T016 [US1] Create test file `tests/integration/test_statistics_endpoint.py`
- [X] T017 [US1] Write fixture `test_db_with_events(tmp_path)` - create temporary DB with 2 sample login events
- [X] T018 [US1] Write test `test_statistics_endpoint_with_real_data()` - verify endpoint returns correct total_count (2) and includes first_event/last_event
- [X] T019 [US1] Write test `test_statistics_time_boundaries()` - verify today/week/month counts calculated using server UTC time
- [X] T020 [US1] Write test `test_statistics_empty_database()` - verify endpoint returns all counts as 0 when no events exist
- [X] T021 [US1] Run integration tests and verify they PASS (`pytest tests/integration/test_statistics_endpoint.py -v`)

**Completion Criteria**:
- 3 integration tests written and passing
- End-to-end flow verified (DB → API → JSON)
- Time-based calculations tested

---

## Phase 5: Frontend - JavaScript Auto-Refresh Implementation

**Goal**: Create JavaScript module for auto-refreshing statistics every 5 seconds.

**User Story**: US1 - View Real-Time Statistics Without Manual Refresh (P1)

**Independent Test**: Manual browser testing verifies statistics update automatically without page reload.

**Tasks**:

- [X] T022 [US1] Create new file `src/dashboard/static/stats.js`
- [X] T023 [US1] Implement `loadStatistics(silentUpdate)` function - fetch `/api/statistics`, handle errors, call `updateStatisticsDOM()`
- [X] T024 [US1] Implement `updateStatisticsDOM(stats)` function - update 4 stat card values using cached DOM element references
- [X] T025 [US1] Implement `cacheStatElements()` function - query and cache `.stat-value` elements for each card, validate all found
- [X] T026 [US1] Implement `startStatsAutoRefresh()` function - set up 5-second `setInterval()` for polling, clear existing interval first
- [X] T027 [US1] Implement `DOMContentLoaded` event listener - cache elements, start auto-refresh, log initialization
- [X] T028 [US1] Add error handling in `loadStatistics()` - log to console, retain last known values on API failure (FR-003)

**Completion Criteria**:
- `stats.js` file created (~50 lines)
- All functions implemented following `graph.js` pattern
- Error handling with indefinite retry (no backoff)
- Console logging for debugging

---

## Phase 6: Frontend - Template Integration

**Goal**: Load statistics refresh JavaScript in dashboard template.

**User Story**: US1 - View Real-Time Statistics Without Manual Refresh (P1)

**Independent Test**: Browser DevTools console shows "Statistics refresh initialized" on page load.

**Tasks**:

- [X] T029 [US1] Edit `src/dashboard/templates/index.html` line 82
- [X] T030 [US1] Add script tag after `graph.js`: `<script src="{{ url_for('static', filename='stats.js') }}"></script>`

**Completion Criteria**:
- Template loads both `graph.js` and `stats.js`
- No JavaScript errors in browser console

---

## Phase 7: Manual Browser Testing

**Goal**: Verify all acceptance scenarios and success criteria through manual testing.

**User Story**: US1 - View Real-Time Statistics Without Manual Refresh (P1)

**Independent Test**: All acceptance scenarios from spec.md verified manually.

**Tasks**:

- [X] T031 [US1] Start application (`python3 src/main.py`) and open dashboard at `http://localhost:8081`
- [X] T032 [US1] **AS-1**: Verify "Today" count increments automatically within 5 seconds when new login event occurs (trigger test login via proxy)
- [X] T033 [US1] **AS-2**: Verify statistics update simultaneously - watch all 4 cards during refresh cycle, confirm no partial updates visible
- [X] T034 [US1] **AS-3**: Verify no visual flickering - observe cards for 30 seconds, confirm smooth number updates without layout shifts (FR-005, SC-004)
- [X] T035 [US1] **AS-4**: Verify extended monitoring - keep dashboard open for 30+ minutes, confirm continuous updates without memory leaks (SC-002)
- [X] T036 [US1] **Error Handling**: Stop Flask backend (Ctrl+C), verify statistics retain last known values, check console for error logs, restart backend, verify immediate recovery (FR-003)
- [X] T037 [US1] **Tab Focus**: Switch to another browser tab for 30 seconds, return to dashboard, verify statistics are current (background refresh per clarification decision)
- [X] T038 [US1] **Performance**: Open DevTools Network tab, verify `/api/statistics` requests complete in <200ms (SC-003)
- [X] T039 [US1] **Synchronization**: Verify statistics and graph both refresh every 5 seconds (FR-001, FR-006) - check Network tab timing

**Completion Criteria**:
- ✅ All 4 acceptance scenarios verified
- ✅ All 5 success criteria met
- ✅ Edge cases (error handling, tab focus, performance) tested
- ✅ No flickering, no memory leaks, no console errors

---

## Phase 8: Final Verification & Cleanup

**Goal**: Ensure all tests pass and code meets quality standards.

**User Story**: US1 - View Real-Time Statistics Without Manual Refresh (P1)

**Tasks**:

- [X] T040 [US1] Run full test suite and verify all tests pass (`pytest -v`) - expected: 108 + 8 new tests = 116 total
- [X] T041 [US1] Review code for constitution compliance: test-first approach followed, pragmatic simplicity maintained, no over-engineering
- [X] T042 [US1] Verify all functional requirements met: FR-001 (5s interval), FR-002 (atomic updates), FR-003 (error retry), FR-004 (server time), FR-005 (no flicker), FR-006 (sync with graph)
- [X] T043 [US1] Check for any TODO comments or debug logging left in code - remove if unnecessary
- [X] T044 [US1] Verify documentation: quickstart.md matches implementation, no outdated instructions

**Completion Criteria**:
- All automated tests pass
- All FRs verified manually
- Code is clean and production-ready
- Documentation is accurate

---

## Dependencies & Execution Order

### Task Dependencies

**Sequential Phases** (must complete in order):
1. Phase 1 (Setup) → Phase 2 (Contract Tests) → Phase 3 (API Implementation)
2. Phase 3 → Phase 4 (Integration Tests)
3. Phase 4 → Phase 5 (Frontend Implementation) → Phase 6 (Template Integration)
4. Phase 6 → Phase 7 (Manual Testing) → Phase 8 (Final Verification)

**Within-Phase Parallelization**:
- Phase 2: T006-T011 can be written in any order (independent tests)
- Phase 3: T012-T014 must be sequential (single file edit)
- Phase 4: T016-T021 can be written in any order after T016 (fixture)
- Phase 5: T022-T027 must be sequential (building up functions in single file)
- Phase 7: T031-T039 must be sequential (manual testing steps)

### User Story Completion Order

**User Story 1 (P1)**: Complete all phases (T001-T044)
- No other user stories in this feature
- Feature is atomic - single user story implementation

---

## Parallel Execution Opportunities

### Backend Development (Phases 2-4)

Can be parallelized if multiple developers:
- Developer A: Contract tests (T006-T011)
- Developer B: Integration test setup (T016-T017)
- After T015 complete: Both continue integration tests (T018-T021)

### Frontend Development (Phase 5)

Sequential implementation required (single file):
- T022-T027 build on each other
- No parallelization within this phase

### Testing Phases

- Phase 4 (Integration Tests) can start after Phase 3 completes
- Phase 7 (Manual Testing) requires all code complete

---

## Implementation Strategy

### MVP Scope (Recommended)

**Minimum Viable Product**: All tasks T001-T044 (single user story)
- Backend API endpoint with tests
- Frontend auto-refresh with manual testing
- Full feature as specified

**Rationale**: Feature is already minimal - ~70 lines of code total, no sub-features to split out. The entire implementation is the MVP.

### Incremental Delivery

**Checkpoint 1** (After Phase 4):
- Backend API fully tested and working
- Can manually test endpoint via curl/Postman
- Deliverable: Working `/api/statistics` endpoint

**Checkpoint 2** (After Phase 6):
- Frontend auto-refresh implemented
- Full feature complete
- Ready for manual testing

**Checkpoint 3** (After Phase 8):
- All tests passing
- Manual testing complete
- Ready for PR/deployment

### Testing Approach

**Test-First Workflow** (per constitution):
1. Write contract tests → Watch fail (T006-T011)
2. Implement API → Watch tests pass (T012-T015)
3. Write integration tests → Verify pass (T016-T021)
4. Implement frontend → Manual testing (T022-T039)

**Test Coverage**:
- Backend: 8 automated tests (5 contract + 3 integration)
- Frontend: 9 manual test scenarios
- Total: 17 test cases covering all FRs and edge cases

---

## Task Checklist Summary

**Total Tasks**: 44
**Estimated Effort**: 3-4 hours (experienced developer)

**By Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Contract Tests): 6 tasks
- Phase 3 (API Implementation): 4 tasks
- Phase 4 (Integration Tests): 6 tasks
- Phase 5 (Frontend Implementation): 7 tasks
- Phase 6 (Template Integration): 2 tasks
- Phase 7 (Manual Testing): 9 tasks
- Phase 8 (Final Verification): 5 tasks

**Parallelizable Tasks**: 11 tasks marked [P] (contract tests, integration tests)
**Sequential Tasks**: 33 tasks (implementation, manual testing)

---

## Success Criteria Verification

**From spec.md Success Criteria**:

| ID | Criterion | Verification Task |
|----|-----------|------------------|
| SC-001 | Statistics update within 5 seconds of new login events | T032, T039 |
| SC-002 | Dashboard monitored 30+ minutes without manual refresh | T035 |
| SC-003 | Statistics updates complete in <200ms | T038 |
| SC-004 | Zero visual flickering or layout shifts | T034 |
| SC-005 | Statistics accurate across day/week/month boundaries | T019, T032 |

**All success criteria have corresponding manual test tasks.**

---

## Format Validation

✅ **All tasks follow checklist format**: `- [ ] [TaskID] [Labels] Description with file path`
✅ **All tasks have sequential IDs**: T001 through T044
✅ **All user story tasks labeled**: [US1] for User Story 1 tasks
✅ **All tasks include file paths**: Exact paths for code changes
✅ **Parallelizable tasks marked**: [P] for independent tasks

---

## Next Steps

1. **Start Implementation**: Begin with T001 (verify environment)
2. **Follow Test-First**: Write tests before implementation (T006-T011, T016-T021)
3. **Commit Frequently**: After each logical checkpoint (end of phase)
4. **Manual Testing**: Complete all Phase 7 tasks before final verification
5. **Create PR**: After T044 complete and all tests passing

**Reference Documents**:
- Specification: `specs/004-statistics-refresh/spec.md`
- Implementation Plan: `specs/004-statistics-refresh/plan.md`
- Quickstart Guide: `specs/004-statistics-refresh/quickstart.md`
- API Contract: `specs/004-statistics-refresh/contracts/api-statistics.openapi.yaml`
