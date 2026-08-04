#!/usr/bin/env python3
# shapes: single planning
"""doctor check: .env exists; required keys present AND uncommented.

Incident (KIT-0032): the evaluator trio ran 2-of-3 because
ANTHROPIC_API_KEY sat commented out in .env — nothing surfaced it
until a mid-review "missing key" failure.

Not-checkable note (per the incident-closure lifecycle rule; not
worktree-specific despite riding KIT-0071's doctor work): a VALID key
is not necessarily a USABLE key. KIT-0069's claude-code evaluator
failed at runtime with a valid ANTHROPIC_API_KEY because the account's
credit balance was zero — and balance has no cheap API, so this check
stops at presence by design. The symptom to recognize: valid key,
evaluator writes no log file → check the Anthropic console credit
balance (same shape as the CodeRabbit quota note in
80-bot-presence.sh).

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
# WARN-level (KIT-0084): TASK_PREFIX left unset or at the old template
# placeholder is silently-wrong project identity — the door writes it
# empty on planning-shape --new precisely so this check surfaces it.
PREFIX_PLACEHOLDER = "TASK"


def _effective_value(raw):
    """Normalize an assignment's right-hand side: a QUOTED value keeps
    everything inside the quotes (a '#' inside quotes is data — the
    old split-then-unquote order corrupted such values, fast-v2
    evaluator KIT-0084); an unquoted trailing `# comment` is not a
    value, and quoted-empty ("" / '') is empty — KEY="" or
    KEY= # placeholder must not PASS an unusable env.
    """
    value = raw.strip()
    if value and value[0] in "\"'":
        closing = value.find(value[0], 1)
        if closing != -1:
            return value[1:closing].strip()
    return value.split("#", 1)[0].strip()


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
            if _effective_value(value):
                return "present"
            state = "commented"
            continue
        if stripped.startswith("#") and stripped.lstrip("# ").startswith(f"{key}="):
            state = "commented"
    return state


def key_value(lines, key):
    """Effective value of key for identity checks: the LAST uncommented
    assignment wins, matching dotenv semantics (CodeRabbit, KIT-0084 —
    key_state's first-non-empty scan serves key PRESENCE, where the
    copy-template-then-append layout matters; a VALUE check must report
    what a parser would actually load). Comments and quotes stripped,
    `export ` accepted. Returns None when no uncommented assignment
    exists at all. Only ever called for non-secret identity keys —
    key_state stays the reader for key material.
    """
    for line in reversed(lines):
        stripped = line.strip()
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].lstrip()
        if stripped.startswith(f"{key}="):
            _, _, value = stripped.partition("=")
            return _effective_value(value)
    return None


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

    warn_parts = []
    warnings = []
    for key in RECOMMENDED_KEYS:
        if key_state(lines, key) != "present":
            warnings.append(key)
    if warnings:
        warn_parts.append(
            "evaluator keys not set: "
            + ", ".join(warnings)
            + " — those evaluators will drop out of the trio"
        )
    prefix = key_value(lines, "TASK_PREFIX")
    if prefix is None or prefix == "" or prefix == PREFIX_PLACEHOLDER:
        warn_parts.append(
            "TASK_PREFIX not set (empty, missing, or the 'TASK' placeholder)"
            " — set your project's task prefix in .env (decided at intake"
            " Step 4a / project onboarding)"
        )
    if warn_parts:
        print("DOCTOR:env-keys:WARN:" + "; ".join(warn_parts))
        return 0

    print(
        "DOCTOR:env-keys:PASS:required and evaluator keys present and "
        "uncommented (presence only — credit balance is not checkable: "
        "a valid key whose evaluator writes no log usually means zero "
        "balance, KIT-0069)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
