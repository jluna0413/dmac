"""
Secure API for DMac.

This module provides secure API functionality for the DMac system.
"""

import asyncio
import functools
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Awaitable

from aiohttp import web
from aiohttp.web import Request, Response, middleware

from config.config import config
from utils.secure_logging import get_logger
from security.security_manager import security_manager

logger = get_logger('dmac.security.secure_api')


@middleware
async def auth_middleware(request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
    """Authentication middleware for API requests.
    
    Args:
        request: The request to authenticate.
        handler: The handler to call if authentication is successful.
        
    Returns:
        The response from the handler, or an error response if authentication fails.
    """
    # Check if the path is exempt from authentication
    exempt_paths = [
        '/api/auth/login',
        '/api/auth/register',
        '/api/health',
        '/api/version',
    ]
    
    if request.path in exempt_paths:
        return await handler(request)
    
    # Get the authentication header
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        logger.warning(f"Missing Authorization header for request to {request.path} from {request.remote}")
        return web.json_response({'error': 'Missing Authorization header'}, status=401)
    
    # Check the authentication type
    auth_parts = auth_header.split()
    
    if len(auth_parts) != 2:
        logger.warning(f"Invalid Authorization header format for request to {request.path} from {request.remote}")
        return web.json_response({'error': 'Invalid Authorization header format'}, status=401)
    
    auth_type, auth_value = auth_parts
    
    # Authenticate based on the type
    if auth_type.lower() == 'bearer':
        # Token authentication
        token = auth_value
        success, message, user_data = await security_manager.validate_token(token, request.remote)
        
        if not success:
            logger.warning(f"Invalid token for request to {request.path} from {request.remote}: {message}")
            return web.json_response({'error': message}, status=401)
        
        # Add the user data to the request
        request['user'] = user_data
    elif auth_type.lower() == 'apikey':
        # API key authentication
        api_key = auth_value
        success, message, user_data = await security_manager.validate_api_key(api_key, request.remote)
        
        if not success:
            logger.warning(f"Invalid API key for request to {request.path} from {request.remote}: {message}")
            return web.json_response({'error': message}, status=401)
        
        # Add the user data to the request
        request['user'] = user_data
    else:
        logger.warning(f"Unsupported authentication type {auth_type} for request to {request.path} from {request.remote}")
        return web.json_response({'error': 'Unsupported authentication type'}, status=401)
    
    # Log the authenticated request
    username = user_data['username']
    logger.debug(f"Authenticated request to {request.path} from {request.remote} for user {username}")
    
    # Call the handler
    return await handler(request)


@middleware
async def rate_limit_middleware(request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
    """Rate limiting middleware for API requests.
    
    Args:
        request: The request to rate limit.
        handler: The handler to call if rate limiting allows.
        
    Returns:
        The response from the handler, or an error response if rate limiting blocks the request.
    """
    # Get the rate limiting configuration
    rate_limit_enabled = config.get('security.rate_limit.enabled', True)
    rate_limit_requests = config.get('security.rate_limit.requests', 100)
    rate_limit_window = config.get('security.rate_limit.window', 60)  # 1 minute
    
    if not rate_limit_enabled:
        return await handler(request)
    
    # Get the client IP address
    ip_address = request.remote
    
    # Get the current time
    current_time = time.time()
    
    # Get the rate limiting data for this IP address
    if not hasattr(request.app, 'rate_limit_data'):
        request.app.rate_limit_data = {}
    
    if ip_address not in request.app.rate_limit_data:
        request.app.rate_limit_data[ip_address] = []
    
    # Remove requests outside the window
    request.app.rate_limit_data[ip_address] = [
        timestamp for timestamp in request.app.rate_limit_data[ip_address]
        if timestamp > current_time - rate_limit_window
    ]
    
    # Check if the rate limit has been exceeded
    if len(request.app.rate_limit_data[ip_address]) >= rate_limit_requests:
        logger.warning(f"Rate limit exceeded for request to {request.path} from {ip_address}")
        
        # Log the rate limit event
        await security_manager.log_security_event(
            event_type='rate_limit_exceeded',
            username=request.get('user', {}).get('username'),
            ip_address=ip_address,
            details={
                'path': request.path,
                'method': request.method,
                'requests': len(request.app.rate_limit_data[ip_address]),
                'window': rate_limit_window,
                'limit': rate_limit_requests,
            }
        )
        
        return web.json_response(
            {
                'error': 'Rate limit exceeded',
                'retry_after': rate_limit_window,
            },
            status=429,
            headers={'Retry-After': str(rate_limit_window)}
        )
    
    # Add the current request to the rate limiting data
    request.app.rate_limit_data[ip_address].append(current_time)
    
    # Call the handler
    return await handler(request)


@middleware
async def security_headers_middleware(request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
    """Security headers middleware for API responses.
    
    Args:
        request: The request.
        handler: The handler to call.
        
    Returns:
        The response from the handler, with security headers added.
    """
    # Call the handler
    response = await handler(request)
    
    # Add security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Referrer-Policy'] = 'no-referrer'
    
    return response


@middleware
async def logging_middleware(request: Request, handler: Callable[[Request], Awaitable[Response]]) -> Response:
    """Logging middleware for API requests.
    
    Args:
        request: The request to log.
        handler: The handler to call.
        
    Returns:
        The response from the handler.
    """
    # Get the start time
    start_time = time.time()
    
    # Log the request
    logger.info(f"{request.method} {request.path} from {request.remote}")
    
    try:
        # Call the handler
        response = await handler(request)
        
        # Calculate the response time
        response_time = time.time() - start_time
        
        # Log the response
        logger.info(f"{request.method} {request.path} from {request.remote} - {response.status} in {response_time:.3f}s")
        
        return response
    except Exception as e:
        # Calculate the response time
        response_time = time.time() - start_time
        
        # Log the error
        logger.exception(f"{request.method} {request.path} from {request.remote} - Error in {response_time:.3f}s: {e}")
        
        # Return an error response
        return web.json_response({'error': str(e)}, status=500)


def setup_secure_api(app: web.Application) -> None:
    """Set up secure API middleware for an application.
    
    Args:
        app: The application to set up.
    """
    # Add the middleware
    app.middlewares.append(logging_middleware)
    app.middlewares.append(security_headers_middleware)
    app.middlewares.append(rate_limit_middleware)
    app.middlewares.append(auth_middleware)
    
    logger.info("Secure API middleware set up")


def require_role(role: str) -> Callable:
    """Decorator to require a specific role for a handler.
    
    Args:
        role: The role to require.
        
    Returns:
        A decorator that checks if the user has the required role.
    """
    def decorator(handler: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]:
        @functools.wraps(handler)
        async def wrapper(request: Request) -> Response:
            # Check if the user is authenticated
            user = request.get('user')
            
            if not user:
                logger.warning(f"Unauthenticated request to {request.path} from {request.remote}")
                return web.json_response({'error': 'Authentication required'}, status=401)
            
            # Check if the user has the required role
            user_role = user.get('role')
            
            if user_role != role and user_role != 'admin':
                logger.warning(f"Unauthorized request to {request.path} from {request.remote} for user {user['username']} (role: {user_role}, required: {role})")
                return web.json_response({'error': 'Insufficient permissions'}, status=403)
            
            # Call the handler
            return await handler(request)
        
        return wrapper
    
    return decorator


def require_admin(handler: Callable[[Request], Awaitable[Response]]) -> Callable[[Request], Awaitable[Response]]:
    """Decorator to require admin role for a handler.
    
    Args:
        handler: The handler to decorate.
        
    Returns:
        A decorated handler that checks if the user is an admin.
    """
    return require_role('admin')(handler)


async def handle_login(request: Request) -> Response:
    """Handle a login request.
    
    Args:
        request: The login request.
        
    Returns:
        A response with the login result.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the login credentials
        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            logger.warning(f"Missing username or password for login request from {request.remote}")
            return web.json_response({'error': 'Missing username or password'}, status=400)
        
        # Attempt to log in
        success, message, token = await security_manager.login(username, password, request.remote)
        
        if not success:
            logger.warning(f"Login failed for user {username} from {request.remote}: {message}")
            return web.json_response({'error': message}, status=401)
        
        # Log the login event
        await security_manager.log_security_event(
            event_type='login',
            username=username,
            ip_address=request.remote,
            details={
                'success': success,
                'message': message,
            }
        )
        
        # Return the token
        return web.json_response({'token': token})
    except Exception as e:
        logger.exception(f"Error handling login request from {request.remote}: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def handle_logout(request: Request) -> Response:
    """Handle a logout request.
    
    Args:
        request: The logout request.
        
    Returns:
        A response with the logout result.
    """
    try:
        # Get the authentication header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning(f"Missing Authorization header for logout request from {request.remote}")
            return web.json_response({'error': 'Missing Authorization header'}, status=401)
        
        # Check the authentication type
        auth_parts = auth_header.split()
        
        if len(auth_parts) != 2 or auth_parts[0].lower() != 'bearer':
            logger.warning(f"Invalid Authorization header format for logout request from {request.remote}")
            return web.json_response({'error': 'Invalid Authorization header format'}, status=401)
        
        # Get the token
        token = auth_parts[1]
        
        # Attempt to log out
        success, message = await security_manager.logout(token)
        
        if not success:
            logger.warning(f"Logout failed from {request.remote}: {message}")
            return web.json_response({'error': message}, status=401)
        
        # Log the logout event
        await security_manager.log_security_event(
            event_type='logout',
            username=request.get('user', {}).get('username'),
            ip_address=request.remote,
            details={
                'success': success,
                'message': message,
            }
        )
        
        # Return success
        return web.json_response({'message': message})
    except Exception as e:
        logger.exception(f"Error handling logout request from {request.remote}: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def handle_register(request: Request) -> Response:
    """Handle a registration request.
    
    Args:
        request: The registration request.
        
    Returns:
        A response with the registration result.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the registration data
        username = body.get('username')
        password = body.get('password')
        email = body.get('email')
        
        if not username or not password or not email:
            logger.warning(f"Missing username, password, or email for registration request from {request.remote}")
            return web.json_response({'error': 'Missing username, password, or email'}, status=400)
        
        # Attempt to register
        success, message = await security_manager.register_user(username, password, email)
        
        if not success:
            logger.warning(f"Registration failed for user {username} from {request.remote}: {message}")
            return web.json_response({'error': message}, status=400)
        
        # Log the registration event
        await security_manager.log_security_event(
            event_type='registration',
            username=username,
            ip_address=request.remote,
            details={
                'success': success,
                'message': message,
                'email': email,
            }
        )
        
        # Return success
        return web.json_response({'message': message})
    except Exception as e:
        logger.exception(f"Error handling registration request from {request.remote}: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def handle_change_password(request: Request) -> Response:
    """Handle a password change request.
    
    Args:
        request: The password change request.
        
    Returns:
        A response with the password change result.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the password change data
        current_password = body.get('current_password')
        new_password = body.get('new_password')
        
        if not current_password or not new_password:
            logger.warning(f"Missing current_password or new_password for password change request from {request.remote}")
            return web.json_response({'error': 'Missing current_password or new_password'}, status=400)
        
        # Get the user
        user = request.get('user')
        
        if not user:
            logger.warning(f"Unauthenticated password change request from {request.remote}")
            return web.json_response({'error': 'Authentication required'}, status=401)
        
        # Attempt to change the password
        success, message = await security_manager.change_password(user['username'], current_password, new_password)
        
        if not success:
            logger.warning(f"Password change failed for user {user['username']} from {request.remote}: {message}")
            return web.json_response({'error': message}, status=400)
        
        # Log the password change event
        await security_manager.log_security_event(
            event_type='password_change',
            username=user['username'],
            ip_address=request.remote,
            details={
                'success': success,
                'message': message,
            }
        )
        
        # Return success
        return web.json_response({'message': message})
    except Exception as e:
        logger.exception(f"Error handling password change request from {request.remote}: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def handle_create_api_key(request: Request) -> Response:
    """Handle an API key creation request.
    
    Args:
        request: The API key creation request.
        
    Returns:
        A response with the API key creation result.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the API key data
        description = body.get('description', '')
        
        # Get the user
        user = request.get('user')
        
        if not user:
            logger.warning(f"Unauthenticated API key creation request from {request.remote}")
            return web.json_response({'error': 'Authentication required'}, status=401)
        
        # Attempt to create the API key
        success, message, api_key = await security_manager.create_api_key(user['username'], description)
        
        if not success:
            logger.warning(f"API key creation failed for user {user['username']} from {request.remote}: {message}")
            return web.json_response({'error': message}, status=400)
        
        # Log the API key creation event
        await security_manager.log_security_event(
            event_type='api_key_creation',
            username=user['username'],
            ip_address=request.remote,
            details={
                'success': success,
                'message': message,
                'description': description,
            }
        )
        
        # Return the API key
        return web.json_response({'api_key': api_key, 'message': message})
    except Exception as e:
        logger.exception(f"Error handling API key creation request from {request.remote}: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def handle_revoke_api_key(request: Request) -> Response:
    """Handle an API key revocation request.
    
    Args:
        request: The API key revocation request.
        
    Returns:
        A response with the API key revocation result.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Get the API key
        api_key = body.get('api_key')
        
        if not api_key:
            logger.warning(f"Missing api_key for API key revocation request from {request.remote}")
            return web.json_response({'error': 'Missing api_key'}, status=400)
        
        # Get the user
        user = request.get('user')
        
        if not user:
            logger.warning(f"Unauthenticated API key revocation request from {request.remote}")
            return web.json_response({'error': 'Authentication required'}, status=401)
        
        # Attempt to revoke the API key
        success, message = await security_manager.revoke_api_key(user['username'], api_key)
        
        if not success:
            logger.warning(f"API key revocation failed for user {user['username']} from {request.remote}: {message}")
            return web.json_response({'error': message}, status=400)
        
        # Log the API key revocation event
        await security_manager.log_security_event(
            event_type='api_key_revocation',
            username=user['username'],
            ip_address=request.remote,
            details={
                'success': success,
                'message': message,
                'api_key': api_key,
            }
        )
        
        # Return success
        return web.json_response({'message': message})
    except Exception as e:
        logger.exception(f"Error handling API key revocation request from {request.remote}: {e}")
        return web.json_response({'error': str(e)}, status=500)


def setup_auth_routes(app: web.Application) -> None:
    """Set up authentication routes for an application.
    
    Args:
        app: The application to set up.
    """
    # Add the routes
    app.router.add_post('/api/auth/login', handle_login)
    app.router.add_post('/api/auth/logout', handle_logout)
    app.router.add_post('/api/auth/register', handle_register)
    app.router.add_post('/api/auth/change-password', handle_change_password)
    app.router.add_post('/api/auth/create-api-key', handle_create_api_key)
    app.router.add_post('/api/auth/revoke-api-key', handle_revoke_api_key)
    
    logger.info("Authentication routes set up")
