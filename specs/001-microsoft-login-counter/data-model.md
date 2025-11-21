# Data Model: Microsoft Login Event Counter

**Feature**: 001-microsoft-login-counter
**Date**: 2025-11-21
**Storage**: chrome.storage.local (primary), IndexedDB (fallback)

## Entities

### LoginEvent

Represents a single successful authentication at login.microsoftonline.com.

**Storage Key**: `loginEvents` (array of LoginEvent objects)

**Fields**:

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| `id` | string (UUID v4) | Yes | Unique identifier for this login event | Non-empty, unique |
| `timestamp` | number (Unix milliseconds) | Yes | When the login occurred (UTC) | Positive integer, <= Date.now() |
| `url` | string | Yes | The login.microsoftonline.com URL that triggered detection | Starts with "https://login.microsoftonline.com/" |
| `detected_at` | number (Unix milliseconds) | Yes | When the extension detected this login | Positive integer, <= Date.now() |

**Example**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": 1700000000000,
  "url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?code=ABC123",
  "detected_at": 1700000000123
}
```

**Constraints**:
- `timestamp` and `detected_at` should be within 2 seconds of each other (detection latency requirement)
- Events stored in chronological order (oldest first)
- No duplicates (same `timestamp` within 1 second = same login)

**Lifecycle**:
1. **Created**: When authentication success detected at login.microsoftonline.com
2. **Stored**: Immediately persisted to chrome.storage.local
3. **Queried**: For statistics and history views
4. **Retained**: Indefinitely unless user manually deletes

---

### LoginStatistics

Aggregated counts of login events for time periods. Computed on-demand, not stored.

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `today` | number | Count of logins today (midnight to midnight, local timezone) |
| `thisWeek` | number | Count of logins this week (Monday to Sunday, local timezone) |
| `thisMonth` | number | Count of logins this month (1st to last day, local timezone) |
| `total` | number | Total count of all login events |
| `periodStart` | Date | Start of the aggregation period (for display) |
| `periodEnd` | Date | End of the aggregation period (for display) |

**Example**:
```json
{
  "today": 3,
  "thisWeek": 10,
  "thisMonth": 42,
  "total": 156,
  "periodStart": "2025-11-21T00:00:00Z",
  "periodEnd": "2025-11-21T23:59:59Z"
}
```

**Computation**:
```typescript
function computeStatistics(events: LoginEvent[]): LoginStatistics {
  const now = new Date();
  const todayStart = startOfDay(now);
  const weekStart = startOfWeek(now); // Monday
  const monthStart = startOfMonth(now);

  return {
    today: events.filter(e => new Date(e.timestamp) >= todayStart).length,
    thisWeek: events.filter(e => new Date(e.timestamp) >= weekStart).length,
    thisMonth: events.filter(e => new Date(e.timestamp) >= monthStart).length,
    total: events.length,
    periodStart: todayStart,
    periodEnd: endOfDay(now)
  };
}
```

---

### StorageMetadata

Metadata about stored data for quota management.

**Storage Key**: `metadata`

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Data schema version (for migrations) |
| `eventCount` | number | Total number of stored events |
| `oldestEvent` | number (Unix ms) | Timestamp of oldest event |
| `newestEvent` | number (Unix ms) | Timestamp of newest event |
| `storageBytes` | number | Approximate storage used in bytes |
| `lastCleanup` | number (Unix ms) | When last maintenance was performed |

**Example**:
```json
{
  "version": "1.0.0",
  "eventCount": 156,
  "oldestEvent": 1680000000000,
  "newestEvent": 1700000000000,
  "storageBytes": 31200,
  "lastCleanup": 1700000000000
}
```

**Purpose**: Monitor storage usage, trigger migrations to IndexedDB if needed

---

## Storage Schema

### chrome.storage.local

Primary storage using chrome.storage.local API.

**Keys**:
- `loginEvents`: Array of LoginEvent objects (sorted by timestamp)
- `metadata`: StorageMetadata object

**Quota**: 10MB (chrome.storage.local limit)

**Estimated Capacity**:
- Each LoginEvent: ~200 bytes (JSON serialized)
- 10MB = ~50,000 events
- At 10 logins/day = ~13 years of data

**Access Patterns**:
```typescript
// Write new event
await chrome.storage.local.get(['loginEvents', 'metadata']);
events.push(newEvent);
await chrome.storage.local.set({ loginEvents: events, metadata: updatedMeta });

