"""
Error Handling for DMac.

This module provides error handling utilities for the DMac system.
"""

import asyncio
import functools
import logging
import sys
import traceback
from typing import Dict, List, Optional, Any, Callable, Awaitable, Type, TypeVar, Union

from config.config import config
from utils.secure_logging import get_logger

logger = get_logger('dmac.utils.error_handling')


class DMacError(Exception):
    """Base class for all DMac errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """Initialize the error.
        
        Args:
            message: The error message.
            code: Optional error code.
            details: Optional error details.
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary.
        
        Returns:
            A dictionary representation of the error.
        """
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            'code': self.code,
            'details': self.details,
        }
    
    def __str__(self) -> str:
        """Get a string representation of the error.
        
        Returns:
            A string representation of the error.
        """
        if self.code:
            return f"{self.__class__.__name__} [{self.code}]: {self.message}"
        else:
            return f"{self.__class__.__name__}: {self.message}"


class ConfigError(DMacError):
    """Error related to configuration."""
    pass


class SecurityError(DMacError):
    """Error related to security."""
    pass


class ModelError(DMacError):
    """Error related to models."""
    pass


class AgentError(DMacError):
    """Error related to agents."""
    pass


class TaskError(DMacError):
    """Error related to tasks."""
    pass


class LearningError(DMacError):
    """Error related to learning."""
    pass


class APIError(DMacError):
    """Error related to the API."""
    pass


class FileError(DMacError):
    """Error related to file operations."""
    pass


class ProcessError(DMacError):
    """Error related to process operations."""
    pass


class NetworkError(DMacError):
    """Error related to network operations."""
    pass


class DatabaseError(DMacError):
    """Error related to database operations."""
    pass


class ValidationError(DMacError):
    """Error related to validation."""
    pass


# Type variable for function return type
T = TypeVar('T')


def handle_errors(error_types: Optional[List[Type[Exception]]] = None, 
                 default_message: str = "An error occurred", 
                 log_traceback: bool = True) -> Callable:
    """Decorator to handle errors in a function.
    
    Args:
        error_types: Optional list of error types to catch.
        default_message: Default error message.
        log_traceback: Whether to log the traceback.
        
    Returns:
        A decorator function.
    """
    if error_types is None:
        error_types = [Exception]
    
    def decorator(func: Callable[..., T]) -> Callable[..., Union[T, DMacError]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, DMacError]:
            try:
                return func(*args, **kwargs)
            except tuple(error_types) as e:
                # Log the error
                if log_traceback:
                    logger.exception(f"Error in {func.__name__}: {e}")
                else:
                    logger.error(f"Error in {func.__name__}: {e}")
                
                # Convert the error to a DMacError if it's not already one
                if isinstance(e, DMacError):
                    return e
                else:
                    return DMacError(str(e) or default_message)
        
        return wrapper
    
    return decorator


def handle_async_errors(error_types: Optional[List[Type[Exception]]] = None, 
                       default_message: str = "An error occurred", 
                       log_traceback: bool = True) -> Callable:
    """Decorator to handle errors in an async function.
    
    Args:
        error_types: Optional list of error types to catch.
        default_message: Default error message.
        log_traceback: Whether to log the traceback.
        
    Returns:
        A decorator function.
    """
    if error_types is None:
        error_types = [Exception]
    
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[Union[T, DMacError]]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Union[T, DMacError]:
            try:
                return await func(*args, **kwargs)
            except tuple(error_types) as e:
                # Log the error
                if log_traceback:
                    logger.exception(f"Error in {func.__name__}: {e}")
                else:
                    logger.error(f"Error in {func.__name__}: {e}")
                
                # Convert the error to a DMacError if it's not already one
                if isinstance(e, DMacError):
                    return e
                else:
                    return DMacError(str(e) or default_message)
        
        return wrapper
    
    return decorator


def format_exception(exc: Exception) -> str:
    """Format an exception for display.
    
    Args:
        exc: The exception to format.
        
    Returns:
        A formatted string representation of the exception.
    """
    if isinstance(exc, DMacError):
        return str(exc)
    else:
        return f"{exc.__class__.__name__}: {str(exc)}"


def format_traceback(exc: Exception) -> str:
    """Format a traceback for display.
    
    Args:
        exc: The exception to format the traceback for.
        
    Returns:
        A formatted string representation of the traceback.
    """
    return ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))


def install_global_exception_handler() -> None:
    """Install a global exception handler for unhandled exceptions."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle an unhandled exception.
        
        Args:
            exc_type: The exception type.
            exc_value: The exception value.
            exc_traceback: The exception traceback.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            # Let KeyboardInterrupt pass through
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    # Install a handler for unhandled exceptions in asyncio
    loop = asyncio.get_event_loop()
    
    def handle_async_exception(loop, context):
        """Handle an unhandled exception in asyncio.
        
        Args:
            loop: The event loop.
            context: The error context.
        """
        exception = context.get('exception')
        if exception:
            logger.critical(f"Unhandled asyncio exception: {exception}", exc_info=exception)
        else:
            logger.critical(f"Unhandled asyncio exception: {context['message']}")
    
    loop.set_exception_handler(handle_async_exception)
    
    logger.info("Installed global exception handler")
