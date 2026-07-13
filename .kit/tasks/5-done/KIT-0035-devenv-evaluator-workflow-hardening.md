# KIT-0035: Dev-env & evaluator-workflow hardening (KIT-0032 + KIT-0040 retros)

**Status**: Done
**Priority**: medium
**Assigned To**: unassigned
**Estimated Effort**: 2-4 hours
**Created**: 2026-06-27
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent**: KIT-0032 (build upgrader agent) — surfaced these in retro
**Related**: KIT-0034 (preflight/bootstrap hardening) — the preflight Gate-1
follow-up from this same retro was folded into KIT-0034 §F4, not duplicated here.

## Overview

The KIT-0032 retro (`.kit/context/retros/KIT-0032-retro.md`) produced five
process/tooling follow-ups. One (preflight Gate 1 pending-vs-failed) went to
KIT-0034 since that task already hardens preflight. The remaining four are
collected here. They are unrelated in code but share a theme: removing
developer-experience friction that cost real time during KIT-0032 — a phantom CI
failure, a mid-session evaluator blocker, an avoidable bot-round cascade, and a
brittle-grep gap between the upgrader agent and the guide it mirrors.

The KIT-0040 retro (`.kit/context/retros/KIT-0040-retro.md`, 2026-07-05) added
three more items of the same theme (F5–F7 below): an evaluator auto-cancel trap
in non-TTY sessions, v2-evaluator discoverability, and a twice-re-litigated
known non-goal that needs one documented sentence.

## Requirements

### Functional Requirements

