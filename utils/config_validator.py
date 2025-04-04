"""
Configuration validation utilities for DMac.

This module provides utilities for validating configuration values.
"""

from typing import Any, Dict, List

from utils.secure_logging import get_logger

logger = get_logger('dmac.utils.config_validator')


class ConfigValidator:
    """Configuration validator."""

    def __init__(self, config_dict: Dict[str, Any]):
        """Initialize the configuration validator.

        Args:
            config_dict: The configuration dictionary.
        """
        self.config = config_dict
        self.validation_rules = {
            # UI configuration
            'ui.dashboard.port': {'type': int, 'min': 1024, 'max': 65535, 'required': True},
            'ui.dashboard.host': {'type': str, 'allowed': ['localhost', '127.0.0.1', '0.0.0.0'], 'required': True},
            'ui.dashboard.enabled': {'type': bool, 'required': True},

            'ui.swarmui.port': {'type': int, 'min': 1024, 'max': 65535, 'required': True},
            'ui.swarmui.host': {'type': str, 'allowed': ['localhost', '127.0.0.1', '0.0.0.0'], 'required': True},
            'ui.swarmui.enabled': {'type': bool, 'required': True},

            'ui.comfyui.port': {'type': int, 'min': 1024, 'max': 65535, 'required': True},
            'ui.comfyui.host': {'type': str, 'allowed': ['localhost', '127.0.0.1', '0.0.0.0'], 'required': True},
            'ui.comfyui.enabled': {'type': bool, 'required': True},

            'ui.opencanvas.port': {'type': int, 'min': 1024, 'max': 65535, 'required': True},
            'ui.opencanvas.host': {'type': str, 'allowed': ['localhost', '127.0.0.1', '0.0.0.0'], 'required': True},
            'ui.opencanvas.enabled': {'type': bool, 'required': True},

            # Model configuration
            'models.gemini.api_url': {'type': str, 'required': True},
            'models.gemini.usage_cap': {'type': int, 'min': 0, 'required': True},

            'models.deepseek.model_name': {'type': str, 'required': True, 'default': 'GandalfBaum/deepseek_r1-claude3.7'},
            'models.deepseek.learning_enabled': {'type': bool, 'required': True, 'default': True},
            'models.deepseek.learning_rate': {'type': float, 'min': 0, 'required': True, 'default': 0.001},
            'models.deepseek.batch_size': {'type': int, 'min': 1, 'required': True, 'default': 32},
            'models.deepseek.epochs': {'type': int, 'min': 1, 'required': True, 'default': 10},
            'models.deepseek.evaluation_interval': {'type': int, 'min': 1, 'required': True, 'default': 100},

            'models.local.model_name': {'type': str, 'required': True, 'default': 'gemma3:12b'},

            'models.ollama.api_url': {'type': str, 'required': True, 'default': 'http://localhost:11434'},
            'models.ollama.models_dir': {'type': str, 'required': True, 'default': 'models/ollama'},

            # Learning system configuration
            'learning.enabled': {'type': bool, 'required': True, 'default': True},
            'learning.data_dir': {'type': str, 'required': True, 'default': 'models/learning_data'},
            'learning.feedback_dir': {'type': str, 'required': True, 'default': 'models/feedback_data'},
            'learning.max_examples': {'type': int, 'min': 1, 'required': True, 'default': 10000},

            # Security configuration
            'security.rate_limit.enabled': {'type': bool, 'required': True, 'default': True},
            'security.rate_limit.max_requests': {'type': int, 'min': 1, 'required': True, 'default': 100},
            'security.rate_limit.time_window': {'type': int, 'min': 1, 'required': True, 'default': 60},

            'security.auth.enabled': {'type': bool, 'required': True, 'default': True},
            'security.auth.session_expiry': {'type': int, 'min': 60, 'required': True, 'default': 3600},

            'security.encryption.enabled': {'type': bool, 'required': True, 'default': True},
            'security.encryption.key_file': {'type': str, 'required': True, 'default': 'config/encryption_key.key'},
        }

    def validate(self) -> List[str]:
        """Validate the configuration.

        Returns:
            A list of validation errors, or an empty list if validation passed.
        """
        errors = []

        for key, rules in self.validation_rules.items():
            # Get the value from the nested dictionary
            value = self._get_nested_value(key)

            # Check if the value exists
            if value is None:
                if rules.get('required', False):
                    errors.append(f"Missing required configuration: {key}")
                continue

            # Type validation
            if 'type' in rules:
                expected_type = rules['type']
                if not isinstance(value, expected_type):
                    errors.append(f"Invalid type for {key}: expected {expected_type.__name__}, got {type(value).__name__}")
                    continue

            # Range validation for numbers
            if isinstance(value, (int, float)):
                if 'min' in rules and value < rules['min']:
                    errors.append(f"Value for {key} is too small: {value} < {rules['min']}")
                if 'max' in rules and value > rules['max']:
                    errors.append(f"Value for {key} is too large: {value} > {rules['max']}")

            # Allowed values validation
            if 'allowed' in rules and value not in rules['allowed']:
                errors.append(f"Invalid value for {key}: {value} not in {rules['allowed']}")

        return errors

    def _get_nested_value(self, key: str) -> Any:
        """Get a value from a nested dictionary using dot notation.

        Args:
            key: The key in dot notation (e.g., 'ui.dashboard.port').

        Returns:
            The value, or None if the key does not exist.
        """
        parts = key.split('.')
        value = self.config

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return None

        return value

    def apply_defaults(self) -> Dict[str, Any]:
        """Apply default values to missing configuration.

        Returns:
            The updated configuration dictionary.
        """
        for key, rules in self.validation_rules.items():
            # Skip if the key already exists
            if self._get_nested_value(key) is not None:
                continue

            # Skip if there's no default value
            if 'default' not in rules:
                continue

            # Set the default value
            self._set_nested_value(key, rules['default'])

        return self.config

    def _set_nested_value(self, key: str, value: Any) -> None:
        """Set a value in a nested dictionary using dot notation.

        Args:
            key: The key in dot notation (e.g., 'ui.dashboard.port').
            value: The value to set.
        """
        parts = key.split('.')
        current = self.config

        # Create nested dictionaries if they don't exist
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the value
        current[parts[-1]] = value


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Validate a configuration dictionary.

    Args:
        config: The configuration dictionary.

    Returns:
        A list of validation errors, or an empty list if validation passed.
    """
    validator = ConfigValidator(config)
    return validator.validate()


def apply_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply default values to missing configuration.

    Args:
        config: The configuration dictionary.

    Returns:
        The updated configuration dictionary.
    """
    validator = ConfigValidator(config)
    return validator.apply_defaults()
