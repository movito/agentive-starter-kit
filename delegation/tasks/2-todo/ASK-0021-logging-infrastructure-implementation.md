# ASK-0021: Logging Infrastructure Implementation

**Status**: Todo
**Priority**: medium
**Assigned To**: feature-developer
**Estimated Effort**: 2-3 hours
**Created**: 2025-11-28

## Related Tasks

**Parent Task**: ASK-0009 (Logging & Observability ADR)
**Depends On**: ADR-0009 (documents the pattern)
**Blocks**: None
**Related**: ADR-0008 (Configuration Architecture)

## Overview

Implement the logging infrastructure documented in ADR-0009. This replaces ~30 `print()` statements with proper Python logging, adds configurable verbosity, and enables optional file logging.

**Why Important**: Currently all output uses `print()`, which is not configurable, filterable, or persistent. Proper logging enables better debugging, CI visibility, and future monitoring.

## Current State

| Component | Current | Target |
|-----------|---------|--------|
| `sync_tasks_to_linear.py` | ~25 print() | logger.info/error |
| `linear_sync_utils.py` | ~5 print() | logger.info/debug |
| Verbosity control | None | LOG_LEVEL env var |
| File logging | None | Optional via LOG_FILE |
| Performance tracking | None | @performance_logged decorator |

## Requirements

### Functional Requirements

1. Create `scripts/logging_config.py` module
2. Replace all `print()` with appropriate `logger.*()` calls
3. Add LOG_LEVEL, LOG_FILE environment variables
4. Add `@performance_logged` decorator for slow operations
5. Update `.env.template` with new variables

### Non-Functional Requirements

- Maintain existing CLI output behavior (same emoji prefixes)
- No new dependencies (use Python stdlib logging)
- Tests should use pytest caplog fixture
- Log files should rotate (10MB, 5 backups)

## Acceptance Criteria

### Must Have

- [ ] `scripts/logging_config.py` created with `setup_logging()` function
- [ ] All `print()` replaced with `logger.*()` calls (~30 replacements)
- [ ] LOG_LEVEL environment variable controls verbosity (default: INFO)
- [ ] LOG_FILE enables optional file logging with rotation
- [ ] `.env.template` updated with LOG_LEVEL and LOG_FILE
- [ ] Existing CLI output unchanged at INFO level
- [ ] Tests pass with logging changes

### Should Have

- [ ] `@performance_logged` decorator for timing slow operations
- [ ] At least one test using pytest caplog
- [ ] Logger hierarchy: `agentive.sync`, `agentive.utils`

### Could Have

- [ ] LOG_JSON for structured JSON output
- [ ] Colored console output (optional)

## Implementation Plan

### Step 1: Create logging_config.py (30 min)

```python
# scripts/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional

def setup_logging(name: str = "agentive") -> logging.Logger:
    """Configure logging for the application."""
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(console)

    # Optional file handler
    log_file = os.getenv("LOG_FILE")
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        ))
        logger.addHandler(file_handler)

    return logger
```

### Step 2: Replace print() in sync_tasks_to_linear.py (45 min)

**Pattern for replacement:**

| Current | Replacement |
|---------|-------------|
| `print("✅ ...")` | `logger.info("✅ ...")` |
| `print("❌ Error: ...")` | `logger.error("❌ ...")` |
| `print("⚠️ ...")` | `logger.warning("⚠️ ...")` |
| `print(f"📋 ...")` | `logger.info(f"📋 ...")` |
| `print("=" * 60)` | `logger.info("=" * 60)` |

**Add at top of file:**
```python
from logging_config import setup_logging
logger = setup_logging("agentive.sync")
```

### Step 3: Replace print() in linear_sync_utils.py (15 min)

```python
from logging_config import setup_logging
logger = setup_logging("agentive.utils")
```

### Step 4: Add performance decorator (20 min)

```python
# In logging_config.py
import time
import functools

def performance_logged(func):
    """Log execution time for slow operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(f"agentive.perf")
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if elapsed > 1.0:
                logger.info(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"{func.__name__} failed after {elapsed:.2f}s: {e}")
            raise
    return wrapper
```

### Step 5: Update .env.template (10 min)

Add section:
```bash
# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# LOG_LEVEL: DEBUG, INFO, WARNING, ERROR (default: INFO)
# LOG_LEVEL=DEBUG

# LOG_FILE: Path to log file (enables file logging with rotation)
# LOG_FILE=logs/agentive.log
```

### Step 6: Add tests (30 min)

```python
# tests/test_logging.py
import logging
from scripts.logging_config import setup_logging, performance_logged

def test_setup_logging_creates_logger():
    logger = setup_logging("test.logger")
    assert logger.name == "test.logger"
    assert logger.level == logging.INFO

def test_setup_logging_respects_level(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    logger = setup_logging("test.debug")
    assert logger.level == logging.DEBUG

def test_performance_logged_logs_slow_operations(caplog):
    @performance_logged
    def slow_func():
        import time
        time.sleep(1.1)
        return "done"

    with caplog.at_level(logging.INFO):
        result = slow_func()

    assert result == "done"
    assert "slow_func completed" in caplog.text
```

### Step 7: Verify and Test (30 min)

1. Run tests: `pytest tests/`
2. Test CLI output: `python scripts/sync_tasks_to_linear.py --help`
3. Test LOG_LEVEL: `LOG_LEVEL=DEBUG python scripts/sync_tasks_to_linear.py`
4. Test LOG_FILE: `LOG_FILE=test.log python scripts/sync_tasks_to_linear.py`

## Success Metrics

### Quantitative

- All ~30 print() statements replaced
- 0 new dependencies added
- Tests pass with ≥80% coverage
- CI passes

### Qualitative

- CLI output unchanged at INFO level
- DEBUG level shows more detail
- File logging works with rotation

## Time Estimate

| Phase | Time |
|-------|------|
| Create logging_config.py | 30 min |
| Replace print() in sync script | 45 min |
| Replace print() in utils | 15 min |
| Add performance decorator | 20 min |
| Update .env.template | 10 min |
| Add tests | 30 min |
| Verify and test | 30 min |
| **Total** | **2-3 hours** |

## Technical Notes

### print() Locations (for reference)

```bash
# sync_tasks_to_linear.py - ~25 print statements
grep -n "print(" scripts/sync_tasks_to_linear.py

# linear_sync_utils.py - ~5 print statements
grep -n "print(" scripts/linear_sync_utils.py
```

### Log Level Mapping

| print() Pattern | Logger Method |
|-----------------|---------------|
| Success (✅) | logger.info() |
| Error (❌) | logger.error() |
| Warning (⚠️) | logger.warning() |
| Info (📋, 🔄, 📂) | logger.info() |
| Debug details | logger.debug() |

### Backward Compatibility

- Default LOG_LEVEL=INFO maintains current verbosity
- Emoji prefixes preserved in log messages
- No changes to CLI arguments or return codes

## References

- **ADR**: `docs/decisions/adr/ADR-0009-logging-observability.md`
- Python logging: https://docs.python.org/3/library/logging.html
- pytest caplog: https://docs.pytest.org/en/stable/how-to/logging.html
- RotatingFileHandler: https://docs.python.org/3/library/logging.handlers.html

## Notes

- Keep emoji prefixes for visual consistency
- Use `logger.exception()` in except blocks for stack traces
- Consider adding `--verbose` CLI flag in future

---

**Template Version**: 1.0.0
**Created**: 2025-11-28
