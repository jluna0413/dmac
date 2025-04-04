"""
Input validation and sanitization utilities for DMac.
"""

import re
from typing import Any, Dict, List, Optional, Pattern, Union


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
