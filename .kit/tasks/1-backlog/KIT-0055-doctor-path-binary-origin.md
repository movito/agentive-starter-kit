# KIT-0055: Doctor — check the PATH-resolved binary's origin (the third-install blind spot)

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 1-2 hours
**Created**: 2026-07-17
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: the ADVERSARIAL_UNATTENDED three-installs incident
(KIT-0044 → KIT-0050 → KIT-0053, final forensics in KIT-0053's
corrected retro) — three sessions reached conflicting "verified"
conclusions because each tested a different binary
**Related**: KIT-0046 (doctor + the skew check this extends)

## Overview

Doctor's version-skew check compares the venv package against `pip`'s
system package — but the binary agents actually invoke is whatever
PATH resolves, which on this machine is a **third** install: an
editable install of the operator's dev checkout, whose version string
matches PyPI while its behavior doesn't. The skew check passed (both
compared packages agreed) while the real skew was invisible. Every
retro flip-flop in the incident traces to this blind spot.

## Requirements

- **F1**: for each skew-checked tool (adversarial-workflow today;
  extensible), resolve the PATH binary (`command -v`), identify its
  backing python + package location, and compare against the
  venv/system pair. Three-way disagreement → WARN naming all three
  origins.
- **F2**: detect editable/VCS installs (`direct_url.json` with
  `"editable": true` or a VCS url) on ANY of the three and emit a
  standing WARN: "dev build in play — version strings may not reflect
  behavior; PATH binary is <origin>". Never FAIL — an editable install
  is intentional on a maintainer's machine; doctor NAMES it (the
  masking-class rule applied to environments).
- **F3**: the check's header comment cites this incident (per the
  Incident Closure lifecycle rule).

## Acceptance Criteria

- [ ] Doctor on this machine WARNs, naming the editable
      `~/Github/adversarial-workflow` install as the PATH binary
- [ ] Three-way agreement on a clean machine → PASS
- [ ] Editable detection covered by fixture tests (fake dist-info)
- [ ] Never blocks: WARN/INFO only

## Notes

- Source: planner empirical matrix 2026-07-17 (KIT-0053 closeout).
  The incident cost three retro corrections across three tasks; the
  check makes the environment shape visible in one doctor line.
