# KIT-0051: Close the kit_markers.py seeded-not-synced drift gap

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-15
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0050 (retro Should-Change #3; fast-v2's real concern)
**Related**: KIT-0033 (kit_markers origin), KIT-0049 (sync tiers)

## Overview

`kit_markers.py` is seeded to consumers by bootstrap (`scripts/local/`,
deliberately not synced) — but the `kit-install` record READER in
`scripts/core/project` (`_doctor_install`) IS synced. The reader and
the marker helper can therefore drift apart across consumer versions:
a consumer's old kit_markers meets a new project script (or vice
versa), and region parsing assumptions diverge silently.

## Requirements

- Decide and implement one of:
  - **(a)** move `kit_markers.py` to `scripts/core/` (rides the
    manifest, versions with the reader) — check the consumer-rsync
    test-exclusion implications (`test_kit_markers.py` currently
    depends on scripts/local placement; self-review item 7);
  - **(b)** add it as a manifest entry while keeping the path (if the
    manifest supports scripts/local entries cleanly);
  - **(c)** make the reader not depend on kit_markers at all (inline a
    minimal region extract in `project` with a pinned-format test both
    sides share).
- Whichever route: a test that pins the record FORMAT contract both
  sides parse (the shared golden), so drift breaks CI, not consumers.

## Acceptance Criteria

- [ ] Reader and marker helper cannot drift silently (shared format
      golden or shared code path)
- [ ] Consumer test-exclusion rules still honored (item 7)
- [ ] Route reasoning stated in the PR

## Notes

- Source: `.kit/context/retros/KIT-0050-retro.md` Should Change #3.
- Not release-blocking for the transformation; schedule alongside or
  after P3 (whose door touches the same seeding paths).
