# KIT-0031: Provenance Stamps for Dormant Repos + Sync Policy (Sync Phase 3)

**Status**: Backlog
**Priority**: low
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-06-12

## Related Tasks

**Parent**: KIT-ADR-0024 (Cross-Repo Topology Default + Drift Control)
**Depends On**: KIT-0030 (policy should reflect the post-plugin reality)
**Related**: KIT-0028 (provenance stamps for the active repos)

## Overview

Close out the sync initiative: stamp the dormant Gen-1 repos so their frozen
state is explicit, clean up migration debris, and write down the ongoing
policy so drift control survives beyond this effort.

## Requirements

### 1. Stamp dormant repos (no retrofit)

**Definition — a repo is dormant kit-derived when all three hold:**
1. Layout marker present: `delegation/` + `.agent-context/`, or `.kit/`
2. No commits within the inactivity threshold (default 90 days;
   `git log -1 --format=%ad`)
3. Not in the active sync set, nor in KIT-0026's kit-sync set

The active sync set, kit-sync set, layout markers, and inactivity threshold
are **owned by the sync policy doc** (Requirement 3) — this task seeds them
there and the definition above then defers to the doc. Bootstrap values:
active = {this kit, suwinex, label-maker, moss}; threshold = 90 days.
Execute Requirement 3 before Requirement 1 so the stamping run reads the
sets from the policy doc, not from this spec.

Regenerate the list from this definition at execution time. The 2026-06-12
survey snapshot (for orientation, not authority): ombruk, ombruk-v2,
thematic-2, gas-taxes, wcag-intro-v01, agentive-studio, epistemic-drift,
research-method-matrix, agentic-lotion-2, design-theory-timeline,
ixda-services-2.0. (dispatch-kit is excluded by clause 3 — it is in
KIT-0026's kit-sync set.)

For each repo matching the definition:

- Add a `## Provenance` section to CLAUDE.md: layout generation
  (Gen-1 `delegation/` / Gen-2 `.kit/`), bootstrap source if known, and the
  line: *"Frozen at this kit snapshot; not part of the active sync set.
  Upgrade deliberately via KIT-ADR-0024 §4 if revived."*
- One commit per repo, no other changes. Skip repos with uncommitted work
  (note them instead).
- Optional helper: a small script that applies the stamp template and
  commit, given a repo path — write it if stamping more than ~5 repos by
  hand proves tedious; don't gold-plate it.

### 2. Clean up migration debris

- `moss-skolemusikkorps-web`: empty repo (zero commits) from an abandoned
  split. Propose disposition to the user (delete locally + on GitHub, or
  keep as the future `-code` repo if moss later splits). **User decision —
  do not delete unilaterally.**

### 3. Write the sync policy (execute first — Requirements 1 and 4 read it)

Add a short policy doc to the canonical pattern doc or `.kit/docs/`. It is
the single owner of: the active sync set, the kit-sync set, the dormancy
definition (layout markers + inactivity threshold), and the provenance
template. Other tasks and scripts reference the doc, never their own copies.
The policy covers:

- New production projects: split topology, bootstrap from kit, pin plugin,
  stamp provenance (restates KIT-ADR-0024 as a checklist)
- Active projects: upgrade pins deliberately; never let a project invent
  shared machinery without a same-week upstream PR (the v7 lesson)
- Dormant projects: frozen by default; revival starts with a provenance
  check and pin refresh
- Quarterly (or per-new-project) drift check: `grep -r "kit-version"` across
  `~/Github/*/CLAUDE.md` — the stamps make this a one-liner

### 4. Revisit the moss topology decision

Schedule (don't execute) the deferred decision: after KIT-0030's moss
migration, present the split-vs-monorepo question again with the actual
post-plugin maintenance picture as input.

## Acceptance Criteria

- [ ] Dormant repo list verified and each stamped (or noted as skipped, with
      reason)
- [ ] moss-skolemusikkorps-web disposition decided by user and executed
- [ ] Sync policy doc committed to this repo and linked from
      `docs/CROSS-REPO-PATTERN.md`
- [ ] moss topology decision queued with its inputs documented

## Risks

### Risk 1: Stamping repos with stale local state
**Likelihood**: Medium (dormant repos may have uncommitted work)
**Impact**: Low
**Mitigation**: `git status` check before touching each repo; skip-and-note
rule above.

## Notes

- Deliberately low priority: nothing here blocks active work; the value is
  making the frozen state explicit so future-you doesn't re-survey.
- Evaluator finding (arch-review-fast, 2026-06-12) suggested splitting this
  into 4 sub-tasks for cohesion. Declined, with reasoning: this is a
  close-out checklist for a solo-maintainer workflow — four task files would
  cost more coordination than they save, and the sub-items share one
  context (the KIT-ADR-0024 initiative). The requirements are independently
  checkable, which captures the benefit of the split without the overhead.
  If any sub-item grows beyond a session, spin it out then.
- The same review's "policy as code" push (automated drift scanning in CI)
  is deferred to the policy doc itself: the grep-based check is proportionate
  at the current repo count; the policy should name the threshold at which
  automation becomes worth it.
