# Firefox Installation Guide

Your Microsoft Login Counter extension is now **fully compatible with Firefox**! 🦊

## Quick Start

### 1. Build for Firefox

```bash
npm run build:firefox
```

This creates a `dist-firefox/` directory with Firefox-specific configuration.

### 2. Load in Firefox (Temporary - for Development)

1. **Open Firefox**
2. **Navigate to:** `about:debugging#/runtime/this-firefox`
3. **Click:** "Load Temporary Add-on..."
4. **Navigate to:** `dist-firefox/` folder
5. **Select:** `manifest.json` (or any file in the folder)
6. **Done!** Extension loads immediately

The extension icon appears in your Firefox toolbar.

### 3. Test It

1. Navigate to any Microsoft service (e.g., https://teams.microsoft.com)
2. Sign in through login.microsoftonline.com
3. Click the extension icon in toolbar
4. View your login statistics!

---

## Differences from Chrome Version

### Manifest Changes (Already Handled)
- Added `browser_specific_settings` with gecko ID
- Changed `background.service_worker` → `background.scripts`
- Firefox minimum version: 109.0+

### API Compatibility
Your code uses standard WebExtension APIs:
- ✅ `chrome.storage.local` - Works in Firefox
- ✅ `chrome.webNavigation` - Works in Firefox
- ✅ `chrome.runtime` - Works in Firefox

Firefox automatically provides `chrome.*` namespace for compatibility.

---

## Development Workflow

### Build Commands

```bash
# Build Chrome version (default)
npm run build

# Build Firefox version
npm run build:firefox

# Clean all builds
npm run clean
```

### Hot Reload

Firefox automatically reloads the extension when you:
1. Rebuild with `npm run build:firefox`
2. Click the "Reload" button in `about:debugging`

Or use watch mode (manual reload still required):
```bash
npm run build:watch
```

---

## Temporary vs Permanent Installation

### Temporary (Current Method)
- **Pros:** Quick for development, no signing required
- **Cons:** Unloads when Firefox closes, requires reload each session
- **Use for:** Development and testing

### Permanent Installation

To make it permanent, you have two options:

#### Option 1: Firefox Add-ons Store (Recommended)

Similar to Chrome Web Store:
1. Create account at [Firefox Add-on Developer Hub](https://addons.mozilla.org/developers/)
2. Submit extension for review
3. Publish as **"Unlisted"** (only you can access via link)
4. **No fees required** (unlike Chrome's $5)

**Advantages:**
- ✅ Free (no registration fee)
- ✅ Survives Firefox restarts
- ✅ Auto-updates
- ✅ Works on company-managed Firefox (policies usually allow store add-ons)

#### Option 2: Self-Hosted Distribution

For Firefox 48+, you can self-host signed extensions:
1. Get it signed by Mozilla (required, even for self-hosting)
2. Host the `.xpi` file anywhere
3. Users install from your URL

---

## Debugging

### View Console Logs

1. Go to `about:debugging#/runtime/this-firefox`
2. Find "Microsoft Login Counter"
3. Click "Inspect" next to it
4. Browser console opens showing your logs

### Check Storage

In the browser console:
```javascript
// View all stored data
browser.storage.local.get(null).then(console.log);

// Clear storage
browser.storage.local.clear();
```

### Common Issues

**Extension not loading:**
- Check Firefox version: Must be 109.0 or higher
- Verify manifest.json exists in dist-firefox/
- Check browser console for errors

**Login detection not working:**
- Verify permissions granted (Firefox will prompt on first install)
- Check that you're actually hitting login.microsoftonline.com
- Open inspect tool and check console logs

**Data not persisting:**
- Temporary add-ons lose data when Firefox closes
- For permanent storage, publish to Add-ons store

---

## Publishing to Firefox Add-ons Store

Want to bypass company policies? Publish as unlisted:

### Requirements:
- ✅ No registration fee (FREE!)
- ✅ Firefox Add-on Developer account
- ✅ Same assets as Chrome (icons, screenshots, description)
- ✅ Privacy policy (if collecting data)

### Steps:

1. **Create account:** https://addons.mozilla.org/developers/
2. **Package extension:**
   ```bash
   cd dist-firefox
   zip -r ../firefox-extension.zip .
   ```
3. **Submit:**
   - Upload zip file
   - Choose "On your own" (unlisted)
   - Fill in metadata
   - Submit for review
4. **Wait:** Usually 1-2 days for review
5. **Install:** Once approved, you get a direct link to install

**Unlisted means:**
- Not searchable on addons.mozilla.org
- Only people with direct link can install
- Perfect for personal use or company-internal tools

---

## Differences: Chrome vs Firefox

| Feature | Chrome | Firefox |
|---------|--------|---------|
| **Store Fee** | $5 one-time | Free |
| **Review Time** | 1-3 days | 1-2 days |
| **Dev Mode** | Load unpacked | Load temporary |
| **Background Script** | Service Worker | Classic scripts |
| **API Namespace** | `chrome.*` | `browser.*` or `chrome.*` |
| **Min Version** | Chrome 100+ | Firefox 109+ |

Both versions are built from the same codebase!

---

## Testing Both Browsers

You can test both versions simultaneously:

```bash
# Terminal 1: Build Chrome version
npm run build

# Terminal 2: Build Firefox version
npm run build:firefox

# Load dist/ in Chrome
# Load dist-firefox/ in Firefox
```

---

## Next Steps

1. ✅ Extension works in Firefox
2. ⚠️ Icons are SVG (need PNG for production)
3. 💡 Consider publishing to Add-ons store to bypass company policies
4. 🎨 Create proper icons (16x16, 48x48, 128x128 PNG)

Need help with any of these? Just ask!
