#!/usr/bin/env python3
"""Compute content hashes for registry artifacts.

Follows the ADR-0007 content hash specification:
- For Markdown: SHA-256 of everything after closing '---' of YAML frontmatter
- For YAML: SHA-256 of file after removing 'registry:' and '_meta:' blocks
- Normalization: LF line endings, strip trailing whitespace per line,
  single trailing newline, UTF-8
- Format: sha256:<64-char-hex-digest>
"""

import hashlib
import re
import sys
from pathlib import Path


def normalize_content(text: str) -> bytes:
    """Normalize content for hashing per ADR-0007 spec."""
    # Convert to LF line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace from each line
    lines = [line.rstrip() for line in text.split("\n")]
    # Rejoin and ensure single trailing newline
    normalized = "\n".join(lines).rstrip("\n") + "\n"
    return normalized.encode("utf-8")


def extract_markdown_body(text: str) -> str:
    """Extract body after closing '---' of YAML frontmatter."""
    if not text.startswith("---"):
        return text

    # Find the closing '---' (skip the opening one)
    lines = text.split("\n")
    in_frontmatter = False
    closing_index = None

    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            continue
        if in_frontmatter and line.strip() == "---":
            closing_index = i
            break

    if closing_index is None:
        return text

    # Everything after the closing '---', excluding the delimiter itself
    body = "\n".join(lines[closing_index + 1 :])
    return body


def extract_yaml_functional_content(text: str) -> str:
    """Remove registry: and _meta: blocks from YAML content."""
    lines = text.split("\n")
    result = []
    skip_block = False
    skip_indent = 0

    for line in lines:
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)

        if skip_block:
            if stripped == "" or current_indent > skip_indent:
                continue
            else:
                skip_block = False

        if re.match(r"^(registry|_meta)\s*:", stripped):
            skip_block = True
            skip_indent = current_indent
            continue

        result.append(line)

    return "\n".join(result)


def compute_hash(file_path: Path) -> str:
    """Compute content hash for an artifact file."""
    text = file_path.read_text(encoding="utf-8")

    if file_path.suffix == ".md":
        body = extract_markdown_body(text)
    elif file_path.suffix in (".yml", ".yaml"):
        body = extract_yaml_functional_content(text)
    else:
        body = text

    normalized = normalize_content(body)
    digest = hashlib.sha256(normalized).hexdigest()
    return f"sha256:{digest}"


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: compute_content_hash.py <file> [file ...]", file=sys.stderr)
        print("       compute_content_hash.py --all", file=sys.stderr)
        return 1

    if sys.argv[1] == "--all":
        repo_root = Path(__file__).parent.parent.parent
        files = sorted(repo_root.glob(".claude/agents/*.md"))
        files += sorted(repo_root.glob(".claude/skills/*/SKILL.md"))
        files += sorted(repo_root.glob(".kit/skills/*/SKILL.md"))
    else:
        files = [Path(arg) for arg in sys.argv[1:]]

    for file_path in files:
        if not file_path.exists():
            print(f"ERROR: {file_path} not found", file=sys.stderr)
            return 1
        content_hash = compute_hash(file_path)
        print(f"{content_hash}  {file_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
