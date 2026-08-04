# KIT-0084 — Evaluator Review Record

**Date**: 2026-08-04
**Task**: `.kit/tasks/3-in-progress/KIT-0084-working-env-from-day-one.md`
**Diff**: `main...feature/KIT-0084-working-env-from-day-one` (full-file context input)
**Ordering**: trio run BEFORE PR open (KIT-0035/KIT-0046 rule)

## Runs

| Evaluator | Model | Verdict | Log |
|-----------|-------|---------|-----|
| code-reviewer-fast-v2 (round 1) | gemini-3-flash | CONCERNS | superseded by round 2 (same file) |
| code-reviewer (deep) | o3 | FAIL | `.adversarial/logs/KIT-0084-code-review-input--code-reviewer.md` |
| claude-code (security) | claude-sonnet-4-6 | **APPROVED** | `.adversarial/logs/KIT-0084-code-review-input--claude-code.md` |
| code-reviewer-fast-v2 (round 2, post-fix) | gemini-3-flash | CONCERNS | `.adversarial/logs/KIT-0084-code-review-input--code-reviewer-fast-v2.md` |

## Findings actioned (commit `4bc3b02` + indent follow-up)

- **JSON null → literal "None"** (fast-v2 r1): the current-state.json
  reader now prints only `isinstance(value, str)` values; test
  `test_null_recorded_prefix_writes_empty_never_none` pins it.
- **Duplicate identity lines survive** (fast-v2 r1, o3): `fill_env_identity`
  rewrites the first assignment and DROPS later duplicates (dotenv
  parsers are last-assignment-wins); indented assignments match too
  (fast-v2 r2). Test: `test_duplicate_identity_lines_deduplicated`.
- **`#` inside quoted values truncated** (fast-v2 r1): `_effective_value`
  is quote-aware — quotes first, comment-split only for unquoted
  values. Tests: `test_quoted_value_with_hash_not_truncated`,
  `test_quoted_key_with_hash_is_present`. (Also fixed an
  empty-string `value[:1] in "\"'"` → IndexError caught by the
  existing empty-key test.)
- **Newline injection via name/prefix** (o3): CR/LF stripped from
  identity values before the rewrite (operator-owned input; hardening,
  not a trust boundary).
- **Printed cp command unquoted / kit .env mode unchecked** (claude-code):
  paths quoted; the kit `.env` gets the same 0600 courtesy warning as
  the preset env-source.
- **Test `split()` fragility** (claude-code): `maxsplit=1` in the
  legacy-body test.

## Findings rejected, with reasoning

- **o3: "door aborts when repo isn't initialised"** — unreachable: on
  `--new` both engines git-init before the env step runs, and the
  check-ignore failure branch exits with its own message (an `if !`
  condition, not a `set -e` abort).
- **o3: "carry-over nukes template lines"** — by design: the file being
  replaced is the template seeded seconds earlier with no operator
  content, and the spec's own non-TTY remedy is the identical wholesale
  `cp`; identity fields are refilled after.
- **o3: allow opting out of the `TASK` WARN** — contradicts the task
  spec, which mandates WARN on empty-or-`TASK`; doctor WARNs are
  non-fatal.
- **o3: ".env exists on re-run"** — `--new` refuses existing targets
  outright; the path does not exist.
- **fast-v2 r2: doctor is first-non-empty-wins, parsers are last-wins** —
  `key_state`'s whole-file first-NON-EMPTY scan is pre-existing,
  previously-litigated behavior (the copy-template-then-append layout
  depends on it); `key_value` mirrors it deliberately, and the door now
  dedupes seeded files so the divergence needs a hand-broken `.env`.
- **fast-v2 r2: `.strip()` inside quotes** — mirrors the pre-existing
  normalization; for this check a whitespace-only quoted prefix is
  unusable anyway, so WARN is correct.
