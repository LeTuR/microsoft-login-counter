/**
 * Unit tests for statistics computation
 * Tests today/thisWeek/thisMonth counts with various event dates
 */

import { describe, it, expect, beforeEach } from '@jest/globals';
import { LoginEvent } from '../../extension/lib/types';

// Import function that will be implemented
import { computeStatistics } from '../../extension/lib/statistics';

describe('computeStatistics function', () => {
  const realDate = Date;

  beforeEach(() => {
    // Mock Date constructor to return consistent time for `new Date()`
    const mockDate = new realDate('2025-11-21T15:30:00Z'); // Friday
    global.Date = jest.fn((arg?: any) => {
      if (arg !== undefined) {
        return new realDate(arg);
      }
      return mockDate;
    }) as any;
    global.Date.now = realDate.now.bind(realDate);
  });

  afterEach(() => {
    global.Date = realDate;
  });

  describe('today count', () => {
    it('counts events from today only', () => {
      const events: LoginEvent[] = [
        {
          id: '1',
          timestamp: new Date('2025-11-21T10:00:00Z').getTime(), // Today
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-21T10:00:00Z').getTime()
        },
        {
          id: '2',
          timestamp: new Date('2025-11-21T14:00:00Z').getTime(), // Today
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-21T14:00:00Z').getTime()
        },
        {
          id: '3',
          timestamp: new Date('2025-11-20T10:00:00Z').getTime(), // Yesterday
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-20T10:00:00Z').getTime()
        }
      ];

      const stats = computeStatistics(events);

      expect(stats.today).toBe(2);
    });
  });

  describe('thisWeek count', () => {
    it('counts events from this week (Monday to Sunday)', () => {
      const events: LoginEvent[] = [
        {
          id: '1',
          timestamp: new Date('2025-11-17T10:00:00Z').getTime(), // Monday this week
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-17T10:00:00Z').getTime()
        },
        {
          id: '2',
          timestamp: new Date('2025-11-21T10:00:00Z').getTime(), // Friday this week
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-21T10:00:00Z').getTime()
        },
        {
          id: '3',
          timestamp: new Date('2025-11-16T10:00:00Z').getTime(), // Sunday last week
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-16T10:00:00Z').getTime()
        }
      ];

      const stats = computeStatistics(events);

      expect(stats.thisWeek).toBe(2);
    });
  });

  describe('thisMonth count', () => {
    it('counts events from this month only', () => {
      const events: LoginEvent[] = [
        {
          id: '1',
          timestamp: new Date('2025-11-01T10:00:00Z').getTime(), // Nov 1
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-01T10:00:00Z').getTime()
        },
        {
          id: '2',
          timestamp: new Date('2025-11-21T10:00:00Z').getTime(), // Nov 21
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-21T10:00:00Z').getTime()
        },
        {
          id: '3',
          timestamp: new Date('2025-10-31T10:00:00Z').getTime(), // Oct 31
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-10-31T10:00:00Z').getTime()
        }
      ];

      const stats = computeStatistics(events);

      expect(stats.thisMonth).toBe(2);
    });
  });

  describe('total count', () => {
    it('counts all events', () => {
      const events: LoginEvent[] = [
        {
          id: '1',
          timestamp: new Date('2025-11-21T10:00:00Z').getTime(),
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-11-21T10:00:00Z').getTime()
        },
        {
          id: '2',
          timestamp: new Date('2025-10-15T10:00:00Z').getTime(),
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-10-15T10:00:00Z').getTime()
        },
        {
          id: '3',
          timestamp: new Date('2025-09-01T10:00:00Z').getTime(),
          url: 'https://login.microsoftonline.com/oauth2/token',
          detected_at: new Date('2025-09-01T10:00:00Z').getTime()
        }
      ];

      const stats = computeStatistics(events);

      expect(stats.total).toBe(3);
    });
  });

  describe('empty state', () => {
    it('returns zero counts for empty event array', () => {
      const stats = computeStatistics([]);

      expect(stats.today).toBe(0);
      expect(stats.thisWeek).toBe(0);
      expect(stats.thisMonth).toBe(0);
      expect(stats.total).toBe(0);
    });
  });

  describe('period boundaries', () => {
    it('includes period start and end dates', () => {
      const stats = computeStatistics([]);

      // Check that periodStart and periodEnd have Date properties
      expect(typeof stats.periodStart.getTime).toBe('function');
      expect(typeof stats.periodEnd.getTime).toBe('function');
      expect(stats.periodEnd.getTime()).toBeGreaterThanOrEqual(
        stats.periodStart.getTime()
      );
    });
  });
});
