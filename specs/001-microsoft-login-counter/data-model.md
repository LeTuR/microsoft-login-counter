# Data Model: Microsoft Login Event Counter

**Feature**: 001-microsoft-login-counter
**Date**: 2025-11-21
**Storage**: SQLite 3.40+ (local database file)

## Entities

### LoginEvent

Represents a single successful Microsoft authentication detected by the proxy.

**Table**: `login_events`

**Fields**:

| Column | Type | Nullable | Description | Constraints |
|--------|------|----------|-------------|-------------|
| `id` | INTEGER | No | Auto-incrementing primary key | PRIMARY KEY AUTOINCREMENT |
| `timestamp` | TEXT | No | ISO 8601 UTC timestamp: "2025-11-21T14:30:00Z" | NOT NULL |
| `unix_timestamp` | INTEGER | No | Unix epoch (seconds) for efficient queries | NOT NULL, >= 0 |
| `detected_via` | TEXT | No | Detection method: "connect_sequence", "http_redirect", "oauth_callback" | NOT NULL |

**Indexes**:
- `idx_login_events_unix_time` on `unix_timestamp` - for fast time-range filtering

**Example Row**:
```sql
INSERT INTO login_events (timestamp, unix_timestamp, detected_via)
VALUES ('2025-11-21T14:30:00Z', 1732198200, 'connect_sequence');
```

**Constraints**:
- `unix_timestamp` derived from `timestamp` (must match)
- Events stored in chronological order (enforced by AUTOINCREMENT id)
- No explicit duplicate prevention (per spec: count every authentication separately)

**Lifecycle**:
1. **Created**: When proxy detects successful authentication via CONNECT + callback pattern
2. **Inserted**: Transaction-protected write to SQLite
3. **Queried**: For statistics aggregation and history display
4. **Retained**: Indefinitely unless user deletes database file

---

### ProxyMetadata

Stores proxy configuration and operational metadata.

**Table**: `proxy_metadata`

**Fields**:

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `key` | TEXT | No | Metadata key | PRIMARY KEY |
| `value` | TEXT | No | Metadata value (string-encoded) | NOT NULL |

**Standard Keys**:
- `schema_version`: Database schema version (e.g., "1.0.0")
- `first_event_date`: ISO 8601 timestamp of first recorded event
- `last_event_date`: ISO 8601 timestamp of most recent event
- `total_events`: String representation of total event count
- `proxy_start_time`: When proxy was first started

**Example Rows**:
```sql
INSERT INTO proxy_metadata (key, value) VALUES
  ('schema_version', '1.0.0'),
  ('first_event_date', '2025-11-21T10:00:00Z'),
  ('total_events', '156');
```

**Purpose**: Track database metadata, support schema migrations, provide operational insights

---

### LoginStatistics (Computed)

Aggregated counts for time periods. Not stored - computed on-demand via SQL queries.

**Structure** (Python dataclass):
```python
@dataclass
class LoginStatistics:
    today_count: int
    week_count: int
    month_count: int
    total_count: int
    period_start: datetime
    period_end: datetime
```

**Computation Queries**:

```sql
-- Today's logins (midnight to midnight, UTC)
SELECT COUNT(*) FROM login_events
WHERE unix_timestamp >= ? AND unix_timestamp < ?;

-- This week's logins (Monday to Sunday, UTC)
SELECT COUNT(*) FROM login_events
WHERE unix_timestamp >= ? AND unix_timestamp < ?;

-- This month's logins (1st to last day, UTC)
SELECT COUNT(*) FROM login_events
WHERE unix_timestamp >= ? AND unix_timestamp < ?;

-- Total logins
SELECT COUNT(*) FROM login_events;
```

**Example Response**:
```json
{
  "today_count": 3,
  "week_count": 10,
  "month_count": 42,
  "total_count": 156,
  "period_start": "2025-11-21T00:00:00Z",
  "period_end": "2025-11-21T23:59:59Z"
}
```

---

## SQLite Schema

### Full Schema DDL

