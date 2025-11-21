# Research: Microsoft Login Event Counter

**Date**: 2025-11-21
**Feature**: 001-microsoft-login-counter
**Purpose**: Resolve technical unknowns from plan.md Technical Context

## Research Questions

### 1. Language/Runtime Selection

**Decision**: Python 3.11+

**Rationale**:
- **Proxy Libraries**: Python has mature HTTP proxy libraries (`mitmproxy`) with excellent HTTP/HTTPS handling
- **Web Framework**: Flask provides lightweight dashboard serving without complexity
- **SQLite Support**: Built-in `sqlite3` module, no additional dependencies
- **Cross-platform**: Runs on Linux/macOS/Windows without modification
- **Rapid Development**: Faster iteration for MVP, excellent for scripting and network tools
- **Logging**: Built-in `logging` module meets basic operational logging needs
- **HTTP Inspection**: mitmproxy provides event hooks for observing HTTP metadata without TLS decryption

**Alternatives Considered**:
- **Node.js 18+**: Strong async I/O for proxy, but less mature HTTP proxy ecosystem compared to Python's mitmproxy
- **Go 1.21+**: Excellent performance and concurrency, but requires more boilerplate for simple dashboard
- **Rust 1.75+**: Best performance but significantly steeper learning curve, overkill for single-user tool

### 2. HTTP Proxy Library

**Decision**: `mitmproxy` library (programmatic API)

**Rationale**:
- **HTTP Metadata Access**: Can inspect HTTP status codes and headers WITHOUT TLS decryption using transparent/regular proxy mode
- **Event-based Architecture**: Provides hooks for `request`, `response`, `http_connect` events
- **Mature & Stable**: Battle-tested library used for security testing and network analysis
- **No MITM Required for Our Use Case**: Can monitor CONNECT method and subsequent redirects without full decryption
- **Python Native**: Pure Python library, integrates cleanly with Flask/SQLite
- **Addon System**: Clean architecture for adding custom logic

**Implementation Approach**:
```python
from mitmproxy import http
from mitmproxy.tools.main import mitmdump

class LoginDetectorAddon:
    def response(self, flow: http.HTTPFlow):
        # Monitor responses from login.microsoftonline.com
        if "login.microsoftonline.com" in flow.request.host:
            if flow.response.status_code == 302:
                location = flow.response.headers.get("Location", "")
                if self.is_success_redirect(location):
                    self.record_login_event()

    def is_success_redirect(self, url: str) -> bool:
        # Check for OAuth success parameters (code=, state=)
        return "code=" in url or "/auth/callback" in url
```

**Alternatives Considered**:
- **pproxy**: Simpler but less control over HTTP metadata inspection
- **Custom socket proxy**: Too low-level, reinventing the wheel
- **Browser automation (Selenium)**: Violates "no browser extension" requirement, still needs browser control

### 3. Web Dashboard Framework

**Decision**: Flask 3.0+

**Rationale**:
- **Lightweight**: Minimal boilerplate, perfect for simple dashboard (3-4 endpoints)
- **Built-in Server**: Development server sufficient for local single-user deployment
- **Template Engine**: Jinja2 for HTML rendering (statistics page, history list)
- **Static Files**: Easy serving of CSS/JS for basic UI
- **SQLite Integration**: Trivial to query database and render results
- **No Build Step**: Pure server-side rendering, no complex frontend build pipeline
- **Same Process**: Can run in same Python process as proxy

**Dashboard Endpoints**:
- `GET /` - Statistics page (today/week/month counts)
- `GET /history` - Login event history (chronological list)
- `GET /api/stats` - JSON API for statistics (optional, for future enhancement)
- `GET /api/events` - JSON API for event list (optional)

**Alternatives Considered**:
- **FastAPI**: Overkill for simple read-only dashboard, async not needed for low-traffic single-user app
- **Django**: Too heavyweight, brings ORM and admin interface we don't need
- **Static HTML + JSON files**: No dynamic queries, hard to aggregate statistics efficiently

### 4. Testing Framework

**Decision**: `pytest` 7.4+ with `pytest-mock`

**Rationale**:
- **Industry Standard**: De facto Python testing framework
- **Fixtures**: Clean setup/teardown for SQLite test databases
- **Parametrized Tests**: Easily test multiple redirect URL patterns
- **Mocking**: `pytest-mock` for mocking HTTP flows without live traffic
- **Integration Support**: Can spawn proxy subprocess for integration tests
- **Contract Testing**: Can use `pytest` with recorded HTTP fixtures from mitmproxy

