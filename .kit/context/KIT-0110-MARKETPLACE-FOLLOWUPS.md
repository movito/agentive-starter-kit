# KIT-0110 — marketplace-side follow-ups from PR movito/agentive-skills#10

**From**: feature-developer-f5 (KIT-0110 session)
**To**: planner — the KIT-0109 followups-file pattern; these are gaps
against the MARKETPLACE repo, out of KIT-0110's scope by the handoff's
routing rule ("marketplace-side → the KIT-0109 followups-file pattern
via the planner")
**Date**: 2026-08-14

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

## F3 — `merge_group` trigger if a merge queue is ever adopted

CodeRabbit noted the verify workflow should carry a `merge_group:`
trigger IF `main` uses a merge queue. It does not today; declined on
the thread. If the operator ever enables a queue there, the trigger
must be added or the required check blocks the queue.
