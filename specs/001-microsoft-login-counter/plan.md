# Implementation Plan: Microsoft Login Event Counter

**Branch**: `001-microsoft-login-counter` | **Date**: 2025-11-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-microsoft-login-counter/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a local HTTP proxy that monitors network traffic to detect Microsoft authentication events (login.microsoftonline.com) without browser extensions. The proxy inspects HTTP metadata (302 redirects with success parameters) to count login events, stores data in SQLite, and serves a web dashboard for viewing statistics (daily/weekly/monthly counts) and login history. The solution preserves end-to-end encryption by avoiding TLS decryption, operates as a standalone local service, and provides basic operational logging for troubleshooting.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: mitmproxy 10.0+ (HTTP proxy), Flask 3.0+ (web dashboard), PyYAML 6.0+ (configuration)
**Storage**: SQLite 3.40+ (Python stdlib sqlite3 module)
**Testing**: pytest 7.4+ with pytest-mock (contract/integration/unit tests)
**Target Platform**: Linux/macOS/Windows desktop - local proxy service with embedded web dashboard
**Project Type**: Single Python application (proxy + dashboard in one process)
**Performance Goals**: <100ms proxy latency per request (SC-007), login detection within 2 seconds (SC-001)
**Constraints**: HTTP metadata monitoring only (no TLS decryption per FR-016/FR-017), no browser extensions (FR-013), single-user local deployment
**Scale/Scope**: Single user, 90+ days of login history (SC-004), ~100-1000 login events expected per user

**Detection Strategy**: Monitor HTTP CONNECT to login.microsoftonline.com + OAuth callback redirect patterns (code=/state= parameters) within 60-second time window

See [research.md](./research.md) for detailed technology selection rationale.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Test-First Development (TDD)

**Status**: ✅ COMPLIANT

**Plan**:
- Contract tests FIRST for HTTP 302 redirect detection pattern
- Integration tests FIRST for proxy traffic monitoring + login counting
- Unit tests FIRST for SQLite operations and time-based statistics aggregation
- Tests will fail initially, implementation follows to make them pass

**Evidence**: Plan mandates test-first workflow in Phase 1 contracts and Phase 2 tasks

### Principle II: Integration & Contract Testing

**Status**: ✅ COMPLIANT

**Requirements Met**:
- Contract tests for Microsoft authentication flow detection (HTTP 302 redirects from login.microsoftonline.com)
- Integration tests for proxy monitoring → detection → database persistence → dashboard display
- Data persistence tests for SQLite transaction integrity across proxy restarts
- Full user journey tests: authentication event → counter increment → statistics display

**Critical Paths Covered**:
1. HTTP metadata inspection (status codes, headers) without TLS decryption
2. Login event detection via redirect pattern matching
3. SQLite write/read operations with transaction support
4. Web dashboard serving and data retrieval
5. Time-based aggregation (daily/weekly/monthly statistics)

### Principle III: Pragmatic Simplicity

**Status**: ✅ COMPLIANT

**Simplicity Choices**:
- Single service combining proxy + web dashboard (no microservices)
- SQLite for storage (no separate database server)
- HTTP metadata monitoring only (no TLS decryption complexity)
- Local deployment (no distributed architecture)
- Basic operational logging (no elaborate observability stack)
- Direct implementation (no unnecessary abstractions or patterns)

**YAGNI Applied**:
- No multi-user support (single user sufficient)
- No export/import features (not in MVP requirements)
- No historical data analytics beyond daily/weekly/monthly (keep it simple)
- No real-time notifications (not requested)

**Complexity Justification**: None required - architecture is appropriately simple for requirements

### Gate Result: ✅ PASS - All principles aligned, proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── proxy/
│   ├── __init__.py
│   ├── addon.py              # mitmproxy addon for login detection
│   ├── detector.py           # Login event detection logic
│   └── session_tracker.py    # Track CONNECT → callback sequences
├── storage/
│   ├── __init__.py
│   ├── database.py           # SQLite connection & schema management
│   └── repository.py         # CRUD operations for login_events
├── dashboard/
│   ├── __init__.py
│   ├── app.py                # Flask application
│   ├── routes.py             # HTTP endpoints
│   └── templates/
│       ├── index.html        # Statistics page
│       └── history.html      # Event history page
├── config/
│   ├── __init__.py
│   └── loader.py             # YAML configuration loading
├── logging/
│   ├── __init__.py
│   └── setup.py              # Logging configuration
└── main.py                   # Entry point: starts proxy + dashboard

tests/
├── contract/
│   ├── test_redirect_detection.py      # HTTP 302 patterns
│   └── test_oauth_callback_patterns.py # OAuth parameter validation
├── integration/
│   ├── test_proxy_to_database.py       # Proxy → detect → store flow
│   ├── test_dashboard_api.py           # Dashboard endpoints + DB queries
│   └── test_persistence.py             # SQLite across restarts
└── unit/
    ├── test_session_tracker.py         # CONNECT tracking logic
    ├── test_statistics.py              # Time-based aggregations
    └── test_database.py                # SQLite operations

config.yaml                   # Configuration file (user-editable)
requirements.txt              # Python dependencies
pytest.ini                    # pytest configuration
README.md                     # Setup instructions
```

**Structure Decision**: Single Python project following standard src/ layout. Proxy logic isolated in `src/proxy/`, dashboard in `src/dashboard/`, storage abstraction in `src/storage/`. Tests mirror source structure with contract/integration/unit hierarchy per constitution. No separate backend/frontend - Flask serves HTML templates directly (server-side rendering).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
