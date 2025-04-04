"""
Test script for security features.
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from config.config import config
from utils.auth import auth_manager
from utils.encryption import encryptor
from utils.rate_limiter import request_rate_limiter, model_token_bucket
from utils.secure_file import secure_path, secure_read_file, secure_write_file
from utils.secure_logging import get_logger
from utils.validation import validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)

logger = get_logger('test_security')


async def test_input_validation():
    """Test input validation."""
    logger.info("Testing input validation")
    
    # Test prompt validation
    valid_prompt = "Generate a function to calculate factorial"
    invalid_prompt = "os.system('rm -rf /')"
    
    assert validator.validate_prompt(valid_prompt), "Valid prompt should be accepted"
    assert not validator.validate_prompt(invalid_prompt), "Invalid prompt should be rejected"
    
    # Test file path validation
    valid_path = "data/test.txt"
    invalid_path = "../etc/passwd"
    
    assert validator.validate_file_path(valid_path), "Valid file path should be accepted"
    assert not validator.validate_file_path(invalid_path), "Invalid file path should be rejected"
    
    # Test JSON validation
    schema = {
        'name': {'type': 'string', 'required': True},
        'age': {'type': 'integer', 'min': 0, 'max': 120},
        'email': {'type': 'string', 'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
    }
    
    valid_json = {'name': 'John', 'age': 30, 'email': 'john@example.com'}
    invalid_json = {'name': 'John', 'age': -1, 'email': 'not-an-email'}
    
    assert not validator.validate_json(valid_json, schema), "Valid JSON should have no errors"
    assert validator.validate_json(invalid_json, schema), "Invalid JSON should have errors"
    
    logger.info("Input validation tests passed")
    return True


async def test_secure_file_operations():
    """Test secure file operations."""
    logger.info("Testing secure file operations")
    
    # Create a test directory
    test_dir = Path('test_data')
    os.makedirs(test_dir, exist_ok=True)
    
    # Test secure path
    valid_path = secure_path(test_dir, 'test.txt')
    invalid_path = secure_path(test_dir, '../etc/passwd')
    
    assert valid_path is not None, "Valid path should be accepted"
    assert invalid_path is None, "Invalid path should be rejected"
    
    # Test secure file write and read
    test_content = "This is a test file."
    assert secure_write_file(test_dir, 'test.txt', test_content), "File should be written successfully"
    
    read_content = secure_read_file(test_dir, 'test.txt')
    assert read_content == test_content, "File content should match"
    
    # Test secure file delete
    os.remove(test_dir / 'test.txt')
    
    # Clean up
    os.rmdir(test_dir)
    
    logger.info("Secure file operations tests passed")
    return True


async def test_rate_limiting():
    """Test rate limiting."""
    logger.info("Testing rate limiting")
    
    # Test request rate limiter
    client_id = "test_client"
    
    # Should allow requests up to the limit
    for i in range(10):
        assert await request_rate_limiter.check_rate_limit(client_id), f"Request {i+1} should be allowed"
    
    # Check remaining requests
    remaining = request_rate_limiter.get_remaining_requests(client_id)
    logger.info(f"Remaining requests: {remaining}")
    
    # Test token bucket
    # Should allow tokens up to the capacity
    for i in range(5):
        assert await model_token_bucket.consume(client_id, 10), f"Token consumption {i+1} should be allowed"
    
    # Check remaining tokens
    tokens = model_token_bucket.get_tokens(client_id)
    logger.info(f"Remaining tokens: {tokens}")
    
    logger.info("Rate limiting tests passed")
    return True


async def test_encryption():
    """Test encryption."""
    logger.info("Testing encryption")
    
    # Test string encryption and decryption
    test_string = "This is a secret message."
    encrypted = encryptor.encrypt(test_string)
    decrypted = encryptor.decrypt(encrypted)
    
    assert decrypted == test_string, "Decrypted string should match original"
    
    # Test file encryption and decryption
    test_dir = Path('test_data')
    os.makedirs(test_dir, exist_ok=True)
    
    test_file = test_dir / 'test.txt'
    with open(test_file, 'w') as f:
        f.write(test_string)
    
    # Encrypt the file
    assert encryptor.encrypt_file(test_file), "File should be encrypted successfully"
    
    # Decrypt the file
    encrypted_file = test_file.with_suffix('.enc')
    decrypted_file = test_dir / 'test_decrypted.txt'
    assert encryptor.decrypt_file(encrypted_file, decrypted_file), "File should be decrypted successfully"
    
    # Check the decrypted content
    with open(decrypted_file, 'r') as f:
        decrypted_content = f.read()
    
    assert decrypted_content == test_string, "Decrypted file content should match original"
    
    # Clean up
    os.remove(test_file)
    os.remove(encrypted_file)
    os.remove(decrypted_file)
    os.rmdir(test_dir)
    
    logger.info("Encryption tests passed")
    return True


async def test_authentication():
    """Test authentication and authorization."""
    logger.info("Testing authentication and authorization")
    
    # Create a test user
    username = "test_user"
    password = "test_password"
    roles = ["user"]
    email = "test@example.com"
    
    assert auth_manager.create_user(username, password, roles, email, force=True), "User should be created successfully"
    
    # Authenticate the user
    session_token = await auth_manager.authenticate(username, password)
    assert session_token is not None, "Authentication should succeed"
    
    # Validate the session
    session = await auth_manager.validate_session(session_token)
    assert session is not None, "Session should be valid"
    assert session['username'] == username, "Session username should match"
    
    # Authorize the user
    assert await auth_manager.authorize(session_token, "user"), "Authorization should succeed for correct role"
    assert not await auth_manager.authorize(session_token, "admin"), "Authorization should fail for incorrect role"
    
    # Log out the user
    assert await auth_manager.logout(session_token), "Logout should succeed"
    
    # Session should no longer be valid
    assert await auth_manager.validate_session(session_token) is None, "Session should be invalid after logout"
    
    # Clean up
    auth_manager.delete_user(username)
    
    logger.info("Authentication tests passed")
    return True


async def main():
    """Main entry point for the test script."""
    logger.info("Starting security tests")
    
    # Test input validation
    validation_success = await test_input_validation()
    logger.info(f"Input validation tests {'succeeded' if validation_success else 'failed'}")
    
    # Test secure file operations
    file_ops_success = await test_secure_file_operations()
    logger.info(f"Secure file operations tests {'succeeded' if file_ops_success else 'failed'}")
    
    # Test rate limiting
    rate_limiting_success = await test_rate_limiting()
    logger.info(f"Rate limiting tests {'succeeded' if rate_limiting_success else 'failed'}")
    
    # Test encryption
    encryption_success = await test_encryption()
    logger.info(f"Encryption tests {'succeeded' if encryption_success else 'failed'}")
    
    # Test authentication
    auth_success = await test_authentication()
    logger.info(f"Authentication tests {'succeeded' if auth_success else 'failed'}")
    
    # Overall result
    overall_success = (
        validation_success and
        file_ops_success and
        rate_limiting_success and
        encryption_success and
        auth_success
    )
    
    logger.info(f"Security tests {'succeeded' if overall_success else 'failed'}")


if __name__ == "__main__":
    asyncio.run(main())
