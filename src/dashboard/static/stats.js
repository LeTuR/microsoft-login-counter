/**
 * Statistics auto-refresh functionality
 * Polls /api/statistics every 5 seconds and updates the DOM
 */

let statsRefreshInterval = null;
let statElements = null;

/**
 * Load statistics from API and update DOM
 *
 * @param {boolean} silentUpdate - If true, update without logging (for auto-refresh)
 */
async function loadStatistics(silentUpdate = false) {
    try {
        const response = await fetch('/api/statistics');

        if (!response.ok) {
            console.error('Statistics API error:', response.status);
            return; // Keep last known values
        }

        const stats = await response.json();

        if (!silentUpdate) {
            console.log('Statistics loaded:', stats);
        }

        updateStatisticsDOM(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Keep last known values, retry on next cycle
    }
}

/**
 * Update statistics values in the DOM
 *
 * @param {Object} stats - Statistics data from API
 */
function updateStatisticsDOM(stats) {
    if (!statElements) {
        console.error('Stat elements not initialized');
        return;
    }

    // Update each statistic card value
    statElements.today.textContent = stats.today_count;
    statElements.week.textContent = stats.week_count;
    statElements.month.textContent = stats.month_count;
    statElements.total.textContent = stats.total_count;
}

/**
 * Cache DOM element references for statistics cards
 */
function cacheStatElements() {
    statElements = {
        today: document.querySelector('.stat-card:nth-child(1) .stat-value'),
        week: document.querySelector('.stat-card:nth-child(2) .stat-value'),
        month: document.querySelector('.stat-card:nth-child(3) .stat-value'),
        total: document.querySelector('.stat-card:nth-child(4) .stat-value')
    };

    // Validate all elements found
    const missing = Object.entries(statElements)
        .filter(([key, el]) => !el)
        .map(([key]) => key);

    if (missing.length > 0) {
        console.error('Missing stat elements:', missing);
        return false;
    }

    return true;
}

/**
 * Start auto-refresh interval
 */
function startStatsAutoRefresh() {
    // Clear existing interval
    if (statsRefreshInterval) {
        clearInterval(statsRefreshInterval);
    }

    // Auto-refresh every 5 seconds (matches graph refresh interval)
    statsRefreshInterval = setInterval(() => {
        loadStatistics(true); // Silent update
    }, 5000);

    console.log('Statistics auto-refresh started (5s interval)');
}

/**
 * Initialize statistics refresh on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    // Only run if we're on the stats page
    const statsContainer = document.querySelector('.stats-grid');
    if (!statsContainer) {
        return; // Not on stats page
    }

    // Cache DOM element references
    if (!cacheStatElements()) {
        console.error('Failed to initialize statistics refresh - missing DOM elements');
        return;
    }

    // Start auto-refresh
    startStatsAutoRefresh();

    console.log('Statistics refresh initialized');
});
