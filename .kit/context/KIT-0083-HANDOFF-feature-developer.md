# KIT-0083: Ship the adversarial CLI — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-04
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/2-todo/KIT-0083-ship-adversarial-cli.md`
**Status**: Ready for implementation — AFTER KIT-0084 (same surfaces; land sequentially, not in parallel)
**Evaluation**: arch-review-fast APPROVED after 2 revision rounds —
`.adversarial/logs/KIT-0083-ship-adversarial-cli--arch-review-fast.md`

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode.

---

## Mission

`.adversarial/` config + evaluator library ship and pass doctor, but the
`adversarial` CLI binary is never installed and never checked — so the
planner's Phase 3 gate fails on first use in every fresh project. Install
the CLI as part of startup; add a doctor line that can't be masked by the
library's PASS. Full requirements F1–F4 in the spec; anchors below
verified 2026-08-04.

## Where each requirement lands

- **F1 (install step; preferred surface = `install-evaluators`)** —
  `scripts/core/project:799` `cmd_install_evaluators()`: today it
  git-clones the evaluator LIBRARY by ref (`--ref` flag parsing at
  `:804-812`, works without pyproject — planning shape, KIT-0068;
  `_get_evaluator_library_version()` at `:845` reads the pyproject pin).
  Extend it to also ensure the CLI: `command -v adversarial` → if absent
  and `uv` present, `uv tool install adversarial-workflow` (pin per F3);
  if `uv` absent, print the exact command and continue (the existing
  git-missing block at `:815-822` is the degradation pattern to mirror —
  one shared check-and-instruct helper, no duplication).
  Door side: the `--with-evaluators` offer (`bootstrap:594-602` prompt/
  skip-notice, `:691-692` flag parse, `:822` preset consumption) routes
  to `install-evaluators` unchanged in mechanism. Update BOTH help
  surfaces to say "evaluator library + CLI": the flag description around
  `bootstrap:53` and the usage line at `project:2512`.
- **F2 (doctor check)** — new file `scripts/core/doctor.d/` (name it to
  sort near `30-evaluators.sh`, e.g. `31-evaluator-cli.sh`): SKIP when
  `.adversarial/` absent (mirror `30-evaluators.sh:17-18`), FAIL when
  `.adversarial/` exists but `command -v adversarial` fails or
  `adversarial --version` exits non-zero, with the fix command in the
  message. Keep output to the `DOCTOR:<name>:<VERDICT>:<msg>` contract.
  Note: `adversarial --version` currently prints "Unknown fields in
  evaluator.yml" warnings to stderr on this machine — probe exit code,
  don't parse output.
- **F3 (pin coherence — SEQUENCING GATE)** — two pins exist:
  `pyproject.toml:42` (`adversarial-workflow>=1.0.1`, PyPI CLI) and
  `pyproject.toml:91` (`[tool.adversarial] library_version = "v0.10.0"`,
  library git ref). Per the spec: the canonical shape-independent home
  for BOTH pins is decided FIRST — in this PR or KIT-0079's, whichever
  lands first (candidates: `.adversarial/config.yml` or the CLAUDE.md
  kit-install region). If #60 is still open when you get here, install
  unpinned-latest with a `TODO(#60)` comment and say so in the PR body.
  Check #60 and KIT-0079 state before writing code.
- **F4 (KIT-0082 hook)** — only if KIT-0082's acceptance test has landed
  by then: add the evaluator-cli assertion. Otherwise note it in the PR
  body for KIT-0082 to pick up.

## Data-shape verification

- Doctor driver: check how `scripts/core/preflight-check.sh` /
  `project doctor` aggregate `doctor.d/*` exit codes before adding a new
  check — match the existing scripts' exit discipline (see how
  30-evaluators.sh terminates each path).
- `uv tool install` puts binaries in `~/.local/bin` — the doctor FAIL
  message should mention PATH if `command -v` misses right after an
  apparently-successful install.

## Test approach

- Doctor check: new cases in `tests/test_doctor.py` following existing
  fixtures (present-config/missing-binary → FAIL; no `.adversarial/` →
  SKIP; binary present → PASS via a stub `adversarial` on PATH).
- `install-evaluators`: extend its existing tests (grep tests/ for
  install_evaluators) with a stubbed `uv`/`command -v` path — do NOT
  hit the network or actually install in tests.
- Known local red herring: 8 test_doctor.py failures on Apple git 2.30.1
  (KIT-0080) are pre-existing; CI is the gate.
- `./scripts/core/ci-check.sh` before push; verify CI on GitHub.

## Out of scope — do not touch

- Resolving #60 itself (consume its decision or TODO it)
- KIT-0079's library-pin relocation (coordinate the home decision only)
- KIT-0080 (git 2.30.1), KIT-0084's .env work (should already be merged)
- While in the installer output: KIT-0081 F4 notes its tail says
  `GOOGLE_API_KEY` where the kit standard is `GEMINI_API_KEY`
  (`.env.template:110`, `20-env-keys.py:31`) — fix in passing ONLY if
  you're already editing that print block; otherwise leave for KIT-0081.

## Evaluation summary

APPROVED (round 3) after: pin-home candidates named + first-lander
sequencing rule (round-2 COUPLING finding); both help surfaces made
explicit (round-2 API finding); shared uv-fallback helper, no framework
(round-1 STRUCTURAL_RISK finding). No outstanding concerns.

---

**Task File**: `.kit/tasks/2-todo/KIT-0083-ship-adversarial-cli.md`
**Evaluation Log**: `.adversarial/logs/KIT-0083-ship-adversarial-cli--arch-review-fast.md`
**Source Issue**: movito/agentive-starter-kit#103 — comment there when the PR opens
