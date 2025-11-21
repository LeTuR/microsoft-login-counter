/**
 * Storage Manager for chrome.storage.local operations
 * Provides wrapper methods for LoginEvent and metadata persistence
 */

import { LoginEvent, StorageMetadata, StorageSchema } from '../lib/types';

export class StorageManager {
  /**
   * Get data from chrome.storage.local
   */
  async get<K extends keyof StorageSchema>(
    keys: K | K[]
  ): Promise<Partial<StorageSchema>> {
    const keysArray = Array.isArray(keys) ? keys : [keys];
    const result = await chrome.storage.local.get(keysArray);
    return result as Partial<StorageSchema>;
  }

  /**
   * Set data in chrome.storage.local
   */
  async set(items: Partial<StorageSchema>): Promise<void> {
    await chrome.storage.local.set(items);
  }

  /**
   * Clear all data from chrome.storage.local
   */
  async clear(): Promise<void> {
    await chrome.storage.local.clear();
  }

  /**
   * Get bytes in use for specified keys
   * @param keys - Optional keys to check (null = all storage)
   */
  async getBytesInUse(keys?: string | string[] | null): Promise<number> {
    return await chrome.storage.local.getBytesInUse(keys ?? null);
  }

  /**
   * Get all login events
   * @returns Array of login events, or empty array if none exist
   */
  async getLoginEvents(): Promise<LoginEvent[]> {
    const result = await this.get('loginEvents');
    return result.loginEvents || [];
  }

  /**
   * Store a new login event
   * Appends to existing events array and updates metadata
   */
  async storeLoginEvent(event: LoginEvent): Promise<void> {
    try {
      // Get existing data
      const { loginEvents = [], metadata } = await this.get(['loginEvents', 'metadata']);

      // Append new event
      const updatedEvents = [...loginEvents, event];

      // Update metadata
      const updatedMetadata: StorageMetadata = {
        version: metadata?.version || '1.0.0',
        eventCount: updatedEvents.length,
        oldestEvent: updatedEvents[0]?.timestamp,
        newestEvent: event.timestamp,
        storageBytes: metadata?.storageBytes || 0, // Will be calculated after write
        lastCleanup: metadata?.lastCleanup,
        usesIndexedDB: metadata?.usesIndexedDB || false
      };

      // Write to storage
      await this.set({
        loginEvents: updatedEvents,
        metadata: updatedMetadata
      });

      // Update storage bytes estimate
      const bytesUsed = await this.getBytesInUse();
      updatedMetadata.storageBytes = bytesUsed;
      await this.set({ metadata: updatedMetadata });

    } catch (error) {
      // Check if quota exceeded
      if (error instanceof Error && error.message.includes('QUOTA_BYTES')) {
        console.error('Storage quota exceeded:', error);
        throw new Error('Storage quota exceeded. Please export and clear old data.');
      }
      throw error;
    }
  }

  /**
   * Get storage metadata
   */
  async getMetadata(): Promise<StorageMetadata | undefined> {
    const result = await this.get('metadata');
    return result.metadata;
  }

  /**
   * Initialize storage with empty data (for first install)
   */
  async initialize(): Promise<void> {
    const metadata: StorageMetadata = {
      version: '1.0.0',
      eventCount: 0,
      storageBytes: 0,
      usesIndexedDB: false
    };

    await this.set({
      loginEvents: [],
      metadata
    });
  }
}
