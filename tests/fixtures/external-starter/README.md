# Fixture: externally-authored task starter + handoff (PLAY-0001)

Acceptance fixture for **KIT-0085** (external starter authoring path).

Provenance: written 2026-08-04 by a claude.ai prototyping session (no kit
checkout access) for the Varv playground project, at the end of the
KIT-0066 prototype-intake flow. Committed here as a faithful snapshot of
what external authoring against `TASK-STARTER-TEMPLATE.md` v1.1.0
actually produces — the deviations are the point:

- `PLAY-0001-TASK-STARTER.md` line ~50: ad-hoc "Coordinator note"
  admitting the worktree was not pre-created and `agent-handoffs.json`
  not updated (template checklist unsatisfiable from outside the
  checkout — KIT-0085 issue 1/3).
- Lines ~57-58: guessed branch name in the LAUNCH block with a
  "correct it if the helper disagrees" hedge (two sources of truth —
  KIT-0085 issue 2).

Sanitization: the only edits versus the operator's originals are the
Vercel team/project IDs in the handoff, replaced with
`team_PLACEHOLDER…`/`prj_PLACEHOLDER…`. Everything else is verbatim.

Intended use: after KIT-0085 ships, this pair must (a) pass the
author-time checklist with zero deviations needing a coordinator note,
and (b) adopt cleanly through `adopt-starter` (the guessed LAUNCH block
being replaced by a stamped one). The live project it came from also
serves as an end-to-end re-validation target.
