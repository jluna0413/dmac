"""
Secure logging utilities for DMac.

This module provides a secure logger that redacts sensitive information.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union


class SecureLogger:
    """Secure logger that redacts sensitive information."""
    
    def __init__(self, name: str):
        """Initialize the secure logger.
        
        Args:
            name: The logger name.
        """
        self.logger = logging.getLogger(name)
        
        # Patterns to redact (pattern, replacement)
        self.patterns: List[Tuple[str, str]] = [
            # API keys and tokens
            (r'api[_-]?key[=:]\s*[\w\-\.]+', 'api_key=REDACTED'),
            (r'api[_-]?token[=:]\s*[\w\-\.]+', 'api_token=REDACTED'),
            (r'access[_-]?token[=:]\s*[\w\-\.]+', 'access_token=REDACTED'),
            (r'auth[_-]?token[=:]\s*[\w\-\.]+', 'auth_token=REDACTED'),
            (r'bearer\s+[\w\-\.]+', 'bearer REDACTED'),
            
            # Passwords
            (r'password[=:]\s*\S+', 'password=REDACTED'),
            (r'passwd[=:]\s*\S+', 'passwd=REDACTED'),
            (r'secret[=:]\s*\S+', 'secret=REDACTED'),
            
            # Personal information
            (r'\b\d{3}[-\.\s]?\d{2}[-\.\s]?\d{4}\b', 'SSN-REDACTED'),  # US SSN
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL-REDACTED'),  # Email
            (r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', 'PHONE-REDACTED'),  # Phone
            
            # Credit card numbers
            (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', 'CC-REDACTED'),  # Credit card
            (r'\b\d{13,16}\b', 'CC-REDACTED'),  # Credit card without separators
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [(re.compile(pattern), replacement) for pattern, replacement in self.patterns]
    
    def _redact(self, message: str) -> str:
        """Redact sensitive information from a log message.
        
        Args:
            message: The log message.
            
        Returns:
            The redacted message.
        """
        if not isinstance(message, str):
            return str(message)
        
        redacted = message
        for pattern, replacement in self.compiled_patterns:
            redacted = pattern.sub(replacement, redacted)
        return redacted
    
    def _redact_args(self, args: tuple) -> tuple:
        """Redact sensitive information from log arguments.
        
        Args:
            args: The log arguments.
            
        Returns:
            The redacted arguments.
        """
        return tuple(self._redact(arg) if isinstance(arg, str) else arg for arg in args)
    
    def _redact_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Redact sensitive information from log keyword arguments.
        
        Args:
            kwargs: The log keyword arguments.
            
        Returns:
            The redacted keyword arguments.
        """
        return {k: self._redact(v) if isinstance(v, str) else v for k, v in kwargs.items()}
    
    def debug(self, message: Any, *args, **kwargs):
        """Log a debug message with sensitive information redacted."""
        self.logger.debug(self._redact(message), *self._redact_args(args), **self._redact_kwargs(kwargs))
    
    def info(self, message: Any, *args, **kwargs):
        """Log an info message with sensitive information redacted."""
        self.logger.info(self._redact(message), *self._redact_args(args), **self._redact_kwargs(kwargs))
    
    def warning(self, message: Any, *args, **kwargs):
        """Log a warning message with sensitive information redacted."""
        self.logger.warning(self._redact(message), *self._redact_args(args), **self._redact_kwargs(kwargs))
    
    def error(self, message: Any, *args, **kwargs):
        """Log an error message with sensitive information redacted."""
        self.logger.error(self._redact(message), *self._redact_args(args), **self._redact_kwargs(kwargs))
    
    def critical(self, message: Any, *args, **kwargs):
        """Log a critical message with sensitive information redacted."""
        self.logger.critical(self._redact(message), *self._redact_args(args), **self._redact_kwargs(kwargs))
    
    def exception(self, message: Any, *args, exc_info=True, **kwargs):
        """Log an exception message with sensitive information redacted."""
        self.logger.exception(self._redact(message), *self._redact_args(args), exc_info=exc_info, **self._redact_kwargs(kwargs))
    
    def log(self, level: int, message: Any, *args, **kwargs):
        """Log a message with the specified level with sensitive information redacted."""
        self.logger.log(level, self._redact(message), *self._redact_args(args), **self._redact_kwargs(kwargs))
    
    @property
    def level(self) -> int:
        """Get the logger level."""
        return self.logger.level
    
    @level.setter
    def level(self, level: int):
        """Set the logger level."""
        self.logger.setLevel(level)


def get_logger(name: str) -> SecureLogger:
    """Get a secure logger.
    
    Args:
        name: The logger name.
        
    Returns:
        A secure logger.
    """
    return SecureLogger(name)
