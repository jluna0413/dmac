"""
Configuration module for DMac.
"""

import os
import yaml

# Import security utilities
try:
    from utils.config_validator import apply_defaults, validate_config
    from utils.secure_file import set_secure_permissions
    from utils.secure_logging import get_logger

    # Use secure logger if available
    logger = get_logger('dmac.config')
    security_enabled = True
except ImportError:
    # Fall back to standard logging if security utilities are not available
    import logging
    logger = logging.getLogger('dmac.config')
    security_enabled = False

class Config:
    """Configuration class for DMac."""

    def __init__(self, config_path=None):
        """Initialize the configuration.

        Args:
            config_path: Path to the configuration file.
        """
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), 'config.yaml')
        self.config = self._load_config()

    def _load_config(self):
        """Load the configuration from the YAML file."""
        if not os.path.exists(self.config_path):
            logger.warning(f"Configuration file not found: {self.config_path}")
            return self._create_default_config()

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)

            logger.info(f"Loaded configuration from {self.config_path}")

            # Validate configuration if security is enabled
            if security_enabled:
                errors = validate_config(config)
                if errors:
                    for error in errors:
                        logger.warning(f"Configuration validation error: {error}")
                    logger.warning("Using default values for invalid configuration")
                    config = apply_defaults(config)

            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._create_default_config()

    def _create_default_config(self):
        """Create a default configuration."""
        logger.info("Creating default configuration")

        default_config = {
            'orchestration': {
                'max_agents': 10,
                'logging_level': 'INFO',
                'versioning': True,
            },
            'agents': {
                'coding': {
                    'enabled': True,
                    'model': 'deepseek-rl',
                },
                'manufacturing': {
                    'enabled': True,
                    'model': 'gemini',
                },
                'design': {
                    'enabled': True,
                    'model': 'gemini',
                },
                'ui': {
                    'enabled': True,
                    'model': 'deepseek-rl',
                },
                'iot': {
                    'enabled': False,
                    'model': 'gemini',
                },
            },
            'models': {
                'deepclaude': {
                    'gemini_api_key': '',
                    'deepseek_model_path': '',
                },
                'gemini': {
                    'api_key': '',
                    'api_url': 'http://gemini.google.com',
                },
                'deepseek': {
                    'model_path': '',
                    'version': '0.324',
                },
                'local': {
                    'model_name': 'gemma3:12b',
                },
            },
            'integrations': {
                'voice': {
                    'enabled': True,
                    'engine': 'CoquiSST',
                },
                'cli': {
                    'enabled': True,
                    'engine': 'Cline',
                },
                'design': {
                    'enabled': True,
                    'blender_path': '',
                    'ue5_path': '',
                },
                'manufacturing': {
                    'enabled': True,
                    '3d_printing': {
                        'klipper_enabled': True,
                        'octoprint_url': 'http://localhost:5000',
                        'slicer_path': '',
                    },
                    'cnc': {
                        'enabled': False,
                        'controller_path': '',
                    },
                    'laser': {
                        'enabled': False,
                        'controller_path': '',
                    },
                    'packaging': {
                        'enabled': False,
                        'cricut_path': '',
                    },
                },
            },
            'ui': {
                'dashboard': {
                    'enabled': True,
                    'port': 8079,
                    'host': 'localhost',
                },
                'swarmui': {
                    'enabled': True,
                    'port': 8080,
                    'host': 'localhost',
                },
                'comfyui': {
                    'enabled': True,
                    'port': 8081,
                    'host': 'localhost',
                },
                'opencanvas': {
                    'enabled': True,
                    'port': 8082,
                    'host': 'localhost',
                },
            },
            'security': {
                'rate_limit': {
                    'enabled': True,
                    'max_requests': 100,
                    'time_window': 60,
                },
                'auth': {
                    'enabled': True,
                    'session_expiry': 3600,
                },
                'encryption': {
                    'enabled': True,
                    'key_file': 'config/encryption_key.key',
                },
            },
        }

        # Create the config directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

        # Save the default configuration
        with open(self.config_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

        return default_config

    def get(self, key, default=None):
        """Get a configuration value.

        Args:
            key: The configuration key.
            default: The default value if the key doesn't exist.

        Returns:
            The configuration value.
        """
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key, value):
        """Set a configuration value.

        Args:
            key: The configuration key.
            value: The configuration value.
        """
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

        # Save the updated configuration
        self.save()

    def save(self):
        """Save the configuration to the YAML file."""
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            # Save the configuration
            with open(self.config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)

            # Set secure permissions if security is enabled
            if security_enabled:
                set_secure_permissions(self.config_path, owner_only=False)

            logger.info(f"Saved configuration to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False


# Create a singleton instance
config = Config()
