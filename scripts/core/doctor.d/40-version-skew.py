#!/usr/bin/env python3
"""doctor check: venv-vs-system version skew for packages that bit us.

Incidents:
- adversarial-workflow (KIT-0044): the venv carried aider-era 0.9.7,
  which MUTATED the working tree during reviews, while the system had
  moved on — the skew went undetected until a review run applied its
  own edit.
- black vs the pyproject.toml pin (KIT-0032): a stale venv Black
  produced a phantom CI formatting failure. Generalizes the KIT-0035 F1
  ci-check warning into a standing check.

isort is deliberately NOT checked: its pin is a floor (>=), not exact,
so "active vs pinned" comparison is meaningless (REVIEW-INSIGHTS,
KIT-0035).

Read-only. Root from DOCTOR_ROOT (driver-set; tests point it at tmp
fixtures with stub executables), else derived from this file's
location. The system-side pip probe uses `pip3` from PATH so tests can
stub it (stub-gh harness pattern).

Emits two lines: venv-skew-adversarial and black-pin.
"""

import os
import re
import shutil
import subprocess  # nosec - fixed argv, no shell
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:  # Python 3.10
    tomllib = None

SKEW_PACKAGE = "adversarial-workflow"


def pip_version(pip_cmd, package):
    """Return the version `pip show` reports, or None if unavailable."""
    try:
        result = subprocess.run(
            [pip_cmd, "show", package],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("Version:"):
            return line.partition(":")[2].strip()
    return None


def black_pin(root):
    """Return the exact black pin from pyproject.toml, or None."""
    pyproject = root / "pyproject.toml"
    if not pyproject.exists() or tomllib is None:
        return None
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return None
    project = data.get("project", {})
    dep_lists = [project.get("dependencies", [])]
    dep_lists.extend(project.get("optional-dependencies", {}).values())
    for deps in dep_lists:
        for dep in deps:
            match = re.match(r"black\s*==\s*([0-9][0-9a-zA-Z.]*)$", dep.strip())
            if match:
                return match.group(1)
    return None


def active_black_version(root):
    """Version of the black the project actually runs (venv first)."""
    candidates = [str(root / ".venv" / "bin" / "black")]
    path_black = shutil.which("black")
    if path_black:
        candidates.append(path_black)
    for black_cmd in candidates:
        if not Path(black_cmd).exists():
            continue
        try:
            result = subprocess.run(
                [black_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        match = re.search(r"(\d+\.\d+(?:\.\d+)?[a-z0-9]*)", result.stdout)
        if match:
            return match.group(1)
    return None


def main():
    root = Path(os.environ.get("DOCTOR_ROOT") or Path(__file__).resolve().parents[3])

    # --- adversarial-workflow: venv vs system ---
    venv_pip = root / ".venv" / "bin" / "pip"
    venv_ver = pip_version(str(venv_pip), SKEW_PACKAGE) if venv_pip.exists() else None
    system_pip = shutil.which("pip3")
    system_ver = pip_version(system_pip, SKEW_PACKAGE) if system_pip else None

    if venv_ver is None and system_ver is None:
        print(
            f"DOCTOR:venv-skew-adversarial:SKIP:{SKEW_PACKAGE} not installed "
            "in venv or system"
        )
    elif venv_ver is None or system_ver is None:
        where = "venv" if venv_ver is None else "system"
        print(
            f"DOCTOR:venv-skew-adversarial:SKIP:{SKEW_PACKAGE} only installed "
            f"on one side ({where} has none) — no comparison possible"
        )
    elif venv_ver == system_ver:
        print(
            f"DOCTOR:venv-skew-adversarial:PASS:{SKEW_PACKAGE} {venv_ver} "
            "matches in venv and system"
        )
    else:
        print(
            f"DOCTOR:venv-skew-adversarial:FAIL:{SKEW_PACKAGE} skew — venv "
            f"{venv_ver} vs system {system_ver} (the KIT-0044 mutation class)"
        )

    # --- black vs pyproject pin ---
    pin = black_pin(root)
    if pin is None:
        print("DOCTOR:black-pin:SKIP:no exact black pin found in pyproject.toml")
        return 0
    active = active_black_version(root)
    if active is None:
        print(f"DOCTOR:black-pin:FAIL:black not runnable but pyproject pins {pin}")
    elif active == pin:
        print(f"DOCTOR:black-pin:PASS:active black {active} matches pyproject pin")
    else:
        print(
            f"DOCTOR:black-pin:FAIL:active black {active} != pyproject pin {pin} "
            "(phantom-CI-failure class, KIT-0032)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