- **fast-v2 r1: `basename /`** — `--new` rejects existing targets (`/`
  exists) and empty targets die at argument validation.

## Residual notes for reviewers

- claude-code MEDIUM (acknowledged trade-off): `.env` contents pass
  through a shell variable during the identity rewrite — chosen over a
  temp file because a leaked temp beside `.env` would not be
  gitignored; short-lived operator-owned process.
- The doctor/parser semantics divergence above is documented in code
  comments; revisit only if a real `.env` shape hits it.

---

## Appended evaluator logs (verbatim, whitespace-stripped; .adversarial/logs/ is untracked by policy)

### Log: code-reviewer-fast-v2

#  Code Reviewer Fast V2

**Source**: /Users/broadcaster_one/Github/ask-worktrees/KIT-0084/.adversarial/inputs/KIT-0084-code-review-input.md
**Evaluator**: code-reviewer-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-08-04 19:44 UTC

---

### Findings

**[CORRECTNESS]: Discrepancy between Doctor's key-parsing and standard `.env` behavior (First-wins vs Last-wins)**
- **Location**: `scripts/core/doctor.d/20-env-keys.py:key_value` and `key_state`
- **Edge case**: Multiple assignments of the same key in `.env` (e.g., `TASK_PREFIX=OLD` followed by `TASK_PREFIX=NEW`).
- **What happens**: Standard `.env` parsers (and shell sourcing) are "last-assignment-wins". However, the `key_value` and `key_state` functions return the first uncommented assignment they encounter. This means the `doctor` may report a "PASS" or "WARN" based on a value that is actually being overridden and ignored by the application.
- **Tested?**: No. Tests only cover single assignments or commented-then-uncommented.

**[CORRECTNESS]: `_effective_value` incorrectly strips internal spaces from quoted strings**
- **Location**: `scripts/core/doctor.d/20-env-keys.py:_effective_value`
- **Edge case**: Quoted values with intentional leading/trailing whitespace (e.g., `TASK_PREFIX=" PROJ "`).
- **What happens**: The function calls `.strip()` on the content *inside* the quotes (`value[1:closing].strip()`). In standard `.env` parsing, quotes are used specifically to preserve such whitespace. This discrepancy causes the `doctor` to validate a "normalized" value that does not match what the application actually loads.
- **Tested?**: No. Existing tests use trimmed values like `"PROJ#1"`.

**[ROBUSTNESS]: `fill_env_identity` fails to deduplicate indented assignments**
- **Location**: `scripts/local/bootstrap:fill_env_identity`
- **Edge case**: An existing `.env` (from an `env-source` or manual edit) has indented assignments (e.g., `  PROJECT_NAME=OLD`).
- **What happens**: The `awk` script uses anchors `^PROJECT_NAME=`. It will fail to match indented lines. Consequently:
    1. It won't replace the indented line.
    2. The `END` block will append a new `PROJECT_NAME=NEW` at the end of the file.
    While a last-wins parser will technically use the new value, the file remains cluttered with duplicates, and the `doctor` (which is first-wins) will incorrectly report the `OLD` value.
- **Tested?**: Partial. `test_duplicate_identity_lines_deduplicated` tests duplicates but they are not indented.

**[CORRECTNESS]: Potential for malformed `.env` if template keys are commented**
- **Location**: `scripts/local/bootstrap:fill_env_identity`
- **Edge case**: The `.env.template` or `env-source` has `PROJECT_NAME` commented out (e.g., `# PROJECT_NAME=`).
- **What happens**: The `awk` script only matches `^PROJECT_NAME=`. If the line is commented, it is ignored by the matching logic and handled by the default `{ print }` block. Then, the `END` block appends a new assignment. Result:
    ```
    # PROJECT_NAME=
    ...
    PROJECT_NAME=NEW_NAME
    ```
    This is safe, but if the user also had an uncommented indented assignment (see above), you end up with three variations, confusing both the operator and the `doctor`.
