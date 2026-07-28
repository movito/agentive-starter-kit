# KIT-0035 Review Starter — Dev-env & Evaluator Friction

**Task**: `.kit/tasks/4-in-review/KIT-0035-devenv-evaluator-workflow-hardening.md`
**PRs**: [#72](https://github.com/movito/agentive-starter-kit/pull/72) (PR 1 — F1/F2/F3/F5/F6/F7) · [#73](https://github.com/movito/agentive-starter-kit/pull/73) (PR 2 — F4)
**Date**: 2026-07-06
**Agent**: feature-developer-f5

## What to review

Two independent PRs (both from `main`, disjoint file sets — merge in either
order; the planner-agreed split keeps F4's guide+agent lockstep pair its own
reviewer context):

### PR 1 (#72) — six friction items, ~6 small diffs

1. **F1** `scripts/core/ci-check.sh` — warn-only Black pin-drift preflight.
   Key check: it must never set `FAILED` (N2); the pin is parsed from
   `pyproject.toml`, never hardcoded.
2. **F2/F3/F6** `.kit/skills/code-review-evaluator/SKILL.md` (v1.3.0) —
   ANTHROPIC_API_KEY-uncommented note, adopted doc-heavy evaluator-before-PR
   ordering (the F3 recommendation + rationale), evaluator-discovery step
   (`adversarial list-evaluators`, prefer `-v2`).
3. **F3** exception note in `feature-developer.md` (2.1.0) and
   `feature-developer-f5.md` (1.1.0) — kept in lockstep.
4. **F5** `scripts/core/prepare-review-input.sh` (1.5.0) — prints
   `export ADVERSARIAL_UNATTENDED=1` in Next steps when stdin or stdout is
   non-TTY.
5. **F7** `docs/DISTRIBUTION-ARCHITECTURE.md` §5(b) — fenced-code-marker
   fail-fast recorded as a known non-goal (anti-re-litigation sentence).
6. Core scripts 3.0.0 → 3.1.0 (`VERSION` + manifest `core_version`).

### PR 2 (#73) — F4 only, guide + agent lockstep

`docs/PLUGIN-UPGRADE-GUIDE.md` detection greps hardened;
`.claude/agents/upgrader.md` (1.1.0) mirrors every pattern (N3: guide wins).
All patterns verified against live `claude plugin` CLI output — before/after
table in the PR description. Note the round-1 evaluator catch: the first
draft of the marketplace grep was bypassable by a local checkout path; the
committed version is anchored to the `Source:` field.

## Verification already done

- `ci-check.sh` full run green on PR 1 (F1 silent on matching venv);
  mismatch path simulated with the exact KIT-0032 stale-version string;
  missing-black path verified safe under `set -e`.
- F5 verified live (this task's own evaluator prep printed the export line).
- Evaluator trio ran BEFORE PR open on both PRs (dogfooding F3).
  Full disposition: `.kit/context/reviews/KIT-0035-evaluator-review.md`
  (PR 1: 4 accepted / 7 declined-with-evidence; PR 2: 2 accepted /
  8 declined-with-evidence — including two empirically disproven sed claims).
- Bots on PR 1: CodeRabbit APPROVED, BugBot pass, zero threads, round 1.

## Known trade-offs (deliberate, documented in the review record)

- F1 is fail-open: a non-`==` pin format silently disables the warn-only
  check (drift is only well-defined against an exact pin).
- PR 2's plugin-list grep is not left-anchored (a *prefixed* sibling name
  would still match) — left-anchoring would couple to the volatile `❯`
  bullet glyph, the exact brittleness class being removed.

## After merge

- `/retro` for the session.
- KIT-0041 (stub-`gh` harness generalization) and KIT-0042 (multi-task
  bundle gates) remain separately tracked.
