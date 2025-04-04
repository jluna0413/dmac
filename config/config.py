"""
Configuration module for DMac.
"""

import os
import yaml
from pathlib import Path

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
            return self._create_default_config()

        with open(self.config_path, 'r') as f:
            return yaml.safe_load(f)

    def _create_default_config(self):
        """Create a default configuration."""
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
                'swarmui': {
                    'enabled': True,
                    'port': 8080,
                },
                'comfyui': {
                    'enabled': True,
                    'port': 8081,
                },
                'opencanvas': {
                    'enabled': True,
                    'port': 8082,
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

        for i, k in enumerate(keys[:-1]):
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

        # Save the updated configuration
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def save(self):
        """Save the configuration to the YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)


# Create a singleton instance
config = Config()
