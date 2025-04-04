"""
Unit tests for the security manager.
"""

import unittest
import asyncio
import os
import shutil
import tempfile
from unittest.mock import patch, MagicMock

from security.security_manager import SecurityManager


class TestSecurityManager(unittest.TestCase):
    """Test case for the SecurityManager class."""
    
    def setUp(self):
        """Set up the test case."""
        # Create a temporary directory for the security manager data
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a security manager with the temporary directory
        self.security_manager = SecurityManager()
        self.security_manager.data_dir = os.path.join(self.temp_dir, 'security')
        self.security_manager.key_dir = os.path.join(self.security_manager.data_dir, 'keys')
        self.security_manager.log_dir = os.path.join(self.security_manager.data_dir, 'logs')
        
        # Create the directories
        os.makedirs(self.security_manager.data_dir, exist_ok=True)
        os.makedirs(self.security_manager.key_dir, exist_ok=True)
        os.makedirs(self.security_manager.log_dir, exist_ok=True)
    
    def tearDown(self):
        """Tear down the test case."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_hash_password(self):
        """Test the _hash_password method."""
        # Test with a password and salt
        password = "password123"
        salt = "abcdef1234567890"
        
        # Hash the password
        password_hash = self.security_manager._hash_password(password, salt)
        
        # Check that the hash is a string
        self.assertIsInstance(password_hash, str)
        
        # Check that the hash is not empty
        self.assertTrue(password_hash)
        
        # Check that the hash is consistent
        self.assertEqual(password_hash, self.security_manager._hash_password(password, salt))
        
        # Check that the hash is different with a different password
        self.assertNotEqual(password_hash, self.security_manager._hash_password("password456", salt))
        
        # Check that the hash is different with a different salt
        self.assertNotEqual(password_hash, self.security_manager._hash_password(password, "0987654321fedcba"))
    
    def test_validate_password(self):
        """Test the _validate_password method."""
        # Test with a valid password
        valid, message = self.security_manager._validate_password("Password123!")
        self.assertTrue(valid)
        self.assertEqual(message, "Password is valid")
        
        # Test with a password that's too short
        valid, message = self.security_manager._validate_password("Pass1!")
        self.assertFalse(valid)
        self.assertEqual(message, f"Password must be at least {self.security_manager.password_min_length} characters long")
        
        # Test with a password without uppercase letters
        self.security_manager.password_require_uppercase = True
        valid, message = self.security_manager._validate_password("password123!")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must contain at least one uppercase letter")
        
        # Test with a password without lowercase letters
        self.security_manager.password_require_lowercase = True
        valid, message = self.security_manager._validate_password("PASSWORD123!")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must contain at least one lowercase letter")
        
        # Test with a password without digits
        self.security_manager.password_require_digit = True
        valid, message = self.security_manager._validate_password("Password!")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must contain at least one digit")
        
        # Test with a password without special characters
        self.security_manager.password_require_special = True
        valid, message = self.security_manager._validate_password("Password123")
        self.assertFalse(valid)
        self.assertEqual(message, "Password must contain at least one special character")
    
    async def async_test_register_user(self):
        """Test the register_user method."""
        # Test with valid user data
        success, message = await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "User registered successfully")
        
        # Check that the user was added to the users dictionary
        self.assertIn("testuser", self.security_manager.users)
        
        # Check that the user data is correct
        user = self.security_manager.users["testuser"]
        self.assertEqual(user["username"], "testuser")
        self.assertEqual(user["email"], "testuser@example.com")
        self.assertEqual(user["role"], "user")
        self.assertIsNotNone(user["password_hash"])
        self.assertIsNotNone(user["salt"])
        
        # Test with an existing username
        success, message = await self.security_manager.register_user(
            username="testuser",
            password="Password456!",
            email="another@example.com"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Username already exists")
        
        # Test with an invalid password
        success, message = await self.security_manager.register_user(
            username="newuser",
            password="pass",
            email="newuser@example.com"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, f"Password must be at least {self.security_manager.password_min_length} characters long")
    
    async def async_test_login(self):
        """Test the login method."""
        # Register a user
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        # Test with valid credentials
        success, message, token = await self.security_manager.login(
            username="testuser",
            password="Password123!",
            ip_address="127.0.0.1"
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Login successful")
        self.assertIsNotNone(token)
        
        # Check that the token was added to the tokens dictionary
        self.assertIn(token, self.security_manager.tokens)
        
        # Check that the token data is correct
        token_data = self.security_manager.tokens[token]
        self.assertEqual(token_data["username"], "testuser")
        self.assertEqual(token_data["ip_address"], "127.0.0.1")
        self.assertGreater(token_data["expiration"], 0)
        
        # Test with invalid username
        success, message, token = await self.security_manager.login(
            username="nonexistent",
            password="Password123!",
            ip_address="127.0.0.1"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username or password")
        self.assertIsNone(token)
        
        # Test with invalid password
        success, message, token = await self.security_manager.login(
            username="testuser",
            password="WrongPassword!",
            ip_address="127.0.0.1"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username or password")
        self.assertIsNone(token)
        
        # Test with too many login attempts
        for _ in range(self.security_manager.max_login_attempts):
            await self.security_manager.login(
                username="testuser",
                password="WrongPassword!",
                ip_address="127.0.0.2"
            )
        
        success, message, token = await self.security_manager.login(
            username="testuser",
            password="Password123!",
            ip_address="127.0.0.2"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Account is locked, try again later")
        self.assertIsNone(token)
    
    async def async_test_logout(self):
        """Test the logout method."""
        # Register a user and log in
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        success, message, token = await self.security_manager.login(
            username="testuser",
            password="Password123!",
            ip_address="127.0.0.1"
        )
        
        # Test with a valid token
        success, message = await self.security_manager.logout(token)
        
        self.assertTrue(success)
        self.assertEqual(message, "Logout successful")
        
        # Check that the token was removed from the tokens dictionary
        self.assertNotIn(token, self.security_manager.tokens)
        
        # Test with an invalid token
        success, message = await self.security_manager.logout("invalid-token")
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid token")
    
    async def async_test_validate_token(self):
        """Test the validate_token method."""
        # Register a user and log in
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        success, message, token = await self.security_manager.login(
            username="testuser",
            password="Password123!",
            ip_address="127.0.0.1"
        )
        
        # Test with a valid token
        success, message, user_data = await self.security_manager.validate_token(token, "127.0.0.1")
        
        self.assertTrue(success)
        self.assertEqual(message, "Token is valid")
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data["username"], "testuser")
        
        # Test with an invalid token
        success, message, user_data = await self.security_manager.validate_token("invalid-token", "127.0.0.1")
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid token")
        self.assertIsNone(user_data)
        
        # Test with a different IP address
        success, message, user_data = await self.security_manager.validate_token(token, "127.0.0.2")
        
        self.assertFalse(success)
        self.assertEqual(message, "IP address mismatch")
        self.assertIsNone(user_data)
        
        # Test with an expired token
        # Modify the token expiration to be in the past
        self.security_manager.tokens[token]["expiration"] = 0
        
        success, message, user_data = await self.security_manager.validate_token(token, "127.0.0.1")
        
        self.assertFalse(success)
        self.assertEqual(message, "Token has expired")
        self.assertIsNone(user_data)
    
    async def async_test_change_password(self):
        """Test the change_password method."""
        # Register a user
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        # Test with valid data
        success, message = await self.security_manager.change_password(
            username="testuser",
            current_password="Password123!",
            new_password="NewPassword456!"
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "Password changed successfully")
        
        # Check that the password was changed
        # Try to log in with the new password
        success, message, token = await self.security_manager.login(
            username="testuser",
            password="NewPassword456!",
            ip_address="127.0.0.1"
        )
        
        self.assertTrue(success)
        
        # Test with invalid username
        success, message = await self.security_manager.change_password(
            username="nonexistent",
            current_password="Password123!",
            new_password="NewPassword456!"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username")
        
        # Test with invalid current password
        success, message = await self.security_manager.change_password(
            username="testuser",
            current_password="WrongPassword!",
            new_password="NewPassword456!"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid current password")
        
        # Test with invalid new password
        success, message = await self.security_manager.change_password(
            username="testuser",
            current_password="NewPassword456!",
            new_password="weak"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, f"Password must be at least {self.security_manager.password_min_length} characters long")
    
    async def async_test_create_api_key(self):
        """Test the create_api_key method."""
        # Register a user
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        # Test with valid data
        success, message, api_key = await self.security_manager.create_api_key(
            username="testuser",
            description="Test API Key"
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "API key created successfully")
        self.assertIsNotNone(api_key)
        self.assertTrue(api_key.startswith("dmac_"))
        
        # Check that the API key was added to the api_keys dictionary
        self.assertIn(api_key, self.security_manager.api_keys)
        
        # Check that the API key data is correct
        api_key_data = self.security_manager.api_keys[api_key]
        self.assertEqual(api_key_data["key"], api_key)
        self.assertEqual(api_key_data["username"], "testuser")
        self.assertEqual(api_key_data["description"], "Test API Key")
        
        # Check that the API key was added to the user's api_keys list
        self.assertIn(api_key, self.security_manager.users["testuser"]["api_keys"])
        
        # Test with invalid username
        success, message, api_key = await self.security_manager.create_api_key(
            username="nonexistent",
            description="Test API Key"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username")
        self.assertIsNone(api_key)
    
    async def async_test_validate_api_key(self):
        """Test the validate_api_key method."""
        # Register a user and create an API key
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        success, message, api_key = await self.security_manager.create_api_key(
            username="testuser",
            description="Test API Key"
        )
        
        # Test with a valid API key
        success, message, user_data = await self.security_manager.validate_api_key(api_key, "127.0.0.1")
        
        self.assertTrue(success)
        self.assertEqual(message, "API key is valid")
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data["username"], "testuser")
        
        # Check that the API key usage was updated
        api_key_data = self.security_manager.api_keys[api_key]
        self.assertEqual(api_key_data["usage_count"], 1)
        self.assertIsNotNone(api_key_data["last_used"])
        
        # Test with an invalid API key
        success, message, user_data = await self.security_manager.validate_api_key("invalid-key", "127.0.0.1")
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid API key")
        self.assertIsNone(user_data)
    
    async def async_test_revoke_api_key(self):
        """Test the revoke_api_key method."""
        # Register a user and create an API key
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        success, message, api_key = await self.security_manager.create_api_key(
            username="testuser",
            description="Test API Key"
        )
        
        # Test with valid data
        success, message = await self.security_manager.revoke_api_key(
            username="testuser",
            api_key=api_key
        )
        
        self.assertTrue(success)
        self.assertEqual(message, "API key revoked successfully")
        
        # Check that the API key was removed from the api_keys dictionary
        self.assertNotIn(api_key, self.security_manager.api_keys)
        
        # Check that the API key was removed from the user's api_keys list
        self.assertNotIn(api_key, self.security_manager.users["testuser"]["api_keys"])
        
        # Test with invalid username
        success, message = await self.security_manager.revoke_api_key(
            username="nonexistent",
            api_key=api_key
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid username")
        
        # Test with invalid API key
        success, message = await self.security_manager.revoke_api_key(
            username="testuser",
            api_key="invalid-key"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Invalid API key")
    
    async def async_test_log_security_event(self):
        """Test the log_security_event method."""
        # Test logging a security event
        await self.security_manager.log_security_event(
            event_type="login",
            username="testuser",
            ip_address="127.0.0.1",
            details={"success": True}
        )
        
        # Check that the event was logged
        # This is hard to test directly, so we'll just check that the method doesn't raise an exception
        
        # Test logging a security event without a username
        await self.security_manager.log_security_event(
            event_type="failed_login",
            username=None,
            ip_address="127.0.0.1",
            details={"success": False}
        )
    
    async def async_test_cleanup(self):
        """Test the cleanup method."""
        # Register a user and log in
        await self.security_manager.register_user(
            username="testuser",
            password="Password123!",
            email="testuser@example.com"
        )
        
        success, message, token = await self.security_manager.login(
            username="testuser",
            password="Password123!",
            ip_address="127.0.0.1"
        )
        
        # Start the security tasks
        self.security_manager.is_running = True
        cleanup_task = asyncio.create_task(self.security_manager._cleanup_loop())
        self.security_manager.security_tasks.append(cleanup_task)
        
        # Test the cleanup method
        await self.security_manager.cleanup()
        
        # Check that the security tasks were stopped
        self.assertFalse(self.security_manager.is_running)
        self.assertEqual(self.security_manager.security_tasks, [])
    
    def test_register_user(self):
        """Test the register_user method."""
        asyncio.run(self.async_test_register_user())
    
    def test_login(self):
        """Test the login method."""
        asyncio.run(self.async_test_login())
    
    def test_logout(self):
        """Test the logout method."""
        asyncio.run(self.async_test_logout())
    
    def test_validate_token(self):
        """Test the validate_token method."""
        asyncio.run(self.async_test_validate_token())
    
    def test_change_password(self):
        """Test the change_password method."""
        asyncio.run(self.async_test_change_password())
    
    def test_create_api_key(self):
        """Test the create_api_key method."""
        asyncio.run(self.async_test_create_api_key())
    
    def test_validate_api_key(self):
        """Test the validate_api_key method."""
        asyncio.run(self.async_test_validate_api_key())
    
    def test_revoke_api_key(self):
        """Test the revoke_api_key method."""
        asyncio.run(self.async_test_revoke_api_key())
    
    def test_log_security_event(self):
        """Test the log_security_event method."""
        asyncio.run(self.async_test_log_security_event())
    
    def test_cleanup(self):
        """Test the cleanup method."""
        asyncio.run(self.async_test_cleanup())


if __name__ == '__main__':
    unittest.main()
