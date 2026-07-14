# KIT-0043 Evaluator Review — preflight Gates 1/2/7 edge hardening (PR #75)

**Date**: 2026-07-14
**Evaluators**: code-reviewer-fast-v2 (Gemini), code-reviewer (o3) — gate logic, normal phase order
**Verdicts**: fast-v2 CONCERNS · o3 CONCERNS-equivalent

## Disposition

### Accepted (fixed in `b1be550`)

| Finding | Source | Fix |
|---------|--------|-----|
| At-cap all-green window still PASSed — the truncation flag was advisory ("verify manually" doesn't help unattended enforcement); a hidden 51st failing run = false PASS | o3 | Verdict priority reworked: visible FAIL > at-cap **PENDING** (never PASS, remedy named) > PASS > running PENDING. Harness: 50-green → PENDING; failure-at-cap → FAIL |
| Truncation guard keyed on the post-event-filter count — a cap-full response of mixed events never tripped it | fast-v2 | Event filter moved out of the gh `--jq` into the local jq stage; guard keys on the RAW returned count. Harness: 40 push + 10 dispatch (cap-full) → PENDING |
| `sort` is locale-dependent | fast-v2 | `LC_ALL=C sort` on the Gate 7 pick |
| OWNER/NAME interpolated into the GraphQL string unvalidated (`--repo` injection, local-only) | o3 | Slug validated against `^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$` before use, whatever its source |

### Declined with evidence

| Finding | Source | Why declined |
|---------|--------|--------------|
| Stale `CI_RUNS` reuse on transient gh failure between attempts | fast-v2 | Cannot occur: `LATEST_RUNS`/`RUN_COUNT`/`CI_RAW_COUNT` are explicitly reset at the top of every attempt, and a successful attempt breaks the loop — there is no later attempt after data lands. The finding itself hedges ("not likely given standard scoping"). |
| Gate 7 should assert exactly one match | o3 | Gate 7's question is "is the task in the right folder" — any matching real task file answers it. A stale backup alongside is user mess for review, not a gate concern; the deterministic `LC_ALL=C sort` pick was accepted instead. |
| Mixed neutral+running detail lacks a "running" suffix | o3 | The per-run detail string already names each run's status (`WF: queued`); the PENDING verdict adds "(still running)". Sufficient signal; the suggested extra marker is redundant. |
| waiting+failure mix priority | fast-v2 (raised as a question, self-answered "correct behavior") | Confirmed correct and now pinned by `test_failure_beats_waiting_sibling`. |

### Earlier same-PR round (CodeRabbit, thread 1/1 resolved)

Gate 7 accepted directories named like task files — fixed in `af00f52`
(`-type f -size +0c`, matching the Gates 5/6 treatment) with a
red-then-green directory-fixture test.

## Raw evaluator logs

## Source: KIT-0043-code-review-input--code-reviewer-fast-v2.md

#  Code Reviewer Fast V2

**Source**: .adversarial/inputs/KIT-0043-code-review-input.md
**Evaluator**: code-reviewer-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-07-13 23:46 UTC

---

### Findings

**[CORRECTNESS]: Potential for false-PASS when `gh run list` errors and `RUN_COUNT` is not reset**
- **Location**: `scripts/core/preflight-check.sh:250`
- **Edge case**: `CI_ATTEMPT` 1 succeeds and finds runs. `CI_ATTEMPT` 2 fails (`gh` returns non-zero) but the loop continues.
- **What happens**: The variable `CI_RUNS` is local to the loop but `RUN_COUNT` and `LATEST_RUNS` are initialized to `0` and `[]` at the start of the while loop. However, if `gh` fails, the logic `if [ $? -eq 0 ]` only sets `CI_FETCH_OK=true`. It doesn't clear `CI_RUNS`. If a previous iteration's `CI_RUNS` variable persists in the shell environment (not likely given standard scoping, but see below), or if logic depends on `RUN_COUNT > 0` to break, a transient failure in a later attempt might use stale data from the first attempt if not carefully managed.
- **Tracing**: In attempt 1, `CI_RUNS` is populated. In attempt 2, `gh` fails. `CI_RUNS` is now potentially empty or holds the previous value depending on the shell. If `CI_RUNS` was set in attempt 1 and the `gh` call in attempt 2 fails without clearing the variable, the script might re-process attempt 1's data.
- **Tested?**: No. Test `test_gh_error_fails_not_pending` only covers constant failure.

**[ROBUSTNESS]: `CI_RUN_LIMIT` Truncation Guard only checks current `LATEST_RUNS`**
- **Location**: `scripts/core/preflight-check.sh:338`
- **Edge case**: Total runs for a commit equal exactly 50, but only 45 are "push/pull_request" events.
- **What happens**: The `gh` call uses `--limit 50`. If there are 50 total runs, but 5 are "workflow_dispatch", the `jq` filter reduces `CI_RUNS` to 45. `RUN_COUNT` becomes 45. The truncation guard `[ "$RUN_COUNT" -ge "$CI_RUN_LIMIT" ]` (45 >= 50) evaluates to false.
- **Result**: The user is *not* warned that runs were potentially dropped by the server-side limit because the count being checked is the *filtered* count, not the raw count returned by `gh`.
- **Tested?**: No. `test_run_count_at_cap_flags_possible_truncation` stubs 50 matching runs, hiding the filter discrepancy.

**[CORRECTNESS]: Logic Error in Gate 1 loop for `CI_ANY_RUNNING` vs `CI_ANY_FAILED_RUN`**
- **Location**: `scripts/core/preflight-check.sh:322`
- **Edge case**: A workflow status is `waiting` (non-terminal).
- **What happens**: The `if [ "$WF_STATUS" = "completed" ]` block is skipped. The `else` block (line 321) handles it. It sets `CI_DETAILS`, `CI_ALL_PASS=false`, and `CI_ANY_RUNNING=true`.
- **Interaction**: This correctly implements Requirement F2 (PENDING instead of FAIL). However, if there was *already* a failed run (e.g., "Lint" failed, "Tests" is waiting), `CI_ANY_FAILED_RUN` is true. The final verdict logic (lines 342-348) prioritizes `elif [ "$CI_ANY_FAILED_RUN" = true ]`.
- **Result**: If one run fails and one is pending, the gate correctly returns `FAIL`. This is correct behavior, but the `CI_DETAILS` string for the `waiting` status now uses `WF_STATUS` directly (e.g., "Tests: waiting;"). This is a minor improvement over the previous "Tests: ;" (empty conclusion) behavior.
- **Tested?**: Yes (partially via `test_waiting_status_is_pending_not_fail`).

**[ROBUSTNESS]: Gate 7 Determinism via `sort` is case-sensitive**
- **Location**: `scripts/core/preflight-check.sh:528`
- **Edge case**: Two files exist: `KIT-0043-Z.md` and `KIT-0043-a.md`.
- **What happens**: Standard `sort` depends on `LC_COLLATE`. In many environments, `Z` comes before `a`. If the user expects alphabetical order, they might get unexpected results.
- **Tested?**: No.

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| Transient `gh` failure after success | Gate 1 | No | Low |
| Truncation guard vs event filter | Gate 1 | No | Med |
| Multi-match ordering (Gate 7) | Gate 7 | No | Low |
| `waiting` + `failure` mix | Gate 1 | No | Low |

### Verdict

**CONCERNS**

The hardening of Gate 1 statuses (F2) and Gate 7 boundaries (F3) is logically sound and well-tested. The "reproduce-or-decline" for Gate 2 (F4) is successfully proven with tests.

However, a logic gap exists in the **Gate 1 truncation guard**: it checks the count *after* filtering for push/PR events. If `gh` returns 50 runs and 10 are unrelated events, the script sees 40 runs and will *not* trigger the "capped" warning, even though the server may have truncated the list and missed the 51st run which might have been a failing push.

**Recommended Fix**: Capture the length of `CI_RUNS` *before* the `jq` event filter to determine if the truncation warning should be displayed.

```bash
RAW_COUNT=$(echo "$CI_RUNS" | jq 'length')
...
if [ "$RAW_COUNT" -ge "$CI_RUN_LIMIT" ]; then
    CI_DETAILS="${CI_DETAILS} (server query capped at ${CI_RUN_LIMIT}...)"
fi
```
## Source: KIT-0043-code-review-input--code-reviewer.md

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0043-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-13 23:47 UTC

---

### Summary
Reviewed updated `scripts/core/preflight-check.sh` (Gate-1 limit/status logic, Gate-7 boundary hardening) plus new tests.  Changes mostly do what they claim, but a few subtle paths still break.  I logged 5 findings (1 correctness, 2 robustness, 2 test-gap/interaction).  No show-stoppers, but one latent false-PASS in Gate-1 merits a fix.

### Findings

**[CORRECTNESS]: Gate-1 still silently ignores dropped runs**
- **Location**: `preflight-check.sh` — Gate 1 loop (≈ line 279, 330–340)
- **Edge case**: Commit spawns > 50 runs (large matrix, repeated re-runs).  Oldest failing run is the 51-st element.
- **What happens**: `gh … --limit "$CI_RUN_LIMIT"` caps server response.  Script sets `CI_DETAILS += "(run count capped …)"` then, if the surviving 50 runs are green, emits `PASS`.  The hidden failing run is never fetched, so Gate-1 gives a **false PASS**.
- **Expected**: Either (a) treat “hit the cap” as PENDING/FAIL, or (b) page until no more runs.  A comment saying “verify manually” doesn’t help unattended enforcement.
- **Test coverage**: NOT covered (tests only assert the cap flag with all-green runs).
- **Severity**: Latent (breaks only on very large CI fan-out).

---

**[ROBUSTNESS]: GraphQL query still injectable via `--repo` override**
- **Location**: `preflight-check.sh`, shared-PR data fetch (≈ line 356)
- **Edge case**: User invokes `preflight-check.sh --repo 'foo", name:"bar`) { issues(first:1){nodes{id}}} #`'`
- **What happens**: `$OWNER`/`$NAME` values are expanded directly inside the GraphQL string ‑- the injected text changes the query that `gh api` sends.  Attack is local‐machine-only, but can leak private data reachable by the token.
- **Expected**: Build the query with `-F owner="$OWNER" -f query='query($owner:String! …'` or validate `--repo` against `^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$`.
- **Test coverage**: NOT covered (no CLI-injection tests).
- **Severity**: Latent security issue (malicious input required).

