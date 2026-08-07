"""Evaluator provisioning: library install + CLI ensure + pin readers.

Extracted verbatim-in-behavior from ``scripts/core/project`` (KIT-0090
PR 3). Provisioning ONLY — running evaluations is and remains
adversarial-workflow's job (task boundary statement).

One deliberate change rides the extraction per KIT-0090 F6 —
KIT-0079, closed by reference here: the evaluator LIBRARY pin is now
read from ``.adversarial/config.yml`` (``evaluator_library_version``,
the canonical home KIT-0083 seeded) first, with pyproject's
``[tool.adversarial] library_version`` as a fallback mirror — so
planning-shape repos (which ship no pyproject) resolve the pin. The
interim drift test ``test_library_pin_mirrors_agree`` dies with this
change (it guarded the two-home state).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _is_tag_like(value):
    """True for a plausible git tag/branch name (e.g. v0.10.0).

    One gate for every pin source — config.yml, the pyproject mirror
    (tomllib, tomli, and regex paths alike), and --ref — so an
    option-shaped value (`--upload-pack=...`) can never reach
    `git clone --branch` as a git OPTION (CodeRabbit, PR #110). List
    args make shell injection impossible; this is about option
    injection and failing clearly.
    """
    # isinstance first: tomllib can hand back an int/bool/list for the
    # mirror pin, and re.fullmatch would raise TypeError instead of the
    # clean invalid-pin exit (CodeRabbit, PR #110).
    return isinstance(value, str) and bool(
        re.fullmatch(r"[0-9A-Za-z][0-9A-Za-z.\-_/+]*", value)
    )


def _get_evaluator_library_version(project_dir):
    """Read the evaluator-library pin: config.yml first, pyproject mirror.

    Canonical home is ``.adversarial/config.yml`` →
    ``evaluator_library_version`` (KIT-0079: planning-shape repos ship
    no pyproject, which made pyproject an unreadable home for half of
    all projects). pyproject's ``[tool.adversarial] library_version``
    stays a fallback mirror. Same anchored-regex read as the CLI pin —
    no YAML dependency, commented-out examples can never match.

    There is deliberately no baked-in default: a silent fallback
    installed a five-minor-versions-old library once (KIT-0068 A08).
    Exits naming both sources when no pin is readable.
    """
    config_yml = Path(project_dir) / ".adversarial" / "config.yml"
    try:
        text = config_yml.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        text = ""
    match = re.search(
        r'^\s*evaluator_library_version\s*:\s*["\']?([^"\'\s#]+)',
        text,
        re.MULTILINE,
    )
    if match:
        candidate = match.group(1)
        # A hand-edited pin reaches `git clone --branch <pin>` as a
        # LIST element (never a shell), so this is not about shell
        # injection — it is about a value like `--upload-pack=...`
        # becoming a git OPTION, and about failing clearly (deep
        # evaluator, PR 3; same reasoning as _is_version_like for the
        # CLI pin, but git tags may start with a letter, e.g. v0.10.0).
        if _is_tag_like(candidate):
            return candidate
        print(f"❌ Invalid evaluator_library_version pin: {candidate!r}")
        print(f"   Source: {config_yml} — fix the pin (a git tag like v0.10.0),")
        print("   or pass an explicit version with --ref <tag>.")
        sys.exit(1)

    pyproject = Path(project_dir) / "pyproject.toml"
    try:
        import tomllib
    except ImportError:  # Python 3.10 — no stdlib tomllib
        try:
            import tomli as tomllib
        except ImportError:
            tomllib = None  # fall back to a regex scan (doctor.d/40 pattern)

    version = None
    try:
        if tomllib is not None:
            with open(pyproject, "rb") as f:
                config = tomllib.load(f)
            version = (
                config.get("tool", {}).get("adversarial", {}).get("library_version")
            )
        else:
            ptext = pyproject.read_text(encoding="utf-8")
            pmatch = re.search(
                r'^\s*library_version\s*=\s*"([^"]+)"', ptext, re.MULTILINE
            )
            version = pmatch.group(1) if pmatch else None
    except (FileNotFoundError, OSError, ValueError, AttributeError):
        version = None

    if not version:
        print("❌ Could not read the evaluator-library version pin")
        print(f"   Source: {config_yml} → evaluator_library_version")
        print(f"   Mirror: {pyproject} → [tool.adversarial] library_version")
        print("   Fix the config.yml pin, or pass --ref <tag>.")
        sys.exit(1)
    if not _is_tag_like(version):
        # The mirror is hand-edited too — same gate as config.yml
        # (CodeRabbit, PR #110).
        print(f"❌ Invalid library_version pin in pyproject.toml: {version!r}")
        print("   Expected a git tag (e.g. v0.10.0); fix the pin or pass --ref.")
        sys.exit(1)
    return version


EVALUATOR_LIBRARY_REPO = "https://github.com/movito/adversarial-evaluator-library.git"

# The PyPI distribution providing the `adversarial` CLI (KIT-0083).
ADVERSARIAL_CLI_DIST = "adversarial-workflow"

# Seconds allowed for `adversarial --version`. MUST match the bound in
# scripts/core/doctor.d/31-evaluator-cli.sh: the whole point of the
# liveness probe is that the installer and the doctor never disagree
# about one install, and a CLI answering in, say, 25s would otherwise be
# "working" to one surface and FAIL to the other (CodeRabbit round 1).
CLI_PROBE_TIMEOUT = 20


def _is_version_like(value):
    """True for a plausible PEP 440-ish version string.

    config.yml is hand-edited, so the pin can be anything. The value is
    passed as a LIST element to subprocess.run (never a shell), so this
    is not about injection — it is about failing clearly: a pin of
    `--force` would otherwise become `adversarial-workflow==--force` and
    surface as a baffling uv error instead of "your pin is wrong"
    (claude-code review).
    """
    return bool(re.fullmatch(r"[0-9][0-9A-Za-z.\-_+!]*", value or ""))


def _get_adversarial_cli_version(project_dir):
    """Read the CLI pin: .adversarial/config.yml first, pyproject.toml as mirror.

    Canonical home is .adversarial/config.yml because it ships to BOTH
    shapes; planning-shape repos have no pyproject.toml at all
    (engine-consumer.sh:294), which is what made pyproject an unreadable
    home for half of all projects (#60, KIT-0083). pyproject stays a
    fallback mirror so the kit's own checkout keeps working.

    Returns None when no pin is readable — callers install nothing and
    print the exact command instead. Deliberately NOT a silent
    unpinned-latest: that is the KIT-0068 A08 class, where a quiet
    fallback installed a five-versions-old library.

    Parsed with a regex rather than a YAML load: `project` runs on bare
    Python with no third-party imports, and PyYAML is not guaranteed
    (same reasoning as the tomllib fallback above).
    """
    config_yml = Path(project_dir) / ".adversarial" / "config.yml"
    try:
        text = config_yml.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        text = ""
    # Anchored to line start so a commented-out example (# adversarial_
    # cli_version: "9.9.9") can never be read as the live pin.
    match = re.search(
        r'^\s*adversarial_cli_version\s*:\s*["\']?([^"\'\s#]+)', text, re.MULTILINE
    )
    if match and _is_version_like(match.group(1)):
        return match.group(1)

    # Mirror: pyproject's dependency spec, e.g. "adversarial-workflow>=1.0.1".
    # Accepts >=, ==, ~= and a bare version: KIT-0079 may write an exact
    # pin here, and matching only >= would silently read as "no pin" and
    # send an installable project down the instruct-only path (o3 review).
    pyproject = Path(project_dir) / "pyproject.toml"
    try:
        ptext = pyproject.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
    mirror = re.search(
        r'["\']' + re.escape(ADVERSARIAL_CLI_DIST) + r'\s*(?:>=|==|~=)?\s*([^"\',\s]+)',
        ptext,
    )
    if not mirror:
        return None
    candidate = mirror.group(1).strip()
    return candidate if _is_version_like(candidate) else None


def _adversarial_cli_works():
    """True when `adversarial` is on PATH AND actually runs.

    Presence is not liveness: a corrupt or half-written install leaves a
    binary that `shutil.which` finds but that exits non-zero on every
    invocation. Checking only presence here while doctor.d/31 probes
    `--version` would let the installer print ✅ for a CLI the very next
    doctor run reports as FAIL (o3 + fast-v2 review, both rounds).

    Probes the EXIT CODE, never the output: a healthy CLI prints
    "Unknown fields in evaluator.yml" warnings to stderr.
    """
    if not shutil.which("adversarial"):
        return False
    try:
        probe = subprocess.run(
            ["adversarial", "--version"],
            capture_output=True,
            text=True,
            timeout=CLI_PROBE_TIMEOUT,
            # Closes the stdin path, exactly as the doctor check does: a
            # corrupt CLI that blocks on stdin must not stall an
            # interactive install, nor swallow input the user typed for
            # the surrounding prompt flow (CodeRabbit round 1).
            stdin=subprocess.DEVNULL,
        )
    except (subprocess.TimeoutExpired, OSError):
        # A hanging or unexecutable binary is not a working one.
        return False
    return probe.returncode == 0


def _ensure_adversarial_cli(project_dir):
    """Ensure the `adversarial` CLI is on PATH; instruct if it can't be.

    The KIT-0083 / issue #103 trap: .adversarial/ config and the evaluator
    library both shipped and doctor reported PASS, but nothing ever
    installed the CLI itself — so the planner's Phase 3 evaluation GATE
    was the first thing to discover it, with `command not found`.

    Never fails the caller: the library install is the command's primary
    job and must not be undone by an optional CLI step. Degrades to
    printing the exact command, mirroring the git-missing block below.
    """
    if _adversarial_cli_works():
        print("✅ adversarial CLI already installed")
        return

    version = _get_adversarial_cli_version(project_dir)
    spec = f"{ADVERSARIAL_CLI_DIST}=={version}" if version else ADVERSARIAL_CLI_DIST
    install_cmd = f"uv tool install {spec}"

    if not shutil.which("uv"):
        print("⚠️  adversarial CLI not found, and uv is not installed")
        # Deliberately says nothing about the LIBRARY's state: this step
        # now runs before the git gate and the clone, so the library may
        # not be installed yet — and if git then fails, it never will be
        # (CodeRabbit round 3).
        print("   Running an evaluation needs the CLI. Install uv, then run:")
        print(f"     {install_cmd}")
        print("   uv: https://docs.astral.sh/uv/getting-started/installation/")
        return

    if not version:
        # No readable pin: instruct rather than install unpinned-latest
        # (KIT-0068 A08 — silent fallbacks install the wrong thing).
        print("⚠️  Could not read the adversarial CLI version pin")
        print("   Source: .adversarial/config.yml → adversarial_cli_version")
        print("   Fix that pin, or install explicitly:")
        print(f"     {install_cmd}")
        return

    print(f"📦 Installing the adversarial CLI ({spec})...")
    try:
        result = subprocess.run(
            ["uv", "tool", "install", spec],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        print("⚠️  CLI install timed out (network issue?)")
        print(f"   Retry manually: {install_cmd}")
        return
    except OSError as exc:
        # `shutil.which` proves the executable bit, not that uv can
        # actually run (noexec mount, broken shim, removed between check
        # and run). Without this the exception escapes the "never fails
        # the caller" contract in this function's docstring — and since
        # this step now runs BEFORE the library install, the user would
        # get neither the CLI nor the library (CodeRabbit round 1).
        print(f"⚠️  Could not run uv: {exc}")
        print(f"   Retry manually: {install_cmd}")
        return

    if result.returncode != 0:
        # No claim about the library here either — see the uv-missing
        # branch above (CodeRabbit round 3).
        print("⚠️  CLI install failed — continuing with the library install")
        # Surface only uv's last line: its full stderr is long and the
        # actionable part is the tail.
        detail = (result.stderr or "").strip().splitlines()
        if detail:
            print(f"   {detail[-1]}")
        print(f"   Retry manually: {install_cmd}")
        return

    # Three post-install states, three different remedies — never one
    # blanket ✅. uv exiting 0 does not by itself mean a usable CLI.
    if _adversarial_cli_works():
        print("✅ adversarial CLI installed")
    elif shutil.which("adversarial"):
        # On PATH but not runnable: a corrupt/partial install. Reinstall
        # is the fix, NOT a PATH change.
        print("⚠️  adversarial CLI installed but not runnable")
        print("   It is on PATH, yet '--version' fails — likely a partial")
        print("   or corrupt install. Reinstall:")
        print(f"     uv tool install --force {spec}")
    else:
        # uv installs into ~/.local/bin; an install can succeed while the
        # binary stays unreachable. Say so here rather than letting the
        # doctor check be the first to notice.
        print("✅ adversarial CLI installed — but it is not on your PATH")
        print("   uv installs tools into ~/.local/bin; add it to PATH:")
        print('     export PATH="$HOME/.local/bin:$PATH"')


def cmd_install_evaluators(args, project_dir):
    """Install evaluators from adversarial-evaluator-library."""
    # Parse arguments
    force = "--force" in args

    # Check for --ref flag (e.g., --ref v0.3.0 or --ref main) BEFORE
    # reading the pyproject pin: an explicit --ref must work even where
    # pyproject.toml is absent (planning-shape repos), and the pin
    # reader fails loud in that case (o3 review, KIT-0068).
    version = None
    for i, arg in enumerate(args):
        if arg == "--ref" and i + 1 < len(args):
            version = args[i + 1]
            # Same tag-shape gate as the config.yml pin (CodeRabbit,
            # PR #110): an option-shaped value must fail clearly here,
            # never reach `git clone --branch` as a git option.
            if not _is_tag_like(version):
                print(f"❌ Invalid --ref value: {version!r}")
                print("   Expected a git tag or branch name (e.g. v0.10.0).")
                sys.exit(1)
            break

    # CLI hardcodes .adversarial/ at repo root (see e2465ae) — do not move into .kit/
    evaluators_dir = project_dir / ".adversarial" / "evaluators"
    evaluators_dir.mkdir(parents=True, exist_ok=True)

    print("📦 Adversarial Evaluator Library Installer")
    print("=" * 50)

    # 1. Ensure the CLI FIRST — before both gates below.
    #
    # It must precede the already-installed early return, because the
    # #103 shape is precisely "library present, CLI absent" and a rerun
    # there must still fix the CLI.
    #
    # It must ALSO precede the git gate: the CLI path needs only `uv`,
    # never git, and doctor.d/31 tells users to run THIS COMMAND to fix
    # a missing CLI. With git absent or broken, that advice would exit
    # 1 without ever attempting the thing it was recommended for
    # (BugBot round 1). The two installs have independent
    # prerequisites, so neither gate may own the other's path.
    _ensure_adversarial_cli(project_dir)
    print()

    # 2. Check for git (required for CLONING the library — not for the
    # CLI step above)
    try:
        git_check = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            # Bounded and stdin-closed for the same reasons as the CLI
            # probe: a wedged git (prompting credential helper, hung
            # filesystem) would otherwise hang install-evaluators
            # indefinitely, and an open stdin lets it consume input the
            # user typed for the surrounding flow (CodeRabbit round 2).
            timeout=CLI_PROBE_TIMEOUT,
            stdin=subprocess.DEVNULL,
        )
        git_ok = git_check.returncode == 0
    except subprocess.TimeoutExpired:
        # A git that never answers is not a usable git — same guidance.
        git_ok = False
    except (FileNotFoundError, OSError):
        # A genuinely absent git raises rather than returning non-zero;
        # without this the intended message below never prints and the
        # user gets a raw traceback instead (found reproducing the
        # BugBot finding above).
        git_ok = False
    if not git_ok:
        print("❌ Git is required but not found")
        print()
        print("Install git:")
        print("  macOS:  brew install git")
        print("  Ubuntu: sudo apt install git")
        print("  Windows: https://git-scm.com/download/win")
        sys.exit(1)

    # 3. Check if already installed — BEFORE resolving the version pin:
    # the no-op rerun path must keep working on repos with no readable
    # pyproject pin (planning shape, or installs done only with --ref);
    # the pin is only needed to clone (BugBot round 2, KIT-0068).
    version_file = evaluators_dir / ".installed-version"
    if version_file.exists() and not force:
        installed = version_file.read_text(encoding="utf-8").strip()
        print(f"⚠️  Evaluators already installed (version: {installed})")
        print("   Use --force to reinstall")
        print("   Use --ref <version> to install a different version")
        return

    if version is None:
        version = _get_evaluator_library_version(project_dir)
    print(f"   Version: {version}")
    print()

    # 4. Clone specific version
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"📥 Cloning evaluator library @ {version}...")
        try:
            result = subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    "--branch",
                    version,
                    EVALUATOR_LIBRARY_REPO,
                    tmpdir,
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        except subprocess.TimeoutExpired:
            print("❌ Clone timed out (network issue?)")
            print("   Check your internet connection and try again")
            sys.exit(1)

        if result.returncode != 0:
            if "Could not resolve host" in result.stderr:
                print("❌ Network error - check your internet connection")
            elif "not found" in result.stderr.lower():
                print(f"❌ Version '{version}' not found")
                print(
                    "   Available versions: "
                    "https://github.com/movito/adversarial-evaluator-library/tags"
                )
            else:
                print(f"❌ Failed to clone: {result.stderr.strip()}")
            sys.exit(1)

        # Get actual commit hash for reproducibility
        # Bounded + stdin-closed like every other git call; a wedged or
        # failing rev-parse degrades to an unknown hash — it must never
        # abort an install whose clone already succeeded (BugBot +
        # CodeRabbit, PR #110).
        try:
            hash_result = subprocess.run(
                ["git", "-C", tmpdir, "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=CLI_PROBE_TIMEOUT,
                stdin=subprocess.DEVNULL,
            )
            commit_hash = (
                hash_result.stdout.strip()[:8]
                if hash_result.returncode == 0
                else "unknown"
            )
        except (subprocess.TimeoutExpired, OSError):
            commit_hash = "unknown"

        # Copy evaluators
        src = Path(tmpdir) / "evaluators"
        if not src.exists():
            print("❌ No evaluators directory in library")
            sys.exit(1)

        installed_count = 0
        for provider_dir in src.iterdir():
            if provider_dir.is_dir() and provider_dir.name not in (
                "__pycache__",
                ".git",
            ):
                dest = evaluators_dir / provider_dir.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(provider_dir, dest)
                print(f"  ✅ {provider_dir.name}/")
                installed_count += 1

        # Write version file for tracking
        version_file.write_text(f"{version} ({commit_hash})\n", encoding="utf-8")

    print()
    print("=" * 50)
    print(f"✅ Installed {installed_count} provider(s) from {version} ({commit_hash})")
    print()
    print("List evaluators:  adversarial list-evaluators")
    print()
    print("API keys needed (add to .env):")
    print("  OPENAI_API_KEY   - OpenAI evaluators")
    print("  GOOGLE_API_KEY   - Gemini evaluators")
    print("  MISTRAL_API_KEY  - Mistral evaluators")
