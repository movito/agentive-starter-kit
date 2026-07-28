# KIT-0073 Review Starter — Doc Curation + the 96-Line README

**PR**: https://github.com/movito/agentive-starter-kit/pull/99
**Branch**: `feature/KIT-0073-doc-curation` (worktree `../ask-worktrees/KIT-0073`)
**Task**: `.kit/tasks/4-in-review/KIT-0073-doc-curation-and-readme.md`
**Binding checklist**: `.kit/context/reviews/DOC-CURATION-AUDIT-2026-07-28.md`
**Date**: 2026-07-28 (feature-developer-f5)

## ⚠️ Merge gate

**This PR is a prose sweep — the planner's TREE-GROUNDED VERIFICATION
is the merge gate** (KIT-0069 rule), not the evaluator trio and not
bot approval. Planner: run sectioned verifiers against the branch
before merge. Everything below is input to that verification.

## What shipped

All 12 audit dispositions + the README rewrite, in 6 commits:

- `5c5882d` F1: 5 archives/deletions with citer repoints (+ manifest
  glob drop with count tests updated 11→10/49→48 — consequence of
  `.adversarial/docs/` emptying)
- `364243d` F2/F3: 6 trims + TEST-SUITE→TESTING-WORKFLOW merge
- `57c173b` F4: README 580→96 lines (H1 byte-identical), two new
  pages (`docs/LINEAR-INTEGRATION.md`, `docs/UPDATING-YOUR-PROJECT.md`),
  STARTING-A-PROJECT additions (prereqs, --adopt fourth way,
  other-doors, preset rules, degraded modes)
- `8c0acdc` evaluator trio recorded + 2 reproduced prose fixes
- `609eae7` bot round 1 (2 accepted, 1 declined with reasoning)
- `5b47d4d` bot round 2 (BugBot dead-restore-lines, class-widened)

KIT-0059 coordination landed (its checklist line updated; only the
deprecation-note removal remains for 0.9.0). Per-disposition
citer-grep evidence: PR body.

## Gates status

- CI: green on all rounds (3.10/3.12/3.14 + lint)
- Bots: CodeRabbit **APPROVED**; BugBot pass; **4 threads, 4 resolved**
  (each with a reply; one declined with reasoning — the TESTING-WORKFLOW
  `-x`/`--maxfail` line quotes the pre-commit hook verbatim)
- Evaluator trio: **recorded, not actioned unreproduced** (prose-sweep
  exception). Verdicts CONCERNS/CONCERNS/CHANGES_REQUESTED; triage
  table in `.kit/context/reviews/KIT-0073-evaluator-review.md` —
  7 of 8 correctness claims were pre-fix-state reconstructions
  (refuted against the tree), 2 prose notes reproduced and actioned.
- F5 link integrity: repo-wide sweep clean (live surfaces only cite
  live paths); displayed commands executed.

## Verification leads for the planner

1. **The trio's out-of-scope notes** (recorded, unactioned):
   manifest count tests are magic numbers (deliberate, CLAUDE.md);
   `_planning_heredoc_core_version` regex is space-sensitive;
   trailing-slash semantics untested. Pre-existing — judge whether
   any deserves a backlog task.
2. **Kept-section integrity**: the trims were scoped to the audit's
   cut lists — verify no kept content was reworded (spot-check
   MANIFEST-UPGRADE tier table / Agent Model Pins / pull-sync, and
   TESTING-WORKFLOW Known Gotchas, all meant to be verbatim).
3. **Incident during F5 (retro fodder)**: `project reconfigure`,
   executed as a displayed-command check, rewrote identity in 9 files
   because the worktree's Serena name is `agentive-starter-kit-KIT-0073`
   — all collateral reverted same-turn, H1 re-verified byte-identical.
   A worktree-context footgun for `displayed_commands_are_contracts`.
4. **Grep-token blind spot (retro fodder)**: BugBot's real find —
   `.adversarial.bak/docs` evaded the `adversarial/docs` citer grep.
   Item-15 greps close a token, not its variants.

## Operator sweep list

- `/tmp/kit0073-clone-check/` (README clone-URL verification scratch)
- `/tmp/kit0073-pr-body.md` (PR body draft)