---

**[ROBUSTNESS]: `sort | head -1` can still pick wrong task file**
- **Location**: Gate 7 `find … | sort | head -1` (≈ line 520)
- **Edge case**: Multiple matching task files, e.g.
  `.kit/tasks/3-in-progress/KIT-0043-edge.md`
  `.kit/tasks/3-in-progress/KIT-0043-edge-OLD.md` (backup)
- **What happens**: Plain `sort` orders by byte value; whichever path happens to come first is accepted.  A stale copy can mask the real file (especially if the good one is empty → removed by `-size +0c`).
- **Expected**: Either assert exactly one match (`wc -l == 1`) or apply a deterministic preference rule (shortest path, newest mtime).
- **Test coverage**: NOT covered.
- **Severity**: Low-medium latent.

---

**[TESTING]: No negative test for “failing run truncated” path**
- **Location**: tests `TestGate1EdgeHardening::test_run_count_at_cap_flags_possible_truncation`
- **Edge case**: Same as first finding but with one hidden failure.
- **What happens**: Current test only asserts the cap note with all-green runs.  The false-PASS scenario is untested, so the bug above could reappear unnoticed.
- **Expected**: Add a 51-run fixture where the last (dropped) run is failure; assert Gate-1 verdict is not PASS.
- **Severity**: Gap.

