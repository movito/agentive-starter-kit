# KIT-0110 — marketplace-side follow-ups from PR movito/agentive-skills#10

**From**: feature-developer-f5 (KIT-0110 session)
**To**: planner — the KIT-0109 followups-file pattern; these are gaps
against the MARKETPLACE repo, out of KIT-0110's scope by the handoff's
routing rule ("marketplace-side → the KIT-0109 followups-file pattern
via the planner")
**Date**: 2026-08-14

> **PLANNER RULINGS (2026-08-14, at KIT-0110 completion)**:
> **F1 — ACCEPTED as the standing contract**: the falsification-run
> story is the verifier's test regime — every future change to
> `verify_plugin_integrity.py` re-runs the four falsifications
> (green / bump-without-copy / malformed digest / planted files) and
> records them in that PR. Adding pytest infra to a deliberately
> infra-free repo is disproportionate at 206 lines and one operator.
> Revisit if the script grows past trivial or a second contributor
> arrives (same trigger as F4).
> **F2 — homed**: markdownlint job rides the KIT-0105 release PR
> (rider recorded in that spec).
> **F3 — stands as declined-unless-queue** (documented below; no
> action unless a merge queue is enabled).
> **F4 — accepted residual stands** with its recorded revisit trigger
> (external contributors).

## F1 — No executable tests for `verify_plugin_integrity.py`

**Severity**: low (CodeRabbit Trivial, PR #10 round 1, thread
`PRRT_kwDOSj0O5s6ZTwR6`)

The verifier's behavior is currently evidenced by falsification runs
recorded in the PR body (green tree / bump-without-copy / malformed
digest / planted unrostered + hidden files), not by automated fixtures.
The marketplace repo has no test infrastructure at all — adding pytest
fixtures means adding a second workflow (or extending the first) plus a
dev-dependency story to a repo that deliberately has none.

Resolution options for the planner:

- accept the falsification-run story as the standing contract (each
  future change to the script re-runs them, recorded in that PR), or
- spec a small `tests/` + workflow step marketplace-side (the fixture
  set is already enumerated in the CodeRabbit thread), or
- mirror the script into the kit repo's test suite as a
  characterization import (cross-repo path fragility — probably not).

## F2 — markdownlint CI still absent (KIT-0109 retro item 3, still open)

PR #10 added the repo's first workflow, which makes adding a
markdownlint job trivially cheap now (the KIT-0109 retro flagged that
the bots were the entire prose gate). Not done in KIT-0110 — zero
content changes was an acceptance criterion and lint config is its own
decision.

## F4 — Accepted residual: PR-ref execution of the verifier (round 2)

**Severity**: accepted residual (CodeRabbit Major, PR #10 round 2,
thread `PRRT_kwDOSj0O5s6ZUCvf`)

On `pull_request`, the verify workflow executes the PR's own copy of
`scripts/verify_plugin_integrity.py`, so a hostile PR could game its
own check. Declined re-architecture (reusable workflow / second repo)
because: the `push: branches: [main]` trigger re-runs the verifier
from trusted post-merge code (a gamed PR check turns main red on
merge — the loud failure this guard exists for); the threat model is
accidental bump-without-copy by trusted sessions, not adversarial PRs
(single-operator repo, human review on merge, fork PRs get read-only
tokens, no secrets); and a same-repo reusable workflow is still taken
from the PR ref on `pull_request`, so a real fix means
`pull_request_target` (ruled out) or a second repo. **Revisit if the
repo ever takes external contributors.**

## F3 — `merge_group` trigger if a merge queue is ever adopted

CodeRabbit noted the verify workflow should carry a `merge_group:`
trigger IF `main` uses a merge queue. It does not today; declined on
the thread. If the operator ever enables a queue there, the trigger
must be added or the required check blocks the queue.
