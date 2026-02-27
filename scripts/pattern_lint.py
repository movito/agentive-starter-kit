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

    Returns True only when the body is empty or contains nothing but ``pass``.
    Any other statement (raise, return, logging, assignment, etc.) means
    the exception is being handled in some way.
    """
    if not body:
        return True
    return all(isinstance(stmt, ast.Pass) for stmt in body)


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
