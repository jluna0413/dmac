"""
Security package for DMac.

This package provides security features for the DMac system.
"""

from security.security_manager import security_manager
from security.secure_api import setup_secure_api, setup_auth_routes, require_role, require_admin
from security.secure_file_ops import secure_file_ops
from security.secure_process_ops import secure_process_ops

__all__ = [
    'security_manager',
    'setup_secure_api',
    'setup_auth_routes',
    'require_role',
    'require_admin',
    'secure_file_ops',
    'secure_process_ops',
]
