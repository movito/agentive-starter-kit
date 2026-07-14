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
| Gate 7 prefix collision (`${TASK_ID}*`, no separator) | fast-v2 | Real in principle, but Gate 7 is explicitly out of scope ("other preflight gates — KIT-0034 landed those; don't touch") and pre-existing. Practically nil with the kit's fixed-width KIT-NNNN IDs (`KIT-0004*` cannot match `KIT-0040-…`). **→ Resolved in KIT-0043 (F3): boundary added (`${TASK_ID}-*`) + pinning test.** |
| Gate 1 `--limit 10` can drop failing runs; unknown statuses count as FAIL; auth errors waste poll retries | o3 | Out of scope (Gate 1, KIT-0034 surface, untouched by this PR). **→ Resolved in KIT-0043 (F1/F2): limit raised to 50 with an at-cap truncation flag; non-terminal statuses now PENDING. Auth-error short-circuit remains declined (minor; poll already bounded at 3×5 s).** |
| Gate 2 fallback mixed commit-status contexts | o3 | Out of scope (Gate 2, untouched). **→ Reproduce-or-decline completed in KIT-0043 (F4): does NOT reproduce — the jq reduces mixed contexts to the failing state and the shell requires exactly "success"; both layers pinned by harness tests (`TestGate2MixedContexts`). Declined with evidence.** |
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

---

# Round 2 (2026-07-14) — internal review substituting for CodeRabbit outage

CodeRabbit crashed with "Internal error occurred during review" on three
attempts (initial + `@coderabbitai review` + `@coderabbitai full review`)
after commit `8fcc577`. Its APPROVED review predates `7166d99` (the
`-size +0c` gate change + tests), so the operator requested an internal
adversarial round on the full current diff as the substitute.

**Evaluators**: code-reviewer-fast-v2 (rerun) + claude-code (first run —
security angle on the shell change, new model family vs round 1).

| Evaluator | Verdict | Disposition |
|-----------|---------|-------------|
| claude-code | **APPROVED** | Clean pass on the full diff including `7166d99`/`8fcc577`. |
| code-reviewer-fast-v2 | CONCERNS | All four findings are repeats of round-1 declines (Gate 1 pagination + unknown-status, Gate 7 bare wildcard, `head -1` ordering) — all out of scope per the handoff (Gates 1–4/7 untouched, KIT-0034 surface) or pre-existing/accepted. It dropped its round-1 Gate 5/6 prefix-collision claim (now acknowledges the literal separators) and marks the empty-file case as addressed by `-size +0c`. No new findings on this PR's surface. |

Round-2 raw logs below.
## Source: KIT-0042-code-review-input--code-reviewer-fast-v2.md (round 2)

#  Code Reviewer Fast V2

**Source**: .adversarial/inputs/KIT-0042-code-review-input.md
**Evaluator**: code-reviewer-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-07-13 21:58 UTC

---

### Findings

**[ROBUSTNESS]: Gate 1 Workflow Search ignores pagination**
- **Location**: `scripts/core/preflight-check.sh:Gate 1` (line 190, in context)
- **Edge case**: A PR triggers more than 10 workflow runs (common in matrix builds or repositories with many specialized CI checks).
- **What happens**: `gh run list --limit 10` is used. If there are 12 runs and the first 10 are `success` but the 11th is `failure`, the script will only see the top 10 and return a false `PASS`.
- **Tested?**: No. Tests only stub a single run entry.

**[CORRECTNESS]: Unknown GitHub run status defaults to FAIL**
- **Location**: `scripts/core/preflight-check.sh` (Gate 1 loop)
- **Edge case**: GitHub API returns a non-terminal status not explicitly handled (e.g., `waiting`, `requested`, `pending`, `action_required`).
- **What happens**: The `if/elif` block only checks `completed` and `in_progress/queued`. Anything else falls into the final `else`, setting `CI_ANY_FAILED_RUN=true`. A PR waiting for a runner would incorrectly report a failure instead of `PENDING`.
- **Tested?**: No.

