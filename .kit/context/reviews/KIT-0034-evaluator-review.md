# KIT-0034 — Evaluator Review Record

**PR**: movito/agentive-starter-kit#69
**Input**: `.adversarial/inputs/KIT-0034-code-review-input.md` (full-file context, 12 files)
**Date**: 2026-07-04/05

## Verdicts

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast-v2 | gemini-3-flash-preview | CONCERNS |
| code-reviewer | o3 | FAIL |
| claude-code | claude-sonnet-4-6 | **APPROVED** |

Logs: `.adversarial/logs/KIT-0034-code-review-input--{code-reviewer-fast-v2,code-reviewer,claude-code}.md`

## Triage — accepted (fixed in follow-up commit)

1. **`THREAD_UNRESOLVED` numeric guard** (o3, claude-code, fast): Gate 2
   fallback now requires `[[ "$THREAD_UNRESOLVED" =~ ^[0-9]+$ ]]` before the
   numeric compare — no bash "integer expression expected" noise on exotic
   jq output.
2. **CR commit-status multi-context determinism** (o3 #1, corrected): the
   evaluator's mechanism was wrong — the combined-status endpoint returns
   the *latest* status per context, so `pending`-shadows-`success` for one
   context cannot happen. The real (smaller) gap was multiple
   CodeRabbit-matching contexts with `tail -1` picking arbitrarily. Fixed:
   all matching contexts must be `success` (with an explicit empty-array
   guard — `all([])` is vacuously true); mixed results surface the first
   non-success state in the FAIL detail. Verified against jq samples and
   the real PR #58 head SHA.
3. **`PR_NUMBER` numeric validation** (claude-code security MEDIUM/LOW):
   explicit `^[0-9]+$` guard before GraphQL interpolation.
4. **`MATCH_SHA` cosmetic bug** (claude-code LOW, pre-existing): the grep
   for a SHA in `"author: STATE"` could never match; PASS detail now prints
   both candidate SHAs.
5. **Gate 4 thread-count 100-cap** (claude-code MEDIUM): PASS detail now
   flags possible truncation when total hits the `first: 100` cap.
6. **Poll-loop state reset + doc notes** (claude-code LOW, fast #4):
   `LATEST_RUNS`/`RUN_COUNT` reset per attempt; TEMP-THEN-COMMIT doc gains
   the same-directory/same-mount caveat; preflight.md documents the ~10 s
   worst-case re-poll block.

## Triage — declined (with verification)

- **o3 "tail -1 picks oldest status" as stated**: combined-status endpoint
  dedups per context (see accepted #2 for the real residue).
- **o3 "exit code 2 breaks callers"**: repo-wide grep shows no script
  chains `preflight-check.sh &&`; only command docs consume it, both
  updated. PENDING must not exit 0 — "all gates confirmed" is the 0
  contract.
- **o3 "CRLF breaks KIT_AGENTS parse"**: `str.split()` splits on `\r` too;
  claim incorrect.
- **o3 "multiline array breaks regex"**: `[^)]*` matches newlines (negated
  class ≠ `.`); claim incorrect. A `)` inside the array block would fail
  the test loudly — desired behavior for a wiring guard.
- **o3 "BugBot multiple check-runs"**: check-runs API defaults to
  `filter=latest`; also pre-existing Gate 3 code, out of scope.
- **fast "allow whitespace around `=`"**: invalid bash (assignments cannot
  have spaces); strict regex is correct.
- **fast "Gate 2/4 should be PENDING on API error"**: review gates are
  fail-closed by design (N1); only CI-run absence maps to PENDING (task
  scope). The FAIL detail surfaces `unresolved=unknown` for diagnosis.
- **claude-code "guard missing agents dir in test"**: module-skip already
  covers stripped checkouts (script absent ⇒ skip); in the kit repo the
  agents dir is guaranteed, and `test_marker_agents_exist` fails loudly if
  the convention moves.

## Manual gate verification (no test harness exists for the script)

- Real run vs PR #63 (2nd false-negative case): Gates 2–4 PASS, Gate 1
  PENDING (branch context), FAIL-beats-PENDING exit precedence confirmed.
- Stub-`gh` matrix (real script, canned output): fallback PASS (A),
  no-review FAIL (B), unresolved-thread FAIL (C), CHANGES_REQUESTED FAIL
  (D), check-run secondary source PASS (E), completed-failure-while-running
  FAIL not PENDING (F). All as specified; recorded in PR #69 description.
