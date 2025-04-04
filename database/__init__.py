"""
Database package for DMac.

This package provides database functionality for the DMac system.
"""

from .pg_manager import pg_manager

# Export the PostgreSQL manager as the default database manager
db_manager = pg_manager

__all__ = ['db_manager', 'pg_manager']
