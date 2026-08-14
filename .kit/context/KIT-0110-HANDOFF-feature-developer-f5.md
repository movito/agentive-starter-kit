# KIT-0110: Release tooling + verification — Implementation Handoff

**You are the feature-developer-f5. Implement this task directly. Do
not delegate or spawn other agents.**

**Date**: 2026-08-14
**From**: planner-f5  **To**: feature-developer-f5
**Task**: .kit/tasks/4-in-review/KIT-0110-release-signal-integrity.md
**Status**: Ready
**Evaluation**: arch-review-fast REVISION_SUGGESTED — all 3 findings
dispositioned in the spec header (base retrieval specified;
human-in-loop accepted; schema validation added). Don't re-litigate.
**Target Codebase**: TWO repos — PR 1 in this kit repo (worktree),
PR 2 in `~/Github/agentive-skills` (planner-created branch there)

## Session topology (read before anything else)

- **Session home / PR 1**: worktree
  `/Users/broadcaster_three/Github/ask-worktrees/KIT-0110`, branch
  `feature/KIT-0110-release-tooling` (real venv, planner-provisioned).
  Verify, never create.
- **PR 2**: branch `feature/KIT-0110-plugin-sha256-check` in
  `/Users/broadcaster_three/Github/agentive-skills` — ALSO
  planner-created; operate on it via absolute paths / `git -C` from
  this session (KIT-0109 precedent: that repo has no worktree
  infrastructure). Verify with
  `git -C /Users/broadcaster_three/Github/agentive-skills branch --show-current`
  before any commit there.
- **Sequencing**: PR 1 (tool, kit repo) → PR 2 (column + check,
  marketplace). PR 2's roster edit uses PR 1's tool to compute the
  `plugin_sha256` values — dogfood it; if the tool can't produce them,
  the tool isn't done.

## Verified anchors (2026-08-14 — re-verify before relying)

- `scripts/local/check_plugin_drift.py` — docstring confirms the
  kit-hash-only design ("the sha256 of the KIT source file", lines
  4-12); roster URL constant ~line 40; `load_roster_text` at line 61.
  Read its roster-parsing before writing your own — pattern reuse; the
  resync tool and the drift check must not disagree about the schema
  (evaluator F3).
- `~/Github/agentive-skills/plugins/agentive-workflow/roster.yaml` —
  the live schema your column extends (295 lines at 2.0.4, merged
  `9331e4f`).
- **No `.github/workflows/` exists in agentive-skills** (verified
  today) — PR 2 creates that repo's first CI workflow. Required-check
  enforcement is a GitHub-settings step the OPERATOR does at
  completion; your job ends at the check existing, green on main, and
  falsified once.
- Base retrieval: `kit_sha256` is a CONTENT hash, not a git blob id —
  see the spec's specified mechanism (history walk + hash-match,
  fail-loud on no-match). The KIT-0109 session did this by hand; your
  fixture test recreates a mini repo with history.

## Test approach

- Kit PR: pytest for the tool — roster parsing, base discovery
  (fixture repo), three-way merge happy path, conflict-surfaced path
  (the spec's falsification), base-not-found fail-loud, column
  emission. `ci-check.sh` before push; evaluator before PR opens
  (code-shaped diff → normal tier, not the prose exception).
- Marketplace PR: the check runs green on current 2.0.4 state;
  falsify once (bump a hash without the body → red); schema-invalid
  roster → its own loud failure. CodeRabbit reviews there (verified
  #4/#5/#9); BugBot unverified.
- Cross-check: after PR 2, run the kit-side drift guard
  (`workflow_dispatch`) — it must STAY green (your column is additive;
  if the guard chokes on the new column, its parser was schema-fragile
  and that's a real finding to fix kit-side).

## Out of scope — do not touch

- Plugin body content (canon or copies) — this task ships tooling and
  metadata, zero content changes.
- KIT-0111 (version-bump guard), KIT-0112 (thread counting) — split
  siblings, their own tasks.
- The KIT-0105 release itself — this task ends with tooling ready for
  that train.
- Gaps → `.kit/tasks/1-backlog/` (you're kit-side for PR 1; for PR 2
  findings, the KIT-0109 followups-file pattern via the planner).

## Process citations

- Review-surface budget per PR (PR-SIZE-WORKFLOW); circuit breaker
  (bot-triage). Two PRs are the plan; either blowing the budget →
  STOP and report.
- Packaged-twin rule does NOT bite here (no door-data files in
  scope) — but `test_door_data_sync.py` staying green is still part
  of `ci-check.sh`.
