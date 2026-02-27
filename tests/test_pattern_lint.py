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
    def test_catches_id_in_id(self):
        """Both sides look like identifiers — likely string containment."""
        tree, lines = _parse("if task_id in event.task_id: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 1
        assert violations[0].rule == "DK003"
        assert "Use ==" in violations[0].message

    def test_catches_name_in_name(self):
        tree, lines = _parse("if agent_name in session_name: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 1

    def test_catches_type_in_type(self):
        tree, lines = _parse("if event_type in other_type: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 1

    def test_ignores_id_in_collection(self):
        """Container membership is fine — not string containment."""
        tree, lines = _parse("if task_id in event.task: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0

    def test_ignores_id_in_set_literal(self):
        tree, lines = _parse("if event_type in {'a', 'b'}: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0

    def test_ignores_name_in_list_variable(self):
        tree, lines = _parse("if agent_name in allowed_names: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0

    def test_ignores_non_identifier_in(self):
        tree, lines = _parse("if 'x' in some_list: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0

    def test_ignores_plain_variable_in_list(self):
        tree, lines = _parse("if item in collection: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0

    def test_substring_comment_suppresses(self):
        tree, lines = _parse(
            "if task_id in text:  # substring: search in body\n    pass"
        )
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0

    def test_noqa_suppresses(self):
        tree, lines = _parse("if task_id in text:  # noqa: DK003\n    pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0

    def test_equality_not_flagged(self):
        tree, lines = _parse("if task_id == event.task: pass")
        violations = check_dk003(tree, lines, "test.py")
        assert len(violations) == 0


# ── DK004: bare except Exception with pass/empty body ──────────────


class TestDK004:
    def test_catches_except_exception_pass(self):
        """Bare except Exception: pass should be flagged."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except Exception:
                pass
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1
        assert violations[0].rule == "DK004"
        assert "silently swallows" in violations[0].message

    def test_catches_except_base_exception_pass(self):
        """Bare except BaseException: pass should be flagged."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except BaseException:
                pass
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1
        assert "BaseException" in violations[0].message

    def test_does_not_flag_logged_exception(self):
        """except Exception as e: logger.error(e) is not bare."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except Exception as e:
                logger.error(e)
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_reraised(self):
        """except Exception: raise is not bare."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except Exception:
                raise
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_noqa_suppresses(self):
        """# noqa: DK004 suppresses the violation."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except Exception:  # noqa: DK004
                pass
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_specific_exception(self):
        """except ValueError: pass is OK — only broad exceptions flagged."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except ValueError:
                pass
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_explicit_return(self):
        """except Exception as e: return None is not bare."""
        tree, lines = _parse(
            """\
            def func():
                try:
                    do_something()
                except Exception as e:
                    return None
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_bare_except_without_type(self):
        """Bare 'except:' (no type) is not in scope — only Exception/BaseException."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except:
                pass
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_catches_except_exception_as_with_pass(self):
        """except Exception as e: pass should be flagged (name bound but unused)."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except Exception as e:
                pass
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 1

    def test_does_not_flag_logging_call(self):
        """except Exception as e: logging.warning(...) is not bare."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except Exception as e:
                logging.warning("Error: %s", e)
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0

    def test_does_not_flag_tuple_exception_with_pass(self):
        """except (Exception, ValueError): pass uses tuple — not a Name node."""
        tree, lines = _parse(
            """\
            try:
                do_something()
            except (Exception, ValueError):
                pass
            """
        )
        violations = check_dk004(tree, lines, "test.py")
        assert len(violations) == 0


# ── Integration ─────────────────────────────────────────────────────


class TestIntegration:
    def test_multiple_violations_in_one_file(self):
        code = textwrap.dedent(
            """\
            x = f.replace(".md", "")
            if task_id in event_id: pass
            try:
                risky()
            except Exception:
                pass
        """
        ).strip()
        tree = ast.parse(code)
        lines = code.splitlines()
        v1 = check_dk001(tree, lines, "test.py")
        v3 = check_dk003(tree, lines, "test.py")
        v4 = check_dk004(tree, lines, "test.py")
        assert len(v1) == 1
        assert len(v3) == 1
        assert len(v4) == 1

    def test_clean_code_has_no_violations(self):
        code = textwrap.dedent(
            """\
            x = filename.removesuffix(".md")
            if task_id == event.task:
                pass
            try:
                risky()
            except Exception as e:
                logger.error(e)
        """
        ).strip()
        tree = ast.parse(code)
        lines = code.splitlines()
        v1 = check_dk001(tree, lines, "test.py")
        v3 = check_dk003(tree, lines, "test.py")
        v4 = check_dk004(tree, lines, "test.py")
        assert len(v1) == 0
        assert len(v3) == 0
        assert len(v4) == 0
