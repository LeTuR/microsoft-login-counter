# Tasks: Microsoft Login Event Counter

**Input**: Design documents from `/specs/001-microsoft-login-counter/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/dashboard-api.md, research.md

**Tests**: Following constitution principle I (Test-First Development), tests are included and MUST be written first before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Proxy Application**: `src/` at repository root
- **Tests**: `tests/` at repository root
- Paths shown below assume single Python project structure per plan.md

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per plan.md (src/, tests/, config.yaml, requirements.txt, pytest.ini)
- [x] T002 [P] Create requirements.txt with dependencies (mitmproxy>=10.0, Flask>=3.0, PyYAML>=6.0, pytest>=7.4, pytest-mock)
- [x] T003 [P] Create pytest.ini configuration file with test paths and coverage settings
- [x] T004 [P] Create config.yaml template with proxy port (8080), dashboard port (8081), database path, and logging configuration
- [x] T005 [P] Create src/proxy/, src/storage/, src/dashboard/, src/config/, src/logging/ directories
- [x] T006 [P] Create tests/contract/, tests/integration/, tests/unit/ directories
- [x] T007 [P] Create .gitignore to exclude __pycache__, *.pyc, .pytest_cache, *.db, logs/
- [x] T008 [P] Create README.md with project overview and setup instructions reference

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Implement SQLite schema in src/storage/schema.sql (CREATE TABLE login_events, CREATE TABLE proxy_metadata, CREATE INDEX)
- [ ] T010 [P] Implement Database class in src/storage/database.py (connection management, schema initialization, transaction support)
- [ ] T011 [P] Implement ConfigLoader class in src/config/loader.py (load/validate config.yaml, provide default values)
- [ ] T012 [P] Implement logging setup in src/logging/setup.py (configure rotating file handler, console handler, log levels from config)
- [ ] T013 [P] Create LoginEvent dataclass in src/storage/models.py (id, timestamp, unix_timestamp, detected_via fields)
- [ ] T014 [P] Create LoginStatistics dataclass in src/storage/models.py (today_count, week_count, month_count, total_count, period_start, period_end)
- [ ] T015 [P] Implement time utility functions in src/storage/time_utils.py (get_day_bounds, get_week_bounds with Monday start, get_month_bounds in UTC)
- [ ] T016 Unit test for Database schema initialization in tests/unit/test_database.py (verify tables created, indexes exist)
- [ ] T017 [P] Unit test for ConfigLoader in tests/unit/test_config_loader.py (verify YAML parsing, default values, validation)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Detect and Count Login Events via Proxy (Priority: P1) 🎯 MVP

**Goal**: Automatically detect Microsoft authentication events through HTTP traffic monitoring and persist to SQLite

**Independent Test**: Configure proxy, log in to Microsoft services multiple times, verify events are stored in database with timestamps

### Tests for User Story 1 ⚠️ WRITE TESTS FIRST

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T018 [P] [US1] Contract test for HTTP CONNECT detection in tests/contract/test_connect_detection.py (verify CONNECT to login.microsoftonline.com triggers session tracking)
- [ ] T019 [P] [US1] Contract test for OAuth callback pattern matching in tests/contract/test_oauth_callback.py (verify code= and state= parameters detected in redirect URLs)
- [ ] T020 [P] [US1] Unit test for is_microsoft_login_connect function in tests/unit/test_detector.py (verify hostname matching for login.microsoftonline.com)
- [ ] T021 [P] [US1] Unit test for is_oauth_callback function in tests/unit/test_detector.py (verify callback URL patterns with success parameters)
- [ ] T022 [P] [US1] Unit test for SessionTracker class in tests/unit/test_session_tracker.py (verify session tracking, timeout after 60 seconds)
- [ ] T023 [P] [US1] Unit test for Repository.insert_login_event in tests/unit/test_repository.py (verify transaction support, timestamp validation)
- [ ] T024 [US1] Integration test for proxy → detector → database flow in tests/integration/test_login_detection_flow.py (mock HTTP flow, verify event persisted)

### Implementation for User Story 1

- [ ] T025 [P] [US1] Implement SessionTracker class in src/proxy/session_tracker.py (track CONNECT events with timestamps, expire old sessions)
- [ ] T026 [P] [US1] Implement is_microsoft_login_connect function in src/proxy/detector.py (check if CONNECT request is to login.microsoftonline.com)
- [ ] T027 [P] [US1] Implement is_oauth_callback function in src/proxy/detector.py (check URL for /callback or /auth path and code=/state= parameters)
- [ ] T028 [US1] Implement LoginDetectorAddon class in src/proxy/addon.py (mitmproxy addon with http_connect and request event handlers)
- [ ] T029 [US1] Implement http_connect handler in src/proxy/addon.py (track sessions via SessionTracker when detecting login.microsoftonline.com)
- [ ] T030 [US1] Implement request handler in src/proxy/addon.py (check for OAuth callbacks within 60s of tracked session, record login event)
- [ ] T031 [US1] Implement Repository class in src/storage/repository.py (insert_login_event, get_events_by_date_range, get_total_count methods)
- [ ] T032 [US1] Implement record_login_event method in src/proxy/addon.py (call Repository.insert_login_event with timestamp and detection method)
- [ ] T033 [US1] Add operational logging in src/proxy/addon.py (log CONNECT detections, callback matches, database writes, errors)
- [ ] T034 [US1] Create main.py entry point to start mitmproxy with LoginDetectorAddon

**Checkpoint**: At this point, User Story 1 should be fully functional - proxy detects logins and stores to SQLite

---

## Phase 4: User Story 2 - View Login Frequency Statistics (Priority: P2)

**Goal**: Display web dashboard showing today/week/month login counts

**Independent Test**: Navigate to http://localhost:8081, verify statistics page shows correct counts for different time periods

### Tests for User Story 2 ⚠️ WRITE TESTS FIRST

- [ ] T035 [P] [US2] Contract test for GET / endpoint in tests/contract/test_dashboard_api.py (verify response status 200, Content-Type text/html)
- [ ] T036 [P] [US2] Unit test for compute_statistics function in tests/unit/test_statistics.py (verify today/week/month aggregations with sample events)
- [ ] T037 [P] [US2] Unit test for time_utils period calculations in tests/unit/test_time_utils.py (verify Monday week start, UTC handling)
- [ ] T038 [P] [US2] Unit test for Repository.get_events_by_date_range in tests/unit/test_repository.py (verify SQL query correctness with date filters)
- [ ] T039 [US2] Integration test for dashboard statistics in tests/integration/test_dashboard_stats.py (insert test events, call GET /, verify HTML contains correct counts)

### Implementation for User Story 2

- [ ] T040 [P] [US2] Implement compute_statistics function in src/dashboard/stats.py (query events by time periods, return LoginStatistics dataclass)
- [ ] T041 [P] [US2] Implement get_statistics helper in src/dashboard/routes.py (call compute_statistics, handle empty database case)
- [ ] T042 [P] [US2] Create index.html Jinja2 template in src/dashboard/templates/ (statistics page layout with today/week/month counts)
- [ ] T043 [P] [US2] Create base.html Jinja2 template in src/dashboard/templates/ (common layout with navigation)
- [ ] T044 [P] [US2] Create style.css in src/dashboard/static/ (simple, readable styling for statistics display)
- [ ] T045 [US2] Implement Flask app initialization in src/dashboard/app.py (create Flask app, configure templates/static folders, set up database connection)
- [ ] T046 [US2] Implement GET / route in src/dashboard/routes.py (call get_statistics, render index.html template with stats)
- [ ] T047 [US2] Handle empty state in index.html template (show "No logins recorded yet" message when total_count is 0)
- [ ] T048 [US2] Update main.py to start Flask dashboard in separate thread alongside proxy

**Checkpoint**: At this point, User Stories 1 AND 2 work together - proxy detects and dashboard displays statistics

---

## Phase 5: User Story 3 - View Login Event History (Priority: P3)

**Goal**: Display chronological list of all past login events with timestamps

**Independent Test**: Navigate to http://localhost:8081/history, verify chronological list of events with formatted timestamps

### Tests for User Story 3 ⚠️ WRITE TESTS FIRST

- [ ] T049 [P] [US3] Contract test for GET /history endpoint in tests/contract/test_dashboard_api.py (verify response status 200, pagination query params)
- [ ] T050 [P] [US3] Unit test for Repository.get_recent_events in tests/unit/test_repository.py (verify LIMIT and ORDER BY clauses, pagination logic)
- [ ] T051 [P] [US3] Unit test for format_timestamp function in tests/unit/test_dashboard_helpers.py (verify ISO 8601 to user-friendly format conversion)
- [ ] T052 [US3] Integration test for history view in tests/integration/test_dashboard_history.py (insert test events, call GET /history, verify HTML contains chronological list)

### Implementation for User Story 3

- [ ] T053 [P] [US3] Implement Repository.get_recent_events method in src/storage/repository.py (query last N events ordered by id DESC, support pagination)
- [ ] T054 [P] [US3] Implement format_timestamp helper in src/dashboard/helpers.py (convert ISO 8601 UTC to local timezone display format)
- [ ] T055 [P] [US3] Create history.html Jinja2 template in src/dashboard/templates/ (table layout with timestamp and detection method columns)
- [ ] T056 [US3] Implement GET /history route in src/dashboard/routes.py (parse page/limit query params, call get_recent_events, render history.html)
- [ ] T057 [US3] Add pagination controls to history.html template (Previous/Next page links based on result count)
- [ ] T058 [US3] Handle empty history state in history.html template (show "No login events recorded yet" when events list is empty)
- [ ] T059 [US3] Add navigation link from index.html to /history and vice versa

**Checkpoint**: All user stories are now independently functional - detection, statistics, and history all work

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T060 [P] Implement GET /api/stats JSON endpoint in src/dashboard/routes.py per contracts/dashboard-api.md
- [ ] T061 [P] Implement GET /api/events JSON endpoint in src/dashboard/routes.py per contracts/dashboard-api.md
- [ ] T062 [P] Add Flask error handlers in src/dashboard/routes.py (404, 500 with HTML/JSON response based on Accept header)
- [ ] T063 [P] Add signal handlers in main.py for graceful shutdown (SIGINT, SIGTERM to close database connections)
- [ ] T064 [P] Implement database connection pooling or separate connections for proxy/dashboard in src/storage/database.py
- [ ] T065 [P] Add HTTP security headers to Flask responses (X-Content-Type-Options, Cache-Control per contracts)
- [ ] T066 [P] Create quickstart.md documentation with browser proxy configuration instructions (Chrome, Firefox, Edge, Safari, system-wide)
- [ ] T067 [P] Add upstream proxy support to config.yaml and main.py (for corporate proxy chaining per research.md issue 2)
- [ ] T068 [P] Implement database migration check on startup in src/storage/database.py (verify schema_version in proxy_metadata)
- [ ] T069 [P] Add performance monitoring in src/proxy/addon.py (track proxy latency, log if exceeding 100ms target)
- [ ] T070 [P] Create example systemd service file in docs/systemd/login-counter.service for Linux deployment
- [ ] T071 Run all tests to verify full system functionality (pytest tests/)
- [ ] T072 Manual end-to-end testing: Start proxy, configure browser, login to Microsoft, verify dashboard displays events
- [ ] T073 Verify constitution compliance: TDD followed (tests first), integration tests exist, pragmatic simplicity maintained
- [ ] T074 Performance validation: Verify proxy latency <100ms, statistics load <10s, history pagination <1s
- [ ] T075 Security review: Verify no TLS decryption, database file permissions 0600, no credentials stored

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3) for MVP-first approach
- **Polish (Phase 6)**: Depends on desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on Foundational (Phase 2) - Technically independent, but displays data from US1's detections
- **User Story 3 (P3)**: Depends on Foundational (Phase 2) - Technically independent, but displays data from US1's detections

### Within Each User Story

1. **Tests FIRST** (contract → unit → integration) - MUST fail before implementation
2. Core detection/query logic
3. Storage/persistence layer
4. UI/API endpoints
5. Error handling and logging
6. Checkpoint: Verify story works independently

### Parallel Opportunities

- **Setup (Phase 1)**: T002-T004, T005-T008 can run in parallel
- **Foundational (Phase 2)**: T010-T015, T017 can run in parallel (after T009 schema done)
- **User Story 1**: T018-T023 tests in parallel, then T025-T027 implementation in parallel
- **User Story 2**: T035-T038 tests in parallel, then T040-T044 implementation in parallel
- **User Story 3**: T049-T051 tests in parallel, then T053-T055 implementation in parallel
- **Polish (Phase 6)**: Most tasks (T060-T070) can run in parallel
- **Between Stories**: US1, US2, US3 can all run in parallel after Foundational phase if team capacity allows

---

## Parallel Example: User Story 1

```bash
# Launch all contract tests for User Story 1 together:
Task T018: "Contract test for HTTP CONNECT detection in tests/contract/test_connect_detection.py"
Task T019: "Contract test for OAuth callback pattern matching in tests/contract/test_oauth_callback.py"

