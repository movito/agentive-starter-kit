# Code Review: agentive-starter-kit — ASK-0039 Add DK004 Lint Rule

## Context

Added a new AST-based lint rule DK004 to `scripts/pattern_lint.py` that detects bare
`except Exception: pass` and `except BaseException: pass` patterns that silently swallow
errors. Also fixed a real DK004 violation found in `scripts/validate_task_status.py`.

**Task**: ASK-0039
**PR**: #22
**Bot review status**: CodeRabbit: APPROVED (0 threads), BugBot: in progress (no findings yet)

## Changed Files

### Source: `scripts/pattern_lint.py`

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
    """DK001: str.replace() used for extension/suffix removal.

    Detects patterns like:
      filename.replace(".md", "")
      name.replace(".py", "")
      s.replace(".yml", "")

    Fix: use str.removesuffix(".ext") instead.
    """
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

        # Check: .replace(".ext", "")
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
    """DK003: 'in' used for string containment on identifier-like values.

    Detects patterns like:
      if task_id in event.task      # string-in-string: substring match
      if name in agent_name         # string-in-string: substring match

    Does NOT flag container membership (legitimate):
      if task_id in frozenset(...)  # set membership
      if name in [a, b, c]         # list membership
      if name in some_set           # variable ending in _set, _list, etc.

    Suppressed by '# substring:' comment on the same line.
    """
    violations = []
    identifier_hints = {"id", "name", "type", "key", "status", "state", "mode", "login"}
    # Right-side names suggesting a collection (not a string)
    collection_suffixes = (
        "_set",
        "_list",
        "_dict",
        "_map",
        "_tuple",
        "_frozenset",
        "_types",
        "_names",
        "_ids",
        "_keys",
        "_values",
        "_items",
        "_transitions",
        "_auto",
        "_counts",
        "_sessions",
        "_statuses",
    )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue

        for op, comparator in zip(node.ops, node.comparators, strict=False):
            if not isinstance(op, ast.In):
                continue

            # Skip collection literals — set, list, tuple, dict on the right
            if isinstance(comparator, (ast.Set, ast.List, ast.Tuple, ast.Dict)):
                continue
            # Skip set/frozenset/list/dict/tuple constructor calls
            if isinstance(comparator, ast.Call):
                func_name = _extract_name(comparator.func)
                if func_name in {"set", "frozenset", "list", "dict", "tuple"}:
                    continue

            left = node.left
            left_name = _extract_name(left)
            right_name = _extract_name(comparator)

            if not left_name or not right_name:
                continue

            # Skip if right side looks like a collection variable
            right_lower = right_name.lower().split(".")[-1]  # last segment
            if any(right_lower.endswith(s) for s in collection_suffixes):
                continue

            # Both sides must look like identifier variables
            left_is_id = any(hint in left_name.lower() for hint in identifier_hints)
            right_is_id = any(hint in right_name.lower() for hint in identifier_hints)

            if not (left_is_id and right_is_id):
                continue

            line = (
                source_lines[node.lineno - 1]
                if node.lineno <= len(source_lines)
                else ""
            )

            # Suppressed by '# substring:' comment
            if "# substring:" in line or "# noqa: DK003" in line:
                continue

            violations.append(
                Violation(
                    rule="DK003",
                    path=path,
                    line=node.lineno,
                    message=(
                        f"'{left_name} in {right_name}'"
                        " looks like string containment."
                        " Use == or add '# substring: <reason>'."
                    ),
                )
            )

    return violations


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


