# KIT-0045: Provision CROSS_REPO_TOKEN and re-enable core-scripts push sync

**Status**: Backlog
**Priority**: low (rises to high when the downstream phase starts)
**Assigned To**: unassigned (step 1–2 are operator-only)
**Estimated Effort**: 30 minutes + PR-tending commitment
**Created**: 2026-07-14
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: KIT-0036 (built the sync engine this workflow wraps),
KIT-0026 (peer-repo sync channel), KIT-ADR-0022/0026 (sync ownership /
pull-based consumer sync)

## Overview

`.github/workflows/sync-core-scripts.yml` never had a green run — 22/22
failures from 2026-03-09 to 2026-07-13 — because the `CROSS_REPO_TOKEN`
secret referenced at target-checkout and PR-create was never created.
On 2026-07-14 the push trigger was parked (workflow_dispatch kept) to
stop the guaranteed-red runs, consistent with the operator's
stabilize-the-kit-first deferral. This task is the deliberate
re-enablement when the downstream/peer-sync phase begins.

## Requirements

1. **Operator: mint a fine-grained PAT** (owner `movito`) scoped to
   exactly `dispatch-kit`, `adversarial-workflow`,
   `adversarial-evaluator-library`. Permissions: Contents RW,
   Pull requests RW, Metadata R. Set a calendar reminder for the
   expiry date.
2. **Operator: set the secret** in agentive-starter-kit:
   `gh secret set CROSS_REPO_TOKEN` — paste the value locally, never
   through an agent transcript.
3. **Verify with one leg**:
   `gh workflow run "Sync Core Scripts to Downstream" -f repo=movito/dispatch-kit`,
   confirm green and inspect the opened PR in dispatch-kit.
4. **Restore the push trigger** from git history (the 2026-07-14 parking
   commit has the full `on: push:` block) and remove the PARKED comment.
5. **Confirm the tending plan**: every core-scripts change on main will
   open PRs in all three peer repos — name who/what reviews them (the
   upgrader agent flow is the likely candidate).

## Acceptance Criteria

- [ ] Secret exists (`gh secret list` shows CROSS_REPO_TOKEN)
- [ ] One dispatch leg verified green with a real PR opened and reviewed
- [ ] Push trigger restored; PARKED comment removed
- [ ] First push-triggered run green on all three legs (fail-fast is off)
- [ ] PR-tending owner named in this task before closing

## Notes

- Source: tool-call/CI failure analysis session, 2026-07-14. Workflow
  parked in the same session's commit.
- The token-absence failure mode is silent-ish: checkout reports
  "Input required and not supplied: token", and (pre-fix) fail-fast
  cancelled sibling legs, masking scope. `fail-fast: false` is already
  in place.
