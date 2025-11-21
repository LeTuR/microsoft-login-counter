# Quickstart: Microsoft Login Event Counter

**Feature**: 001-microsoft-login-counter
**Date**: 2025-11-21
**Purpose**: Get the extension running for development and testing

## Prerequisites

- Node.js 18.x or later
- npm 9.x or later
- Edge or Chrome browser
- Git

## Quick Start (5 minutes)

### 1. Clone and Install

```bash
git clone <repository-url>
cd microsoft-login-counter
npm install
```

### 2. Build Extension

```bash
npm run build
```

This compiles TypeScript and bundles the extension to `dist/`.

### 3. Load in Browser

**Edge/Chrome**:
1. Open `edge://extensions` (or `chrome://extensions`)
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `dist/` directory
5. Extension icon appears in toolbar

### 4. Test Login Detection

1. Navigate to https://login.microsoftonline.com
2. Complete authentication (or simulate in test environment)
3. Click extension icon
4. Verify login count incremented

---

## Project Structure

```
microsoft-login-counter/
├── extension/              # Source code
│   ├── background/         # Background script (login detection)
│   ├── popup/              # Popup UI (statistics display)
│   ├── storage/            # Data persistence layer
│   ├── lib/                # Shared utilities
│   └── manifest.json       # Extension configuration
├── tests/                  # Test suites
│   ├── contract/           # Browser API contracts
│   ├── integration/        # End-to-end flows
│   └── unit/               # Business logic tests
├── specs/                  # Design documents
│   └── 001-microsoft-login-counter/
│       ├── spec.md         # Feature specification
│       ├── plan.md         # Implementation plan
│       ├── data-model.md   # Data structures
│       ├── research.md     # Technical decisions
│       └── contracts/      # API contracts
├── dist/                   # Build output (ignored by git)
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
└── README.md               # Project documentation
```

---

## Development Workflow

### Run Tests

```bash
# All tests
npm test

# Watch mode (auto-rerun on changes)
npm test -- --watch

# Coverage report
npm test -- --coverage

# Specific test file
npm test -- tests/unit/date-utils.test.ts
```

### Build for Development

```bash
# Build once
npm run build

# Watch mode (rebuild on file changes)
npm run build:watch
```

### Reload Extension

After code changes:
1. Run `npm run build` (or use watch mode)
2. Go to `edge://extensions`
3. Click "Reload" icon on extension card

Or use `web-ext` for auto-reload:
```bash
npm run dev
```

---

## Testing Login Detection

### Manual Testing

**Test Case 1: Successful Login**
1. Open Edge
2. Navigate to https://login.microsoftonline.com
3. Sign in with Microsoft account
4. Open extension popup
5. Verify "Today: 1 login" displayed

**Test Case 2: Multiple Logins**
1. Sign out of all Microsoft services
2. Navigate to https://teams.microsoft.com
3. Authenticate when prompted
4. Navigate to https://outlook.office.com
5. Authenticate again
6. Open extension popup
7. Verify "Today: 2 logins"

**Test Case 3: Rapid Logins (Deduplication)**
1. Open 3 tabs simultaneously
2. Navigate all to login.microsoftonline.com
3. Authenticate in first tab (redirects cause other tabs to auth too)
4. Open extension popup
5. Verify only 1 login counted (1-second cooldown prevents duplicates)

### Automated Testing

```bash
# Run contract tests (browser API mocks)
npm test -- tests/contract/

# Run integration tests
npm test -- tests/integration/

# Run specific test suite
npm test -- --testNamePattern="login detection"
```

---

## Configuration

### Extension Permissions

Defined in `extension/manifest.json`:

```json
{
  "permissions": [
    "storage",        // For chrome.storage.local
    "webNavigation"   // For detecting login.microsoftonline.com navigation
  ],
  "host_permissions": [
    "https://login.microsoftonline.com/*"
  ]
}
```

### Storage Limits

- **chrome.storage.local**: 10MB quota
- **Estimated capacity**: ~50,000 login events
- **Migration**: Prompt for IndexedDB if >8MB used

### URL Patterns Monitored

```
https://login.microsoftonline.com/*/oauth2/v2.0/authorize*
https://login.microsoftonline.com/common/oauth2/authorize*
https://login.microsoftonline.com/*/oauth2/v2.0/token*
```

---

## Common Development Tasks

### Add a New Test

```typescript
// tests/unit/new-feature.test.ts
import { describe, it, expect } from '@jest/globals';
import { newFeature } from '../../extension/lib/new-feature';

describe('newFeature', () => {
  it('does something correctly', () => {
    const result = newFeature('input');
    expect(result).toBe('expected output');
  });
});
```

