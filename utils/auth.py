"""
Authentication and authorization utilities for DMac.

This module provides utilities for user authentication and authorization.
"""

import hashlib
import os
import secrets
import time
from typing import Dict, List, Optional, Set, Union

from utils.encryption import encryptor
from utils.secure_file import secure_read_json, secure_write_json
from utils.secure_logging import get_logger

logger = get_logger('dmac.utils.auth')


class AuthManager:
    """Authentication and authorization manager."""
    
    def __init__(self, users_file: str = 'config/users.json'):
        """Initialize the authentication manager.
        
        Args:
            users_file: Path to the users file.
        """
        self.users_file = users_file
        self.users: Dict[str, Dict] = {}
        self.sessions: Dict[str, Dict] = {}
        self.session_expiry = 3600  # 1 hour
        
        # Load users from file
        self._load_users()
    
    def _load_users(self) -> None:
        """Load users from file."""
        users_data = secure_read_json('', self.users_file)
        if users_data:
            self.users = users_data
            logger.info(f"Loaded {len(self.users)} users from {self.users_file}")
        else:
            logger.warning(f"No users file found at {self.users_file}")
            # Create a default admin user if no users exist
            if not self.users:
                self._create_default_admin()
    
    def _save_users(self) -> None:
        """Save users to file."""
        if secure_write_json('', self.users_file, self.users):
            logger.info(f"Saved {len(self.users)} users to {self.users_file}")
        else:
            logger.error(f"Failed to save users to {self.users_file}")
    
    def _create_default_admin(self) -> None:
        """Create a default admin user."""
        # Generate a random password
        password = secrets.token_hex(8)
        
        # Create the admin user
        self.create_user(
            username='admin',
            password=password,
            roles=['admin'],
            email='admin@example.com',
            force=True
        )
        
        logger.info(f"Created default admin user with password: {password}")
        logger.info("Please change this password immediately!")
    
    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash a password.
        
        Args:
            password: The password to hash.
            salt: The salt to use for hashing. If None, a random salt will be generated.
            
        Returns:
            A tuple of (password_hash, salt).
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Hash the password with the salt
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        return password_hash, salt
    
    def create_user(self, username: str, password: str, roles: List[str], email: str, force: bool = False) -> bool:
        """Create a new user.
        
        Args:
            username: The username.
            password: The password.
            roles: The user roles.
            email: The user email.
            force: Whether to overwrite an existing user.
            
        Returns:
            True if the user was created successfully, False otherwise.
        """
        # Check if the user already exists
        if username in self.users and not force:
            logger.warning(f"User already exists: {username}")
            return False
        
        # Hash the password
        password_hash, salt = self._hash_password(password)
        
        # Create the user
        self.users[username] = {
            'password_hash': password_hash,
            'salt': salt,
            'roles': roles,
            'email': email,
            'created_at': time.time(),
            'last_login': None,
        }
        
        # Save the users
        self._save_users()
        
        logger.info(f"Created user: {username}")
        return True
    
    def update_user(self, username: str, password: Optional[str] = None, roles: Optional[List[str]] = None, email: Optional[str] = None) -> bool:
        """Update a user.
        
        Args:
            username: The username.
            password: The new password, or None to keep the current password.
            roles: The new user roles, or None to keep the current roles.
            email: The new user email, or None to keep the current email.
            
        Returns:
            True if the user was updated successfully, False otherwise.
        """
        # Check if the user exists
        if username not in self.users:
            logger.warning(f"User does not exist: {username}")
            return False
        
        # Update the password
        if password is not None:
            password_hash, salt = self._hash_password(password)
            self.users[username]['password_hash'] = password_hash
            self.users[username]['salt'] = salt
        
        # Update the roles
        if roles is not None:
            self.users[username]['roles'] = roles
        
        # Update the email
        if email is not None:
            self.users[username]['email'] = email
        
        # Save the users
        self._save_users()
        
        logger.info(f"Updated user: {username}")
        return True
    
    def delete_user(self, username: str) -> bool:
        """Delete a user.
        
        Args:
            username: The username.
            
        Returns:
            True if the user was deleted successfully, False otherwise.
        """
        # Check if the user exists
        if username not in self.users:
            logger.warning(f"User does not exist: {username}")
            return False
        
        # Delete the user
        del self.users[username]
        
        # Save the users
        self._save_users()
        
        logger.info(f"Deleted user: {username}")
        return True
    
    async def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate a user.
        
        Args:
            username: The username.
            password: The password.
            
        Returns:
            A session token if authentication is successful, None otherwise.
        """
        # Check if the user exists
        if username not in self.users:
            logger.warning(f"Authentication failed: User does not exist: {username}")
            return None
        
        # Get the user
        user = self.users[username]
        
        # Hash the password with the user's salt
        password_hash, _ = self._hash_password(password, user['salt'])
        
        # Check if the password is correct
        if password_hash != user['password_hash']:
            logger.warning(f"Authentication failed: Incorrect password for user: {username}")
            return None
        
        # Generate a session token
        session_token = secrets.token_hex(32)
        
        # Create the session
        self.sessions[session_token] = {
            'username': username,
            'expires': time.time() + self.session_expiry,
            'roles': user['roles'],
        }
        
        # Update the last login time
        self.users[username]['last_login'] = time.time()
        self._save_users()
        
        logger.info(f"Authentication successful for user: {username}")
        return session_token
    
    async def validate_session(self, session_token: str) -> Optional[Dict]:
        """Validate a session.
        
        Args:
            session_token: The session token.
            
        Returns:
            The session data if the session is valid, None otherwise.
        """
        # Check if the session exists
        if session_token not in self.sessions:
            logger.warning(f"Session validation failed: Session does not exist")
            return None
        
        # Get the session
        session = self.sessions[session_token]
        
        # Check if the session has expired
        if time.time() > session['expires']:
            logger.warning(f"Session validation failed: Session has expired for user: {session['username']}")
            del self.sessions[session_token]
            return None
        
        logger.info(f"Session validation successful for user: {session['username']}")
        return session
    
    async def authorize(self, session_token: str, required_roles: Union[str, List[str], Set[str]]) -> bool:
        """Check if a session has the required roles.
        
        Args:
            session_token: The session token.
            required_roles: The required roles. Can be a single role or a list/set of roles.
            
        Returns:
            True if the session has at least one of the required roles, False otherwise.
        """
        # Validate the session
        session = await self.validate_session(session_token)
        if not session:
            return False
        
        # Convert required_roles to a set
        if isinstance(required_roles, str):
            required_roles = {required_roles}
        elif isinstance(required_roles, list):
            required_roles = set(required_roles)
        
        # Check if the user has at least one of the required roles
        user_roles = set(session['roles'])
        if user_roles.intersection(required_roles):
            logger.info(f"Authorization successful for user: {session['username']}")
            return True
        
        logger.warning(f"Authorization failed for user: {session['username']}")
        return False
    
    async def logout(self, session_token: str) -> bool:
        """Log out a user.
        
        Args:
            session_token: The session token.
            
        Returns:
            True if the user was logged out successfully, False otherwise.
        """
        # Check if the session exists
        if session_token not in self.sessions:
            logger.warning(f"Logout failed: Session does not exist")
            return False
        
        # Get the username
        username = self.sessions[session_token]['username']
        
        # Delete the session
        del self.sessions[session_token]
        
        logger.info(f"Logout successful for user: {username}")
        return True
    
    def cleanup_sessions(self) -> int:
        """Clean up expired sessions.
        
        Returns:
            The number of sessions that were cleaned up.
        """
        # Get the current time
        current_time = time.time()
        
        # Find expired sessions
        expired_sessions = [
            token for token, session in self.sessions.items()
            if current_time > session['expires']
        ]
        
        # Delete expired sessions
        for token in expired_sessions:
            del self.sessions[token]
        
        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        return len(expired_sessions)


# Create a singleton instance
auth_manager = AuthManager()
