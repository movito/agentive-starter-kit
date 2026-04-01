"""Tests for compute_content_hash.py."""

import hashlib
import sys
import textwrap
from pathlib import Path

import pytest

# Add scripts/core to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "core"))

from compute_content_hash import (
    compute_hash,
    extract_markdown_body,
    extract_yaml_functional_content,
    normalize_content,
)


class TestNormalizeContent:
    def test_lf_passthrough(self):
        result = normalize_content("hello\nworld\n")
        assert result == b"hello\nworld\n"

    def test_crlf_to_lf(self):
        result = normalize_content("hello\r\nworld\r\n")
        assert result == b"hello\nworld\n"

    def test_cr_to_lf(self):
        result = normalize_content("hello\rworld\r")
        assert result == b"hello\nworld\n"

    def test_strip_trailing_whitespace(self):
        result = normalize_content("hello   \nworld\t\n")
        assert result == b"hello\nworld\n"

    def test_single_trailing_newline(self):
        result = normalize_content("hello\n\n\n")
        assert result == b"hello\n"

    def test_adds_trailing_newline(self):
        result = normalize_content("hello")
        assert result == b"hello\n"

    def test_utf8_encoding(self):
        result = normalize_content("héllo\n")
        assert result == "héllo\n".encode("utf-8")

    def test_empty_string(self):
        result = normalize_content("")
        assert result == b"\n"


class TestExtractMarkdownBody:
    def test_basic_frontmatter(self):
        text = textwrap.dedent("""\
            ---
            name: test
            version: 1.0.0
            ---

            # Body content
            Some text here.
        """)
        body = extract_markdown_body(text)
        assert body.startswith("\n# Body content")
        assert "name: test" not in body

    def test_no_frontmatter(self):
        text = "# Just a heading\nSome text."
        body = extract_markdown_body(text)
        assert body == text

    def test_frontmatter_with_registry_block(self):
        text = textwrap.dedent("""\
            ---
            name: test
            registry:
              type: agent
              version: 1.0.0
            ---

            # Body
        """)
        body = extract_markdown_body(text)
        assert body.startswith("\n# Body")
        assert "registry:" not in body

    def test_unclosed_frontmatter(self):
        text = "---\nname: test\nno closing delimiter"
        body = extract_markdown_body(text)
        assert body == text

    def test_body_with_triple_dashes(self):
        """Triple dashes in the body should not be confused with frontmatter."""
        text = textwrap.dedent("""\
            ---
            name: test
            ---

            # Body

            ---

            More content after hr.
        """)
        body = extract_markdown_body(text)
        assert "---" in body
        assert "More content after hr." in body


class TestExtractYamlFunctionalContent:
    def test_removes_registry_block(self):
        text = textwrap.dedent("""\
            name: evaluator
            registry:
              type: evaluator
              version: 1.0.0
            prompt: |
              Do something
        """)
        result = extract_yaml_functional_content(text)
        assert "registry:" not in result
        assert "name: evaluator" in result
        assert "prompt: |" in result

    def test_removes_meta_block(self):
        text = textwrap.dedent("""\
            name: evaluator
            _meta:
              source: test
              installed: 2026-01-01
            prompt: |
              Do something
        """)
        result = extract_yaml_functional_content(text)
        assert "_meta:" not in result
        assert "name: evaluator" in result

    def test_preserves_non_registry_content(self):
        text = textwrap.dedent("""\
            name: test
            model_requirement:
              family: claude
            prompt: hello
        """)
        result = extract_yaml_functional_content(text)
        assert result == text


class TestComputeHash:
    def test_markdown_file(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\nname: test\n---\n\n# Hello\n", encoding="utf-8")
        result = compute_hash(md)
        assert result.startswith("sha256:")
        assert len(result) == len("sha256:") + 64

    def test_yaml_file(self, tmp_path):
        yml = tmp_path / "test.yml"
        yml.write_text("name: test\nprompt: hello\n", encoding="utf-8")
        result = compute_hash(yml)
        assert result.startswith("sha256:")

    def test_hash_deterministic(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text("---\nname: test\n---\n\n# Hello\n", encoding="utf-8")
        h1 = compute_hash(md)
        h2 = compute_hash(md)
        assert h1 == h2

    def test_frontmatter_change_no_body_change(self, tmp_path):
        """Changing only frontmatter should not change the hash."""
        md1 = tmp_path / "v1.md"
        md1.write_text("---\nname: test\n---\n\n# Hello\n", encoding="utf-8")

        md2 = tmp_path / "v2.md"
        md2.write_text(
            "---\nname: test\nregistry:\n  version: 1.0.0\n---\n\n# Hello\n",
            encoding="utf-8",
        )

        assert compute_hash(md1) == compute_hash(md2)

    def test_body_change_changes_hash(self, tmp_path):
        md1 = tmp_path / "v1.md"
        md1.write_text("---\nname: test\n---\n\n# Hello\n", encoding="utf-8")

        md2 = tmp_path / "v2.md"
        md2.write_text("---\nname: test\n---\n\n# Goodbye\n", encoding="utf-8")

        assert compute_hash(md1) != compute_hash(md2)

    def test_whitespace_normalization(self, tmp_path):
        """Files differing only in trailing whitespace should have same hash."""
        md1 = tmp_path / "v1.md"
        md1.write_text("---\nname: test\n---\n\n# Hello\n", encoding="utf-8")

        md2 = tmp_path / "v2.md"
        md2.write_text("---\nname: test\n---\n\n# Hello   \n\n\n", encoding="utf-8")

        assert compute_hash(md1) == compute_hash(md2)

    def test_crlf_lf_same_hash(self, tmp_path):
        """CRLF and LF versions should produce the same hash."""
        md1 = tmp_path / "lf.md"
        md1.write_bytes(b"---\nname: test\n---\n\n# Hello\n")

        md2 = tmp_path / "crlf.md"
        md2.write_bytes(b"---\r\nname: test\r\n---\r\n\r\n# Hello\r\n")

        assert compute_hash(md1) == compute_hash(md2)
