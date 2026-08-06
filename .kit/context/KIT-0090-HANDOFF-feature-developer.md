# KIT-0090: Extract the lifecycle scripts into the agentive-kit package — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-06
**From**: planner-f5
**To**: feature-developer (f5 variant recommended — multi-PR, sustained)
**Task**: `.kit/tasks/3-in-progress/KIT-0090-extract-scripts-package.md`
**Status**: Ready — ADR-0028 Accepted; this is migration phase 1 and the only active work item
**Evaluation**: arch-review-fast APPROVED 2026-08-06, round 2 —
`.adversarial/logs/KIT-0090-extract-scripts-package--arch-review-fast.md`
(round-1 findings and their dispositions are recorded in the spec header)

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode
(describes the planning/code split, not your working directory — see
Session topology).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0090`, branch
  `feature/KIT-0090-extract-scripts-package` — created and provisioned
  by the planner (venv real, `.env` + `.adversarial/evaluators`
  symlinked read-only, task file already `3-in-progress`)
- VERIFY, never create: `git branch --show-current` must show the
  branch above before your first edit; if not, STOP and ask
- This task spans MULTIPLE PRs (spec §PR Plan). The worktree/branch
  above is for PR 1; create subsequent stacked branches per
  `STACKED-PR-WORKFLOW.md`. `gh pr create` needs `--head <branch>` from
  any worktree (WORKTREE-WORKFLOW.md triage entry)
- Never edit `agent-handoffs.json` on a branch; note `project move`
  auto-edits it — revert that hunk if it happens (KIT-0086 carve-out,
  recorded in that spec's header)

---

## Mission

Extract `scripts/core/` into a `src/agentive_kit/` Python package with
a console CLI, published to PyPI, consumed by this repo through a
one-release shim. Spec F1–F6 is authoritative; this handoff maps it to
code. This is ADR-0028 phase 1: the step that ends copy-distribution
for scripts and gives the code a maintainable shape (module split +
per-module tests — KIT-0089 F3 closes by reference here).

## Verified anchors (2026-08-06 — re-grep before relying)

- `scripts/core/project` is **2,822 lines**. Root resolution is
  file-location based: `Path(__file__).resolve().parent.parent.parent`
  at `:843` and `:2337` (plus pyproject lookups `:44`, `:144`).
  **F2 replaces this with CWD-walk discovery** — walk up from CWD to a
  directory whose CLAUDE.md carries the kit-install region
  (`<!-- BEGIN KIT-LOCAL: kit-install -->`, written by
  `engine-consumer.sh`); refuse with a clear message when no marker is
  found. This is the highest-risk change — test nested dirs, worktrees,
  split-pair planning repos, and non-kit dirs explicitly.
- Doctor driver at `project:1939` (`cmd doctor`): runs every executable
  in `scripts/core/doctor.d/` (12 checks today, incl. `15-git-version`
  and `31-evaluator-cli` from KIT-0080/0083); exit contract documented
  at `:1953`. Per-check migration decisions (Python module vs shell
  kept under a driver) are yours per F1 — record each.
- `cmd_install_evaluators` at `:799` (library git-clone + CLI ensure —
  the KIT-0083 shape); `_sync_coordination_metadata` at `:144` (gets
  the KIT-0086 skip-when-not-on-main guard IN the extracted module, F6);
  `_get_evaluator_library_version` at `:845` area (gets the KIT-0079
  config.yml reader, F6 — then DELETE `test_library_pin_mirrors_agree`).
- Portable git resolution (KIT-0080, PR #107) now lives inline in each
  script — consolidate into `gitio` (F1). Keep the 2.30 floor and the
  stub-git fixtures; they migrate with their modules.
- Package name `agentive-kit`: PyPI HTTP 404 (available) verified
  2026-08-06; bare `agentive` HTTP 200 (taken) — check that dist's
  entry points before naming the console script `agentive`; fallback
  `akit`.

## Environmental claims — sources, not restatements

- Git floor / portability constraints: spec KIT-0080 §Update 2026-08-05
  and README §Requirements (do not re-derive)
- Test-suite state: KIT-0080 retro §scorecard — suite fully green; any
  failure you see is REAL
- Fix-recipe caution: the KIT-0083 one-liner precedent was verified on
  the happy path only (KIT-0080 retro §What Should Change #3) — when
  you move resolvers into `gitio`, port PR #107's failure-path tests
  (`cd ""`, non-repo), not just the code

## Test approach

- **Behavior first**: the existing suite is the spec. PR 1 gate: full
  suite green against the package with the shim in place, BEFORE any
  behavior change. Per-module test files split as modules extract
  (monolith test files shrink PR by PR; KIT-0089's shrink-only
  intuition applies even though its lint isn't built).
- New surface (CWD-walk discovery): dedicated tests incl. refusal
  outside a kit repo. For every new guard-test: break the condition
  once, watch it fail (house rule since KIT-0083).
- `./scripts/core/ci-check.sh` per PR; CI green on GitHub per PR; bots
  + evaluator + preflight gates per PR as usual.

## Out of scope — do not touch

- Phases 2–4 (door switch, consumer migration, sync-machinery
  retirement) — `scripts/.core-manifest.json` and
  `sync_from_manifest.py` stay EXACTLY as they are this phase
- Evaluator execution (adversarial-workflow's job — spec §Out of Scope
  boundary statement), Linear sync behavior, plugin channel
- `scripts/local/` (bootstrap + engines) — the door is phase 2; only
  `scripts/core/` extracts now. `new-worktree.sh` is `scripts/local/`
  — it stays put this phase even though `worktree` logic is listed in
  F1: extract the LIBRARY half (resolution, provisioning list) and
  leave the entry script delegating; note it for phase 2.

## PR plan (from the spec — refine in PR 1's description)

1. Package skeleton + `gitio` + `lifecycle` + typed models + shim
2. Doctor driver + checks migration
3. Evaluators (+F6 closures) / preflight / review-input / worktree lib
4. Publish workflow + README Requirements row + dogfood switch

Each PR independently green and shippable. If sequencing pressure
appears mid-flight, raise it — do not silently merge phases.

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0090-extract-scripts-package.md`
**Evaluation Log**: `.adversarial/logs/KIT-0090-extract-scripts-package--arch-review-fast.md`
**ADR**: `.kit/adr/KIT-ADR-0028-versioned-packages-not-file-copies.md` (Accepted)
