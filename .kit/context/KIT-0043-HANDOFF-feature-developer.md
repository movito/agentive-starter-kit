# KIT-0043 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0043-preflight-gates-127-edge-hardening.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-14 (planner-f5)
**Estimated effort**: 2–3 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ WORKTREE PILOT — read first

This is the kit's first worktree-based implementation session. **Your
repository root is `/Users/broadcaster_three/Github/ask-worktrees/KIT-0043/`**
— a git worktree already created by the planner, checked out on
`feature/KIT-0043-preflight-gates-edge-hardening` (tracking origin/main).
The planner's primary clone stays on `main`; do not operate on it.

- `.venv` and `.env` are symlinked into the worktree from the primary
  clone — pytest, ci-check.sh, and evaluators should work as usual.
- Everything else is a normal checkout: commit, push, and open the PR
  from here exactly as always.
- **Pilot duty**: note EVERY worktree-specific friction you hit
  (permission prompts, hook failures, path assumptions, Serena, memory
  gaps) in your retro — they are requirements input for KIT-0044
  (worktree codification).
- If the worktree is fundamentally broken (hooks or venv unusable),
  stop, record what failed, and tell the operator — do NOT fall back to
  working in the primary clone without the operator's OK.

## Mission

Harden preflight Gates 1, 2, and 7 against the edge set that o3 and
fast-v2 flagged convergently across three KIT-0042 evaluator runs
(declined there as out of scope; tracked here).

## Verified runtime facts (planner checked 2026-07-14)

- **F1**: `preflight-check.sh:253` —
  `gh $GH_REPO_ARG run list --commit "$LATEST_SHA" --limit 10 --json ...`.
  The query ALREADY filters server-side by commit, so truncation only
  bites when one SHA has >10 runs. This repo runs ~2 workflows per push —
  the "justify the limit against real run counts" acceptance path is
  likely correct here; a modest limit raise is a fine belt-and-braces.
  Verify the real `gh run list` flag surface before choosing; paste the
  checked command in the PR.
- **F2**: status handling at lines 298–304: `completed:success` → PASS,
  `completed:skipped|neutral` → tolerated, `in_progress|queued` →
  PENDING; **everything else falls to FAIL** — that else-branch is the
  bug. Enumerate current GitHub run statuses from the API docs (e.g.
  `waiting`, `requested`, `pending`, `action_required`) — non-terminal
  unknowns go to PENDING; keep a completed non-success run as FAIL (N3
  from KIT-0034 still binds).
- **F3**: Gate 7 at line 501 —
  `find .kit/tasks/3-in-progress .kit/tasks/4-in-review -name "${TASK_ID}*"`.
  No boundary after the ID. Task files are `<ID>-slug.md`, so
  `"${TASK_ID}-*"` suffices. Mirror
  `test_prefix_is_not_a_match_boundary_violation` from the KIT-0042
  round.
- **`head -1` sites** (optional criterion, F3-conditional): lines 221,
  479, 490, 501. Only touch the ones F3's edit already reaches.
- **F4**: o3's mixed-context Gate 2 claim is UNVERIFIED — reproduce it in
  the stub harness FIRST (a success + a failure CodeRabbit commit-status
  context on the same SHA); fix only if it reproduces, else record the
  decline with the repro. Do not start the fix round by trusting the
  claim.

## Test approach

- Extend `tests/test_preflight_check.py` (KIT-0040 harness): multi-run
  payloads for F1, unknown-status payloads for F2 (both PENDING-expected
  and completed-failure-still-FAILs), fixture-collision for F3, and the
  F4 repro attempt. Keep the `GATE:N:Name:VERDICT:` format intact.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.
- Gate logic, not docs — normal phase order (evaluator-before-PR does
  not apply).

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — one minor finding (formalize the
conditional `head -1` note), accepted as an optional acceptance
criterion. All six structural dimensions rated clean. Disposition +
planner-verified anchors in the task file's Evaluation section; log:
`.adversarial/logs/KIT-0043-preflight-gates-127-edge-hardening--arch-review-fast.md`.

## Out of scope

- Gates 3–6 (KIT-0034/0042 landed those)
- Rewriting the preflight script beyond the named edges (N-series
  constraints from KIT-0034 stand: shell + `gh`, no new deps)
- KIT-0041 (harness generalization), KIT-0044 (worktree codification —
  your retro feeds it, your diff doesn't)
- Downstream repos (operator deferral stands)

## PR sizing

Single PR, < 250 lines including tests:
branch `feature/KIT-0043-preflight-gates-edge-hardening` (already created
in the worktree).
