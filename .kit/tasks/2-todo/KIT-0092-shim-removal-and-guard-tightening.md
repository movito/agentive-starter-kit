# KIT-0092: 0.3.x shim removal + preset-guard retightening

**Status**: Todo
**Priority**: high (PROMOTED 2026-08-08, KIT-0093 retro #2: the "one release" promise window is open — schedule as agentive-kit **0.3.1** promptly)

> **Scope update (2026-08-08)**: **Part B is DONE** — shipped inside
> KIT-0093 PR #116, where the old probe became blocking (break-once
> proof in that PR body). Remaining scope: **Part A** (shim removal)
> + **Part C** (monolith test shrinkage), released together as 0.3.1.
**Type**: Infrastructure / cleanup
**Estimated Effort**: 0.5 day
**Created**: 2026-08-08
**Source**: KIT-0091 retro (Should Change #1 and #2); the "one release" deprecation promise needs a named home so it cannot drift
**Evaluation**: skipped (planner) — enumerated cleanup with decisions in-spec

## Part A — remove the one-release deprecation shims (0.3.x)

The 0.2.0 release left four delegator shims whose bodies die together
in the next minor (the file list IS the requirement — no discovery
needed):

- `scripts/core/preflight-check.sh`
- `scripts/core/prepare-review-input.sh`
- `scripts/core/gh-review-helper.sh`
- (`scripts/local/new-worktree.sh` STAYS as a thin delegator — door
  surface, phase 2 decides its fate)

Also dying with them: the declined loader-dedup thread from PR #113
(the duplication exists only while the shims do — removing them
resolves it by deletion; note that closure in the PR body). Sweep
callers first: skills/commands/docs that invoke the `.sh` paths move
to `agentive preflight` / `review-input` / `review-helper`.

## Part B — retighten `TestPresetNeverDistributed` (unblocked now)

The guard probes the literal string "agentive-kit", conflating the
config-home LOCATION (`agentive-config` — what it actually guards)
with the package NAME. Every package shim trips it, so ALLOWED grew to
7 entries for the wrong reason (KIT-0090 set the precedent,
KIT-0091 added four). Fix: probe `agentive-config` only; shrink
ALLOWED back to the three genuine config-home readers; the guard's
original meaning is restored and shim entries become unnecessary
regardless of Part A's timing.

## Part C — monolith test shrinkage (folded from KIT-0089, 2026-08-08)

The legacy test monoliths grew during the extraction because they carry
the shim-contract tests (`test_project_script.py` 2,006 lines,
`test_doctor.py` 2,638 as of 2026-08-08). When Part A removes the shim
bodies, their contract tests and the legacy-path coverage they exercise
die too — the monoliths must SHRINK in the same PR, with the remaining
(genuinely still-relevant) cases either deleted with the shims or moved
beside the package modules they actually test. Record before/after line
counts in the PR body.

## Acceptance Criteria

- [ ] Part B: probe distinguishes location from package name; ALLOWED
      back to 3; guard broken once to prove it still fires
- [ ] Part A: four shim bodies removed at 0.3.x; no live surface
      invokes the `.sh` paths (grep-proven in the PR body);
      loader-dedup decline closed by deletion
- [ ] Released as part of agentive-kit 0.3.x with a CHANGELOG note

## Out of Scope

- `scripts/core/project` shim retirement — its one-release clock is
  tied to phase 2's door switch, not this task
- `new-worktree.sh` (phase 2)
