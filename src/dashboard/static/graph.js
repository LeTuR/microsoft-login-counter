/**
 * Login trends bar chart visualization with gradient colors
 */

let chartInstance = null;
let currentPeriod = '7d';
let autoRefreshInterval = null;

/**
 * Calculate gradient colors for bar chart based on count values.
 * Uses linear RGB interpolation from light blue to dark blue.
 *
 * @param {Array} dataPoints - Array of {bucket, count, timestamp} objects
 * @returns {Array} Array of RGB color strings
 */
function calculateGradientColors(dataPoints) {
    if (!dataPoints || dataPoints.length === 0) {
        return [];
    }

    // Light blue: rgb(173, 216, 230)
    // Dark blue: rgb(0, 61, 107)
    const lightBlue = { r: 173, g: 216, b: 230 };
    const darkBlue = { r: 0, g: 61, b: 107 };

    // Extract counts
    const counts = dataPoints.map(p => p.count);
    const min = Math.min(...counts);
    const max = Math.max(...counts);

    // Edge case: all counts are the same
    if (min === max) {
        // Use medium blue #0078d4
        const mediumBlue = 'rgb(0, 120, 212)';
        return dataPoints.map(() => mediumBlue);
    }

    // Calculate gradient color for each bar
    return counts.map(count => {
        // Normalize count to 0-1 range
        const normalized = (count - min) / (max - min);

        // Linear RGB interpolation
        const r = Math.round(lightBlue.r + (darkBlue.r - lightBlue.r) * normalized);
        const g = Math.round(lightBlue.g + (darkBlue.g - lightBlue.g) * normalized);
        const b = Math.round(lightBlue.b + (darkBlue.b - lightBlue.b) * normalized);

        return `rgb(${r}, ${g}, ${b})`;
    });
}

/**
 * Render or update the bar chart
 *
 * @param {Object} graphData - Response from /api/graph-data
 * @param {boolean} silentUpdate - If true, update without animation
 */
function renderGraph(graphData, silentUpdate = false) {
    const canvas = document.getElementById('login-graph');
    if (!canvas) return;

    const ctx = canvas.getContext('2d');

    // Extract data
    const labels = graphData.dataPoints.map(point => new Date(point.timestamp));
    const counts = graphData.dataPoints.map(point => point.count);
    const gradientColors = calculateGradientColors(graphData.dataPoints);

    // Chart configuration
    const config = {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Login Events',
                data: counts,
                backgroundColor: gradientColors,
                borderColor: '#fff',
                borderWidth: 1,
                barPercentage: 0.9,
                categoryPercentage: 0.8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        title: function(context) {
                            const date = context[0].parsed.x;
                            return new Date(date).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric'
                            });
                        },
                        label: function(context) {
                            return `Logins: ${context.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: graphData.aggregationLevel === 'week' ? 'week' : 'day',
                        displayFormats: {
                            day: 'MMM d',
                            week: 'MMM d'
                        }
                    },
                    title: {
                        display: true,
                        text: 'Date'
                    }
                },
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Login Count'
                    },
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    };

    if (chartInstance) {
        // Update existing chart
        chartInstance.data.labels = labels;
        chartInstance.data.datasets[0].data = counts;
        chartInstance.data.datasets[0].backgroundColor = gradientColors;
        chartInstance.options.scales.x.time.unit = graphData.aggregationLevel === 'week' ? 'week' : 'day';

        // Silent update (no animation) or normal update
        chartInstance.update(silentUpdate ? 'none' : undefined);
    } else {
        // Create new chart
        chartInstance = new Chart(ctx, config);
    }
}

/**
 * Load graph data from API
 *
 * @param {string} period - Time period ('24h', '7d', '30d', 'all')
 * @param {boolean} silentUpdate - If true, update chart without animation
 */
async function loadGraphData(period, silentUpdate = false) {
    try {
        const response = await fetch(`/api/graph-data?period=${period}`);

        if (!response.ok) {
            console.error('Failed to load graph data:', response.status);
            return;
        }

        const data = await response.json();
        renderGraph(data, silentUpdate);
    } catch (error) {
        console.error('Error loading graph data:', error);
    }
}

/**
 * Set up period filter button handlers
 */
function setupFilterButtons() {
    const buttons = document.querySelectorAll('.filter-btn');

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            // Update active state
            buttons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');

            // Load new period
            currentPeriod = this.dataset.period;
            loadGraphData(currentPeriod, false);
        });
    });
}

/**
 * Start auto-refresh interval
 */
function startAutoRefresh() {
    // Clear existing interval
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }

    // Auto-refresh every 5 seconds
    autoRefreshInterval = setInterval(() => {
        loadGraphData(currentPeriod, true);
    }, 5000);
}

/**
 * Initialize the graph on page load
 */
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('login-graph');
    if (!canvas) return;

    // Set up filter buttons
    setupFilterButtons();

    // Load initial data
    loadGraphData(currentPeriod, false);

    // Start auto-refresh
    startAutoRefresh();
});
