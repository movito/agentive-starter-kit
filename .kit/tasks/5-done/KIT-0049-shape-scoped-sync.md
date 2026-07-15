# KIT-0049: Shape-scoped `project sync`

**Status**: Done
**Priority**: high (raised by planner 2026-07-14: this completes P2's
promise — planning repos are live but update-locked until it lands.
Recommended sequence: KIT-0049 next, small and unblocking, then P1.)
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-07-14
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0048 (planning-repo shape) — filed from a BugBot finding
on PR #78
**Related**: KIT-ADR-0026 (the sync engine), ADR-0027 P3 (the one door —
may absorb or reshape this)

## Overview

`sync_from_manifest.py` selects entries from the UPSTREAM manifest's
tiers, so a full `project sync` into a planning-shaped repo would
install the single-shape toolchain files (`ci-check.sh`,
`pattern_lint.py`, …) the shape must never ship, and would replace the
reduced planning manifest with upstream's full one.

KIT-0048 shipped the stopgap: `cmd_sync` reads the shape record and
**refuses** (exit 2, wrapper convention) with a pointer here. This task
makes sync shape-aware.

## Requirements

*(The two open decisions below were LOCKED by the planner 2026-07-14
after evaluation — the evaluator correctly refused to approve
development on undecided architecture.)*

- **Single source = the consumer's own manifest** (DECIDED). Sync
  intersects upstream entries with the file list the consumer's
  `scripts/.core-manifest.json` already records — KIT-0048 writes the
  reduced planning manifest at bootstrap, so the record exists. Sync
  updates what the consumer HAS; it never introduces files the
  manifest doesn't list. `PLANNING_CORE`/`PLANNING_LOCAL` stay in
  `bootstrap-consumer.sh` as a *seeding* concern only. No new
  YAML/JSON shape-config format (declined: a second declarative file
  is the config sprawl ADR-0025/0027 decline; the manifest is already
  the machine-readable record).
- **Trigger = implicit, shape-read, no flag** (DECIDED). Sync reads
  the shape record via the existing `_doctor_shape()` reader
  (`scripts/core/project:1264`). Because manifest-intersection is
  shape-agnostic, this survives P3 untouched: the door orchestrates
  installs; sync remains the update path. The P3 coordination note is
  dissolved, not deferred.
- **v1 limitation, explicit and loud**: planning repos receive
  *updates* to recorded files, not *additions* — a brand-new upstream
  script does not self-appear. Addition path = re-bootstrap
  (marker-merge-safe) or a documented manual manifest add; revisit
  when P3 considers shape-aware upstream manifests. The sync report
  must NAME skipped additions (the engine's existing announcement
  pattern — never silent).
- The replaced-manifest problem: a complete sync must not overwrite the
  planning manifest's reduced file list with upstream's full list
  (falls out of intersection; pin it with a test anyway).
- Remove the KIT-0048 refusal guard once subsets work; keep the
  malformed-shape refusal (exit 2, wrapper convention).

## Acceptance Criteria

- [ ] `project sync` in a planning-shaped repo updates ONLY
      manifest-recorded files and preserves the reduced manifest
- [ ] Skipped upstream additions are NAMED in the sync report/output
- [ ] Single-shape sync behavior unchanged, including additions
      arriving (characterization test)
- [ ] The KIT-0048 guard replaced by working subset logic; malformed
      shape still refuses with exit 2
- [ ] Engine exit-code contract (0/1/2/3/4) untouched

## Evaluation (2026-07-14)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — correct
core objection: the spec framed architecture as "decide later". Planner
disposition: both decisions LOCKED above (consumer-manifest
intersection as single source; implicit shape-read trigger). Declined:
a new declarative shape-config file (Option A) — the consumer manifest
already is that file. The P3-overlap risk dissolves under the chosen
mechanism (shape-agnostic intersection). Log:
`.adversarial/logs/KIT-0049-shape-scoped-sync--arch-review-fast.md`.
