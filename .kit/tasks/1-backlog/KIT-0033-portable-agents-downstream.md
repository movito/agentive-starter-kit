# KIT-0033: Make planner + feature-developer truly portable downstream

**Status**: Backlog
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 4-8 hours
**Created**: 2026-06-26
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: PR #57 (consolidate planner and feature-developer agents) — surfaced this gap
**Related**: KIT-0026 (sync agents+skills across kit repos), ASK-0044 (.kit/ boundary)

## Overview

PR #57 consolidated planner and feature-developer agents and opted into shipping
both downstream via `bootstrap-consumer.sh` (dropped the prior `--exclude='planner.md'`
and folded ASK-specific Project Context into `feature-developer.md`). BugBot
correctly flagged two gaps before merge:

1. **`feature-developer.md` ships ASK identity downstream**
   ([thread](https://github.com/movito/agentive-starter-kit/pull/57#discussion_r3484524391))
   — Project Context section hardcodes KIT-NNNN prefix, kit layout, kit-only rules.
   Consumer projects rsyncing the file inherit ASK's identity instead of their own.

2. **`planner.md` ships without its task infrastructure**
   ([thread](https://github.com/movito/agentive-starter-kit/pull/57#discussion_r3484524395))
   — V2 planner workflow assumes `.kit/tasks/`, handoffs, `./scripts/core/project
   start|complete`, and related paths. `bootstrap-consumer.sh` does not sync the
   `.kit/` skeleton, so a consumer invoking the shipped planner hits missing
   directories and broken task-lifecycle commands.

Both findings were merged-with-acknowledgement; this task resolves them properly.

## Requirements

### Functional Requirements

- **F1**: A consumer project bootstrapped via `bootstrap-consumer.sh` receives a
  working `.kit/` skeleton (empty `tasks/<status-folders>/`, `context/`,
  `templates/`, `adr/`) — enough for `./scripts/core/project start|complete`
  and the planner workflow to function on day one.
- **F2**: The onboarding flow overwrites `Project Context` and `Stack Notes`
  sections in `feature-developer.md` (and any analogous sections in `planner.md`)
  with the consumer project's values — derived from interview answers or
  defaulted to safe placeholders that the consumer can fill in later.
- **F3**: A clear opt-out: a consumer that doesn't want the kit workflow can
  refuse the `.kit/` scaffold and the ship-downstream agents during bootstrap.

### Non-Functional Requirements

- **N1**: No regression for ASK itself — the agents must still work for kit
  development with their current filled-in content.
- **N2**: The mechanism for overwriting Project Context / Stack Notes must be
  robust (markers, not fragile line-number assumptions) so future agent edits
  don't silently break the overwrite.

## Design Notes

Possible approaches (to be evaluated during implementation):

1. **EXTENSION POINT markers**: Add `<!-- BEGIN KIT-LOCAL --> ... <!-- END KIT-LOCAL -->`
   markers around filled sections so bootstrap can `sed`/`awk` replace them safely.
2. **Source-of-truth indirection**: Strip filled content from the agent files;
   have the agents say "read Project Rules from CLAUDE.md" (which downstream
   bootstrap already customizes). Trade-off: ASK contributors lose the
   convenience of the filled-in content in the agent file itself.
3. **Template-and-local split**: Ship `feature-developer.template.md` as a
   pristine template alongside `feature-developer.md` (the ASK-local copy).
   Bootstrap copies the template; ASK uses the filled local. This re-introduces
   the v6/v7 split this PR collapsed, so probably not the right answer.

Lean: **approach 1** (markers) is least invasive and respects both audiences.

## Acceptance Criteria

- [ ] `bootstrap-consumer.sh` provisions a usable `.kit/` skeleton in consumer
  repos
- [ ] After bootstrap, `feature-developer.md` and `planner.md` in the consumer
  repo have **Project Context** filled for the consumer (not for ASK)
- [ ] After bootstrap, `feature-developer.md` has **Stack Notes** filled for the
  consumer's stack (not ASK's pytest/DK rules/pre-commit gauntlet) — verifies
  F2's "both sections overwritten" requirement
- [ ] After bootstrap, `./scripts/core/project start <ID>` works in the consumer
  repo against a stub task in `.kit/tasks/2-todo/`
- [ ] After bootstrap, `./scripts/core/project complete <ID>` moves the same
  stub task to `.kit/tasks/5-done/` and updates the `**Status**` field — covers
  the full lifecycle, not just task start
- [ ] ASK's own copies of the agents are unchanged in content (only the markers
  added, if approach 1 is chosen)
- [ ] BugBot threads on PR #57 can be marked resolved once this lands

## Test Plan

- Bootstrap a fresh consumer project end-to-end; verify the planner workflow
  runs through Phases 1-8 without missing-file errors
- Run pre-commit + CI on ASK after the marker additions
- Manually invoke `planner.md` in ASK; verify Project Context still loads
  ASK-specific content

## Notes

- This work is *not* in scope of PR #57 (consolidation only). Acknowledged in
  thread replies on PR #57.
- Coordinate with KIT-0026 if agent/skill cross-repo sync changes overlap.
