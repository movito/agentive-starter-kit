# KIT-0124: Ship the deep-review workflow to door/plugin consumers

**Status**: Backlog
**Priority**: Low (until a consumer opts into Tier 3)
**Created**: 2026-09-30
**Filed by**: fd-f5 (KIT-0116 Phase 3, /code-review finding — parked
per the resume starter's "discovered gaps → backlog" rule)

## Problem

REVIEW-PIPELINE.md 1.2.0 (a door-distributed twin) carries the formal
Tier-3 escalation contract, whose exact invocation names the saved
workflow `.claude/workflows/deep-review.js`. But the packaged door
ships no `.claude/` tree, and the agentive-workflow plugin does not
carry workflows either — so door/plugin-scaffolded consumers receive
a contract pointing at a file they don't have. Only kit-cloned
consumers (the consumer engine rsyncs `.claude/` wholesale) get it.

This is the #142/#143 shipped-set drift class: kit content outside
the distributed set never reaches consumers.

## Mitigation already in place (KIT-0116 Phase 3)

REVIEW-PIPELINE.md's Tier-3 section carries an explicit distribution
note: on such consumers an invocation is *requested but could not
execute* and is recorded as such per the contract. Honest, but the
capability gap remains.

## Direction

Do NOT solve ad hoc — the distribution mechanism is exactly the
territory of the UPGRADE-GESTALT arc's successor distribution ADR
(baseline+overlays; see KIT-ADR-0037 draft and its deferred
distribution successor). When that ADR lands, `deep-review.js` (and
`.claude/workflows/` generally) gets a ruled distribution channel;
this task then implements it and removes the caveat from
REVIEW-PIPELINE.md (both twins, same commit).

## Acceptance criteria

- [ ] A door- or plugin-scaffolded consumer can run the Tier-3
      invocation exactly as REVIEW-PIPELINE.md states it
- [ ] The distribution note in REVIEW-PIPELINE.md (+ door twin) is
      removed or rewritten to match reality
- [ ] The channel choice cites the distribution ADR, not ad-hoc copy
