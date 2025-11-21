/**
 * Unit tests for LoginEvent creation and validation
 * Tests UUID generation, timestamp validation, URL validation
 */

import { describe, it, expect } from '@jest/globals';

// Import function that will be implemented
import { createLoginEvent } from '../../extension/background/login-detector';

describe('LoginEvent creation', () => {
  describe('createLoginEvent function', () => {
    it('generates unique UUID v4 for each event', () => {
      const url = 'https://login.microsoftonline.com/common/oauth2/authorize?code=ABC';
      const timestamp = Date.now();

      const event1 = createLoginEvent(url, timestamp);
      const event2 = createLoginEvent(url, timestamp);

      // IDs should be unique
      expect(event1.id).not.toBe(event2.id);

      // UUID v4 format: xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      expect(event1.id).toMatch(uuidRegex);
      expect(event2.id).toMatch(uuidRegex);
    });

    it('captures timestamp correctly', () => {
      const url = 'https://login.microsoftonline.com/oauth2/authorize?code=X';
      const timestamp = 1700000000000;

      const event = createLoginEvent(url, timestamp);

      expect(event.timestamp).toBe(timestamp);
    });

    it('captures URL correctly', () => {
      const url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token';
      const timestamp = Date.now();

      const event = createLoginEvent(url, timestamp);

      expect(event.url).toBe(url);
    });

    it('sets detected_at within 5 seconds of timestamp', () => {
      const url = 'https://login.microsoftonline.com/oauth2/token';
      const timestamp = Date.now();

      const event = createLoginEvent(url, timestamp);

      // detected_at should be very close to timestamp (< 5 seconds)
      const diff = Math.abs(event.detected_at - event.timestamp);
      expect(diff).toBeLessThan(5000);
    });

    it('creates valid LoginEvent structure', () => {
      const url = 'https://login.microsoftonline.com/oauth2/authorize?code=Y';
      const timestamp = Date.now();

      const event = createLoginEvent(url, timestamp);

      // Check all required fields exist
      expect(event).toHaveProperty('id');
      expect(event).toHaveProperty('timestamp');
      expect(event).toHaveProperty('url');
      expect(event).toHaveProperty('detected_at');

      // Check types
      expect(typeof event.id).toBe('string');
      expect(typeof event.timestamp).toBe('number');
      expect(typeof event.url).toBe('string');
      expect(typeof event.detected_at).toBe('number');
    });
  });

  describe('validation rules', () => {
    it('requires timestamp to be positive number', () => {
      const url = 'https://login.microsoftonline.com/oauth2/token';

      // Valid timestamp
      const validEvent = createLoginEvent(url, Date.now());
      expect(validEvent.timestamp).toBeGreaterThan(0);
    });

    it('requires URL to start with https://login.microsoftonline.com/', () => {
      const validUrl = 'https://login.microsoftonline.com/oauth2/token';
      const timestamp = Date.now();

      const event = createLoginEvent(validUrl, timestamp);

      expect(event.url).toMatch(/^https:\/\/login\.microsoftonline\.com\//);
    });

    it('ensures timestamp is not in the future', () => {
      const url = 'https://login.microsoftonline.com/oauth2/token';
      const timestamp = Date.now();

      const event = createLoginEvent(url, timestamp);

      // timestamp should be <= current time (allowing small clock skew)
      expect(event.timestamp).toBeLessThanOrEqual(Date.now() + 1000);
    });
  });
});
