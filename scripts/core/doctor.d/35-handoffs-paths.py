#!/usr/bin/env python3
# shapes: single planning
"""doctor check: agent-handoffs.json task paths point at real files.

KIT-0086 F2: feature-branch lifecycle moves no longer rewrite the
shared coordination JSON (single-writer guard — the planner owns it on
main), so its ``.kit/tasks/<folder>/<file>`` path strings can go stale
between a branch-side move and the planner's next edit. Drift must be
LOUD without reintroducing a second writer: this check WARNs when a
recorded path does not exist while the same file name exists in a
different status folder (a stale pointer), and stays quiet on paths
that are simply gone (archived/deleted tasks are the planner's
bookkeeping, not drift).

Read-only (N3). Root comes from DOCTOR_ROOT (set by the driver).
"""

import json
import os
import re
import sys
from pathlib import Path

NAME = "35-handoffs-paths.py"

root = Path(os.environ.get("DOCTOR_ROOT") or Path(__file__).resolve().parents[3])
handoffs = root / ".kit" / "context" / "agent-handoffs.json"
tasks_dir = root / ".kit" / "tasks"

if not handoffs.is_file() or not tasks_dir.is_dir():
    print(f"DOCTOR:{NAME}:SKIP:no agent-handoffs.json or .kit/tasks in this repo")
    sys.exit(0)

try:
    text = handoffs.read_text(encoding="utf-8")
    json.loads(text)  # structural sanity only; paths are scanned as strings
except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
    print(
        f"DOCTOR:{NAME}:WARN:agent-handoffs.json unreadable or not JSON "
        f"({exc.__class__.__name__}) — fix it on main (planner owns this file)"
    )
    sys.exit(0)

# Scan raw path strings — the same shape lifecycle rewrites; scanning
# text (not the JSON tree) also catches paths in nested/unknown keys.
recorded = set(re.findall(r"\.kit/tasks/[0-9]+-[a-z-]+/[A-Za-z0-9._-]+\.md", text))

stale = []
for rel in sorted(recorded):
    if (root / rel).is_file():
        continue
    file_name = rel.rsplit("/", 1)[1]
    actual = [
        f".kit/tasks/{p.parent.name}/{p.name}"
        for p in tasks_dir.glob(f"*/{file_name}")
        if p.is_file()
    ]
    if actual:
        stale.append(f"{rel} -> {actual[0]}")

if stale:
    detail = "; ".join(stale)
    print(
        f"DOCTOR:{NAME}:WARN:stale task path(s) in agent-handoffs.json "
        f"({detail}) — planner repairs on main; branch sessions must not "
        "edit this file (KIT-0086)"
    )
else:
    print(
        f"DOCTOR:{NAME}:PASS:all {len(recorded)} recorded task path(s) "
        "resolve to their folders"
    )
