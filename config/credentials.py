"""
Secure credentials management for DMac.

This module provides secure ways to load and manage API keys and other sensitive credentials.
It prioritizes environment variables, then falls back to a local credentials file.
The credentials file should NEVER be committed to version control.
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger('dmac.config.credentials')

# Path to the credentials file
CREDENTIALS_FILE = Path(os.environ.get('DMAC_CREDENTIALS_FILE', 'config/credentials.json'))


class CredentialsManager:
    """Manager for secure credentials."""
    
    def __init__(self):
        """Initialize the credentials manager."""
        self.credentials = {}
        self._load_credentials()
    
    def _load_credentials(self) -> None:
        """Load credentials from environment variables and credentials file."""
        # First, try to load from credentials file
        self._load_from_file()
        
        # Then, override with environment variables (environment variables take precedence)
        self._load_from_env()
    
    def _load_from_file(self) -> None:
        """Load credentials from a JSON file."""
        if not CREDENTIALS_FILE.exists():
            logger.warning(f"Credentials file not found: {CREDENTIALS_FILE}")
            return
        
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                file_credentials = json.load(f)
            
            # Flatten nested dictionaries with dot notation
            flat_credentials = {}
            self._flatten_dict(file_credentials, flat_credentials)
            
            self.credentials.update(flat_credentials)
            logger.info(f"Loaded credentials from file: {CREDENTIALS_FILE}")
        except Exception as e:
            logger.error(f"Error loading credentials from file: {e}")
    
    def _flatten_dict(self, nested_dict: Dict[str, Any], flat_dict: Dict[str, Any], prefix: str = '') -> None:
        """Flatten a nested dictionary using dot notation.
        
        Args:
            nested_dict: The nested dictionary to flatten.
            flat_dict: The flat dictionary to update.
            prefix: The prefix to use for keys.
        """
        for key, value in nested_dict.items():
            new_key = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                self._flatten_dict(value, flat_dict, new_key)
            else:
                flat_dict[new_key] = value
    
    def _load_from_env(self) -> None:
        """Load credentials from environment variables."""
        # Look for environment variables with the DMAC_ prefix
        for key, value in os.environ.items():
            if key.startswith('DMAC_'):
                # Convert to lowercase and remove the prefix
                config_key = key[5:].lower().replace('_', '.')
                self.credentials[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a credential value.
        
        Args:
            key: The credential key.
            default: The default value to return if the key is not found.
            
        Returns:
            The credential value, or the default value if the key is not found.
        """
        return self.credentials.get(key, default)
    
    def has(self, key: str) -> bool:
        """Check if a credential exists.
        
        Args:
            key: The credential key.
            
        Returns:
            True if the credential exists, False otherwise.
        """
        return key in self.credentials


# Create a singleton instance
credentials = CredentialsManager()


def create_example_credentials_file() -> None:
    """Create an example credentials file."""
    example_file = Path('config/credentials.example.json')
    
    example_credentials = {
        "models": {
            "gemini": {
                "api_key": "your-gemini-api-key-here"
            },
            "openai": {
                "api_key": "your-openai-api-key-here"
            }
        },
        "integrations": {
            "github": {
                "token": "your-github-token-here"
            }
        }
    }
    
    with open(example_file, 'w') as f:
        json.dump(example_credentials, f, indent=2)
    
    logger.info(f"Created example credentials file: {example_file}")
    logger.info("Copy this file to config/credentials.json and add your actual credentials.")
    logger.info("IMPORTANT: Never commit credentials.json to version control!")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create an example credentials file
    create_example_credentials_file()