**[INTERACTION]: Shell Globbing Prefix Collision in Gate 7**
- **Location**: `scripts/core/preflight-check.sh` (Gate 7)
- **Edge case**: Task `KIT-4` exists when an artifact for `KIT-40` is in the directory.
- **What happens**: `find ... -name "${TASK_ID}*"` is used. Unlike Gates 5/6 which have literal separators (e.g., `-code-review`), Gate 7 uses a bare wildcard. `find . -name "KIT-4*"` will match `KIT-40-task.md`.
- **Tested?**: No. The new `test_prefix_is_not_a_match_boundary_violation` only tests Gates 5 and 6.

**[ROBUSTNESS]: `head -1` on non-deterministic `find` output**
- **Location**: `scripts/core/preflight-check.sh` (Gates 5, 6, and 7)
- **Edge case**: Multiple files match a pattern (e.g., a manual backup `KIT-0042-REVIEW-STARTER.md.bak` or `KIT-0042-REVIEW-STARTER.md~`).
- **What happens**: `find` returns all matches. `head -1` picks the first one returned by the filesystem. If the "real" file is empty but the backup has content, the gate might pass or fail non-deterministically depending on inode order.
- **Tested?**: No.

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| >10 Workflow Runs | Gate 1 | No | Med (False PASS) |
| Non-terminal CI Status | Gate 1 | No | Med (False FAIL) |
| Prefix Collision (KIT-4 vs KIT-40) | Gate 7 | No | Low (False PASS) |
| Empty file check (binary/null) | Gates 5/6 | Partial | Low (Uses `-size +0c`) |

### Verdict

**CONCERNS**

The PR successfully implements the "Route B" convention and correctly adds `-size +0c` to prevent empty pointer files from passing Gates 5 and 6. However, the core logic in **Gate 1** (CI check) contains latent correctness bugs regarding how it interprets GitHub's API (limit and unknown statuses). Additionally, while prefix collisions were addressed for the changed Gates 5/6, **Gate 7** remains vulnerable to the exact same prefix collision issue because it lacks a literal separator in its `find` pattern.

**Required Fixes:**
1. Update Gate 1 to handle non-terminal statuses (`waiting`, etc.) as `PENDING`.
2. Increase `--limit` in Gate 1 or verify if 10 is a hard project constraint.
3. Fix Gate 7 pattern to match the boundary safety of Gates 5/6.
## Source: KIT-0042-code-review-input--claude-code.md (round 2)

#  Claude Code

**Source**: .adversarial/inputs/KIT-0042-code-review-input.md
**Evaluator**: claude-code
**Model**: anthropic/claude-sonnet-4-6
**Generated**: 2026-07-13 22:00 UTC

---

## Phase 1: Understand Intent

This is a CI/CD preflight check system for a software development workflow tool ("agentive-starter-kit"). The primary executable changes are in `scripts/core/preflight-check.sh` and `tests/test_preflight_check.py`.

**What it does**: Before a PR can be submitted for human review, it must pass 7 gates:
1. CI (GitHub Actions) is green
2. CodeRabbit bot has reviewed
3. BugBot has reviewed
4. Zero unresolved review threads
5. Evaluator review artifact exists (non-empty file)
6. Review starter document exists (non-empty file)
7. Task file is in the correct folder

**Critical paths**: The shell script gates 5/6 were changed to add `-type f -size +0c` to `find` commands, and FAIL messages were extended to include bundle/multi-PR guidance. Four new Python tests were added.

**Assumptions**: TASK_ID is fixed-width (KIT-NNNN), files are local filesystem artifacts, `gh` CLI is available and authenticated.

---

## Phase 2: Security Analysis

### Injection Vectors

**SQL/Command injection**: No SQL. Shell variable interpolation into `find -name` is quoted correctly. GraphQL queries interpolate `$OWNER`, `$NAME`, `$PR_NUMBER` directly into the query string — analyzed below.

**Path traversal**: Gate 5/6 `find` is constrained to `.kit/context/reviews` and `.kit/context` with `-maxdepth 1` (Gate 6). Findings are used only for display/existence checks, not for file reads or execution.

---

### MEDIUM: GraphQL Injection via $OWNER, $NAME, $PR_NUMBER

