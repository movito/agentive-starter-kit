# KIT-0079: Planning-shape targets can't resolve the evaluator pin

**Status**: Backlog
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
