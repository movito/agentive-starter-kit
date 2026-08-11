# KIT-0100: Canon fixes round 2 (F1–F6 + F8) + plugin 2.0.2 — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-11
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/3-in-progress/KIT-0100-canon-fixes-round-2.md`
**Status**: Ready — SCOPE-SPLIT at promotion: this task is **F1–F6 +
F8 + the 2.0.2 release ONLY**; F7/F9/F10 belong to KIT-0101 (their
text in your spec is source-record — do NOT implement them)
**Evaluation**: skipped (planner) — enumerated fixes with verified
anchors (KIT-0092/0099 precedent class); the finding file
`.kit/context/KIT-0099-KIT-FOLLOWUPS.md` carries F1–F6's full detail

**Target Codebase**: This repo (agentive-starter-kit) — single-repo
mode (the repo split, not your working directory).

## Session topology (read before anything else)

- Worktree: `~/Github/ask-worktrees/KIT-0100`, branch
  `feature/KIT-0100-canon-fixes-round-2` — created and provisioned by
  the planner; VERIFY (`git branch --show-current`), never create;
  wrong branch → STOP and ask
- ONE PR for the fixes; the 2.0.2 release step follows its merge
  (same-task, KIT-0092 precedent). Plugin Drift Guard goes RED on
  your PR by design; green at 2.0.2. Say so in the PR body.

## Scope, precisely

**F1–F6** — the six 2.0.1 follow-ups, full detail + suggested fix
shapes in `.kit/context/KIT-0099-KIT-FOLLOWUPS.md` (each was verified
against canon at filing; RE-VERIFY every anchor — KIT-0098's repair
touched neighboring text):

1. Stale "Phase 6"→Phase 7 refs — feature-developer + -f5 (pair rule)
2. `gh run watch` wrapped in a real timeout — ci-checker
3. `--allow-empty` guarded by `git diff --cached --quiet` — check-ci
   (cite the self-review scoped-staging rule)
4. Evaluator fallback stays within the change-shape's tier —
   code-review-evaluator skill
5. Step 2 trio snippet points at the tier rule — feature-developer +
   -f5 (pair rule)
6. wrap-up verifies the review-starter path before printing it

**F8** — interview-first launches carry the opening prompt: sweep
every instruction that says "open a session with <agent>" —
new-project.md's handoff steps, project-intake.md's own Step 5 "Next
action" line, bootstrap/README first-session texts if they name an
agent — to either include the message in the command
(`claude --agent project-intake "Begin the intake."`) or state "the
agent waits for your first message — type begin". Add one sentence to
each FIRST-TURN CONTRACT block acknowledging it fires on the first
USER message. Grep-derive the sweep list; record it in the PR.

**Release 2.0.2** — the KIT-0099 recipe: refresh changed files into
`~/Github/agentive-skills` (clone current on main; work on a branch,
PR there, CodeRabbit reviews it), roster.yaml hashes, plugin.json +
marketplace.json → 2.0.2, CHANGELOG entry (fix families). The
marketplace README's Maintenance section documents the namespacing
transform — follow it (`/preflight` → `/agentive-workflow:preflight`
in plugin copies; never namespace script paths, `agentive` CLI calls,
or evaluator names). Post-merge verification: drift guard GREEN (run
URL), `claude plugin update agentive-workflow@agentive-skills` lands
2.0.2, `claude plugin list` cited.

## Ground rules (standing policy — cited, not restated)

Pair-identity + evaluator-ordering contract tests must stay green
(update pins in the same commit if a fix legitimately rewords a
sentinel); review-surface budget (~500 prose lines — F1–F6+F8 is
well under; if it isn't, stop and report); fast-tier-only +
`--format diff` (prose-shaped); circuit breaker; every sweep's end
state grep-verified (the sweep-completeness class — F1's Phase-6 refs
and F8's launch instructions BOTH get a class grep, quoted in the PR).

## Out of scope — do not touch

- **F7 / F9 / F10** (KIT-0101 — even though their text sits in your
  spec file as source record)
- KIT-0074/0094/0095; the door's code beyond nothing (F1–F6+F8 are
  all `.claude/` prose); sync machinery; kit `.claude/` content
  beyond the enumerated fixes

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0100-canon-fixes-round-2.md`
**Finding detail**: `.kit/context/KIT-0099-KIT-FOLLOWUPS.md` (F1–F6); the spec's F8 block
**Release recipe**: KIT-0099 spec + agentive-skills README §Maintenance
