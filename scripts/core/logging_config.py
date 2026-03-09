"""
Logging Configuration
=====================

Configurable logging infrastructure for the agentive-starter-kit.

Features:
    - Environment variable configuration (LOG_LEVEL, LOG_FILE)
    - Console output with timestamp formatting
    - Optional file logging with rotation (10MB, 5 backups)
    - Performance decorator for timing slow operations

Usage:
    from logging_config import setup_logging, performance_logged

    logger = setup_logging("agentive.sync")
    logger.info("✅ Task synced successfully")

    @performance_logged
    def slow_operation():
        ...

Environment Variables:
    LOG_LEVEL: DEBUG, INFO, WARNING, ERROR (default: INFO)
    LOG_FILE: Path to log file (enables file logging with rotation)

See: ADR-0009 Logging & Observability
"""

import functools
import logging
import os
import time
from logging.handlers import RotatingFileHandler
from typing import Callable, TypeVar

# Type variable for preserving function signatures
F = TypeVar("F", bound=Callable)


def setup_logging(name: str = "agentive") -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        name: Logger name (hierarchical, e.g., "agentive.sync")

    Returns:
        Configured logger instance

    Environment Variables:
        LOG_LEVEL: Logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO
        LOG_FILE: Path to log file. If set, enables file logging with rotation.

    Example:
        logger = setup_logging("agentive.sync")
        logger.info("✅ Task synced")
        logger.debug("Processing file: %s", filename)
    """
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if logger.handlers:
        return logger

    # Get log level from environment
    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)

    # Console handler - always enabled
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler - optional, enabled via LOG_FILE env var
    log_file = os.getenv("LOG_FILE")
    if log_file:
        # Create directory if needed
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # Rotating file handler: 10MB max, 5 backups
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger (avoid duplicate logs)
    logger.propagate = False

    return logger


def performance_logged(func: F) -> F:
    """
    Decorator to log execution time for slow operations.

    Logs at INFO level if operation takes > 1 second.
    Logs at ERROR level if operation raises an exception.

    Args:
        func: Function to wrap

    Returns:
        Wrapped function with performance logging

    Example:
        @performance_logged
        def sync_to_linear():
            # Slow API calls here
            pass
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger("agentive.perf")
        start = time.perf_counter()

        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start

            # Only log if operation was slow (> 1 second)
            if elapsed > 1.0:
                logger.info("%s completed in %.2fs", func.__name__, elapsed)

            return result

        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error("%s failed after %.2fs: %s", func.__name__, elapsed, e)
            raise

    return wrapper  # type: ignore[return-value]