- **Tested?**: Yes, `test_missing_lines_appended_commented_left_alone` confirms this behavior.

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| Duplicate keys (First vs Last wins) | `key_value` | No | Med: Doctor reports/validates wrong data |
| Internal whitespace in quotes | `_effective_value` | No | Low: Minor identity mismatch |
| Indented key replacement | `fill_env_identity` | No | Low: File clutter/Doctor confusion |
| Missing closing quote in `.env` | `_effective_value` | No | Low: Falls back to split logic safely |

### Trace: `_effective_value` missing quote
If `raw` is `"value`:
1. `value` = `"value`
2. `value[0]` is `"`
3. `closing` = `value.find("\"", 1)` -> `-1`
4. Returns `value.split("#", 1)[0].strip()` -> `"value`
This is handled correctly as a fallback.

### Trace: `fill_env_identity` JSON Null
If `current-state.json` has `"task_prefix": null`:
1. Python block sets `value = None`.
2. `isinstance(value, str)` is False.
3. Python prints nothing.
4. Shell `prefix` is `""`.
5. `fill_env_identity` writes `TASK_PREFIX=` (empty).
This is handled correctly (checked by `test_null_recorded_prefix_writes_empty_never_none`).

### Verdict

**CONCERNS**

The logic for `doctor` and `bootstrap` is slightly inconsistent regarding how it handles `.env` files that aren't perfectly formatted (specifically duplicates and indentation). While it works for standard "happy path" seeding, a user who manually edits their `.env` with indentation or duplicates will see the `doctor` and the `bootstrap` tool disagreeing on the project's identity. The most significant gap is the `first-wins` logic in `doctor.d/20-env-keys.py`, which is the opposite of how environment variables actually behave in Linux/Python.
### Log: code-reviewer

#  Code Reviewer

**Source**: /Users/broadcaster_one/Github/ask-worktrees/KIT-0084/.adversarial/inputs/KIT-0084-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-08-04 19:33 UTC

---

### Summary
Reviewed changes around `.env` seeding (KIT-0084), doctor checks and bootstrap logic.
Found 6 non-trivial edge-case/logic problems (2 immediate correctness bugs, 3 latent, 1 test gap).

### Findings

**[CORRECTNESS]: bootstrap fails when repo isn’t initialised yet**
- **Location**: `scripts/local/bootstrap:copy_env_into_target` (line ~560)
- **Edge case**: `bootstrap --new` targets whose export engine does NOT create a `.git` (custom export engine, or a future refactor).
- **What happens**: `git -C "$TARGET" check-ignore -q .env` is called before `git init` has happened ⇒ exit-status 128, bash `-e` terminates the whole door. User sees “.env is not gitignored” even though the ignore file would be created later.
- **Expected**: Door should defer the ignore check until after a repo exists, or fall back to “no repo yet – assume future .gitignore will ignore `.env`”.
- **Test coverage**: NOT covered – all current tests run default export path which already contains a repo.
- **Severity**: Bug

---

**[CORRECTNESS]: Operator carry-over silently nukes earlier template lines**
- **Location**: `scripts/local/bootstrap:offer_env_carryover` (line ~630)
- **Edge case**: No `env-source`; template seeded first, then operator answers “yes” to key copy.
- **What happens**: `copy_env_into_target` overwrites the file wholesale with the kit’s `.env`, discarding the earlier template comments and any non-key variables that template had added. Only `PROJECT_NAME` / `TASK_PREFIX` get re-added afterwards.
- **Expected**: Keys should be *merged*; content not related to secrets should survive.
- **Test coverage**: NOT covered (tests only hit the “no”/non-TTY path).
- **Severity**: Latent – data loss once an operator answers “yes”.

---

