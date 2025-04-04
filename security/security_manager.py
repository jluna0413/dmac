"""
Security Manager for DMac.

This module provides security features for the DMac system.
"""

import asyncio
import base64
import hashlib
import json
import logging
import os
import re
import secrets
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

from config.config import config
from utils.secure_logging import get_logger

logger = get_logger('dmac.security.security_manager')


class SecurityManager:
    """Manager for security features."""
    
    def __init__(self):
        """Initialize the security manager."""
        # Load configuration
        self.enabled = config.get('security.enabled', True)
        self.data_dir = Path(config.get('security.data_dir', 'data/security'))
        self.key_dir = self.data_dir / 'keys'
        self.log_dir = self.data_dir / 'logs'
        self.token_expiration = config.get('security.token_expiration', 3600)  # 1 hour
        self.max_login_attempts = config.get('security.max_login_attempts', 5)
        self.lockout_duration = config.get('security.lockout_duration', 300)  # 5 minutes
        self.password_min_length = config.get('security.password_min_length', 12)
        self.password_require_uppercase = config.get('security.password_require_uppercase', True)
        self.password_require_lowercase = config.get('security.password_require_lowercase', True)
        self.password_require_digit = config.get('security.password_require_digit', True)
        self.password_require_special = config.get('security.password_require_special', True)
        
        # Create the data directories if they don't exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.key_dir, exist_ok=True)
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Initialize security data
        self.users = {}
        self.tokens = {}
        self.login_attempts = {}
        self.blocked_ips = {}
        self.api_keys = {}
        
        # Initialize security tasks
        self.security_tasks = []
        self.is_running = False
        
        logger.info("Security manager initialized")
    
    async def initialize(self) -> bool:
        """Initialize the security manager.
        
        Returns:
            True if initialization was successful, False otherwise.
        """
        if not self.enabled:
            logger.info("Security manager is disabled")
            return True
        
        try:
            # Load security data
            await self._load_users()
            await self._load_api_keys()
            
            # Start the security tasks
            self.is_running = True
            cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.security_tasks.append(cleanup_task)
            
            logger.info("Security manager initialized successfully")
            return True
        except Exception as e:
            logger.exception(f"Error initializing security manager: {e}")
            return False
    
    async def register_user(self, username: str, password: str, email: str, 
                          role: str = 'user') -> Tuple[bool, str]:
        """Register a new user.
        
        Args:
            username: The username of the new user.
            password: The password of the new user.
            email: The email of the new user.
            role: The role of the new user.
            
        Returns:
            A tuple of (success, message).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled"
        
        # Check if the username already exists
        if username in self.users:
            logger.warning(f"User {username} already exists")
            return False, "Username already exists"
        
        # Validate the password
        password_valid, password_message = self._validate_password(password)
        if not password_valid:
            logger.warning(f"Invalid password for user {username}: {password_message}")
            return False, password_message
        
        # Hash the password
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        # Create the user
        user = {
            'username': username,
            'password_hash': password_hash,
            'salt': salt,
            'email': email,
            'role': role,
            'created_at': time.time(),
            'last_login': None,
            'login_attempts': 0,
            'locked_until': None,
            'api_keys': [],
        }
        
        # Add the user to the dictionary
        self.users[username] = user
        
        # Save the user to disk
        await self._save_user(user)
        
        logger.info(f"Registered user {username} with role {role}")
        return True, "User registered successfully"
    
    async def login(self, username: str, password: str, ip_address: str) -> Tuple[bool, str, Optional[str]]:
        """Log in a user.
        
        Args:
            username: The username of the user.
            password: The password of the user.
            ip_address: The IP address of the user.
            
        Returns:
            A tuple of (success, message, token).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled", None
        
        # Check if the IP address is blocked
        if ip_address in self.blocked_ips:
            blocked_until = self.blocked_ips[ip_address]
            if blocked_until > time.time():
                logger.warning(f"Login attempt from blocked IP address {ip_address}")
                return False, "Too many login attempts, try again later", None
            else:
                # Remove the IP address from the blocked list
                del self.blocked_ips[ip_address]
        
        # Check if the username exists
        if username not in self.users:
            logger.warning(f"Login attempt for non-existent user {username} from {ip_address}")
            
            # Record the login attempt
            if ip_address not in self.login_attempts:
                self.login_attempts[ip_address] = []
            
            self.login_attempts[ip_address].append(time.time())
            
            # Check if the IP address should be blocked
            if len(self.login_attempts[ip_address]) >= self.max_login_attempts:
                # Block the IP address
                self.blocked_ips[ip_address] = time.time() + self.lockout_duration
                logger.warning(f"Blocked IP address {ip_address} for {self.lockout_duration} seconds")
            
            return False, "Invalid username or password", None
        
        # Get the user
        user = self.users[username]
        
        # Check if the user is locked
        if user['locked_until'] and user['locked_until'] > time.time():
            logger.warning(f"Login attempt for locked user {username} from {ip_address}")
            return False, "Account is locked, try again later", None
        
        # Check the password
        salt = user['salt']
        password_hash = self._hash_password(password, salt)
        
        if password_hash != user['password_hash']:
            logger.warning(f"Invalid password for user {username} from {ip_address}")
            
            # Increment the login attempts
            user['login_attempts'] += 1
            
            # Check if the user should be locked
            if user['login_attempts'] >= self.max_login_attempts:
                # Lock the user
                user['locked_until'] = time.time() + self.lockout_duration
                logger.warning(f"Locked user {username} for {self.lockout_duration} seconds")
            
            # Save the user to disk
            await self._save_user(user)
            
            return False, "Invalid username or password", None
        
        # Reset the login attempts
        user['login_attempts'] = 0
        user['locked_until'] = None
        user['last_login'] = time.time()
        
        # Save the user to disk
        await self._save_user(user)
        
        # Generate a token
        token = secrets.token_hex(32)
        expiration = time.time() + self.token_expiration
        
        # Store the token
        self.tokens[token] = {
            'username': username,
            'expiration': expiration,
            'ip_address': ip_address,
        }
        
        logger.info(f"User {username} logged in from {ip_address}")
        return True, "Login successful", token
    
    async def logout(self, token: str) -> Tuple[bool, str]:
        """Log out a user.
        
        Args:
            token: The token of the user.
            
        Returns:
            A tuple of (success, message).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled"
        
        # Check if the token exists
        if token not in self.tokens:
            logger.warning(f"Logout attempt with invalid token")
            return False, "Invalid token"
        
        # Get the token data
        token_data = self.tokens[token]
        username = token_data['username']
        
        # Remove the token
        del self.tokens[token]
        
        logger.info(f"User {username} logged out")
        return True, "Logout successful"
    
    async def validate_token(self, token: str, ip_address: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate a token.
        
        Args:
            token: The token to validate.
            ip_address: The IP address of the user.
            
        Returns:
            A tuple of (success, message, user_data).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled", None
        
        # Check if the token exists
        if token not in self.tokens:
            logger.warning(f"Token validation attempt with invalid token from {ip_address}")
            return False, "Invalid token", None
        
        # Get the token data
        token_data = self.tokens[token]
        username = token_data['username']
        expiration = token_data['expiration']
        token_ip = token_data['ip_address']
        
        # Check if the token has expired
        if expiration < time.time():
            logger.warning(f"Token validation attempt with expired token for user {username} from {ip_address}")
            
            # Remove the token
            del self.tokens[token]
            
            return False, "Token has expired", None
        
        # Check if the IP address matches
        if token_ip != ip_address:
            logger.warning(f"Token validation attempt with IP mismatch for user {username} from {ip_address} (expected {token_ip})")
            return False, "IP address mismatch", None
        
        # Get the user data
        user = self.users[username]
        
        # Create a copy of the user data without sensitive information
        user_data = user.copy()
        del user_data['password_hash']
        del user_data['salt']
        
        logger.debug(f"Token validated for user {username} from {ip_address}")
        return True, "Token is valid", user_data
    
    async def change_password(self, username: str, current_password: str, new_password: str) -> Tuple[bool, str]:
        """Change a user's password.
        
        Args:
            username: The username of the user.
            current_password: The current password of the user.
            new_password: The new password of the user.
            
        Returns:
            A tuple of (success, message).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled"
        
        # Check if the username exists
        if username not in self.users:
            logger.warning(f"Password change attempt for non-existent user {username}")
            return False, "Invalid username"
        
        # Get the user
        user = self.users[username]
        
        # Check the current password
        salt = user['salt']
        password_hash = self._hash_password(current_password, salt)
        
        if password_hash != user['password_hash']:
            logger.warning(f"Invalid current password for user {username}")
            return False, "Invalid current password"
        
        # Validate the new password
        password_valid, password_message = self._validate_password(new_password)
        if not password_valid:
            logger.warning(f"Invalid new password for user {username}: {password_message}")
            return False, password_message
        
        # Hash the new password
        new_salt = secrets.token_hex(16)
        new_password_hash = self._hash_password(new_password, new_salt)
        
        # Update the user
        user['password_hash'] = new_password_hash
        user['salt'] = new_salt
        
        # Save the user to disk
        await self._save_user(user)
        
        logger.info(f"Password changed for user {username}")
        return True, "Password changed successfully"
    
    async def create_api_key(self, username: str, description: str) -> Tuple[bool, str, Optional[str]]:
        """Create an API key for a user.
        
        Args:
            username: The username of the user.
            description: A description of the API key.
            
        Returns:
            A tuple of (success, message, api_key).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled", None
        
        # Check if the username exists
        if username not in self.users:
            logger.warning(f"API key creation attempt for non-existent user {username}")
            return False, "Invalid username", None
        
        # Get the user
        user = self.users[username]
        
        # Generate an API key
        api_key = f"dmac_{secrets.token_hex(32)}"
        
        # Create the API key data
        api_key_data = {
            'key': api_key,
            'username': username,
            'description': description,
            'created_at': time.time(),
            'last_used': None,
            'usage_count': 0,
        }
        
        # Add the API key to the dictionaries
        self.api_keys[api_key] = api_key_data
        user['api_keys'].append(api_key)
        
        # Save the API key and user to disk
        await self._save_api_key(api_key_data)
        await self._save_user(user)
        
        logger.info(f"Created API key for user {username}")
        return True, "API key created successfully", api_key
    
    async def validate_api_key(self, api_key: str, ip_address: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """Validate an API key.
        
        Args:
            api_key: The API key to validate.
            ip_address: The IP address of the user.
            
        Returns:
            A tuple of (success, message, user_data).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled", None
        
        # Check if the API key exists
        if api_key not in self.api_keys:
            logger.warning(f"API key validation attempt with invalid key from {ip_address}")
            return False, "Invalid API key", None
        
        # Get the API key data
        api_key_data = self.api_keys[api_key]
        username = api_key_data['username']
        
        # Update the API key usage
        api_key_data['last_used'] = time.time()
        api_key_data['usage_count'] += 1
        
        # Save the API key to disk
        await self._save_api_key(api_key_data)
        
        # Get the user data
        user = self.users[username]
        
        # Create a copy of the user data without sensitive information
        user_data = user.copy()
        del user_data['password_hash']
        del user_data['salt']
        
        logger.debug(f"API key validated for user {username} from {ip_address}")
        return True, "API key is valid", user_data
    
    async def revoke_api_key(self, username: str, api_key: str) -> Tuple[bool, str]:
        """Revoke an API key.
        
        Args:
            username: The username of the user.
            api_key: The API key to revoke.
            
        Returns:
            A tuple of (success, message).
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return False, "Security manager is disabled"
        
        # Check if the username exists
        if username not in self.users:
            logger.warning(f"API key revocation attempt for non-existent user {username}")
            return False, "Invalid username"
        
        # Check if the API key exists
        if api_key not in self.api_keys:
            logger.warning(f"API key revocation attempt with invalid key for user {username}")
            return False, "Invalid API key"
        
        # Get the API key data
        api_key_data = self.api_keys[api_key]
        key_username = api_key_data['username']
        
        # Check if the API key belongs to the user
        if key_username != username:
            logger.warning(f"API key revocation attempt for key belonging to user {key_username} by user {username}")
            return False, "API key does not belong to user"
        
        # Get the user
        user = self.users[username]
        
        # Remove the API key from the dictionaries
        del self.api_keys[api_key]
        if api_key in user['api_keys']:
            user['api_keys'].remove(api_key)
        
        # Delete the API key file
        api_key_path = self.key_dir / f"{api_key}.json"
        if api_key_path.exists():
            os.remove(api_key_path)
        
        # Save the user to disk
        await self._save_user(user)
        
        logger.info(f"Revoked API key for user {username}")
        return True, "API key revoked successfully"
    
    async def log_security_event(self, event_type: str, username: Optional[str], 
                               ip_address: str, details: Dict[str, Any]) -> None:
        """Log a security event.
        
        Args:
            event_type: The type of event.
            username: The username associated with the event, or None.
            ip_address: The IP address associated with the event.
            details: Additional details about the event.
        """
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return
        
        # Create the event
        event = {
            'event_type': event_type,
            'username': username,
            'ip_address': ip_address,
            'timestamp': time.time(),
            'details': details,
        }
        
        # Log the event
        logger.info(f"Security event: {event_type} from {ip_address}" + (f" for user {username}" if username else ""))
        
        # Save the event to disk
        event_path = self.log_dir / f"{int(time.time())}_{event_type}.json"
        try:
            with open(event_path, 'w') as f:
                json.dump(event, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving security event: {e}")
    
    async def cleanup(self) -> None:
        """Clean up resources used by the security manager."""
        if not self.enabled:
            logger.debug("Security manager is disabled")
            return
        
        logger.info("Cleaning up security manager")
        
        # Stop the security tasks
        self.is_running = False
        
        # Cancel all security tasks
        for task in self.security_tasks:
            task.cancel()
        
        # Wait for all security tasks to complete
        if self.security_tasks:
            await asyncio.gather(*self.security_tasks, return_exceptions=True)
        
        self.security_tasks = []
        
        logger.info("Security manager cleaned up")
    
    async def _load_users(self) -> None:
        """Load users from disk."""
        # Clear existing users
        self.users = {}
        
        # Load users from disk
        user_files = list(self.data_dir.glob("user_*.json"))
        
        for user_file in user_files:
            try:
                with open(user_file, 'r') as f:
                    user = json.load(f)
                
                username = user['username']
                
                # Add the user to the dictionary
                self.users[username] = user
            except Exception as e:
                logger.exception(f"Error loading user from {user_file}: {e}")
        
        logger.info(f"Loaded {len(self.users)} users")
    
    async def _save_user(self, user: Dict[str, Any]) -> None:
        """Save a user to disk.
        
        Args:
            user: The user to save.
        """
        username = user['username']
        user_path = self.data_dir / f"user_{username}.json"
        
        try:
            with open(user_path, 'w') as f:
                json.dump(user, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving user {username}: {e}")
    
    async def _load_api_keys(self) -> None:
        """Load API keys from disk."""
        # Clear existing API keys
        self.api_keys = {}
        
        # Load API keys from disk
        api_key_files = list(self.key_dir.glob("*.json"))
        
        for api_key_file in api_key_files:
            try:
                with open(api_key_file, 'r') as f:
                    api_key_data = json.load(f)
                
                api_key = api_key_data['key']
                
                # Add the API key to the dictionary
                self.api_keys[api_key] = api_key_data
            except Exception as e:
                logger.exception(f"Error loading API key from {api_key_file}: {e}")
        
        logger.info(f"Loaded {len(self.api_keys)} API keys")
    
    async def _save_api_key(self, api_key_data: Dict[str, Any]) -> None:
        """Save an API key to disk.
        
        Args:
            api_key_data: The API key data to save.
        """
        api_key = api_key_data['key']
        api_key_path = self.key_dir / f"{api_key}.json"
        
        try:
            with open(api_key_path, 'w') as f:
                json.dump(api_key_data, f, indent=2)
        except Exception as e:
            logger.exception(f"Error saving API key {api_key}: {e}")
    
    async def _cleanup_loop(self) -> None:
        """Cleanup loop for expired tokens and other temporary data."""
        while self.is_running:
            try:
                # Clean up expired tokens
                current_time = time.time()
                expired_tokens = [
                    token for token, token_data in self.tokens.items()
                    if token_data['expiration'] < current_time
                ]
                
                for token in expired_tokens:
                    del self.tokens[token]
                
                if expired_tokens:
                    logger.debug(f"Cleaned up {len(expired_tokens)} expired tokens")
                
                # Clean up login attempts
                for ip_address in list(self.login_attempts.keys()):
                    # Remove attempts older than the lockout duration
                    self.login_attempts[ip_address] = [
                        attempt for attempt in self.login_attempts[ip_address]
                        if attempt > current_time - self.lockout_duration
                    ]
                    
                    # Remove the IP address if there are no attempts
                    if not self.login_attempts[ip_address]:
                        del self.login_attempts[ip_address]
                
                # Clean up blocked IPs
                for ip_address in list(self.blocked_ips.keys()):
                    if self.blocked_ips[ip_address] < current_time:
                        del self.blocked_ips[ip_address]
                
                # Wait before the next cleanup
                await asyncio.sleep(60)  # Wait for 1 minute
            except asyncio.CancelledError:
                logger.info("Cleanup loop cancelled")
                break
            except Exception as e:
                logger.exception(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)  # Wait for 1 minute before trying again
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash a password with a salt.
        
        Args:
            password: The password to hash.
            salt: The salt to use.
            
        Returns:
            The hashed password.
        """
        # Combine the password and salt
        salted_password = password + salt
        
        # Hash the salted password
        hasher = hashlib.sha256()
        hasher.update(salted_password.encode())
        password_hash = hasher.hexdigest()
        
        return password_hash
    
    def _validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate a password.
        
        Args:
            password: The password to validate.
            
        Returns:
            A tuple of (valid, message).
        """
        # Check the password length
        if len(password) < self.password_min_length:
            return False, f"Password must be at least {self.password_min_length} characters long"
        
        # Check for uppercase letters
        if self.password_require_uppercase and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase letters
        if self.password_require_lowercase and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for digits
        if self.password_require_digit and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        # Check for special characters
        if self.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"


# Create a singleton instance
security_manager = SecurityManager()
