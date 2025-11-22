# Tasks: Bar Chart Visualization for Daily Login Trends

**Input**: Design documents from `/specs/003-bar-chart-visualization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: This project follows Test-First Development (TDD) per the constitution. All test tasks are included and MUST be completed BEFORE implementation tasks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Repository root: `/home/magicletur/repositories/microsoft-login-counter/`
- Source: `src/`
- Tests: `tests/`
- Dashboard static files: `src/dashboard/static/`
- Dashboard templates: `src/dashboard/templates/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verify existing Chart.js integration and prepare for bar chart implementation

- [ ] T001 Verify Chart.js v4.4.1 is loaded and functional in src/dashboard/templates/base.html
- [ ] T002 [P] Review existing graph.js structure in src/dashboard/static/graph.js to understand line chart implementation
- [ ] T003 [P] Review existing CSS styles in src/dashboard/static/style.css for graph container

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Verify backend aggregation and API compatibility for bar chart data

**⚠️ CRITICAL**: These verification tasks ensure existing infrastructure works correctly before bar chart changes

- [ ] T004 Verify existing get_aggregated_graph_data() function handles 90-day threshold correctly in src/storage/repository.py
- [ ] T005 [P] Verify existing /api/graph-data endpoint returns data compatible with bar chart rendering in src/dashboard/routes.py
- [ ] T006 [P] Run existing contract tests to establish baseline (tests/contract/test_graph_api.py)

**Checkpoint**: Foundation verified - bar chart implementation can now begin

---

## Phase 3: User Story 1 - View Daily Login Counts with Bar Chart (Priority: P1) 🎯 MVP

**Goal**: Replace line chart with interactive bar chart showing daily login counts with gradient blue colors

**Independent Test**: Generate login events across multiple days with varying counts (e.g., 5 logins on Monday, 2 on Tuesday, 10 on Wednesday), visit the dashboard, and verify that a bar chart displays with distinct bars for each day showing the correct heights corresponding to login counts with gradient colors from light to dark blue.

### Tests for User Story 1 (TDD - Write FIRST, ensure they FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T007 [P] [US1] Write unit test for calculateGradientColors() with two different values in tests/unit/test_gradient.py
- [ ] T008 [P] [US1] Write unit test for calculateGradientColors() with all same values (edge case) in tests/unit/test_gradient.py
- [ ] T009 [P] [US1] Write unit test for calculateGradientColors() with zero values in tests/unit/test_gradient.py
- [ ] T010 [P] [US1] Write unit test for calculateGradientColors() with large range (0-1000) in tests/unit/test_gradient.py
- [ ] T011 [P] [US1] Write unit test for calculateGradientColors() RGB format validation in tests/unit/test_gradient.py
- [ ] T012 [P] [US1] Write integration test for bar chart rendering with gradient colors in tests/integration/test_bar_rendering.py
- [ ] T013 [P] [US1] Write integration test for zero-height bars visibility in tests/integration/test_bar_rendering.py

**RUN TESTS - Verify they all FAIL with expected failures**

### Implementation for User Story 1

#### Gradient Color Calculation

- [ ] T014 [US1] Implement calculateGradientColors() function in src/dashboard/static/graph.js with linear RGB interpolation from #add8e6 to #003d6b

**RUN UNIT TESTS - Verify gradient calculation tests now PASS**

#### Bar Chart Configuration

- [ ] T015 [US1] Change Chart.js type from 'line' to 'bar' in renderGraph() function in src/dashboard/static/graph.js
- [ ] T016 [US1] Remove line-specific properties (tension, fill, pointRadius) from dataset configuration in src/dashboard/static/graph.js
- [ ] T017 [US1] Add bar-specific properties (barPercentage: 0.9, categoryPercentage: 0.8) to dataset configuration in src/dashboard/static/graph.js
- [ ] T018 [US1] Set backgroundColor to gradient array using calculateGradientColors() in renderGraph() function in src/dashboard/static/graph.js
- [ ] T019 [US1] Update borderColor and borderWidth for bar styling in dataset configuration in src/dashboard/static/graph.js

#### Silent Update Integration

- [ ] T020 [US1] Update silent update logic to recalculate gradient colors in renderGraph() function in src/dashboard/static/graph.js

**RUN ALL TESTS - Verify User Story 1 tests now PASS**

**Manual Verification**:
- [ ] T021 [US1] Visual test: Verify bar chart displays with gradient colors (light blue for low counts, dark blue for high counts)
- [ ] T022 [US1] Visual test: Verify bars are visually distinct with appropriate spacing
- [ ] T023 [US1] Visual test: Verify tooltips show correct date and count on hover
- [ ] T024 [US1] Visual test: Verify zero-height bars are present for days with no logins

**Checkpoint**: At this point, User Story 1 should be fully functional - users can see daily login counts as a bar chart with gradient colors

---

## Phase 4: User Story 2 - Maintain Time Period Filtering with Bar Chart (Priority: P2)

**Goal**: Ensure existing time period filters (Last 24H, 7D, 30D, All Time) work correctly with bar chart and gradient colors

