# KIT-0028: Canonicalize Cross-Repo Pattern Doc and Repair Conventions (Sync Phase 0)

**Status**: Done
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 2-3 hours
**Created**: 2026-06-12

## Related Tasks

**Parent**: KIT-ADR-0024 (Cross-Repo Topology Default + Drift Control)
**Depends On**: None
**Related**: KIT-0027 (cross-repo first-class support), KIT-0029/0030/0031 (later sync phases)

## Overview

KIT-ADR-0024 made `docs/CROSS-REPO-PATTERN.md` in this repo the single
canonical copy of the cross-repo pattern. Today three diverging forks exist
(ixda-services-2.0, suwinex-planning, label-maker-planning), and at least one
fork — suwinex-planning's `2026-04-16-cross-repo-agent-pattern.md` — is
*newer* than the kit's copy (it gained an adversarial evaluator recipe on
2026-04-22 and field-testing revisions). Additionally, label-maker-planning
declares the cross-repo split only in README prose; its CLAUDE.md lacks the
machine-readable `## Target Repository` section that slash commands depend on
for auto-detection.

This task repairs the conventions across the active repos before any
machinery work (Phases 1-2) begins.

## Requirements

### 1. Merge newest fork content into the canonical doc

1. Diff `suwinex-planning/.kit/context/2026-04-16-cross-repo-agent-pattern.md`
   against `docs/CROSS-REPO-PATTERN.md` (this repo)
2. Merge content present only in forks (evaluator recipe, lessons learned,
   `prepare-review-input.sh` workflow) into the canonical doc
3. Also diff the label-maker-planning copy (`docs/CROSS-REPO-PATTERN.md`
   there) for any unique deltas

### 2. Replace forks with links

In suwinex-planning and label-maker-planning, replace the forked pattern doc
with a short stub: link to the canonical doc (GitHub URL of
movito/agentive-starter-kit `docs/CROSS-REPO-PATTERN.md`) plus any
project-specific deltas that don't belong upstream. ixda-services-2.0 is out
of the active-4 scope; leave its copy but note the canonical location at the
top if touched.

**Allowed deltas in a stub** (everything else upstreams or is dropped):
- The project's target repo path, GitHub slug, and branch rules
- Stack-specific testing/CI commands for that target
- Worked examples using the project's task prefix
General pattern guidance, evaluator recipes, and lessons learned are never
deltas — they go upstream.

### 3. Fix label-maker-planning CLAUDE.md

Add the machine-readable section:

```markdown
## Target Repository

- **Path**: `../label-maker-code`
- **GitHub**: movito/label-maker-code
```

Verify the cross-repo-aware commands (`/retro`, `/wrap-up`, `/check-ci`)
detect it (dry-run one command's detection step).

### 4. Add `## Provenance` stamps

Add to CLAUDE.md of suwinex-planning, label-maker-planning, and
moss-skolemusikkorps:

```markdown
## Provenance

- **kit-version**: <version at bootstrap, best-effort from git history>
- **bootstrapped**: <date> from <source repo>
- **plugin**: agentive-workflow@<pinned version, if adopted>
```

**Determination procedure** (in order; stop at first hit):
1. Existing provenance note in CLAUDE.md/README (suwinex documents its
   2026-05-09 bootstrap from ixda-services-2.0)
2. `git log --reverse --oneline -- pyproject.toml CHANGELOG.md | head -3`
   in the project — bootstrap commits typically import these verbatim;
   match content against kit release history
3. Layout heuristic: `delegation/` + `.agent-context/` ⇒ pre-`.kit/`
   generation (≤ v0.2.x); `.kit/` ⇒ ≥ 2026-04 layout

Where the original bootstrap version is still unknowable, record the
assessed state (`kit-version: unknown (pre-0.2.x layout)` is acceptable for
moss) — honesty over false precision.

## Acceptance Criteria

- [x] Canonical `docs/CROSS-REPO-PATTERN.md` contains the evaluator recipe
      and all fork-only content; no information lost from any fork
      (kit commit 624a11e; label-maker's copy was byte-identical to the
      previous canonical — zero unique deltas)
- [x] suwinex-planning and label-maker-planning pattern docs are link stubs
      (with deltas if any), committed to their `main` (e1c7bdb, eea12bb)
- [x] label-maker-planning CLAUDE.md has a working `## Target Repository`
      section; auto-detection verified by running suwinex's
      `lib/target_repo.sh` parser against it with `PROJECT_ROOT` set —
      resolves `movito/label-maker-code` / `../label-maker-code` correctly
- [x] All three active planning repos have `## Provenance` sections
      (moss 24b721f: kit v0.4.0, 2026-03-21 — determined from first commit,
      better than the anticipated "unknown")
- [x] Kit version bumped to 0.5.1 and CHANGELOG updated in this repo

## Completion Findings (2026-06-12)

- **label-maker-planning's slash commands are NOT cross-repo aware** — its
  `.claude/commands/*.md` are the kit's single-repo versions with no
  `## Target Repository` detection step. The new CLAUDE.md section is
  parseable (verified above) but inert until the detection-aware commands
  arrive. Folded into KIT-0030 Requirement 5 (label-maker is the first
  migration target; the plugin's commands must carry the detection step).
- The cross-repo helper scripts (`prepare-review-input.sh`,
  `lib/target_repo.sh`) still live only downstream (suwinex,
  ixda-services-2.0). The canonical doc notes this; upstreaming is
  KIT-0026/KIT-0030 scope.

## Risks

### Risk 1: Forks contain contradictory revisions
**Likelihood**: Low — forks share a common 2026-04-17 ancestor
**Impact**: Low
**Mitigation**: Prefer the most recently dated section; preserve both with a
note if genuinely contradictory.

### Risk 2: Link stubs break offline/grep workflows in projects
**Likelihood**: Low
**Impact**: Low
**Mitigation**: Stub includes a one-paragraph summary of the pattern and the
local conventions (target path, branch rules), so day-to-day agent work never
needs the full doc.

## Notes

- Touches 4 repos; all planning-side commits go straight to `main` per the
  pattern itself. No feature branches needed for planning artifacts.
- moss-skolemusikkorps is a monorepo (no Target Repository section needed);
  it only receives the Provenance stamp in this phase.
- Evaluator finding (arch-review-fast, 2026-06-12): manual diff/merge of doc
  forks doesn't scale. Accepted for this one-time consolidation; ongoing
  drift prevention is handled by KIT-0031's policy (stubs + provenance
  stamps make future drift detectable by grep, and link stubs remove the
  fork mechanism entirely).