Run with: `npm test -- tests/unit/new-feature.test.ts`

### Inspect Storage

```javascript
// In browser console (on extension popup or background page):
chrome.storage.local.get(null, (data) => {
  console.log('All storage:', data);
});

// Or use async/await:
const data = await chrome.storage.local.get();
console.log('Login events:', data.loginEvents);
console.log('Metadata:', data.metadata);
```

### Clear Storage (Reset Extension)

```javascript
// In browser console:
await chrome.storage.local.clear();
console.log('Storage cleared');
```

Or via extension popup (if implemented):
- Click "Settings" → "Clear all data" → Confirm

### Debug Login Detection

```typescript
// Add to background/login-detector.ts:
chrome.webNavigation.onCompleted.addListener((details) => {
  console.log('Navigation completed:', details.url);
  console.log('Frame ID:', details.frameId);
  console.log('Timestamp:', new Date(details.timeStamp));

  if (isLoginSuccess(details.url)) {
    console.log('✅ Login detected!');
  } else {
    console.log('❌ Not a login URL');
  }
});
```

View logs: `edge://extensions` → Extension details → "Inspect views: background page"

---

## Troubleshooting

### Extension Not Detecting Logins

**Symptoms**: Counter doesn't increment after login

**Solutions**:
1. Check browser console for errors: `edge://extensions` → inspect background page
2. Verify URL patterns match: Add debug logging to `isLoginSuccess()`
3. Check permissions in manifest.json: `webNavigation` and `host_permissions`
4. Test with simpler URL first: Try navigating directly to https://login.microsoftonline.com/common/oauth2/v2.0/authorize

### Storage Not Persisting

**Symptoms**: Data lost after browser restart

**Solutions**:
1. Verify chrome.storage.local used (not sessionStorage)
2. Check for quota errors in console
3. Inspect storage: `chrome.storage.local.get(null, console.log)`
4. Ensure writes complete before browser closes

### Tests Failing

**Symptoms**: Jest tests fail with "chrome is not defined"

**Solutions**:
1. Verify jest.config.js sets up chrome mocks
2. Install @types/chrome: `npm install --save-dev @types/chrome`
3. Check test environment: `testEnvironment: 'jsdom'` in jest.config.js
4. Mock chrome APIs in test setup:
   ```typescript
   global.chrome = {
     storage: { local: { get: jest.fn(), set: jest.fn() } }
   } as any;
   ```

### Build Errors

**Symptoms**: TypeScript compilation fails

**Solutions**:
1. Clear build cache: `rm -rf dist/ && npm run build`
2. Check TypeScript version: `npx tsc --version` (should be 5.x)
3. Verify tsconfig.json paths resolve correctly
4. Install missing types: `npm install --save-dev @types/chrome`

---

## Next Steps

1. **Run tests**: `npm test` to verify everything works
2. **Manual testing**: Load extension and test login detection
3. **Review data model**: See `specs/001-microsoft-login-counter/data-model.md`
4. **Implement Phase 1**: Start with login detection (User Story 1 - P1)
5. **Follow TDD**: Write tests first, then implement

---

## Useful Commands

```bash
# Development
npm run build:watch        # Auto-rebuild on changes
npm test -- --watch        # Auto-rerun tests on changes
npm run dev                # Build + watch + auto-reload

# Testing
npm test                   # Run all tests
npm test -- --coverage     # With coverage report
npm test -- unit/          # Run unit tests only

# Production
npm run build              # Production build
npm run lint               # Check code style
npm run format             # Auto-format code

# Utilities
npm run clean              # Remove dist/
npm run type-check         # TypeScript validation only
```

---

## Development Tips

1. **Use watch mode**: Run `npm run build:watch` in one terminal, tests in another
2. **Check console often**: Background page console shows detection logs
3. **Test incrementally**: Verify each user story independently
4. **Follow constitution**: Write tests first (TDD), keep it simple
5. **Inspect storage frequently**: Verify data structure matches data-model.md

---

## Resources

- **Spec**: [spec.md](./spec.md) - Feature requirements
- **Plan**: [plan.md](./plan.md) - Implementation plan
- **Data Model**: [data-model.md](./data-model.md) - Data structures
- **Contracts**: [contracts/browser-apis.md](./contracts/browser-apis.md) - API contracts
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) - Development principles

- **Chrome Extensions Docs**: https://developer.chrome.com/docs/extensions/
- **webNavigation API**: https://developer.chrome.com/docs/extensions/reference/webNavigation/
- **storage API**: https://developer.chrome.com/docs/extensions/reference/storage/
