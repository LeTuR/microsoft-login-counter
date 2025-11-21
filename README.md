# Microsoft Login Counter

A cross-browser extension for **Microsoft Edge, Chrome, and Firefox** that automatically detects and counts Microsoft authentication events at login.microsoftonline.com.

## Features

- 🔐 **Automatic Detection**: Monitors login.microsoftonline.com and detects successful authentications
- 📊 **Statistics View**: Display login counts for today, this week, this month, and total
- 📋 **History View**: Chronological list of all past login events with timestamps
- 💾 **Local Storage**: All data stored locally in your browser (no external servers)
- ⚡ **Performance**: < 2 seconds detection latency, < 50MB memory footprint

## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd microsoft-login-counter
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build the extension:**

   **For Chrome/Edge:**
   ```bash
   npm run build
   ```

   **For Firefox:**
   ```bash
   npm run build:firefox
   ```

4. **Load in browser:**

   **Chrome/Edge:**
   - Open `edge://extensions` (or `chrome://extensions`)
   - Enable "Developer mode"
   - Click "Load unpacked"
   - Select the `dist/` directory

   **Firefox:**
   - Open `about:debugging#/runtime/this-firefox`
   - Click "Load Temporary Add-on"
   - Select any file in `dist-firefox/` directory

   Extension icon appears in toolbar

### Usage

1. Navigate to any Microsoft service that requires authentication
2. Sign in through login.microsoftonline.com
3. Click the extension icon to view statistics and history

## Development

### Project Structure

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
└── dist/                   # Build output (generated)
```

### Available Commands

```bash
# Development
npm run build              # Build for Chrome/Edge
npm run build:firefox      # Build for Firefox
npm run build:watch        # Watch mode (rebuild on changes)

# Testing
npm test                   # Run all tests
npm test -- --watch        # Auto-rerun tests on changes
npm test -- --coverage     # Generate coverage report

# Utilities
npm run clean              # Remove dist/ and dist-firefox/
npm run type-check         # TypeScript validation only
```

### Testing

The project follows Test-First Development (TDD):

```bash
# Run all tests
npm test

# Run specific test suite
npm test tests/unit/login-detector.test.ts

# Watch mode for continuous testing
npm test -- --watch
```

Test coverage:
- **Unit tests**: Business logic (date calculations, statistics, event creation)
- **Contract tests**: Browser API interactions (webNavigation, storage)
- **Integration tests**: End-to-end login counting flow

### Building for Production

```bash
npm run build
```

This compiles TypeScript, bundles code with esbuild, and copies static files to `dist/`.

## Technical Details

### Architecture

- **Language**: TypeScript 5.x (strict mode)
- **Target Platform**: Microsoft Edge / Chrome (Manifest V3)
- **Storage**: chrome.storage.local (10MB quota), IndexedDB fallback
- **Build Tool**: esbuild
- **Testing**: Jest 29.x with ts-jest and chrome API mocks

### Detection Mechanism

The extension uses `chrome.webNavigation.onCompleted` to monitor:
- `https://login.microsoftonline.com/*/oauth2/v2.0/authorize` (authorization code flow)
- `https://login.microsoftonline.com/*/oauth2/v2.0/token` (token endpoint)

A 1-second cooldown prevents duplicate counts from redirect chains.

### Data Model

**LoginEvent:**
```typescript
{
  id: string;           // UUID v4
  timestamp: number;    // Unix milliseconds (UTC)
  url: string;          // Full login URL
  detected_at: number;  // Detection timestamp
}
```

**Statistics** (computed on-demand):
- Today: Logins since midnight (local timezone)
- This Week: Monday to Sunday (ISO 8601)
- This Month: 1st to last day of month
- Total: All time

### Storage Capacity

- **chrome.storage.local**: 10MB quota
- **Estimated capacity**: ~50,000 events (200 bytes each)
- **At 10 logins/day**: ~13 years of data

## Troubleshooting

### Extension Not Detecting Logins

**Solutions:**
1. Check browser console for errors: `edge://extensions` → inspect background page
2. Verify URL patterns match: Add debug logging to `isLoginSuccess()`
3. Check permissions in manifest.json: `webNavigation` and `host_permissions`

### Storage Not Persisting

**Solutions:**
1. Verify chrome.storage.local used (not sessionStorage)
2. Check for quota errors in console
3. Inspect storage: `chrome.storage.local.get(null, console.log)`

### Tests Failing

**Solutions:**
1. Verify jest.config.js sets up chrome mocks
2. Install @types/chrome: `npm install --save-dev @types/chrome`
3. Check test environment: `testEnvironment: 'jsdom'` in jest.config.js

## Browser Support

- ✅ **Google Chrome** 100+
- ✅ **Microsoft Edge** 100+
- ✅ **Firefox** 109+

See [FIREFOX.md](FIREFOX.md) for Firefox-specific instructions.

## Design Documents

See `specs/001-microsoft-login-counter/` for detailed design:

- **spec.md**: Feature specification with user stories
- **plan.md**: Implementation plan and technical context
- **data-model.md**: Data structures and storage schema
- **contracts/browser-apis.md**: Browser API contracts
- **tasks.md**: Task breakdown and execution order
- **quickstart.md**: Development setup guide

## Constitution Principles

This project follows three core principles:

1. **Test-First Development (TDD)**: All tests written before implementation
2. **Integration & Contract Testing**: Robust testing for browser API interactions
3. **Pragmatic Simplicity**: YAGNI principles, avoid over-engineering

## License

MIT

## Version

**v1.0.0** - Initial release

---

For more details, see the [quickstart guide](specs/001-microsoft-login-counter/quickstart.md) or [feature specification](specs/001-microsoft-login-counter/spec.md).
