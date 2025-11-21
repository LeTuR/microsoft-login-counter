# Browser API Contracts

**Feature**: 001-microsoft-login-counter
**Date**: 2025-11-21
**Purpose**: Define contracts with browser extension APIs

## chrome.webNavigation API

### onCompleted Event

**Contract**: Triggered when navigation to a URL completes successfully.

**Event Data**:
```typescript
interface WebNavigationOnCompletedDetails {
  tabId: number;           // ID of tab where navigation occurred
  url: string;             // Full URL of completed navigation
  processId: number;       // ID of process running the renderer for the tab
  frameId: number;         // 0 = main frame, >0 = subframe
  timeStamp: number;       // Time when navigation completed (milliseconds since epoch)
  documentLifecycle: 'prerender' | 'active'; // Document state
}
```

**Expected Behavior**:
- Fires AFTER page load completes (including redirects)
- Provides full final URL including query parameters
- `frameId: 0` indicates main frame navigation (what we monitor)
- `timeStamp` is when browser completed navigation

**Usage**:
```typescript
chrome.webNavigation.onCompleted.addListener(
  (details: WebNavigationOnCompletedDetails) => {
    if (details.frameId !== 0) return; // Only main frame
    if (isLoginSuccess(details.url)) {
      recordLoginEvent(details.timeStamp, details.url);
    }
  },
  { url: [{ hostEquals: 'login.microsoftonline.com' }] }
);
```

**Test Contract**:
```typescript
describe('webNavigation.onCompleted contract', () => {
  it('provides required fields', () => {
    const mockDetails = {
      tabId: 123,
      url: 'https://login.microsoftonline.com/common/oauth2/authorize',
      frameId: 0,
      timeStamp: Date.now()
    };

    expect(mockDetails).toHaveProperty('tabId');
    expect(mockDetails).toHaveProperty('url');
    expect(mockDetails).toHaveProperty('frameId');
    expect(mockDetails).toHaveProperty('timeStamp');
  });

  it('fires for main frame navigations', () => {
    // Verify frameId:0 events are received
  });

  it('provides accurate timestamp', () => {
    // Verify timeStamp is within reasonable range of Date.now()
  });
});
```

---

## chrome.storage.local API

### get() Method

**Contract**: Retrieves stored data by key(s).

**Signature**:
```typescript
function get(
  keys?: string | string[] | { [key: string]: any } | null
): Promise<{ [key: string]: any }>;
```

**Expected Behavior**:
- Returns Promise resolving to object with requested keys
- Missing keys return `undefined` in result object
- `null` or no argument returns all stored data
- Max read size: 10MB (quota limit)

**Usage**:
```typescript
const { loginEvents, metadata } = await chrome.storage.local.get(['loginEvents', 'metadata']);
// loginEvents: LoginEvent[] | undefined
// metadata: StorageMetadata | undefined
```

**Test Contract**:
```typescript
describe('storage.local.get contract', () => {
  it('returns requested keys', async () => {
    await chrome.storage.local.set({ test: 'value' });
    const result = await chrome.storage.local.get('test');
    expect(result.test).toBe('value');
  });

  it('returns undefined for missing keys', async () => {
    const result = await chrome.storage.local.get('nonexistent');
    expect(result.nonexistent).toBeUndefined();
  });

  it('supports multiple keys', async () => {
    await chrome.storage.local.set({ a: 1, b: 2 });
    const result = await chrome.storage.local.get(['a', 'b']);
    expect(result).toEqual({ a: 1, b: 2 });
  });
});
```

---

### set() Method

**Contract**: Stores data by key-value pairs.

**Signature**:
```typescript
function set(items: { [key: string]: any }): Promise<void>;
```

**Expected Behavior**:
- Overwrites existing keys
- Persists across browser restarts
- Rejects if quota exceeded
- Atomic write (all or nothing)
- Max write size: 10MB total

**Usage**:
```typescript
await chrome.storage.local.set({
  loginEvents: [...existingEvents, newEvent],
  metadata: updatedMetadata
});
```

**Test Contract**:
```typescript
describe('storage.local.set contract', () => {
  it('persists data', async () => {
    await chrome.storage.local.set({ test: 'value' });
    const result = await chrome.storage.local.get('test');
    expect(result.test).toBe('value');
  });

  it('overwrites existing keys', async () => {
    await chrome.storage.local.set({ test: 'old' });
    await chrome.storage.local.set({ test: 'new' });
    const result = await chrome.storage.local.get('test');
    expect(result.test).toBe('new');
  });

  it('rejects on quota exceeded', async () => {
    const largeData = { huge: 'x'.repeat(11 * 1024 * 1024) };
    await expect(chrome.storage.local.set(largeData)).rejects.toThrow();
  });
});
```

---

### getBytesInUse() Method

**Contract**: Returns storage space used by specified keys.

**Signature**:
```typescript
function getBytesInUse(keys?: string | string[] | null): Promise<number>;
```

**Expected Behavior**:
- Returns size in bytes
- `null` returns total storage used
- Used for quota monitoring

**Usage**:
```typescript
const bytesUsed = await chrome.storage.local.getBytesInUse();
if (bytesUsed > 8 * 1024 * 1024) {
  // Trigger migration to IndexedDB
}
```

