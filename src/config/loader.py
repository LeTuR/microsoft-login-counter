"""Configuration loading and validation."""
import yaml
import os
from pathlib import Path
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and validate configuration from YAML file."""
    
    # Default configuration values
    DEFAULTS = {
        'proxy': {
            'port': 8080,
            'listen_address': '127.0.0.1',
            'upstream_proxy': None
        },
        'dashboard': {
            'port': 8081,
            'listen_address': '127.0.0.1'
        },
        'storage': {
            'database_path': '~/.microsoft-login-counter/events.db'
        },
        'logging': {
            'level': 'INFO',
            'log_dir': '~/.microsoft-login-counter/logs',
            'max_size_mb': 10,
            'backup_count': 5
        },
        'detection': {
            'callback_timeout': 60
        }
    }
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config: Dict[str, Any] = {}
        
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file with defaults.
        
        Returns:
            Dict containing merged configuration (file + defaults)
        """
        # Start with defaults
        self.config = self._deep_copy_dict(self.DEFAULTS)
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                file_config = yaml.safe_load(f) or {}
            
            # Merge file config over defaults
            self.config = self._merge_configs(self.config, file_config)
            logger.info(f"Configuration loaded from: {self.config_path}")
        else:
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
        
        # Validate configuration
        self._validate()
        
        # Expand paths (~ to home directory)
        self._expand_paths()
        
        return self.config
    
    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """
        Recursively merge two configuration dictionaries.
        
        Args:
            base: Base configuration (defaults)
            override: Override configuration (from file)
            
        Returns:
            Merged configuration dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def _deep_copy_dict(self, d: Dict) -> Dict:
        """Deep copy a dictionary."""
        result = {}
        for key, value in d.items():
            if isinstance(value, dict):
                result[key] = self._deep_copy_dict(value)
            else:
                result[key] = value
        return result
    
    def _validate(self):
        """Validate configuration values."""
        # Validate ports
        proxy_port = self.config['proxy']['port']
        dashboard_port = self.config['dashboard']['port']
        
        if not (1024 <= proxy_port <= 65535):
            raise ValueError(f"Invalid proxy port: {proxy_port} (must be 1024-65535)")
        
        if not (1024 <= dashboard_port <= 65535):
            raise ValueError(f"Invalid dashboard port: {dashboard_port} (must be 1024-65535)")
        
        if proxy_port == dashboard_port:
            raise ValueError("Proxy and dashboard ports must be different")
        
        # Validate logging level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        log_level = self.config['logging']['level'].upper()
        if log_level not in valid_levels:
            raise ValueError(f"Invalid log level: {log_level} (must be one of {valid_levels})")
        
        # Validate callback timeout
        timeout = self.config['detection']['callback_timeout']
        if not (1 <= timeout <= 300):
            raise ValueError(f"Invalid callback timeout: {timeout} (must be 1-300 seconds)")
        
        logger.info("Configuration validated successfully")
    
    def _expand_paths(self):
        """Expand ~ in file paths to home directory."""
        self.config['storage']['database_path'] = os.path.expanduser(
            self.config['storage']['database_path']
        )
        self.config['logging']['log_dir'] = os.path.expanduser(
            self.config['logging']['log_dir']
        )
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path.
        
        Args:
            key_path: Dot-separated path (e.g., 'proxy.port')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