- **Location**: `scripts/core/preflight-check.sh` — the `gh api graphql` call (approximately line ~330 in the full file)
- **Issue**: `$OWNER`, `$NAME`, and `$PR_NUMBER` are interpolated directly into a GraphQL query string via shell variable expansion:
  ```bash
  PR_DATA=$(gh api graphql -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: $PR_NUMBER) { ...
  ```
  `PR_NUMBER` is validated as `^[0-9]+$` before this point — that protection holds. However, `$OWNER` and `$NAME` are derived from `gh repo view --json nameWithOwner` or `$REPO_OVERRIDE` (user-supplied via `--repo`). A malicious `--repo` value like `foo\", name: \"bar`) { issues { nodes { body } } } #` could inject into the GraphQL query. In practice this is a local CLI tool run by a developer on their own machine against their own GitHub token, substantially limiting exploitability. But the injection vector is real.
- **Remediation**: Use `-f` variable substitution for the GraphQL query rather than shell string interpolation, or use `-F` fields to pass variables separately:
  ```bash
  gh api graphql \
    -F owner="$OWNER" \
    -F name="$NAME" \
    -F pr="$PR_NUMBER" \
    -f query='query($owner:String!,$name:String!,$pr:Int!){ repository(owner:$owner,name:$name){ pullRequest(number:$pr){ ... } } }'
  ```

---

### LOW: REPO_OVERRIDE Not Validated for Expected Format

- **Location**: `preflight-check.sh` — `--repo` argument parsing and `$REPO_OVERRIDE` assignment
- **Issue**: `$REPO_OVERRIDE` accepts any string. While a malformed value would likely cause `gh` to fail gracefully, the value flows unvalidated into `$OWNER`/`$NAME` via `cut -d/ -f1` and `cut -d/ -f2`, and then into the GraphQL query (as noted above). There is no check that the value matches `owner/repo` format.
- **Remediation**: Add a format check:
  ```bash
  if ! [[ "$REPO_OVERRIDE" =~ ^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$ ]]; then
      echo "ERROR: --repo must be in owner/name format"
      exit 1
  fi
  ```

---

### Authentication & Authorization

No hardcoded credentials. The script requires `gh auth status` to pass before proceeding — this is correct. The script runs with whatever GitHub token the local `gh` CLI has; no privilege escalation is possible from within the script itself.

---

### Data Handling

- No PII is logged beyond GitHub usernames (which are public).
- No sensitive data is written to files.
- Error messages embed TASK_ID and file paths — these are internal development artifacts, not production user data.

---

## Phase 3: Correctness Analysis

### LOW: Gate 5 `find` Ordering Across `-o` with `-type f -size +0c`