**[ROBUSTNESS]: Duplicate PROJECT_NAME / TASK_PREFIX lines remain stale**
- **Location**: `scripts/local/bootstrap:fill_env_identity` (line ~680)
- **Edge case**: `env-source` already contains `PROJECT_NAME=` / `TASK_PREFIX=`.
- **What happens**: Function rewrites the *first* matching line but leaves the old one further down. Libraries that read “last assignment wins” (python-dotenv, Node dotenv) will still see the stale value.
- **Expected**: Either de-duplicate (delete later matches) or always rewrite *all* occurrences.
- **Test coverage**: NOT covered (tests assert only first value).
- **Severity**: Latent – wrong identity under common dotenv parsers.

---

**[SECURITY/ROBUSTNESS]: New-line / shell token injection in ENV_PREFIX / ENV_NAME**
- **Location**: `fill_env_identity` awk substitution
- **Edge case**: Operator passes `--prefix 'FOO\nMALICIOUS=1'` or project folder name contains back-ticks/newlines.  Value is pushed into `.env` unescaped.
- **What happens**: Results in multi-line injection: extra environment variables, potentially used by later tooling, with no validation.  Not remote-code-exec but breaks invariants and could smuggle secrets into logs.
- **Expected**: Validate `[A-Z0-9_-]+` for prefixes and names, or at least reject control characters.
- **Test coverage**: NOT covered.
- **Severity**: Latent / security hardening.

---

**[ROBUSTNESS]: `.env` placeholder “TASK” treated as always wrong**
- **Location**: `scripts/core/doctor.d/20-env-keys.py` (line ~90)
- **Edge case**: Legitimate legacy projects that *do* use prefix `TASK`.
- **What happens**: Doctor always WARNs, cannot be silenced.
- **Expected**: Allow opt-out (e.g. `TASK_PREFIX_FORCE=1`) or warn only when the project was created by the new door (has a creation marker).
- **Test coverage**: Explicitly asserts the constant behaviour; no test for legitimate TASK prefix.
- **Severity**: Gap / potential annoyance.

---

**[TESTING]: `copy_env_into_target` path where `.env` already exists is untested**
- **Location**: multiple call-sites
- **Edge case**: Re-running `bootstrap --new` after manual edits, or operator accidentally copies twice.
- **What happens**: File is overwritten with no confirmation.  Behaviour is undefined if file is a symlink.
- **Expected**: Unit or e2e test that existing non-symlink file is refused or merged.
- **Test coverage**: Not present.
- **Severity**: Gap

### Edge Cases Verified Clean
- Template missing → door prints warning and continues without crash.
- Mixed “export ” prefixes, quoted empty values – env-keys check flags them.
- Legacy first-session body removal path works for both new and legacy texts.

### Test Gap Summary

| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| Repo not yet initialised when `.env` copied | copy_env_into_target | No | Door aborts on custom exporters |
| Operator carry-over overwrite | offer_env_carryover | No | Silent data loss |
| Duplicate PROJECT_NAME/PREFIX lines | fill_env_identity | No | Identity drift under dotenv parsers |
| Control chars in prefix/name | fill_env_identity | No | Env poisoning |
| Legitimate TASK prefix | env-keys doctor | No | Permanent false WARN |
| Existing `.env` file on re-run | copy_env_into_target | No | Overwrite without notice |

### Verdict
**FAIL** – The new door flow contains two concrete correctness bugs that can abort an install or silently clobber `.env`, plus several latent robustness issues.  Fix at least the git-init ordering and the carry-over overwrite before merging.
### Log: claude-code

#  Claude Code

**Source**: /Users/broadcaster_one/Github/ask-worktrees/KIT-0084/.adversarial/inputs/KIT-0084-code-review-input.md
**Evaluator**: claude-code
**Model**: anthropic/claude-sonnet-4-6
**Generated**: 2026-08-04 19:35 UTC

---

# Code Review: KIT-0084

## Phase 1: Understand Intent

