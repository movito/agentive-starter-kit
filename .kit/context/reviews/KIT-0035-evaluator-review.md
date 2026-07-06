# KIT-0035 Evaluator Review — PR 1 (dev-env & evaluator friction)

**Date**: 2026-07-06
**Trio**: code-reviewer-fast-v2 (Gemini), code-reviewer (o3), claude-code (Sonnet)
**Ordering**: run BEFORE PR open — dogfooding the F3 rule this PR introduces
**Verdicts**: fast-v2 CONCERNS (r1+r2) · o3 FAIL · claude-code CHANGES_REQUESTED

## Disposition

### Accepted (fixed in `ebb4224` and follow-up commit)

| Finding | Source | Fix |
|---------|--------|-----|
| pyproject grep would emit stderr noise if file absent | fast-v2 r1/r2 | `2>/dev/null` on the grep |
| Version pattern could in principle match a bare integer if Black's output format changed | claude-code (MEDIUM) | `ACTIVE_BLACK` pattern now requires a dotted version |
| Doc-heavy exception was binary ("docs only"), excluding doc-dominated mixed tasks | fast-v2 r1 (INTERACTION) | Reworded in skill + both feature-developer agents: doc-*dominated* qualifies |
| TTY hint checked stdout only; stdin is what the CLI prompt reads | fast-v2 r2 | Hint fires when either fd 0 or fd 1 is non-TTY |

### Declined with evidence