---

**[INTERACTION]: `CI_ALL_PASS` default can flip on mixed “neutral”+running**
- **Location**: Gate-1 verdict builder
- **Edge case**: One completed : neutral + one queued run.
- **What happens**: Loop sets `CI_ALL_PASS=false` (because a queued run isn’t completed) but `CI_ANY_RUNNING=true`.  Final `elif` chain treats this as *PENDING*, which is fine.  BUT if the only *completed* run is neutral/skipped, `CI_DETAILS` lacks “running” suffix so humans may mis-read a neutral-only build as done.
- **Expected**: Append “running” marker whenever `CI_ANY_RUNNING` is true, even if no failures.
- **Test coverage**: partial (no neutral+running combo).
- **Severity**: Minor UX/clarity.

### Edge Cases Verified Clean
• Unknown non-terminal statuses (`waiting`, `hyperqueued`) correctly yield PENDING
• Directory masquerading as task file is rejected (`-type f`)
• Gate-7 prefix collision (`KIT-4` vs `KIT-40`) no longer passes
• Zero-byte task/review files rejected via `-size +0c`
• Mixed CodeRabbit commit-status contexts correctly fail fallback

### Test Gap Summary
| Edge Case | Function/Gate | Tested? | Risk |
|-----------|---------------|---------|------|
| > 50 runs with hidden failure | Gate 1 | ❌ | Med-High |
| GraphQL injection via `--repo` | shared GraphQL | ❌ | Med |
| Multiple task-slug matches | Gate 7 | ❌ | Low-Med |
| Neutral + running workflow mix | Gate 1 | ❌ | Low |
| Unknown status & cap note | Gate 1 | ✔ | — |

### Verdict
**CONCERNS**

No immediate red-line breakage, but the latent Gate-1 truncation bug (false PASS) and un-sanitised GraphQL interpolation should be addressed.  Recommend:
1. Replace the fixed `--limit` pull with pagination or treat “cap hit” as PENDING.
2. Sanitize or parameterise `$OWNER`/`$NAME` before GraphQL call.
3. Tighten Gate-7 selection or assert single match.
4. Add the missing tests described above.

Merge is acceptable if mitigations are quick-follow-ups; otherwise hold.
