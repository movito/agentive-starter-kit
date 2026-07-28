# KIT-0035 Handoff — feature-developer

**Task**: `.kit/tasks/5-done/KIT-0035-devenv-evaluator-workflow-hardening.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-05 (planner-f5)
**Estimated effort**: 3–5 hours across two PRs (see PR Plan in the task file)

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## Mission

Remove seven pieces of dev-env/evaluator friction recorded across the
KIT-0032 and KIT-0040 retros. Two PRs: PR 1 carries F1+F2+F3+F5+F6+F7
(small, doc-heavy); PR 2 carries F4 alone (upgrade-guide greps + upgrader
agent, an atomic lockstep pair).

## Verified current state (planner checked 2026-07-05 — post-PR #71)

- `.kit/skills/self-review/SKILL.md` is **v1.2.0** (updated by PR #71 with
  new Step 3 items 8–9 and two Quick Reference rows). No KIT-0035
  requirement targets this file — but if you touch any shared checklist,
  do NOT renumber items 8–9 away. Read the file fresh before any edit.
- Black pin is `black==26.3.1` at `pyproject.toml:36` (the spec's "26.x"
  prose predates a bump). F1 must parse the pin from `pyproject.toml`, not
  hardcode a version.
- `scripts/core/prepare-review-input.sh` currently has **no**
  `ADVERSARIAL_UNATTENDED` or TTY handling (grep verified empty) — F5 is
  greenfield within that script.
- v2 evaluator variants exist **only under `.adversarial/evaluators/google/`**:
  `arch-review-fast-v2`, `code-reviewer-fast-v2`, `gemini-deep-v2`,
  `gemini-flash-v2`. `openai/code-reviewer` has no v2 (as the KIT-0040
  retro noted). F6's discovery step: `ls .adversarial/evaluators/*/`.
- code-review-evaluator skill: `.kit/skills/code-review-evaluator/SKILL.md`.

## Implementation guidance

### PR 1

- **F1 (highest value)** — `scripts/core/ci-check.sh`: Black step is step
  1/6 at lines ~55–62 (`black --check --diff .`). Before it, compare the
  active `black --version` against the `pyproject.toml` pin (line 36,
  `black==26.3.1` today — parse, don't hardcode) and print a one-line
  warning naming `pip install -e ".[dev]"` on mismatch. Warn only — the
  existing Black step remains the gate (N2). Extend to isort only if it's
  genuinely cheap. Per KIT-0040: `verify-ci.sh`-style scripts have no test
  harness; a documented manual check (run with a deliberately stale venv)
  satisfies the acceptance criterion.
- **F2** — one note in `.adversarial/evaluators/README.md` (and/or the
  code-review-evaluator skill): the `claude-code` evaluator needs
  `ANTHROPIC_API_KEY` uncommented in `.env`. Doc only; never add a key.
- **F3 (decision-only)** — write the recommendation on evaluator-trio-
  before-PR-open for doc-heavy tasks. Evidence base: KIT-0032 (4 bot rounds
  post-hoc), KIT-0033 (evaluator-while-CI-pending worked well), KIT-0040
  retro's "external-finding yield concentrates on fresh code". Deliver as a
  short section in the code-review-evaluator skill or a workflow doc; amend
  the feature-developer workflow ONLY if you recommend adoption, and keep
  it scoped to doc-heavy deliverables. Planner pre-agrees with a
  conditional reorder; the written rationale is the deliverable.
- **F5** — `scripts/core/prepare-review-input.sh`: prefer auto-setting
  `ADVERSARIAL_UNATTENDED=1` when `[ ! -t 1 ]` if it stays a one-liner
  (with an echo saying so); otherwise add the export line to the printed
  "Next steps". Context: in non-TTY sessions a >50k-token input
  auto-cancels without it (KIT-0040 retro #1).
- **F6** — add the discovery step to the code-review-evaluator skill: list
  installed evaluators (`ls .adversarial/evaluators/*/`) before choosing,
  prefer `-v2` where present. Verify whether the `adversarial` CLI has a
  `list` command before pointing at it — if unsure, the `ls` is the safe
  instruction.
- **F7** — one sentence in `.kit/docs/KIT-MIGRATION-PLAYBOOK.md` (bootstrap
  section): a literal BEGIN-marker line inside a fenced code sample (with
  no parseable region of that name) makes `kit_markers.py` fail fast by
  design — loud abort beats silent clobber; fence-aware parsing is a
  non-goal. This was declined twice on PR #70; the sentence exists to stop
  re-litigation.

### PR 2 — F4

- Source list of brittle greps: `.kit/context/reviews/KIT-0032-evaluator-review.md`
  ("Follow-up to raise against the guide") — ANSI colours, URL-form
  marketplace source line, `@` vs `(source)` row format, case-sensitive
  flat-ref grep, `grep -A8` Provenance window.
- Fix in `docs/PLUGIN-UPGRADE-GUIDE.md` first (it is the source of truth),
  then update `.claude/agents/upgrader.md` to mirror — same commit, never
  let them diverge (N3). Where the agent adds resilience the guide lacks,
  move that resilience INTO the guide.
- Test approach: run the hardened greps against real current output
  (`claude plugin marketplace list` etc. where feasible) and paste
  before/after matches in the PR description.

## Preflight note (both PRs)

Gates 5/6 key artifacts to a single task ID (exact-name match,
`preflight-check.sh:487`). Both PRs belong to the one task KIT-0035, so
standard naming works — no bundle pointer files needed. For PR 2 use the
same task ID; the review starter and evaluator record from PR 1 will
already exist — update them rather than duplicating (KIT-0042 will handle
multi-task bundles properly; this task is not that case).

## Test approach

- `./scripts/core/ci-check.sh` before each push (F1's warning must not
  fail the run — verify both match and mismatch paths).
- F1 manual verification: temporarily `pip install black==25.1.0` in a
  scratch venv or document the simulated check; record in PR 1's
  description.
- No pytest surface expected; if F1's pin-parsing becomes a helper
  function, put it where `patterns.yml` says CLI-layer logic lives and
  test it.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED (bundle breadth) — planner accepted
the kernel as the two-PR plan, declined the task split. Disposition in the
task file; log in
`.adversarial/logs/KIT-0035-devenv-evaluator-workflow-hardening--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Adding any API key anywhere (F2 is doc-only)
- Changing the evaluator trio composition or the adversarial CLI
- `.kit/skills/self-review/SKILL.md` edits (nothing in this task needs it)
- KIT-0041/KIT-0042 items (harness generalization, bundle gates)
- Downstream repos (operator deferral stands)

## PR sizing

PR 1 ≈ 6 small diffs across scripts/docs/skills (< 200 lines). PR 2 ≈ two
files in lockstep (< 200 lines). Do not merge them into one — the split is
the accepted evaluator finding.
