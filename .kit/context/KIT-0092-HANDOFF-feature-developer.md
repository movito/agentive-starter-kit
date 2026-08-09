# KIT-0092: Shim removal + monolith test shrinkage (0.3.1) — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-08
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/3-in-progress/KIT-0092-shim-removal-and-guard-tightening.md`
**Status**: Ready — the 0.3.x "one release" promise window; likely a single PR
**Evaluation**: skipped (planner) — enumerated cleanup, decisions in-spec;
the file list IS the requirement

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode
(the repo split, not your working directory — see Session topology).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0092`, branch
  `feature/KIT-0092-shim-removal` — created and provisioned by the
  planner; task file already `3-in-progress`
- VERIFY, never create: `git branch --show-current` must show the
  branch above before your first edit; if not, STOP and ask
- Single PR expected; if it splits, stacked per STACKED-PR-WORKFLOW
  (branch-verify before every fix commit — the rule your predecessor's
  incident wrote)

---

## Mission

Remove the three one-release deprecation shim bodies, sweep their
callers to the `agentive` CLI, shrink the monolith test files that
existed to test them, and release as **agentive-kit 0.3.1**. Spec
Parts A + C are the scope. **Part B is DONE** — verified 2026-08-08:
`TestPresetNeverDistributed.ALLOWED` is back to exactly 3 config-home
readers and the probe matches `agentive-config` only (shipped in
KIT-0093 PR #116, break-once proof in that PR body). Do not redo it.

## Part A — the removals (verified state, 2026-08-08)

The three shims, already thin delegators:

- `scripts/core/preflight-check.sh` — 76 lines
- `scripts/core/prepare-review-input.sh` — 65 lines
- `scripts/core/gh-review-helper.sh` — 65 lines

`scripts/local/new-worktree.sh` STAYS (delegator; its fate belongs to
phase 3+, per KIT-0093's decision table). `scripts/core/project` STAYS
(its one-release clock started at the 0.3.0 door switch — retirement is
a phase 3 question; spec Out of Scope).

**Caller sweep before deletion** — 8 files in `.claude/` reference the
`.sh` paths (grep hits, 2026-08-08): `commands/babysit-pr.md`,
`commands/triage-threads.md`, `commands/commit-push-pr.md`,
`commands/preflight.md`, `skills/bot-triage/SKILL.md`,
`skills/self-review/SKILL.md`, `skills/pre-implementation/SKILL.md`,
`skills/code-review-evaluator/SKILL.md`. Also sweep
`.kit/context/workflows/` and any doc naming the paths. Replacements:
`agentive preflight` / `agentive review-input` / `agentive
review-helper`. Re-grep for the full set — the 8 is a snapshot. The
final grep proving zero live references goes in the PR body.

**Dies with the shims**: the loader-dedup thread declined on PR #113 —
the duplication exists only while the shims do; note the
closed-by-deletion in the PR body.

## Part C — monolith test shrinkage (baseline, 2026-08-08)

| File | Lines now | What shrinks |
|---|---|---|
| `tests/test_preflight_check.py` | 1,215 | the bash half of the implementation-parameterized matrix dies with the bash; keep the python parameterization (it pins the package) |
| `tests/test_prepare_review_input.py` | 388 | same shape |
| `tests/test_project_script.py` | 2,006 | shim-contract cases for the three removed scripts go; `project`-shim cases STAY (that shim survives) |
| `tests/test_doctor.py` | 2,645 | any case that exercises the removed shims' paths goes; the doctor's own coverage stays |

Judgment rule: a test dies with the shim it tests; a test that pins
PACKAGE behavior moves beside the package tests
(`tests/agentive_kit/`) or stays if already keyed to the CLI. Record
before/after line counts in the PR body (spec Part C requirement).
Do NOT chase a target number — the requirement is that nothing tests
deleted code, not that a count is hit.

## Release

Version bump to 0.3.1 (single-sourced `agentive_kit.__version__`), tag
`agentive-kit-v0.3.1`, existing publish workflow. CHANGELOG note names
the removed scripts and their replacements (spec AC).

**Optional passenger — planner note**: KIT-0074 (stacked-PR tooling:
review-input base awareness + preflight Gate 1 honesty) is a natural
0.3.1 passenger now that both surfaces live in the package. It is NOT
in scope unless the operator says so mid-flight — if they do, its spec
is in `1-backlog/`; otherwise ignore this note.

## Test approach

- Full suite before every push (removals are delegation-surface
  changes — TESTING-WORKFLOW rule); the door-E2E and entrance-shim
  slow suites must run (they exercise scaffold + shim paths).
- The caller sweep is doc-text — but `/preflight` and the review flow
  must be exercised once post-sweep (dogfood: run `agentive preflight`
  through the updated command doc's instructions).
- Evaluator trio before PR open; disposition table; deep rounds ≤2.
- bash 3.2 rule applies if you touch engine heredocs (patterns.yml
  `bash32_heredoc_apostrophes` — new this week).

## Out of scope — do not touch

- `scripts/core/project` shim, `scripts/local/new-worktree.sh`,
  `scripts/local/` engines (phase 3)
- Part B (done), `ci-check.sh` (its dormant find/set-e fix is recorded
  in KIT-0052's disposition if you happen to touch the file — only
  then)
- Sync machinery (phase 4), plugin content, Linear sync

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0092-shim-removal-and-guard-tightening.md`
**Folded content**: Part C carries archived KIT-0089's intent (see its disposition)
**ADR**: `.kit/adr/KIT-ADR-0028-versioned-packages-not-file-copies.md` (phase 1's deprecation promise, kept)
