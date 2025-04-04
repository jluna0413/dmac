"""
Input validation and sanitization utilities for DMac.
"""

import re
import uuid
from typing import Any, Dict, List, Optional, Pattern, Union, Callable, Type, TypeVar, cast

from utils.secure_logging import get_logger
from utils.error_handling import ValidationError

logger = get_logger('dmac.utils.validation')


# Type variable for the value type
T = TypeVar('T')


class InputValidator:
    """Input validator for DMac."""

    # Common dangerous patterns to check for
    DANGEROUS_PATTERNS = [
        r"exec\s*\(",
        r"eval\s*\(",
        r"os\.system\s*\(",
        r"subprocess\.run\s*\(",
        r"subprocess\.call\s*\(",
        r"subprocess\.Popen\s*\(",
        r"__import__\s*\(",
        r"importlib\.",
        r"open\s*\(.+,\s*['\"]w['\"]",
        r"\.\.\/",  # Path traversal
        r"\/etc\/passwd",
        r"\/etc\/shadow",
    ]

    def __init__(self):
        """Initialize the input validator."""
        # Compile regex patterns for efficiency
        self.dangerous_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.DANGEROUS_PATTERNS]

    def validate_prompt(self, prompt: str, max_length: int = 10000) -> bool:
        """Validate a user prompt.

        Args:
            prompt: The prompt to validate.
            max_length: The maximum allowed length.

        Returns:
            True if the prompt is valid, False otherwise.
        """
        # Check for empty prompt
        if not prompt or not prompt.strip():
            return False

        # Check for maximum length
        if len(prompt) > max_length:
            return False

        # Check for potentially malicious patterns
        for pattern in self.dangerous_patterns:
            if pattern.search(prompt):
                return False

        return True

    def sanitize_prompt(self, prompt: str) -> str:
        """Sanitize a user prompt.

        Args:
            prompt: The prompt to sanitize.

        Returns:
            The sanitized prompt.
        """
        # Remove control characters
        sanitized = ''.join(char for char in prompt if ord(char) >= 32 or char in '\n\r\t')

        # Replace potentially dangerous sequences
        for pattern in self.dangerous_patterns:
            sanitized = pattern.sub("[REMOVED]", sanitized)

        return sanitized

    def validate_file_path(self, path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """Validate a file path.

        Args:
            path: The file path to validate.
            allowed_extensions: List of allowed file extensions.

        Returns:
            True if the file path is valid, False otherwise.
        """
        # Check for empty path
        if not path or not path.strip():
            return False

        # Check for path traversal attempts
        if '..' in path or '~' in path:
            return False

        # Check for absolute paths
        if path.startswith('/') or (len(path) > 1 and path[1] == ':'):
            return False

        # Check for allowed extensions
        if allowed_extensions:
            extension = path.split('.')[-1].lower() if '.' in path else ''
            if extension not in allowed_extensions:
                return False

        return True

    def sanitize_file_path(self, path: str) -> str:
        """Sanitize a file path.

        Args:
            path: The file path to sanitize.

        Returns:
            The sanitized file path.
        """
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[^a-zA-Z0-9_\-\./]', '', path)

        # Remove path traversal attempts
        sanitized = re.sub(r'\.\.|~', '', sanitized)

        # Remove leading slashes and drive letters
        sanitized = re.sub(r'^[/\\]|^[a-zA-Z]:', '', sanitized)

        return sanitized

    def validate_json(self, json_data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
        """Validate JSON data against a schema.

        Args:
            json_data: The JSON data to validate.
            schema: The schema to validate against.

        Returns:
            A list of validation errors, or an empty list if validation passed.
        """
        errors = []

        for key, rules in schema.items():
            # Check required fields
            if rules.get('required', False) and key not in json_data:
                errors.append(f"Missing required field: {key}")
                continue

            # Skip validation if field is not present and not required
            if key not in json_data:
                continue

            value = json_data[key]

            # Type validation
            if 'type' in rules:
                expected_type = rules['type']
                if expected_type == 'string' and not isinstance(value, str):
                    errors.append(f"Field {key} must be a string")
                elif expected_type == 'number' and not isinstance(value, (int, float)):
                    errors.append(f"Field {key} must be a number")
                elif expected_type == 'integer' and not isinstance(value, int):
                    errors.append(f"Field {key} must be an integer")
                elif expected_type == 'boolean' and not isinstance(value, bool):
                    errors.append(f"Field {key} must be a boolean")
                elif expected_type == 'array' and not isinstance(value, list):
                    errors.append(f"Field {key} must be an array")
                elif expected_type == 'object' and not isinstance(value, dict):
                    errors.append(f"Field {key} must be an object")

            # String validation
            if isinstance(value, str):
                if 'minLength' in rules and len(value) < rules['minLength']:
                    errors.append(f"Field {key} must be at least {rules['minLength']} characters long")
                if 'maxLength' in rules and len(value) > rules['maxLength']:
                    errors.append(f"Field {key} must be at most {rules['maxLength']} characters long")
                if 'pattern' in rules and not re.match(rules['pattern'], value):
                    errors.append(f"Field {key} must match pattern: {rules['pattern']}")

            # Number validation
            if isinstance(value, (int, float)):
                if 'minimum' in rules and value < rules['minimum']:
                    errors.append(f"Field {key} must be at least {rules['minimum']}")
                if 'maximum' in rules and value > rules['maximum']:
                    errors.append(f"Field {key} must be at most {rules['maximum']}")

            # Array validation
            if isinstance(value, list):
                if 'minItems' in rules and len(value) < rules['minItems']:
                    errors.append(f"Field {key} must have at least {rules['minItems']} items")
                if 'maxItems' in rules and len(value) > rules['maxItems']:
                    errors.append(f"Field {key} must have at most {rules['maxItems']} items")
                if 'items' in rules and isinstance(rules['items'], dict):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            item_errors = self.validate_json(item, rules['items'])
                            for error in item_errors:
                                errors.append(f"Item {i} in field {key}: {error}")

            # Object validation
            if isinstance(value, dict) and 'properties' in rules:
                nested_errors = self.validate_json(value, rules['properties'])
                for error in nested_errors:
                    errors.append(f"In field {key}: {error}")

        return errors


# Create a singleton instance
validator = InputValidator()


# Enhanced validation functions

def validate_string(value: Any, name: str, min_length: int = 0, max_length: Optional[int] = None,
                   pattern: Optional[str] = None, required: bool = True) -> str:
    """Validate a string value.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        min_length: The minimum length of the string.
        max_length: The maximum length of the string.
        pattern: Optional regex pattern the string must match.
        required: Whether the value is required.

    Returns:
        The validated string.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Check if the value is required
    if value is None or value == '':
        if required:
            raise ValidationError(f"{name} is required")
        else:
            return ''

    # Check if the value is a string
    if not isinstance(value, str):
        raise ValidationError(f"{name} must be a string")

    # Check the length
    if len(value) < min_length:
        raise ValidationError(f"{name} must be at least {min_length} characters long")

    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"{name} must be at most {max_length} characters long")

    # Check the pattern
    if pattern is not None and not re.match(pattern, value):
        raise ValidationError(f"{name} must match the pattern: {pattern}")

    return value


def validate_integer(value: Any, name: str, min_value: Optional[int] = None,
                    max_value: Optional[int] = None, required: bool = True) -> int:
    """Validate an integer value.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        min_value: The minimum value.
        max_value: The maximum value.
        required: Whether the value is required.

    Returns:
        The validated integer.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Check if the value is required
    if value is None:
        if required:
            raise ValidationError(f"{name} is required")
        else:
            return 0

    # Convert to integer
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be an integer")

    # Check the range
    if min_value is not None and int_value < min_value:
        raise ValidationError(f"{name} must be at least {min_value}")

    if max_value is not None and int_value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}")

    return int_value


def validate_float(value: Any, name: str, min_value: Optional[float] = None,
                  max_value: Optional[float] = None, required: bool = True) -> float:
    """Validate a float value.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        min_value: The minimum value.
        max_value: The maximum value.
        required: Whether the value is required.

    Returns:
        The validated float.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Check if the value is required
    if value is None:
        if required:
            raise ValidationError(f"{name} is required")
        else:
            return 0.0

    # Convert to float
    try:
        float_value = float(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be a number")

    # Check the range
    if min_value is not None and float_value < min_value:
        raise ValidationError(f"{name} must be at least {min_value}")

    if max_value is not None and float_value > max_value:
        raise ValidationError(f"{name} must be at most {max_value}")

    return float_value


def validate_boolean(value: Any, name: str, required: bool = True) -> bool:
    """Validate a boolean value.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        required: Whether the value is required.

    Returns:
        The validated boolean.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Check if the value is required
    if value is None:
        if required:
            raise ValidationError(f"{name} is required")
        else:
            return False

    # Convert to boolean
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)):
        return bool(value)

    if isinstance(value, str):
        value_lower = value.lower()
        if value_lower in ('true', 'yes', '1', 'y', 't'):
            return True
        elif value_lower in ('false', 'no', '0', 'n', 'f'):
            return False

    raise ValidationError(f"{name} must be a boolean")


