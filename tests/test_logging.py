"""
Tests for Logging Infrastructure
================================

Test suite for the logging configuration module.

Test Categories:
    1. Logger creation and configuration
    2. LOG_LEVEL environment variable handling
    3. LOG_FILE environment variable handling
    4. @performance_logged decorator

Usage:
    pytest tests/test_logging.py -v

See: ADR-0009 Logging & Observability
"""

import logging
import os
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.logging_config import performance_logged, setup_logging


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def reset_loggers():
    """Reset logging state between tests."""
    # Clear all handlers from test loggers before each test
    for name in ["test.logger", "test.debug", "test.file", "agentive.perf"]:
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.setLevel(logging.NOTSET)
    yield
    # Cleanup after test
    for name in ["test.logger", "test.debug", "test.file", "agentive.perf"]:
        logger = logging.getLogger(name)
        logger.handlers = []


# =============================================================================
# SETUP_LOGGING TESTS
# =============================================================================


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_creates_logger_with_name(self):
        """setup_logging creates a logger with the specified name."""
        logger = setup_logging("test.logger")

        assert logger.name == "test.logger"
        assert isinstance(logger, logging.Logger)

    def test_default_level_is_info(self):
        """Default log level is INFO when LOG_LEVEL not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove LOG_LEVEL if present
            os.environ.pop("LOG_LEVEL", None)
            logger = setup_logging("test.logger")

            assert logger.level == logging.INFO

    def test_respects_log_level_debug(self, monkeypatch):
        """LOG_LEVEL=DEBUG sets logger level to DEBUG."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        logger = setup_logging("test.debug")

        assert logger.level == logging.DEBUG

    def test_respects_log_level_warning(self, monkeypatch):
        """LOG_LEVEL=WARNING sets logger level to WARNING."""
        monkeypatch.setenv("LOG_LEVEL", "WARNING")
        logger = setup_logging("test.logger")

        assert logger.level == logging.WARNING

    def test_respects_log_level_error(self, monkeypatch):
        """LOG_LEVEL=ERROR sets logger level to ERROR."""
        monkeypatch.setenv("LOG_LEVEL", "ERROR")
        logger = setup_logging("test.logger")

        assert logger.level == logging.ERROR

    def test_log_level_case_insensitive(self, monkeypatch):
        """LOG_LEVEL is case-insensitive."""
        monkeypatch.setenv("LOG_LEVEL", "debug")
        logger = setup_logging("test.debug")

        assert logger.level == logging.DEBUG

    def test_invalid_log_level_defaults_to_info(self, monkeypatch):
        """Invalid LOG_LEVEL defaults to INFO."""
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        logger = setup_logging("test.logger")

        assert logger.level == logging.INFO

    def test_creates_console_handler(self):
        """setup_logging adds a console handler."""
        logger = setup_logging("test.logger")

        assert len(logger.handlers) >= 1
        assert any(
            isinstance(h, logging.StreamHandler) for h in logger.handlers
        )

    def test_no_duplicate_handlers_on_multiple_calls(self):
        """Multiple calls to setup_logging don't add duplicate handlers."""
        logger1 = setup_logging("test.logger")
        handler_count = len(logger1.handlers)

        logger2 = setup_logging("test.logger")

        assert logger1 is logger2
        assert len(logger2.handlers) == handler_count

    def test_propagate_disabled(self):
        """Logger propagation is disabled to avoid duplicate logs."""
        logger = setup_logging("test.logger")

        assert logger.propagate is False


# =============================================================================
# FILE LOGGING TESTS
# =============================================================================


class TestFileLogging:
    """Tests for file logging configuration."""

    def test_creates_file_handler_when_log_file_set(self, monkeypatch, tmp_path):
        """LOG_FILE creates a file handler."""
        log_file = tmp_path / "test.log"
        monkeypatch.setenv("LOG_FILE", str(log_file))

        logger = setup_logging("test.file")

        from logging.handlers import RotatingFileHandler

        assert any(
            isinstance(h, RotatingFileHandler) for h in logger.handlers
        )

    def test_creates_log_directory(self, monkeypatch, tmp_path):
        """LOG_FILE creates parent directory if needed."""
        log_dir = tmp_path / "logs" / "subdir"
        log_file = log_dir / "test.log"
        monkeypatch.setenv("LOG_FILE", str(log_file))

        setup_logging("test.file")

        assert log_dir.exists()

    def test_writes_to_log_file(self, monkeypatch, tmp_path):
        """Logger writes messages to log file."""
        log_file = tmp_path / "test.log"
        monkeypatch.setenv("LOG_FILE", str(log_file))

        logger = setup_logging("test.file")
        logger.info("Test message")

        # Flush handlers
        for handler in logger.handlers:
            handler.flush()

        content = log_file.read_text()
        assert "Test message" in content


# =============================================================================
# PERFORMANCE DECORATOR TESTS
# =============================================================================


class TestPerformanceLogged:
    """Tests for @performance_logged decorator."""

    def test_returns_function_result(self):
        """Decorator returns the original function's result."""

        @performance_logged
        def my_func():
            return "result"

        assert my_func() == "result"

    def test_preserves_function_name(self):
        """Decorator preserves the original function name."""

        @performance_logged
        def my_func():
            pass

        assert my_func.__name__ == "my_func"

    def test_logs_slow_operations(self, caplog):
        """Decorator logs operations taking > 1 second."""

        @performance_logged
        def slow_func():
            time.sleep(1.1)
            return "done"

        with caplog.at_level(logging.INFO, logger="agentive.perf"):
            result = slow_func()

        assert result == "done"
        assert "slow_func completed" in caplog.text
        assert "1." in caplog.text  # Shows elapsed time

    def test_does_not_log_fast_operations(self, caplog):
        """Decorator does not log operations taking < 1 second."""

        @performance_logged
        def fast_func():
            return "quick"

        with caplog.at_level(logging.INFO, logger="agentive.perf"):
            result = fast_func()

        assert result == "quick"
        assert "fast_func" not in caplog.text

    def test_logs_exceptions(self, caplog):
        """Decorator logs when function raises exception."""

        @performance_logged
        def failing_func():
            raise ValueError("test error")

        with caplog.at_level(logging.ERROR, logger="agentive.perf"):
            with pytest.raises(ValueError):
                failing_func()

        assert "failing_func failed" in caplog.text
        assert "test error" in caplog.text

    def test_reraises_exceptions(self):
        """Decorator re-raises the original exception."""

        @performance_logged
        def failing_func():
            raise ValueError("original error")

        with pytest.raises(ValueError, match="original error"):
            failing_func()


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestLoggingIntegration:
    """Integration tests for logging infrastructure."""

    def test_hierarchical_loggers(self, caplog):
        """Child loggers inherit parent configuration."""
        parent = setup_logging("agentive")
        child = setup_logging("agentive.sync")

        # Both should be configured independently
        assert parent.name == "agentive"
        assert child.name == "agentive.sync"

    def test_emoji_prefixes_preserved(self, capsys):
        """Emoji prefixes in log messages are preserved."""
        logger = setup_logging("test.logger")

        logger.info("✅ Task synced successfully")
        logger.warning("⚠️  Warning message")
        logger.error("❌ Error occurred")

        # Flush handlers to ensure output is captured
        for handler in logger.handlers:
            handler.flush()

        captured = capsys.readouterr()
        assert "✅" in captured.err
        assert "⚠️" in captured.err
        assert "❌" in captured.err
