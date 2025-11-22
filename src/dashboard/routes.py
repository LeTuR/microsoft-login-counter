"""Dashboard routes for statistics display."""
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, current_app, jsonify, request

from src.storage.repository import Repository, get_aggregated_graph_data
from src.storage.models import TimePeriod, TimePeriodFilter
from src.dashboard.stats import compute_statistics

logger = logging.getLogger(__name__)


def get_statistics():
    """
    Get login statistics from database.

    Returns:
        LoginStatistics object or None if database unavailable
    """
    try:
        db_path = current_app.config['DATABASE_PATH']
        repository = Repository(db_path)
        stats = compute_statistics(repository)
        repository.close()
        return stats
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return None


def register_routes(app: Flask):
    """
    Register dashboard routes.

    Args:
        app: Flask application instance
    """

    @app.route('/')
    def index():
        """Display statistics dashboard."""
        stats = get_statistics()

        if stats is None:
            return render_template('error.html',
                                   message="Unable to load statistics from database"), 500

        return render_template('index.html', stats=stats)

    @app.route('/api/graph-data')
    def graph_data():
        """
        Get aggregated graph data for specified time period.

        Query Parameters:
            period: Time period filter ("24h", "7d", "30d", "all")

        Returns:
            JSON response with aggregated data points
        """
        period_param = request.args.get('period', '7d')

        # Parse period parameter
        period_map = {
            '24h': TimePeriod.LAST_24H,
            '7d': TimePeriod.LAST_7D,
            '30d': TimePeriod.LAST_30D,
            'all': TimePeriod.ALL_TIME
        }

        if period_param not in period_map:
            return jsonify({'error': 'Invalid period parameter'}), 400

        period = period_map[period_param]

        # Calculate date range
        now = datetime.utcnow()
        if period == TimePeriod.LAST_24H:
            start_date = now - timedelta(hours=24)
        elif period == TimePeriod.LAST_7D:
            start_date = now - timedelta(days=7)
        elif period == TimePeriod.LAST_30D:
            start_date = now - timedelta(days=30)
        else:  # ALL_TIME
            start_date = datetime(2020, 1, 1)  # Far back enough

        time_filter = TimePeriodFilter(
            period=period,
            start_date=start_date,
            end_date=now
        )

        # Get aggregated data
        try:
            db_path = current_app.config['DATABASE_PATH']
            data_points = get_aggregated_graph_data(db_path, time_filter)

            # Determine aggregation level
            from src.storage.repository import determine_aggregation_level
            aggregation = determine_aggregation_level(start_date, now)

            # Calculate total events
            total_events = sum(point.count for point in data_points)

            response = {
                'dataPoints': [point.to_dict() for point in data_points],
                'period': period_param,
                'aggregationLevel': aggregation,
                'totalEvents': total_events,
                'dateRange': {
                    'start': start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'end': now.strftime('%Y-%m-%dT%H:%M:%SZ')
                }
            }

            return jsonify(response), 200

        except Exception as e:
            logger.error(f"Error getting graph data: {e}")
            return jsonify({'error': 'Internal server error'}), 500

    @app.route('/api/statistics')
    def statistics():
        """
        Get current login statistics.

        Returns:
            JSON response with login counts for today/week/month/all-time
        """
        stats = get_statistics()

        if stats is None:
            return jsonify({'error': 'Internal server error'}), 500

        return jsonify(stats.to_dict()), 200

    logger.info("Dashboard routes registered")
