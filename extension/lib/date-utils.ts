/**
 * Date utility functions for time period calculations
 * All dates in user's local timezone
 * Week starts Monday (ISO 8601)
 */

/**
 * Get the start of day (midnight) for a given date
 */
export function startOfDay(date: Date): Date {
  const result = new Date(date);
  result.setHours(0, 0, 0, 0);
  return result;
}

/**
 * Get the end of day (23:59:59.999) for a given date
 */
export function endOfDay(date: Date): Date {
  const result = new Date(date);
  result.setHours(23, 59, 59, 999);
  return result;
}

/**
 * Get the start of week (Monday at midnight) for a given date
 * ISO 8601: Week starts on Monday
 */
export function startOfWeek(date: Date): Date {
  const result = new Date(date);
  const day = result.getDay();
  // Convert Sunday (0) to 7, so Monday is 1
  const diff = day === 0 ? 6 : day - 1;
  result.setDate(result.getDate() - diff);
  result.setHours(0, 0, 0, 0);
  return result;
}

/**
 * Get the end of week (Sunday at 23:59:59.999) for a given date
 * ISO 8601: Week ends on Sunday
 */
export function endOfWeek(date: Date): Date {
  const result = new Date(date);
  const day = result.getDay();
  // Convert Sunday (0) to 7, so Monday is 1
  const diff = day === 0 ? 0 : 7 - day;
  result.setDate(result.getDate() + diff);
  result.setHours(23, 59, 59, 999);
  return result;
}

/**
 * Get the start of month (1st at midnight) for a given date
 */
export function startOfMonth(date: Date): Date {
  const result = new Date(date);
  result.setDate(1);
  result.setHours(0, 0, 0, 0);
  return result;
}

/**
 * Get the end of month (last day at 23:59:59.999) for a given date
 */
export function endOfMonth(date: Date): Date {
  const result = new Date(date);
  result.setMonth(result.getMonth() + 1, 0); // 0th day of next month = last day of current month
  result.setHours(23, 59, 59, 999);
  return result;
}