**Test Structure**:
```
tests/
├── contract/
│   └── test_redirect_detection.py  # HTTP 302 redirect pattern matching
├── integration/
│   ├── test_proxy_flow.py          # Proxy start → detect → store → display
│   └── test_database_persistence.py # SQLite across restarts
└── unit/
    ├── test_event_counter.py        # Login counting logic
    └── test_statistics.py           # Time-based aggregation
```

**Alternatives Considered**:
- **unittest**: Python stdlib, but less ergonomic than pytest
- **nose2**: Declining in popularity, less active development
- **Robot Framework**: Too heavyweight for simple unit/integration tests

### 5. HTTP Metadata Detection Without TLS Decryption

**Decision**: Monitor HTTP CONNECT method + track redirect chains

**Rationale**:
- **CONNECT Tunnel Observation**: When browser initiates HTTPS to `login.microsoftonline.com`, proxy sees `CONNECT login.microsoftonline.com:443`
- **OAuth Redirect Flow**: Microsoft OAuth redirects to callback URL (different domain), which generates new CONNECT or HTTP request
- **Observable Pattern**:
  1. `CONNECT login.microsoftonline.com:443` → User authenticating
  2. Within 5-60 seconds: `CONNECT app.example.com:443` OR `GET http://localhost:port/callback?code=...`
  3. Redirect timing + callback URL pattern = successful authentication

**Detection Strategy**:
```python
# Track active authentication sessions
sessions = {}  # {session_id: timestamp}

def http_connect(flow):
    if "login.microsoftonline.com" in flow.request.host:
        session_id = flow.client_conn.id
        sessions[session_id] = time.time()

def request(flow):
    # Check if this is a callback request after Microsoft login
    if "/callback" in flow.request.path or "/auth" in flow.request.path:
        if "code=" in flow.request.url or "token=" in flow.request.url:
            # Check if recent login.microsoftonline.com CONNECT
            session_id = flow.client_conn.id
            if session_id in sessions:
                elapsed = time.time() - sessions[session_id]
                if elapsed < 60:  # Within 60 seconds
                    record_login_event()
                    del sessions[session_id]
```

**Limitations & Mitigations**:
- **False Negatives**: If entire flow is within encrypted tunnel to single domain, detection may fail
  - Mitigation: Most Microsoft OAuth flows redirect to different callback domain (observable)
- **False Positives**: Non-authentication CONNECT to login.microsoftonline.com
  - Mitigation: Only count when followed by callback with OAuth parameters within time window

**Alternatives Considered**:
- **Full TLS decryption**: Violates FR-017 (no MITM), security/privacy risk, requires custom certificates
- **Deep packet inspection**: Still requires TLS decryption
- **Browser extension**: Violates FR-013 (no browser extensions) per company policy

### 6. SQLite Schema Design

**Decision**: Simple two-table schema with time-based indexes

**Schema**:
```sql
CREATE TABLE login_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,      -- ISO 8601 UTC: "2025-11-21T14:30:00Z"
    unix_timestamp INTEGER NOT NULL,  -- Unix epoch for efficient range queries
    detected_via TEXT NOT NULL    -- "http_redirect", "connect_sequence", etc.
);

CREATE INDEX idx_login_events_unix_time ON login_events(unix_timestamp);

CREATE TABLE proxy_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
-- Stores: schema_version, last_cleanup_date, first_event_date
```

**Rationale**:
- **Simplicity**: Two tables, minimal relationships
- **Time Queries**: Index on `unix_timestamp` for fast filtering by date ranges
- **ISO 8601**: Human-readable timestamps for debugging and display
- **Unix Epoch**: Fast integer comparisons for daily/weekly/monthly aggregation
- **Detection Method**: Track how each event was detected for troubleshooting
- **No Over-normalization**: Flat structure, no unnecessary joins

**Query Examples**:
```sql
-- Today's logins
SELECT COUNT(*) FROM login_events
WHERE unix_timestamp >= ? AND unix_timestamp < ?

-- This week's logins
SELECT COUNT(*) FROM login_events
WHERE unix_timestamp >= ? AND unix_timestamp < ?

-- Recent 100 events
SELECT timestamp, detected_via FROM login_events
ORDER BY id DESC LIMIT 100
```

**Alternatives Considered**:
- **Denormalized statistics table**: Premature optimization, compute aggregations on-demand
- **Separate users table**: Not needed (single user per deployment)
- **JSON column for metadata**: SQLite JSON support is available, but simple TEXT sufficient for key-value pairs

