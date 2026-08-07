# KIT-0091: Port the bash gate surfaces into agentive-kit — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-07
**From**: planner-f5
**To**: feature-developer (f5 variant recommended — rewrite with parity contracts)
**Task**: `.kit/tasks/3-in-progress/KIT-0091-port-gate-scripts.md`
**Status**: Ready — phase 1b; agentive-kit 0.1.0 is live, this completes phase 1's module list
**Evaluation**: arch-review-fast APPROVED 2026-08-07, round 2 —
`.adversarial/logs/KIT-0091-port-gate-scripts--arch-review-fast.md`
(dispositions in the spec header: `ghio` accepted; parity binds
behavior, not code shape)

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode
(the repo split, not your working directory — see Session topology).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0091`, branch
  `feature/KIT-0091-port-gate-scripts` — created and provisioned by the
  planner; task file already `3-in-progress`
- VERIFY, never create: `git branch --show-current` must show the
  branch above before your first edit; if not, STOP and ask
- Likely 2 PRs (preflight+ghio; review-input+worktree lib) — stacked
  branches per STACKED-PR-WORKFLOW.md. Note its NEW sections (2026-08-07):
  stacked PRs now trigger `pull_request` CI natively (the base-branch
  filter is gone — expect real runs, no dispatch ritual unless the
  #105/#108 residual flake appears, in which case dispatch AND report
  it); force-push fallback = relay the exact command to the operator
  via `!` prefix; narrow-refspec explicit-lease pattern documented
- `project move` on a branch now SKIPS agent-handoffs.json (the
  KIT-0086 guard shipped in 0.1.0) — no manual reverts needed

---

## Mission

Port the three deferred bash surfaces (~1,760 lines, recounted below)
into `agentive-kit` as `preflight`, `review_input`, and `worktree`
modules, plus the `ghio` module for all GitHub interactions. These are
GATE surfaces — parity is proven by captured behavior matrices, not
asserted. Release as 0.2.x. Spec F1–F5 is authoritative.

## Verified anchors (2026-08-07 — re-grep before relying)

- **Package layout** (differs from the KIT-0090 spec's original
  `src/` sketch — this is what actually shipped):
  `packages/agentive-kit/src/agentive_kit/` with `cli.py`, `doctor/`,
  `evaluators.py`, `gitio.py`, `lifecycle.py`, `models.py`, `root.py`;
  tests under `tests/agentive_kit/`; version single-sourced from
  `agentive_kit.__version__` (dynamic, per CodeRabbit PR #108);
  console script `agentive`; publish via
  `.github/workflows/publish-agentive-kit.yml` on `agentive-kit-v*`
  tags (trusted publishing).
- **Surfaces to port** (wc -l, 2026-08-07):
  - `scripts/core/preflight-check.sh` — 678 lines, the 7-gate
    completion check (23 "Gate" mentions). Gate 1's at-cap semantics:
    see REVIEW-INSIGHTS "Preflight Gate 1 at-cap semantics (since
    PR #75)" — at-cap reports PENDING, never PASS; that behavior is
    part of the parity matrix, cite it, don't re-derive it.
  - `scripts/core/prepare-review-input.sh` — 492 lines (cross-repo
    aware, `--repo`-routed) + `scripts/core/gh-review-helper.sh` —
    296 lines (its `gh` companion; port the pair together into
    `review_input` + `ghio`).
  - `scripts/local/new-worktree.sh` — 295 lines; port the LIBRARY half
    (primary-root resolution, provisioning list, Serena config
    generation) into `worktree`; the entry script becomes a thin
    delegator and STAYS in scripts/local (door surface, phase 2).
- **Totals**: 1,761 lines measured vs "~1,370" in the retro — the
  delta is `gh-review-helper.sh`, which the retro's figure excluded;
  the port includes it (source: this file's wc -l output, not either
  summary).

## Environmental claims — sources, not restatements

- Suite state: fully green on main at `ad70ef6` — treat any failure as
  REAL (source: KIT-0090 PR series, 1,033 passing at #111's merge)
- Preflight Gate 1 at-cap: REVIEW-INSIGHTS entry (KIT-0043) — parity
  matrix input, verify against the bash before porting
- Fast-hook blind spot: TESTING-WORKFLOW §Full-suite rule — your F3
  shims are delegation changes; the full-suite rule applies to every
  PR here

## Test approach

- **F2 parity matrices FIRST**: for each surface, run the bash
  original against a fixture matrix (per-gate pass/fail/edge for
  preflight; representative PR shapes for review-input incl. cross-repo;
  provisioning outcomes for worktree) and COMMIT the captured matrix
  before writing Python. The port reproduces the matrix; divergences
  are documented improvements only.
- `ghio` gets stub-`gh` fixtures mirroring the stub-git pattern; PATH +
  `GIT_*` isolation per tests/conftest.py discipline.
- Every guard-test broken once (house rule). Full suite before every
  push (delegation changes — TESTING-WORKFLOW rule).
- Evaluator trio BEFORE each PR opens, with per-PR disposition tables;
  deep rounds capped ~2 (code-review-evaluator SKILL §Oscillation
  protocol — this procedure was named from your predecessor's series).

## Out of scope — do not touch

- Phase 2 surfaces: `scripts/local/bootstrap`, engines,
  `new-worktree.sh`'s ENTRY script beyond thin delegation
- `wait-for-bots.sh` / `check-bots.sh` — port only if trivially
  absorbed by `review_input`; otherwise note for phase 2
- Sync machinery (`.core-manifest.json`, `sync_from_manifest.py`) —
  phase 4
- Behavior improvements beyond documented parity divergences

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0091-port-gate-scripts.md`
**Evaluation Log**: `.adversarial/logs/KIT-0091-port-gate-scripts--arch-review-fast.md`
**ADR**: `.kit/adr/KIT-ADR-0028-versioned-packages-not-file-copies.md` (Accepted; this is phase 1b)