**Test Contract**:
```typescript
describe('storage.local.getBytesInUse contract', () => {
  it('returns storage size', async () => {
    await chrome.storage.local.set({ test: 'value' });
    const bytes = await chrome.storage.local.getBytesInUse();
    expect(bytes).toBeGreaterThan(0);
  });

  it('tracks total size for null argument', async () => {
    await chrome.storage.local.set({ a: 'x', b: 'y' });
    const bytes = await chrome.storage.local.getBytesInUse(null);
    expect(bytes).toBeGreaterThan(0);
  });
});
```

---

## Login Detection Contract

### isLoginSuccess() Function

**Contract**: Determines if a URL represents successful Microsoft authentication.

**Signature**:
```typescript
function isLoginSuccess(url: string): boolean;
```

**URL Patterns Indicating Success**:

1. **Authorization code redirect**:
   ```
   https://login.microsoftonline.com/common/oauth2/v2.0/authorize?...&code=XXX
   ```

2. **Redirect away from login.microsoftonline.com**:
   - After successful auth, user redirected to app (e.g., outlook.office.com)
   - Detection: Navigation FROM login.microsoftonline.com TO different domain

3. **Successful token endpoint**:
   ```
   https://login.microsoftonline.com/common/oauth2/v2.0/token
   ```
   (POST request, detected via webNavigation completion after form submit)

**Implementation**:
```typescript
function isLoginSuccess(url: string): boolean {
  if (!url.startsWith('https://login.microsoftonline.com/')) {
    return false;
  }

  // Check for authorization code in URL
  const hasAuthCode = url.includes('code=') && url.includes('oauth2');

  // Check for token endpoint completion
  const isTokenEndpoint = url.includes('/oauth2/v2.0/token') || url.includes('/oauth2/token');

  return hasAuthCode || isTokenEndpoint;
}
```

**Test Contract**:
```typescript
describe('isLoginSuccess contract', () => {
  it('detects authorization code URLs', () => {
    const url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?code=ABC123';
    expect(isLoginSuccess(url)).toBe(true);
  });

  it('detects token endpoint URLs', () => {
    const url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token';
    expect(isLoginSuccess(url)).toBe(true);
  });

  it('rejects non-login URLs', () => {
    const url = 'https://outlook.office.com';
    expect(isLoginSuccess(url)).toBe(false);
  });

  it('rejects login page without success indicators', () => {
    const url = 'https://login.microsoftonline.com/common/login';
    expect(isLoginSuccess(url)).toBe(false);
  });
});
```

---

## Date/Time Calculations Contract

### Time Period Functions

**Contract**: Calculate time period boundaries for statistics aggregation.

**Functions**:

```typescript
function startOfDay(date: Date): Date;
function endOfDay(date: Date): Date;
function startOfWeek(date: Date): Date; // Monday
function endOfWeek(date: Date): Date;   // Sunday
function startOfMonth(date: Date): Date;
function endOfMonth(date: Date): Date;
```

**Expected Behavior**:
- All dates in user's local timezone
- Week starts Monday (ISO 8601)
- Month boundaries respect varying month lengths
- Handle DST transitions correctly

**Test Contract**:
```typescript
describe('time period calculations contract', () => {
  it('startOfDay returns midnight', () => {
    const date = new Date('2025-11-21T15:30:00');
    const start = startOfDay(date);
    expect(start.getHours()).toBe(0);
    expect(start.getMinutes()).toBe(0);
    expect(start.getSeconds()).toBe(0);
  });

  it('startOfWeek returns Monday', () => {
    const friday = new Date('2025-11-21'); // Friday
    const monday = startOfWeek(friday);
    expect(monday.getDay()).toBe(1); // 1 = Monday
  });

  it('handles month boundaries', () => {
    const endFeb = new Date('2025-02-28');
    const start = startOfMonth(endFeb);
    expect(start.getDate()).toBe(1);
    expect(start.getMonth()).toBe(1); // February
  });
});
```

---

## Extension Lifecycle Contract

### Initialization

**Contract**: Extension initialization on browser startup or install.

**Event**: `chrome.runtime.onInstalled`

**Expected Behavior**:
- Fired on extension install, update, or browser startup
- Initialize storage if not exists
- Migrate data if version changed
- Set up listeners

**Usage**:
```typescript
chrome.runtime.onInstalled.addListener(async (details) => {
  if (details.reason === 'install') {
    // First install - initialize storage
    await chrome.storage.local.set({
      loginEvents: [],
      metadata: {
        version: '1.0.0',
        eventCount: 0,
        storageBytes: 0
      }
    });
  } else if (details.reason === 'update') {
    // Extension updated - check for migrations
    await migrateDataIfNeeded();
  }
});
```

**Test Contract**:
```typescript
describe('extension lifecycle contract', () => {
  it('initializes storage on install', async () => {
    await simulateInstall();
    const { loginEvents } = await chrome.storage.local.get('loginEvents');
    expect(loginEvents).toEqual([]);
  });

  it('preserves data on update', async () => {
    await chrome.storage.local.set({ loginEvents: [mockEvent] });
    await simulateUpdate();
    const { loginEvents } = await chrome.storage.local.get('loginEvents');
    expect(loginEvents).toContainEqual(mockEvent);
  });
});
```
