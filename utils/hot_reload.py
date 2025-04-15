"""
Hot Reload Utility for DMac

This module provides hot reload functionality for the DMac project,
allowing developers to see changes in real-time without restarting the server.
"""

import os
import sys
import time
import threading
import logging
import importlib
from typing import List, Dict, Any, Callable, Set
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

# Set up logging
logger = logging.getLogger('dmac.hot_reload')

class HotReloadHandler(FileSystemEventHandler):
    """
    File system event handler for hot reload functionality.
    """

    def __init__(self,
                 watch_directories: List[str],
                 file_extensions: List[str],
                 on_reload: Callable,
                 ignore_patterns: List[str] = None,
                 debounce_seconds: float = 0.5):
        """
        Initialize the hot reload handler.

        Args:
            watch_directories: List of directories to watch for changes
            file_extensions: List of file extensions to watch
            on_reload: Callback function to execute on reload
            ignore_patterns: List of patterns to ignore
            debounce_seconds: Debounce time in seconds
        """
        self.watch_directories = [Path(d).resolve() for d in watch_directories]
        self.file_extensions = file_extensions
        self.on_reload = on_reload
        self.ignore_patterns = ignore_patterns or []
        self.debounce_seconds = debounce_seconds
        self.last_reload_time = 0
        self.pending_reload = False
        self.reload_lock = threading.Lock()
        self.modified_files = set()

        # Start the debounce thread
        self.debounce_thread = threading.Thread(target=self._debounce_reload, daemon=True)
        self.debounce_thread.start()

    def on_any_event(self, event: FileSystemEvent):
        """
        Handle any file system event.

        Args:
            event: File system event
        """
        if event.is_directory:
            return

        # Check if the file has a watched extension
        file_path = Path(event.src_path).resolve()
        if not any(file_path.name.endswith(ext) for ext in self.file_extensions):
            return

        # Check if the file matches any ignore patterns
        if any(pattern in str(file_path) for pattern in self.ignore_patterns):
            return

        # Add the file to the modified files set
        with self.reload_lock:
            self.modified_files.add(file_path)
            self.pending_reload = True

    def _debounce_reload(self):
        """
        Debounce reload to prevent multiple reloads in quick succession.
        """
        while True:
            time.sleep(0.1)  # Check frequently but don't hog CPU

            with self.reload_lock:
                if self.pending_reload and time.time() - self.last_reload_time > self.debounce_seconds:
                    # Make a copy of modified files and clear the set
                    modified_files = self.modified_files.copy()
                    self.modified_files.clear()
                    self.pending_reload = False
                    self.last_reload_time = time.time()

                    # Execute the reload callback
                    try:
                        self.on_reload(modified_files)
                    except Exception as e:
                        logger.error(f"Error during hot reload: {str(e)}")

