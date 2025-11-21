"""Logging configuration setup."""
import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any


def setup_logging(config: Dict[str, Any]):
    """
    Configure logging with rotating file handler and console handler.
    
    Args:
        config: Configuration dictionary with logging settings
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO').upper())
    log_dir = log_config.get('log_dir', '~/.microsoft-login-counter/logs')
    log_dir = os.path.expanduser(log_dir)
    max_size_bytes = log_config.get('max_size_mb', 10) * 1024 * 1024
    backup_count = log_config.get('backup_count', 5)
    
    # Create log directory
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Rotating file handler
    log_file = os.path.join(log_dir, 'login-counter.log')
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_size_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    logging.info(f"Logging configured: level={log_level}, file={log_file}")
