# KIT-0070: Linear-sync script hardening — dry-run, arg strictness, visible logs

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-25
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0068 honest-flag #1 (PR #93 completion report) — the
fd's end-to-end verification of the A15 fix surfaced these
**Related**: KIT-0070 is post-0.9.0 small-fry; no sequencing pressure

## Overview

`scripts/optional/sync_tasks_to_linear.py` works (verified end-to-end
against live Linear during KIT-0068) but has three operator-hostile
edges: no `--dry-run`, unknown CLI args silently ignored (a typo'd
flag runs a REAL create/update sync against the live workspace), and
its log output is invisible when invoked via `project linearsync`
(script context).

## Requirements

- **F1 — `--dry-run`**: print the create/update/skip plan, touch
  nothing. `project linearsync --dry-run` passes through.
- **F2 — strict args**: unknown flags exit 2 with usage — a live-API
  script must never treat a typo as "proceed with defaults"
  (argparse with no passthrough; note the exit-code convention,
  KIT-0037).
- **F3 — visible logs under `project linearsync`**: whatever
  swallows the script's logging in subprocess context (buffering or
  logging-to-nowhere), fix so the per-task action lines reach the
  operator's terminal.
- **F4 — never print secrets**: F1-F3 changes must keep the API key
  out of all output (it lives in .env; the fd noted the root .env
  carries a live key).

## Acceptance Criteria

- [ ] `--dry-run` demonstrably read-only (transcript)
- [ ] Unknown flag → exit 2 + usage (test)
- [ ] `project linearsync` shows per-task lines (transcript)
- [ ] No secret material in any output path (grep of outputs)

## Notes

- Evaluation skipped (planner): small hardening, decisions in-spec.
