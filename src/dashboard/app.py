"""Flask application for statistics dashboard."""
import logging
from flask import Flask

logger = logging.getLogger(__name__)


def create_app(database_path: str) -> Flask:
    """
    Create and configure Flask application.

    Args:
        database_path: Path to SQLite database

    Returns:
        Configured Flask application instance
    """
    app = Flask(__name__)

    # Store database path in app config
    app.config['DATABASE_PATH'] = database_path

    # Register routes
    from src.dashboard.routes import register_routes
    register_routes(app)

    logger.info(f"Dashboard app created with database: {database_path}")

    return app