This PR implements "working `.env` from day one" for new projects created via `bootstrap --new`. Key goals:
1. **F1**: Seed `.env` (0600, gitignored) from preset env-source or `.env.template`
2. **F2**: Fill `PROJECT_NAME`/`TASK_PREFIX` identity fields; doctor warns on placeholder values
3. **F3**: Operator-consented API key carry-over (TTY prompt or printed command; never agent-executed)
4. **F4**: First-session CLAUDE.md region updated with doctor env-keys note
5. **F5**: `.env.template` comments updated to reflect actual mechanism

Critical paths: `copy_env_into_target()` (secret handling), `fill_env_identity()` (awk-based in-memory rewrite), `offer_env_carryover()` (consent boundary), `key_value()` in the doctor check.

---

## Phase 2: Security Analysis

### [MEDIUM]: In-memory `.env` Rewrite Exposes Content via Shell Variable

- **Location**: `scripts/local/bootstrap`, `fill_env_identity()`, around the `content="$(…)"` assignment
- **Issue**: The entire `.env` contents (including any API keys already seeded by `copy_env_into_target`) are captured into a shell variable `content` and then written back via `printf '%s\n' "$content"`. Shell variables holding secret material are visible in `/proc/<pid>/environ` on Linux and can appear in crash dumps or tracing tools. The comment says "no temp file" to avoid a gitignore gap, but the chosen alternative moves the exposure from filesystem to process memory/environment in a less controlled way.

  The risk is low in practice (short-lived process, operator-owned machine), but it's worth documenting. A more robust alternative would be a temp file written inside the target directory (which IS gitignored for `.env`) with a `.env.kit-tmp.XXXXX` name that also matches the gitignore pattern, followed by atomic rename — though the current approach is acceptable given the deployment context.

- **Remediation**: Add a comment explicitly acknowledging this trade-off. If hardening is desired, use a temp file with a name that matches the gitignore glob (e.g., `.env.tmp.*` added to `.gitignore` during bootstrap) and use `mktemp` + `mv` (the TEMP-THEN-COMMIT pattern used elsewhere).

---

### [LOW]: `offer_env_carryover` Prints Absolute Paths to Kit `.env` Without Checking Mode

- **Location**: `scripts/local/bootstrap`, `offer_env_carryover()`, the non-TTY branch
- **Issue**: The printed `cp` command includes the absolute path to the kit clone's `.env`. If the operator runs this in a logging environment (e.g., CI with captured output), the path is exposed in logs — though not the content. More importantly, the function does not check `$kit_env`'s file mode before printing it as a copy source. The `apply_env_source()` function warns when the source is not 0600; `offer_env_carryover()` silently proceeds regardless of the kit `.env`'s mode.
- **Remediation**: Add a mode check (similar to the one in `apply_env_source`) before suggesting the copy command:
  ```bash
  mode="$(stat -f '%Lp' "$kit_env" 2>/dev/null || stat -c '%a' "$kit_env" 2>/dev/null || echo unknown)"
  if [ "$mode" != "600" ]; then
      echo "Warning: $kit_env is mode $mode (expected 0600) — tighten it before copying" >&2
  fi
  ```

---

### [LOW]: `key_value()` — Commented-Out Assignment Returns `value_seen = ""`

- **Location**: `scripts/core/doctor.d/20-env-keys.py`, `key_value()`, lines handling the `TASK_PREFIX=` case
- **Issue**: When `TASK_PREFIX=` appears uncommented but empty, `value_seen` is set to `""`. When the function returns `value_seen` (which is `""`), the caller checks `prefix == ""` and correctly warns. However, if `TASK_PREFIX=` appears multiple times (e.g., a commented template line followed by an empty live line), the function exits early on the first non-empty value via `return value`. The scan logic mirrors `key_state()` in structure but does not handle the "whole file scan" semantic the same way for the case where a later uncommented line has a non-empty value after an earlier empty one. Specifically: the first NON-EMPTY assignment wins (per the docstring), but `value_seen = ""` is set on the first EMPTY assignment and never updated if a later line has a non-empty value. This means if the file has:
  ```
  TASK_PREFIX=
  TASK_PREFIX=MYPROJECT
  ```
  The function returns `""` (warns) instead of `"MYPROJECT"` (passes). This is the inverse of the `key_state()` "present wins" semantic.
