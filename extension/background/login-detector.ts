/**
 * Login detection logic for Microsoft authentication
 * Monitors login.microsoftonline.com and detects successful authentication events
 */

import { LoginEvent } from '../lib/types';
import { StorageManager } from '../storage/storage-manager';

/**
 * Generates a UUID v4
 */
function generateUUID(): string {
  // UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Determines if a URL represents successful Microsoft authentication
 * @param url - The URL to check
 * @returns true if the URL indicates successful login
 */
export function isLoginSuccess(url: string): boolean {
  // Must be HTTPS and from login.microsoftonline.com
  if (!url.startsWith('https://login.microsoftonline.com/')) {
    return false;
  }

  // Check for authorization code in URL (oauth2 flow)
  const hasAuthCode = url.includes('code=') && url.includes('oauth2');

  // Check for token endpoint completion
  const isTokenEndpoint =
    url.includes('/oauth2/v2.0/token') || url.includes('/oauth2/token');

  return hasAuthCode || isTokenEndpoint;
}

/**
 * Creates a new LoginEvent from URL and timestamp
 * @param url - The login URL
 * @param timestamp - When the login occurred (Unix milliseconds)
 * @returns A new LoginEvent object
 */
export function createLoginEvent(url: string, timestamp: number): LoginEvent {
  return {
    id: generateUUID(),
    timestamp,
    url,
    detected_at: Date.now()
  };
}

// Track last login time for cooldown logic
let lastLoginTime = 0;
const COOLDOWN_MS = 1000; // 1 second cooldown

const storageManager = new StorageManager();

/**
 * Handles navigation completion events
 * Filters for main frame, applies URL filter, detects login success,
 * creates and stores events with cooldown
 */
function handleNavigationCompleted(
  details: chrome.webNavigation.WebNavigationFramedCallbackDetails
): void {
  try {
    // Only process main frame navigations (frameId = 0)
    if (details.frameId !== 0) {
      return;
    }

    // Check if URL indicates successful login
    if (!isLoginSuccess(details.url)) {
      return;
    }

    // Apply cooldown to prevent redirect-induced duplicates
    const now = Date.now();
    if (now - lastLoginTime < COOLDOWN_MS) {
      console.log('Login event within cooldown period, skipping');
      return;
    }

    // Update last login time
    lastLoginTime = now;

    // Create and store login event
    const event = createLoginEvent(details.url, details.timeStamp);

    console.log('Login detected:', {
      url: details.url,
      timestamp: new Date(details.timeStamp).toISOString(),
      eventId: event.id
    });

    // Store event asynchronously
    storageManager.storeLoginEvent(event).catch((error) => {
      console.error('Failed to store login event:', error);
    });
  } catch (error) {
    console.error('Error handling navigation completion:', error);
  }
}

/**
 * Initialize the login detector
 * Sets up event listeners and initializes storage if needed
 */
async function initialize(): Promise<void> {
  try {
    console.log('Initializing Microsoft Login Counter...');

    // Check if storage is initialized
    const metadata = await storageManager.getMetadata();
    if (!metadata) {
      console.log('First run - initializing storage');
      await storageManager.initialize();
    }

    // Set up webNavigation listener with URL filter
    chrome.webNavigation.onCompleted.addListener(handleNavigationCompleted, {
      url: [{ hostEquals: 'login.microsoftonline.com' }]
    });

    console.log('Microsoft Login Counter initialized successfully');
  } catch (error) {
    console.error('Failed to initialize login detector:', error);
  }
}

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener(async (details) => {
  try {
    if (details.reason === 'install') {
      console.log('Extension installed - initializing storage');
      await storageManager.initialize();
    } else if (details.reason === 'update') {
      console.log('Extension updated');
      // Future: handle data migrations here if needed
    }
  } catch (error) {
    console.error('Error during extension installation:', error);
  }
});

// Initialize on script load
initialize();
