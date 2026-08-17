# KIT-0115: bot-triage ninth lying face — reviewDecision stuck at CHANGES_REQUESTED

**Status**: Backlog
**Priority**: low (documentation of a known deception; the truth-source
protocol already sidesteps it)
**Type**: Canon fix (`.claude/skills/bot-triage/` — rostered; rides the
next plugin release)
**Estimated Effort**: ~20 min
**Created**: 2026-08-17
**Source**: KIT-0113 retro, "Process notes" (deliberately NOT filed
mid-release — editing a rostered component would have opened another
drift cycle while 2.1.1 was in flight)

## Requirement

Add the ninth documented lying-status face to the bot-triage skill:

**`reviewDecision` stays `CHANGES_REQUESTED` indefinitely when the bot
clears its findings via a `COMMENTED` review instead of an `APPROVED`
one.** GitHub's decision field only flips on an explicit APPROVED from
the same reviewer; a bot that acknowledges fixes in comment-state
reviews leaves the PR-level field permanently red even though every
thread is resolved.

## Evidence (verified live, 2026-08-16/17)

agentive-starter-kit **#136**: CodeRabbit posted CHANGES_REQUESTED at
`fd7b166`; the fix rounds landed and threads were resolved; the
PR-level `reviewDecision` still read `CHANGES_REQUESTED` at merge
time. Thread-level GraphQL (the standing truth source) showed the real
state. Note the same task also re-confirmed faces already on file:
BugBot `skipping` while its threads were posted (twice), and
CodeRabbit's check reading "Review in progress" after its head review
had landed.

## Acceptance

- [ ] Ninth face documented in the skill alongside the existing eight,
      with the #136 evidence line and the remedy (thread-level
      reviewThreads GraphQL + per-review SHA matching, never the
      PR-level decision field)
- [ ] Component `version:` bumped; rides the next plugin release
      (drift guard red-by-design between merge and that cut)

## Out of scope

- Any change to the triage procedure itself — the protocol already
  keys on threads, not reviewDecision; this face is documentation so
  the field's lie is expected rather than rediscovered.
