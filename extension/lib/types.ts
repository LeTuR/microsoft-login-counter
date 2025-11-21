/**
 * Type definitions for Microsoft Login Counter extension
 * Based on data-model.md from specs/001-microsoft-login-counter/
 */

/**
 * Represents a single successful authentication at login.microsoftonline.com
 */
export interface LoginEvent {
  /** Unique identifier (UUID v4) */
  id: string;

  /** When the login occurred (Unix milliseconds, UTC) */
  timestamp: number;

  /** The login.microsoftonline.com URL that triggered detection */
  url: string;

  /** When the extension detected this login (Unix milliseconds) */
  detected_at: number;
}

/**
 * Aggregated counts of login events for time periods
 * Computed on-demand, not stored
 */
export interface LoginStatistics {
  /** Count of logins today (midnight to midnight, local timezone) */
  today: number;

  /** Count of logins this week (Monday to Sunday, local timezone) */
  thisWeek: number;

  /** Count of logins this month (1st to last day, local timezone) */
  thisMonth: number;

  /** Total count of all login events */
  total: number;

  /** Start of the aggregation period (for display) */
  periodStart: Date;

  /** End of the aggregation period (for display) */
  periodEnd: Date;
}

/**
 * Metadata about stored data for quota management
 */
export interface StorageMetadata {
  /** Data schema version (for migrations) */
  version: string;

  /** Total number of stored events */
  eventCount: number;

  /** Timestamp of oldest event (Unix milliseconds) */
  oldestEvent?: number;

  /** Timestamp of newest event (Unix milliseconds) */
  newestEvent?: number;

  /** Approximate storage used in bytes */
  storageBytes: number;

  /** When last maintenance was performed (Unix milliseconds) */
  lastCleanup?: number;

  /** Whether IndexedDB is being used instead of chrome.storage.local */
  usesIndexedDB?: boolean;
}

/**
 * Storage schema keys
 */
export interface StorageSchema {
  loginEvents: LoginEvent[];
  metadata: StorageMetadata;
}
