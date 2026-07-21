# KIT-0063: Make the consumer-boundary inventory bidirectional

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: <1 hour
**Created**: 2026-07-22
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0057 retro (What Should Change #3; CodeRabbit caught
the one-directional gap on PR #90)

## Overview

`TestConsumerTestsRsyncBoundary` in `test_bootstrap_consumer.py`
asserts inventory ⊆ engine excludes — so an engine-only addition
(e.g. `test_bots_conformance.py` in KIT-0057) passes silently until a
bot notices. Extend it to also parse the engine's exclude list and
assert engine ⊆ inventory: set equality, both directions loud.

## Acceptance Criteria

- [ ] Engine exclude list parsed; equality asserted both ways
- [ ] Deliberately desynced fixture proves both directions fire

## Notes

- Evaluation skipped (planner): single-test extension of an existing
  evaluated mechanism — the skip category.
