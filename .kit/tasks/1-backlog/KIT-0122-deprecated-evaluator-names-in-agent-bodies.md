# KIT-0122: Agent bodies command deprecated evaluators — sweep to -v2 and pin with a guard

**Status**: Backlog
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 2-4 hours + plugin release ride
**Created**: 2026-09-14
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: KIT-0121 (evaluator update-channel sync — same subsystem,
this is the runtime half of that sync gap), KIT-0111 (version-bump
guard — this rides the same next release train), KIT-0115 (also riding
next release)

## Overview

Library v0.10.0 ships v1 and v2 evaluators side by side, with v1 marked
`status: deprecated` / `replaced_by: <name>-v2` in evaluator.yml. The
adversarial-workflow CLI has ZERO handling for those fields — its
discovery layer logs them in the generic "Unknown fields in
evaluator.yml" warning and discards them. Invoking `adversarial
code-reviewer-fast` therefore silently runs the stale evaluator.

The kit's own agent bodies are what put those v1 names in agents'
hands: Phase 5 of feature-developer commands `adversarial
code-reviewer-fast` / `code-reviewer` / `claude-code` verbatim, with
only a soft "Prefer the -v2 variants" note later in the section.

**Incident (ixda-services-planning, 2026-09-14)**: an implementation
agent ran its entire Gate 5 pass on deprecated `code-reviewer-fast`
(Gemini 2.5 Flash) and only noticed during retro metrics. On identical
input, v1 returned FAIL/5 findings/0 surviving; `code-reviewer-fast-v2`
(Gemini 3 Flash) returned CONCERNS with 1 real finding v1 missed. Not
cosmetic.

## Verified facts (2026-09-14)

1. 9 deprecated evaluators installed in a current v0.10.0 consumer
   install (google/{code-reviewer-fast, arch-review-fast, gemini-deep,
   gemini-flash}, mistral/codestral-code, openai/{gpt5-synthesis,
   gpt5-diversity, gpt52-reasoning, gpt54-pro}).
2. `grep -rn "deprecated\|replaced_by" adversarial_workflow/` (CLI @
   038d4e7): zero code hits. Only `evaluators/discovery.py:244` touches
   the fields, as discarded unknowns.
3. v1 names hard-coded in FOUR kit bodies, present in kit main AND
   distributed plugin 2.1.1 (cache + marketplace copies verified):
   `.claude/agents/feature-developer.md`,
   `.claude/agents/feature-developer-f5.md`,
   `.claude/skills/bot-triage/SKILL.md`,
   `.claude/skills/code-review-evaluator/SKILL.md`.
4. The consumer project itself carries no evaluator names — plugin
   agents are the sole source. Fix must ride a plugin release to reach
   consumers.

## Requirements

1. Sweep the four bodies: every literal evaluator invocation moves to
   the `-v2` name; the "prefer -v2" soft note becomes a hard rule
   ("v1 names are deprecated; the CLI runs them without warning —
   never invoke a non-`-v2` name unless the library provides no v2").
2. Keep the fd/fd-f5 SYNC-block contract: both files change
   identically in one commit.
3. **Guard, not just sweep** (the incident's lesson: the note already
   existed and didn't help): add a test or pattern-lint rule that fails
   when an agent/skill body under `.claude/` invokes an evaluator name
   marked deprecated in the installed library
   (`.adversarial/evaluators/*/*/evaluator.yml` → `status: deprecated`).
   Grep-level is fine; it must catch `adversarial <v1-name>` command
   lines, not prose mentions in example/history blocks.
4. Plugin release: bodies are rostered plugin components — minor bump,
   all four version fields, per Merge-Gate Protocol. Pair with KIT-0115
   / KIT-0117's pending release train if timing allows.
5. Upstream escalation filed: the CLI should parse
   `status`/`replaced_by` and at minimum warn loudly on invoking a
   deprecated evaluator (draft:
   `.kit/context/KIT-0122-adversarial-workflow-deprecation-issue-draft.md`).
   The kit sweep is NOT contingent on upstream — it is the only fix
   that works today.

## Out of scope

- CLI-side refuse/auto-route behavior — upstream's decision (issue
  draft states the options).
- Removing deprecated evaluators from installs — library packaging
  choice; they must remain invocable for reproducing old reviews.
- KIT-0121's channel-sync question.

## Acceptance Criteria

- [ ] No `adversarial <deprecated-name>` invocation lines remain in
      `.claude/agents/` or `.claude/skills/` (kit main)
- [ ] fd / fd-f5 changed identically (SYNC contract intact)
- [ ] Guard exists and fails on reintroduction of a deprecated name
- [ ] Plugin release plan noted (or executed) so consumers receive it
- [ ] Upstream issue filed on movito/adversarial-workflow
- [ ] Evaluator cost/selection table in fd bodies updated if v2
      pricing differs

## References

- Incident retro: ixda-services-planning, 2026-09-14 (Gate 5 ran
  deprecated code-reviewer-fast end-to-end; v2 comparison table in the
  agent's report)
- `adversarial_workflow/evaluators/discovery.py:244` — the discard point
- KIT-0121 — sibling task, install/update channel sync