# Launch all unit tests for User Story 1 together:
Task T020: "Unit test for is_microsoft_login_connect in tests/unit/test_detector.py"
Task T021: "Unit test for is_oauth_callback in tests/unit/test_detector.py"
Task T022: "Unit test for SessionTracker in tests/unit/test_session_tracker.py"
Task T023: "Unit test for Repository.insert_login_event in tests/unit/test_repository.py"

# After tests fail, launch parallel implementation tasks:
Task T025: "Implement SessionTracker class in src/proxy/session_tracker.py"
Task T026: "Implement is_microsoft_login_connect in src/proxy/detector.py"
Task T027: "Implement is_oauth_callback in src/proxy/detector.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T008)
2. Complete Phase 2: Foundational (T009-T017) - CRITICAL: blocks all stories
   - Write foundational tests (T016-T017)
   - Verify tests fail
   - Implement foundation (T009-T015)
   - Verify tests pass
3. Complete Phase 3: User Story 1 (T018-T034)
   - Write tests first (T018-T024)
   - Verify tests FAIL
   - Implement (T025-T034)
   - Verify tests PASS
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Configure browser proxy, log in to Microsoft, verify detection works

**Result**: Minimal viable product - proxy detects and counts Microsoft logins

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP COMPLETE** (detection working)
3. Add User Story 2 → Test independently → **Statistics dashboard added**
4. Add User Story 3 → Test independently → **History view added**
5. Add Polish → Final improvements
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T018-T034) - Detection & storage
   - Developer B: User Story 2 (T035-T048) - Statistics dashboard
   - Developer C: User Story 3 (T049-T059) - History view
