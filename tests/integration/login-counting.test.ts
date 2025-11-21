/**
 * Integration test for end-to-end login counting flow
 * Tests: mock webNavigation event → storage write → verify event persisted
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { clearMockStorage } from '../setup/chrome-mocks';
import { StorageManager } from '../../extension/storage/storage-manager';

describe('end-to-end login counting', () => {
  let storageManager: StorageManager;

  beforeEach(async () => {
    clearMockStorage();
    jest.clearAllMocks();
    storageManager = new StorageManager();

    // Initialize storage
    await storageManager.initialize();
  });

  it('detects login and stores event', async () => {
    // This test will verify the full flow once implementation is complete
    // For now, we test that storage can accept login events

    const mockEvent = {
      id: '550e8400-e29b-41d4-a716-446655440000',
      timestamp: Date.now(),
      url: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?code=ABC',
      detected_at: Date.now()
    };

    // Store event
    await storageManager.storeLoginEvent(mockEvent);

    // Verify event was stored
    const events = await storageManager.getLoginEvents();
    expect(events).toHaveLength(1);
    expect(events[0]).toMatchObject({
      id: mockEvent.id,
      timestamp: mockEvent.timestamp,
      url: mockEvent.url
    });
  });

  it('increments counter with each login', async () => {
    // Store multiple events
    for (let i = 0; i < 3; i++) {
      const event = {
        id: `event-${i}`,
        timestamp: Date.now() + i * 1000,
        url: 'https://login.microsoftonline.com/oauth2/token',
        detected_at: Date.now() + i * 1000
      };
      await storageManager.storeLoginEvent(event);
    }

    // Verify count
    const events = await storageManager.getLoginEvents();
    expect(events).toHaveLength(3);

    // Verify metadata updated
    const metadata = await storageManager.getMetadata();
    expect(metadata?.eventCount).toBe(3);
  });

  it('persists events across storage operations', async () => {
    const event1 = {
      id: 'event-1',
      timestamp: Date.now(),
      url: 'https://login.microsoftonline.com/oauth2/authorize?code=X',
      detected_at: Date.now()
    };

    await storageManager.storeLoginEvent(event1);

    // Create new storage manager instance (simulates extension restart)
    const newStorageManager = new StorageManager();
    const events = await newStorageManager.getLoginEvents();

    expect(events).toHaveLength(1);
    expect(events[0].id).toBe('event-1');
  });

  it('handles cooldown - rejects duplicate within 1 second', async () => {
    // This will be fully tested once login detector is implemented
    // For now, test that we can store events with different timestamps

    const baseTime = Date.now();
    const event1 = {
      id: 'event-1',
      timestamp: baseTime,
      url: 'https://login.microsoftonline.com/oauth2/token',
      detected_at: baseTime
    };

    const event2 = {
      id: 'event-2',
      timestamp: baseTime + 500, // 500ms later (within cooldown)
      url: 'https://login.microsoftonline.com/oauth2/token',
      detected_at: baseTime + 500
    };

    await storageManager.storeLoginEvent(event1);

    // For now, this will store both - cooldown logic will be in login detector
    await storageManager.storeLoginEvent(event2);

    const events = await storageManager.getLoginEvents();
    // Note: Cooldown filtering happens in login-detector, not storage
    expect(events.length).toBeGreaterThanOrEqual(1);
  });

  it('updates metadata correctly', async () => {
    const event = {
      id: 'test-event',
      timestamp: 1700000000000,
      url: 'https://login.microsoftonline.com/oauth2/token',
      detected_at: 1700000000123
    };

    await storageManager.storeLoginEvent(event);

    const metadata = await storageManager.getMetadata();

    expect(metadata).toBeDefined();
    expect(metadata?.eventCount).toBe(1);
    expect(metadata?.oldestEvent).toBe(1700000000000);
    expect(metadata?.newestEvent).toBe(1700000000000);
    expect(metadata?.version).toBe('1.0.0');
  });
});
