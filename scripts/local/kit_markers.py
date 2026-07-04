#!/usr/bin/env python3
"""kit_markers — overwrite/preserve KIT-LOCAL marker regions in agent files.

The canonical agents (`planner.md`, `feature-developer.md`) wrap their
consumer-customizable sections (Project Context, Stack Notes) in stable
markers:

    <!-- BEGIN KIT-LOCAL: project-context -->
    ...consumer-owned content...
    <!-- END KIT-LOCAL: project-context -->

`bootstrap-consumer.sh` uses this helper so that:

- **Fresh bootstrap** — the upstream agent is copied, then each marker
  region is replaced with consumer-derived placeholder content (so a
  consumer never inherits the kit's own Project Context / Stack Notes).
- **Re-bootstrap** — the upstream agent is copied to pick up structural
  improvements *outside* the markers, while the consumer's existing
  content *inside* every marker region is preserved verbatim
  (byte-for-byte).

Stdlib only — consumers run this with the bare `python3` the `project`
script already requires; no venv needed.

CLI:
    kit_markers.py merge --upstream U --out O [--consumer C] [--project-name N]
    kit_markers.py extract <file> <region>
    kit_markers.py replace <file> <region> (--content-file F | --stdin)
    kit_markers.py regions <file>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Markers are matched as whole lines, tolerating benign whitespace drift
# inside the comment ([ \t] only — never \s, so tolerance can't cross a
# line break). A consumer whose marker gained an extra space must still
# parse: treating its region as absent would silently replace customized
# content with placeholders on re-bootstrap.
BEGIN_RE = re.compile(
    r"^[ \t]*<!--[ \t]*BEGIN[ \t]+KIT-LOCAL:[ \t]*(?P<name>\S+?)[ \t]*-->[ \t]*\r?$",
    re.MULTILINE,
)


def _region_pattern(name: str) -> re.Pattern[str]:
    """Compile a DOTALL pattern capturing the inner content of one region.

    Group 'body' is everything between the newline after BEGIN and the
    newline before END — never the marker lines themselves — so an
    extract/replace round-trip is byte-identical. Drifted marker lines are
    captured and re-emitted verbatim, never normalized.
    """
    esc = re.escape(name)
    # \r?\n so files with CRLF line endings (Windows / git autocrlf) parse
    # too. The newline is captured inside begin/end and re-emitted verbatim,
    # and the body group is preserved byte-for-byte regardless of ending.
    return re.compile(
        r"(?P<begin>^[ \t]*<!--[ \t]*BEGIN[ \t]+KIT-LOCAL:[ \t]*"
        + esc
        + r"[ \t]*-->[ \t]*\r?\n)"
        r"(?P<body>.*?)"
        r"(?P<end>\r?\n[ \t]*<!--[ \t]*END[ \t]+KIT-LOCAL:[ \t]*" + esc + r"[ \t]*-->)",
        re.DOTALL | re.MULTILINE,
    )


def _begin_marker_line_re(name: str) -> re.Pattern[str]:
    """Loose, line-anchored detector for a BEGIN marker of region *name*.

    Deliberately looser than the parse patterns (case-insensitive, colon
    optional, no closing --> required) so a marker damaged beyond what
    parsing tolerates is still *detected* and merge fails fast instead of
    silently clobbering the region's content with a placeholder. Line-
    anchored so a prose sentence mentioning a marker never matches.
    """
    esc = re.escape(name)
    return re.compile(
        r"^[ \t]*<!--[ \t]*BEGIN[ \t]+KIT-LOCAL\b[ \t]*:?[ \t]*" + esc + r"\b",
        re.MULTILINE | re.IGNORECASE,
    )


def find_regions(text: str) -> list[str]:
    """Return the unique region names in *text*, in first-seen order.

    Region names are expected to be unique within a file; duplicates are
    de-duplicated here so callers iterate each name once (replace_region
    rewrites every occurrence of a name regardless).
    """
    seen: list[str] = []
    for name in BEGIN_RE.findall(text):
        if name not in seen:
            seen.append(name)
    return seen


def extract_region(text: str, name: str) -> str | None:
    """Return the inner content of region *name*, or None if absent."""
    match = _region_pattern(name).search(text)
    if match is None:
        return None
    return match.group("body")


def replace_region(text: str, name: str, new_content: str) -> str:
    """Return *text* with region *name*'s inner content replaced.

    The marker lines are preserved. Every occurrence of the named region
    is rewritten (a well-formed agent has exactly one, but duplicates must
    not be silently skipped). Raises KeyError if the region is absent so
    callers fail loudly rather than silently no-op.
    """
    pattern = _region_pattern(name)
    if pattern.search(text) is None:
        raise KeyError(f"region not found: {name}")

    def _sub(match: re.Match[str]) -> str:
        return match.group("begin") + new_content + match.group("end")

    return pattern.sub(_sub, text)


def merge(
    upstream: str,
    consumer: str | None = None,
    placeholders: dict[str, str] | None = None,
) -> str:
    """Merge marker regions into the *upstream* agent text.

    For each region defined upstream:
    - if *consumer* contains the same region, keep the consumer's content
      (re-bootstrap preservation);
    - else if a *placeholder* is supplied for it, use that (fresh
      bootstrap);
    - else leave the upstream content untouched.
    """
    placeholders = placeholders or {}
    result = upstream
    for name in find_regions(upstream):
        if consumer is not None:
            preserved = extract_region(consumer, name)
            if preserved is None and _begin_marker_line_re(name).search(consumer):
                # A line looks like this region's BEGIN marker but the
                # region is not parseable (END edited away, marker damaged
                # beyond whitespace tolerance). Fail fast rather than
                # silently clobber the consumer's trapped content with a
                # placeholder on re-bootstrap. Line-anchored, so a prose
                # mention of a marker inside another region never trips it.
                raise ValueError(
                    f"malformed KIT-LOCAL region in consumer file: {name} "
                    "(BEGIN marker line present but region not parseable — "
                    "missing/mismatched END marker or damaged BEGIN marker?)"
                )
            if preserved is not None:
                result = replace_region(result, name, preserved)
                continue
        if name in placeholders:
            result = replace_region(result, name, placeholders[name])
    return result


def default_placeholders(project_name: str) -> dict[str, str]:
    """Generate safe, consumer-neutral placeholder content per region.

    Derives a human title from the project directory name; the rest is
    explicit TODOs the consumer fills in. Contains no kit identity.
    """
    title = project_name.replace("-", " ").replace("_", " ").title().strip()
    if not title:
        title = "Your Project"
    project_context = (
        f"This is the **{title}** project.\n"
        "\n"
        "- **Tech Stack**: TODO — languages, frameworks, runtimes\n"
        "- **Layout**: TODO — repo / workspace structure\n"
        "- **Task Prefix**: TODO — e.g. PROJ-NNNN\n"
        "- **Language**: TODO — content + code/comment language\n"
        "- **Topology**: single-repo\n"
        "\n"
        "**Rules:**\n"
        "\n"
        "- TODO — fill in the project-specific rules this agent must follow"
    )
    stack_notes = (
        "- **Test/lint loop**: TODO — local test, lint, and format commands\n"
        "- **Build/run**: TODO — how to build and run the project locally\n"
        "- **Pre-commit**: TODO — describe the pre-commit hooks, if any\n"
        "- **Gotchas**: TODO — what an implementer coming in cold gets wrong\n"
        "- **Task lifecycle**: `./scripts/core/project start|move|complete <ID>`"
    )
    return {"project-context": project_context, "stack-notes": stack_notes}


# ─────────────────────────────────────────
# CLI
# ─────────────────────────────────────────
def _cmd_merge(args: argparse.Namespace) -> int:
    upstream = Path(args.upstream).read_text(encoding="utf-8")

    consumer = None
    if args.consumer is not None and Path(args.consumer).is_file():
        consumer = Path(args.consumer).read_text(encoding="utf-8")

    placeholders = None
    if args.project_name is not None:
        placeholders = default_placeholders(args.project_name)

    merged = merge(upstream, consumer=consumer, placeholders=placeholders)
    Path(args.out).write_text(merged, encoding="utf-8")
    return 0


def _cmd_extract(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    body = extract_region(text, args.region)
    if body is None:
        print(f"region not found: {args.region}", file=sys.stderr)
        return 1
    sys.stdout.write(body)
    return 0


def _cmd_replace(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    if args.stdin:
        new_content = sys.stdin.read()
    else:
        new_content = Path(args.content_file).read_text(encoding="utf-8")
    try:
        updated = replace_region(text, args.region, new_content)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    Path(args.file).write_text(updated, encoding="utf-8")
    return 0


def _cmd_regions(args: argparse.Namespace) -> int:
    text = Path(args.file).read_text(encoding="utf-8")
    for name in find_regions(text):
        print(name)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_merge = sub.add_parser("merge", help="merge marker regions into an agent")
    p_merge.add_argument("--upstream", required=True)
    p_merge.add_argument("--out", required=True)
    p_merge.add_argument("--consumer", default=None)
    p_merge.add_argument("--project-name", default=None)
    p_merge.set_defaults(func=_cmd_merge)

    p_extract = sub.add_parser("extract", help="print a region's inner content")
    p_extract.add_argument("file")
    p_extract.add_argument("region")
    p_extract.set_defaults(func=_cmd_extract)

    p_replace = sub.add_parser("replace", help="replace a region's inner content")
    p_replace.add_argument("file")
    p_replace.add_argument("region")
    group = p_replace.add_mutually_exclusive_group(required=True)
    group.add_argument("--content-file")
    group.add_argument("--stdin", action="store_true")
    p_replace.set_defaults(func=_cmd_replace)

    p_regions = sub.add_parser("regions", help="list region names in a file")
    p_regions.add_argument("file")
    p_regions.set_defaults(func=_cmd_regions)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
