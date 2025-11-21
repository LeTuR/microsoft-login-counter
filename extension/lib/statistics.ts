/**
 * Statistics computation for login events
 * Aggregates events by time periods (today/week/month)
 */

import { LoginEvent, LoginStatistics } from './types';
import {
  startOfDay,
  endOfDay,
  startOfWeek,
  startOfMonth
} from './date-utils';

/**
 * Compute login statistics from an array of login events
 * @param events - Array of LoginEvent objects
 * @returns LoginStatistics with counts for today, thisWeek, thisMonth, and total
 */
export function computeStatistics(events: LoginEvent[]): LoginStatistics {
  const now = new Date();
  const todayStart = startOfDay(now);
  const weekStart = startOfWeek(now); // Monday
  const monthStart = startOfMonth(now);

  // Filter events by time periods
  const todayEvents = events.filter(
    (e) => new Date(e.timestamp) >= todayStart
  );

  const weekEvents = events.filter(
    (e) => new Date(e.timestamp) >= weekStart
  );

  const monthEvents = events.filter(
    (e) => new Date(e.timestamp) >= monthStart
  );

  return {
    today: todayEvents.length,
    thisWeek: weekEvents.length,
    thisMonth: monthEvents.length,
    total: events.length,
    periodStart: todayStart,
    periodEnd: endOfDay(now)
  };
}
