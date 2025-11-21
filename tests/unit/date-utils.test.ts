/**
 * Unit tests for date utility functions
 * Tests startOfDay, startOfWeek (Monday), startOfMonth calculations
 */

import { describe, it, expect } from '@jest/globals';
import {
  startOfDay,
  endOfDay,
  startOfWeek,
  endOfWeek,
  startOfMonth,
  endOfMonth
} from '../../extension/lib/date-utils';

describe('date-utils', () => {
  describe('startOfDay', () => {
    it('returns midnight for given date', () => {
      const date = new Date('2025-11-21T15:30:45.123Z');
      const start = startOfDay(date);

      expect(start.getHours()).toBe(0);
      expect(start.getMinutes()).toBe(0);
      expect(start.getSeconds()).toBe(0);
      expect(start.getMilliseconds()).toBe(0);
    });

    it('preserves date when input is already at midnight', () => {
      const date = new Date('2025-11-21T00:00:00.000');
      // Set to local midnight explicitly
      date.setHours(0, 0, 0, 0);
      const start = startOfDay(date);

      expect(start.getTime()).toBe(date.getTime());
    });
  });

  describe('endOfDay', () => {
    it('returns 23:59:59.999 for given date', () => {
      const date = new Date('2025-11-21T10:00:00Z');
      const end = endOfDay(date);

      expect(end.getHours()).toBe(23);
      expect(end.getMinutes()).toBe(59);
      expect(end.getSeconds()).toBe(59);
      expect(end.getMilliseconds()).toBe(999);
    });
  });

  describe('startOfWeek', () => {
    it('returns Monday for a Friday', () => {
      const friday = new Date('2025-11-21'); // Friday Nov 21
      const monday = startOfWeek(friday);

      expect(monday.getDay()).toBe(1); // 1 = Monday
      expect(monday.getDate()).toBe(17); // Nov 17 is Monday
    });

    it('returns same date if already Monday', () => {
      const monday = new Date('2025-11-17T10:00:00Z'); // Monday
      const start = startOfWeek(monday);

      expect(start.getDay()).toBe(1); // Still Monday
      expect(start.getDate()).toBe(17);
      expect(start.getHours()).toBe(0); // Midnight
    });

    it('handles Sunday correctly (returns previous Monday)', () => {
      const sunday = new Date('2025-11-23'); // Sunday Nov 23
      const monday = startOfWeek(sunday);

      expect(monday.getDay()).toBe(1); // Monday
      expect(monday.getDate()).toBe(17); // Nov 17 is Monday of that week
    });

    it('sets time to midnight', () => {
      const date = new Date('2025-11-21T15:30:00Z');
      const start = startOfWeek(date);

      expect(start.getHours()).toBe(0);
      expect(start.getMinutes()).toBe(0);
      expect(start.getSeconds()).toBe(0);
    });
  });

  describe('endOfWeek', () => {
    it('returns Sunday for a Friday', () => {
      const friday = new Date('2025-11-21'); // Friday Nov 21
      const sunday = endOfWeek(friday);

      expect(sunday.getDay()).toBe(0); // 0 = Sunday
      expect(sunday.getDate()).toBe(23); // Nov 23 is Sunday
    });

    it('sets time to 23:59:59.999', () => {
      const date = new Date('2025-11-21T10:00:00Z');
      const end = endOfWeek(date);

      expect(end.getHours()).toBe(23);
      expect(end.getMinutes()).toBe(59);
      expect(end.getSeconds()).toBe(59);
    });
  });

  describe('startOfMonth', () => {
    it('returns 1st of month at midnight', () => {
      const date = new Date('2025-11-21T15:30:00Z');
      const start = startOfMonth(date);

      expect(start.getDate()).toBe(1); // 1st of month
      expect(start.getMonth()).toBe(10); // November (0-indexed)
      expect(start.getHours()).toBe(0);
      expect(start.getMinutes()).toBe(0);
    });

    it('handles month boundaries correctly', () => {
      const endFeb = new Date('2025-02-28T12:00:00Z');
      const start = startOfMonth(endFeb);

      expect(start.getDate()).toBe(1);
      expect(start.getMonth()).toBe(1); // February (0-indexed)
      expect(start.getFullYear()).toBe(2025);
    });
  });

  describe('endOfMonth', () => {
    it('returns last day of month at 23:59:59.999', () => {
      const date = new Date('2025-11-15T10:00:00Z');
      const end = endOfMonth(date);

      expect(end.getDate()).toBe(30); // November has 30 days
      expect(end.getMonth()).toBe(10); // November
      expect(end.getHours()).toBe(23);
      expect(end.getMinutes()).toBe(59);
    });

    it('handles varying month lengths', () => {
      // February (non-leap year)
      const feb = new Date('2025-02-15');
      const endFeb = endOfMonth(feb);
      expect(endFeb.getDate()).toBe(28);

      // January (31 days)
      const jan = new Date('2025-01-15');
      const endJan = endOfMonth(jan);
      expect(endJan.getDate()).toBe(31);

      // April (30 days)
      const apr = new Date('2025-04-15');
      const endApr = endOfMonth(apr);
      expect(endApr.getDate()).toBe(30);
    });
  });

  describe('cross-function consistency', () => {
    it('week range contains 7 days', () => {
      const date = new Date('2025-11-21');
      const start = startOfWeek(date);
      const end = endOfWeek(date);

      const diffMs = end.getTime() - start.getTime();
      const diffDays = diffMs / (1000 * 60 * 60 * 24);

      // Should be approximately 7 days (6 days + ~1 day for the partial day)
      expect(diffDays).toBeGreaterThanOrEqual(6);
      expect(diffDays).toBeLessThan(8);
    });

    it('month range respects calendar month', () => {
      const date = new Date('2025-11-21');
      const start = startOfMonth(date);
      const end = endOfMonth(date);

      expect(start.getMonth()).toBe(end.getMonth());
      expect(start.getDate()).toBe(1);
      expect(end.getDate()).toBe(30); // November has 30 days
    });
  });
});
