# KIT-0090 — PR 1 Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/108
**Branch**: `feature/KIT-0090-extract-scripts-package` (worktree
`~/Github/ask-worktrees/KIT-0090`)
**Scope**: PR 1 of 4 (KIT-ADR-0028 phase 1) — package skeleton +
`gitio` + `lifecycle` + typed models + shim. **The task stays
in-progress**: PRs 2–4 (doctor, evaluators/preflight/review-input/
worktree lib, publish+dogfood) follow in this session.

## Gate status

- **Local suite**: 970 fast / full green at every push
- **CI**: green on head `4690c73` via **manually dispatched** runs
  (31128654133 on d0aa929, 31128839170 on 4690c73). ⚠️ The
  `pull_request` event produced NO runs across four pushes — the known
  KIT-0067-era anomaly. **The dispatched run on the branch is the CI
  proof for any merge-go**; the PR's checks rollup will not show it.
- **Bots**: BugBot round 1 pass; CodeRabbit 10 actionable + BugBot 2 +
  CodeRabbit 2 follow-ups = **16 threads, all replied and resolved**
  (14 taken with fixes/tests, 1 declined with reasoning
  [domain-error-strategy rewrite — phase-1 behavior preservation], 1
  reply-correction).
- **Evaluator trio**: run BEFORE PR open (ordering rule) — 6 rounds;
  dispositions in `.kit/context/reviews/KIT-0090-pr1-evaluator-review.md`,
  including a recorded o3 oscillation (underscore boundary,
  rounds 4↔5).

## What a human reviewer should actually look at

1. **Root discovery rule** (`agentive_kit/root.py`): `.kit/` +
   `CLAUDE.md`, marker-independent — this admits the kit repo itself
   (no kit-install region upstream). Confirm you're happy with that
   rule as stable API.
2. **KIT-0086 guard semantics** (`lifecycle.sync_coordination_metadata`):
   `agent-handoffs.json` written only when branch == literally
   `main`; undeterminable branch skips (fail-safe). Repos with a
   non-`main` default branch would never auto-update the JSON —
   accepted limitation, recorded.
3. **One deliberate behavior change**: task-ID matching is now
   boundary-anchored (`KIT-1` no longer matches `KIT-1234`); `-` and
   `_` both count as separators.
4. **Sequencing risk** (PR body ⚠️): consumers syncing `main` before
   the PR-4 publish get lifecycle commands that instruct installing a
   not-yet-published package. Merge PRs 1–4 close together, or accept
   the window.

## F6 closure state

- KIT-0086 F1 (single-writer guard): **landed here**, verified by
  mutation + byte-for-byte zero-diff test. F2 (drift WARN) → doctor
  check in PR 2, where KIT-0086 closes by reference.
- KIT-0079: PR 3 (evaluators module).