| Finding | Source | Why declined |
|---------|--------|--------------|
| `set -e` hard-exits when Black missing | o3 (FAIL driver) | Empirically false: pipeline ends in `head -1` (exit 0). Tested: `bash -c 'set -e; V=$(no-such-cmd --version 2>/dev/null \| head -1 \| grep -Eo ... \| head -1); echo survived'` → survives, empty var, warn skipped. |
| Extraction yields `26` not `26.3.1` | claude-code (MEDIUM) | Empirically false: `grep -o` is leftmost-*longest*; live run extracted `26.3.1`. Dotted pattern adopted anyway as belt-and-braces. |
| Non-`==` pin styles (`>=`, `~=`, Poetry tables) silently disable the check | o3, fast-v2 | By design: the check is warn-only and fail-open. Drift is only well-defined against an exact `==` pin (that is also why isort's `>=` floor is excluded — documented in the inline comment). |
| Auto-export `ADVERSARIAL_UNATTENDED` instead of printing it | o3 | A child process cannot export into the caller's shell; the printed export line at the top of the copied Next-steps block is the correct mechanism (also noted inline). |
| Large-diff memory blow-up, tab-in-filename parsing, 4-backtick fence collision, path traversal via git index | o3, fast-v2 | Pre-existing `prepare-review-input.sh` internals — not introduced or touched by this PR (KIT-0040 retro: external-finding yield concentrates on fresh code). Candidates for a future hardening task if they ever bite. |
| `synced_at` not updated with `core_version` bump | claude-code (LOW) | `synced_at` records consumer sync time, not source edit time — historically untouched by source-side version bumps (KIT-0036 precedent). |
| Literal string comparison risks false positives on version metadata variants | fast-v2 r2 | Theoretical for Black (plain `X.Y.Z` releases); warn-only path, zero build impact. |

## Raw evaluator logs

## Source: KIT-0035-code-review-input--code-reviewer-fast-v2.md

#  Code Reviewer Fast V2

**Source**: .adversarial/inputs/KIT-0035-code-review-input.md
**Evaluator**: code-reviewer-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-07-06 00:15 UTC

---

### Findings

**[CORRECTNESS]: Potential infinite `grep` or incorrect matching in `ci-check.sh`**
- **Location**: `scripts/core/ci-check.sh:65`
- **Edge case**: `pyproject.toml` missing the `black==` string or multiple matches found.
- **What happens**: `grep -Eo 'black==[0-9][0-9A-Za-z.]*'` is piped to `head -1`. If `pyproject.toml` is absent or doesn't match, `PINNED_BLACK` is empty. While the `if` check handles the empty case, the logic assumes `black` is always pinned with `==`. If a user uses `>=` or `~=`, the check silently skips. More importantly, if `pyproject.toml` contains many occurrences of the word "black" in descriptions or other tool configs, the current regex might pull the wrong version string if it's not strictly formatted.
- **Tested?**: No

**[ROBUSTNESS]: `ADVERSARIAL_UNATTENDED` check relies on `stdout`, not `stdin`**
- **Location**: `scripts/core/prepare-review-input.sh:472`
- **Edge case**: Script run inside a `cron` job or a CI runner where `stdout` is captured but `stdin` is not necessarily connected to a TTY.
- **What happens**: The script checks `[ ! -t 1 ]` (stdout). However, the `adversarial` CLI likely checks `stdin` (`-t 0`) to determine if it should prompt `[y/N]`. If a user runs the script in a way where stdout is piped to a file but stdin is still a TTY, the warning will be printed, but the environment variable isn't strictly necessary. Conversely, if stdin is redirected but stdout isn't, the warning won't show, but the CLI will fail.
- **Tested?**: No

**[INTERACTION]: `PINNED_BLACK` and `ACTIVE_BLACK` version string mismatch**
- **Location**: `scripts/core/ci-check.sh:65-66`
- **Edge case**: Version strings with different verbosity (e.g., `24.1.1` vs `24.1.1.0`).
- **What happens**: The script uses a strict string comparison `[ "$PINNED_BLACK" != "$ACTIVE_BLACK" ]`. Because `black --version` output can vary by OS/distro and `pyproject.toml` might include extras or specific build metadata, a literal string comparison is prone to false-positive warnings.
- **Tested?**: No

**[CORRECTNESS]: Broken path logic in `ci-check.sh` pre-activation**
- **Location**: `scripts/core/ci-check.sh:65`
- **Edge case**: Script run from a subdirectory other than the project root.
- **What happens**: Although the script performs `cd "$PROJECT_ROOT"`, the `grep` for `pyproject.toml` uses a relative path. If for any reason the `cd` failed (though `set -e` is on), or if `pyproject.toml` is in a different location in a consumer repo, `PINNED_BLACK` will be empty. The script does not verify the existence of `pyproject.toml` before grepping, which would emit a "No such file or directory" error to stderr mid-execution.
- **Tested?**: No

### Test Gap Summary

| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| Missing `pyproject.toml` | `ci-check.sh` | No | Low (stderr noise) |
| Non-standard Black pin (`>=`, `~=`) | `ci-check.sh` | No | Medium (Missing warning) |
| Version string metadata mismatch | `ci-check.sh` | No | Low (False positive warning) |
| Large input in non-TTY stdin | `prepare-review-input.sh` | No | Medium (Agent hangs/fails) |

### Verdict

**CONCERNS**

The logic in `ci-check.sh` for version checking is fragile. It assumes a specific pinning style (`==`) and relies on literal string equality, which is risky for version numbers across different environments. Additionally, the TTY check in `prepare-review-input.sh` should ideally check `stdin` rather than `stdout` to accurately predict when the `adversarial` CLI will hang.

The changes to the `.md` files (agents and skills) are structurally sound and follow the provided requirements faithfully. No logic errors were found in the documentation-heavy sections.

**Must fix prior to merge**:
1. Change `[ ! -t 1 ]` to `[ ! -t 0 ]` in `prepare-review-input.sh` to correctly detect if the user can interact with the CLI.
2. In `ci-check.sh`, redirect `grep` stderr to `/dev/null` or verify `pyproject.toml` existence to avoid noise in environments where the file is missing.
## Source: KIT-0035-code-review-input--code-reviewer.md

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0035-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-06 00:11 UTC

---

### Summary
Reviewed the shell additions in `scripts/core/ci-check.sh` (Black-version drift warning) and the tail changes in `scripts/core/prepare-review-input.sh` (non-TTY hint).
Found 6 non-trivial issues: 3 correctness / robustness bugs, 1 interaction hazard, 2 test gaps. No new race conditions spotted.

### Findings

**[CORRECTNESS]: `set -e` causes hard exit when Black is missing**
- **Location**: `scripts/core/ci-check.sh` (lines 52-62)
- **Edge case**: Developer has not installed Black (`black` not on `$PATH`) or is in a fresh venv.
- **What happens**: `ACTIVE_BLACK=$(black --version …)` is executed while `set -e` is active. The command returns 127 → the *entire script aborts immediately* before the user-friendly check or any other CI steps run. This is a regression; earlier versions only failed Black inside an `if black --check …` guard that didn’t abort.
- **Expected**: Script should fall back to “Black not installed” warning (symmetrical to the flake8 pre-flight) and continue to later steps, or fail with a clear message, but not die mid-assignment.
- **Test coverage**: NOT covered (no harness).
- **Severity**: Bug

---

**[ROBUSTNESS]: Pinned-version grep misses quoted / tool-table pins**
- **Location**: `ci-check.sh` (lines 55-57)
- **Edge case**: `pyproject.toml` using Poetry-style tables or quotes, e.g.
  `black = {version = "^26.3"}`  or `"black==26.3.1"` inside a multiline string.
- **What happens**: `grep -Eo 'black==…'` finds nothing → `PINNED_BLACK` empty → drift check silently disabled even though a pin exists.
- **Expected**: Parse `tool.poetry.dependencies.black` or read `pyproject.toml` with `tomllib`/`python -c` so all pin syntaxes work.
- **Test coverage**: NOT covered.
- **Severity**: Latent

---

**[ROBUSTNESS]: Memory blow-up on large diffs**
- **Location**: `prepare-review-input.sh` (~300, ~320) – captures full diff into `DIFF_CONTENT` variable.
- **Edge case**: Very large PR (e.g. vendor drop, 20-30 MB diff).
- **What happens**: Entire diff is loaded into one shell variable; Bash hits the 128 MiB limit or exhausts memory → script aborts or truncates silently.
- **Expected**: Stream diff straight to file (`git … diff … >> "$OUTPUT_FILE"`), avoiding huge in-memory strings.
- **Test coverage**: NOT covered.
- **Severity**: Latent

---

**[CORRECTNESS]: Markdown fence can be prematurely closed**
- **Location**: `prepare-review-input.sh` – emits four-backtick fences around file bodies.
- **Edge case**: Source file itself contains ```` (four backticks) sequence (common in Markdown docs showing triple-backtick examples).
- **What happens**: Outer fence closes early, the remainder of the file is emitted as raw markdown, mangling the input; evaluators may mis-parse or the rest of the script’s output becomes invalid Markdown.
- **Expected**: Choose fence length dynamically (number of backticks ≥ longest sequence + 1) or use indentation fencing.
- **Test coverage**: NOT covered.
- **Severity**: Latent

---

**[CORRECTNESS]: Tab character in filenames breaks status parsing**
- **Location**: `prepare-review-input.sh` (loop over `git diff --name-status`)
- **Edge case**: File name contains a literal tab (`\t`). Git will quote the path; the script splits on tab (`IFS=$'\t'`) and mis-parses the line, producing wrong `file_path`.
- **What happens**: Changed file is skipped or wrong path concatenated → missing content in full-file appendix; evaluator may flag “file missing”.
- **Expected**: Use `git diff -z --name-status` (+ `IFS=`, `read -r -d ''`) or rely on `git ls-files -z`-style parsing that handles embedded tabs/newlines.
- **Test coverage**: NOT covered.
- **Severity**: Latent

---

**[INTERACTION]: Non-TTY hint printed but not useful in scripted flows**
- **Location**: `prepare-review-input.sh` (lines 468-475)
- **Edge case**: Script runs in CI or another non-TTY automation; operator copies “Next steps” block verbatim (three `adversarial` commands) into the same non-TTY shell.
- **What happens**: Variable `ADVERSARIAL_UNATTENDED` is *not* exported (only suggested). Subsequent evaluator commands still hang on large input.
- **Expected**: Auto-export when `! -t 1` (`export ADVERSARIAL_UNATTENDED=1`) or prefix it to the printed commands.
- **Test coverage**: NOT covered.
- **Severity**: Gap/Usability

### Edge Cases Verified Clean
• Whitespace in `TARGET_PATH` is rejected with clear error.
• Empty diff handled (prints warning but generates file).
• Deleted files correctly skipped in full-content section.
• Missing API keys only documented – no code path alters `.env`.

### Test Gap Summary
| Edge Case | Function / Script | Tested? | Risk |
|-----------|------------------|---------|------|
| Black not installed | ci-check.sh | No | High (script abort) |
| Non-`black==` pin formats | ci-check.sh | No | Medium |
| Large diff (>128 MiB) | prepare-review-input.sh | No | Medium |
| 4-backtick collision | prepare-review-input.sh | No | Medium |
| Tab in filename | prepare-review-input.sh | No | Low |
| Non-TTY evaluator flow | prepare-review-input.sh | No | Low |

### Verdict
**FAIL**

The new Black-drift preflight introduces a hard-exit regression when Black is missing (`set -e` + command substitution). Other robustness gaps could silently drop files or corrupt the generated review input. Address at least the hard-exit defect before merge.
## Source: KIT-0035-code-review-input--claude-code.md

#  Claude Code

**Source**: .adversarial/inputs/KIT-0035-code-review-input.md
**Evaluator**: claude-code
**Model**: anthropic/claude-sonnet-4-6
**Generated**: 2026-07-06 00:12 UTC

---

## Phase 1: Understand Intent

This PR is a **documentation and tooling hardening change** for the `agentive-starter-kit` — an AI agent workflow framework. It addresses developer-experience friction surfaced in KIT-0032 and KIT-0040 retrospectives. The changes are:

1. **`ci-check.sh`**: Adds a warning when the active Black version differs from the `pyproject.toml` pin
2. **`prepare-review-input.sh`**: Surfaces `ADVERSARIAL_UNATTENDED=1` for non-TTY sessions; adds it to the static help text
3. **Agent/skill docs**: Adds evaluator-ordering guidance for doc-heavy tasks, v2 evaluator discovery instructions, and API key notes
4. **Metadata/housekeeping**: Task status promotion, version bumps, path updates

Critical paths: `ci-check.sh` (runs in dev/CI), `prepare-review-input.sh` (agent automation), agent spec files (behavioral instructions for LLM agents).

---

## Phase 2: Security Analysis

### Injection Vectors

**`ci-check.sh` — version string injection via `pyproject.toml`**

The new Black version check reads data from `pyproject.toml` and interpolates it into `echo` output:

```bash
PINNED_BLACK=$(grep -Eo 'black==[0-9][0-9A-Za-z.]*' pyproject.toml | head -1 | sed 's/^black==//')
ACTIVE_BLACK=$(black --version 2>/dev/null | head -1 | grep -Eo '[0-9][0-9A-Za-z.]*' | head -1)
if [ -n "$PINNED_BLACK" ] && [ -n "$ACTIVE_BLACK" ] && [ "$PINNED_BLACK" != "$ACTIVE_BLACK" ]; then
    echo "⚠️  Active Black $ACTIVE_BLACK differs from pyproject.toml pin $PINNED_BLACK"
```

The regex `[0-9][0-9A-Za-z.]*` constrains both variables tightly. Neither value can contain shell metacharacters (no spaces, `$`, backticks, semicolons, etc.). The variables are only used in `echo` and string comparison — no `eval`, no command substitution with user data. **Risk: negligible.** The worst-case `pyproject.toml` craft is a denial-of-service (confusing output), not code execution.

**`prepare-review-input.sh` — TASK_ID validation**

```bash
if ! printf '%s' "$TASK_ID" | grep -qE '^[A-Z][A-Z0-9]*-[A-Z0-9]+$'; then
    echo "ERROR: TASK-ID must look like ABC-123 or ABC-TEST, got: '$TASK_ID'" >&2
    exit 1
fi
```

TASK_ID is validated against a strict allowlist regex before use in the output filename. The output path is:

```bash
OUTPUT_FILE="$OUTPUT_DIR/${TASK_ID}-code-review-input.md"
```

With the regex, TASK_ID can only be alphanumeric + hyphen, no path traversal possible. Good.

**Whitespace-in-path protection:**

```bash
case "$TARGET_PATH" in
    *[[:space:]]*)
        echo "ERROR: TARGET_PATH '$TARGET_PATH' contains whitespace" >&2
        exit 1
        ;;
esac
```

This is present and correctly blocks the word-splitting footgun. However, `TARGET_PATH` is still echoed into an error message unquoted in concept but the echo uses double quotes, which is safe for display. Good.

**`prepare-review-input.sh` — shell variable quoting**

The `GIT_DIR_ARG` variable is intentionally unquoted (to allow empty-string collapse). The comment acknowledges this. Given TARGET_PATH is already validated as whitespace-free, this is acceptable. The `# shellcheck disable=SC2086` annotations are present.

**No hardcoded credentials or secrets** observed anywhere in the diff.

**No command injection vectors** via user-controlled data in the new code paths.

---

## Phase 3: Correctness Analysis

### MEDIUM: Black Version Comparison May Produce False Positives on Pre-release Versions

**Location**: `scripts/core/ci-check.sh`, new preflight block

**Issue**: The `ACTIVE_BLACK` regex `[0-9][0-9A-Za-z.]*` matches version strings correctly, but `head -1` on `black --version` output produces something like `black, 26.3.1 (Python 3.11.x)`. The extraction regex then picks the **first numeric token** — which is `26` (a bare integer, not `26.3.1`). This produces:

```
⚠️  Active Black 26 differs from pyproject.toml pin 26.3.1
```

A spurious warning on a correctly configured environment. This is a warn-only path (not a gate), so it cannot cause false build failures, but it degrades signal quality.

```bash
# Current:
ACTIVE_BLACK=$(black --version 2>/dev/null | head -1 | grep -Eo '[0-9][0-9A-Za-z.]*' | head -1)
# Typical output: "black, 26.3.1 (Python 3.11.9)"
# Extracts: "26" (first match, not "26.3.1")
```

**Remediation**:
```bash
# Match the full semver-like token after ", " :
ACTIVE_BLACK=$(black --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+[A-Za-z0-9.]*' | head -1)
```

Or use `awk`:
```bash
ACTIVE_BLACK=$(black --version 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i ~ /^[0-9]+\.[0-9]/) {print $i; exit}}')
```

---

### LOW: `ADVERSARIAL_UNATTENDED` Export Hint Only Shown in Non-TTY; Static Help Always Shows It

**Location**: `scripts/core/prepare-review-input.sh`, lines ~468-471 (summary block) vs. `usage()` function (~L102)

**Issue**: The `usage()` static help text unconditionally shows `export ADVERSARIAL_UNATTENDED=1`, while the end-of-run summary only shows it when `[ ! -t 1 ]`. This is the intended behavior (help is printed to stdout before the TTY check matters), and the comment explains the rationale. However, the static help text says "non-TTY sessions only" which is accurate. No functional bug — this is a minor consistency note.

The non-TTY check `[ ! -t 1 ]` tests whether **stdout** is a TTY. In agent sessions, this is the correct signal. However, if the script is run with stdout redirected to a file (e.g., `./prepare-review-input.sh KIT-0035 > out.txt`) in an interactive terminal session, it will also show the hint. This is a cosmetic false positive, not a correctness issue.

---

### LOW: `CHANGED_COUNT` Line Count Off-by-One Possible for Single-File Changes

**Location**: `scripts/core/prepare-review-input.sh`, near the end

```bash
CHANGED_COUNT=$(printf '%s\n' "$CHANGED_STATUS" | wc -l | tr -d ' ')
```

`wc -l` counts newlines. If `CHANGED_STATUS` ends with a newline, count is correct. `git diff --name-status` output typically ends with a newline, making the count accurate. This is a pre-existing pattern, not introduced by this PR. No change needed.

---

### LOW: `PINNED_BLACK` May Be Empty Without Clear Indication

**Location**: `scripts/core/ci-check.sh`, new preflight block

```bash
PINNED_BLACK=$(grep -Eo 'black==[0-9][0-9A-Za-z.]*' pyproject.toml | head -1 | sed 's/^black==//')
```

If the `pyproject.toml` format changes (e.g., uses `black >= 26.0` instead of `black==26.3.1`), `PINNED_BLACK` will be empty, and the entire warning block is silently skipped (due to `[ -n "$PINNED_BLACK" ]`). This is intentional and safe — no false positive — but means the warning silently disappears if the pin format changes, which could be surprising. The task spec notes isort uses `>=` and explicitly says "no drift check applies there," showing this was considered. Acceptable as-is.

---

### LOW: Version Bump in Manifest `synced_at` Not Updated

**Location**: `scripts/.core-manifest.json`

```json
"core_version": "3.1.0",
"synced_at": "2026-06-13T00:00:00Z",
```

The `core_version` was bumped to `3.1.0` but `synced_at` still reflects `2026-06-13`. If consumers use `synced_at` to determine staleness, this could mislead them. However, the manifest's README/docs suggest this timestamp reflects the last consumer-sync time, not the source edit time. Still worth flagging.

---

## Phase 4: Code Quality

### Positive Observations

**Excellent defensive coding throughout `prepare-review-input.sh`:**
- TASK_ID validated against strict regex before filesystem use
- Whitespace-in-path detection with clear error messages
- Lockfile detection and skip with explicit notes
- Binary file detection via `grep -Iq`
- Empty file handling before binary detection (prevents misclassification)
- 4-backtick outer fences to prevent premature code fence closure in markdown output
- `printf '%s\n'` instead of `echo` for arbitrary string content
- Explicit `shellcheck disable` annotations where intentional
- `set -e` with explicit exit codes throughout

**Good documentation hygiene:**
- Every non-obvious decision has an inline comment explaining *why*, not just *what*
- Retro cross-references (KIT-0032, KIT-0040) link decisions to evidence
- The `ADVERSARIAL_UNATTENDED` hint correctly explains it cannot be exported into the caller's shell

**Correct separation of concerns:**
- Warning is warn-only (N2 requirement honored): Black version mismatch does not fail the build
- `prepare-review-input.sh` correctly avoids auto-setting the env var (can't export into caller's shell) and instead prints the export line

**Agent spec changes are well-scoped:**
- The doc-heavy ordering exception is clearly labeled as an exception, not a blanket rule
- Code-heavy tasks explicitly retain the original CI/bots-first order
- The `claude-code` key note includes the verification command and the "never add a key" rule

---

## Findings

### [MEDIUM]: Black Version Extraction May Produce Truncated Version String
- **Location**: `scripts/core/ci-check.sh`, new preflight block (~line 63)
- **Issue**: `grep -Eo '[0-9][0-9A-Za-z.]*' | head -1` on `black --version` output (e.g., `black, 26.3.1 (Python 3.11.9)`) extracts `26` as the first match, not `26.3.1`. This causes a spurious mismatch warning even when Black is correctly installed — the warning fires comparing `26` (extracted active) against `26.3.1` (pinned).
- **Remediation**:
  ```bash
  ACTIVE_BLACK=$(black --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+[A-Za-z0-9.]*' | head -1)
  ```
  This matches the full dotted version token. Alternatively: `| awk '{for(i=1;i<=NF;i++) if($i~/^[0-9]+\.[0-9]/) {print $i; exit}}'`

### [LOW]: `synced_at` in `.core-manifest.json` Not Updated With Version Bump
- **Location**: `scripts/.core-manifest.json`, `synced_at` field
- **Issue**: `core_version` bumped from `3.0.0` to `3.1.0` but `synced_at` remains `2026-06-13T00:00:00Z`. Depending on how consumers interpret this field, it may indicate a stale sync.
- **Remediation**: Update `synced_at` to reflect the current date when bumping `core_version`, or document that `synced_at` reflects consumer sync time (not source edit time) — whichever is the intended semantics.

### [LOW]: TTY Check Tests Stdout, Not "Is This an Agent Session"
- **Location**: `scripts/core/prepare-review-input.sh`, ~line 471
- **Issue**: `[ ! -t 1 ]` detects non-TTY stdout, which includes pipe redirection in interactive sessions. This is a cosmetic false positive (the hint appears when `./prepare-review-input.sh KIT-0035 | tee out.txt` is run manually). No functional impact — the hint is correct advice in all such cases.
- **Remediation**: Accept as-is or add a note in the comment explaining the deliberate choice. Current inline comment is already accurate.

---

### Positive Observations

- Input validation on TASK_ID (strict allowlist regex) prevents path traversal
- Whitespace-in-path check on TARGET_PATH prevents word-splitting injection
- `set -e` throughout shell scripts with explicit exit codes
- All `shellcheck disable` suppressions are explained with inline rationale
- Warning-only design for version mismatch (does not gate the build — N2 honored)
- The `ADVERSARIAL_UNATTENDED` note correctly avoids attempting `export` in the child shell
- Agent spec docs cleanly scope the ordering exception to doc-heavy tasks only
- `printf '%s\n'` used instead of `echo` for content that may start with `-`
- 4-backtick outer fences prevent markdown fence injection in generated review files
- No hardcoded credentials anywhere; explicit "never add a key" instructions in two places

---

## Context Required / Unverifiable

- **`black --version` output format**: The exact output format of `black --version` on the pinned version `26.3.1` cannot be verified here. If the format differs from `black, X.Y.Z (Python ...)`, the extraction behavior may differ. The MEDIUM finding above is based on documented Black behavior across versions.
- **`adversarial` CLI behavior**: The `ADVERSARIAL_UNATTENDED` env var behavior, the auto-cancel threshold, and the `list-evaluators` subcommand are described but not verifiable from this code.
- **`target_repo.sh` library**: The `target_repo_init`, `target_repo_is_set` functions are imported but the library isn't in this diff. The whitespace guard is present; full behavior of these functions is unverifiable.
- **`synced_at` semantics**: Whether this field is consumer-written (updated on sync) or source-written (updated on release) determines whether the LOW finding is a real issue.

---

## Overall Assessment

**CHANGES_REQUESTED**

The PR is well-constructed with a clear intent, good inline documentation, and solid defensive coding practices throughout the shell scripts. The security posture is sound: no injection vulnerabilities, no credential exposure, correct input validation.

The **one issue requiring a fix before merge** is the MEDIUM finding: the Black version extraction regex will produce a truncated version string (`26` instead of `26.3.1`) on current Black output format, generating spurious warnings on correctly-configured environments. Since the entire value of F1 is accurate diagnostic output, this defeats the purpose of the feature and should be corrected. The fix is a one-line regex change.

The LOW findings (manifest timestamp, TTY check scope) are minor and can be addressed at the author's discretion — the manifest timestamp in particular warrants clarification of intended semantics.