```sql
-- Login events table
CREATE TABLE login_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    unix_timestamp INTEGER NOT NULL,
    detected_via TEXT NOT NULL
);

CREATE INDEX idx_login_events_unix_time ON login_events(unix_timestamp);

-- Proxy metadata table
CREATE TABLE proxy_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Initialize metadata
INSERT INTO proxy_metadata (key, value) VALUES
    ('schema_version', '1.0.0'),
    ('created_at', datetime('now'));
```

### Database File Location

**Path**: `~/.microsoft-login-counter/events.db` (configurable via config.yaml)

**Permissions**: 0600 (owner read/write only)

**Size Estimates**:
- Each event: ~100 bytes (row + index overhead)
- 1000 events: ~100 KB
- 10,000 events: ~1 MB
- 100,000 events (years of data): ~10 MB

---

## Data Validation Rules

### On Event Creation

1. **timestamp**: Must be valid ISO 8601 format
2. **unix_timestamp**: Must be positive integer, derived from timestamp
3. **detected_via**: Must be one of allowed values ("connect_sequence", "http_redirect", "oauth_callback")
4. **Timezone**: All timestamps stored in UTC, converted to local for display

### On Event Storage

1. **Transaction Protected**: Use SQLite transactions for atomicity
2. **No Explicit Deduplication**: Per spec (FR-012), count every authentication separately
3. **Integrity**: FOREIGN KEY constraints enforced (none needed for flat schema)

### On Query

1. **Time Range Validation**: start < end for date filters
2. **Limit Enforcement**: History queries limited to reasonable page sizes (default: 100 events)
3. **Prepared Statements**: All queries use parameterized statements (SQL injection prevention)

---

## State Transitions

### LoginEvent Lifecycle

```
[Proxy Detects Pattern]
  - CONNECT to login.microsoftonline.com
  - Followed by OAuth callback within 60s
         ↓
[Validation]
  - Check timestamp validity
  - Validate detection method
         ↓ Valid
[Database Write]
  - BEGIN TRANSACTION
  - INSERT INTO login_events
  - UPDATE proxy_metadata (last_event_date, total_events)
  - COMMIT
         ↓ Success
[Event Persisted]
  - Available for queries immediately
  - Survives proxy restart
         ↓
[Query/Display]
  - Dashboard aggregates for statistics
  - History view shows chronological list
         ↓
[Retention]
  - Kept indefinitely in database file
  - User can delete database to clear data
```

---

## Relationships

```
login_events (many) → LoginStatistics (computed)
  - Statistics computed via SQL aggregation queries
  - No stored relationship

login_events (many) → proxy_metadata (one)
  - Metadata tracks bounds and count of events
  - Updated transactionally with event inserts
```

---

## Performance Considerations

### Read Performance

**Statistics Queries**:
- Time-based filtering uses indexed `unix_timestamp` column
- Each aggregation query: O(log n) index scan + O(k) result scan (k = matching rows)
- For 10,000 events with daily filter (~10 matches): < 1ms

**History Queries**:
- Recent N events: `SELECT * FROM login_events ORDER BY id DESC LIMIT N`
- Uses primary key index: O(1) for lookup + O(N) for scan
- For 100 events: < 1ms

### Write Performance

**New Event Insert**:
- Single INSERT with transaction: ~1-5ms on SSD
- Index update (unix_timestamp): O(log n) - negligible for <100k events
- Metadata update: Key-value update, O(1)

**Transaction Overhead**:
- BEGIN/COMMIT add ~0.5ms per write
- Acceptable for low-frequency writes (1-10 logins per day)

### Storage Growth

**Linear Growth**: ~100 bytes per event
- 10 logins/day = ~365 KB/year
- 100 logins/day = ~3.65 MB/year
- Database file will remain manageable (<100 MB) for years

**No Cleanup Needed**: Indefinite retention per spec (Assumption 5)

**Vacuum Strategy**: Optional periodic `VACUUM` to reclaim space (not required for MVP)

---

## Migration Strategy

### Version 1.0.0 → Future Versions

Schema migrations handled via `proxy_metadata.schema_version` check on startup.

