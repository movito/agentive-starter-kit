"""KIT-LOCAL marker-region reading for the package (KIT-0091).

A minimal, read-only port of the region grammar from
``scripts/local/kit_markers.py`` — the repo-resident tool stays the
one WRITER (merge/replace); the package only ever needs to READ a
region (preflight's ``bots:`` declaration). The pattern below is
byte-for-byte the reader half of that tool's ``_region_pattern``, and
``tests/agentive_kit/test_markers.py`` pins the two against each other
so they cannot drift apart silently.

Grammar notes carried over verbatim: markers are matched as whole
lines, tolerating benign whitespace drift inside the comment
(``[ \\t]`` only — never ``\\s``, so tolerance can't cross a line
break), and ``\\r?\\n`` keeps CRLF files parsing.
"""

from __future__ import annotations

import re


def _region_pattern(name: str) -> re.Pattern[str]:
    esc = re.escape(name)
    return re.compile(
        r"(?P<begin>^[ \t]*<!--[ \t]*BEGIN[ \t]+KIT-LOCAL:[ \t]*"
        + esc
        + r"[ \t]*-->[ \t]*\r?\n)"
        r"(?P<body>.*?)"
        r"(?P<end>\r?\n[ \t]*<!--[ \t]*END[ \t]+KIT-LOCAL:[ \t]*" + esc + r"[ \t]*-->)",
        re.DOTALL | re.MULTILINE,
    )


def extract_region(text: str, name: str) -> str | None:
    """Return the inner content of region *name*, or ``None`` if absent."""
    match = _region_pattern(name).search(text)
    if match is None:
        return None
    return match.group("body")
