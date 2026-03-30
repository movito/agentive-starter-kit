# Spec Compliance Check: ASK-0039 Workflow Verification — Full TDD Lifecycle

## Task Specification

```markdown
# ASK-0039: Workflow Verification — Full TDD Lifecycle (All 9 Phases)

**Status**: In Progress
**Priority**: medium
**Assigned To**: feature-developer-v3
**Estimated Effort**: 1-2 hours
**Created**: 2026-02-27
**Depends On**: ASK-0037, ASK-0038

## Purpose

**This is a verification task.** Its primary goal is to exercise ALL 9 phases of the
v3 workflow on a real Python code change with TDD. This is the comprehensive test —
if this task completes successfully, the upgraded workflow is validated.

## Overview

Add a new lint rule `DK004` to `scripts/pattern_lint.py`: detect bare `except Exception`
clauses that silently swallow errors without logging or re-raising.

## Requirements

### Functional Requirements

1. Add rule `DK004` to `scripts/pattern_lint.py`:
   - **Detects**: `except Exception` (or `except BaseException`) followed by `pass`
     or an empty body — i.e., silently swallowed exceptions
   - **Does NOT flag**: `except Exception as e: logger.error(...)` (logged)
   - **Does NOT flag**: `except Exception: raise` (re-raised)
   - **Does NOT flag**: `except Exception as e: return ...` (explicit return)
   - **Suppressed by**: `# noqa: DK004` comment on the except line
   - **Message**: `"Bare 'except {type}' with pass/empty body silently swallows errors. Log, re-raise, or add '# noqa: DK004'."`