**Migration Pattern**:
```python
def migrate_schema(db: sqlite3.Connection):
    current_version = get_metadata(db, 'schema_version')

    if current_version == '1.0.0':
        # Migrate to 1.1.0 (hypothetical: add 'source_ip' column)
        db.execute('ALTER TABLE login_events ADD COLUMN source_ip TEXT')
        set_metadata(db, 'schema_version', '1.1.0')
        db.commit()

    # Add more migrations as needed
```

**Migration Types**:
- **Additive**: Add columns with defaults (backward compatible)
- **Transformative**: Create new table, copy data, drop old (requires downtime)
- **Backfill**: Update existing rows with computed values

---

## Access Patterns

### Common Queries

**1. Today's Login Count**:
```python
today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0)
today_end = today_start + timedelta(days=1)

cursor.execute('''
    SELECT COUNT(*) FROM login_events
    WHERE unix_timestamp >= ? AND unix_timestamp < ?
''', (today_start.timestamp(), today_end.timestamp()))
```

**2. Recent 100 Events**:
```python
cursor.execute('''
    SELECT timestamp, detected_via FROM login_events
    ORDER BY id DESC LIMIT 100
''')
```

**3. Events in Date Range**:
```python
cursor.execute('''
    SELECT * FROM login_events
    WHERE unix_timestamp >= ? AND unix_timestamp < ?
    ORDER BY unix_timestamp ASC
''', (start_ts, end_ts))
```

**4. First and Last Event**:
```python
cursor.execute('SELECT MIN(unix_timestamp), MAX(unix_timestamp) FROM login_events')
```

---

## Security Considerations

### Data Protection

- **File Permissions**: Database file set to 0600 (owner only)
- **No Credentials**: Database does not store passwords or tokens
- **Local Only**: No network access, no data transmission
- **SQL Injection**: All queries use parameterized statements

### Privacy

Per spec Assumption 8, only these data points are stored:
- Event occurred (timestamp)
- Detection method (technical detail)
- **NOT stored**: User identity, credentials, auth tokens, session data, activity after login

---

## Testing Strategy

### Unit Tests

- Schema creation and migration logic
- Event validation (timestamp formats, detection methods)
- Statistics computation (time period calculations)
- Metadata operations (get/set)

### Integration Tests

- Full write flow: proxy → detector → database
- Query performance with 1000+ events
- Database persistence across connection close/reopen
- Transaction rollback on errors

### Contract Tests

- Schema matches expected structure
- Queries return expected result format
- Foreign key constraints enforced (if added later)

---

## Implementation Notes

### Python sqlite3 Usage

```python
import sqlite3
from datetime import datetime, timezone

# Connection management
conn = sqlite3.connect('~/.microsoft-login-counter/events.db')
conn.row_factory = sqlite3.Row  # Dict-like row access

# Insert event (transactional)
def record_login_event(timestamp: datetime, method: str):
    with conn:  # Auto-commit on success, rollback on exception
        conn.execute('''
            INSERT INTO login_events (timestamp, unix_timestamp, detected_via)
            VALUES (?, ?, ?)
        ''', (timestamp.isoformat(), int(timestamp.timestamp()), method))

        # Update metadata
        conn.execute('''
            INSERT OR REPLACE INTO proxy_metadata (key, value)
            VALUES ('last_event_date', ?)
        ''', (timestamp.isoformat(),))

# Query statistics
def get_today_count() -> int:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    today_end = today_start + timedelta(days=1)

    cursor = conn.execute('''
        SELECT COUNT(*) as count FROM login_events
        WHERE unix_timestamp >= ? AND unix_timestamp < ?
    ''', (int(today_start.timestamp()), int(today_end.timestamp())))

    return cursor.fetchone()['count']
```

### Thread Safety

SQLite connections are NOT thread-safe. For proxy + dashboard in one process:
- **Option 1**: Single connection, mutex-protected access
- **Option 2**: Separate connections (one for proxy writes, one for dashboard reads)
- **Option 3**: Connection pool with max size = 1

Recommendation: Option 2 (separate connections) for simplicity.

---

## Next Steps

- [x] Data model documented
- [ ] Generate SQLite schema init script (`src/storage/schema.sql`)
- [ ] Implement database.py with connection management
- [ ] Implement repository.py with CRUD operations
- [ ] Write unit tests for database operations
