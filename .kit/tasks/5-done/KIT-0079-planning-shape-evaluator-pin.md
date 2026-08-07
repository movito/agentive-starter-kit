# KIT-0079: Planning-shape targets can't resolve the evaluator pin

> **CLOSED BY REFERENCE (2026-08-07)**: implemented inside KIT-0090
> PR #110 — the evaluator-library pin is read config.yml-first
> (`evaluator_library_version` in `.adversarial/config.yml`, which
> ships in BOTH shapes), pyproject demoted to fallback mirror;
> `test_library_pin_mirrors_agree` deleted as planned. Planning-shape
> repos now resolve the pin without a pyproject. Disposition: done via
> KIT-0090.

> **Consumption note (planner, 2026-08-06)**: KIT-0083 / PR #106 landed
> the canonical pin home this task consumes: `.adversarial/config.yml`
> now carries `evaluator_library_version` (currently INERT — the reader
> still uses pyproject). This task's job narrows to: move
> `_get_evaluator_library_version()` to read config.yml (pyproject as
> fallback mirror at most), and DELETE
> `test_library_pin_mirrors_agree` — that drift test exists only to
> guard the interim two-home state (KIT-0083 retro, follow-up #6).
> Note KIT-ADR-0028 (Proposed): if accepted, this lands inside the
> scripts package rather than the copied script.

**Status**: Done
**Priority**: high (blocks clean intake of every split pair)
**Created**: 2026-07-29

## Overview

`install-evaluators` reads `[tool.adversarial] library_version` from
`pyproject.toml` — which planning-shape repos deliberately don't have
(KIT-0068 made the read fail loud; correct for consumers, wrong for a
shape that ships no pyproject). Found live during the ev-queue
intake: the door's evaluator offer failed in the fresh planning repo;
`--ref v0.10.0` rescued it manually (planner, same day).

## Requirements

- **F1**: give planning-shape targets a pin source — preferred: the
  door passes `--ref <pin>` (read from the KIT's own pyproject at
  create time) when the target lacks pyproject; alternative: seed the
  pin into the planning scaffold's kit-install record and teach
  install-evaluators to read it as fallback. Choose at
  implementation; record why.
- **F2**: the intake agent's Step-5 doctor relay should not show a
  FAIL the flow itself caused — verify a fresh planning intake ends
  evaluator-clean.
- **F3**: also from the same intake run: the intake flow creates no
  GitHub remote for the planning repo, but the workflow (PRs, bots,
  preflight) requires one — add remote creation (private) +
  `--target-github`-style confirmation to the documented intake flow,
  Step 2.5-adjacent. Planner did it manually for ev-queue.

## Evidence

Subagent intake report 2026-07-29 (experiment appendix) + planner
rescue transcript. Also noted there: a credential-scan `|| fallback`
masked a ugrep regex error as SCAN-CLEAN — banked separately in
REVIEW-INSIGHTS.
