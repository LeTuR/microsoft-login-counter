"""Database connection and schema management."""
import sqlite3
import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Database:
    """SQLite database connection manager with schema initialization."""
    
    def __init__(self, database_path: str):
        """
        Initialize database connection.
        
        Args:
            database_path: Path to SQLite database file (supports ~ for home directory)
        """
        self.database_path = os.path.expanduser(database_path)
        self._ensure_database_directory()
        self.connection: Optional[sqlite3.Connection] = None
        
    def _ensure_database_directory(self):
        """Create database directory if it doesn't exist."""
        db_dir = os.path.dirname(self.database_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)
            logger.info(f"Database directory ensured: {db_dir}")
    
    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection with proper configuration.
        
        Returns:
            sqlite3.Connection: Database connection object
        """
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.database_path,
                check_same_thread=False  # Allow multi-threaded access
            )
            self.connection.row_factory = sqlite3.Row  # Dict-like row access
            logger.info(f"Database connected: {self.database_path}")
        return self.connection
    
    def initialize_schema(self):
        """Initialize database schema from schema.sql file."""
        schema_file = Path(__file__).parent / "schema.sql"
        
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        conn = self.connect()
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema (multiple statements)
        conn.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema initialized")
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with transaction handling."""
        if exc_type is not None:
            # Rollback on exception
            if self.connection:
                self.connection.rollback()
                logger.error(f"Transaction rolled back due to: {exc_val}")
        else:
            # Commit on success
            if self.connection:
                self.connection.commit()
        self.close()
        return False  # Don't suppress exceptions
