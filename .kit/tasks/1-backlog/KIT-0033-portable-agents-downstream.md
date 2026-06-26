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
and folded ASK-specific Project Context into `feature-developer.md`). Two bot
review rounds surfaced four related gaps:

1. **`feature-developer.md` ships ASK identity downstream**
   (BugBot — [thread](https://github.com/movito/agentive-starter-kit/pull/57#discussion_r3484524391))
   — Project Context section hardcodes KIT-NNNN prefix, kit layout, kit-only rules.
   Consumer projects rsyncing the file inherit ASK's identity instead of their own.

2. **`planner.md` ships without its task infrastructure**
   (BugBot — [thread](https://github.com/movito/agentive-starter-kit/pull/57#discussion_r3484524395),
   re-raised by CodeRabbit — [thread](https://github.com/movito/agentive-starter-kit/pull/57#discussion_r3484592020))
   — V2 planner workflow assumes specific paths used in Phases 1/4/5/8:
   `.kit/tasks/` (status folders), `.kit/context/` (handoffs, reviews),
   `.kit/templates/` (task starter template), and `./scripts/core/project
   start|complete`. `bootstrap-consumer.sh` does not sync the `.kit/` skeleton,
   so a consumer invoking the shipped planner hits missing directories on its
   first task scan and broken commands in the lifecycle flow.

3. **Re-bootstrap leaves stale canonical agent**
   (BugBot — [thread](https://github.com/movito/agentive-starter-kit/pull/57#discussion_r3484585878))
   — The `rm -f` sweep added in 37085b3 deletes retired variants
   (`planner2/3`, `feature-developer-v3/v6/v7`) so they don't linger alongside
   the V2 canonicals. But rsync's `--ignore-existing` (kept intentionally to
   preserve consumer customizations) means a *pre-existing* `feature-developer.md`
   or `planner.md` in the consumer is **never** replaced with the new V2
   canonical. Consumers can be stuck on a pre-consolidation agent indefinitely
   after re-bootstrap. The naive fix — dropping `--ignore-existing` — would
   clobber consumer Project Context fills. The proper fix requires the same
   marker mechanism as gap #1 (update outside markers, preserve inside).

All findings were merged-with-acknowledgement on PR #57; this task resolves
them properly.

## Requirements

### Functional Requirements

- **F1**: A consumer project bootstrapped via `bootstrap-consumer.sh` receives a
  working `.kit/` skeleton sufficient for the V2 planner and feature-developer
  workflows on day one. Concretely, the skeleton must provide:
  - `.kit/tasks/1-backlog/`, `.kit/tasks/2-todo/`, `.kit/tasks/3-in-progress/`,
    `.kit/tasks/4-in-review/`, `.kit/tasks/5-done/`, `.kit/tasks/6-canceled/`,
    `.kit/tasks/7-blocked/` (referenced by planner Phase 1 scan)
  - `.kit/context/` (handoffs, reviews — referenced by planner Phase 4 and
    feature-developer handoff reads)
  - `.kit/templates/TASK-STARTER-TEMPLATE.md` (referenced by planner Phase 5)
  - A functional `./scripts/core/project` script (referenced by planner Phase
    1/8 and feature-developer Phase 1)
- **F2**: The onboarding flow overwrites `Project Context` and `Stack Notes`
  sections in `feature-developer.md` (and any analogous sections in `planner.md`)
  with the consumer project's values — derived from interview answers or
  defaulted to safe placeholders that the consumer can fill in later.
- **F3**: A clear opt-out: a consumer that doesn't want the kit workflow can
  refuse the `.kit/` scaffold and the ship-downstream agents during bootstrap.
- **F4**: Re-running `bootstrap-consumer.sh` against an existing consumer
  checkout refreshes the canonical V2 agents (planner.md, feature-developer.md)
  with upstream improvements (new phases, edited Stack Notes structure, etc.)
  **without** clobbering the consumer's filled-in Project Context / Stack Notes
  sections. This requires the marker mechanism from N2 — without markers, the
  only safe rsync mode is `--ignore-existing` (current behavior), which leaves
  consumers stuck on whatever agent version they first bootstrapped.

### Non-Functional Requirements

- **N1**: No regression for ASK itself — the agents must still work for kit
  development with their current filled-in content.
- **N2**: The mechanism for overwriting Project Context / Stack Notes must be
  robust (markers, not fragile line-number assumptions) so future agent edits
  don't silently break the overwrite. **Markers are necessary, not preferred**:
  without them, F4 (re-bootstrap refresh) is unreachable — rsync's
  `--ignore-existing` is the only safe default for consumer-customizable files,
  and the only way to update file structure *outside* a customized region while
  preserving content *inside* it is with explicit region markers.

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
- [ ] **Re-bootstrap refresh**: bootstrap a fresh consumer, then bump an
  agent in the upstream kit (add a new phase, edit a Stack Notes bullet),
  then re-run `bootstrap-consumer.sh`. The consumer's agent file picks up the
  upstream change **outside** the marker regions; the consumer's customized
  content **inside both** the Project Context **and** the Stack Notes marker
  regions is preserved verbatim. Verifies F4 + N2 together — a partial
  implementation that preserves Project Context but clobbers Stack Notes
  must fail this check.
- [ ] **F3 opt-out**: bootstrap with an explicit opt-out flag (or interview
  answer) refusing the `.kit/` scaffold and ship-downstream agents. Result:
  no `.kit/` directory is created, no `planner.md` or `feature-developer.md`
  is copied to the consumer, and `bootstrap-consumer.sh` exits cleanly with
  a one-line summary of what it skipped.
- [ ] ASK's own copies of the agents are unchanged in content (only the markers
  added, if approach 1 is chosen)
- [ ] BugBot + CodeRabbit threads on PR #57 can be marked resolved once this
  lands (4 threads total — see Overview for IDs)

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