def validate_list(value: Any, name: str, item_validator: Callable[[Any, str], T],
                 min_length: int = 0, max_length: Optional[int] = None,
                 required: bool = True) -> List[T]:
    """Validate a list value.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        item_validator: A function to validate each item in the list.
        min_length: The minimum length of the list.
        max_length: The maximum length of the list.
        required: Whether the value is required.

    Returns:
        The validated list.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Check if the value is required
    if value is None:
        if required:
            raise ValidationError(f"{name} is required")
        else:
            return []

    # Check if the value is a list
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"{name} must be a list")

    # Check the length
    if len(value) < min_length:
        raise ValidationError(f"{name} must have at least {min_length} items")

    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"{name} must have at most {max_length} items")

    # Validate each item
    validated_items = []
    for i, item in enumerate(value):
        try:
            validated_item = item_validator(item, f"{name}[{i}]")
            validated_items.append(validated_item)
        except ValidationError as e:
            raise ValidationError(f"Invalid item in {name}: {e}")

    return validated_items


def validate_dict(value: Any, name: str, schema: Dict[str, Callable[[Any, str], Any]],
                 required: bool = True, allow_extra: bool = False) -> Dict[str, Any]:
    """Validate a dictionary value.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        schema: A dictionary mapping field names to validator functions.
        required: Whether the value is required.
        allow_extra: Whether to allow extra fields not in the schema.

    Returns:
        The validated dictionary.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Check if the value is required
    if value is None:
        if required:
            raise ValidationError(f"{name} is required")
        else:
            return {}

    # Check if the value is a dictionary
    if not isinstance(value, dict):
        raise ValidationError(f"{name} must be a dictionary")

    # Validate each field
    validated_dict = {}
    for field_name, validator in schema.items():
        field_value = value.get(field_name)
        try:
            validated_value = validator(field_value, f"{name}.{field_name}")
            validated_dict[field_name] = validated_value
        except ValidationError as e:
            raise ValidationError(f"Invalid field in {name}: {e}")

    # Check for extra fields
    if not allow_extra:
        extra_fields = set(value.keys()) - set(schema.keys())
        if extra_fields:
            raise ValidationError(f"{name} contains extra fields: {', '.join(extra_fields)}")
    else:
        # Copy extra fields
        for field_name, field_value in value.items():
            if field_name not in schema:
                validated_dict[field_name] = field_value

    return validated_dict


