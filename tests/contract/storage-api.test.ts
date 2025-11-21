/**
 * Contract test for chrome.storage.local API
 * Verifies get/set/clear methods and quota handling
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { clearMockStorage } from '../setup/chrome-mocks';

describe('storage.local API contract', () => {
  beforeEach(() => {
    clearMockStorage();
    jest.clearAllMocks();
  });

  describe('get() method', () => {
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

      expect(result.a).toBe(1);
      expect(result.b).toBe(2);
    });

    it('returns all data when called with null', async () => {
      await chrome.storage.local.set({ x: 10, y: 20 });
      const result = await chrome.storage.local.get(null);

      expect(result.x).toBe(10);
      expect(result.y).toBe(20);
    });
  });

  describe('set() method', () => {
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

    it('supports storing arrays', async () => {
      const arr = [1, 2, 3];
      await chrome.storage.local.set({ myArray: arr });
      const result = await chrome.storage.local.get('myArray');

      expect(result.myArray).toEqual(arr);
    });

    it('supports storing objects', async () => {
      const obj = { nested: { value: 42 } };
      await chrome.storage.local.set({ myObject: obj });
      const result = await chrome.storage.local.get('myObject');

      expect(result.myObject).toEqual(obj);
    });
  });

  describe('clear() method', () => {
    it('removes all stored data', async () => {
      await chrome.storage.local.set({ a: 1, b: 2 });
      await chrome.storage.local.clear();
      const result = await chrome.storage.local.get(['a', 'b']);

      expect(result.a).toBeUndefined();
      expect(result.b).toBeUndefined();
    });
  });

  describe('getBytesInUse() method', () => {
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

    it('increases as more data is added', async () => {
      await chrome.storage.local.set({ small: 'x' });
      const bytesSmall = await chrome.storage.local.getBytesInUse();

      await chrome.storage.local.set({ large: 'x'.repeat(1000) });
      const bytesLarge = await chrome.storage.local.getBytesInUse();

      expect(bytesLarge).toBeGreaterThan(bytesSmall);
    });
  });
});
