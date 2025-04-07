"""
Configuration module for DMac.
"""

import os
import json
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
        self.agent_config_path = os.path.join(os.path.dirname(__file__), 'agent_config.json')
        self.model_config_path = os.path.join(os.path.dirname(__file__), 'model_config.json')

        # Load the main configuration
        self.config = self._load_config()

        # Load additional configurations
        self._load_agent_config()
        self._load_model_config()

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

    def _load_agent_config(self):
        """Load the agent configuration from the JSON file."""
        if not os.path.exists(self.agent_config_path):
            logger.warning(f"Agent configuration file not found: {self.agent_config_path}")
            return

        try:
            with open(self.agent_config_path, 'r') as f:
                agent_config = json.load(f)

            # Merge with main config
            if 'agents' not in self.config:
                self.config['agents'] = {}

            self.config['agents'].update(agent_config.get('agents', {}))

            # Add benchmarking config
            if 'benchmarking' not in self.config:
                self.config['benchmarking'] = {}

            self.config['benchmarking'].update(agent_config.get('benchmarking', {}))

            # Add task routing config
            if 'task_routing' not in self.config:
                self.config['task_routing'] = {}

            self.config['task_routing'].update(agent_config.get('task_routing', {}))

            # Add reinforcement learning config
            if 'reinforcement_learning' not in self.config:
                self.config['reinforcement_learning'] = {}

            self.config['reinforcement_learning'].update(agent_config.get('reinforcement_learning', {}))

            logger.info(f"Loaded agent configuration from {self.agent_config_path}")
        except Exception as e:
            logger.error(f"Error loading agent configuration: {e}")

    def _load_model_config(self):
        """Load the model configuration from the JSON file."""
        if not os.path.exists(self.model_config_path):
            logger.warning(f"Model configuration file not found: {self.model_config_path}")
            return

        try:
            with open(self.model_config_path, 'r') as f:
                model_config = json.load(f)

            # Merge with main config
            if 'models' not in self.config:
                self.config['models'] = {}

            # Add default provider and model
            self.config['models']['default_provider'] = model_config.get('default_provider', 'ollama')
            self.config['models']['default_model'] = model_config.get('default_model', 'gemma:7b')

            # Add Ollama config
            if 'ollama' not in self.config['models']:
                self.config['models']['ollama'] = {}

            self.config['models']['ollama'].update(model_config.get('ollama', {}))

            # Add DeepSeek config
            if 'deepseek' not in self.config['models']:
                self.config['models']['deepseek'] = {}

            self.config['models']['deepseek'].update(model_config.get('deepseek', {}))

            logger.info(f"Loaded model configuration from {self.model_config_path}")
        except Exception as e:
            logger.error(f"Error loading model configuration: {e}")

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
                    'model_name': 'deepseek-coder',
                    'learning_enabled': True,
                    'learning_rate': 0.001,
                    'batch_size': 32,
                    'epochs': 10,
                    'evaluation_interval': 100,
                },
                'local': {
                    'model_name': 'gemma3:12b',
                },
                'ollama': {
                    'enabled': True,
                    'api_url': 'http://localhost:11434',
                    'models': ['llama2', 'mistral', 'gemma'],
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
            'webarena': {
                'enabled': True,
                'dir': 'external/webarena',
                'data_dir': 'data/webarena',
                'max_concurrent_runs': 2,
                'default_timeout': 3600,
                'ollama': {
                    'enabled': True,
                    'default_system_prompt': "You are a helpful AI assistant that controls a web browser to help users with their tasks."
                },
                'visualization': {
                    'enabled': True
                }
            },
            'dashboard': {
                'enabled': True,
                'host': '0.0.0.0',
                'port': 8080,
                'static_dir': 'dashboard/static',
                'templates_dir': 'dashboard/templates'
            },
            'api': {
                'enabled': True,
                'host': '0.0.0.0',
                'port': 8000
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
