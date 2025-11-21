/**
 * Popup UI logic for Microsoft Login Counter
 * Displays statistics and history views
 */

import { StorageManager } from '../storage/storage-manager';
import { computeStatistics } from '../lib/statistics';
import { LoginEvent } from '../lib/types';

const storageManager = new StorageManager();

/**
 * Format a period label with date range
 * @param label - The label (e.g., "This Week", "This Month")
 * @param start - Start date of the period
 * @param end - End date of the period
 */
function formatPeriodLabel(label: string, start: Date, end: Date): string {
  const formatDate = (date: Date) => {
    const month = date.toLocaleDateString('en-US', { month: 'short' });
    const day = date.getDate();
    return `${month} ${day}`;
  };

  return `${formatDate(start)} - ${formatDate(end)}`;
}

/**
 * Format a login event timestamp to user-friendly date/time string
 * @param timestamp - Unix milliseconds timestamp
 */
function formatLoginEvent(timestamp: number): string {
  const date = new Date(timestamp);
  const dateStr = date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
  const timeStr = date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit'
  });
  return `${dateStr} at ${timeStr}`;
}

/**
 * Render statistics view with login counts
 */
async function renderStatistics(): Promise<void> {
  const loadingState = document.getElementById('loading-state');
  const emptyState = document.getElementById('empty-state');
  const statisticsContent = document.getElementById('statistics-content');

  if (!loadingState || !emptyState || !statisticsContent) return;

  try {
    // Show loading state
    loadingState.classList.remove('hidden');
    emptyState.classList.add('hidden');
    statisticsContent.classList.add('hidden');

    // Load events and compute statistics
    const events = await storageManager.getLoginEvents();
    const stats = computeStatistics(events);

    // Hide loading
    loadingState.classList.add('hidden');

    // Show empty state or statistics
    if (stats.total === 0) {
      emptyState.classList.remove('hidden');
      statisticsContent.classList.add('hidden');
    } else {
      emptyState.classList.add('hidden');
      statisticsContent.classList.remove('hidden');

      // Update statistics values
      const todayEl = document.getElementById('stat-today');
      const weekEl = document.getElementById('stat-week');
      const monthEl = document.getElementById('stat-month');
      const totalEl = document.getElementById('stat-total');
      const weekPeriodEl = document.getElementById('stat-week-period');
      const monthPeriodEl = document.getElementById('stat-month-period');

      if (todayEl) todayEl.textContent = stats.today.toString();
      if (weekEl) weekEl.textContent = stats.thisWeek.toString();
      if (monthEl) monthEl.textContent = stats.thisMonth.toString();
      if (totalEl) totalEl.textContent = stats.total.toString();

      // Add period labels
      if (weekPeriodEl) {
        const weekStart = new Date(stats.periodStart);
        weekStart.setDate(weekStart.getDate() - weekStart.getDay() + (weekStart.getDay() === 0 ? -6 : 1));
        const weekEnd = new Date(weekStart);
        weekEnd.setDate(weekEnd.getDate() + 6);
        weekPeriodEl.textContent = formatPeriodLabel('', weekStart, weekEnd);
      }

      if (monthPeriodEl) {
        const monthStart = new Date(stats.periodStart);
        monthStart.setDate(1);
        const monthEnd = new Date(monthStart);
        monthEnd.setMonth(monthEnd.getMonth() + 1, 0);
        monthPeriodEl.textContent = formatPeriodLabel('', monthStart, monthEnd);
      }
    }
  } catch (error) {
    console.error('Failed to load statistics:', error);
    loadingState.classList.add('hidden');
    if (emptyState) {
      emptyState.innerHTML = '<p>Error loading statistics</p>';
      emptyState.classList.remove('hidden');
    }
  }
}

/**
 * Render history view with login events
 */
async function renderHistory(): Promise<void> {
  const loadingState = document.getElementById('history-loading-state');
  const emptyState = document.getElementById('history-empty-state');
  const historyList = document.getElementById('history-list');

  if (!loadingState || !emptyState || !historyList) return;

  try {
    // Show loading state
    loadingState.classList.remove('hidden');
    emptyState.classList.add('hidden');
    historyList.classList.add('hidden');

    // Load events (last 100 for performance)
    const allEvents = await storageManager.getLoginEvents();
    const events = allEvents.slice(-100).reverse(); // Most recent first

    // Hide loading
    loadingState.classList.add('hidden');

    // Show empty state or history
    if (events.length === 0) {
      emptyState.classList.remove('hidden');
      historyList.classList.add('hidden');
    } else {
      emptyState.classList.add('hidden');
      historyList.classList.remove('hidden');

      // Clear and populate history list
      historyList.innerHTML = '';

      events.forEach((event, index) => {
        const li = document.createElement('li');
        li.className = 'history-item';

        const icon = document.createElement('div');
        icon.className = 'history-icon';
        icon.textContent = (index + 1).toString();

        const details = document.createElement('div');
        details.className = 'history-details';

        const timestamp = document.createElement('div');
        timestamp.className = 'history-timestamp';
        timestamp.textContent = formatLoginEvent(event.timestamp);

        const url = document.createElement('div');
        url.className = 'history-url';
        url.textContent = event.url;
        url.title = event.url;

        details.appendChild(timestamp);
        details.appendChild(url);

        li.appendChild(icon);
        li.appendChild(details);

        historyList.appendChild(li);
      });
    }
  } catch (error) {
    console.error('Failed to load history:', error);
    loadingState.classList.add('hidden');
    if (emptyState) {
      emptyState.innerHTML = '<p>Error loading history</p>';
      emptyState.classList.remove('hidden');
    }
  }
}

/**
 * Setup tab navigation
 */
function setupTabs(): void {
  const tabStatistics = document.getElementById('tab-statistics');
  const tabHistory = document.getElementById('tab-history');
  const viewStatistics = document.getElementById('view-statistics');
  const viewHistory = document.getElementById('view-history');

  if (!tabStatistics || !tabHistory || !viewStatistics || !viewHistory) return;

  tabStatistics.addEventListener('click', () => {
    // Activate statistics tab
    tabStatistics.classList.add('active');
    tabHistory.classList.remove('active');
    viewStatistics.classList.add('active');
    viewHistory.classList.remove('active');
  });

  tabHistory.addEventListener('click', () => {
    // Activate history tab
    tabHistory.classList.add('active');
    tabStatistics.classList.remove('active');
    viewHistory.classList.add('active');
    viewStatistics.classList.remove('active');

    // Load history when tab is opened (lazy loading)
    renderHistory();
  });
}

/**
 * Initialize popup
 */
async function initialize(): Promise<void> {
  try {
    setupTabs();
    await renderStatistics();
  } catch (error) {
    console.error('Failed to initialize popup:', error);
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}