2. Add tests in `tests/test_pattern_lint.py` (create if it doesn't exist):
   - Test that DK004 catches `except Exception: pass`
   - Test that DK004 catches `except BaseException: pass`
   - Test that DK004 does NOT flag `except Exception as e: logger.error(e)`
   - Test that DK004 does NOT flag `except Exception: raise`
   - Test that DK004 does NOT flag lines with `# noqa: DK004`
   - Test that DK004 does NOT flag `except ValueError: pass` (specific exceptions are OK)

3. Register DK004 in the `lint_file()` function alongside DK001 and DK003

4. Update the module docstring to list DK004

### Non-Functional Requirements

1. Follow AST-based approach (consistent with DK001/DK003 — no regex)
2. Tests must run via `pytest tests/test_pattern_lint.py -v`
3. Pattern lint must still pass on existing codebase after adding DK004
4. All existing tests must still pass
```

## Implementation

### Changed Files

#### `scripts/pattern_lint.py`

```python
#!/usr/bin/env python3
"""Project-specific lint rules that catch recurring bot-finding patterns.

Metadata:
    version: 1.0.0
    origin: dispatch-kit
    origin-version: 0.3.2
    last-updated: 2026-02-27
    created-by: "@movito with planner2"

Runs as a pre-commit hook and in CI. Returns exit code 1 if any violations
are found. Operates on AST for accuracy — no regex hacks.

Rules:
  DK001  str.replace() used for extension/suffix removal
  DK003  'in' used for identifier comparison without '# substring:' comment
  DK004  Bare 'except Exception/BaseException' with pass/empty body
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Violation:
    rule: str
    path: str
    line: int
    message: str

    def __str__(self) -> str:
        return f"{self.path}:{self.line}: {self.rule} {self.message}"


def check_dk001(tree: ast.AST, source_lines: list[str], path: str) -> list[Violation]:
    """DK001: str.replace() used for extension/suffix removal."""
    violations = []
    extension_patterns = {".md", ".py", ".yml", ".yaml", ".json", ".txt", ".toml"}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "replace":
            continue
        if len(node.args) < 2:
            continue

        first_arg = node.args[0]
        second_arg = node.args[1]

        if (
            isinstance(first_arg, ast.Constant)
            and isinstance(first_arg.value, str)
            and first_arg.value in extension_patterns
            and isinstance(second_arg, ast.Constant)
            and second_arg.value == ""
        ):
            line = (
                source_lines[node.lineno - 1]
                if node.lineno <= len(source_lines)
                else ""
            )
            if "# noqa: DK001" not in line:
                violations.append(
                    Violation(
                        rule="DK001",
                        path=path,
                        line=node.lineno,
                        message=(
                            f'str.replace("{first_arg.value}", "")'
                            f" removes all occurrences."
                            f' Use removesuffix("{first_arg.value}").'
                        ),
                    )
                )

    return violations


def check_dk003(tree: ast.AST, source_lines: list[str], path: str) -> list[Violation]:
    """DK003: 'in' used for string containment on identifier-like values."""
    # [existing code unchanged]
    ...


def check_dk004(tree: ast.AST, source_lines: list[str], path: str) -> list[Violation]:
    """DK004: Bare 'except Exception/BaseException' with pass or empty body.

    Detects patterns like:
      except Exception: pass
      except BaseException: pass
      except Exception as e: pass

    Does NOT flag:
      except Exception as e: logger.error(e)   (logged)
      except Exception: raise                   (re-raised)
      except Exception as e: return None        (explicit return)
      except ValueError: pass                   (specific exception)
      except: pass                              (bare except without type)

    Suppressed by '# noqa: DK004' comment on the except line.
    """
    violations = []
    broad_exceptions = {"Exception", "BaseException"}

    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue

        # Only flag broad exception types (Exception, BaseException)
        if node.type is None:
            # Bare 'except:' without a type — not in scope
            continue
        if not isinstance(node.type, ast.Name):
            continue
        if node.type.id not in broad_exceptions:
            continue

        # Check if body is pass-only or empty
        if not _is_swallowed(node.body):
            continue

        # Check for noqa suppression
        line = source_lines[node.lineno - 1] if node.lineno <= len(source_lines) else ""
        if "# noqa: DK004" in line:
            continue

        violations.append(
            Violation(
                rule="DK004",
                path=path,
                line=node.lineno,
                message=(
                    f"Bare 'except {node.type.id}' with pass/empty body"
                    " silently swallows errors."
                    " Log, re-raise, or add '# noqa: DK004'."
                ),
            )
        )

    return violations


def _is_swallowed(body: list[ast.stmt]) -> bool:
    """Check if an except handler body silently swallows the exception.

    Returns True if the body is empty or contains only ``pass``.
    Returns False if the body contains raise, return, logging calls,
    or any other meaningful statement.
    """
    if not body:
        return True

    # Body contains only 'pass' statement(s)
    if all(isinstance(stmt, ast.Pass) for stmt in body):
        return True

    # Check if body contains meaningful handling
    for stmt in body:
        if isinstance(stmt, ast.Raise):
            return False
        if isinstance(stmt, ast.Return):
            return False
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            func = stmt.value.func
            # logger.error(...), logging.warning(...), etc.
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id in ("logger", "logging", "log"):
                    return False

    return False


def lint_file(path: str) -> list[Violation]:
    """Run all lint rules on a single Python file."""
    try:
        source = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []

    try:
        tree = ast.parse(source, filename=path)
    except SyntaxError:
        return []

    source_lines = source.splitlines()

    violations = []
    violations.extend(check_dk001(tree, source_lines, path))
    violations.extend(check_dk003(tree, source_lines, path))
    violations.extend(check_dk004(tree, source_lines, path))

    return violations
```

#### `scripts/validate_task_status.py`

Change: Narrowed `except Exception: pass` to `except (OSError, UnicodeDecodeError): pass` in `get_status_from_file()` — this was a real DK004 violation found by the new rule.

```python
def get_status_from_file(file_path: Path) -> Optional[str]:
    """Extract the Status field from a task file."""
    try:
        content = file_path.read_text()
        match = re.search(r"\*\*Status\*\*:\s*(\w+(?:\s+\w+)?)", content)
        if match:
            return match.group(1).strip()
    except (OSError, UnicodeDecodeError):
        pass
    return None
```

### Test Files

#### `tests/test_pattern_lint.py`

```python
"""Tests for scripts/pattern_lint.py — project-specific lint rules."""

from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from pattern_lint import check_dk001, check_dk003, check_dk004


def _parse(code: str) -> tuple[ast.AST, list[str]]:
    """Parse code string into AST and source lines."""
    dedented = textwrap.dedent(code).strip()
    tree = ast.parse(dedented)
    lines = dedented.splitlines()
    return tree, lines


# ── DK004: bare except Exception with pass/empty body ──────────────


class TestDK004:
    def test_catches_except_exception_pass(self):
        """Bare except Exception: pass should be flagged."""
        tree, lines = _parse("""
            try:
                do_something()
            except Exception:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1
        assert violations[0].rule == "DK004"
        assert "silently swallows" in violations[0].message

    def test_catches_except_base_exception_pass(self):
        """Bare except BaseException: pass should be flagged."""
        tree, lines = _parse("""
            try:
                do_something()
            except BaseException:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1
        assert "BaseException" in violations[0].message

    def test_does_not_flag_logged_exception(self):
        """except Exception as e: logger.error(e) is not bare."""
        tree, lines = _parse("""
            try:
                do_something()
            except Exception as e:
                logger.error(e)
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_reraised(self):
        """except Exception: raise is not bare."""
        tree, lines = _parse("""
            try:
                do_something()
            except Exception:
                raise
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_noqa_suppresses(self):
        """# noqa: DK004 suppresses the violation."""
        tree, lines = _parse("""
            try:
                do_something()
            except Exception:  # noqa: DK004
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_specific_exception(self):
        """except ValueError: pass is OK — only broad exceptions flagged."""
        tree, lines = _parse("""
            try:
                do_something()
            except ValueError:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_explicit_return(self):
        """except Exception as e: return None is not bare."""
        tree, lines = _parse("""
            def func():
                try:
                    do_something()
                except Exception as e:
                    return None
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_bare_except_without_type(self):
        """Bare 'except:' (no type) is not in scope — only Exception/BaseException."""
        tree, lines = _parse("""
            try:
                do_something()
            except:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_catches_except_exception_as_with_pass(self):
        """except Exception as e: pass should be flagged (name bound but unused)."""
        tree, lines = _parse("""
            try:
                do_something()
            except Exception as e:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1

    def test_does_not_flag_logging_call(self):
        """except Exception as e: logging.warning(...) is not bare."""
        tree, lines = _parse("""
            try:
                do_something()
            except Exception as e:
                logging.warning("Error: %s", e)
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_tuple_exception_with_pass(self):
        """except (Exception, ValueError): pass uses tuple — not a Name node."""
        tree, lines = _parse("""
            try:
                do_something()
            except (Exception, ValueError):
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0


# Integration tests also updated to include DK004 checks.
```

## Handoff Notes

- DK004 follows the exact same pattern as DK001/DK003: AST-based, same function signature, same noqa mechanism
- Found and fixed a real DK004 violation in `scripts/validate_task_status.py:53` — narrowed `except Exception` to `except (OSError, UnicodeDecodeError)`
- `_is_swallowed()` helper uses `all()` guard with `isinstance(ast.Pass)` for robustness
- Tuple exception types (e.g., `except (Exception, ValueError):`) are not flagged because `node.type` is `ast.Tuple`, not `ast.Name`
