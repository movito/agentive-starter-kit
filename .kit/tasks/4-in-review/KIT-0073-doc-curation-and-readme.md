# KIT-0073: Doc curation — execute the approved dispositions + the 120-line README

**Status**: In Review
**Priority**: high
**Assigned To**: feature-developer-f5
**Estimated Effort**: 1 day
**Created**: 2026-07-28
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: doc-curation audit (operator-approved in full, 2026-07-28)
— `.kit/context/reviews/DOC-CURATION-AUDIT-2026-07-28.md` (the
binding disposition table with per-doc rationale, citations, and
verifier notes; this spec only summarizes it)
**Related**: KIT-0059 (0.9.0 set — coordination note in F2),
KIT-0067 (created STARTING-A-PROJECT, the move target)
**Sequenced before**: the 0.9.0 release task

## Overview

Execute the operator-approved curation: 5 archives/deletions, 1
merge, 6 trims, and the README rewrite (580 → ~120 lines) with two
new reference pages. Every disposition was adversarially verified
against live citations — the report is the checklist; re-verify each
citation list against current main before acting (the audit ran on
`0294bc3`).

## Requirements

- **F1 — archives/deletions (5)**: empty `docs/prd/` (delete);
  `.kit/docs/TESTING.md` → `docs/archive/`;
  `.kit/context/workflows/RESEARCH-QUALITY-STANDARDS.md` →
  `docs/archive/`; `.adversarial/docs/EVALUATION-WORKFLOW.md`
  1-line tombstone → repoint citers to
  `.claude/skills/code-review-evaluator/SKILL.md`, then delete;
  `.adversarial/templates/arch-assess-input-template.md` →
  `docs/archive/` + drop the arch-assess entry from
  create-project.md's brace-glob (per the report's note). Every
  removal: repo-wide citer grep pasted in the PR.
- **F2 — trims (6)**: per the report's cut lists. Notables:
  AGENT-CREATION-WORKFLOW 902L → its useful weight;
  MANIFEST-UPGRADE-GUIDE's frozen 2.0.0 example manifest → pointer
  to live `scripts/.core-manifest.json` (**coordination**: this
  satisfies a KIT-0059 checklist item early — update KIT-0059's
  task file line 44 and the deprecation-note reference in the same
  PR, per the verifier's note). Kept sections stay verbatim —
  every live citer points at kept content (verified); do not
  reword what you don't cut.
- **F3 — merge (1)**: TEST-SUITE-WORKFLOW.md content →
  TESTING-WORKFLOW.md (which is also getting F2-trimmed — do the
  merge and trim as one edit); tombstone-free delete after citer
  repoint.
- **F4 — README rewrite**: execute the section table in the report
  verbatim (stay/move/drop per section). New pages:
  `docs/LINEAR-INTEGRATION.md` (the 66-line Linear section) and
  `docs/UPDATING-YOUR-PROJECT.md` (update-pulling). Moves into
  STARTING-A-PROJECT preserve that doc's voice (newcomer-facing,
  defers option matrices to `bootstrap --help`). Target ~120 lines;
  hard ceiling 150. Pointers, never copies.
- **F5 — link integrity**: after all moves, a repo-wide grep proves
  no live surface cites a moved/deleted path (historical records
  exempt). The README's doc-links section reflects the new layout.

## Acceptance Criteria

- [ ] All 12 dispositions executed per the report; each checked off
      in the PR body with its citer-grep evidence
- [ ] README ≤150 lines, duplicating nothing that lives elsewhere
- [ ] Two new reference pages exist and are linked
- [ ] KIT-0059 task file updated in the same PR (F2 coordination)
- [ ] No live surface cites a moved/deleted path (F5 grep)
- [ ] Tree-grounded verification requested from the planner before
      merge (this is a prose sweep — the trio is recorded, not
      actioned; the planner's verification is the gate)

## Notes

- Evaluation skipped (planner): dispositions derive from an
  adversarially-verified audit plus operator approval — the same
  skip category as KIT-0069, with the same compensating control
  (planner tree-grounded verification pre-merge).
- patterns.yml applies hard: `displayed_commands_are_contracts`
  (README/STARTING-A-PROJECT print commands — execute each),
  `fix_by_class_not_instance`, `evidence_files_append_only` (the
  audit record and curation report are evidence — never edit).
- Archived files are frozen: no polish, and expect (resolve, don't
  fix) bot nits against `docs/archive/` (KIT-0062 class).
- PR sizing: ONE PR is fine here (mostly moves + one rewrite) but
  split README-rewrite from archival if reviewable lines exceed
  ~500 (PR-SIZE archival rules).