### 7. Proxy Deployment & Configuration

**Decision**: Single Python script with YAML configuration file

**Rationale**:
- **Simple Deployment**: `python login_counter_proxy.py` starts both proxy and dashboard in separate threads
- **Configuration File**: `config.yaml` for proxy port, dashboard port, database path, log level
- **Logging to File**: Rotating log files in `~/.microsoft-login-counter/logs/`
- **Database Location**: `~/.microsoft-login-counter/events.db` (SQLite file)
- **Graceful Shutdown**: Signal handling (SIGINT/SIGTERM) for clean database close

**Configuration Example**:
```yaml
proxy:
  port: 8080
  listen_address: 127.0.0.1

dashboard:
  port: 8081
  listen_address: 127.0.0.1

storage:
  database_path: ~/.microsoft-login-counter/events.db

logging:
  level: INFO
  log_dir: ~/.microsoft-login-counter/logs
  max_size_mb: 10
  backup_count: 5
```

**Browser Configuration**:
- User manually sets system or browser HTTP proxy to `localhost:8080`
- Instructions provided in quickstart.md for Chrome/Edge/Firefox/Safari/System-wide
- No automatic proxy configuration (PAC files) for simplicity

**Service Management (Optional)**:
- Systemd unit file for Linux
- Launchd plist for macOS
- NSSM wrapper for Windows service
- Not required for MVP, user can run manually

**Alternatives Considered**:
- **Docker container**: Adds complexity, requires Docker installation, overkill for simple local tool
- **System-level transparent proxy**: Requires root/admin privileges, too invasive
- **PAC file auto-config**: Complex, not needed for single-host deployment

## Technology Stack Summary

| Component | Choice | Version |
|-----------|--------|---------|
| **Language** | Python | 3.11+ |
| **Proxy Library** | mitmproxy | 10.0+ |
| **Web Framework** | Flask | 3.0+ |
| **Database** | SQLite | 3.40+ (Python stdlib) |
| **Testing** | pytest + pytest-mock | 7.4+ |
| **Logging** | Python logging module | stdlib |
| **Configuration** | PyYAML | 6.0+ |

## Implementation Roadmap

### Phase 1: Core Proxy & Detection (P1 - Critical)
1. SQLite schema creation and basic CRUD operations (TDD)
2. mitmproxy addon skeleton with event logging
3. CONNECT method tracking for login.microsoftonline.com
4. Callback detection logic with OAuth parameter matching
5. Event recording to SQLite with transaction support

### Phase 2: Web Dashboard (P2 - High)
1. Flask application with basic routing
2. Statistics endpoint (today/week/month counts via SQL aggregation)
3. History endpoint (chronological list with pagination)
4. Simple HTML templates with Jinja2 (no JavaScript framework needed)
5. Basic CSS for readable display

### Phase 3: Operations & Deployment (P3 - Medium)
1. Configuration file loading (YAML)
2. Logging configuration (file rotation, levels)
3. Graceful shutdown handling
4. Quickstart documentation with browser configuration steps
5. Error handling and user-friendly error messages

## Open Issues & Mitigations

### Issue 1: Detection Accuracy Without TLS Decryption

**Risk**: May miss logins if Microsoft changes OAuth flow or app callback is same-domain encrypted

**Mitigation**:
- Start with heuristic-based detection (CONNECT + callback timing)
- Add operational logging to track detection attempts
- User can manually verify via dashboard and logs
- Future enhancement: Optional TLS inspection mode with user consent

### Issue 2: Corporate Proxy Compatibility

**Risk**: If user's network has corporate proxy, our proxy may conflict or require chaining

**Mitigation**:
- Support upstream proxy configuration in config.yaml
- mitmproxy supports `--upstream-proxy` mode
- Document in quickstart.md how to chain proxies

### Issue 3: Browser Auto-Configuration

**Risk**: User must manually configure proxy settings, could be error-prone

**Mitigation**:
- Provide clear step-by-step instructions with screenshots
- Include verification step: "Visit http://localhost:8081 to confirm dashboard loads"
- Future enhancement: Provide PAC file generator script

## Next Steps

- [x] Research complete - all NEEDS CLARIFICATION resolved
- [ ] Update plan.md Technical Context with final decisions
- [ ] Generate data-model.md (SQLite schema details)
- [ ] Generate contracts/ (HTTP endpoints for dashboard API)
- [ ] Generate quickstart.md (user setup instructions)
- [ ] Update agent context with Python/Flask/mitmproxy stack
