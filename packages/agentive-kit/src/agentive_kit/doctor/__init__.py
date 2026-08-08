"""Environment doctor: driver, install-record reader, preset comparison.

Extracted verbatim-in-behavior from ``scripts/core/project`` (KIT-0090
PR 2); the existing test suite (tests/test_doctor.py drives the real
driver through the ``--dir=`` seam) is the spec.

Per-check migration decision (KIT-0090 F1, recorded): ALL 12 checks —
shell and Python alike — REMAIN executable files run by this driver.
The executable-file contract (emit ``DOCTOR:<name>:<verdict>:<detail>``
lines, receive ``DOCTOR_ROOT``) is a public seam: the whole doctor
test suite, consumer repos' synced check sets, and the ``--dir=``
override all depend on it, and rewriting checks as Python modules
would buy no behavior for that churn. A copy of the check set ships as
package data (``agentive_kit/doctor/checks/``) so a globally installed
CLI can doctor a repo whose synced copies are gone after phase 2; the
repo-local ``scripts/core/doctor.d`` wins whenever present, so today's
behavior is byte-identical.

The kit-install record reader lives here too (shape/profile/bots —
KIT-0048/0050/0056); the legacy script deliberately KEEPS its own copy
for ``cmd_sync`` (sync must work package-free for consumers until
phase 3 — recorded duplication, dies with the script in phase 4).
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from agentive_kit import gitio


def default_checks_dir(project_dir: Path) -> Path:
    """Resolve the check set: repo-local doctor.d, else packaged copy.

    The repo-local set wins whenever present (phase-1 repos all carry
    it, so behavior is unchanged); the packaged copy exists for
    post-phase-2 installs. ``--dir=`` overrides both.
    """
    local = project_dir / "scripts" / "core" / "doctor.d"
    if local.is_dir():
        return local
    return PACKAGED_CHECKS_DIR


# Single definition so the driver can recognize the packaged set.
PACKAGED_CHECKS_DIR = Path(__file__).resolve().parent / "checks"

# Interpreter fallback for packaged checks only: pip/sdist installs may
# drop the execute bit (deep evaluator, PR 2 — a wheel usually keeps
# it, an sdist build usually does not), and packaged checks must not
# FAIL for a packaging artifact. Repo-local doctor.d and --dir= keep
# the strict executability contract the tests pin.
_CHECK_INTERPRETERS = {".py": [sys.executable], ".sh": ["bash"]}


def _normalize_bots(raw):
    """Canonical form of a bots declaration, or None when invalid.

    Valid: ``none`` alone, or a non-empty subset of
    {coderabbit, bugbot} (any order/duplication/case, comma- or
    space-separated; normalized to canonical lowercase order — the
    same tolerance as the door's normalize_bots and the preflight
    reader, so one declaration can never be valid to one reader and
    invalid to another). Shared by the record reader and the
    ``--against-preset`` comparison so the two can never disagree on
    what a declaration means (KIT-0056).
    """
    tokens = raw.replace(",", " ").lower().split()
    if not tokens:
        return None
    for token in tokens:
        # membership: vocabulary check, not identifier equality
        if token not in ("coderabbit", "bugbot", "none"):
            return None
    if "none" in tokens:
        return "none" if len(tokens) == 1 else None
    return " ".join(t for t in ("coderabbit", "bugbot") if t in tokens)


def _doctor_install(project_dir):
    """Read the installation's shape+profile+bots record (KIT-0048
    F2/F3, extended by KIT-0050 F4 and KIT-0056 F1 — one reader,
    never two).

    The record lives in CLAUDE.md's ``kit-install`` KIT-LOCAL region and
    kit_markers.py is its only reader (N4: one extract, runtime-read, no
    cache). Returns ``(shape, profile, bots, errors)`` where ``errors``
    is a list of ``(record, detail)`` pairs, ``record`` in
    {"shape-record", "profile-record", "bots-record"}:

    - anything absent (kit_markers, CLAUDE.md, region) ->
      ("single", "python", None, []) — back-compat: absent means
      today's single shape with the Python toolchain, never an error;
    - a readable record: shape in {single, planning}; a missing
      profile: line defaults by shape (single -> python,
      planning -> none — the KIT-0050 back-compat rule); a missing
      bots: line is None — "both bots expected", the pre-KIT-0056
      default, never an error;
    - malformed/unknown value or unreadable record -> the affected
      value(s) are None and ``errors`` carries the detail — the caller
      runs the FULL check set AND emits a DOCTOR:<record>:FAIL line —
      fail loud while staying maximally diagnostic, never silently
      fall back.
    """
    kit_markers = project_dir / "scripts" / "local" / "kit_markers.py"
    claude_md = project_dir / "CLAUDE.md"
    if not claude_md.exists():
        return "single", "python", None, []
    if not kit_markers.exists():
        # Packaged repos (KIT-0093) ship no kit_markers.py copy — the
        # reader travels with the package (agentive_kit.markers).
        # Absent region keeps the single/python back-compat default;
        # an unreadable file or unbalanced markers fail loud, exactly
        # like the script path (BugBot, PR #116).
        from agentive_kit import markers

        try:
            text = claude_md.read_text(encoding="utf-8")
        except OSError as exc:
            detail = f"shape record unreadable ({exc.__class__.__name__})"
            return None, None, None, [("shape-record", detail)]
        region = markers.extract_region(text, "kit-install")
        if region is None:
            if "BEGIN KIT-LOCAL: kit-install" in text:
                return (
                    None,
                    None,
                    None,
                    [
                        (
                            "shape-record",
                            "kit-install region malformed (unbalanced "
                            "markers) — running the full check set",
                        )
                    ],
                )
            return "single", "python", None, []
        region_text = region
        return _parse_install_record(region_text)
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(kit_markers),
                "extract",
                str(claude_md),
                "kit-install",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        detail = f"shape record unreadable ({exc.__class__.__name__})"
        return None, None, None, [("shape-record", detail)]
    if result.returncode != 0:
        # kit_markers exits 1 with this exact stderr for a missing region
        # (absent = single, back-compat). ANY other failure — crash, bad
        # interpreter, argv error — is an unreadable record and must fail
        # loud, not silently fall back (o3 review).
        if "region not found" in result.stderr:
            return "single", "python", None, []
        detail = result.stderr.strip().splitlines()
        return (
            None,
            None,
            None,
            [
                (
                    "shape-record",
                    "kit_markers extract failed "
                    f"(exit {result.returncode}: "
                    f"{detail[0] if detail else 'no stderr'})",
                )
            ],
        )
    return _parse_install_record(result.stdout)


def _parse_install_record(region_text):
    """Parse a kit-install region body into (shape, profile, bots,
    errors) — shared by the script path and the packaged in-process
    reader (KIT-0093), so the two can never disagree on semantics."""
    raw_shape = None
    raw_profile = None
    raw_bots = None
    for line in region_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("shape:") and raw_shape is None:
            raw_shape = stripped.partition(":")[2].strip()
        elif stripped.startswith("profile:") and raw_profile is None:
            raw_profile = stripped.partition(":")[2].strip()
        elif stripped.startswith("bots:") and raw_bots is None:
            raw_bots = stripped.partition(":")[2].strip()

    errors = []
    shape = None
    if raw_shape is None:
        errors.append(
            (
                "shape-record",
                "kit-install region present but has no shape: line — "
                "running the full check set",
            )
        )
    elif raw_shape == "single" or raw_shape == "planning":
        shape = raw_shape
    else:
        errors.append(
            (
                "shape-record",
                f"unknown shape '{raw_shape}' in kit-install region — "
                "expected single|planning; running the full check set",
            )
        )

    profile = None
    if raw_profile is None:
        # Absent profile defaults by shape; with the shape itself
        # unreadable there is no default to derive — profile stays None
        # (run everything) without a second error line for one cause.
        if shape == "single":
            profile = "python"
        elif shape == "planning":
            profile = "none"
    elif raw_profile == "python" or raw_profile == "none":
        if shape is None:
            # An unreadable shape poisons the profile too: a profile's
            # legality is shape-dependent (planning forces none), so
            # honoring one from a record whose shape cannot be trusted
            # could SKIP checks the shape-record FAIL just promised to
            # run. profile stays None — run everything (BugBot, PR #80).
            pass
        elif raw_profile == "python" and shape == "planning":
            # The P3 matrix pairing, hard-coded as in KIT-0048: planning
            # forces none. Honoring the illegal combination would run
            # toolchain checks a planning repo cannot satisfy; silently
            # coercing would drop what the record says — fail loud.
            errors.append(
                (
                    "profile-record",
                    "profile 'python' is not legal for shape 'planning' "
                    "(planning forces none) — running the full check set",
                )
            )
        else:
            profile = raw_profile
    else:
        errors.append(
            (
                "profile-record",
                f"unknown profile '{raw_profile}' in kit-install region — "
                "expected python|none; running the full check set",
            )
        )

    # bots declaration (KIT-0056): independent of shape/profile — it
    # scopes no doctor checks, only the preflight gates and the
    # --against-preset comparison. Absent = None = both bots expected.
    # An invalid value fails loud (F4): a typo'd declaration silently
    # read as "declared absent" could SKIP gates it should not.
    bots = None
    if raw_bots is not None:
        bots = _normalize_bots(raw_bots)
        if bots is None:
            errors.append(
                (
                    "bots-record",
                    f"invalid bots declaration '{raw_bots}' in kit-install "
                    "region — expected 'none' or a subset of: "
                    "coderabbit bugbot",
                )
            )
    return shape, profile, bots, errors


def _check_declared(check_path, keyword):
    """Tokens a doctor.d check declares via its `# <keyword>:` header
    line — keyword is "shapes" (KIT-0048) or "profiles" (KIT-0050 F5);
    the two declarations share one mechanism by design.

    Returns a set of tokens, or None when the check declares nothing —
    an undeclared OR empty declaration runs everywhere (never silently
    skipped; o3 review: an empty set would skip the check in every
    shape forever). Case-insensitive; scanned over the first 30 lines,
    which covers long banners without picking up documentation strings
    deep in a check body (convention: the header sits right under the
    shebang).
    """
    try:
        text = check_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    head = "\n".join(text.splitlines()[:30])
    # [^\S\n] = horizontal whitespace only — \s would slurp the newline
    # of an empty declaration and capture the NEXT line as tokens
    match = re.search(
        r"^#[^\S\n]*" + keyword + r":[^\S\n]*(.*)$",
        head,
        re.MULTILINE | re.IGNORECASE,
    )
    if match:
        # lowercase the tokens too — IGNORECASE only covers the keyword,
        # and '# Shapes: Single' must match shape 'single' (CodeRabbit)
        declared = {token.lower() for token in match.group(1).split()}
        return declared or None
    return None


def _config_home(project_dir):
    """Locate the operator config home (KIT-0058, ADR-0027 P7
    amendment): the visible sibling
    ``<primary-clone-parent>/agentive-config`` of this checkout,
    resolved worktree-safely via ``--git-common-dir``.
    ``AGENTIVE_KIT_CONFIG_DIR`` is the ONLY override — an override,
    never a search chain. Mirrors the door's ``config_home()``; the
    equivalence test in tests/test_setup_door.py pins the two so the
    door and doctor can never disagree on the path. Returns None when
    the checkout is not a git repository (no sibling to name).

    Anchoring note (BugBot, PR #91): each resolver anchors to ITS OWN
    checkout — the door to the kit clone, doctor to the project it
    diagnoses. The two name the same folder exactly when kit and
    project share a parent (the documented sibling layout); a consumer
    checkout has no pointer to the kit clone's local path, so the
    kit's parent is not computable from here. When the layouts
    diverge, the override pins the real location, and every output
    line below names the resolved path so the anchor is visible.
    """
    override = os.environ.get("AGENTIVE_KIT_CONFIG_DIR")
    if override:
        # leading-~ expansion mirrors the bash resolvers (env files can
        # carry a literal tilde the shell never expanded)
        return Path(override).expanduser()
    # Delegated to gitio.git_common_dir — the KIT-0080 portable
    # resolution (plain --git-common-dir, GIT_* location-var scrub,
    # anchored on project_dir) lives in ONE place since PR 1.
    common_dir = gitio.git_common_dir(project_dir)
    if common_dir is None:
        return None
    # KIT-0080: plain --git-common-dir, absolutized here. The
    # --path-format=absolute form needs git >= 2.31; Apple's system git
    # (2.30.1) echoes the flag back as an output line and exits 0, so
    # `common` became "--path-format=absolute\n<path>" and the home
    # resolved to garbage. Plain output is RELATIVE to the -C directory
    # (both gits return a bare ".git" from a primary clone), so anchor
    # it on project_dir — never on the process cwd. `/` already discards
    # the left operand when `common` is absolute.
    #
    # No .resolve(): that would follow symlinked ancestors and report a
    # PHYSICAL path, diverging from the bash resolvers this function is
    # pinned equivalent to (tests/test_setup_door.py). os.path.normpath
    # collapses the "<root>/.git" join without touching symlinks.
    # Two levels: `joined` is <primary-clone>/.git, so .parent is the
    # clone root and .parent.parent its PARENT, where the visible
    # agentive-config sibling lives.
    return common_dir.parent.parent / "agentive-config"


def _print_preset_comparison(shape, profile, bots, record_errors, project_dir):
    """`doctor --against-preset` (KIT-0056 F8, ADR-0027 P7): compare
    the project's kit-install record against the operator preset at
    ``<kit-parent>/agentive-config/preset`` (KIT-0058;
    ``AGENTIVE_KIT_CONFIG_DIR`` overrides the location).

    INFO-only by design: divergence is reported as
    ``PRESET:<field>:INFO:<detail>`` lines and NEVER as WARN/FAIL, and
    the doctor exit code is never affected — a deliberately-lean
    project is not wrong. Doctor validates the RECORD (the DOCTOR:
    lines above); the preset is only a comparison baseline. The
    PRESET: prefix keeps these lines out of DOCTOR: parsers entirely.

    Keys other than shape/profile/bots are ignored here by design:
    the door owns the preset-key vocabulary (unknown keys WARN there);
    duplicating its key list in this comparator would be a second
    source of truth that drifts. Structural faults shared with the
    door's parser (malformed lines, duplicate keys) do get reported —
    as INFO, with the comparison skipped whole.
    """
    home = _config_home(project_dir)
    print()
    if home is None:
        print(
            f"PRESET:comparison:INFO:cannot locate the config home "
            f"({project_dir} is not a git clone) — nothing to compare"
        )
        return
    preset_path = home / "preset"
    if not preset_path.is_file():
        print(
            f"PRESET:comparison:INFO:no preset found at {preset_path} — "
            "nothing to compare (the path anchors to this project's "
            "primary-clone parent; set AGENTIVE_KIT_CONFIG_DIR if your "
            "config home lives beside the kit clone elsewhere)"
        )
        return
    try:
        preset_lines = preset_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        print(
            f"PRESET:comparison:INFO:preset unreadable "
            f"({exc.__class__.__name__}) — comparison skipped"
        )
        return
    preset_values = {}
    for lineno, line in enumerate(preset_lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            # loud, names the line, and skips the WHOLE comparison — a
            # partial read could report agreement on fields it never
            # parsed (the masking class, record-reader face)
            print(
                f"PRESET:comparison:INFO:preset malformed at line {lineno} "
                f"('{stripped}') — fix {preset_path}; comparison skipped"
            )
            return
        key, _, value = stripped.partition(":")
        key = key.strip()
        if key in preset_values:
            # same duplicate rule as the door's load_preset — silently
            # letting the last value win could compare against a value
            # the door would refuse to load
            print(
                f"PRESET:comparison:INFO:duplicate preset key '{key}' at "
                f"line {lineno} — fix {preset_path}; comparison skipped"
            )
            return
        preset_values[key] = value.strip()

    if shape is None or profile is None:
        print(
            "PRESET:comparison:INFO:kit-install record unreadable "
            "(see the DOCTOR record FAIL lines) — comparison skipped"
        )
        return

    bots_errored = any(record == "bots-record" for record, _ in record_errors)
    record_values = {
        "shape": shape,
        "profile": profile,
        # absent bots line = both expected (the pre-KIT-0056 default)
        "bots": bots if bots is not None else "coderabbit bugbot",
    }
    defaulted = {"bots": bots is None}
    # Vocabulary checks mirror the door's validate_values: a preset
    # value the door would refuse to install must read as malformed
    # preset data here, never as legitimate divergence (CodeRabbit).
    valid_vocab = {
        "shape": ("single", "planning"),
        "profile": ("python", "none"),
    }
    if (
        preset_values.get("shape") == "planning"
        and preset_values.get("profile") == "python"
    ):
        print(
            "PRESET:comparison:INFO:preset declares an illegal pair "
            "(planning forces profile none) — fix the preset; "
            "shape/profile comparison skipped"
        )
        preset_values.pop("shape", None)
        preset_values.pop("profile", None)
    compared = 0
    divergences = 0
    for key in ("shape", "profile", "bots"):
        preset_val = preset_values.get(key, "")
        if not preset_val:
            continue
        # membership: dict-key + vocabulary checks, not identifier
        # equality (the same construct the legacy script used)
        if key in valid_vocab and preset_val not in valid_vocab[key]:  # noqa: DK003
            print(
                f"PRESET:{key}:INFO:preset {key} value invalid "
                f"('{preset_val}') — {key} comparison skipped"
            )
            continue
        if key == "bots":
            if bots_errored:
                print(
                    "PRESET:bots:INFO:recorded bots declaration is invalid "
                    "(see DOCTOR:bots-record above) — bots comparison skipped"
                )
                continue
            normalized = _normalize_bots(preset_val)
            if normalized is None:
                print(
                    f"PRESET:bots:INFO:preset bots value invalid "
                    f"('{preset_val}') — bots comparison skipped"
                )
                continue
            preset_val = normalized
        compared += 1
        if preset_val != record_values[key]:
            suffix = (
                " (defaulted — no line in the record)" if defaulted.get(key) else ""
            )
            print(
                f"PRESET:{key}:INFO:record has '{record_values[key]}'{suffix}, "
                f"preset says '{preset_val}' — informational only, a "
                "deliberately-lean project is not wrong"
            )
            divergences += 1
    if compared == 0:
        print(
            "PRESET:comparison:INFO:preset answers none of the comparable "
            "fields (shape/profile/bots) — nothing to compare"
        )
    elif divergences == 0:
        print(
            f"PRESET:comparison:INFO:record matches the preset on all "
            f"{compared} compared field(s)"
        )


def cmd_doctor(args, project_dir):
    """`project doctor`: run all doctor.d environment checks (ADR-0027 P4).

    Composable driver: every executable in scripts/core/doctor.d/ runs;
    a failing check never short-circuits its siblings (the fail-fast-
    masking lesson from the sync workflow). Checks emit
    ``DOCTOR:<name>:<verdict>:<detail>`` lines — <name> and <verdict>
    are colon-free tokens, <detail> is everything after the third colon
    (parsers split on the first three colons only, exactly like the
    preflight GATE: format). Verdicts: PASS, WARN, FAIL, SKIP.

    Exit-code contract (F3 — driver errors never overload 0/1):
      0  every check PASS or SKIP
      1  at least one FAIL
      2  warnings only (no FAIL)
      3  driver/usage error (unknown flag, doctor.d missing or empty)

    Read-only (N3): the driver and every check diagnose the environment;
    they never mutate config, env, or the working tree.
    """
    doctor_dir = default_checks_dir(project_dir)
    against_preset = False
    for arg in args:
        # An empty value would resolve Path("") to the cwd and silently
        # diagnose the wrong tree — usage error instead (BugBot round 6).
        if arg == "--against-preset":
            # KIT-0056 F8: compare the record against the operator
            # preset, INFO-only (see _print_preset_comparison).
            against_preset = True
        elif arg.startswith("--dir="):
            # test/advanced seam: run a different check set (resolve now —
            # checks run with a different cwd, so relative would break)
            value = arg.partition("=")[2]
            if not value:
                print("❌ --dir= requires a path")
                return 3
            doctor_dir = Path(value).resolve()
        elif arg.startswith("--root="):
            # diagnose another checkout (e.g. the primary clone from a
            # worktree); checks receive it as DOCTOR_ROOT
            value = arg.partition("=")[2]
            if not value:
                print("❌ --root= requires a path")
                return 3
            project_dir = Path(value).resolve()
            if not project_dir.is_dir():
                print(f"❌ --root is not a directory: {project_dir}")
                return 3
        else:
            print(f"Unknown option: {arg}")
            print(
                "Usage: ./scripts/core/project doctor "
                "[--dir=<checks-dir>] [--root=<checkout>] [--against-preset]"
            )
            return 3

    if not doctor_dir.is_dir():
        print(f"❌ doctor checks directory not found: {doctor_dir}")
        return 3
    # dotfiles (.DS_Store & friends) are never checks — everything else
    # in doctor.d/ is held to the check contract
    checks = sorted(
        p for p in doctor_dir.iterdir() if p.is_file() and not p.name.startswith(".")
    )
    if not checks:
        print(f"❌ no checks found in {doctor_dir}")
        return 3

    # Per-shape inclusion (KIT-0048, fills the P2 seam) and per-profile
    # inclusion (KIT-0050 F5): checks declare their shapes/profiles in
    # `# shapes:` / `# profiles:` headers; the driver reads the install
    # record once and stays otherwise declaration-driven. A malformed
    # record runs everything AND fails loud via the record lines below.
    shape, profile, bots, record_errors = _doctor_install(project_dir)

    # Scrub ambient GIT_* so a leaked GIT_DIR (the KIT-0043 incident
    # class — e.g. doctor invoked from a pre-commit hook in a worktree)
    # cannot redirect git-facing checks at the wrong repository.
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["DOCTOR_ROOT"] = str(project_dir)
    verdicts = []
    for record, detail in record_errors:
        print(f"DOCTOR:{record}:FAIL:{detail}")
        verdicts.append("FAIL")
    for check in checks:
        name = check.name
        declared = _check_declared(check, "shapes")
        if shape is not None and declared is not None and shape not in declared:
            print(
                f"DOCTOR:{name}:SKIP:not applicable to shape '{shape}' "
                f"(check declares: {' '.join(sorted(declared))})"
            )
            verdicts.append("SKIP")
            continue
        declared_profiles = _check_declared(check, "profiles")
        if (
            profile is not None
            and declared_profiles is not None
            and profile not in declared_profiles
        ):
            print(
                f"DOCTOR:{name}:SKIP:not applicable to profile '{profile}' "
                f"(check declares: {' '.join(sorted(declared_profiles))})"
            )
            verdicts.append("SKIP")
            continue
        argv = [str(check)]
        if not os.access(check, os.X_OK):
            interp = (
                _CHECK_INTERPRETERS.get(check.suffix)
                if doctor_dir == PACKAGED_CHECKS_DIR
                else None
            )
            if interp is None:
                print(f"DOCTOR:{name}:FAIL:check file is not executable")
                verdicts.append("FAIL")
                continue
            argv = [*interp, str(check)]
        try:
            result = subprocess.run(
                argv,
                cwd=project_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            print(f"DOCTOR:{name}:FAIL:check timed out after 30s")
            verdicts.append("FAIL")
            continue
        except OSError as exc:
            print(f"DOCTOR:{name}:FAIL:check failed to run ({exc.__class__.__name__})")
            verdicts.append("FAIL")
            continue

        emitted = False
        for line in result.stdout.splitlines():
            if not line.startswith("DOCTOR:"):
                continue
            parts = line.split(":", 3)
            # F1 field contract: exactly DOCTOR:<name>:<verdict>:<detail>
            # with non-empty name and detail — an incomplete record must
            # not be able to count as a pass (CodeRabbit round 2)
            malformed = len(parts) < 4 or not parts[1] or not parts[3].strip()
            verdict = parts[2] if len(parts) >= 3 else ""
            # membership: verdict vocabulary check, not identifier equality
            if malformed or verdict not in ("PASS", "WARN", "FAIL", "SKIP"):
                # malformed line: surface it, count it as a failure
                print(line)
                verdicts.append("FAIL")
                emitted = True
                continue
            print(line)
            verdicts.append(verdict)
            emitted = True
        if result.stderr:
            sys.stderr.write(result.stderr)
        if not emitted:
            print(
                f"DOCTOR:{name}:FAIL:check produced no DOCTOR line "
                f"(exit {result.returncode})"
            )
            verdicts.append("FAIL")
        elif result.returncode != 0:
            # a check that emitted lines but then crashed may have lost
            # its remaining concerns — surface the crash, don't let an
            # early PASS line mask it (fast-v2 review finding)
            print(
                f"DOCTOR:{name}:FAIL:check exited {result.returncode} "
                "after emitting output — remaining concerns may be lost"
            )
            verdicts.append("FAIL")

    fails = verdicts.count("FAIL")
    warns = verdicts.count("WARN")
    passes = verdicts.count("PASS")
    skips = verdicts.count("SKIP")
    print(f"\nDoctor: {passes} pass, {warns} warn, {fails} fail, {skips} skip")
    if against_preset:
        _print_preset_comparison(shape, profile, bots, record_errors, project_dir)
    if fails:
        return 1
    if warns:
        return 2
    return 0