3. Stories complete and integrate independently
4. All merge into main without conflicts (different files)

---

## Task Summary

**Total Tasks**: 75
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 9 tasks (2 test tasks)
- Phase 3 (User Story 1 - P1): 17 tasks (7 test tasks, 10 implementation tasks)
- Phase 4 (User Story 2 - P2): 14 tasks (5 test tasks, 9 implementation tasks)
- Phase 5 (User Story 3 - P3): 11 tasks (4 test tasks, 7 implementation tasks)
- Phase 6 (Polish): 16 tasks

**Test Tasks**: 18 (24% of total - focused on critical paths per constitution)
**Parallel Tasks**: 43 tasks marked [P] (57% can run in parallel)

**MVP Scope** (User Story 1 only): 34 tasks (Setup + Foundational + US1)
**Full Feature**: 75 tasks (all phases)

---

## Notes

- **[P]** tasks operate on different files with no dependencies - can run in parallel
- **[Story]** label maps task to specific user story for traceability
- Each user story is independently completable and testable
- **CRITICAL**: Follow TDD - write tests FIRST, verify they FAIL, then implement
- Constitution compliance: Test-first (Principle I), integration tests (Principle II), pragmatic simplicity (Principle III)
- Tests focus on critical paths: detection logic, database persistence, API contracts
- Commit after each task or logical group
- Stop at checkpoints to validate each story independently
- Manual testing required for proxy configuration and browser integration
- Follow research.md decisions for implementation details
- Refer to data-model.md for schema and contracts/dashboard-api.md for endpoint specifications