// Read for statistics
const { loginEvents } = await chrome.storage.local.get('loginEvents');
const stats = computeStatistics(loginEvents);

// Read for history view
const { loginEvents } = await chrome.storage.local.get('loginEvents');
const recentEvents = loginEvents.slice(-100); // Last 100 events
```

---

### IndexedDB (Fallback)

Used only if chrome.storage.local quota exceeded.

**Database**: `MicrosoftLoginCounter`
**Version**: 1

**Object Store**: `loginEvents`
- **keyPath**: `id`
- **Indexes**:
  - `timestamp` (unique: false) - for time-range queries
  - `detected_at` (unique: false) - for debugging

**Migration Trigger**:
- When `metadata.storageBytes` > 8MB (80% of quota)
- Prompt user for permission
- Copy all events to IndexedDB
- Clear chrome.storage.local except metadata
- Set `metadata.usesIndexedDB = true`

---

## Data Validation Rules

### On Event Creation
1. **timestamp** must be valid Unix milliseconds (> 0, <= Date.now())
2. **url** must start with "https://login.microsoftonline.com/"
3. **id** must be unique (UUID v4 format)
4. **detected_at** must be within 5 seconds of timestamp (detection latency tolerance)

### On Event Storage
1. **No duplicates**: Reject if event with timestamp within 1 second exists (cooldown logic)
2. **Chronological order**: Events stored in timestamp order
3. **Quota check**: Reject if storage would exceed quota (trigger migration or cleanup)

### On Query
1. **Time period validation**: Ensure start < end for date range queries
2. **Limit validation**: History view limited to prevent memory issues (max 10,000 events loaded at once)

---

## State Transitions

### LoginEvent Lifecycle

```
[Authentication Success]
         ↓
   [Event Detected] → Create LoginEvent
         ↓
   [Cooldown Check] → Within 1s? → Discard (duplicate)
         ↓ No
   [Validation] → Invalid? → Log error, discard
         ↓ Valid
   [Storage Write] → Success → Event persisted
         ↓
   [Query/Display] → Used in statistics and history
         ↓
   [Retention] → Kept indefinitely (user deletion only)
```

---

## Relationships

```
LoginEvent (many) → LoginStatistics (computed)
- Statistics aggregate multiple LoginEvent records
- No stored relationship (computed on-demand)

LoginEvent (many) → StorageMetadata (one)
- Metadata tracks count and bounds of LoginEvents
- Updated atomically with event writes
```

---

## Performance Considerations

### Read Performance
- **Statistics computation**: O(n) where n = total events
  - Optimized by early filtering (only scan relevant time range)
  - For 1000 events, < 10ms on modern hardware

- **History view**: O(1) for recent events (last 100)
  - Use array slicing, no full scan needed

### Write Performance
- **New event**: O(1) append + O(1) metadata update
  - chrome.storage.local write: ~5-10ms
  - No indexes to update (chronological append)

### Storage Growth
- **Linear growth**: 200 bytes per event
- **Migration threshold**: 8MB (40,000 events)
- **Cleanup strategy**: None needed (indefinite retention per spec)

---

## Migration Strategy

### Version 1.0.0 → Future Versions

If data model changes:
1. Check `metadata.version`
2. Apply transformation to each LoginEvent
3. Update `metadata.version`
4. Persist updated data

Example migration (hypothetical):
```typescript
async function migrateV1toV2() {
  const { loginEvents, metadata } = await chrome.storage.local.get();

  if (metadata.version === '1.0.0') {
    // Add new field to each event
    const migratedEvents = loginEvents.map(e => ({
      ...e,
      newField: computeNewField(e)
    }));

    await chrome.storage.local.set({
      loginEvents: migratedEvents,
      metadata: { ...metadata, version: '2.0.0' }
    });
  }
}
```