def _extract_name(node: ast.AST) -> str | None:
    """Extract a readable name from an AST node."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _extract_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
        return node.attr
    return None


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


def main() -> int:
    """Entry point. Accepts file paths as arguments."""
    if len(sys.argv) < 2:
        print("Usage: pattern_lint.py <file1.py> [file2.py ...]", file=sys.stderr)
        return 0  # No files = no violations

    all_violations = []
    for path in sys.argv[1:]:
        if not path.endswith(".py"):
            continue
        all_violations.extend(lint_file(path))

    if all_violations:
        for v in sorted(all_violations, key=lambda v: (v.path, v.line)):
            print(v, file=sys.stderr)
        print(f"\n{len(all_violations)} pattern violation(s) found.", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Source: `scripts/validate_task_status.py` (minor fix only)

Only change: line 53 narrowed from `except Exception:` to `except (OSError, UnicodeDecodeError):`.

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

## Test Files

### Tests: `tests/test_pattern_lint.py`

```python
"""Tests for scripts/pattern_lint.py — project-specific lint rules."""

from __future__ import annotations

import ast

# Import the lint functions directly
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


# ── DK001: str.replace for extension removal ────────────────────────


class TestDK001:
    def test_catches_replace_md(self):
        tree, lines = _parse('x = filename.replace(".md", "")')
        violations = check_dk001(tree, lines, "test.py")
        assert len(violations) == 1
        assert violations[0].rule == "DK001"
        assert "removesuffix" in violations[0].message

    def test_catches_replace_py(self):
        tree, lines = _parse('x = name.replace(".py", "")')
        violations = check_dk001(tree, lines, "test.py")
        assert len(violations) == 1

    def test_catches_replace_yml(self):
        tree, lines = _parse('x = path.replace(".yml", "")')
        violations = check_dk001(tree, lines, "test.py")
        assert len(violations) == 1

    def test_ignores_non_extension_replace(self):
        tree, lines = _parse('x = name.replace("foo", "bar")')
        violations = check_dk001(tree, lines, "test.py")
        assert len(violations) == 0

    def test_ignores_replace_with_non_empty_replacement(self):
        tree, lines = _parse('x = name.replace(".md", ".txt")')
        violations = check_dk001(tree, lines, "test.py")
        assert len(violations) == 0

    def test_noqa_suppresses(self):
        tree, lines = _parse('x = f.replace(".md", "")  # noqa: DK001')
        violations = check_dk001(tree, lines, "test.py")
        assert len(violations) == 0

    def test_ignores_removesuffix(self):
        tree, lines = _parse('x = filename.removesuffix(".md")')
        violations = check_dk001(tree, lines, "test.py")
        assert len(violations) == 0


# ── DK003: 'in' for identifier comparison ───────────────────────────


class TestDK003:
    # [11 tests - same as before, unchanged]
    ...


# ── DK004: bare except Exception with pass/empty body ──────────────


class TestDK004:
    def test_catches_except_exception_pass(self):
        """Bare except Exception: pass should be flagged."""
        tree, lines = _parse("""\
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
        tree, lines = _parse("""\
            try:
                do_something()
            except BaseException:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1
        assert "BaseException" in violations[0].message

    def test_does_not_flag_logged_exception(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except Exception as e:
                logger.error(e)
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_reraised(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except Exception:
                raise
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_noqa_suppresses(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except Exception:  # noqa: DK004
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_specific_exception(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except ValueError:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_explicit_return(self):
        tree, lines = _parse("""\
            def func():
                try:
                    do_something()
                except Exception as e:
                    return None
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_bare_except_without_type(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_catches_except_exception_as_with_pass(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except Exception as e:
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1

    def test_does_not_flag_logging_call(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except Exception as e:
                logging.warning("Error: %s", e)
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_tuple_exception_with_pass(self):
        tree, lines = _parse("""\
            try:
                do_something()
            except (Exception, ValueError):
                pass
            """)
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0


# ── Integration ─────────────────────────────────────────────────────


class TestIntegration:
    def test_multiple_violations_in_one_file(self):
        code = textwrap.dedent("""\
            x = f.replace(".md", "")
            if task_id in event_id: pass
            try:
                risky()
            except Exception:
                pass
        """).strip()
        tree = ast.parse(code)
        lines = code.splitlines()
        v1 = check_dk001(tree, lines, "test.py")
        v3 = check_dk003(tree, lines, "test.py")
        v4 = check_dk004(tree, lines, "test.py")
        assert len(v1) == 1
        assert len(v3) == 1
        assert len(v4) == 1

    def test_clean_code_has_no_violations(self):
        code = textwrap.dedent("""\
            x = filename.removesuffix(".md")
            if task_id == event.task:
                pass
            try:
                risky()
            except Exception as e:
                logger.error(e)
        """).strip()
        tree = ast.parse(code)
        lines = code.splitlines()
        v1 = check_dk001(tree, lines, "test.py")
        v3 = check_dk003(tree, lines, "test.py")
        v4 = check_dk004(tree, lines, "test.py")
        assert len(v1) == 0
        assert len(v3) == 0
        assert len(v4) == 0
```

## What the Bots Found

- **CodeRabbit**: APPROVED with 0 findings — no issues found
- **BugBot**: Still scanning (in progress)

## Valid Values and Boundaries

- **`broad_exceptions` set**: `{"Exception", "BaseException"}` — exact string match against `ast.Name.id`
- **`node.type`**: can be `None` (bare except), `ast.Name` (single type), `ast.Tuple` (multiple types), `ast.Attribute` (module.Type)
- **`_is_swallowed` body**: can be empty list, list of `ast.Pass`, or list of meaningful statements

## Key Questions

1. Does `_is_swallowed` correctly handle an except body that has BOTH a logging call AND a pass statement (e.g., `logger.error(e); pass`)?
2. Should the rule detect `except Exception` where the body is just a comment (AST strips comments, so `except Exception: # intentional\n    pass` still has `[ast.Pass]` as body)?