**Independent Test**: Record login events across 60 days, click the "Last 7 Days" filter button, and verify the bar chart updates to show only the past 7 days' worth of bars with accurate daily counts and recalculated gradient colors.

### Tests for User Story 2 (TDD - Write FIRST, ensure they FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T025 [P] [US2] Write integration test for bar chart filter change with gradient recalculation in tests/integration/test_bar_rendering.py
- [ ] T026 [P] [US2] Write integration test for hourly aggregation with 24H filter showing bars in tests/integration/test_bar_rendering.py
- [ ] T027 [P] [US2] Write integration test for weekly aggregation with > 90 days showing bars in tests/integration/test_bar_rendering.py
- [ ] T028 [P] [US2] Write integration test for auto-refresh maintaining filter state and updating gradient in tests/integration/test_bar_rendering.py

**RUN TESTS - Verify they all FAIL with expected failures**

### Implementation for User Story 2

#### Filter Compatibility

- [ ] T029 [US2] Verify period filter button click handlers work with bar chart in src/dashboard/static/graph.js (should already work, just verify)
- [ ] T030 [US2] Verify gradient colors recalculate when filter changes (calculateGradientColors called on each loadGraphData)

#### Aggregation Level Verification

- [ ] T031 [US2] Verify hourly bars display correctly for 24H filter (backend already handles this, verify frontend rendering)
- [ ] T032 [US2] Verify daily bars display correctly for 7D and 30D filters
- [ ] T033 [US2] Verify weekly bars display correctly for periods > 90 days (backend already handles this, verify frontend rendering)

**RUN ALL TESTS - Verify User Story 2 tests now PASS**

**Manual Verification**:
- [ ] T034 [US2] Visual test: Click each filter button (24H, 7D, 30D, All) and verify bar chart updates with correct aggregation
- [ ] T035 [US2] Visual test: Verify gradient colors recalculate for each filter (lightest to darkest based on visible range)
- [ ] T036 [US2] Visual test: Verify auto-refresh updates bar chart without losing filter selection
- [ ] T037 [US2] Visual test: Verify smooth transitions when switching filters (no flicker)

**Checkpoint**: At this point, User Story 2 should be fully functional - time period filtering works seamlessly with bar chart visualization

---

## Phase 5: User Story 3 - Responsive Bar Chart on Mobile Devices (Priority: P3)

**Goal**: Ensure bar chart remains readable and interactive on mobile devices with touch-friendly bars

**Independent Test**: Open the dashboard on a mobile device with a 375px screen width, verify that the bar chart displays properly with readable bars, and confirm that tapping on bars shows tooltips.

### Tests for User Story 3 (TDD - Write FIRST, ensure they FAIL)

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T038 [P] [US3] Write integration test for mobile bar chart rendering at 320px width in tests/integration/test_bar_rendering.py
- [ ] T039 [P] [US3] Write integration test for touch target size verification (minimum 44px) in tests/integration/test_bar_rendering.py
- [ ] T040 [P] [US3] Write integration test for mobile tooltip display on tap in tests/integration/test_bar_rendering.py

**RUN TESTS - Verify they all FAIL with expected failures**

### Implementation for User Story 3

#### Mobile Responsiveness

- [ ] T041 [US3] Verify existing responsive CSS applies correctly to bar chart in src/dashboard/static/style.css (no changes expected)
- [ ] T042 [US3] Verify bar chart height on mobile (300px minimum) ensures 44px touch targets in src/dashboard/static/style.css
- [ ] T043 [US3] Verify Chart.js responsive options work with bar chart (maintainAspectRatio: false already configured)

#### Touch Interaction

- [ ] T044 [US3] Verify tooltip displays on tap for mobile devices (Chart.js handles this automatically, verify it works)
- [ ] T045 [US3] Verify X-axis labels rotate or abbreviate on small screens (Chart.js handles this, verify behavior)

**RUN ALL TESTS - Verify User Story 3 tests now PASS**

**Manual Verification**:
- [ ] T046 [US3] Mobile test: Open dashboard on 320px viewport and verify bars are readable
- [ ] T047 [US3] Mobile test: Tap on bars and verify tooltips appear
- [ ] T048 [US3] Mobile test: Verify no horizontal scrolling required
- [ ] T049 [US3] Mobile test: Verify X-axis labels are legible (rotated or abbreviated if needed)
- [ ] T050 [US3] Mobile test: Test on actual mobile device (iOS and Android) to verify touch responsiveness

**Checkpoint**: At this point, User Story 3 should be fully functional - bar chart works excellently on mobile devices with touch-friendly interaction

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements, documentation, and cleanup

### Edge Case Verification

- [ ] T051 [P] Manual test: Verify gradient works correctly with outlier values (1 very high count, others low)
- [ ] T052 [P] Manual test: Verify smooth transition from line chart to bar chart on first load (no flicker)
- [ ] T053 [P] Manual test: Verify bar chart performs well with 90 bars (max daily before weekly aggregation)

### Documentation

- [ ] T054 [P] Update CLAUDE.md with bar chart implementation notes (if needed)
- [ ] T055 [P] Add inline code comments explaining gradient calculation algorithm in src/dashboard/static/graph.js
- [ ] T056 [P] Verify quickstart.md instructions match actual implementation