class HotReloader:
    """
    Hot reloader for the DMac project.
    """

    def __init__(self,
                 project_root: str = None,
                 watch_directories: List[str] = None,
                 file_extensions: List[str] = None,
                 ignore_patterns: List[str] = None,
                 debounce_seconds: float = 0.5,
                 auto_start: bool = True):
        """
        Initialize the hot reloader.

        Args:
            project_root: Root directory of the project
            watch_directories: List of directories to watch for changes
            file_extensions: List of file extensions to watch
            ignore_patterns: List of patterns to ignore
            debounce_seconds: Debounce time in seconds
            auto_start: Whether to start the reloader automatically
        """
        self.project_root = Path(project_root or os.getcwd()).resolve()

        # Default directories to watch
        self.watch_directories = watch_directories or [
            str(self.project_root / 'dashboard'),
            str(self.project_root / 'api'),
            str(self.project_root / 'utils'),
            str(self.project_root / 'agents'),
            str(self.project_root / 'integrations'),

        ]

        # Default file extensions to watch
        self.file_extensions = file_extensions or [
            '.py', '.js', '.html', '.css', '.json', '.yaml', '.yml'
        ]

        # Default patterns to ignore
        self.ignore_patterns = ignore_patterns or [
            '__pycache__', '.git', '.idea', '.vscode', 'node_modules',
            '.dart_tool', '.pub', 'build', '.pytest_cache'
        ]

        self.debounce_seconds = debounce_seconds
        self.observer = None
        self.handler = None
        self.reload_callbacks = []

        # Start the reloader if auto_start is True
        if auto_start:
            self.start()

    def start(self):
        """
        Start the hot reloader.
        """
        if self.observer:
            logger.warning("Hot reloader is already running")
            return

        # Create the event handler
        self.handler = HotReloadHandler(
            watch_directories=self.watch_directories,
            file_extensions=self.file_extensions,
            on_reload=self._on_reload,
            ignore_patterns=self.ignore_patterns,
            debounce_seconds=self.debounce_seconds
        )

        # Create and start the observer
        self.observer = Observer()
        for directory in self.watch_directories:
            if os.path.exists(directory):
                self.observer.schedule(self.handler, directory, recursive=True)
            else:
                logger.warning(f"Directory not found: {directory}")

        self.observer.start()
        logger.info(f"Hot reloader started, watching: {', '.join(self.watch_directories)}")

    def stop(self):
        """
        Stop the hot reloader.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("Hot reloader stopped")

    def add_reload_callback(self, callback: Callable[[Set[Path]], None]):
        """
        Add a callback function to execute on reload.

        Args:
            callback: Callback function that takes a set of modified files
        """
        self.reload_callbacks.append(callback)

    def _on_reload(self, modified_files: Set[Path]):
        """
        Handle reload event.

        Args:
            modified_files: Set of modified files
        """
        logger.info(f"Hot reload triggered by changes to {len(modified_files)} files")

        # Execute all registered callbacks
        for callback in self.reload_callbacks:
            try:
                callback(modified_files)
            except Exception as e:
                logger.error(f"Error in reload callback: {str(e)}")

        # Reload Python modules if any Python files were modified
        python_files = [f for f in modified_files if f.name.endswith('.py')]
        if python_files:
            self._reload_python_modules(python_files)

    def _reload_python_modules(self, python_files: List[Path]):
        """
        Reload Python modules that were modified.

        Args:
            python_files: List of modified Python files
        """
        for file_path in python_files:
            try:
                # Convert file path to module name
                rel_path = file_path.relative_to(self.project_root)
                module_parts = list(rel_path.parts)

                # Remove file extension
                module_parts[-1] = module_parts[-1][:-3]

                # Convert to module name
                module_name = '.'.join(module_parts)

                # Check if the module is loaded
                if module_name in sys.modules:
                    # Reload the module
                    logger.info(f"Reloading module: {module_name}")
                    importlib.reload(sys.modules[module_name])
            except Exception as e:
                logger.error(f"Error reloading module {file_path}: {str(e)}")

# Singleton instance
_hot_reloader = None

def get_hot_reloader() -> HotReloader:
    """
    Get the singleton hot reloader instance.

    Returns:
        Hot reloader instance
    """
    global _hot_reloader
    if _hot_reloader is None:
        _hot_reloader = HotReloader(auto_start=False)
    return _hot_reloader

def start_hot_reload(project_root: str = None,
                    watch_directories: List[str] = None,
                    file_extensions: List[str] = None,
                    ignore_patterns: List[str] = None,
                    debounce_seconds: float = 0.5):
    """
    Start the hot reloader.

    Args:
        project_root: Root directory of the project
        watch_directories: List of directories to watch for changes
        file_extensions: List of file extensions to watch
        ignore_patterns: List of patterns to ignore
        debounce_seconds: Debounce time in seconds

    Returns:
        Hot reloader instance
    """
    reloader = get_hot_reloader()

    # Update configuration if provided
    if project_root:
        reloader.project_root = Path(project_root).resolve()
    if watch_directories:
        reloader.watch_directories = watch_directories
    if file_extensions:
        reloader.file_extensions = file_extensions
    if ignore_patterns:
        reloader.ignore_patterns = ignore_patterns
    if debounce_seconds:
        reloader.debounce_seconds = debounce_seconds

    # Start the reloader
    reloader.start()

    return reloader

def stop_hot_reload():
    """
    Stop the hot reloader.
    """
    reloader = get_hot_reloader()
    reloader.stop()

def add_reload_callback(callback: Callable[[Set[Path]], None]):
    """
    Add a callback function to execute on reload.

    Args:
        callback: Callback function that takes a set of modified files
    """
    reloader = get_hot_reloader()
    reloader.add_reload_callback(callback)
