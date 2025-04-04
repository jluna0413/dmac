"""
Data encryption utilities for DMac.

This module provides utilities for encrypting sensitive data.
"""

import base64
import os
from pathlib import Path
from typing import Optional, Union

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from utils.secure_file import set_secure_permissions
from utils.secure_logging import get_logger

logger = get_logger('dmac.utils.encryption')


class DataEncryptor:
    """Data encryptor for sensitive information."""
    
    def __init__(self, key_file: Union[str, Path] = 'config/encryption_key.key'):
        """Initialize the data encryptor.
        
        Args:
            key_file: Path to the encryption key file.
        """
        self.key_file = Path(key_file) if isinstance(key_file, str) else key_file
        self.key = self._load_or_generate_key()
        self.fernet = Fernet(self.key)
    
    def _load_or_generate_key(self) -> bytes:
        """Load or generate an encryption key.
        
        Returns:
            The encryption key.
        """
        if os.path.exists(self.key_file):
            try:
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                logger.info(f"Loaded encryption key from {self.key_file}")
                return key
            except Exception as e:
                logger.error(f"Error loading encryption key: {e}")
                logger.info("Generating a new encryption key")
        
        # Generate a new key
        key = Fernet.generate_key()
        
        try:
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            
            # Save the key to a file
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # Set secure permissions
            set_secure_permissions(self.key_file, owner_only=True)
            
            logger.info(f"Generated and saved new encryption key to {self.key_file}")
            return key
        except Exception as e:
            logger.error(f"Error saving encryption key: {e}")
            return key
    
    def encrypt(self, data: Union[str, bytes]) -> str:
        """Encrypt data.
        
        Args:
            data: The data to encrypt.
            
        Returns:
            The encrypted data as a base64-encoded string.
        """
        if isinstance(data, str):
            data = data.encode()
        
        encrypted = self.fernet.encrypt(data)
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data.
        
        Args:
            encrypted_data: The encrypted data as a base64-encoded string.
            
        Returns:
            The decrypted data.
        """
        encrypted = base64.urlsafe_b64decode(encrypted_data)
        decrypted = self.fernet.decrypt(encrypted)
        return decrypted.decode()
    
    def encrypt_file(self, file_path: Union[str, Path]) -> bool:
        """Encrypt a file.
        
        Args:
            file_path: The path to the file to encrypt.
            
        Returns:
            True if the file was encrypted successfully, False otherwise.
        """
        try:
            # Convert to Path if it's a string
            if isinstance(file_path, str):
                file_path = Path(file_path)
            
            # Check if the file exists
            if not file_path.exists():
                logger.warning(f"File does not exist: {file_path}")
                return False
            
            # Read the file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt the data
            encrypted = self.fernet.encrypt(data)
            
            # Write the encrypted data to a new file
            encrypted_file_path = file_path.with_suffix('.enc')
            with open(encrypted_file_path, 'wb') as f:
                f.write(encrypted)
            
            # Set secure permissions
            set_secure_permissions(encrypted_file_path, owner_only=True)
            
            logger.info(f"Encrypted file {file_path} to {encrypted_file_path}")
            return True
        except Exception as e:
            logger.error(f"Error encrypting file: {e}")
            return False
    
    def decrypt_file(self, encrypted_file_path: Union[str, Path], output_file_path: Optional[Union[str, Path]] = None) -> bool:
        """Decrypt a file.
        
        Args:
            encrypted_file_path: The path to the encrypted file.
            output_file_path: The path to write the decrypted file to. If None, the decrypted file will be written to the same location as the encrypted file, but with the .enc suffix removed.
            
        Returns:
            True if the file was decrypted successfully, False otherwise.
        """
        try:
            # Convert to Path if it's a string
            if isinstance(encrypted_file_path, str):
                encrypted_file_path = Path(encrypted_file_path)
            
            # Check if the file exists
            if not encrypted_file_path.exists():
                logger.warning(f"File does not exist: {encrypted_file_path}")
                return False
            
            # Determine the output file path
            if output_file_path is None:
                if encrypted_file_path.suffix == '.enc':
                    output_file_path = encrypted_file_path.with_suffix('')
                else:
                    output_file_path = encrypted_file_path.with_suffix('.dec')
            elif isinstance(output_file_path, str):
                output_file_path = Path(output_file_path)
            
            # Read the encrypted file
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt the data
            decrypted = self.fernet.decrypt(encrypted_data)
            
            # Write the decrypted data to the output file
            with open(output_file_path, 'wb') as f:
                f.write(decrypted)
            
            # Set secure permissions
            set_secure_permissions(output_file_path, owner_only=True)
            
            logger.info(f"Decrypted file {encrypted_file_path} to {output_file_path}")
            return True
        except Exception as e:
            logger.error(f"Error decrypting file: {e}")
            return False


def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
    """Derive an encryption key from a password.
    
    Args:
        password: The password to derive the key from.
        salt: The salt to use for key derivation. If None, a random salt will be generated.
        
    Returns:
        A tuple of (key, salt).
    """
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


# Create a singleton instance
encryptor = DataEncryptor()