### Final Verification

- [ ] T057 Run full test suite (all tests from all user stories) and verify 100% pass rate
- [ ] T058 Run existing contract tests to ensure no regressions in API compatibility
- [ ] T059 Cross-browser testing: Verify bar chart works in Chrome, Firefox, Safari, Edge
- [ ] T060 Performance test: Verify auto-refresh with 90 bars completes in < 5 seconds

---

## Dependencies & Parallel Execution

### User Story Completion Order

```
Phase 1: Setup (T001-T003)
    ↓
Phase 2: Foundational (T004-T006) ← Must complete before user stories
    ↓
┌───────────────────────────────────────────────┐
│ Phase 3: User Story 1 (T007-T024) 🎯 MVP     │
│ Can start after Phase 2 completes             │
└───────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────┐
│ Phase 4: User Story 2 (T025-T037)             │
│ Depends on: User Story 1 complete             │
└───────────────────────────────────────────────┘
    ↓
┌───────────────────────────────────────────────┐
│ Phase 5: User Story 3 (T038-T050)             │
│ Depends on: User Story 1 complete             │
│ Can run in parallel with User Story 2         │
└───────────────────────────────────────────────┘
    ↓
Phase 6: Polish (T051-T060)
```

### Parallel Execution Opportunities

**Within User Story 1**:
- T007-T013 (all test tasks) can run in parallel
- T021-T024 (all manual verification tasks) can run in parallel

**Within User Story 2**:
- T025-T028 (all test tasks) can run in parallel
- T034-T037 (all manual verification tasks) can run in parallel

**Within User Story 3**:
- T038-T040 (all test tasks) can run in parallel
- T046-T050 (all manual verification tasks) can run in parallel

**Within Phase 6**:
- T051-T053 (manual tests) can run in parallel
- T054-T056 (documentation) can run in parallel

**Cross-Story Parallelization**:
- User Story 2 and User Story 3 implementation can run in parallel after User Story 1 completes

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**MVP = User Story 1 Only** (T001-T024)

This delivers:
- ✅ Bar chart visualization with gradient colors
- ✅ Daily login count bars
- ✅ Zero-height bars for days with no logins
- ✅ Interactive tooltips
- ✅ Gradient color scale (light to dark blue)

**Total MVP Tasks**: 24 tasks
**Estimated Time**: 2-4 hours (including testing)

### Incremental Delivery

**Iteration 1** (MVP): User Story 1
- Delivers core value: bar chart with gradient
- Independently testable
- Can be deployed without User Stories 2 and 3

**Iteration 2**: User Story 2
- Adds: Time period filtering compatibility
- Builds on: User Story 1
- Independently testable with existing filters

**Iteration 3**: User Story 3
- Adds: Mobile responsiveness verification
- Builds on: User Story 1
- Independently testable on mobile devices
- Can be done in parallel with User Story 2

**Iteration 4**: Polish
- Final edge case verification
- Documentation updates
- Cross-browser testing

### Task Summary

**Total Tasks**: 60
- Phase 1 (Setup): 3 tasks
- Phase 2 (Foundational): 3 tasks
- Phase 3 (User Story 1): 18 tasks (7 tests + 11 implementation)
- Phase 4 (User Story 2): 13 tasks (4 tests + 9 implementation)
- Phase 5 (User Story 3): 13 tasks (3 tests + 10 implementation)
- Phase 6 (Polish): 10 tasks

**Parallel Opportunities**: 35 tasks marked with [P] (58% can run in parallel)

**Test Coverage**:
- Unit tests: 5 (gradient calculation)
- Integration tests: 9 (bar chart rendering, filtering, mobile)
- Contract tests: Reuse existing (compatibility verification)
- Manual tests: 17 (visual verification, cross-browser, performance)

### Testing Philosophy

Following **Constitution Principle I (TDD)**:
1. Write tests FIRST for each user story
2. Verify tests FAIL before implementation
3. Implement feature to make tests PASS
4. Refactor while keeping tests green

**Test-First Workflow**:
- User Story 1: T007-T013 (tests) → T014-T020 (implementation) → T021-T024 (verification)
- User Story 2: T025-T028 (tests) → T029-T033 (implementation) → T034-T037 (verification)
- User Story 3: T038-T040 (tests) → T041-T045 (implementation) → T046-T050 (verification)

---

## Validation Checklist

✅ **Format Validation**: All tasks follow `- [ ] [ID] [P?] [Story?] Description with file path` format
✅ **Sequential IDs**: Tasks numbered T001-T060 in execution order
✅ **Story Labels**: All user story tasks include [US1], [US2], or [US3] label
✅ **Parallel Markers**: [P] added to tasks that can run in parallel
✅ **File Paths**: All implementation tasks include exact file paths
✅ **Test-First**: Tests written before implementation per TDD principle
✅ **Independent Stories**: Each user story has clear goal and independent test
✅ **MVP Identified**: User Story 1 marked as MVP scope
✅ **Dependencies Documented**: Story completion order clearly defined
✅ **Parallel Opportunities**: 35 tasks identified for parallel execution
