"""
Secure File Operations for DMac.

This module provides secure file operations for the DMac system.
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple, BinaryIO

from config.config import config
from utils.secure_logging import get_logger

logger = get_logger('dmac.security.secure_file_ops')


class SecureFileOps:
    """Secure file operations for the DMac system."""
    
    def __init__(self):
        """Initialize the secure file operations."""
        # Load configuration
        self.enabled = config.get('security.file_ops.enabled', True)
        self.max_file_size = config.get('security.file_ops.max_file_size', 100 * 1024 * 1024)  # 100 MB
        self.allowed_extensions = set(config.get('security.file_ops.allowed_extensions', [
            '.txt', '.json', '.csv', '.md', '.py', '.js', '.html', '.css', '.jpg', '.jpeg', '.png', '.gif'
        ]))
        self.blocked_extensions = set(config.get('security.file_ops.blocked_extensions', [
            '.exe', '.dll', '.bat', '.cmd', '.sh', '.ps1', '.vbs', '.js', '.jar', '.msi'
        ]))
        self.scan_files = config.get('security.file_ops.scan_files', True)
        
        logger.info("Secure file operations initialized")
    
    async def validate_file_path(self, file_path: str, base_dir: Optional[str] = None) -> Tuple[bool, str]:
        """Validate a file path.
        
        Args:
            file_path: The file path to validate.
            base_dir: Optional base directory to restrict the file path to.
            
        Returns:
            A tuple of (valid, message).
        """
        if not self.enabled:
            logger.debug("Secure file operations are disabled")
            return True, "Secure file operations are disabled"
        
        # Check if the file path is empty
        if not file_path:
            logger.warning("Empty file path")
            return False, "Empty file path"
        
        # Convert the file path to a Path object
        path = Path(file_path)
        
        # Check if the file path is absolute
        if path.is_absolute():
            logger.warning(f"Absolute file path: {file_path}")
            return False, "Absolute file paths are not allowed"
        
        # Check if the file path contains parent directory references
        if '..' in path.parts:
            logger.warning(f"File path contains parent directory references: {file_path}")
            return False, "File paths with parent directory references are not allowed"
        
        # Check if the file path is within the base directory
        if base_dir:
            base_path = Path(base_dir)
            try:
                # Resolve the paths to their absolute paths
                abs_base_path = base_path.resolve()
                abs_file_path = (base_path / path).resolve()
                
                # Check if the file path is within the base directory
                if not str(abs_file_path).startswith(str(abs_base_path)):
                    logger.warning(f"File path is outside the base directory: {file_path}")
                    return False, "File path is outside the allowed directory"
            except Exception as e:
                logger.exception(f"Error resolving file path: {e}")
                return False, f"Error resolving file path: {e}"
        
        # Check the file extension
        if path.suffix:
            # Check if the extension is blocked
            if path.suffix.lower() in self.blocked_extensions:
                logger.warning(f"Blocked file extension: {path.suffix}")
                return False, f"File extension {path.suffix} is not allowed"
            
            # Check if the extension is allowed
            if self.allowed_extensions and path.suffix.lower() not in self.allowed_extensions:
                logger.warning(f"File extension not in allowed list: {path.suffix}")
                return False, f"File extension {path.suffix} is not allowed"
        
        return True, "File path is valid"
    
    async def validate_file_content(self, file_content: bytes) -> Tuple[bool, str]:
        """Validate file content.
        
        Args:
            file_content: The file content to validate.
            
        Returns:
            A tuple of (valid, message).
        """
        if not self.enabled:
            logger.debug("Secure file operations are disabled")
            return True, "Secure file operations are disabled"
        
        # Check the file size
        if len(file_content) > self.max_file_size:
            logger.warning(f"File size exceeds maximum: {len(file_content)} > {self.max_file_size}")
            return False, f"File size exceeds maximum of {self.max_file_size} bytes"
        
        # Scan the file content if enabled
        if self.scan_files:
            # This is a placeholder for a real file scanning implementation
            # In a real implementation, this would use a virus scanner or other security checks
            
            # For now, just check for some basic patterns
            try:
                # Check for executable content
                if file_content.startswith(b'MZ') or file_content.startswith(b'ZM'):
                    logger.warning("File content appears to be an executable")
                    return False, "File content appears to be an executable"
                
                # Check for shell script content
                if file_content.startswith(b'#!/'):
                    logger.warning("File content appears to be a shell script")
                    return False, "File content appears to be a shell script"
                
                # Check for PowerShell script content
                if b'powershell' in file_content.lower():
                    logger.warning("File content appears to contain PowerShell commands")
                    return False, "File content appears to contain PowerShell commands"
            except Exception as e:
                logger.exception(f"Error scanning file content: {e}")
                return False, f"Error scanning file content: {e}"
        
        return True, "File content is valid"
    
    async def read_file(self, file_path: str, base_dir: Optional[str] = None) -> Tuple[bool, str, Optional[bytes]]:
        """Read a file securely.
        
        Args:
            file_path: The path of the file to read.
            base_dir: Optional base directory to restrict the file path to.
            
        Returns:
            A tuple of (success, message, content).
        """
        if not self.enabled:
            logger.debug("Secure file operations are disabled")
            return True, "Secure file operations are disabled", None
        
        # Validate the file path
        valid, message = await self.validate_file_path(file_path, base_dir)
        if not valid:
            return False, message, None
        
        # Construct the full path
        full_path = Path(base_dir) / file_path if base_dir else Path(file_path)
        
        try:
            # Check if the file exists
            if not full_path.exists():
                logger.warning(f"File does not exist: {full_path}")
                return False, "File does not exist", None
            
            # Check if the path is a file
            if not full_path.is_file():
                logger.warning(f"Path is not a file: {full_path}")
                return False, "Path is not a file", None
            
            # Read the file
            with open(full_path, 'rb') as f:
                content = f.read()
            
            # Validate the file content
            valid, message = await self.validate_file_content(content)
            if not valid:
                return False, message, None
            
            logger.debug(f"Read file: {full_path}")
            return True, "File read successfully", content
        except Exception as e:
            logger.exception(f"Error reading file {full_path}: {e}")
            return False, f"Error reading file: {e}", None
    
    async def write_file(self, file_path: str, content: bytes, base_dir: Optional[str] = None) -> Tuple[bool, str]:
        """Write to a file securely.
        
        Args:
            file_path: The path of the file to write to.
            content: The content to write to the file.
            base_dir: Optional base directory to restrict the file path to.
            
        Returns:
            A tuple of (success, message).
        """
        if not self.enabled:
            logger.debug("Secure file operations are disabled")
            return True, "Secure file operations are disabled"
        
        # Validate the file path
        valid, message = await self.validate_file_path(file_path, base_dir)
        if not valid:
            return False, message
        
        # Validate the file content
        valid, message = await self.validate_file_content(content)
        if not valid:
            return False, message
        
        # Construct the full path
        full_path = Path(base_dir) / file_path if base_dir else Path(file_path)
        
        try:
            # Create the directory if it doesn't exist
            os.makedirs(full_path.parent, exist_ok=True)
            
            # Write the file
            with open(full_path, 'wb') as f:
                f.write(content)
            
            logger.debug(f"Wrote file: {full_path}")
            return True, "File written successfully"
        except Exception as e:
            logger.exception(f"Error writing file {full_path}: {e}")
            return False, f"Error writing file: {e}"
    
    async def delete_file(self, file_path: str, base_dir: Optional[str] = None) -> Tuple[bool, str]:
        """Delete a file securely.
        
        Args:
            file_path: The path of the file to delete.
            base_dir: Optional base directory to restrict the file path to.
            
        Returns:
            A tuple of (success, message).
        """
        if not self.enabled:
            logger.debug("Secure file operations are disabled")
            return True, "Secure file operations are disabled"
        
        # Validate the file path
        valid, message = await self.validate_file_path(file_path, base_dir)
        if not valid:
            return False, message
        
        # Construct the full path
        full_path = Path(base_dir) / file_path if base_dir else Path(file_path)
        
        try:
            # Check if the file exists
            if not full_path.exists():
                logger.warning(f"File does not exist: {full_path}")
                return False, "File does not exist"
            
            # Check if the path is a file
            if not full_path.is_file():
                logger.warning(f"Path is not a file: {full_path}")
                return False, "Path is not a file"
            
            # Delete the file
            os.remove(full_path)
            
            logger.debug(f"Deleted file: {full_path}")
            return True, "File deleted successfully"
        except Exception as e:
            logger.exception(f"Error deleting file {full_path}: {e}")
            return False, f"Error deleting file: {e}"
    
    async def list_files(self, directory: str, base_dir: Optional[str] = None) -> Tuple[bool, str, Optional[List[str]]]:
        """List files in a directory securely.
        
        Args:
            directory: The directory to list files in.
            base_dir: Optional base directory to restrict the directory to.
            
        Returns:
            A tuple of (success, message, files).
        """
        if not self.enabled:
            logger.debug("Secure file operations are disabled")
            return True, "Secure file operations are disabled", None
        
        # Validate the directory path
        valid, message = await self.validate_file_path(directory, base_dir)
        if not valid:
            return False, message, None
        
        # Construct the full path
        full_path = Path(base_dir) / directory if base_dir else Path(directory)
        
        try:
            # Check if the directory exists
            if not full_path.exists():
                logger.warning(f"Directory does not exist: {full_path}")
                return False, "Directory does not exist", None
            
            # Check if the path is a directory
            if not full_path.is_dir():
                logger.warning(f"Path is not a directory: {full_path}")
                return False, "Path is not a directory", None
            
            # List the files
            files = [str(f.relative_to(full_path)) for f in full_path.glob('*') if f.is_file()]
            
            logger.debug(f"Listed {len(files)} files in directory: {full_path}")
            return True, "Files listed successfully", files
        except Exception as e:
            logger.exception(f"Error listing files in directory {full_path}: {e}")
            return False, f"Error listing files: {e}", None
    
    async def compute_file_hash(self, file_path: str, base_dir: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Compute the hash of a file.
        
        Args:
            file_path: The path of the file to hash.
            base_dir: Optional base directory to restrict the file path to.
            
        Returns:
            A tuple of (success, message, hash).
        """
        if not self.enabled:
            logger.debug("Secure file operations are disabled")
            return True, "Secure file operations are disabled", None
        
        # Read the file
        success, message, content = await self.read_file(file_path, base_dir)
        if not success:
            return False, message, None
        
        try:
            # Compute the hash
            hasher = hashlib.sha256()
            hasher.update(content)
            file_hash = hasher.hexdigest()
            
            logger.debug(f"Computed hash for file: {file_path}")
            return True, "Hash computed successfully", file_hash
        except Exception as e:
            logger.exception(f"Error computing hash for file {file_path}: {e}")
            return False, f"Error computing hash: {e}", None


# Create a singleton instance
secure_file_ops = SecureFileOps()