def validate_enum(value: Any, name: str, allowed_values: List[T], required: bool = True) -> T:
    """Validate an enum value.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        allowed_values: The allowed values.
        required: Whether the value is required.

    Returns:
        The validated enum value.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Check if the value is required
    if value is None:
        if required:
            raise ValidationError(f"{name} is required")
        else:
            return cast(T, None)

    # Check if the value is in the allowed values
    if value not in allowed_values:
        raise ValidationError(f"{name} must be one of: {', '.join(str(v) for v in allowed_values)}")

    return value


def validate_email(value: Any, name: str, required: bool = True) -> str:
    """Validate an email address.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        required: Whether the value is required.

    Returns:
        The validated email address.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Validate as a string first
    email = validate_string(value, name, required=required)

    if email:
        # Check if the email is valid
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(f"{name} must be a valid email address")

    return email


def validate_url(value: Any, name: str, required: bool = True) -> str:
    """Validate a URL.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        required: Whether the value is required.

    Returns:
        The validated URL.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Validate as a string first
    url = validate_string(value, name, required=required)

    if url:
        # Check if the URL is valid
        url_pattern = r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(/[-\w%!$&\'()*+,;=:@/~]+)*(?:\?[-\w%!$&\'()*+,;=:@/~]*)?(?:#[-\w%!$&\'()*+,;=:@/~]*)?$'
        if not re.match(url_pattern, url):
            raise ValidationError(f"{name} must be a valid URL")

    return url


def validate_uuid(value: Any, name: str, required: bool = True) -> str:
    """Validate a UUID.

    Args:
        value: The value to validate.
        name: The name of the value for error messages.
        required: Whether the value is required.

    Returns:
        The validated UUID.

    Raises:
        ValidationError: If the value is invalid.
    """
    # Validate as a string first
    uuid_str = validate_string(value, name, required=required)

    if uuid_str:
        # Check if the UUID is valid
        try:
            uuid.UUID(uuid_str)
        except ValueError:
            raise ValidationError(f"{name} must be a valid UUID")

    return uuid_str
