# KIT-0069 Handoff — feature-developer

**Task**: `.kit/tasks/3-in-progress/KIT-0069-audit-truth-sweep.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-27 (planner-f5)
**Estimated effort**: 1-1.5 days

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0069/`** — branch
`feature/KIT-0069-audit-truth-sweep`, fully provisioned. Run
`git pull --ff-only` first. Absolute paths / `git -C` throughout.

**⚠️ VENV HAZARD (KIT-0065 incident, fix pending in KIT-0071)**: this
worktree's `.venv` is a SYMLINK to the primary clone's venv. NEVER
run `venv --clear`, venv rebuilds, or delete `.venv` here — a rebuild
through the symlink destroys the primary's venv. `pytest` through it
is fine (read/execute only). If you think you need a venv operation,
stop and say so instead.

## Mission

Make every live prose surface tell the truth about the current kit.
The audit record is your checklist; the ownership rule in the spec is
binding — every A-number you own gets a one-line disposition in the
PR body (fixed / already-fixed / defer-with-reason), no silent drops.

## Evidence base

`.kit/context/reviews/PRE-090-CRUFT-AUDIT-2026-07-24.md` — findings
A00-A91 with verified evidence. Your exclusions (owned elsewhere) are
enumerated in the spec's Ownership rule; note KIT-0068 (PR #93) and
KIT-0065 (PR #94) have MERGED since the audit — some of your targets
were partially touched (e.g. EVALUATION-WORKFLOW's aider refs are
fixed but its stale verdicts/paths remain yours; A46's 53%-coverage
claims are untouched). Re-verify each finding against CURRENT main
before editing — "already fixed" is a legitimate disposition.

## Context you must not lose

- **Fix by CLASS, then grep the class repo-wide** (spec F1) — the
  audit found instances, not exhaustive sets. Paste the class greps
  in the PR.
- **Self-review item 15 applies constantly here** (added from
  KIT-0065's one regression): after fixing a token in a file, grep
  THAT FILE for the token before moving on. This task is hundreds of
  token fixes — item 15 is your main defense against a long bot tail.
- **Expect the prose-hardening self-feeding tail** (KIT-0066
  insight): bots find nits INTRODUCED by wording fixes. Batch
  holistically, fix per-file completely, expect an extra round
  anyway.
- **Dangerous-contradiction priorities first** (spec F2):
  LINEAR-SYNC-BEHAVIOR's `project sync` advice, 53%-vs-80% coverage,
  powertest-runner's Task-spawning instruction, /check-spec's
  uninstalled evaluator (check what evaluator library v0.10.0
  actually ships before choosing fix-vs-retire), security-reviewer's
  foreign LinkedIn/Dropbox rules.
- **Model pins**: verify current model IDs against live Anthropic
  docs at implementation time — not memory, not this handoff.
- **Templates prove themselves by generation** (F3): scratch-generate
  one agent via create-agent.sh after fixing AGENT-TEMPLATE; the
  generated file must carry no stale content.
- **Don't touch KIT-0067's set**: launchers, onboarding agent,
  AGENT-SYSTEM-GUIDE/tmux-tips/COVERAGE-WORKFLOW/EVALUATION-WORKFLOW
  restructuring, serena artifacts, docs/adr ownership — text-level
  A-number fixes inside files 0067 will archive are "defer to
  KIT-0067" dispositions, not edits.
- Historical records stay untouched (retros, done/canceled tasks,
  ADRs, review records).

## Test approach

- Ordering rule: local checks green → evaluator trio
  (`echo y | ADVERSARIAL_UNATTENDED=1 …`; log-file-with-verdict is
  the proof; `git status` after every run) → PR open.
- Mostly-prose diff: expect preflight Gates 2/3 to say "docs-only"
  while bots review anyway (known divergence, KIT-0062 F7 owns it).
- Mind the trailing-whitespace hook when touching files with
  embedded evaluator output (Phase-5 note).
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

Spec evaluation skipped by design (planner): the checklist derives
from an audit where every finding survived adversarial verification;
disposition in the spec's Notes. Trio still runs pre-PR.

## Out of scope

Per the spec's Ownership rule — KIT-0067's structural set, KIT-0065's
aider set (merged), KIT-0068's behavioral set (merged), 0.9.0
removals.

## PR sizing

Split allowed by area if > 500 reviewable lines:
(1) agents + skills + commands + templates, (2) docs + workflows +
top-level. Lead-task naming per the bundle convention if split.
