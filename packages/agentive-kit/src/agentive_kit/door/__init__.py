"""The setup door as package subcommands — ``agentive new`` / ``agentive adopt``.

KIT-0104 (KIT-ADR-0030): the door stops being a place you must stand
and becomes a tool you have installed. This module is a PORT of
``scripts/local/bootstrap``'s front — argument parsing, the
shape × profile matrix (single owner: THIS module), the preset
resolution chain, and orchestration — while the two engines it drives
(``engine-scaffold.sh``, ``engine-consumer.sh``) ship as packaged data
scripts under ``door/engines/`` and stay pure executors. The
engine-consolidation follow-up (filed with this task's PR 2) is the
interim's exit.

Shape × profile legality (single owner: THIS module — doctor and every
other reader consult the recorded pair, never re-derive the matrix)::

    |          | python      | none         |
    |----------|-------------|--------------|
    | single   | ✔ (default) | ✔ (docs-only)|
    | planning | ✘           | ✔ (forced)   |

Deliberate differences from the kit-side ``bootstrap`` (each the
packaged-world consequence of KIT-ADR-0028/0030/0032, said out loud
here and in the KIT-0104 PR body):

- **Adopt is packaged-mode**: content scaffold + kit-install record +
  check hook. Nothing is copied from a kit tree — agents come from the
  ``agentive-workflow`` plugin and lifecycle scripts from this package
  (the legacy copy-adopt retires with the bootstrap shim).
- **``--design-materials`` is refused with a pointer**: the materials
  flow rsyncs a kit working tree and execs an interactive agent — it
  cannot ship as package data. Its successor is the ``project-intake``
  agent (KIT-ADR-0031 / KIT-0105).
- **The operator preset home anchors to the TARGET's parent**
  (``<target-parent>/agentive-config``), not the kit clone's parent —
  there is no kit clone to anchor to. ``AGENTIVE_KIT_CONFIG_DIR``
  remains the one explicit override (operator decision, 2026-08-13).
- **No kit-clone ``.env`` carry-over offer**: keys reach a new project
  via the preset's ``env-source`` (the packaged channel) or by operator
  hand — there is no kit checkout to copy from.
- **``--no-kit`` adopt is rung 0** (KIT-ADR-0032): check hook + git
  init only. No ``.kit/``, no CLAUDE.md, no kit-install record — a
  plain repo, reported as success, never as a deficiency.

Engine data staging: the engines resolve their source tree from their
own location (``SCRIPT_DIR/../..``), so the door stages a faux kit
root in a temp dir — engines + data files arranged in the kit-tree
layout — and runs them from there unmodified. The data store under
``door/data/`` uses dot-free names (git and packaging tools treat
hidden files unevenly); ``_STAGE_MAP`` is the store → kit-layout
mapping, and ``sync_pairs()`` feeds the guard test that pins every
store file byte-identical to its kit-tree source until the
engine-consolidation follow-up dissolves the duplication.

Exit contract (the door's F6, unchanged):
  0  install succeeded — the doctor verdict is REPORTED, never encoded
  1  install failed (an engine or record step errored)
  2  usage error or illegal shape/profile combination
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import agentive_kit
from agentive_kit import markers

_DOOR_DIR = Path(__file__).resolve().parent
_ENGINES_DIR = _DOOR_DIR / "engines"
_DATA_DIR = _DOOR_DIR / "data"

# ─────────────────────────────────────────
# The matrix — door-owned data (F2)
# ─────────────────────────────────────────
LEGAL_PAIRS = frozenset(
    (("single", "python"), ("single", "none"), ("planning", "none"))
)


def legal_pairs_human() -> str:
    return "single+python (default), single+none, planning+none (forced)"


PRESET_KEYS = (
    "shape",
    "profile",
    "bots",
    "evaluators",
    "venv",
    "target-path",
    "target-github",
    "env-source",
)

# Store path (relative to door/data/) → staged kit-root-relative path.
# Directories stage recursively; files stage one-to-one.
_STAGE_MAP = {
    "kit-templates": ".kit/templates",
    "workflows": ".kit/context/workflows",
    "docs": "docs",
    "adversarial": ".adversarial",
    "checks": "scripts/local/templates",
    "env.template": ".env.template",
    "gitignore": ".gitignore",
    "coderabbitignore": ".coderabbitignore",
}

# Engine files → staged kit-root-relative path (the engines resolve
# PROJECT_ROOT/KIT_ROOT as SCRIPT_DIR/../.., so they must sit at
# scripts/local/ inside the staged root).
_ENGINE_MAP = {
    "engine-scaffold.sh": "scripts/local/engine-scaffold.sh",
    "engine-consumer.sh": "scripts/local/engine-consumer.sh",
    "kit_markers.py": "scripts/local/kit_markers.py",
}

# Kit-tree source of every packaged copy (repo-relative → package path
# relative to door/). tests/test_door_data_sync.py walks this to pin
# store and source byte-identical — edits to either side must land in
# both until the engine-consolidation follow-up dissolves the copies.
_SYNC_SOURCES = {
    "engines/engine-scaffold.sh": "scripts/local/engine-scaffold.sh",
    "engines/engine-consumer.sh": "scripts/local/engine-consumer.sh",
    "engines/kit_markers.py": "scripts/local/kit_markers.py",
    # kit-templates maps per FILE, not per directory: .kit/templates/
    # also holds builder-only templates (AGENT-TEMPLATE,
    # OPERATIONAL-RULES) the scaffold engine deliberately never ships —
    # a directory mapping would pull them into every consumer wheel
    # (caught by the sync guard's reverse direction, first run).
    "data/kit-templates/TASK-STARTER-TEMPLATE.md": (
        ".kit/templates/TASK-STARTER-TEMPLATE.md"
    ),
    "data/kit-templates/PROTOTYPE-HANDOFF-TEMPLATE.md": (
        ".kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md"
    ),
    "data/workflows": ".kit/context/workflows",
    "data/docs/CROSS-REPO-PATTERN.md": "docs/CROSS-REPO-PATTERN.md",
    "data/adversarial/config.yml": ".adversarial/config.yml",
    "data/adversarial/templates": ".adversarial/templates",
    "data/checks/checks-python.sh": "scripts/local/templates/checks-python.sh",
    "data/checks/checks-none.sh": "scripts/local/templates/checks-none.sh",
    "data/env.template": ".env.template",
    "data/gitignore": ".gitignore",
    "data/coderabbitignore": ".coderabbitignore",
}


def sync_pairs() -> list[tuple[str, Path]]:
    """(repo-relative source, packaged copy path) file pairs.

    Directory entries in ``_SYNC_SOURCES`` expand to every file in the
    PACKAGED copy; the guard test additionally asserts the source dirs
    carry no extra files, so additions can't slip past the pin either.
    """
    pairs: list[tuple[str, Path]] = []
    for pkg_rel, repo_rel in _SYNC_SOURCES.items():
        pkg_path = _DOOR_DIR / pkg_rel
        if pkg_path.is_dir():
            for child in sorted(pkg_path.rglob("*")):
                if child.is_file():
                    rel = child.relative_to(pkg_path)
                    pairs.append((f"{repo_rel}/{rel}", child))
        else:
            pairs.append((repo_rel, pkg_path))
    return pairs


# ─────────────────────────────────────────
# Errors and small helpers
# ─────────────────────────────────────────
class DoorExit(SystemExit):
    """SystemExit carrying the door's exit contract (0/1/2).

    Deliberately used for SUCCESS as well as failure (``DoorExit(0)``
    at the end of orchestration) — the port keeps the bash door's
    exit-is-the-interface shape, so ``door.main()`` never returns and
    ``cli.py`` treats it exactly like the other pass-through
    subcommands. Tests catch ``SystemExit`` (units) or read the
    subprocess return code (E2E)."""


def _die_usage(mode: str, message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    print(
        f"Run 'agentive {mode} --help' for usage and examples.",
        file=sys.stderr,
    )
    raise DoorExit(2)


def _die_install(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise DoorExit(1)


def _is_tty() -> bool:
    return sys.stdin.isatty()


def _prompt_yn(question: str) -> str:
    ans = input(f"{question} [y/N] ")
    return "yes" if ans.lower().startswith("y") else "no"


def _expand_tilde(value: str) -> str:
    """Leading-~ expansion, the env-source precedent — a preset or env
    value can carry a literal tilde the shell never expanded.
    ``expanduser`` also handles ``~user/…`` correctly (deep evaluator,
    this PR — the bash door's ``${1/#\\~/$HOME}`` mangled that form);
    a mid-string ``~`` stays literal."""
    if value.startswith("~"):
        return os.path.expanduser(value)
    return value


# ─────────────────────────────────────────
# Preset layer (KIT-0056/0058, re-anchored by KIT-0104)
# ─────────────────────────────────────────
def config_home(target: Path) -> Path | None:
    """Locate the operator config home; never write anything.

    Packaged-world anchor (operator decision 2026-08-13): the VISIBLE
    sibling of the project being created or adopted —
    ``<target-parent>/agentive-config`` — since there is no kit clone
    to be a sibling of. For the conventional one-projects-folder
    layout this resolves to the same directory the kit-side door used.
    ``AGENTIVE_KIT_CONFIG_DIR`` is the ONLY override — an override,
    never a search chain, and a TRUSTED operator-owned value.
    """
    env_override = os.environ.get("AGENTIVE_KIT_CONFIG_DIR")
    if env_override:
        return Path(_expand_tilde(env_override))
    parent = Path(os.path.abspath(target)).parent
    return parent / "agentive-config"


def load_preset(
    home: Path | None, no_preset: bool
) -> tuple[dict[str, str], Path | None]:
    """Read the flat ``key: value`` preset; fail loud, never partial.

    Malformed lines and duplicate keys exit 2 naming the line; unknown
    keys WARN and are skipped (forward compatibility). Returns the
    (possibly empty) answers dict and the preset path when loaded.
    """
    if no_preset or home is None:
        return {}, None
    preset_file = home / "preset"
    if not preset_file.is_file():
        return {}, None
    if not os.access(preset_file, os.R_OK):
        print(
            f"Error: preset exists but is not readable: {preset_file} — "
            "fix its permissions, or pass --no-preset",
            file=sys.stderr,
        )
        raise DoorExit(2)
    data: dict[str, str] = {}
    try:
        text = preset_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        # a preset the door cannot read is a usage problem to fix, never
        # a traceback (fast-gate evaluator, this PR)
        print(
            f"Error: could not read preset {preset_file}: {exc} — fix the "
            "file, or pass --no-preset",
            file=sys.stderr,
        )
        raise DoorExit(2) from None
    for lineno, line in enumerate(text.splitlines(), start=1):
        line = line.rstrip("\r")  # CRLF tolerance (kit_markers precedent)
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in line:
            print(
                f"Error: malformed preset line {lineno} in {preset_file}: "
                f"'{line}' (expected 'key: value')",
                file=sys.stderr,
            )
            raise DoorExit(2)
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if key not in PRESET_KEYS:
            print(
                f"Warning: unknown preset key '{key}' (line {lineno} in "
                f"{preset_file}) — ignored",
                file=sys.stderr,
            )
            continue
        if key in data:
            print(
                f"Error: duplicate preset key '{key}' (line {lineno} in "
                f"{preset_file}) — a preset answers each question once",
                file=sys.stderr,
            )
            raise DoorExit(2)
        data[key] = value
    return data, preset_file


def preset_get(preset: dict[str, str], key: str) -> str | None:
    """A stored-but-empty answer counts as unanswered (falls through)."""
    value = preset.get(key, "")
    return value if value else None


def seed_config_home(home: Path | None, no_preset: bool) -> None:
    """Defensive guardrail seeding on FIRST USE of an existing home.

    Idempotent, never overwrites, never creates the folder itself
    (creating it is the operator engaging the preset flow —
    /setup-preset guides that). A seeding failure warns and continues:
    guardrails are a courtesy, never the install's critical path.
    Temp-then-mv so an interrupted partial write can never stick.
    """
    if no_preset or home is None or not home.is_dir():
        return
    gitignore = home / ".gitignore"
    if not gitignore.exists():
        try:
            tmp = home / ".gitignore.tmp"
            tmp.write_text("env.source\n*.env\n", encoding="utf-8")
            tmp.replace(gitignore)
            print(f"Seeded {gitignore} (env.source and *.env stay out of git)")
        except OSError:
            try:
                (home / ".gitignore.tmp").unlink(missing_ok=True)
            except OSError:
                pass
            print(
                f"Warning: could not seed {gitignore} — check the folder's "
                "permissions",
                file=sys.stderr,
            )
    readme = home / "README.md"
    if not readme.exists():
        body = (
            "# agentive-config\n"
            "\n"
            "Operator config for the agentive setup door — a visible\n"
            "sibling of your projects folder, personal and per-machine,\n"
            "never distributed by any sync or export path. `preset`\n"
            "pre-answers the door's questions (author it conversationally\n"
            "with /setup-preset; format reference: docs/preset.example in\n"
            "the kit). Keeping this folder in a PRIVATE git repo is\n"
            "welcome — the seeded .gitignore keeps `env.source` and\n"
            "`*.env` out of git, and `agentive doctor` warns if the\n"
            "remote is not private. Secrets stay in `env.source`\n"
            "(chmod 600), referenced by path from the preset — never\n"
            "committed, never pasted into chat.\n"
        )
        try:
            tmp = home / "README.md.tmp"
            tmp.write_text(body, encoding="utf-8")
            tmp.replace(readme)
            print(
                f"Seeded {readme} (what this folder is; private-repo "
                "pattern welcome)"
            )
        except OSError:
            try:
                (home / "README.md.tmp").unlink(missing_ok=True)
            except OSError:
                pass
            print(
                f"Warning: could not seed {readme} — check the folder's " "permissions",
                file=sys.stderr,
            )


# ─────────────────────────────────────────
# Resolution chain (CLI flag → preset → kit default → prompt)
# ─────────────────────────────────────────
def normalize_bots(raw: str) -> str | None:
    """Canonicalize a bots answer; ``None`` = empty/unanswered.

    Raises ``ValueError`` with the user-facing message on an unknown
    token or an illegal 'none' combination — callers print it and
    convert to their own usage error, exactly like the bash pair
    (normalize_bots stderr + die_usage).
    """
    tokens = [tok for tok in raw.replace(",", " ").lower().split() if tok]
    cr = bb = none = False
    for tok in tokens:
        # membership over a fixed vocabulary — identifier equality per
        # token, same rule as every other bots reader
        if tok == "coderabbit":
            cr = True
        elif tok == "bugbot":
            bb = True
        elif tok == "none":
            none = True
        else:
            raise ValueError(
                f"Error: unknown bot '{tok}' (expected: coderabbit, " "bugbot, or none)"
            )
    if none:
        if cr or bb:
            raise ValueError(
                f"Error: 'none' cannot be combined with bot names (got: {raw})"
            )
        return "none"
    if cr and bb:
        return "coderabbit bugbot"
    if cr:
        return "coderabbit"
    if bb:
        return "bugbot"
    return None  # empty → unanswered, caller decides


def kit_default(key: str, shape: str = "") -> str | None:
    if key == "shape":
        return "single"
    if key == "profile":
        return "none" if shape == "planning" else "python"
    return None  # no kit default — falls to the prompt layer


def resolve_setting(
    key: str,
    cli_value: str,
    preset: dict[str, str],
    shape: str = "",
    record: dict[str, str] | None = None,
) -> str | None:
    """The ONE resolution chain: CLI → (record blocks preset) → preset
    → kit default. A question the target's record already answered is
    not open, so the preset layer is not consulted for it — the chain
    falls through to the kit default exactly as on a preset-less
    machine. The record itself is preserved by the engine
    (append-if-absent / --preserve-regions), so the RESOLVED value may
    deliberately differ from the recorded one — every surface that must
    follow the record (venv offer, materials gate) keys on
    ``effective_profile``, never on this return value. This mirrors the
    bash door byte-for-byte (bootstrap resolve_setting + its
    EFFECTIVE_PROFILE pattern, BugBot rounds 2-3 of PR #83)."""
    if cli_value:
        return cli_value
    rec_value = (record or {}).get(key.replace("-", "_"), "")
    if not rec_value:
        preset_value = preset_get(preset, key)
        if preset_value:
            return preset_value
    return kit_default(key, shape)


# ─────────────────────────────────────────
# Validation (pure — no filesystem access)
# ─────────────────────────────────────────
def validate_values(shape: str, profile: str) -> bool:
    """``profile`` may be "" (unresolved). Prints the error itself."""
    if shape not in ("single", "planning"):
        print(
            f"Error: unknown shape: '{shape}' (expected: single | planning)",
            file=sys.stderr,
        )
        return False
    if profile not in ("python", "none", ""):
        print(
            f"Error: unknown profile: '{profile}' (expected: python | none)",
            file=sys.stderr,
        )
        return False
    return True


def validate_pair(shape: str, profile: str) -> bool:
    if (shape, profile) in LEGAL_PAIRS:
        return True
    print(
        f"Error: illegal shape/profile combination: {shape} + {profile}",
        file=sys.stderr,
    )
    print(f"       Legal pairs: {legal_pairs_human()}", file=sys.stderr)
    return False


def validate_combo(opts: "DoorOptions") -> bool:
    """Cross-flag legality — reads the RESOLVED options. Prints the
    offending pairing and returns False (main converts to exit 2)."""
    if opts.shape == "planning":
        if opts.no_kit:
            print(
                "Error: --no-kit contradicts --shape planning (the planning "
                "shape IS the kit workflow)",
                file=sys.stderr,
            )
            return False
        if opts.design_materials == "yes":
            print(
                "Error: --design-materials applies to single-shape adopts only",
                file=sys.stderr,
            )
            return False
        if opts.name or opts.prefix:
            print(
                "Error: --name/--prefix apply to '--new --shape single' "
                "exports only",
                file=sys.stderr,
            )
            return False
    else:
        if opts.target_path or opts.target_github:
            print(
                "Error: --target-path/--target-github apply to the planning "
                "shape only",
                file=sys.stderr,
            )
            return False
    if opts.mode == "new":
        if opts.no_kit:
            print(
                "Error: --no-kit applies to --adopt (single shape) only",
                file=sys.stderr,
            )
            return False
        if opts.design_materials == "yes":
            print(
                "Error: --design-materials applies to --adopt only",
                file=sys.stderr,
            )
            return False
    else:
        if opts.name or opts.prefix:
            print("Error: --name/--prefix apply to --new only", file=sys.stderr)
            return False
    if opts.effective_profile == "none":
        if opts.with_venv == "yes":
            print(
                "Error: --with-venv requires profile python (effective "
                "profile: none)",
                file=sys.stderr,
            )
            return False
        if opts.design_materials == "yes":
            print(
                "Error: --design-materials requires profile python (the "
                "materials flow runs setup-dev)",
                file=sys.stderr,
            )
            return False
    if opts.design_materials == "yes" and opts.no_kit:
        print(
            "Error: --no-kit contradicts --design-materials (the materials "
            "flow installs the full kit workflow)",
            file=sys.stderr,
        )
        return False
    return True


# ─────────────────────────────────────────
# Argument parsing
# ─────────────────────────────────────────
class DoorOptions:
    """Parsed + resolved door state (the bash globals, named)."""

    def __init__(self, mode: str):
        self.mode = mode  # "new" | "adopt"
        self.target_raw = ""
        self.target: Path | None = None
        self.shape_cli = ""
        self.profile_cli = ""
        self.shape = ""
        self.profile = ""
        self.effective_shape = ""
        self.effective_profile = ""
        self.name = ""
        self.prefix = ""
        self.target_path = ""
        self.target_github = ""
        self.no_kit = False
        self.design_materials = ""
        self.with_evaluators = ""
        self.with_venv = ""
        self.bots_cli = ""
        self.bots = ""
        self.no_preset = False
        self.env_source = ""
        self.record: dict[str, str] = {}
        self.preset: dict[str, str] = {}
        self.preset_path: Path | None = None


_VALUE_FLAGS = {
    "--shape": "shape_cli",
    "--profile": "profile_cli",
    "--name": "name",
    "--prefix": "prefix",
    "--target-path": "target_path",
    "--target-github": "target_github",
    "--bots": "bots_cli",
}

_SWITCH_FLAGS = {
    "--no-kit": ("no_kit", True),
    "--no-preset": ("no_preset", True),
    "--design-materials": ("design_materials", "yes"),
    "--no-design-materials": ("design_materials", "no"),
    "--with-evaluators": ("with_evaluators", "yes"),
    "--without-evaluators": ("with_evaluators", "no"),
    "--with-venv": ("with_venv", "yes"),
    "--without-venv": ("with_venv", "no"),
}


def usage_text(mode: str) -> str:
    """The door's help — the flag list `/new-project` derives its
    interview from at runtime (KIT-0067 F2), so every flag appears."""
    other = "adopt" if mode == "new" else "new"
    if mode == "new":
        headline = (
            "Create <dir> (must not exist) as a packaged agentive project:\n"
            ".kit/ content scaffold + records + pins. Lifecycle scripts come\n"
            "from agentive-kit and agent bodies from the agentive-workflow\n"
            "plugin — nothing is copied. Runs from anywhere; no kit checkout\n"
            "is involved."
        )
    else:
        headline = (
            "Install the packaged agentive workflow into an EXISTING\n"
            "directory: .kit/ content scaffold + records + pins, preserving\n"
            "every file already present. Lifecycle scripts come from\n"
            "agentive-kit and agent bodies from the agentive-workflow\n"
            "plugin — nothing is copied. Runs from anywhere; no kit checkout\n"
            "is involved."
        )
    return f"""\
agentive {mode} — the agentive setup door (agentive-kit v{agentive_kit.__version__})

Usage: agentive {mode} <dir> [flags]

{headline}

Shape × profile legality (single owner: the agentive package — doctor
and every other reader consult the recorded pair, never re-derive):

  |          | python      | none         |
  |----------|-------------|--------------|
  | single   | ✔ (default) | ✔ (docs-only)|
  | planning | ✘           | ✔ (forced)   |

Flags (every interactive question has one — non-TTY runs never hang):
  --shape <s>          single (default) | planning
  --profile <p>        python | none (default: by shape, see matrix)
  --name / --prefix    project name / task prefix (new, single only)
  --target-path / --target-github
                       product-repo pointer (planning only)
  --no-kit             rung 0 (KIT-ADR-0032): plain repo, no .kit/, no
                       kit install (adopt, single shape only)
  --bots <b>           declare which review bots run on this project:
                       'coderabbit bugbot' (or a subset) | 'none'
                       (comma or space separated). Recorded as a
                       `bots:` line in the kit-install region; the
                       preflight gates SKIP declared-absent bots.
                       No flag/answer = no line = both bots expected.
  --with-evaluators / --without-evaluators
                       answer the evaluator-install offer (provisions
                       the evaluator library + the adversarial CLI)
  --with-venv / --without-venv
                       answer the venv offer (profile python only)
  --no-preset          ignore the operator preset for this run
  --design-materials / --no-design-materials
                       (adopt) the interactive materials flow does not
                       ship in the package — use the project-intake
                       agent instead; --no-design-materials silences
                       the detection hint on git-less targets

Resolution chain: CLI flag → operator preset → kit default →
interactive prompt (TTY only). On adopt of a target that already
carries a kit-install record, the record's values win over the preset
for shape/profile/bots/target-pointer (the record is the project's
identity; divergence is `agentive doctor --against-preset`'s INFO
surface, never a silent re-answer).

Operator preset: flat `key: value` lines at
<target-parent>/agentive-config/preset — a VISIBLE sibling of your
projects folder. Recognized keys: shape, profile, bots, evaluators
(yes|no), venv (yes|no), target-path, target-github, env-source.
AGENTIVE_KIT_CONFIG_DIR overrides the location (an override, never a
search chain — a TRUSTED, operator-owned value). Author a preset
conversationally with the /setup-preset command.

Every --new target ends with a present, mode-0600, gitignored .env —
copied from the preset's env-source when set, else seeded from the
scaffold's .env.template. API keys move only by OPERATOR action.

Exit contract:
  0  install succeeded — the doctor verdict is REPORTED, never encoded
  1  install failed (an engine or record step errored)
  2  usage error or illegal shape/profile combination

See also: agentive {other} --help
"""


def parse_args(mode: str, argv: list[str]) -> DoorOptions:
    opts = DoorOptions(mode)
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--help", "-h"):
            print(usage_text(mode))
            raise DoorExit(0)
        matched = False
        for flag, attr in _VALUE_FLAGS.items():
            if arg == flag:
                i += 1
                value = argv[i] if i < len(argv) else ""
                if value.startswith("-"):
                    # a following flag is not a value ('--shape --bots'
                    # must not adopt '--bots')
                    _die_usage(
                        mode,
                        f"{flag} requires a value (got the flag '{value}' " "instead)",
                    )
                if not value:
                    # deliberate deviation from the bash door, which let
                    # a trailing '--shape' silently resolve to the kit
                    # default (deep evaluator, this PR): an explicit
                    # flag with no value is a mistake to surface, never
                    # an answer to drop (the masking class)
                    _die_usage(mode, f"{flag} requires a value")
                setattr(opts, attr, value)
                matched = True
                break
            if arg.startswith(flag + "="):
                value = arg[len(flag) + 1 :]
                if not value:
                    _die_usage(mode, f"{flag} requires a value")
                setattr(opts, attr, value)
                matched = True
                break
        if not matched and arg in _SWITCH_FLAGS:
            attr, value = _SWITCH_FLAGS[arg]
            setattr(opts, attr, value)
            matched = True
        if not matched:
            if arg.startswith("-"):
                _die_usage(mode, f"unknown argument: {arg}")
            if opts.target_raw:
                _die_usage(
                    mode,
                    f"multiple target directories given ('{opts.target_raw}' "
                    f"and '{arg}')",
                )
            opts.target_raw = arg
        i += 1
    return opts


# ─────────────────────────────────────────
# Record loading + conflict checks (adopt)
# ─────────────────────────────────────────
def load_record(target: Path) -> dict[str, str]:
    """Best-effort read of the target's kit-install record — an
    unreadable or absent region loads nothing (the engine and doctor
    fail loud on malformed records; the door's conflict checks simply
    have nothing to compare)."""
    claude_md = target / "CLAUDE.md"
    if not claude_md.is_file():
        return {}
    try:
        text = claude_md.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        # best-effort by contract: a CLAUDE.md the door cannot decode
        # loads nothing here — the engine's own reader fails loud on it
        # (UnicodeDecodeError is not an OSError; BugBot round 2)
        return {}
    region = markers.extract_region(text, "kit-install")
    if region is None:
        return {}
    record: dict[str, str] = {}
    for key in ("shape", "profile", "bots", "target_path", "target_github"):
        match = re.search(rf"^[ \t]*{key}:[ \t]*(.*?)[ \t]*$", region, re.MULTILINE)
        # .strip() catches the \r a CRLF CLAUDE.md leaves before the
        # MULTILINE $ (extract_region keeps CRLF interiors; the bash
        # door's [[:space:]] trim ate it too — BugBot, this PR)
        if match and match.group(1).strip():
            record[key] = match.group(1).strip()
    return record


def check_record_conflict(opts: DoorOptions) -> None:
    """EXPLICIT flags that contradict the existing record are an error,
    never a silent preserve. Only the door can do this — it alone knows
    whether a value was operator-given or defaulted."""
    rec = opts.record
    if opts.shape_cli and rec.get("shape") and opts.shape_cli != rec["shape"]:
        _die_usage(
            opts.mode,
            f"--shape {opts.shape_cli} conflicts with the target's existing "
            f"kit-install record (shape: {rec['shape']}) — update the record "
            "first, or drop the flag",
        )
    if opts.profile_cli and rec.get("profile") and opts.profile_cli != rec["profile"]:
        _die_usage(
            opts.mode,
            f"--profile {opts.profile_cli} conflicts with the target's "
            f"existing kit-install record (profile: {rec['profile']}) — "
            "update the record first, or drop the flag",
        )
    if opts.bots_cli and rec.get("bots"):
        # compare NORMALIZED forms — 'BugBot CodeRabbit' in the record
        # is the same declaration, not a conflict. An unnormalizable
        # record keeps its raw text: the inevitable mismatch routes the
        # operator to fix the record, which is the right advice.
        try:
            rec_canon = normalize_bots(rec["bots"]) or rec["bots"]
        except ValueError:
            rec_canon = rec["bots"]
        if opts.bots_cli != rec_canon:
            _die_usage(
                opts.mode,
                f"--bots '{opts.bots_cli}' conflicts with the target's "
                f"existing kit-install record (bots: {rec['bots']}) — update "
                "the record first, or drop the flag",
            )


# ─────────────────────────────────────────
# Environment guards
# ─────────────────────────────────────────
def _scrubbed_env() -> dict[str, str]:
    """os.environ minus GIT_* — the KIT-0048 leak class. The engines
    scrub too; this is defense in depth for every git call the door
    itself makes."""
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    # Flush before every child spawn: the child writes to the shared
    # fd directly, so buffered door prints would otherwise appear
    # AFTER engine/doctor output when stdout is a pipe (smoke run,
    # 2026-08-13).
    sys.stdout.flush()
    sys.stderr.flush()
    kwargs.setdefault("env", _scrubbed_env())
    return subprocess.run(cmd, **kwargs)


def ensure_git_identity() -> None:
    """Fail fast with a real message when the install will commit into
    the target but git has no identity."""
    for key in ("user.name", "user.email"):
        found = False
        for scope in ("--global", "--system"):
            result = _run(
                ["git", "config", scope, "--get", key],
                capture_output=True,
                text=True,
            )
            # exit 0 with an EMPTY value is still no identity — git
            # itself refuses to commit with an empty ident, so catching
            # it here keeps the message actionable (fast-gate
            # evaluator, this PR)
            if result.returncode == 0 and result.stdout.strip():
                found = True
                break
        if not found:
            print(
                f"Error: git identity incomplete ({key} unset) — this "
                "install commits into the target.",
                file=sys.stderr,
            )
            print("       Set it first:", file=sys.stderr)
            print(
                "         git config --global user.name  'Your Name'",
                file=sys.stderr,
            )
            print(
                "         git config --global user.email you@example.com",
                file=sys.stderr,
            )
            raise DoorExit(1)


def _looks_like_kit_checkout(target: Path) -> bool:
    """The packaged equivalent of bootstrap's target==PROJECT_ROOT
    refusal: the door provisions projects, never the kit itself."""
    return (target / "scripts" / "local" / "bootstrap").is_file() and (
        target / "scripts" / "local" / "engine-consumer.sh"
    ).is_file()


# ─────────────────────────────────────────
# .env seeding (KIT-0084) — --new only
# ─────────────────────────────────────────
def copy_env_into_target(target: Path, source: Path) -> None:
    """The ONE writer of ``target/.env``: refused unless .env is
    gitignored in the target; the file is BORN 0600 (no window at
    looser permissions); contents are NEVER printed, logged, or
    staged."""
    check = _run(
        ["git", "-C", str(target), "check-ignore", "-q", ".env"],
        capture_output=True,
    )
    if check.returncode != 0:
        _die_install(
            ".env is not gitignored in the target — refusing to seed " "secrets into it"
        )
    content = source.read_bytes()
    env_path = target / ".env"
    # O_NOFOLLOW: never write THROUGH a pre-planted .env symlink — the
    # gitignore check above sees the symlink path, not its referent
    # (deep evaluator, this PR; defense in depth — --new targets are
    # door-created, so a pre-existing symlink is already anomalous).
    try:
        fd = os.open(
            env_path,
            os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW,
            0o600,
        )
    except OSError:
        _die_install(
            f"refusing to write {env_path}: it exists as a symlink or "
            "could not be opened — remove it and re-run"
        )
    try:
        os.write(fd, content)
    finally:
        os.close(fd)
    os.chmod(env_path, 0o600)


def _file_mode(path: Path) -> str:
    try:
        return oct(path.stat().st_mode & 0o777)[2:]
    except OSError:
        return "unknown"


def apply_env_source(target: Path, source_raw: str) -> None:
    """Secrets by reference: the preset names an operator-owned .env
    template; the door copies it 0600."""
    source = Path(_expand_tilde(source_raw))
    if not source.is_file() or not os.access(source, os.R_OK):
        # defense in depth — main pre-validated both before any work
        _die_install(f"preset env-source missing or unreadable: {source}")
    mode = _file_mode(source)
    if mode != "600":
        print(
            f"Warning: env-source {source} is mode {mode} (0600 expected) — "
            f"tighten it: chmod 600 {source}",
            file=sys.stderr,
        )
    copy_env_into_target(target, source)
    print(
        "Seeded .env from preset env-source (mode 0600, gitignored; "
        "contents never printed)"
    )


def seed_env_from_template(target: Path) -> None:
    """Fallback seeding: the target's own .env.template. It carries no
    secrets, but the seeded file will — same discipline from birth."""
    template = target / ".env.template"
    if not template.is_file():
        print(
            "Warning: no .env.template in the target — .env not seeded; "
            "create it by hand (chmod 600)",
            file=sys.stderr,
        )
        return
    copy_env_into_target(target, template)
    print(
        "Seeded .env from .env.template (mode 0600, gitignored) — API keys "
        "still to be added"
    )


def note_env_keys(target: Path) -> None:
    """The packaged world has no kit clone to carry keys over from —
    keys reach a project via the preset's env-source or by operator
    hand. Say so, never silently."""
    print(
        f"No API keys seeded — add them to {target}/.env "
        "('agentive doctor' names what is missing; a preset env-source "
        "seeds them automatically next time)"
    )


def fill_env_identity(opts: DoorOptions) -> None:
    """PROJECT_NAME/TASK_PREFIX in the seeded .env (KIT-0084 F2).

    First assignment rewritten, later DUPLICATES dropped (dotenv
    parsers are last-assignment-wins); indentation and an ``export ``
    prefix tolerated; values with '#', spaces, or tabs written
    double-quoted (safe — quote characters are stripped first).
    Temp-then-rename so a failed write never truncates the .env; the
    temp lives inside .git/ when possible so an interrupted run can
    never leave stageable key material.
    """
    target = opts.target
    assert target is not None
    env_path = target / ".env"
    if not env_path.is_file():
        return
    name = target.name
    prefix = ""
    if opts.shape == "single":
        # the scaffold engine already derived and recorded the prefix —
        # read the recorded value rather than re-deriving it here
        state_path = target / ".kit" / "context" / "current-state.json"
        try:
            with open(state_path, encoding="utf-8") as f:
                value = json.load(f)["project"]["task_prefix"]
        except (OSError, ValueError, KeyError):
            value = None
        # a JSON null must yield nothing, never the string "None"
        if isinstance(value, str):
            prefix = value
        if not prefix:
            prefix = opts.prefix
    # strip newline/CR/quote characters — they cannot be written into a
    # dotenv line faithfully (hardening, not a trust boundary)
    strip = str.maketrans("", "", "\n\r\"'")
    name = name.translate(strip)
    prefix = prefix.translate(strip)

    def emit(key: str, value: str) -> str:
        if re.search(r"[# \t]", value):
            return f'{key}="{value}"'
        return f"{key}={value}"

    seen_name = seen_prefix = False
    out_lines: list[str] = []
    line_re = re.compile(r"^[ \t]*(?:export[ \t]+)?(PROJECT_NAME|TASK_PREFIX)=")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        match = line_re.match(line)
        if match and match.group(1) == "PROJECT_NAME":
            if not seen_name:
                out_lines.append(emit("PROJECT_NAME", name))
                seen_name = True
            continue
        if match and match.group(1) == "TASK_PREFIX":
            if not seen_prefix:
                out_lines.append(emit("TASK_PREFIX", prefix))
                seen_prefix = True
            continue
        out_lines.append(line)
    if not seen_name:
        out_lines.append(emit("PROJECT_NAME", name))
    if not seen_prefix:
        out_lines.append(emit("TASK_PREFIX", prefix))

    tmp_dir = target / ".git" if (target / ".git").is_dir() else target
    fd, tmp_name = tempfile.mkstemp(prefix=".env-rewrite.", dir=tmp_dir)
    try:
        os.write(fd, ("\n".join(out_lines) + "\n").encode("utf-8"))
        os.close(fd)
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, env_path)
    except OSError:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        _die_install(".env rewrite failed — the seeded .env is untouched")
    shown_prefix = prefix or "(empty — set at intake; doctor warns until then)"
    print(
        f"Project identity written to .env: PROJECT_NAME={name} "
        f"TASK_PREFIX={shown_prefix}"
    )


# ─────────────────────────────────────────
# Engine staging + invocation
# ─────────────────────────────────────────
def stage_door_root(stage_dir: Path) -> Path:
    """Arrange engines + data in the kit-tree layout the engines expect
    (they resolve their source tree as SCRIPT_DIR/../..), so they run
    UNMODIFIED — the port stays a port."""
    for store_rel, staged_rel in _STAGE_MAP.items():
        src = _DATA_DIR / store_rel
        dest = stage_dir / staged_rel
        if src.is_dir():
            shutil.copytree(src, dest, dirs_exist_ok=True)
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
    for engine_rel, staged_rel in _ENGINE_MAP.items():
        src = _ENGINES_DIR / engine_rel
        dest = stage_dir / staged_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        # wheels usually keep the execute bit, sdist installs may not
        # (the doctor _CHECK_INTERPRETERS lesson) — engines are invoked
        # via `bash`/`python3` anyway; +x restored for hygiene
        os.chmod(dest, 0o755)
    return stage_dir


def _run_engine(staged_root: Path, engine: str, args: list[str]) -> int:
    """Run a staged engine, output inherited (the door's output IS the
    engine output plus the tail sections)."""
    script = staged_root / "scripts" / "local" / engine
    result = _run(["bash", str(script), *args])
    return result.returncode


# ─────────────────────────────────────────
# Tail sections: verification, offers, doctor
# ─────────────────────────────────────────
def verify_packages(target: Path) -> None:
    """The two package installs are VERIFIED or INSTRUCTED, never
    assumed and never a hard failure (the KIT-0083 degradation
    pattern). The exact strings are a contract —
    tests/test_scaffold_acceptance.py defines them."""
    print()
    print("━━━ package verification ━━━")
    # The lifecycle CLI is what is running right now — verified by
    # construction (the bootstrap-era PATH probe exists for the shim;
    # here the door IS the CLI).
    print(f"agentive CLI: agentive-kit v{agentive_kit.__version__} (verified)")
    plugin_ok = False
    claude_bin = shutil.which("claude")
    if claude_bin:
        # timeout-bounded: the probes are best-effort verification, so
        # a hung `claude` degrades to the install instruction instead
        # of stalling the tail (CodeRabbit, this PR)
        try:
            mkt = _run(
                ["claude", "plugin", "marketplace", "list"],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            mkt = None
        # marketplace source anchored to GitHub (a Directory source
        # silently defeats version pins — KIT-0030; the doctor
        # 50-plugin-source.sh approach)
        source_re = re.compile(
            r"^\s*source:\s*(github \(|https://github\.com/)"
            r"movito/agentive-skills(\s*\)|$)",
            re.IGNORECASE,
        )
        if (
            mkt is not None
            and mkt.returncode == 0
            and any(source_re.search(line) for line in mkt.stdout.splitlines())
        ):
            try:
                plugins = _run(
                    ["claude", "plugin", "list"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except subprocess.TimeoutExpired:
                plugins = None
            plugin_re = re.compile(r"agentive-workflow([@ (]|$)", re.IGNORECASE)
            if (
                plugins is not None
                and plugins.returncode == 0
                and plugin_re.search(plugins.stdout)
            ):
                plugin_ok = True
    if plugin_ok:
        print(
            "agent plugin: verified (agentive-workflow via the "
            "agentive-skills marketplace)"
        )
    else:
        print("Install the agent plugin:")
        print("    claude plugin marketplace add movito/agentive-skills")
        print("    claude plugin install agentive-workflow@agentive-skills")
        if not claude_bin:
            print("  (needs the Claude Code CLI on PATH first)")


def _cli_subprocess(target: Path, *cli_args: str) -> int:
    """Run an ``agentive`` subcommand in the target via the SAME
    interpreter/installation as this process — never a PATH probe that
    could find a different (older) install."""
    result = _run(
        [sys.executable, "-m", "agentive_kit.cli", *cli_args],
        cwd=str(target),
    )
    return result.returncode


def run_offers(opts: DoorOptions) -> None:
    target = opts.target
    assert target is not None
    if opts.with_evaluators == "":
        if _is_tty():
            opts.with_evaluators = _prompt_yn(
                "Install adversarial evaluators now? (library + CLI)"
            )
        else:
            print(
                "Offer skipped (non-interactive): evaluators (library + CLI) "
                "— pass --with-evaluators to install"
            )
            opts.with_evaluators = "no"
    if opts.with_evaluators == "yes":
        # Copied-scripts targets (legacy adopts) keep their own
        # installer; packaged targets use this package's.
        if os.access(target / "scripts" / "core" / "project", os.X_OK):
            rc = _run(
                ["./scripts/core/project", "install-evaluators"],
                cwd=str(target),
            ).returncode
            if rc != 0:
                print(
                    "Warning: evaluator install failed — doctor will flag "
                    "it; re-run './scripts/core/project install-evaluators' "
                    "in the target"
                )
        else:
            rc = _cli_subprocess(target, "install-evaluators")
            if rc != 0:
                print(
                    "Warning: evaluator install failed — doctor will flag "
                    "it; re-run 'agentive install-evaluators' in the target"
                )

    # EFFECTIVE profile, not the resolved one: a profile:none-recorded
    # adopt must never be offered the Python toolchain.
    if opts.effective_profile == "python":
        setup_dev = target / "scripts" / "optional" / "setup-dev.sh"
        if not setup_dev.is_file():
            # Packaged scaffolds ship no setup-dev.sh — an explicit
            # venv answer is acknowledged out loud, never silently
            # dropped (the masking class); the default path says so
            # once too.
            if opts.with_venv == "yes":
                print(
                    "venv setup skipped: this scaffold ships no setup-dev.sh "
                    "— create one when your pyproject exists "
                    "(python3 -m venv .venv)"
                )
            else:
                print(
                    "venv: not offered — packaged scaffolds ship no "
                    "setup-dev.sh; create one when your pyproject exists "
                    "(python3 -m venv .venv)"
                )
        else:
            if opts.with_venv == "":
                if _is_tty():
                    opts.with_venv = _prompt_yn(
                        "Set up the Python venv now (setup-dev.sh)?"
                    )
                else:
                    print(
                        "Offer skipped (non-interactive): venv — pass "
                        "--with-venv to set up"
                    )
                    opts.with_venv = "no"
            if opts.with_venv == "yes":
                rc = _run(
                    ["bash", "scripts/optional/setup-dev.sh"], cwd=str(target)
                ).returncode
                if rc != 0:
                    print(
                        "Warning: venv setup failed — run 'bash "
                        "scripts/optional/setup-dev.sh' in the target"
                    )


def run_doctor_tail(opts: DoorOptions) -> None:
    target = opts.target
    assert target is not None
    print()
    print(f"━━━ project doctor ({target}) ━━━")
    # Copied-scripts targets (legacy adopts) run their own doctor;
    # packaged targets run this package's.
    if os.access(target / "scripts" / "core" / "project", os.X_OK):
        doctor_exit = _run(
            ["./scripts/core/project", "doctor"], cwd=str(target)
        ).returncode
    else:
        doctor_exit = _cli_subprocess(target, "doctor")
    # doctor's exit contract (KIT-0046 F3): 1 = at least one FAIL,
    # 2 = warnings only.
    if doctor_exit == 0:
        verdict = "all checks passed"
    elif doctor_exit == 1:
        verdict = "FAILURES (see above) — install still succeeded; fix before working"
    elif doctor_exit == 2:
        verdict = "WARNINGS (see above) — install still succeeded"
    else:
        verdict = f"doctor could not run (exit {doctor_exit})"
    print()
    print(f"Doctor verdict: {verdict}")
    print(
        f"Install complete: shape={opts.effective_shape} "
        f"profile={opts.effective_profile} → {target}"
    )


# ─────────────────────────────────────────
# Orchestration
# ─────────────────────────────────────────
def _git_init_commit(target: Path, message: str) -> None:
    """git init -b main + initial commit; exit 1 with the F6 message on
    failure (the tree is on disk but sits uncommitted)."""
    steps = (
        ["git", "-C", str(target), "init", "--quiet", "-b", "main"],
        ["git", "-C", str(target), "add", "-A"],
        ["git", "-C", str(target), "commit", "--quiet", "-m", message],
    )
    for cmd in steps:
        if _run(cmd).returncode != 0:
            _die_install(
                "initial commit failed — commit the scaffold in the target "
                "yourself, then re-run doctor"
            )
    print("Scaffold committed (branch: main).")


def _seed_check_hook(opts: DoorOptions, staged_root: Path) -> None:
    """Rung-0 check-hook seeding (adopt --no-kit): the hook is
    toolchain-level, not kit-workflow-level, so rung 0 still gets it —
    but the record's writer (the consumer engine) is not run, because
    rung 0 records nothing (KIT-ADR-0032: no kit install)."""
    target = opts.target
    assert target is not None
    hook = target / "scripts" / "local" / "checks.sh"
    if hook.exists():
        print("scripts/local/checks.sh already present (preserved — " "consumer-owned)")
        return
    hook.parent.mkdir(parents=True, exist_ok=True)
    template = (
        staged_root
        / "scripts"
        / "local"
        / "templates"
        / f"checks-{opts.effective_profile}.sh"
    )
    shutil.copy2(template, hook)
    os.chmod(hook, 0o755)
    print(f"Seeded scripts/local/checks.sh (profile: {opts.effective_profile})")


def _consumer_record_args(opts: DoorOptions) -> list[str]:
    # engines receive the EFFECTIVE pair — a recorded target's engines
    # must act on the recorded identity, never the resolved defaults
    # (CodeRabbit, this PR)
    args = [
        "--internal-record-only",
        "--packaged",
        "--shape",
        opts.effective_shape,
        "--profile",
        opts.effective_profile,
    ]
    if opts.mode == "adopt":
        # an adopted repo's KIT-LOCAL regions are consumer-owned —
        # preserved, never reseeded (the fresh-export reseed semantics
        # apply only to --new trees this door just produced)
        args.append("--preserve-regions")
    if opts.mode == "new" and opts.name:
        args += ["--project-name", opts.name]
    if opts.target_path:
        args += ["--target-path", opts.target_path]
    if opts.target_github:
        args += ["--target-github", opts.target_github]
    if opts.bots:
        args += ["--bots", opts.bots]
    return args


def _orchestrate(opts: DoorOptions, staged_root: Path) -> None:
    target = opts.target
    assert target is not None
    print(
        f"Setup door: mode={opts.mode} shape={opts.effective_shape} "
        f"profile={opts.effective_profile} target={target}"
    )

    if opts.mode == "adopt" and opts.no_kit:
        # ── Rung 0 (KIT-ADR-0032): plain repo — no .kit/, no record ──
        _seed_check_hook(opts, staged_root)
        if not (target / ".git").exists():
            _git_init_commit(
                target,
                f"Initial commit: rung-0 repo (profile: {opts.effective_profile})",
            )
        verify_packages(target)
        # Explicit offer answers are acknowledged OUT LOUD, never
        # silently dropped (the masking class): rung 0 carries no
        # .adversarial config and no setup-dev.sh, so neither offer
        # can be honored here.
        if opts.with_evaluators == "yes":
            print(
                "Evaluators not installed — --no-kit targets carry no "
                ".adversarial config (rung 0); adopt without --no-kit to "
                "get the kit workflow"
            )
        if opts.with_venv == "yes":
            print(
                "venv setup skipped: rung-0 targets ship no setup-dev.sh — "
                "create one when your pyproject exists (python3 -m venv .venv)"
            )
        print()
        print(
            "Rung 0 (--no-kit): plain repo — no .kit/, no kit install. "
            "Doctor not run (nothing to check); promotion to a split "
            "pair is additive (KIT-ADR-0032)."
        )
        print(
            f"Install complete: shape={opts.effective_shape} "
            f"profile={opts.effective_profile} → {target} (rung 0)"
        )
        raise DoorExit(0)

    # effective pair, same rule as _consumer_record_args
    scaffold_args = [
        str(target),
        "--shape",
        opts.effective_shape,
        "--profile",
        opts.effective_profile,
    ]
    if opts.name:
        scaffold_args += ["--name", opts.name]
    if opts.prefix:
        scaffold_args += ["--prefix", opts.prefix]
    if opts.target_path:
        scaffold_args += ["--target-path", opts.target_path]
    if opts.target_github:
        scaffold_args += ["--target-github", opts.target_github]

    if opts.mode == "new":
        # exist_ok=False: main() already refused an existing target, so
        # a directory appearing between that check and here is a race —
        # fail loud rather than scaffold into it (claude-code
        # evaluator, this PR)
        try:
            target.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            _die_usage(
                opts.mode,
                f"--new target already exists: {target} (use 'agentive "
                "adopt' for existing directories)",
            )
    rc = _run_engine(staged_root, "engine-scaffold.sh", scaffold_args)
    if rc != 0:
        _die_install(f"scaffold engine failed (exit {rc})")

    # The consumer engine stays the ONE writer of the CLAUDE.md
    # kit-install record (and seeds the per-repo check hook).
    rc = _run_engine(
        staged_root,
        "engine-consumer.sh",
        [*_consumer_record_args(opts), str(target)],
    )
    if rc != 0:
        _die_install(f"install record step failed (exit {rc})")

    if not (target / ".git").exists():
        _git_init_commit(
            target,
            "Initial commit: agentive project scaffold "
            f"(shape: {opts.effective_shape}, profile: {opts.effective_profile})",
        )

    # ── Working .env from day one (KIT-0084) — --new only ──
    if opts.mode == "new":
        if opts.env_source:
            apply_env_source(target, opts.env_source)
        else:
            seed_env_from_template(target)
            note_env_keys(target)
        fill_env_identity(opts)

    verify_packages(target)
    run_offers(opts)
    run_doctor_tail(opts)
    raise DoorExit(0)


# ─────────────────────────────────────────
# main
# ─────────────────────────────────────────
def main(mode: str, argv: list[str]) -> None:
    """Entry for ``agentive new`` (mode="new") / ``agentive adopt``."""
    if mode not in ("new", "adopt"):  # defensive — cli dispatch owns this
        raise ValueError(f"unknown door mode: {mode}")
    opts = parse_args(mode, argv)

    # ── Target first: the packaged preset home anchors to it ──
    if not opts.target_raw:
        if _is_tty():
            opts.target_raw = input("Target directory: ")
        if not opts.target_raw:
            _die_usage(mode, f"target directory is required (agentive {mode} <dir>)")
    target = Path(_expand_tilde(opts.target_raw))
    target = Path(os.path.abspath(target))

    if mode == "new":
        if target.exists():
            _die_usage(
                mode,
                f"--new target already exists: {target} (use 'agentive "
                "adopt' for existing directories)",
            )
    else:
        if not target.is_dir():
            _die_usage(
                mode,
                f"--adopt target does not exist: {target} (use 'agentive "
                "new' to create one)",
            )
        if _looks_like_kit_checkout(target):
            _die_usage(
                mode,
                f"target looks like an agentive-starter-kit checkout "
                f"({target}) — the door provisions projects, not the kit "
                "itself",
            )
    opts.target = target

    # ── Preset (CLI → preset → kit default → prompt) ──
    if opts.bots_cli:
        try:
            normalized = normalize_bots(opts.bots_cli)
        except ValueError as exc:
            print(exc, file=sys.stderr)
            _die_usage(mode, "invalid --bots value")
        if normalized is None:
            _die_usage(mode, "invalid --bots value")
        opts.bots_cli = normalized
    home = config_home(target)
    opts.preset, opts.preset_path = load_preset(home, opts.no_preset)
    if opts.preset_path:
        print(f"Preset: {opts.preset_path} (pass --no-preset to ignore it)")
    # First-use guardrail seeding — right after the read, so an engaged
    # config home gains its .gitignore before any operator git-init
    # happens around it. No-ops on the stranger path.
    seed_config_home(home, opts.no_preset)

    if mode == "adopt":
        opts.record = load_record(target)

    shape = resolve_setting("shape", opts.shape_cli, opts.preset, record=opts.record)
    opts.shape = shape or ""
    if not validate_values(opts.shape, opts.profile_cli):
        raise DoorExit(2)
    if opts.shape == "planning" and opts.profile_cli == "python":
        if not validate_pair("planning", "python"):
            raise DoorExit(2)
    profile = resolve_setting(
        "profile", opts.profile_cli, opts.preset, opts.shape, opts.record
    )
    opts.profile = profile or ""
    if not validate_pair(opts.shape, opts.profile):
        raise DoorExit(2)
    if opts.shape == "planning" and not opts.profile_cli:
        print("planning shape → profile none (forced; the only legal pair)")
    # The EFFECTIVE pair: on adopt of a recorded target the record wins
    # over the resolved default — every Python-toolchain surface keys
    # on the effective profile, and the ENGINES receive the effective
    # pair (CodeRabbit, this PR: passing resolved defaults would seed
    # single/python state into a recorded planning/none target whose
    # record the same run preserves — a latent the bash door shares).
    opts.effective_shape = opts.record.get("shape", "") or opts.shape
    opts.effective_profile = opts.record.get("profile", "") or opts.profile
    if opts.record and not validate_pair(opts.effective_shape, opts.effective_profile):
        # a hand-edited record carrying an illegal pair must stop here,
        # not reach the engines
        print(
            "       (from the target's kit-install record — fix the "
            "record in CLAUDE.md, then re-run)",
            file=sys.stderr,
        )
        raise DoorExit(2)
    if not validate_combo(opts):
        raise DoorExit(2)

    # Preset may answer the planning shape's target-pointer questions —
    # but only when neither a flag nor the target's record already did.
    if opts.shape == "planning":
        if not opts.target_path and not opts.record.get("target_path"):
            preset_tp = preset_get(opts.preset, "target-path")
            if preset_tp:
                opts.target_path = preset_tp
        if not opts.target_github and not opts.record.get("target_github"):
            preset_tg = preset_get(opts.preset, "target-github")
            if preset_tg:
                opts.target_github = preset_tg

    if opts.target_github and not re.fullmatch(
        r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", opts.target_github
    ):
        _die_usage(
            mode,
            f"--target-github must look like owner/repo "
            f"(got: {opts.target_github})",
        )

    # ── The materials flow does not ship in the package ──
    if opts.design_materials == "yes":
        _die_usage(
            mode,
            "the --design-materials flow is not available in the packaged "
            "door — open the target in Claude Code and run the "
            "project-intake agent instead (or run scripts/local/bootstrap "
            "--adopt --design-materials from an agentive-starter-kit "
            "checkout while the shim lasts)",
        )
    if (
        mode == "adopt"
        and opts.shape == "single"
        and not opts.design_materials
        and not (target / ".git").exists()
        and opts.profile == "python"
    ):
        print(
            "Hint: target has no git repo — if it holds design materials, "
            "open it in Claude Code and run the project-intake agent (the "
            "packaged door does not run the materials flow)"
        )
    opts.design_materials = opts.design_materials or "no"

    # ── Rung 0 records nothing — explicit record-bound flags are an
    #    error, never a silent drop (the masking class) ──
    if opts.no_kit and opts.bots_cli:
        _die_usage(
            mode,
            "--bots writes the kit-install record, and --no-kit targets "
            "record nothing (rung 0) — drop one of the flags",
        )

    # ── Bots declaration (skipped for rung 0 — nothing records it) ──
    if not opts.no_kit and not opts.record.get("bots"):
        if opts.bots_cli:
            opts.bots = opts.bots_cli  # already normalized at parse time
        else:
            preset_bots = preset_get(opts.preset, "bots")
            if preset_bots:
                try:
                    normalized = normalize_bots(preset_bots)
                except ValueError as exc:
                    print(exc, file=sys.stderr)
                    _die_usage(mode, f"invalid preset key 'bots: {preset_bots}'")
                if normalized is None:
                    _die_usage(mode, f"invalid preset key 'bots: {preset_bots}'")
                opts.bots = normalized
            elif _is_tty():
                raw = input(
                    "Which bots review PRs here? [coderabbit bugbot / none — "
                    "Enter = expect both, record nothing] "
                )
                if raw:
                    try:
                        normalized = normalize_bots(raw)
                    except ValueError as exc:
                        print(exc, file=sys.stderr)
                        _die_usage(mode, "invalid bots answer")
                    if normalized is None:
                        _die_usage(mode, "invalid bots answer")
                    opts.bots = normalized

    # ── Preset offer answers + env-source (validated BEFORE any work —
    #    a bad preset value must abort a pristine run, not a
    #    half-installed target) ──
    if not opts.with_evaluators:
        offer = preset_get(opts.preset, "evaluators")
        if offer is not None:
            if offer not in ("yes", "no"):
                _die_usage(
                    mode,
                    f"preset key 'evaluators' must be yes or no (got: {offer})",
                )
            opts.with_evaluators = offer
    if opts.profile == "python" and not opts.with_venv:
        offer = preset_get(opts.preset, "venv")
        if offer is not None:
            # validate BEFORE deciding applicability — a malformed
            # value fails loud even when the answer would be ignored
            if offer not in ("yes", "no"):
                _die_usage(mode, f"preset key 'venv' must be yes or no (got: {offer})")
            if opts.effective_profile != "python":
                print(
                    "Preset venv answer ignored — the target's record "
                    f"(profile: {opts.effective_profile}) has no Python "
                    "toolchain"
                )
            else:
                opts.with_venv = offer
    if mode == "new":
        env_source = preset_get(opts.preset, "env-source")
        if env_source is not None:
            expanded = Path(_expand_tilde(env_source))
            if not expanded.is_absolute() and opts.preset_path is not None:
                # a relative env-source is relative to the PRESET's own
                # home — the seeded guardrails put env.source right
                # beside the preset, and the packaged door runs from
                # anywhere, so cwd-relative would be a lottery (BugBot,
                # this PR)
                expanded = opts.preset_path.parent / expanded
            if not expanded.is_file():
                _die_usage(
                    mode,
                    f"preset env-source not found: {expanded} — fix the "
                    "preset (or drop the key)",
                )
            if not os.access(expanded, os.R_OK):
                _die_usage(
                    mode,
                    f"preset env-source is not readable: {expanded} — fix "
                    "its permissions",
                )
            opts.env_source = str(expanded)

    # ── Orchestrate ──
    if mode == "adopt":
        check_record_conflict(opts)
    # a --new install (and an adopt of a git-less target) will commit
    if mode == "new" or not (target / ".git").exists():
        ensure_git_identity()

    with tempfile.TemporaryDirectory(prefix="agentive-door-") as tmp:
        staged_root = stage_door_root(Path(tmp))
        _orchestrate(opts, staged_root)
