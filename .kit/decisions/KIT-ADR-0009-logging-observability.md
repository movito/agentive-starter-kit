# KIT-ADR-0009: Logging & Observability Architecture

**Status**: Accepted

**Date**: 2025-11-28

**Deciders**: planner, User

## Context

### Problem Statement

The project currently uses `print()` statements for all output, which is:
- Not configurable (can't adjust verbosity)
- Not structured (hard to parse programmatically)
- Not persistent (no file logging)
- Not hierarchical (can't filter by component)

We need a proper logging architecture that supports development debugging, production monitoring, and future observability needs.

### Forces at Play

**Technical Requirements:**
- Console output for development (human-readable)
- File output for persistence (debugging after-the-fact)
- Structured output option (JSON for APIs/monitoring)
- Component-based filtering (sync vs agents vs CLI)

**Constraints:**
- Must be backward-compatible (existing CLI behavior)
- Should use Python standard library (no heavy dependencies)
- Must work in CI environment (GitHub Actions)

**Assumptions:**
- Most users run scripts locally during development
- CI runs need captured output for debugging
- Future monitoring may require structured logs

## Decision

We will adopt a **hierarchical logging architecture** with dual output (console + file) and optional structured formatting.

### Core Principles

1. **Hierarchical loggers**: Component-based naming (`agentive.sync`, `agentive.cli`)
2. **Dual output**: Console for humans, files for persistence
3. **Configurable verbosity**: Environment variable controls log level
4. **Performance tracking**: Decorator for timing slow operations

### Implementation Details

**Logger Hierarchy:**

```
agentive                    # Root logger
├── agentive.sync           # Linear sync operations
├── agentive.cli            # CLI commands
├── agentive.daemon         # Task monitor daemon
└── agentive.utils          # Utility functions
```

**Configuration (via environment):**

```bash
# Log level (default: INFO)
LOG_LEVEL=DEBUG              # DEBUG, INFO, WARNING, ERROR

# Log file (default: None - console only)
LOG_FILE=logs/agentive.log   # Enable file logging

# Structured output (default: False)
LOG_JSON=true                # JSON format for machine parsing
```

**Logger Setup Pattern:**

```python
# scripts/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(name: str = "agentive") -> logging.Logger:
    """Configure logging for the application."""
    logger = logging.getLogger(name)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))

    # Console handler (human-readable)
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(console)

    # File handler (optional, rotating)
    log_file = os.getenv("LOG_FILE")
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        logger.addHandler(file_handler)

    return logger
```

**Usage in Scripts:**

```python
# scripts/sync_tasks_to_linear.py
from logging_config import setup_logging

logger = setup_logging("agentive.sync")

def sync_task(task):
    logger.info(f"Syncing task: {task.task_id}")
    logger.debug(f"Task details: {task}")
    # ... sync logic ...
    logger.info(f"✅ Synced: {task.task_id}")
```

**Performance Logging Decorator:**

```python
import time
import functools

def performance_logged(func):
    """Log execution time for slow operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"agentive.perf.{func.__module__}")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if elapsed > 1.0:  # Only log slow operations
                logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {e}")
            raise
    return wrapper
```

**Log Levels Guide:**

| Level | Use For | Example |
|-------|---------|---------|
| DEBUG | Detailed diagnostics | `logger.debug(f"Parsing {file}")` |
| INFO | Normal operations | `logger.info("✅ Task synced")` |
| WARNING | Recoverable issues | `logger.warning("No team ID, auto-detecting")` |
| ERROR | Failures | `logger.error(f"API error: {e}")` |

**Testing with Captured Logs:**

```python
# tests/test_sync.py
import logging

def test_sync_logs_success(caplog):
    """Verify sync logs appropriate messages."""
    with caplog.at_level(logging.INFO):
        sync_task(mock_task)

    assert "Syncing task" in caplog.text
    assert "✅ Synced" in caplog.text
```

## Consequences

### Positive

- ✅ **Configurable verbosity**: Adjust via `LOG_LEVEL`
- ✅ **Persistent logs**: Optional file output with rotation
- ✅ **Filtered output**: Component-based logger names
- ✅ **Performance visibility**: Timing decorator for slow ops
- ✅ **Test-friendly**: pytest caplog integration

### Negative

- ⚠️ **Migration effort**: Replace ~30 print statements
- ⚠️ **Slight complexity**: Logger setup vs direct print
- ⚠️ **File management**: Log rotation needs disk space awareness

### Neutral

- 📊 **Standard library**: No new dependencies (logging is built-in)
- 📊 **Future-ready**: Can add structured logging (structlog) later

## Alternatives Considered

### Alternative 1: Keep print() Statements

**Description**: Continue using print() for all output

**Rejected because**:
- ❌ Not configurable (no log levels)
- ❌ Not filterable (all or nothing)
- ❌ Not persistent (console only)
- ❌ Not testable (hard to capture)

### Alternative 2: structlog from Start

**Description**: Use structlog for structured logging immediately

**Not adopted yet because**:
- ❌ Additional dependency
- ❌ Overkill for current needs
- ✅ Good future option when we need JSON logs

### Alternative 3: loguru

**Description**: Use loguru for simplified logging

**Not adopted because**:
- ❌ Additional dependency
- ❌ Non-standard API
- ❌ Standard library is sufficient

## Implementation Status

**Current State**: Documentation only (this ADR)

**Implementation Task**: ASK-0021 (Logging Infrastructure Implementation)
- Replace print() with logger calls
- Add logging_config.py module
- Update .env.template with LOG_* variables
- Add performance decorator

## Related Decisions

- KIT-ADR-0008: Configuration Architecture (environment variable pattern)
- KIT-ADR-0005: Test Infrastructure (pytest caplog for log testing)

## References

- Python logging: https://docs.python.org/3/library/logging.html
- 12-factor logs: https://12factor.net/logs
- structlog (future): https://www.structlog.org/
- pytest caplog: https://docs.pytest.org/en/stable/how-to/logging.html

## Revision History

- 2025-11-28: Initial decision (Accepted)
  - Documented hierarchical logging pattern
  - Defined dual output (console + file)
  - Created implementation task ASK-0021

---

**Template Version**: 1.1.0
**Last Updated**: 2025-11-28
**Project**: agentive-starter-kit
