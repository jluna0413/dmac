"""
Secure file operations for DMac.

This module provides utilities for secure file operations.
"""

import json
import os
import shutil
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from utils.secure_logging import get_logger

logger = get_logger('dmac.utils.secure_file')


def secure_path(base_dir: Union[str, Path], user_path: str) -> Optional[Path]:
    """Create a secure file path that prevents path traversal.
    
    Args:
        base_dir: The base directory that files should be restricted to.
        user_path: The user-provided path.
        
    Returns:
        A secure Path object, or None if the path is invalid.
    """
    try:
        # Convert base_dir to Path if it's a string
        if isinstance(base_dir, str):
            base_dir = Path(base_dir)
        
        # Make sure base_dir is absolute
        base_dir = base_dir.absolute()
        
        # Normalize the path to resolve any '..' components
        normalized_path = os.path.normpath(user_path)
        
        # Check for path traversal attempts
        if normalized_path.startswith('..') or '/../' in normalized_path:
            logger.warning(f"Path traversal attempt detected: {user_path}")
            return None
        
        # Create the full path
        full_path = (base_dir / normalized_path).absolute()
        
        # Ensure the path is within the base directory
        if not str(full_path).startswith(str(base_dir)):
            logger.warning(f"Path escapes base directory: {full_path} not in {base_dir}")
            return None
        
        return full_path
    except Exception as e:
        logger.error(f"Error creating secure path: {e}")
        return None


def secure_read_file(base_dir: Union[str, Path], file_path: str, binary: bool = False) -> Optional[Union[str, bytes]]:
    """Read a file securely.
    
    Args:
        base_dir: The base directory that files should be restricted to.
        file_path: The file path relative to the base directory.
        binary: Whether to read the file in binary mode.
        
    Returns:
        The file contents, or None if the file could not be read.
    """
    try:
        # Get a secure path
        secure_file_path = secure_path(base_dir, file_path)
        if not secure_file_path:
            return None
        
        # Check if the file exists
        if not secure_file_path.exists():
            logger.warning(f"File does not exist: {secure_file_path}")
            return None
        
        # Check if the path is a file
        if not secure_file_path.is_file():
            logger.warning(f"Path is not a file: {secure_file_path}")
            return None
        
        # Read the file
        mode = 'rb' if binary else 'r'
        with open(secure_file_path, mode) as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return None


def secure_write_file(base_dir: Union[str, Path], file_path: str, content: Union[str, bytes], binary: bool = False) -> bool:
    """Write a file securely.
    
    Args:
        base_dir: The base directory that files should be restricted to.
        file_path: The file path relative to the base directory.
        content: The content to write to the file.
        binary: Whether to write the file in binary mode.
        
    Returns:
        True if the file was written successfully, False otherwise.
    """
    try:
        # Get a secure path
        secure_file_path = secure_path(base_dir, file_path)
        if not secure_file_path:
            return False
        
        # Create parent directories if they don't exist
        os.makedirs(secure_file_path.parent, exist_ok=True)
        
        # Write the file
        mode = 'wb' if binary else 'w'
        with open(secure_file_path, mode) as f:
            f.write(content)
        
        return True
    except Exception as e:
        logger.error(f"Error writing file: {e}")
        return False


def secure_delete_file(base_dir: Union[str, Path], file_path: str) -> bool:
    """Delete a file securely.
    
    Args:
        base_dir: The base directory that files should be restricted to.
        file_path: The file path relative to the base directory.
        
    Returns:
        True if the file was deleted successfully, False otherwise.
    """
    try:
        # Get a secure path
        secure_file_path = secure_path(base_dir, file_path)
        if not secure_file_path:
            return False
        
        # Check if the file exists
        if not secure_file_path.exists():
            logger.warning(f"File does not exist: {secure_file_path}")
            return False
        
        # Check if the path is a file
        if not secure_file_path.is_file():
            logger.warning(f"Path is not a file: {secure_file_path}")
            return False
        
        # Delete the file
        os.remove(secure_file_path)
        
        return True
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False


def secure_read_json(base_dir: Union[str, Path], file_path: str) -> Optional[Dict[str, Any]]:
    """Read a JSON file securely.
    
    Args:
        base_dir: The base directory that files should be restricted to.
        file_path: The file path relative to the base directory.
        
    Returns:
        The JSON data, or None if the file could not be read.
    """
    try:
        # Read the file
        content = secure_read_file(base_dir, file_path)
        if content is None:
            return None
        
        # Parse the JSON
        return json.loads(content)
    except json.JSONDecodeError:
        logger.error(f"Error parsing JSON file: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading JSON file: {e}")
        return None


def secure_write_json(base_dir: Union[str, Path], file_path: str, data: Dict[str, Any], indent: int = 2) -> bool:
    """Write a JSON file securely.
    
    Args:
        base_dir: The base directory that files should be restricted to.
        file_path: The file path relative to the base directory.
        data: The JSON data to write.
        indent: The indentation level for the JSON file.
        
    Returns:
        True if the file was written successfully, False otherwise.
    """
    try:
        # Convert the data to JSON
        content = json.dumps(data, indent=indent)
        
        # Write the file
        return secure_write_file(base_dir, file_path, content)
    except Exception as e:
        logger.error(f"Error writing JSON file: {e}")
        return False


def set_secure_permissions(file_path: Union[str, Path], owner_only: bool = True) -> bool:
    """Set secure permissions on a file.
    
    Args:
        file_path: The file path.
        owner_only: Whether to restrict permissions to the owner only.
        
    Returns:
        True if the permissions were set successfully, False otherwise.
    """
    try:
        # Convert to Path if it's a string
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Check if the file exists
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False
        
        # Set permissions
        if owner_only:
            # Owner read/write only (600)
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)
        else:
            # Owner read/write, group read, others none (640)
            os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP)
        
        return True
    except Exception as e:
        logger.error(f"Error setting file permissions: {e}")
        return False
