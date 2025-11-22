# Implementation Plan: Auto-Refresh Statistics Grid

**Branch**: `004-statistics-refresh` | **Date**: 2025-11-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-statistics-refresh/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Enable auto-refresh functionality for the statistics grid (Today, This Week, This Month, All Time counts) to match the existing 5-second auto-refresh behavior of the bar chart visualization. Currently, the graph updates automatically via JavaScript polling to `/api/graph-data`, but the statistics cards remain static after initial page load. This feature will add a parallel auto-refresh mechanism that polls statistics data and updates the DOM without page reload, maintaining synchronization with the graph refresh cycle.

## Technical Context

**Language/Version**: Python 3.11+ (backend), JavaScript ES6+ (frontend)
**Primary Dependencies**: Flask (backend), Chart.js 4.4.1 (graph rendering), Vanilla JavaScript (statistics refresh)
**Storage**: SQLite via Repository pattern (`src/storage/repository.py`)
**Testing**: pytest (Python), manual browser testing (JavaScript)
**Target Platform**: Web dashboard (HTML/CSS/JavaScript frontend, Flask backend)
**Project Type**: Web application (Python backend + JavaScript frontend)
**Performance Goals**: Statistics refresh completes in <200ms, 5-second refresh interval
**Constraints**: No visual flickering during updates, atomic updates (all stats together), indefinite retry on errors
**Scale/Scope**: Single-page dashboard with 4 statistics cards, existing auto-refresh infrastructure from feature 003

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Test-First Development (TDD) - ✓ PASS

- **Status**: Ready for test-first workflow
- **Plan**:
  - Backend: Write integration tests for new `/api/statistics` endpoint before implementation
  - Frontend: Manual browser testing for DOM updates and refresh behavior
  - Tests will verify: response format, atomic updates, error handling, synchronization with graph
- **Rationale**: The backend API endpoint is testable via pytest integration tests. Frontend JavaScript will be tested manually in browser for visual behavior (no flickering, smooth updates) since the project doesn't currently have JavaScript unit test infrastructure.

### Integration & Contract Testing - ✓ PASS

- **Status**: Integration tests required for statistics API
- **Plan**:
  - Add contract tests for `/api/statistics` endpoint response schema
  - Add integration tests for end-to-end refresh flow (DB → API → JSON response)
  - Verify time-based calculations (today, week, month boundaries)
- **Rationale**: Statistics calculation involves database queries and time-based logic that must be tested end-to-end. Contract tests ensure the API response format remains stable for the JavaScript client.

### Pragmatic Simplicity - ✓ PASS

- **Status**: Design follows YAGNI and reuses existing patterns
- **Plan**:
  - Reuse existing `compute_statistics()` function from `src/dashboard/stats.py`
  - Reuse existing auto-refresh pattern from `graph.js` (setInterval polling)
  - Create minimal new endpoint `/api/statistics` that returns JSON version of current statistics
  - Update DOM elements directly without introducing new frameworks
- **Rationale**: No new abstractions needed. The graph auto-refresh pattern is proven and simple. Statistics calculation logic already exists. The implementation adds ~50 lines of JavaScript and ~20 lines of Python.

**Constitution Compliance**: ✅ ALL GATES PASS - Feature aligns with all constitution principles

## Project Structure

### Documentation (this feature)

```text
specs/004-statistics-refresh/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
# Web application structure (Python backend + JavaScript frontend)
src/
├── dashboard/
│   ├── app.py                  # Flask app factory
│   ├── routes.py               # Routes (add /api/statistics endpoint)
│   ├── stats.py                # Statistics calculation (existing, reused)
│   ├── templates/
│   │   ├── base.html           # Base template (no changes)
│   │   └── index.html          # Dashboard template (no changes to structure)
│   └── static/
│       ├── graph.js            # Graph auto-refresh (existing, reference pattern)
│       ├── stats.js            # NEW: Statistics auto-refresh logic
│       └── style.css           # Styles (no changes expected)
├── storage/
│   ├── repository.py           # Data access (existing, reused)
│   └── models.py               # Data models (existing, reused)
└── proxy/                      # Proxy addon (no changes)

tests/
├── contract/                   # NEW: Add API contract tests for /api/statistics
├── integration/                # NEW: Add integration tests for statistics endpoint
└── unit/                       # Existing unit tests (no changes)
```

**Structure Decision**: Using existing web application structure. The feature adds one new backend endpoint (`/api/statistics` in `routes.py`), one new JavaScript file (`static/stats.js` for refresh logic), and updates the HTML template to load the new script. Backend reuses existing `compute_statistics()` function and Repository pattern. Frontend follows the same polling pattern established by `graph.js`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations - table not needed*

---

## Phase 1 Complete: Design & Contracts

**Status**: ✅ Complete
**Date**: 2025-11-22

### Artifacts Generated

1. **research.md** - Technical research and design decisions
2. **data-model.md** - Data structures and API response format (reuses existing `LoginStatistics`)
3. **contracts/api-statistics.openapi.yaml** - OpenAPI 3.0 contract for `/api/statistics` endpoint
4. **quickstart.md** - Developer implementation guide with test-first workflow
5. **CLAUDE.md** - Updated agent context with new technologies

### Constitution Re-Check (Post-Design)

**Test-First Development (TDD)** - ✅ PASS
- Quickstart guide includes contract tests (write first, watch fail)
- Integration tests for end-to-end flow
- Manual browser testing checklist for frontend behavior
- No violations

**Integration & Contract Testing** - ✅ PASS
- OpenAPI contract defined in `contracts/api-statistics.openapi.yaml`
- Contract tests in quickstart verify schema compliance
- Integration tests verify DB → API → JSON flow
- No violations

**Pragmatic Simplicity** - ✅ PASS
- Reuses existing `LoginStatistics` model (no new entities)
- Reuses existing `compute_statistics()` function
- Follows existing `graph.js` auto-refresh pattern
- Minimal implementation (~50 lines JS, ~20 lines Python)
- No violations

**Final Constitution Compliance**: ✅ ALL GATES PASS

---

## Next Steps

This planning phase is complete. To proceed with implementation:

1. Run `/speckit.tasks` to generate the detailed task breakdown (tasks.md)
2. Follow test-first workflow from quickstart.md
3. Implement tasks in order (backend tests → backend → frontend → manual testing)
4. Commit after each logical task completion
5. Create PR when all tasks complete and tests pass