- **Remediation**: Fix the scan to continue past empty assignments:
  ```python
  if value:
      return value
  value_seen = ""  # record that an empty assignment exists; keep scanning
  # do NOT return here — a later non-empty line should win
  ```
  Actually, looking at the code again, this IS what the code does — `value_seen = ""` and then `continue` (via the loop). But the issue is that `return value` only fires when `value` is truthy, so an empty value falls through to `value_seen = ""` and continues. A subsequent non-empty value would correctly `return value`. The logic is actually correct. **Retracting this finding** — the code is correct for this case.

---

### [LOW]: `fill_env_identity` Writes `.env` Without Verifying Gitignore First

- **Location**: `scripts/local/bootstrap`, `fill_env_identity()`
- **Issue**: `fill_env_identity()` rewrites `$TARGET/.env` using `printf '%s\n' "$content" > "$TARGET/.env"` but does NOT call `git check-ignore` first (unlike `copy_env_into_target`). The function is called after `copy_env_into_target` has already verified gitignore, so in the normal flow this is fine. However, if `fill_env_identity()` were ever called independently (e.g., sourced in a test with only `TARGET` set and no prior gitignore check), it would write without the guard.
- **Remediation**: This is a defense-in-depth concern given the current call sites. Document explicitly in the function that callers must ensure `.env` is gitignored before calling (or add the check). The test `TestFillEnvIdentityUnits` does not set up gitignore, which confirms the function skips this check.

---

### [POSITIVE]: No Hardcoded Credentials

No API keys, tokens, or secrets appear anywhere in the changed code. Test fixtures use clearly labeled dummy strings (`KIT0056-FIXTURE-SECRET-NEVER-PRINT`, `sk-test-*`).

### [POSITIVE]: Values Passed via Environment to awk, Never Interpolated

The `fill_env_identity` function passes `PROJECT_NAME` and `TASK_PREFIX` values via `ENV_NAME`/`ENV_PREFIX` environment variables to `awk` using `ENVIRON[]`, never via `-v` or string interpolation into the awk program. This correctly prevents injection through operator-supplied project names containing special characters.

### [POSITIVE]: umask-First File Creation

`copy_env_into_target()` uses `(umask 077; cat "$1" > "$TARGET/.env")` followed by `chmod 600`, ensuring the file is born at mode 0600 with no window at looser permissions.

### [POSITIVE]: Gitignore Check Before Any Secret Write

`copy_env_into_target()` calls `git check-ignore -q .env` before writing, refusing to proceed if `.env` is not gitignored.

### [POSITIVE]: Secret Values Never Echoed

All seeding functions explicitly state and demonstrate that contents are never printed. The test suite asserts this (`assert SECRET not in result.stdout + result.stderr`).

---

## Phase 3: Correctness Analysis

### [MEDIUM]: `fill_env_identity` — Trailing Newline Behavior with `printf '%s\n'`

- **Location**: `scripts/local/bootstrap`, `fill_env_identity()`
- **Issue**: The content is captured via command substitution: `content="$(… awk … "$TARGET/.env")"`. Command substitution strips trailing newlines. If the original `.env` ends with content followed by a newline (standard), the captured string loses that trailing newline. Then `printf '%s\n' "$content"` adds exactly one newline back. This means:
  - A file ending in `\n` → captured without `\n` → written with `\n` ✓
  - A file ending in `\n\n` (blank line at end) → captured without both trailing `\n`s → written with one `\n` — the blank line is lost.
  - A file NOT ending in `\n` (non-standard) → written with `\n` added — this changes the file.

  In practice, `.env.template` ends with a final newline, so the seeded `.env` will too, and this is correct behavior. The edge case of trailing blank lines being stripped is cosmetic for `.env` files.

