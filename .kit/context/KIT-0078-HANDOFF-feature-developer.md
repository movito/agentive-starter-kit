# KIT-0078 Handoff — feature-developer

**Task**: `.kit/tasks/2-todo/KIT-0078-cold-start-path.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-29 (planner-f5)
**Estimated effort**: 1 day

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

Root: `/Users/broadcaster_three/Github/ask-worktrees/KIT-0078/`,
branch `feature/KIT-0078-cold-start`, real venv. `git pull --ff-only`
+ verify rev-parse == origin/main first. Serena by absolute path.
Never `project reconfigure` here.

## Mission

The operator's verdict IS the design principle: **"tell the user
what to do from the README, not ask them to guess."** Docs instruct
in sequence; agents confirm and receive. The spec's five recorded
snags are your checklist; its F1-F5 are the shape. Nothing in this
task adds capability — it re-sequences what exists so a newcomer
with empty hands succeeds using only what's on screen.

## Verified anchors (re-verify)

- Entry surfaces today: `.claude/commands/new-project.md` (routes to
  intake or door), `.claude/agents/project-intake.md` (has a fresh
  FIRST-TURN CONTRACT block, 576266a — extend, don't duplicate),
  `.claude/agents/create-project.md` (same block; F2 decides its
  demotion — grep for what still needs it before folding),
  `.kit/launchers/launch` (KEPT deliberately; work-session menu, not
  creation — KIT-0075 owns modernization).
- Keystroke-literal pattern established at 9020969
  (STARTING-A-PROJECT "How every kit conversation starts" + three
  sites + preset.example) — extend that pattern, keep its wording.
- README quickstart (96-line README — keep it lean; sequences live
  in STARTING-A-PROJECT, README points).
- The snag-4 tool error: AskUserQuestion with free-text-shaped
  options → the F4 rule. Check both command texts + intake.

## Context you must not lose

- displayed_commands_are_contracts incl. the CLAIMS clause: every
  printed instruction executed/verified in its addressed context.
- Prose/UX diff: fast-only trio for Gate 5; planner tree-grounded
  verification is the merge gate; F5's two cold-start transcripts
  are the real acceptance evidence.
- Items 15/16 (variants, representations); evidence files
  append-only.
- KIT-0075 is promoted to follow immediately — do NOT absorb its
  scope (launcher internals, native invocation); your F2 demotions
  only touch docs/pointers/agent text.

## Out of scope

Launcher internals (KIT-0075); door/engine logic; new capabilities.

## PR sizing

One PR (~docs + two command texts + two agent texts + transcripts).
