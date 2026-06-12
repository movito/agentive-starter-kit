# KIT-0029: Reconcile feature-developer Variants into Canonical v7 (Sync Phase 1)

**Status**: Done
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 3-5 hours
**Created**: 2026-06-12

## Related Tasks

**Parent**: KIT-ADR-0024 (Cross-Repo Topology Default + Drift Control)
**Depends On**: KIT-0028 (canonical pattern doc — v7 references it)
**Related**: KIT-0026 (agents_core manifest tier), KIT-0030 (plugin distribution)

## Overview

The feature-developer agent has forked across active projects, and the most
advanced variant is stranded downstream:

| Repo | Variant | Notable deltas |
|------|---------|----------------|
| agentive-starter-kit | feature-developer-v5, v6 | v6 added cross-repo awareness (2026-05) |
| suwinex-planning | v6 | SvelteKit-specific phases, bot-watcher sub-agent pattern |
| label-maker-planning | v6 | Python/reportlab stack notes |
| moss-skolemusikkorps | v6 (edited, uncommitted) + **v7** | v7: inline CI/bot polling via ScheduleWakeup (replaces the deprecated bot-watcher sub-agent), claude-fable-5 model, verify-before-believing reflex, Sanity MCP footguns |

This task produces one canonical v7 in this repo, with project-specific
content separated from portable content, so the plugin (KIT-0030) and the
manifest (KIT-0026) have a single source to distribute.

## Requirements

### 1. Investigate before merging

- Read moss's uncommitted `feature-developer-v6.md` edits and the deleted
  `.claude/commands/wrap-up.md` (visible in moss git status) — understand
  why before reconciling; the deletion may encode a workflow decision that
  belongs in the canonical version (or it may be local cleanup)
- Read moss retros (`.agent-context/retros/`) for v7-relevant learnings not
  yet in the agent file

### 2. Three-way reconciliation

1. Diff suwinex v6, label-maker v6, and moss v7
2. Classify every section: **portable** (workflow phases, polling pattern,
   triage rules, shell rules) vs **project-specific** (stack notes, task
   prefixes, MCP footguns, directory tables)
3. Produce canonical `feature-developer-v7.md` in this repo containing only
   portable content, with clearly marked extension points
   (`## Project Context`, `## Stack Notes`, `### Recurring Footguns`) that
   downstream projects fill in
4. Frontmatter per KIT-0026 standard: `name`, `description`, `model`,
   `version` (semver), `origin: agentive-starter-kit`, `last-updated`,
   `created-by`

### 3. Preserve the v7 innovations

The canonical version MUST retain, as portable content:

- Inline CI/bot polling via ScheduleWakeup with cache-window guidance
  (60-270s warm / avoid 300s / 1200s+ long polls); bot-watcher sub-agent
  explicitly deprecated
- Verify-before-believing reflex (grep installed type definitions before
  trusting evaluator claims about APIs)
- Evaluator trio table with costs and when-to-use
- Gated phase workflow (pre-implementation gate, self-review gate, CI+bots
  gate, evaluator gate, preflight gate)

### 4. Model reference policy

v7 in moss pins `claude-fable-5`. Decide and document: canonical agent files
reference a model *tier* (e.g., "latest Opus-class") or a pinned ID with an
upgrade note. Pinned IDs go stale; tiers are ambiguous. Recommendation:
pinned ID + `last-updated` + a line in the kit upgrade checklist.

### 5. Version and changelog

- Bump kit minor version; CHANGELOG entry summarizing the reconciliation
- Mark v5/v6 in this repo as superseded (delete or move per KIT-0026's
  deletion list practice)

## Acceptance Criteria

- [x] Canonical `feature-developer-v7.md` in `.claude/agents/` of this repo,
      portable-only, with extension points documented (v2.1.0)
- [x] All four v7 innovations (above) present and project-agnostic
- [x] moss wrap-up deletion and v6 edits investigated; outcome recorded in
      the task's notes (see Investigation Outcome below)
- [x] No project-specific strings (MOSS-, SWP-, LBL-, stack names) in the
      canonical file outside example blocks (grep-verified; provenance
      moved from frontmatter to CHANGELOG)
- [x] Frontmatter conforms to KIT-0026 standard
- [x] Kit version bumped to 0.6.0; v5/v6 deleted (git history preserves
      them; no agents manifest tier exists yet — that's KIT-0026)
- [x] Downstream adoption explicitly deferred to KIT-0030 (the moss
      wrap-up restore and v6 model bump were separate user-directed
      moss-local commits, not v7 adoption)

## Risks

### Risk 1: Over-abstraction makes the agent vague
**Likelihood**: Medium
**Impact**: High — a generic agent that knows no stack performs worse
**Mitigation**: Extension points are mandatory sections the bootstrap/
onboarding flow fills; canonical file ships with one worked example block.

### Risk 2: moss's uncommitted edits conflict with v7
**Likelihood**: Medium
**Impact**: Low
**Mitigation**: Investigation step (Requirement 1) happens first; user
arbitrates if the edits encode an unmerged decision.

## Notes

- This is upstream-only work: the deliverable lands in agentive-starter-kit.
  Distribution to projects is KIT-0030 (plugin) / KIT-0026 (kit manifest).
- planner3 (suwinex) vs planner2 (kit) reconciliation is intentionally out
  of scope — separate smaller task if wanted; feature-developer is the
  highest-drift, highest-value agent.

## Investigation Outcome (Requirement 1, 2026-06-12)

- **moss v6 uncommitted edit**: one line — model pin
  `claude-sonnet-4-20250514` → `claude-opus-4-8`. User confirmed
  Claude Opus 4.8 is a real model; kept and committed in moss (92aeb50).
  No workflow decision encoded.
- **moss wrap-up.md deletion**: local cleanup, not a workflow decision.
  User asked for restore + retrofit; restored in moss (a103bbe) with
  MOSS-NNNN placeholders, monorepo note, semver frontmatter, and removal
  of an unused `gh repo view` step. The newest wrap-up generation
  (cross-repo Step 0 + planning-repo exception) lives in suwinex v1.3.0 —
  canonicalizing /wrap-up is KIT-0030 scope, not this task.
- **moss retros (MOSS-0002..0009)**: two portable learnings not yet in
  v7, folded into the canonical file: (1) batch same-category bot fixes
  into one commit to avoid repeated scan rounds; (2) evaluators reliably
  miss CSS/cascade bugs while catching logic edge cases — flag dual
  render-path components for manual review.
