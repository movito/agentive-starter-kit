#!/usr/bin/env python3
"""doctor check: .env exists; required keys present AND uncommented.

Incident (KIT-0032): the evaluator trio ran 2-of-3 because
ANTHROPIC_API_KEY sat commented out in .env — nothing surfaced it
until a mid-review "missing key" failure.

Never prints key values — presence and comment-state only (read-only,
N3). Root comes from DOCTOR_ROOT (set by the driver; tests point it at
tmp fixtures), falling back to the repo root relative to this file.
"""

import os
import sys
from pathlib import Path

# FAIL-level: the trio cannot run at all without it.
REQUIRED_KEYS = ["ANTHROPIC_API_KEY"]
# WARN-level: o3 / Gemini evaluators silently drop out without these.
RECOMMENDED_KEYS = ["OPENAI_API_KEY", "GEMINI_API_KEY"]


def key_state(lines, key):
    """Return 'present', 'commented', or 'missing' for key. Values unread.

    Scans the WHOLE file: an uncommented assignment anywhere wins over a
    commented one (the copy-template-then-append layout keeps the
    commented template line — o3 review caught the first-match-wins
    false FAIL). Accepts an optional `export ` prefix. Strict `KEY=value`
    format otherwise — spaces around `=` are deliberately not recognized
    (standard .env parsers do not accept them either).
    """
    state = "missing"
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].lstrip()
        if stripped.startswith(f"{key}="):
            _, _, value = stripped.partition("=")
            # normalize before judging: an unquoted trailing `# comment`
            # is not a value, and quoted-empty ("" / '') is empty —
            # KEY="" or KEY= # placeholder must not PASS an unusable env
            value = value.split("#", 1)[0].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1].strip()
            if value:
                return "present"
            state = "commented"
            continue
        if stripped.startswith("#") and stripped.lstrip("# ").startswith(f"{key}="):
            state = "commented"
    return state


def main():
    root = Path(os.environ.get("DOCTOR_ROOT") or Path(__file__).resolve().parents[3])
    env_file = root / ".env"

    if not env_file.exists():
        print(
            "DOCTOR:env-keys:FAIL:.env not found — copy .env.template and fill in keys"
        )
        return 0

    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"DOCTOR:env-keys:FAIL:.env unreadable ({exc.__class__.__name__})")
        return 0

    problems = []
    for key in REQUIRED_KEYS:
        state = key_state(lines, key)
        if state == "commented":
            problems.append(f"{key} commented out or empty")
        elif state == "missing":
            problems.append(f"{key} missing")
    if problems:
        print(f"DOCTOR:env-keys:FAIL:{'; '.join(problems)} in .env")
        return 0

    warnings = []
    for key in RECOMMENDED_KEYS:
        if key_state(lines, key) != "present":
            warnings.append(key)
    if warnings:
        print(
            "DOCTOR:env-keys:WARN:evaluator keys not set: "
            + ", ".join(warnings)
            + " — those evaluators will drop out of the trio"
        )
        return 0

    print("DOCTOR:env-keys:PASS:required and evaluator keys present and uncommented")
    return 0


if __name__ == "__main__":
    sys.exit(main())