- **F1 — venv tool-version drift warning in `ci-check.sh`** *(highest value)*.
  KIT-0032 hit a *phantom* Black failure: the local `.venv` carried Black
  `23.12.1` while `pyproject.toml` pins `26.x`, so `ci-check.sh` (which activates
  `.venv`) reformatted `tests/test_pattern_lint.py` and failed, while the
  pinned/CI Black considered it clean — on a markdown-only change that could not
  affect Black. Add a cheap preflight in `ci-check.sh`: compare the active
  `black --version` against the `pyproject.toml` pin and, on mismatch, print a
  one-line warning ("venv Black X differs from pinned Y — run
  `pip install -e \".[dev]\"`") **before** the formatting step, so a stale venv
  reads as an environment issue, not a code failure. Consider extending to isort
  if cheap.

- **F2 — Document the `claude-code` evaluator's `ANTHROPIC_API_KEY` need**. The
  Phase-7 evaluator trio's `claude-code` (Anthropic) evaluator silently failed
  mid-session because `ANTHROPIC_API_KEY` was commented out in `.env`. Add a note
  to the evaluator docs (`.adversarial/evaluators/README.md` or the Phase-7
  / code-review-evaluator skill) that the `claude-code` evaluator requires the key
  uncommented in `.env`, so it's known up front rather than discovered as a
  blocker. (Do not add the key anywhere — doc only.)

- **F3 — Evaluate evaluator-trio-before-PR ordering for doc-heavy tasks**. In
  KIT-0032, running Phase 7 (evaluator trio) *after* opening the PR meant each
  evaluator-driven rewrite triggered a fresh bot round (4 rounds total for a
  single doc file). Evaluate whether, for documentation/agent-spec deliverables,
  the feature-developer workflow should run the evaluator trio **before** PR open
  (Phase 7 → 5/6) to collapse bot cycles. Output: a recommendation + a small
  workflow-doc amendment if adopted — **not** an unconditional reorder (code-heavy
  tasks still benefit from CI/bots first). Decision-only until the planner agrees.

- **F4 — Harden the brittle greps in `docs/PLUGIN-UPGRADE-GUIDE.md`**. All three
  Phase-7 evaluators independently flagged brittle output-matching in the upgrader
  agent (ANSI colours, URL-form marketplace source line, `@` vs `(source)` row
  format, case-sensitive flat-ref grep, `grep -A8` Provenance window). These greps
  are inherited **verbatim from the guide** — the agent must mirror the guide, so
  the fix belongs in the guide, then the agent re-syncs. Make the guide's
  detection patterns resilient (e.g. `GitHub.*movito/agentive-skills` rather than a
  fixed-paren match) and update `.claude/agents/upgrader.md` to match in lockstep.
  See the KIT-0032 evaluator review for the specific patterns:
  `.kit/context/reviews/KIT-0032-evaluator-review.md` ("Follow-up to raise against
  the guide").

- **F5 — `prepare-review-input.sh` must surface `ADVERSARIAL_UNATTENDED`**
  *(KIT-0040 retro #1)*. In a non-TTY agent session, a >50k-token evaluator
  input auto-cancels unless `ADVERSARIAL_UNATTENDED=1` is exported — but the
  script's "Next steps" output lists the three evaluator commands without
  mentioning it, so every future agent burns one failed evaluator invocation
  discovering it. Either add the export to the next-steps output, or auto-set
  it when stdout is not a TTY (prefer auto-set if it stays a one-liner).

- **F6 — Make the v2-evaluator preference executable** *(KIT-0040 retro #2)*.
  The agent spec says "prefer -v2 where installed," but discovering that
  `code-reviewer-fast-v2` exists (while `code-reviewer` has no v2) requires
  `ls .adversarial/evaluators/*/`. Add the discovery step to the
  code-review-evaluator skill (`.kit/skills/code-review-evaluator/`) — a
  one-line "list installed evaluators first" command — or point at an
  `adversarial list` command if the CLI has one.

- **F7 — Document the fenced-code-marker fail-fast as a known non-goal**
  *(KIT-0040 retro #3)*. A literal BEGIN-marker line inside a fenced code
  sample (with no parseable region for that name) makes `kit_markers.py`
  fail fast and abort the merge. This was flagged by evaluators twice on
  PR #70 and declined twice with the same reasoning (loud abort beats silent
  clobber; markdown-fence parsing is out of scope for a stdlib helper). Add
  one sentence to `.kit/docs/KIT-MIGRATION-PLAYBOOK.md` (or the bootstrap
  docs) so future reviewer/evaluator rounds don't re-litigate it.

### Non-Functional Requirements

- **N1**: No new dependencies; `ci-check.sh` stays shell + the existing toolchain.
- **N2**: F1's warning must not fail the build on its own — it warns; the existing
  Black step remains the gate.
- **N3**: F4 keeps the guide as the source of truth; the agent never diverges from
  it (KIT-0032 design rule: "if the agent and guide disagree, the guide wins").

## Acceptance Criteria

- [ ] `ci-check.sh` warns (does not fail) when active Black differs from the
      `pyproject.toml` pin, naming the reinstall command
- [ ] Evaluator docs state the `claude-code` evaluator needs `ANTHROPIC_API_KEY`
      uncommented in `.env`
- [ ] A written recommendation on evaluator-before-PR ordering for doc-heavy tasks
      (with a workflow-doc amendment iff adopted)
- [ ] `docs/PLUGIN-UPGRADE-GUIDE.md` detection greps made resilient, and
      `.claude/agents/upgrader.md` re-synced to match
- [ ] Any `ci-check.sh` logic change has test coverage if a harness exists, else a
      documented manual check
- [ ] `prepare-review-input.sh` surfaces (or auto-sets) `ADVERSARIAL_UNATTENDED`
      for non-TTY sessions
- [ ] code-review-evaluator skill includes an evaluator-discovery step (v2
      variants findable without spelunking)
- [ ] Fenced-code-marker fail-fast documented as a known non-goal in the
      migration/bootstrap docs

## Notes

- Source: `.kit/context/retros/KIT-0032-retro.md` (Process Actions, F1–F4) and
  `.kit/context/retros/KIT-0040-retro.md` (Process Actions 1–3, F5–F7; folded
  in by planner 2026-07-05 — same dev-env/evaluator-friction theme). The
  fourth KIT-0040 action (generalize the stub-`gh` harness) is implementation
  work of a different scope — tracked as KIT-0041.
- F1 is the highest-value, most self-contained item; F2/F3 are doc/decision work.
  F4 can be split out (it touches the guide + agent, a different surface) if the
  planner prefers smaller PRs.
- The fifth retro action (preflight Gate 1 pending-vs-failed) lives in **KIT-0034
  §F4** to keep all preflight changes in one PR.

## PR Plan

Two PRs (planner decision, from the 2026-07-05 evaluation):

- **PR 1 — dev-env & evaluator friction**: F1 (ci-check venv-drift warning),
  F2 (ANTHROPIC_API_KEY doc), F3 (ordering recommendation), F5
  (ADVERSARIAL_UNATTENDED surfacing), F6 (v2 discoverability), F7
  (fenced-code non-goal doc). Small diffs, doc-heavy.
- **PR 2 — upgrade-guide grep hardening**: F4 only
  (`docs/PLUGIN-UPGRADE-GUIDE.md` + `.claude/agents/upgrader.md` in
  lockstep). Different surface, different reviewer context; N3's
  guide-wins rule makes this an atomic pair.

## Evaluation (2026-07-05)

`arch-review-fast` (gemini-2.5-flash): **REVISION_SUGGESTED** — bundle spans
too many surfaces; individual requirements judged "sound and well-defined".
Log: `.adversarial/logs/KIT-0035-devenv-evaluator-workflow-hardening--arch-review-fast.md`.
Planner disposition:

- **Accepted (the kernel)**: the review-surface concern is real at 7
  requirements / 8+ files. Addressed with the two-PR plan above rather than
  a task split — F4 is the one genuinely different surface.
- **Declined (task split into 3+ tickets and a standing "friction
  backlog")**: single-operator kit; retro-sourced bundles are the working
  convention (KIT-0034/0040 precedent) and per-requirement progress stays
  visible in the acceptance criteria. If a future friction bundle exceeds
  ~7 items or two PRs, revisit.
