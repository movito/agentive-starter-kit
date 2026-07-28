# KIT-0073 Handoff — feature-developer

**Task**: `.kit/tasks/2-todo/KIT-0073-doc-curation-and-readme.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-28 (planner-f5)
**Estimated effort**: 1 day

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0073/`** — branch
`feature/KIT-0073-doc-curation`, real per-worktree venv. Run
`git pull --ff-only` **and verify `git rev-parse HEAD` matches
`origin/main`** first. Absolute paths / `git -C` throughout. Serena:
absolute worktree path only.

## Mission

Execute the operator-approved curation.
**`.kit/context/reviews/DOC-CURATION-AUDIT-2026-07-28.md` is the
binding checklist** — per-doc dispositions, cut lists, citations,
verifier notes. The spec's F-items organize it; where they and the
report differ in detail, the report wins. The audit ran on `0294bc3`
— re-verify each citation list against current main before acting.

## Working rules that bind hardest here

- **Grep discipline**: `grep -Rn` only (rg has false-empty modes
  here); class sweeps indentation-tolerant (`^\s*` + token);
  historical records (retros, reviews, done/canceled tasks, .kit/adr,
  CHANGELOG, docs/archive) are exempt from citer counts AND from
  editing.
- **Evidence files are append-only**: the audit record, curation
  report, and cruft-audit record get read, never edited — even when
  they cite paths you're moving.
- **Items 15/16**: after every token fix, grep the file; execute
  every command the README/reference pages display; verify every
  claim on lines you edit.
- **README moves are rewrites-in-voice, not copy-pastes**:
  STARTING-A-PROJECT is newcomer-facing and defers option matrices
  to `bootstrap --help` — content moving in adopts that register.
  The two new reference pages get the standard doc header style.
- **KIT-0059 coordination (F2)**: replacing MANIFEST-UPGRADE-GUIDE's
  frozen example manifest satisfies a KIT-0059 checklist item —
  update `.kit/tasks/1-backlog/KIT-0059-*.md:~44` and its
  deprecation-note reference in the SAME PR (report's verifier note
  has specifics).
- **Prose-sweep gate**: record one trio run for Gate 5 but action
  nothing unreproduced; when the PR is thread-clean, tell the
  planner it's ready for TREE-GROUNDED VERIFICATION — that
  verification (not the trio) is this PR's merge gate.

## Test approach

- Link-integrity is the test surface: F5's repo-wide grep after all
  moves; run `pytest` (some tests assert doc existence — e.g.
  about-adr.md has one; find any that pin paths you touch BEFORE
  moving) and `./scripts/core/ci-check.sh` before pushing.
- README/pages: run every displayed command once
  (`displayed_commands_are_contracts`).
- Scratch: mktemp -d; list leftovers.

## Out of scope

- Rewording KEPT sections beyond the report's cut lists; the 0.9.0
  removals; KIT-0062's config; any agent/skill content changes
  beyond citer repoints.

## PR sizing

One PR expected (moves + one rewrite). Split per PR-SIZE archival
rules if reviewable lines > ~500: (1) README + new pages,
(2) archives/trims/merge.
