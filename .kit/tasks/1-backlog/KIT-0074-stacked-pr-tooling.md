# KIT-0074: Stacked-PR tooling — review-input base awareness + Gate 1 honesty

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-28
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0067 retro (Should Change #1/#2, Process Actions 1/2)
**Related**: KIT-0062 (bot signals), STACKED-PR-WORKFLOW.md (the
doc recipe this automates)

## Overview

Two tooling gaps the KIT-0067 stacked pair paid for by hand:

- `prepare-review-input.sh --format full` against main re-included
  ALL of PR 1 plus every archived file's moved text (966KB input);
  hand-scoping to `--base <stack-parent> --format diff` cut it to
  246KB.
- Preflight Gate 1 reported "no CI runs registered" on the stacked
  PR — true but mystifying; the real condition was "stacked on a
  non-default base; CI runs on retarget".

## Requirements

- **F1**: `prepare-review-input.sh` gains `--base <ref>`, defaulting
  to the PR's actual base branch when that base is not the default
  branch (read via `gh pr view --json baseRefName`); document the
  diff-only hallucination trade-off in its help text.
- **F2**: input size guard — warn (not fail) above ~500KB, naming
  the likely cause (mass moves / wrong base) and the `--base` remedy.
- **F3**: preflight Gate 1 recognizes the stacked shape: when the
  PR's base is not the default branch, report
  `PENDING:stacked on <base> — CI runs on retarget`, never "no runs
  registered". Test in the stub-gh harness.

## Acceptance Criteria

- [ ] Stacked-PR input generated correctly on the first try
      (fixture or transcript)
- [ ] Size warning fires on an oversized input (test)
- [ ] Gate 1 stacked wording pinned by a stub-gh test
- [ ] Core VERSION bump + manifests if core files change

## Notes

- Evaluation skipped (planner): tooling hardening with decisions
  in-spec; evidence lived in KIT-0067's retro.
