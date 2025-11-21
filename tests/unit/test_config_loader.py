"""Unit tests for ConfigLoader YAML parsing and validation."""
import os
import tempfile
import pytest
import yaml

from src.config.loader import ConfigLoader


class TestConfigLoader:
    """Test ConfigLoader class functionality."""

    @pytest.fixture
    def temp_config_file(self):
        """Create temporary config file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name

        yield config_path

        # Cleanup
        if os.path.exists(config_path):
            os.remove(config_path)

    def test_load_with_no_config_file_uses_defaults(self):
        """Test load() uses defaults when config file doesn't exist."""
        loader = ConfigLoader('nonexistent.yaml')
        config = loader.load()

        assert config['proxy']['port'] == 8080
        assert config['proxy']['listen_address'] == '127.0.0.1'
        assert config['dashboard']['port'] == 8081
        assert config['dashboard']['listen_address'] == '127.0.0.1'
        assert config['logging']['level'] == 'INFO'
        assert config['detection']['callback_timeout'] == 60

    def test_load_with_config_file_merges_values(self, temp_config_file):
        """Test load() merges file config over defaults."""
        file_config = {
            'proxy': {
                'port': 9090
            },
            'logging': {
                'level': 'DEBUG'
            }
        }

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        config = loader.load()

        # File values should override defaults
        assert config['proxy']['port'] == 9090
        assert config['logging']['level'] == 'DEBUG'

        # Non-overridden values should remain from defaults
        assert config['proxy']['listen_address'] == '127.0.0.1'
        assert config['dashboard']['port'] == 8081

    def test_load_with_empty_file_uses_defaults(self, temp_config_file):
        """Test load() handles empty YAML file gracefully."""
        # Create empty file
        with open(temp_config_file, 'w') as f:
            f.write('')

        loader = ConfigLoader(temp_config_file)
        config = loader.load()

        assert config['proxy']['port'] == 8080

    def test_validation_rejects_invalid_proxy_port_too_low(self, temp_config_file):
        """Test validation rejects proxy port < 1024."""
        file_config = {'proxy': {'port': 80}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)

        with pytest.raises(ValueError, match="Invalid proxy port"):
            loader.load()

    def test_validation_rejects_invalid_proxy_port_too_high(self, temp_config_file):
        """Test validation rejects proxy port > 65535."""
        file_config = {'proxy': {'port': 70000}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)

        with pytest.raises(ValueError, match="Invalid proxy port"):
            loader.load()

    def test_validation_rejects_invalid_dashboard_port(self, temp_config_file):
        """Test validation rejects dashboard port < 1024."""
        file_config = {'dashboard': {'port': 500}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)

        with pytest.raises(ValueError, match="Invalid dashboard port"):
            loader.load()

    def test_validation_rejects_duplicate_ports(self, temp_config_file):
        """Test validation rejects same port for proxy and dashboard."""
        file_config = {
            'proxy': {'port': 8080},
            'dashboard': {'port': 8080}
        }

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)

        with pytest.raises(ValueError, match="Proxy and dashboard ports must be different"):
            loader.load()

    def test_validation_rejects_invalid_log_level(self, temp_config_file):
        """Test validation rejects invalid logging level."""
        file_config = {'logging': {'level': 'INVALID'}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)

        with pytest.raises(ValueError, match="Invalid log level"):
            loader.load()

    def test_validation_accepts_all_valid_log_levels(self, temp_config_file):
        """Test validation accepts all standard log levels."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

        for level in valid_levels:
            file_config = {'logging': {'level': level}}

            with open(temp_config_file, 'w') as f:
                yaml.dump(file_config, f)

            loader = ConfigLoader(temp_config_file)
            config = loader.load()

            assert config['logging']['level'].upper() == level

    def test_validation_handles_lowercase_log_level(self, temp_config_file):
        """Test validation converts lowercase log level to uppercase."""
        file_config = {'logging': {'level': 'debug'}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        config = loader.load()

        assert config['logging']['level'] == 'debug'  # Original preserved in config

    def test_validation_rejects_callback_timeout_too_low(self, temp_config_file):
        """Test validation rejects callback timeout < 1."""
        file_config = {'detection': {'callback_timeout': 0}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)

        with pytest.raises(ValueError, match="Invalid callback timeout"):
            loader.load()

    def test_validation_rejects_callback_timeout_too_high(self, temp_config_file):
        """Test validation rejects callback timeout > 300."""
        file_config = {'detection': {'callback_timeout': 500}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)

        with pytest.raises(ValueError, match="Invalid callback timeout"):
            loader.load()

    def test_path_expansion_for_database_path(self, temp_config_file):
        """Test ~ is expanded in database_path."""
        file_config = {'storage': {'database_path': '~/test.db'}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        config = loader.load()

        expected = os.path.expanduser('~/test.db')
        assert config['storage']['database_path'] == expected

    def test_path_expansion_for_log_dir(self, temp_config_file):
        """Test ~ is expanded in log_dir."""
        file_config = {'logging': {'log_dir': '~/logs'}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        config = loader.load()

        expected = os.path.expanduser('~/logs')
        assert config['logging']['log_dir'] == expected

    def test_get_method_with_simple_key(self, temp_config_file):
        """Test get() retrieves simple top-level value."""
        file_config = {'proxy': {'port': 9090}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        loader.load()

        assert loader.get('proxy') == {'port': 9090, 'listen_address': '127.0.0.1', 'upstream_proxy': None}

    def test_get_method_with_dotted_key(self, temp_config_file):
        """Test get() retrieves nested value with dot notation."""
        file_config = {'proxy': {'port': 9090}}

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        loader.load()

        assert loader.get('proxy.port') == 9090

    def test_get_method_with_nonexistent_key_returns_default(self, temp_config_file):
        """Test get() returns default for nonexistent key."""
        loader = ConfigLoader(temp_config_file)
        loader.load()

        assert loader.get('nonexistent.key', 'default_value') == 'default_value'

    def test_get_method_with_nonexistent_key_no_default_returns_none(self, temp_config_file):
        """Test get() returns None for nonexistent key when no default."""
        loader = ConfigLoader(temp_config_file)
        loader.load()

        assert loader.get('nonexistent.key') is None

    def test_deep_merge_preserves_non_overlapping_keys(self, temp_config_file):
        """Test merge preserves keys from both config and defaults."""
        file_config = {
            'proxy': {
                'port': 9090,
                'custom_option': 'value'
            }
        }

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        config = loader.load()

        # File value
        assert config['proxy']['port'] == 9090
        # File-only value
        assert config['proxy']['custom_option'] == 'value'
        # Default value
        assert config['proxy']['listen_address'] == '127.0.0.1'

    def test_load_with_upstream_proxy(self, temp_config_file):
        """Test upstream_proxy configuration is loaded correctly."""
        file_config = {
            'proxy': {
                'upstream_proxy': 'http://corporate-proxy:3128'
            }
        }

        with open(temp_config_file, 'w') as f:
            yaml.dump(file_config, f)

        loader = ConfigLoader(temp_config_file)
        config = loader.load()

        assert config['proxy']['upstream_proxy'] == 'http://corporate-proxy:3128'

    def test_defaults_include_all_required_sections(self):
        """Test DEFAULTS includes all required configuration sections."""
        defaults = ConfigLoader.DEFAULTS

        assert 'proxy' in defaults
        assert 'dashboard' in defaults
        assert 'storage' in defaults
        assert 'logging' in defaults
        assert 'detection' in defaults

    def test_defaults_have_sensible_values(self):
        """Test default values are sensible and complete."""
        defaults = ConfigLoader.DEFAULTS

        # Proxy
        assert defaults['proxy']['port'] == 8080
        assert defaults['proxy']['listen_address'] == '127.0.0.1'
        assert defaults['proxy']['upstream_proxy'] is None

        # Dashboard
        assert defaults['dashboard']['port'] == 8081
        assert defaults['dashboard']['listen_address'] == '127.0.0.1'

        # Storage
        assert '~/.microsoft-login-counter/events.db' in defaults['storage']['database_path']

        # Logging
        assert defaults['logging']['level'] == 'INFO'
        assert '~/.microsoft-login-counter/logs' in defaults['logging']['log_dir']
        assert defaults['logging']['max_size_mb'] == 10
        assert defaults['logging']['backup_count'] == 5

        # Detection
        assert defaults['detection']['callback_timeout'] == 60
