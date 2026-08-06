# KIT-0083: Ship the adversarial CLI, not just its config — install step + doctor PATH check

**Status**: Done
**Priority**: high (the planner's Phase 3 evaluation GATE fails out of the box in every fresh consumer project)
**Type**: Infrastructure
**Estimated Effort**: 3-4 h
**Created**: 2026-08-04
**Source**: GitHub issue #103 (operator-filed, fresh consumer project 2026-08-04)
**Evaluation**: arch-review-fast APPROVED 2026-08-04 after 2 revision rounds (pin-home candidates named + sequencing rule; help-text surfaces made explicit; shared uv-fallback helper). Log: `.adversarial/logs/KIT-0083-ship-adversarial-cli--arch-review-fast.md`

## Overview

The scaffold ships the *config* side of adversarial evaluation —
`.adversarial/config.yml` and the evaluator library — and the doctor
reports it green:

```
DOCTOR:evaluators:PASS:evaluator library installed (5 entries)
```

But nothing installs the `adversarial` CLI itself, and no check verifies
it. The failure is deferred to the worst possible moment: everything looks
provisioned until the planner's Phase 3 GATE actually runs
`adversarial arch-review-fast` and gets `adversarial not found`. The only
copy on the operator's machine was the kit checkout's own
`.venv/bin/adversarial` — which a consumer project shouldn't reach into.

Verified against source (2026-08-04):

- `grep -rn adversarial scripts/optional/setup-dev.sh` → no matches
  (setup-dev.sh creates the project venv/editable install only)
- `scripts/core/doctor.d/30-evaluators.sh` checks only
  `.adversarial/evaluators/` non-emptiness — no `command -v adversarial`
  anywhere in doctor.d
- Field workaround that worked: `uv tool install adversarial-workflow`
  (PyPI; installs 1 executable), after which the global CLI ran correctly
  against the consumer project's own `.adversarial/` config — verified by
  6 arch-review-fast runs writing to `.adversarial/logs/`.

## Requirements

- **F1 — startup install step.** Some startup surface installs the CLI
  (`uv tool install adversarial-workflow`, or equivalent) so a fresh
  project can run its first evaluation without manual surgery.
  **Preferred surface**: extend `project install-evaluators` to ensure
  the CLI alongside the library — one dedicated command owns the whole
  evaluator suite (highest cohesion; it is also the command every doctor
  FAIL message already points at). The door's `--with-evaluators` offer
  then routes to it unchanged in mechanism — but BOTH help surfaces are
  updated to say the offer provisions "evaluator library + CLI": the
  `bootstrap --help` flag description AND `install-evaluators`' own
  usage text, so the broadened behavior is explicit at every entry
  point, not silent (choosing a different surface requires recording
  why in the PR). Constraints:
  - Must work for BOTH shapes. Planning repos have no venv and no
    pyproject (profile `none`), so a global tool install (`uv tool`) is
    the natural mechanism there — do not require a project venv.
  - Non-TTY safe: a flag and/or preset key answers it; skipping must be
    loud (the door's existing "Offer skipped (non-interactive)" pattern).
  - If `uv` is absent, degrade to printing the exact install command —
    never fail the whole install over the optional CLI. Keep this
    check-and-instruct logic in ONE function/script the door and
    `install-evaluators` share; if a second uv-installed tool ever
    appears, it reuses that helper rather than copying the pattern
    (single-use today — do not build a generic installer framework).
- **F2 — doctor check for the binary.** A distinct doctor line (e.g.
  `evaluator-cli`) that FAILs when `.adversarial/` exists but no
  `adversarial` is on PATH (`command -v adversarial` + a cheap
  `adversarial --version` exit-0 probe), so the library PASS can never
  mask a missing binary again. SKIP when `.adversarial/` is absent,
  mirroring 30-evaluators.sh.
- **F3 — pin coherence (#60).** Two different pins exist today and they
  are NOT the same thing:
  - `pyproject.toml:42` → `"adversarial-workflow>=1.0.1"` — the CLI, a
    PyPI distribution
  - `pyproject.toml:91` → `[tool.adversarial] library_version = "v0.10.0"`
    — the evaluator LIBRARY, a git ref consumed by `install-evaluators`
  Issue #60 reports these read as inconsistent (v0.10.0 does not exist on
  PyPI — it is not a PyPI version at all). F1's install step must use
  whatever pin #60 lands on, and the pin must live somewhere BOTH shapes
  can read. This is NOT an open-ended architecture question — two
  shape-independent homes already ship in every scaffold; pick one at
  implementation and record why:
  - `.adversarial/config.yml` — present in both shapes, already owns
    evaluator-suite configuration (natural home; KIT-0079 can use the
    same line for the library ref)
  - the CLAUDE.md kit-install region — flat `key: value` lines the
    consumer engine already writes for both shapes
  `pyproject.toml` is disqualified as the canonical home by the planning
  shape's lack of one (KIT-0079's root cause) — it may carry a mirror for
  Python tooling, but a reader must not require it. **Sequencing
  requirement**: the canonical-home decision (one home for BOTH pins,
  library and CLI) is made and written down FIRST — in this task's PR or
  in KIT-0079's, whichever lands first; the other consumes it. Do not
  implement F3 against a pin location that the sibling task would then
  move.
- **F4 — KIT-0082 hook.** The scaffold acceptance test (KIT-0082, if
  landed first) gains an assertion: fresh scaffold + startup flow →
  doctor's evaluator-cli line is PASS or a loud, actionable SKIP.

## Acceptance Criteria

- [ ] A fresh `--new` project (both shapes) can run
      `adversarial arch-review-fast <spec>` after following only the
      printed startup steps — no reaching into the kit checkout
- [ ] `project doctor` FAILs with an actionable message when the CLI is
      missing but the config/library are present (the #103 trap)
- [ ] Install step honors the #60 pin decision; no surface names a
      version that doesn't exist for its ecosystem
- [ ] Existing doctor tests still pass; new check has test coverage

## Out of Scope

- Resolving #60 itself (which pin scheme is correct) — this task consumes
  its decision; if #60 is still open at implementation time, install
  unpinned-latest with a TODO naming #60
- The evaluator-library pin relocation for planning shape (KIT-0079)
- **`.claude/agents/create-project.md` — do not touch** (operator
  decision 2026-08-05). It carries three contradictions with this
  task's install path (`pipx` at `:180`/`:317`, per-evaluator
  `adversarial library install` at `:214-217`, and an unearned
  `adversarial-workflow: <version> verified` summary at `:260`).
  Fixing them here is tempting and wrong: **KIT-0087 F3 owns that
  file**, and KIT-0078 F2 may fold it away entirely — a deleted file
  carries no contradictions. Patching it here would be churn on a
  surface two other tasks are already holding. Note the contradictions
  in the PR body and move on.

## Related

- Issue #103 (source), #60 (pin inconsistency), KIT-0079 (planning-shape
  library pin), KIT-0082 (acceptance test), KIT-0081 F4 (installer tail
  names GOOGLE_API_KEY instead of GEMINI_API_KEY — same surface, fold in
  if touching the installer output)