- **Location**: `preflight-check.sh`, Gate 5 `find` command
- **Issue**: The `-type f -size +0c` predicates are placed *after* the `\(...-o-...\)` group. POSIX `find` evaluates left-to-right with short-circuit; `-type f -size +0c` applies only to files that matched the name group, which is correct. However, the current ordering means `-type f -size +0c` is evaluated as a global filter *after* the OR group — this is the intended behavior and it works correctly. **Not actually a bug**, but worth confirming: the parenthesized OR group is evaluated first (it's an expression), then `-type f -size +0c` applies to the result. This is correct POSIX `find` behavior.

---

### LOW: Gate 7 Prefix Collision (Acknowledged Out-of-Scope, but Documentably Present)

- **Location**: `preflight-check.sh`, Gate 7
  ```bash
  TASK_FILE=$(find .kit/tasks/3-in-progress .kit/tasks/4-in-review -name "${TASK_ID}*" 2>/dev/null | head -1 || true)
  ```
- **Issue**: `${TASK_ID}*` without a separator could match a longer ID (e.g., `KIT-999` matching `KIT-9999-task.md`). The review record acknowledges this as pre-existing and practically nil with fixed-width `KIT-NNNN` IDs. With the convention of 4-digit zero-padded IDs this is indeed not a real risk. Documented here for completeness; the evaluator review disposition is sound.
- **Remediation**: If variable-length IDs are ever introduced, change to `-name "${TASK_ID}-*"` (add separator).

---

### LOW: `head -1` on `find` Output is Filesystem-Order Dependent

- **Location**: Gates 5, 6, 7 in `preflight-check.sh`
- **Issue**: Multiple matching files (e.g., `KIT-9999-code-review.md` and `KIT-9999-code-review-r2.md`) result in `head -1` selecting arbitrarily based on filesystem traversal order. The review record acknowledges this as acceptable for Gate 5 (any persisted record satisfies the intent), and Gate 6 uses `maxdepth 1` with an exact name making multiple matches essentially impossible.
- **Remediation**: No immediate change required given current conventions. If determinism becomes important, add `| sort | head -1`.

---

### LOW: Test Fixture Cleanup Assumes `missing_ok=True` (Python 3.8+)

- **Location**: `tests/test_preflight_check.py`, `TestGate56Bundle` tests
- **Issue**: `path.unlink(missing_ok=True)` requires Python 3.8+. The project appears to target 3.11+ based on context, so this is fine. The `list[str] | None` type hint also requires Python 3.10+ (for the `|` union syntax without `from __future__ import annotations`). However, `from __future__ import annotations` is present at the top of the file, making this a non-issue at runtime.
- **Remediation**: No action needed given the `from __future__ import annotations` import.

---

### LOW: Test KIT-999 Boundary Test Depends on HEAD_TASK Being KIT-9999

- **Location**: `tests/test_preflight_check.py`, `test_prefix_is_not_a_match_boundary_violation`
- **Issue**: The test asserts that `KIT-999` does not match `KIT-9999` artifacts. This works correctly because the Gate 5 pattern is `${TASK_ID}-evaluator-review*.md` — `KIT-999-evaluator-review*.md` does not match `KIT-9999-code-review.md`. The test is valid and the mechanism is sound (the literal `-` separator is the boundary). However, the test comment says "KIT-9999 artifacts must NOT satisfy the gates for the shorter task ID KIT-999" but the fixture's artifact is `KIT-9999-code-review.md` which uses a different pattern than what KIT-999 would search for. This is correct behavior but the test is implicitly dependent on the fixture file name having `-code-review` not `-evaluator-review` as the suffix. If the fixture changed to use `-evaluator-review`, the name pattern `KIT-999-evaluator-review*.md` still wouldn't match `KIT-9999-evaluator-review*.md`. So the test is robust regardless.

---

### MEDIUM: Gate 1 `--limit 10` Can Drop Runs (Acknowledged, Unaddressed)

- **Location**: `preflight-check.sh`, Gate 1 (`gh run list --commit "$LATEST_SHA" --limit 10`)
- **Issue**: The evaluator review acknowledges this as out-of-scope. However, it is a genuine correctness issue in the changed code's context (the full file is in scope). A matrix build with >10 jobs could have a failing run silently dropped. The fix (`--commit` instead of branch-level reduces this risk significantly since commit-scoped runs are typically fewer), but the hard cap remains.
- **Remediation**: If more than 10 runs are possible, add pagination or increase the limit to `--limit 50`. Since the `--commit` flag significantly constrains results, this is low-urgency.

---

### LOW: TASK_ID Derived from Branch with No Sanitization for `find`

- **Location**: `preflight-check.sh` — TASK_ID derivation via `sed` and use in `find -name`
- **Issue**: TASK_ID is derived via `sed -n 's|^feature/\([A-Z][A-Z0-9]*-[0-9][0-9]*\).*|\1|p'` which constrains it to uppercase letters, digits, and hyphens. This character set is safe for `find -name` glob patterns. The o3 evaluator confirmed this as clean. No issue.

---

## Phase 4: Code Quality

### Positive Observations

The code quality overall is high:

1. **Structured output format** (`GATE:N:Name:VERDICT:detail`) is consistent and machine-parseable — downstream tools and tests rely on it correctly.
2. **Defensive error handling**: `|| true` on `find` commands prevents `set -e` exits on empty results; `2>/dev/null` suppresses spurious errors; explicit exit code checks on `gh` calls.
3. **Non-empty file guard** (`-type f -size +0c`) — the new addition in this PR correctly hardens Gates 5/6 against zero-byte artifacts.
4. **Excellent test harness**: The stub-`gh` pattern is well-architected. Module-scoped fixtures, clean git environment isolation, comprehensive canned payload builders, and clear test intent via docstrings.
5. **PR_NUMBER numeric validation** before GraphQL interpolation — correct defense against the most obvious injection vector.
6. **Acknowledgment discipline**: The evaluator review document correctly tracks accepted vs. declined findings with evidence, making future re-litigation cheap.
7. **`extra_args` extensibility** in `PreflightProject.run()` is cleanly added with a `None` default and safe spread.
8. **Test cleanup via `finally`** blocks in the new bundle tests — correct resource cleanup even on test failure.

---

### LOW: Long FAIL Message Lines May Cause Issues in Some Terminals/Parsers

- **Location**: `preflight-check.sh`, Gates 5 and 6 FAIL echo statements
- **Issue**: The new FAIL messages are single long lines (~200 chars). The `_gates()` parser in the test harness uses `re.match(r"^GATE:(\d+):[^:]*:(PASS|FAIL|PENDING):(.*)$", line)` — the `(.*)` captures the entire remainder including the embedded colons in the file path (`${TASK_ID}-evaluator-review.md`). The regex works correctly since `[^:]*` stops at the first colon after `GATE:N:`, and `(.*)` is greedy. The REVIEW-STARTER.md path in the Gate 6 message doesn't contain colons, so parsing is clean.
- **Remediation**: No code change required; the PR author flagged this for human visual inspection and the parser handles it correctly.

---

### LOW: `test_fail_details_name_bundle_convention` Does Not Assert Gate 7

- **Location**: `tests/test_preflight_check.py`, `test_fail_details_name_bundle_convention`
- **Issue**: The test runs with `--task KIT-9997`. There's no task file for KIT-9997 in `3-in-progress` or `4-in-review`, so Gate 7 also fails. The test only asserts `result.returncode == 1` and checks gates 5 and 6 — it doesn't assert Gate 7 fails. This is fine (the returncode assertion covers it), but it's a minor incompleteness.
- **Remediation**: Optionally add `assert gates[7][0] == "FAIL"` for completeness, or add a KIT-9997 task stub file and verify Gate 7 passes to isolate the test to gates 5/6.

---

## Context Required / Unverifiable

- **`target_repo.sh` library**: The `target_repo_init`, `target_repo_is_set`, `TARGET_REPO`, `TARGET_PATH`, `GIT_DIR_ARG`, `GH_REPO_ARG` variables are sourced from `scripts/core/lib/target_repo.sh` which is not shown in the diff. The security of cross-repo mode depends on this library's validation of `--repo` values.
- **`dispatch` command**: The fire-and-forget `dispatch emit` call is stubbed in tests. Its actual security properties (event log integrity, injection via `$_PF_SUMMARY`) cannot be assessed without the implementation.
- **GitHub token scope**: The `gh auth status` check confirms authentication but not token scope. If the token has write access, a compromised `--repo` value could potentially be used to query private repository data — not assessable from this code alone.
- **Pre-commit hook interaction**: The COMMIT-PROTOCOL.md note about pre-commit aborting commits is a process concern, not a code security issue.

---

## Overall Assessment

**APPROVED**

The changes in this PR are narrow and well-executed:

1. **The core change** — adding `-type f -size +0c` to Gates 5/6 `find` commands — is correct, properly motivated, and tested with a red-green harness case.
2. **The FAIL message enhancement** is appropriately scoped (single-line, GATE prefix intact, both bundle cases covered).
3. **The four new tests** cover the intended behavioral contract (pointer files pass, prefix boundary, empty files fail, message content).
4. **The evaluator disposition** is sound — the prefix-collision claim was empirically disproven with correct reasoning (literal separator IS the boundary), and the accepted findings were properly implemented.

The one genuine security concern (GraphQL injection via `$OWNER`/`$NAME`) is pre-existing, not introduced by this PR, and practically constrained to a local developer tool context. It warrants a follow-up issue but does not block this PR.

No critical or high issues were introduced by this diff. The pre-existing issues (Gate 1 limit, Gate 7 prefix, GraphQL injection) are correctly scoped as out-of-range for this task.
