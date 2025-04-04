"""
Unit tests for the error handling module.
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock

from utils.error_handling import (
    DMacError, ConfigError, SecurityError, ModelError, AgentError, TaskError,
    LearningError, APIError, FileError, ProcessError, NetworkError, DatabaseError,
    ValidationError, handle_errors, handle_async_errors, format_exception, format_traceback
)


class TestErrorHandling(unittest.TestCase):
    """Test case for the error handling module."""
    
    def test_dmac_error(self):
        """Test the DMacError class."""
        # Test with just a message
        error = DMacError("Test error")
        self.assertEqual(str(error), "DMacError: Test error")
        self.assertEqual(error.message, "Test error")
        self.assertIsNone(error.code)
        self.assertEqual(error.details, {})
        
        # Test with a message and code
        error = DMacError("Test error", "TEST_ERROR")
        self.assertEqual(str(error), "DMacError [TEST_ERROR]: Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.code, "TEST_ERROR")
        self.assertEqual(error.details, {})
        
        # Test with a message, code, and details
        error = DMacError("Test error", "TEST_ERROR", {"key": "value"})
        self.assertEqual(str(error), "DMacError [TEST_ERROR]: Test error")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.code, "TEST_ERROR")
        self.assertEqual(error.details, {"key": "value"})
        
        # Test to_dict method
        error_dict = error.to_dict()
        self.assertEqual(error_dict, {
            "error": "DMacError",
            "message": "Test error",
            "code": "TEST_ERROR",
            "details": {"key": "value"}
        })
    
    def test_error_subclasses(self):
        """Test the error subclasses."""
        # Test ConfigError
        error = ConfigError("Config error")
        self.assertEqual(str(error), "ConfigError: Config error")
        self.assertIsInstance(error, DMacError)
        
        # Test SecurityError
        error = SecurityError("Security error")
        self.assertEqual(str(error), "SecurityError: Security error")
        self.assertIsInstance(error, DMacError)
        
        # Test ModelError
        error = ModelError("Model error")
        self.assertEqual(str(error), "ModelError: Model error")
        self.assertIsInstance(error, DMacError)
        
        # Test AgentError
        error = AgentError("Agent error")
        self.assertEqual(str(error), "AgentError: Agent error")
        self.assertIsInstance(error, DMacError)
        
        # Test TaskError
        error = TaskError("Task error")
        self.assertEqual(str(error), "TaskError: Task error")
        self.assertIsInstance(error, DMacError)
        
        # Test LearningError
        error = LearningError("Learning error")
        self.assertEqual(str(error), "LearningError: Learning error")
        self.assertIsInstance(error, DMacError)
        
        # Test APIError
        error = APIError("API error")
        self.assertEqual(str(error), "APIError: API error")
        self.assertIsInstance(error, DMacError)
        
        # Test FileError
        error = FileError("File error")
        self.assertEqual(str(error), "FileError: File error")
        self.assertIsInstance(error, DMacError)
        
        # Test ProcessError
        error = ProcessError("Process error")
        self.assertEqual(str(error), "ProcessError: Process error")
        self.assertIsInstance(error, DMacError)
        
        # Test NetworkError
        error = NetworkError("Network error")
        self.assertEqual(str(error), "NetworkError: Network error")
        self.assertIsInstance(error, DMacError)
        
        # Test DatabaseError
        error = DatabaseError("Database error")
        self.assertEqual(str(error), "DatabaseError: Database error")
        self.assertIsInstance(error, DMacError)
        
        # Test ValidationError
        error = ValidationError("Validation error")
        self.assertEqual(str(error), "ValidationError: Validation error")
        self.assertIsInstance(error, DMacError)
    
    def test_handle_errors_decorator(self):
        """Test the handle_errors decorator."""
        # Test with a function that doesn't raise an error
        @handle_errors()
        def no_error_func():
            return "success"
        
        result = no_error_func()
        self.assertEqual(result, "success")
        
        # Test with a function that raises a DMacError
        @handle_errors()
        def dmac_error_func():
            raise ConfigError("Config error")
        
        result = dmac_error_func()
        self.assertIsInstance(result, ConfigError)
        self.assertEqual(result.message, "Config error")
        
        # Test with a function that raises a standard exception
        @handle_errors()
        def std_error_func():
            raise ValueError("Value error")
        
        result = std_error_func()
        self.assertIsInstance(result, DMacError)
        self.assertEqual(result.message, "Value error")
        
        # Test with specific error types
        @handle_errors(error_types=[ValueError])
        def specific_error_func():
            raise ValueError("Value error")
        
        result = specific_error_func()
        self.assertIsInstance(result, DMacError)
        self.assertEqual(result.message, "Value error")
        
        # Test with specific error types that don't match
        @handle_errors(error_types=[ValueError])
        def non_matching_error_func():
            raise TypeError("Type error")
        
        with self.assertRaises(TypeError):
            non_matching_error_func()
        
        # Test with a default message
        @handle_errors(default_message="Default error message")
        def empty_error_func():
            raise Exception()
        
        result = empty_error_func()
        self.assertIsInstance(result, DMacError)
        self.assertEqual(result.message, "Default error message")
    
    def test_handle_async_errors_decorator(self):
        """Test the handle_async_errors decorator."""
        # Test with a function that doesn't raise an error
        @handle_async_errors()
        async def no_error_func():
            return "success"
        
        result = asyncio.run(no_error_func())
        self.assertEqual(result, "success")
        
        # Test with a function that raises a DMacError
        @handle_async_errors()
        async def dmac_error_func():
            raise ConfigError("Config error")
        
        result = asyncio.run(dmac_error_func())
        self.assertIsInstance(result, ConfigError)
        self.assertEqual(result.message, "Config error")
        
        # Test with a function that raises a standard exception
        @handle_async_errors()
        async def std_error_func():
            raise ValueError("Value error")
        
        result = asyncio.run(std_error_func())
        self.assertIsInstance(result, DMacError)
        self.assertEqual(result.message, "Value error")
        
        # Test with specific error types
        @handle_async_errors(error_types=[ValueError])
        async def specific_error_func():
            raise ValueError("Value error")
        
        result = asyncio.run(specific_error_func())
        self.assertIsInstance(result, DMacError)
        self.assertEqual(result.message, "Value error")
        
        # Test with specific error types that don't match
        @handle_async_errors(error_types=[ValueError])
        async def non_matching_error_func():
            raise TypeError("Type error")
        
        with self.assertRaises(TypeError):
            asyncio.run(non_matching_error_func())
        
        # Test with a default message
        @handle_async_errors(default_message="Default error message")
        async def empty_error_func():
            raise Exception()
        
        result = asyncio.run(empty_error_func())
        self.assertIsInstance(result, DMacError)
        self.assertEqual(result.message, "Default error message")
    
    def test_format_exception(self):
        """Test the format_exception function."""
        # Test with a DMacError
        error = ConfigError("Config error")
        formatted = format_exception(error)
        self.assertEqual(formatted, "ConfigError: Config error")
        
        # Test with a standard exception
        error = ValueError("Value error")
        formatted = format_exception(error)
        self.assertEqual(formatted, "ValueError: Value error")
    
    def test_format_traceback(self):
        """Test the format_traceback function."""
        try:
            # Raise an exception to get a traceback
            raise ValueError("Value error")
        except ValueError as e:
            # Format the traceback
            formatted = format_traceback(e)
            
            # Check that the traceback contains the expected information
            self.assertIn("Traceback", formatted)
            self.assertIn("ValueError: Value error", formatted)


if __name__ == '__main__':
    unittest.main()
