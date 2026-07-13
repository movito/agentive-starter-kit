# KIT-0042 Evaluator Review — bundle-aware preflight Gates 5/6 (PR #74)

**Date**: 2026-07-13
**Evaluators**: code-reviewer-fast-v2 (Gemini), code-reviewer (o3) — gate logic, normal phase order (doc-dominated exception does not apply)
**Verdicts**: fast-v2 CONCERNS · o3 (see log)

## Disposition

### Accepted (fixed in `7166d99`)

| Finding | Source | Fix |
|---------|--------|-----|
| Zero-byte "pointer" files satisfied Gates 5/6 | o3 | Both finds now require `-type f -size +0c`; red-then-green harness case (`test_empty_pointer_files_do_not_pass`) |
| Prefix false-positive untested | o3 (and the spec's conditional criterion) | Boundary pinning test added (`test_prefix_is_not_a_match_boundary_violation`: KIT-999 not satisfied by KIT-9999 artifacts) — kept despite the convention route leaving exact-name matching unchanged, so future pattern edits can't silently lose the boundary |

### Declined with evidence

| Finding | Source | Why declined |
|---------|--------|--------------|
| Gate 5 glob prefix collision (KIT-4 matches KIT-40's record) | fast-v2 (headline) | Empirically false: every Gate 5/6 pattern has a literal separator (`-evaluator-review`, `-code-review`, `-REVIEW-STARTER`) immediately after `${TASK_ID}` — that IS the boundary. Tested: `KIT-4-…`/`KIT-004-…` patterns matched neither `KIT-40-evaluator-review.md` nor `KIT-0042-evaluator-review.md`; control (`KIT-40-…`) matched. Now also pinned by the boundary test. |
| Gate 7 prefix collision (`${TASK_ID}*`, no separator) | fast-v2 | Real in principle, but Gate 7 is explicitly out of scope ("other preflight gates — KIT-0034 landed those; don't touch") and pre-existing. Practically nil with the kit's fixed-width KIT-NNNN IDs (`KIT-0004*` cannot match `KIT-0040-…`). Candidate follow-up if variable-length IDs ever appear. |
| Gate 1 `--limit 10` can drop failing runs; unknown statuses count as FAIL; auth errors waste poll retries | o3 | Out of scope (Gate 1, KIT-0034 surface, untouched by this PR). |
| Gate 2 fallback mixed commit-status contexts | o3 | Out of scope (Gate 2, untouched). |
| `head -1` on multiple matches is arbitrary | fast-v2, o3 | Pre-existing and acceptable: Gate 6 is exact-name + maxdepth 1 (≤1 match); Gate 5's wildcard exists to accept preserved rounds (`-r1.md`) — any persisted record satisfies the gate's intent. |
| FAIL hint names only the `-evaluator-review.md` variant | o3 | Deliberate: the hint targets the bundle-pointer case, whose convention (review-handoff skill + KIT-0037/38/39 reference files) uses exactly that name. One canonical filename to create beats a three-pattern menu in an error message; the accepted-pattern list lives in the script comment above the find. |

## Raw evaluator logs

## Source: KIT-0042-code-review-input--code-reviewer-fast-v2.md

#  Code Reviewer Fast V2

**Source**: .adversarial/inputs/KIT-0042-code-review-input.md
**Evaluator**: code-reviewer-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-07-13 21:43 UTC

---

### Findings

**[ROBUSTNESS]: Filename Prefix Collision in Gate 5 Search**
- **Location**: `scripts/core/preflight-check.sh:Gate 5`
- **Edge case**: Searching for `KIT-4` when `KIT-40-evaluator-review.md` exists but `KIT-4-evaluator-review.md` does not.
- **What happens**: The `find` command uses `${TASK_ID}-evaluator-review*.md`. If `TASK_ID` is `KIT-4`, the glob matches `KIT-40-evaluator-review.md`. The script then sets `EVAL_FILE` and returns a false `PASS` for Gate 5.
- **Tested?**: No. (The implementation guidance explicitly warned about this "prefix safety trap" from KIT-0040, but the developer used a loose glob instead of boundary-safe logic).

**[CORRECTNESS]: False Positive in Gate 7 Task Location**
- **Location**: `scripts/core/preflight-check.sh:Gate 7`
- **Edge case**: Searching for task `KIT-9` when `KIT-99-some-task.md` exists in the `3-in-progress` folder.
- **What happens**: `find ... -name "${TASK_ID}*"` will match any filename starting with that ID. This results in Gate 7 passing for the wrong task.
- **Tested?**: No.

**[ROBUSTNESS]: Potential for Multiple Matches in Head-1 Selection**
- **Location**: `scripts/core/preflight-check.sh:Gates 5, 6, and 7`
- **Edge case**: Multiple files matching the glob (e.g., a backup file like `KIT-0042-REVIEW-STARTER.md.bak`).
- **What happens**: `find` returns all matches; `head -1` picks one arbitrarily based on filesystem order. While not a "break," it makes the gate non-deterministic and potentially masks issues where the "wrong" file is being validated.
- **Tested?**: No.

**[INTERACTION]: Shell-Specific Globbing vs. Find behavior**
- **Location**: `scripts/core/preflight-check.sh:487`
- **Edge case**: `TASK_ID` contains characters that are shell-special but valid in filenames (though unlikely for IDs).
- **What happens**: The variable is quoted in the `-name` argument, which is correct, but the logic relies on `find` interpreting the internal glob. If the convention moves to something more complex, this remains a brittle point.
- **Tested?**: Yes (baseline only).

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| Prefix collision (KIT-4 vs KIT-40) | Gate 5 `find` | No | High - False PASS on missing artifacts |
| Prefix collision (KIT-9 vs KIT-99) | Gate 7 `find` | No | Medium - False PASS on task location |
| Multiple matches (Starters/Reviews) | Gates 5/6/7 | No | Low - Non-deterministic PASS |

### Verdict

**CONCERNS**

The implementation correctly fulfills the **F1.1** requirement (improving the failure messages) and the **F2** requirement (adding a test for the bundle convention). However, it ignored a specific warning in the **Implementation Guidance** regarding prefix collisions (`KIT-0004` vs `KIT-0040`).

Because the `find` commands use `${TASK_ID}-...*` without boundaries, a PR for a low-numbered task will "steal" the pass status of a higher-numbered task if those files exist in the directory.

**Required Fixes:**
1. In `preflight-check.sh`, ensure globs are anchored or use exact matching where possible. For Gate 5, the glob should likely be `${TASK_ID}-evaluator-review.md` (or specific variants) rather than a trailing wildcard that allows digits to follow the ID.
2. Update `tests/test_preflight_check.py` to include a collision test case as requested in the task spec.
## Source: KIT-0042-code-review-input--code-reviewer.md

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0042-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-13 21:45 UTC

---

### Summary
Reviewed the only executable change (preflight-check.sh; two `echo … FAIL:` lines) plus the new tests that exercise them.
No new logic landed, but the wider file still contains edge-case traps.
Found 4 latent correctness/robustness issues and 3 documentation/test-gap issues.

### Findings

**ROBUSTNESS: Gate-1 status list can miss failing workflows**
- Location: `preflight-check.sh` – Gate 1, `gh run list --limit 10` (≈ line 190)
- Edge case: A push that launches > 10 workflow runs (matrix build with 12 jobs + “Lint”, etc.).
- What happens: `--limit 10` silently drops older runs. If one of the dropped runs has concluded ≠ success, Gate 1 still reports PASS.
- Expected: Fetch *all* runs for the commit (or page until none remain) before deciding.
- Test coverage: NOT covered (all tests stub a single run).
- Severity: Latent.

**CORRECTNESS: Unknown GitHub run status marked as FAIL**
- Location: Gate 1 loop (`if [ "$WF_STATUS" = "in_progress" ] … elif … else …`)
- Edge case: New status values (“waiting”, “requested”, “pending”) returned by the API.
- What happens: Branch falls into the final `else` ⇒ counted as a *failed* run, even though the run is merely queued.
- Expected: Treat unknown-but-non-terminal states like “queued”/“in_progress” → PENDING, not FAIL.
- Test coverage: NOT covered.
- Severity: Latent.

**CORRECTNESS: CodeRabbit fallback wrongly passes when *some* contexts succeed**
- Location: Gate 2 fallback, commit-status query (`all(. == "success")`)
- Edge case: CodeRabbit publishes two contexts (“CodeRabbit/Static”, “CodeRabbit/Runtime”) and *one* of them fails.
- What happens: `map(select(. != "success")) | first` picks the first **non-success** element only if *all* succeed; if *one* succeeds and one fails, `all(. == "success")` returns false, branch falls into “… else (map(select(. != "success")) | first)” which **does** surface the failing state *but* the subsequent logic only tests `if [ "$CR_SIGNAL" = "success" ]`. Any non-empty non-success string still counts as “signal present” and can pass fallback when other conditions hold.
- Expected: Require exactly “success”; anything else (including mixed) should fail.
- Test coverage: NOT covered (tests stub a single “success”).
- Severity: Latent.

**ROBUSTNESS: Gate 5/6 PASS with empty or binary “pointer” files**
- Location: Gate 5 (`find … | head -1`) and Gate 6 (similar)
- Edge case: File exists but is empty, contains only NUL bytes, or is a symlink outside the repo.
- What happens: Gates pass; later human reviewer clicks a broken link and sees no content.
- Expected: At minimum, non-empty regular file check (`-s` and `-type f`).
- Test coverage: NOT covered (tests write non-empty pointers).
- Severity: Latent.

**TESTING: Prefix-collision false-positive still untested**
- Location: Tests `TestGate56Bundle`
- Edge case: Task `KIT-0004` vs file `KIT-0040-evaluator-review.md`.
- What happens: Current `find -name "${TASK_ID}-code-review*.md"` would not match, but if option (a) is ever chosen the risk returns. The contract in the task spec explicitly called for this test.
- Test coverage: NOT covered.
- Severity: Gap.

**DOCUMENTATION: New FAIL hint hard-codes `-evaluator-review.md` variant only**
- Location: Two new echo strings (Gate 5/6)
- Edge case: Team follows *current* naming (`${TASK_ID}-code-review.md`).
- What happens: Gate fails, operator reads hint that shows *only* the legacy “evaluator-review” filename, thinks the file is mis-named, churn ensues.
- Expected: Hint should list all three accepted patterns or phrase generically.
- Severity: Robustness / UX.

**INTERACTION: CI poll loop ignores repo-level rate-limit / auth errors**
- Location: Gate 1; when `gh run list` starts returning 403/401 after the first attempt, script still sleeps and retries twice, wasting 10 s before deterministic FAIL.
- Edge case: Token with insufficient scopes.
- What happens: needless delay; could short-circuit on auth error.
- Severity: Minor.

### Edge Cases Verified Clean
• TASK_ID with lowercase → rejected earlier in branch-name regex
• TASK_ID containing glob metacharacters → safe (quoted in `find -name`)
• Multiple evaluator files ‑ first one wins but semantics acceptable
• Long Unicode em-dash in new message does not corrupt `grep "^GATE:"` parsing

### Test Gap Summary

| Edge Case | Function / Gate | Tested? | Risk |
|-----------|-----------------|---------|------|
| >10 workflow runs | Gate 1 | ❌ | Med |
| Unknown run status “waiting” | Gate 1 | ❌ | Med |
| Mixed CodeRabbit contexts (one fail) | Gate 2 | ❌ | Med |
| Prefix collision KIT-0004 vs KIT-0040 | Gate 5/6 | ❌ | Low-Med |
| Empty pointer file | Gate 5/6 | ❌ | Low |

### Verdict
**CONCERNS** – No immediate breakage from the two-line change, but several latent bugs in surrounding logic and new messaging inconsistencies surfaced during review.

Address at least the Gate 1 limit, mixed CodeRabbit context handling, and update the user hint before relying on these gates for enforcement.
