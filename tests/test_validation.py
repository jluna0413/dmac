"""
Unit tests for the validation module.
"""

import unittest
from unittest.mock import patch, MagicMock

from utils.validation import (
    validator, validate_string, validate_integer, validate_float, validate_boolean,
    validate_list, validate_dict, validate_enum, validate_email, validate_url, validate_uuid
)
from utils.error_handling import ValidationError


class TestInputValidator(unittest.TestCase):
    """Test case for the InputValidator class."""
    
    def test_validate_prompt(self):
        """Test the validate_prompt method."""
        # Test with a valid prompt
        self.assertTrue(validator.validate_prompt("Hello, world!"))
        
        # Test with an empty prompt
        self.assertFalse(validator.validate_prompt(""))
        self.assertFalse(validator.validate_prompt("   "))
        
        # Test with a prompt that exceeds the maximum length
        long_prompt = "x" * 10001
        self.assertFalse(validator.validate_prompt(long_prompt))
        
        # Test with a prompt containing dangerous patterns
        self.assertFalse(validator.validate_prompt("exec('import os; os.system(\"rm -rf /\")'))"))
        self.assertFalse(validator.validate_prompt("eval('__import__(\"os\").system(\"rm -rf /\")'))"))
        self.assertFalse(validator.validate_prompt("os.system('rm -rf /')"))
        self.assertFalse(validator.validate_prompt("subprocess.run(['rm', '-rf', '/'])"))
        self.assertFalse(validator.validate_prompt("open('file.txt', 'w').write('hello')"))
        self.assertFalse(validator.validate_prompt("../../etc/passwd"))
    
    def test_sanitize_prompt(self):
        """Test the sanitize_prompt method."""
        # Test with a normal prompt
        self.assertEqual(validator.sanitize_prompt("Hello, world!"), "Hello, world!")
        
        # Test with control characters
        self.assertEqual(validator.sanitize_prompt("Hello\x00, world!"), "Hello, world!")
        
        # Test with dangerous patterns
        self.assertEqual(
            validator.sanitize_prompt("exec('import os; os.system(\"rm -rf /\")'))"),
            "[REMOVED]'import os; os.system(\"rm -rf /\")'))")
        
        self.assertEqual(
            validator.sanitize_prompt("eval('__import__(\"os\").system(\"rm -rf /\")'))"),
            "[REMOVED]'__import__(\"os\").system(\"rm -rf /\")'))")
        
        self.assertEqual(
            validator.sanitize_prompt("os.system('rm -rf /')"),
            "os.[REMOVED]'rm -rf /')")
    
    def test_validate_file_path(self):
        """Test the validate_file_path method."""
        # Test with a valid file path
        self.assertTrue(validator.validate_file_path("path/to/file.txt"))
        
        # Test with an empty path
        self.assertFalse(validator.validate_file_path(""))
        self.assertFalse(validator.validate_file_path("   "))
        
        # Test with path traversal attempts
        self.assertFalse(validator.validate_file_path("../path/to/file.txt"))
        self.assertFalse(validator.validate_file_path("~/path/to/file.txt"))
        
        # Test with absolute paths
        self.assertFalse(validator.validate_file_path("/path/to/file.txt"))
        self.assertFalse(validator.validate_file_path("C:/path/to/file.txt"))
        
        # Test with allowed extensions
        self.assertTrue(validator.validate_file_path("file.txt", allowed_extensions=["txt", "csv"]))
        self.assertFalse(validator.validate_file_path("file.exe", allowed_extensions=["txt", "csv"]))
    
    def test_sanitize_file_path(self):
        """Test the sanitize_file_path method."""
        # Test with a normal file path
        self.assertEqual(validator.sanitize_file_path("path/to/file.txt"), "path/to/file.txt")
        
        # Test with dangerous characters
        self.assertEqual(validator.sanitize_file_path("path/to/file!@#$%^&*.txt"), "path/to/file.txt")
        
        # Test with path traversal attempts
        self.assertEqual(validator.sanitize_file_path("../path/to/file.txt"), "path/to/file.txt")
        self.assertEqual(validator.sanitize_file_path("~/path/to/file.txt"), "path/to/file.txt")
        
        # Test with absolute paths
        self.assertEqual(validator.sanitize_file_path("/path/to/file.txt"), "path/to/file.txt")
        self.assertEqual(validator.sanitize_file_path("C:/path/to/file.txt"), "path/to/file.txt")
    
    def test_validate_json(self):
        """Test the validate_json method."""
        # Define a schema
        schema = {
            "name": {"type": "string", "required": True, "minLength": 3},
            "age": {"type": "integer", "required": True, "minimum": 0},
            "email": {"type": "string", "required": False, "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"},
            "tags": {"type": "array", "required": False, "minItems": 1},
            "address": {
                "type": "object",
                "required": False,
                "properties": {
                    "street": {"type": "string", "required": True},
                    "city": {"type": "string", "required": True},
                }
            }
        }
        
        # Test with valid data
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "john.doe@example.com",
            "tags": ["user", "admin"],
            "address": {
                "street": "123 Main St",
                "city": "Anytown"
            }
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(errors, [])
        
        # Test with missing required field
        data = {
            "age": 30
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("Missing required field: name", errors)
        
        # Test with invalid type
        data = {
            "name": "John Doe",
            "age": "thirty"
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("Field age must be an integer", errors)
        
        # Test with value below minimum
        data = {
            "name": "John Doe",
            "age": -1
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("Field age must be at least 0", errors)
        
        # Test with string below minimum length
        data = {
            "name": "Jo",
            "age": 30
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("Field name must be at least 3 characters long", errors)
        
        # Test with invalid pattern
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "invalid-email"
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("Field email must match pattern", errors)
        
        # Test with array below minimum items
        data = {
            "name": "John Doe",
            "age": 30,
            "tags": []
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("Field tags must have at least 1 items", errors)
        
        # Test with invalid nested object
        data = {
            "name": "John Doe",
            "age": 30,
            "address": {
                "street": "123 Main St"
            }
        }
        errors = validator.validate_json(data, schema)
        self.assertEqual(len(errors), 1)
        self.assertIn("In field address: Missing required field: city", errors)


class TestEnhancedValidation(unittest.TestCase):
    """Test case for the enhanced validation functions."""
    
    def test_validate_string(self):
        """Test the validate_string function."""
        # Test with a valid string
        self.assertEqual(validate_string("Hello", "name"), "Hello")
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_string(None, "name")
        self.assertEqual(str(cm.exception), "ValidationError: name is required")
        
        # Test with None when not required
        self.assertEqual(validate_string(None, "name", required=False), "")
        
        # Test with non-string
        with self.assertRaises(ValidationError) as cm:
            validate_string(123, "name")
        self.assertEqual(str(cm.exception), "ValidationError: name must be a string")
        
        # Test with string below minimum length
        with self.assertRaises(ValidationError) as cm:
            validate_string("Hi", "name", min_length=3)
        self.assertEqual(str(cm.exception), "ValidationError: name must be at least 3 characters long")
        
        # Test with string above maximum length
        with self.assertRaises(ValidationError) as cm:
            validate_string("Hello, world!", "name", max_length=5)
        self.assertEqual(str(cm.exception), "ValidationError: name must be at most 5 characters long")
        
        # Test with pattern that matches
        self.assertEqual(validate_string("abc123", "name", pattern=r"^[a-z0-9]+$"), "abc123")
        
        # Test with pattern that doesn't match
        with self.assertRaises(ValidationError) as cm:
            validate_string("ABC123", "name", pattern=r"^[a-z0-9]+$")
        self.assertEqual(str(cm.exception), "ValidationError: name must match the pattern: ^[a-z0-9]+$")
    
    def test_validate_integer(self):
        """Test the validate_integer function."""
        # Test with a valid integer
        self.assertEqual(validate_integer(123, "age"), 123)
        
        # Test with a valid integer as string
        self.assertEqual(validate_integer("123", "age"), 123)
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_integer(None, "age")
        self.assertEqual(str(cm.exception), "ValidationError: age is required")
        
        # Test with None when not required
        self.assertEqual(validate_integer(None, "age", required=False), 0)
        
        # Test with non-integer
        with self.assertRaises(ValidationError) as cm:
            validate_integer("abc", "age")
        self.assertEqual(str(cm.exception), "ValidationError: age must be an integer")
        
        # Test with integer below minimum
        with self.assertRaises(ValidationError) as cm:
            validate_integer(17, "age", min_value=18)
        self.assertEqual(str(cm.exception), "ValidationError: age must be at least 18")
        
        # Test with integer above maximum
        with self.assertRaises(ValidationError) as cm:
            validate_integer(65, "age", max_value=60)
        self.assertEqual(str(cm.exception), "ValidationError: age must be at most 60")
    
    def test_validate_float(self):
        """Test the validate_float function."""
        # Test with a valid float
        self.assertEqual(validate_float(3.14, "pi"), 3.14)
        
        # Test with a valid float as string
        self.assertEqual(validate_float("3.14", "pi"), 3.14)
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_float(None, "pi")
        self.assertEqual(str(cm.exception), "ValidationError: pi is required")
        
        # Test with None when not required
        self.assertEqual(validate_float(None, "pi", required=False), 0.0)
        
        # Test with non-float
        with self.assertRaises(ValidationError) as cm:
            validate_float("abc", "pi")
        self.assertEqual(str(cm.exception), "ValidationError: pi must be a number")
        
        # Test with float below minimum
        with self.assertRaises(ValidationError) as cm:
            validate_float(2.5, "pi", min_value=3.0)
        self.assertEqual(str(cm.exception), "ValidationError: pi must be at least 3.0")
        
        # Test with float above maximum
        with self.assertRaises(ValidationError) as cm:
            validate_float(4.0, "pi", max_value=3.5)
        self.assertEqual(str(cm.exception), "ValidationError: pi must be at most 3.5")
    
    def test_validate_boolean(self):
        """Test the validate_boolean function."""
        # Test with a valid boolean
        self.assertEqual(validate_boolean(True, "active"), True)
        self.assertEqual(validate_boolean(False, "active"), False)
        
        # Test with valid boolean-like values
        self.assertEqual(validate_boolean(1, "active"), True)
        self.assertEqual(validate_boolean(0, "active"), False)
        self.assertEqual(validate_boolean("true", "active"), True)
        self.assertEqual(validate_boolean("false", "active"), False)
        self.assertEqual(validate_boolean("yes", "active"), True)
        self.assertEqual(validate_boolean("no", "active"), False)
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_boolean(None, "active")
        self.assertEqual(str(cm.exception), "ValidationError: active is required")
        
        # Test with None when not required
        self.assertEqual(validate_boolean(None, "active", required=False), False)
        
        # Test with non-boolean
        with self.assertRaises(ValidationError) as cm:
            validate_boolean("maybe", "active")
        self.assertEqual(str(cm.exception), "ValidationError: active must be a boolean")
    
    def test_validate_list(self):
        """Test the validate_list function."""
        # Define a validator for list items
        def validate_item(item, name):
            if not isinstance(item, str):
                raise ValidationError(f"{name} must be a string")
            return item.upper()
        
        # Test with a valid list
        self.assertEqual(validate_list(["a", "b", "c"], "tags", validate_item), ["A", "B", "C"])
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_list(None, "tags", validate_item)
        self.assertEqual(str(cm.exception), "ValidationError: tags is required")
        
        # Test with None when not required
        self.assertEqual(validate_list(None, "tags", validate_item, required=False), [])
        
        # Test with non-list
        with self.assertRaises(ValidationError) as cm:
            validate_list("abc", "tags", validate_item)
        self.assertEqual(str(cm.exception), "ValidationError: tags must be a list")
        
        # Test with list below minimum length
        with self.assertRaises(ValidationError) as cm:
            validate_list(["a"], "tags", validate_item, min_length=2)
        self.assertEqual(str(cm.exception), "ValidationError: tags must have at least 2 items")
        
        # Test with list above maximum length
        with self.assertRaises(ValidationError) as cm:
            validate_list(["a", "b", "c"], "tags", validate_item, max_length=2)
        self.assertEqual(str(cm.exception), "ValidationError: tags must have at most 2 items")
        
        # Test with invalid item
        with self.assertRaises(ValidationError) as cm:
            validate_list(["a", 123, "c"], "tags", validate_item)
        self.assertEqual(str(cm.exception), "ValidationError: Invalid item in tags: ValidationError: tags[1] must be a string")
    
    def test_validate_dict(self):
        """Test the validate_dict function."""
        # Define a schema
        schema = {
            "name": lambda v, n: validate_string(v, n, min_length=3),
            "age": lambda v, n: validate_integer(v, n, min_value=0),
        }
        
        # Test with a valid dictionary
        self.assertEqual(
            validate_dict({"name": "John", "age": 30}, "user", schema),
            {"name": "John", "age": 30}
        )
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_dict(None, "user", schema)
        self.assertEqual(str(cm.exception), "ValidationError: user is required")
        
        # Test with None when not required
        self.assertEqual(validate_dict(None, "user", schema, required=False), {})
        
        # Test with non-dictionary
        with self.assertRaises(ValidationError) as cm:
            validate_dict("abc", "user", schema)
        self.assertEqual(str(cm.exception), "ValidationError: user must be a dictionary")
        
        # Test with missing field
        with self.assertRaises(ValidationError) as cm:
            validate_dict({"name": "John"}, "user", schema)
        self.assertEqual(str(cm.exception), "ValidationError: Invalid field in user: ValidationError: user.age is required")
        
        # Test with invalid field
        with self.assertRaises(ValidationError) as cm:
            validate_dict({"name": "Jo", "age": 30}, "user", schema)
        self.assertEqual(str(cm.exception), "ValidationError: Invalid field in user: ValidationError: user.name must be at least 3 characters long")
        
        # Test with extra fields not allowed
        with self.assertRaises(ValidationError) as cm:
            validate_dict({"name": "John", "age": 30, "email": "john@example.com"}, "user", schema)
        self.assertEqual(str(cm.exception), "ValidationError: user contains extra fields: email")
        
        # Test with extra fields allowed
        self.assertEqual(
            validate_dict({"name": "John", "age": 30, "email": "john@example.com"}, "user", schema, allow_extra=True),
            {"name": "John", "age": 30, "email": "john@example.com"}
        )
    
    def test_validate_enum(self):
        """Test the validate_enum function."""
        # Define allowed values
        allowed_values = ["red", "green", "blue"]
        
        # Test with a valid value
        self.assertEqual(validate_enum("red", "color", allowed_values), "red")
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_enum(None, "color", allowed_values)
        self.assertEqual(str(cm.exception), "ValidationError: color is required")
        
        # Test with None when not required
        self.assertIsNone(validate_enum(None, "color", allowed_values, required=False))
        
        # Test with invalid value
        with self.assertRaises(ValidationError) as cm:
            validate_enum("yellow", "color", allowed_values)
        self.assertEqual(str(cm.exception), "ValidationError: color must be one of: red, green, blue")
    
    def test_validate_email(self):
        """Test the validate_email function."""
        # Test with a valid email
        self.assertEqual(validate_email("user@example.com", "email"), "user@example.com")
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_email(None, "email")
        self.assertEqual(str(cm.exception), "ValidationError: email is required")
        
        # Test with None when not required
        self.assertEqual(validate_email(None, "email", required=False), "")
        
        # Test with invalid email
        with self.assertRaises(ValidationError) as cm:
            validate_email("invalid-email", "email")
        self.assertEqual(str(cm.exception), "ValidationError: email must be a valid email address")
    
    def test_validate_url(self):
        """Test the validate_url function."""
        # Test with a valid URL
        self.assertEqual(validate_url("https://example.com", "url"), "https://example.com")
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_url(None, "url")
        self.assertEqual(str(cm.exception), "ValidationError: url is required")
        
        # Test with None when not required
        self.assertEqual(validate_url(None, "url", required=False), "")
        
        # Test with invalid URL
        with self.assertRaises(ValidationError) as cm:
            validate_url("invalid-url", "url")
        self.assertEqual(str(cm.exception), "ValidationError: url must be a valid URL")
    
    def test_validate_uuid(self):
        """Test the validate_uuid function."""
        # Test with a valid UUID
        self.assertEqual(validate_uuid("123e4567-e89b-12d3-a456-426614174000", "id"), "123e4567-e89b-12d3-a456-426614174000")
        
        # Test with None when required
        with self.assertRaises(ValidationError) as cm:
            validate_uuid(None, "id")
        self.assertEqual(str(cm.exception), "ValidationError: id is required")
        
        # Test with None when not required
        self.assertEqual(validate_uuid(None, "id", required=False), "")
        
        # Test with invalid UUID
        with self.assertRaises(ValidationError) as cm:
            validate_uuid("invalid-uuid", "id")
        self.assertEqual(str(cm.exception), "ValidationError: id must be a valid UUID")


if __name__ == '__main__':
    unittest.main()
