# KIT-0095: Package + doctor hygiene riders (next agentive-kit release)

**Status**: Backlog
**Priority**: low (riders — ship with whatever cuts the next
agentive-kit release: KIT-0074, phase 3, or a standalone 0.3.2)
**Type**: Infrastructure / hygiene
**Estimated Effort**: 1-2 h combined
**Created**: 2026-08-08
**Source**: KIT-0092 retro (incident closures + process actions)
**Evaluation**: skipped (planner) — two enumerated fixes with their
investigations already done

Two small fixes that both live in released code, bundled so neither
needs its own ceremony:

## R1 — remove the `ADVERSARIAL_UNATTENDED=1` hint from `agentive review-input`

The ported review-input's "Next steps" output still advertises
`ADVERSARIAL_UNATTENDED=1`, an env flag that has never existed in the
installed adversarial-workflow (the KIT-0044 incident, re-observed in
KIT-0092). Replace with the verified `echo y |` pattern — and per
self-review lesson #10's new triage note, verify against the ACTUAL
installed tool (`command -v adversarial` → follow it; a repo-venv grep
false-negatives on uv-installed CLIs).

## R2 — `doctor.d/55-worktree-provisioning.sh`: worktree-hookpath concern

Extend the worktree-provisioning check (which already houses the
KIT-0065/KIT-0044 venv incidents) with a hookpath concern: WARN when a
worktree's environment would give git hooks no usable pytest (the
KIT-0092 session hit the pre-commit "missing binary" state; the hook
itself now distinguishes missing-binary from test-failure — this is
the doctor-side early warning). Cite the incident in the check header;
keep it portable (BSD userland).

## Acceptance Criteria

- [ ] R1: no shipped output names `ADVERSARIAL_UNATTENDED`; the
      replacement hint verified against the installed tool
- [ ] R2: the WARN fires in a worktree with no venv/pytest and stays
      quiet in a provisioned one (both directions tested — break-once
      rule)
- [ ] Ships in a tagged agentive-kit release with a CHANGELOG line