- **Remediation**: Acceptable for this use case. A comment noting the trailing-newline behavior would help future maintainers.

---

### [LOW]: `key_value()` Does Not Handle Multi-Line Values or Continuation

- **Location**: `scripts/core/doctor.d/20-env-keys.py`, `key_value()`
- **Issue**: Like `key_state()`, this function processes one line at a time and doesn't handle quoted values spanning multiple lines or backslash continuations. This is consistent with the existing `key_state()` behavior and appropriate for a `.env` parser that explicitly documents "strict `KEY=value` format."
- **Remediation**: No change needed; the existing behavior is consistent and documented.

---

### [LOW]: `remove_region_if_unmodified` — Legacy Body Comparison Is Exact String Match

- **Location**: `scripts/local/engine-consumer.sh`, `remove_region_if_unmodified()`
- **Issue**: The `$4` legacy body parameter is compared with `[ "$REGION_BODY_NOW" != "$4" ]`. This works correctly for exact matches. However, if a consumer has the legacy body with a trailing newline difference (e.g., their editor added a trailing newline after the region content), it would not match as "unmodified" and would be incorrectly preserved as "customized." This is an edge case in existing pre-KIT-0084 consumers.
- **Remediation**: Low risk. The `kit_markers extract` output is deterministic, so trailing newline differences are unlikely. No change needed.

---

### [MEDIUM]: `offer_env_carryover` — TTY Path Calls `copy_env_into_target` Which Calls `exit 1`

- **Location**: `scripts/local/bootstrap`, `offer_env_carryover()` and `copy_env_into_target()`
- **Issue**: When the operator answers "yes" to the consent prompt, `copy_env_into_target` is called with the kit's `.env` as source. If the gitignore check fails (`git check-ignore -q .env` returns non-zero), `copy_env_into_target` calls `exit 1`. This is correct behavior — but in the TTY path, the operator has just been prompted and consented, and then the process exits with "refusing to seed secrets." The error message is accurate but the UX is slightly jarring (consent granted, then immediate exit). This is acceptable since the gitignore check should pass (it was already verified during `seed_env_from_template`), but if the `.env` somehow got un-gitignored between those two calls, the error is correct.
- **Remediation**: Not a bug; the defense-in-depth check is correct. No change needed.

---

### [LOW]: `test_no_kit_rebootstrap_removes_legacy_first_session_body` — Fragile String Splitting

- **Location**: `tests/test_bootstrap_shapes.py`, `test_no_kit_rebootstrap_removes_legacy_first_session_body()`
- **Issue**: The test uses `.split(begin)` and `.split(end)` to manipulate CLAUDE.md content. If `begin` or `end` appear more than once in the file (e.g., the file already has two first-session regions due to a bug being tested), `split()` with no maxsplit would produce more than 2 parts and the unpacking `head, rest = seeded.split(begin)` would raise `ValueError`. This is a test-only concern.
- **Remediation**: Use `split(begin, 1)` and `split(end, 1)` for robustness:
  ```python
  head, rest = seeded.split(begin, 1)
  _, tail = rest.split(end, 1)
  ```

---

## Phase 4: Code Quality

### [LOW]: `fill_env_identity` — Python Heredoc Uses BASH-Style PYEOF but Runs in Subshell

- **Location**: `scripts/local/bootstrap`, `fill_env_identity()`
- **Issue**: The `python3 - "$TARGET/.kit/context/current-state.json" 2>/dev/null <<'PYEOF' ... PYEOF` construct is correct and works properly. The `2>/dev/null` suppresses errors (e.g., missing JSON file), and the `|| prefix=""` handles Python exit failures. The `[ -n "$prefix" ] || prefix="$PREFIX"` fallback to the CLI-supplied `$PREFIX` is a good defensive measure.

  One subtle issue: if `python3` is not available on `PATH`, the command substitution itself might fail. Under `set -e`, this would exit the script. The `2>/dev/null` only suppresses stderr, not the exit code. The `|| prefix=""` handles this correctly since it catches any non-zero exit.
