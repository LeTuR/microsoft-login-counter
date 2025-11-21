"""Dashboard routes for statistics display."""
import logging
from flask import Flask, render_template, current_app

from src.storage.repository import Repository
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

    logger.info("Dashboard routes registered")