- **Remediation**: No change needed; the error handling is correct.

---

### [LOW]: Inconsistent Quoting in `offer_env_carryover` Printed Command

- **Location**: `scripts/local/bootstrap`, `offer_env_carryover()`, non-TTY branch
- **Issue**: The printed copy command `cp $kit_env $TARGET/.env && chmod 600 $TARGET/.env` is printed without quoting the paths. If `$kit_env` or `$TARGET` contain spaces or special characters, the printed command would be incorrect when copy-pasted.
- **Remediation**: Quote the paths in the printed command:
  ```bash
  echo "    cp \"$kit_env\" \"$TARGET/.env\" && chmod 600 \"$TARGET/.env\""
  ```
  This is a UX issue, not a security issue (the values are not being executed here, only printed).

---

### [POSITIVE]: Comprehensive Test Coverage

The PR adds well-structured tests:
- `TestTaskPrefixWarn` covers all three warn cases (empty, missing, placeholder) plus combined warnings and commented-line behavior
- `TestEnvSeedingE2E` covers single/planning shapes, preset env-source path, and the non-TTY carry-over message
- `TestFillEnvIdentityUnits` tests the in-memory rewrite in isolation via `sourced()`
- The legacy body upgrade path test is well-designed and tests the exact scenario it was built for

### [POSITIVE]: Security Boundary Clearly Documented

The operator/agent boundary is explicitly documented in multiple places (bootstrap header comment, `docs/STARTING-A-PROJECT.md`, `offer_env_carryover()` comments, CLAUDE.md first-session region). The rationale (permission classifier blocks agent-side key copies) is accurate and actionable.

### [POSITIVE]: Upgrade Path Handled

The `FIRST_SESSION_BODY_LEGACY` mechanism for handling pre-KIT-0084 consumers on `--no-kit` re-bootstrap is clean and the test covers it specifically.

### [POSITIVE]: GIT_* Variable Scrubbing

Both `bootstrap` and `engine-consumer.sh` scrub all `GIT_*` variables at startup, preventing the KIT-0048 class of GIT_DIR leak corruption.

---

## Context Required / Unverifiable

- The behavior of `is_tty` in CI and automated environments cannot be confirmed without runtime context. Tests use `stdin=subprocess.DEVNULL` which correctly triggers the non-TTY path.
- The `stat -f '%Lp'` (macOS) vs `stat -c '%a'` (Linux) fallback for mode checking is inherited from existing code and assumed correct.
- The `git check-ignore` behavior with `.gitignore` patterns containing `.env` is assumed to work as expected; this is not exercised with a real `.gitignore` in `TestFillEnvIdentityUnits` (only in `TestEnvSeedingE2E`).
- Whether the Claude Code permission classifier actually blocks agent-side `.env` writes is a runtime claim that cannot be verified from the code alone.

---

## Overall Assessment

**APPROVED**

The implementation is security-conscious and well-executed. The critical path — secret file creation — correctly implements umask-first permissions, gitignore verification, and non-printing discipline. Values are passed to `awk` via environment variables, not string interpolation. The operator/agent boundary is clearly defined and documented. Test coverage is thorough with both unit and E2E tests.

The findings are:
- Two **MEDIUM** issues: an acknowledged trade-off (shell variable holding `.env` contents during rewrite) and a cosmetic trailing-newline behavior — neither is a security vulnerability
- Three **LOW** issues: a missing mode-check before printing the carry-over command, a test robustness improvement, and a UX issue with unquoted paths in printed commands

None of these block production readiness. The medium findings should be tracked as follow-up improvements but do not require rework before merge.
