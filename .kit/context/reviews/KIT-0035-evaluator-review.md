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

---

# KIT-0035 Evaluator Review — PR 2 (upgrade-guide grep hardening, #73)

**Date**: 2026-07-06
**Evaluators**: code-reviewer-fast-v2 (Gemini), code-reviewer (o3) — doc-only PR, run BEFORE PR open per the F3 ordering rule
**Verdicts**: fast-v2 CONCERNS (r1+r2) · o3 FAIL (r1)

## Disposition

### Accepted (fixed in the round-1 fix commit)

| Finding | Source | Fix |
|---------|--------|-----|
| `github.*movito/...` matched a local checkout path (`Directory (/Users/alice/github/movito/agentive-skills)`), bypassing the pin guard | o3 (FAIL driver) + fast-v2 — convergent | Pattern anchored to the `Source:` field; accepts only the GitHub paren form or github.com URL form. Bypass case + both legit forms tested. |
| `grep -A3 'agentive-workflow'` also matches `agentive-workflow-beta` siblings | o3 | Tightened to `agentive-workflow([@ (]|$)` — row-format drift still tolerated, suffixed siblings excluded. Tested. |

### Declined with evidence

| Finding | Source | Why declined |
|---------|--------|--------------|
| sed range "stops at the start line — prints only the header" | o3 | Empirically false: POSIX sed searches the end address from the line AFTER the start match. Tested on BSD sed with the pin 9 lines below the header — found. |
| sed range "prints nothing when Provenance is the last section" | fast-v2 (r1+r2) | Empirically false: when the end address never matches, the range runs to EOF. Tested on BSD sed — pin at EOF found. |
| `Source:` capitalization / spacing variance | fast-v2 r2 | Already handled: the grep uses `-Ei` (case-insensitive) and `^[[:space:]]*` / `: *` tolerances; verified against live output. |
| Prefixed sibling (`my-agentive-workflow`) still matches | fast-v2 r2 | Diminishing returns: `-A3` output shows all matching rows, so a prefixed sibling is visible next to the real row, not silently substituted. Left-anchoring would require matching the `❯` bullet glyph — exactly the volatile-format coupling this PR removes. |
| Bare command names without a slash evade the flat-ref grep | fast-v2 | Out of scope: the check targets slash-references; a bare name in prose is not a command reference. |
| `grep -oE '[0-9]+\.[0-9]+\.[0-9]+'` could multi-match | fast-v2 | Pre-existing Phase 1 text, unchanged by this PR; input is a single pin line. |
| Metacharacters in substituted artifact names | fast-v2 r2 | Pre-existing hard rule already covers it: single-quote every substituted value, halt on embedded quotes/metacharacters. |
| ANSI strip documented but not integrated into every pipeline | o3 | Deliberate: current CLI verified to strip colours when piped (2026-07-06); the gotcha records the contingency recipe without adding a noise stage to every command for a hypothetical. |

## Raw evaluator logs (PR 2)

## Source: KIT-0035-code-review-input--code-reviewer-fast-v2.md (PR 2 run)

#  Code Reviewer Fast V2

**Source**: .adversarial/inputs/KIT-0035-code-review-input.md
**Evaluator**: code-reviewer-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-07-06 06:13 UTC

---

### Findings

**[CORRECTNESS]: False Negative in Marketplace Source Guard due to Grep Anchoring**
- **Location**: `.claude/agents/upgrader.md:Phase 0a` / `docs/PLUGIN-UPGRADE-GUIDE.md:Prerequisites`
- **Edge case**: `claude plugin marketplace list` output with leading indentation or slightly different spacing before the `source:` key.
- **What happens**: The regex `^[[:space:]]*source: *...` is used. However, the command `claude plugin marketplace list` typically outputs a list where "Source" might be a nested field or part of a YAML-like block. If the CLI output uses "Source:" (capitalized) or contains multiple spaces before the colon, this grep will fail and trigger a **HALT** even if the source is correct.
- **Tested?**: No.

**[CORRECTNESS]: RegEx for row-format drift too broad (Potential Collision)**
- **Location**: `.claude/agents/upgrader.md:Phase 0b`
- **Edge case**: A plugin named `my-agentive-workflow` or `test-agentive-workflow` is installed.
- **What happens**: The grep `grep -A3 -E 'agentive-workflow([@ (]|$)'` looks for the string anywhere in the line. If a user has a custom plugin with a prefix that contains the target string, this grep will return multiple matches or the wrong match, leading the agent to potentially verify the status of the wrong plugin.
- **Tested?**: No.

**[ROBUSTNESS]: Sed Range Failure on Missing Closing Header**
- **Location**: `.claude/agents/upgrader.md:Phase 1` / `docs/PLUGIN-UPGRADE-GUIDE.md:Step 1`
- **Edge case**: `CLAUDE.md` has a `## Provenance` header at the very end of the file with no following `## ` header.
- **What happens**: `sed -n '/^## Provenance/,/^## /p'` will fail to match the range correctly or may swallow the rest of the file if the closing pattern `^## ` is never found. In some `sed` implementations, if the end-pattern is not found, it does not print anything for that range.
- **Tested?**: No.

**[INTERACTION]: Unprotected Variable Substitution in Reconcile Logic**
- **Location**: `.claude/agents/upgrader.md:Phase 2a`
- **Edge case**: Artifact names containing characters like `&`, `[`, or `*`.
- **What happens**: The agent is instructed to `grep -rn 'agentive-workflow:<old-name>'`. While the instructions mention single-quoting, the manual execution of these generated commands by the LLM often leads to shell interpretation issues if the "reasoned" artifact name from the CHANGELOG contains glob characters or regex metacharacters, leading to incorrect grep results.
- **Tested?**: No.

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| Missing trailing header in CLAUDE.md | `sed` Provenance extraction | No | Low - Extraction fails, agent relies on CLI. |
| Case sensitivity in "Source" field | Phase 0a Marketplace Guard | No | Medium - False HALT preventing upgrades. |
| Overlapping plugin names | Phase 0b/1 Plugin List Grep | No | Medium - Agent might target wrong plugin metadata. |
| ANSI codes in non-interactive shell | CLI Greps | No | Low - Documented as a "Gotcha" but not handled in commands. |

### Verdict

**CONCERNS**

The hardening of the `grep` and `sed` patterns improves upon the previous version, but introduces new rigidities. Specifically, the `sed` range for Provenance assumes a following `## ` header which isn't guaranteed if Provenance is the last section. The marketplace guard is also fragile regarding the exact string "source:" (case sensitivity and prefixing).

**Recommendation**: Change `sed` to a simpler `grep -A` or use a more robust range like `/^## Provenance/,/^(#| \w)/`. Ensure marketplace grep is case-insensitive for the key (e.g., `grep -Ei 'source:'`).
## Source: KIT-0035-code-review-input--code-reviewer.md (PR 2 run)

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0035-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-06 00:31 UTC

---

### Summary
Reviewed the two Markdown “code-as-runbook” files that implement the upgrader agent’s shell recipe.
Although no executable Python/JS was changed, the new grep/sed one-liners are themselves code and can mis-classify project state.
I found 4 correctness/robustness issues (2 serious), plus three un-tested edge cases.

### Findings

**CORRECTNESS: GitHub-source guard can be bypassed by local “Directory” paths**
- Location: `.claude/agents/upgrader.md` 0a and `docs/…GUIDE.md` Prerequisites
- Edge case: `claude plugin marketplace list` prints
  `agentive-skills   Directory (/Users/alice/github/movito/agentive-skills)`
- What happens: The new test
  `grep -Ei 'github.*movito/agentive-skills'`
  matches the substring “github”, so the upgrader treats the directory source as “GitHub-form” and proceeds.
- Expected: Halt with the “Directory source” refusal because pins will be ignored.
- Test coverage: NOT covered (no mocked CLI output containing a path with the word github).
- Severity: Bug – causes a wrong PASS at Phase 0 and the upgrade continues on an un-pinned, mutable plugin tree.

---

**CORRECTNESS: sed range prints only the header, hides the pin**
- Location: both files, Phase 1 “Current pin” command
  `sed -n '/^## Provenance/,/^## /p' CLAUDE.md`
- Edge case: The very next line after the header contains the version, then another header later.
- What happens: Because the range end pattern `^## ` also matches the first line, sed stops immediately; only “## Provenance” is echoed.
  Subsequent `grep agentive-workflow` therefore fails → the script concludes “may be absent”.
- Expected: The command should exclude the first line in the end-match (e.g. `/^## Provenance/,$p | sed '1d'`) or use a negated look-ahead.
- Test coverage: NOT covered.
- Severity: Latent – the run still succeeds (it falls back to `plugin list`), but the Provenance check and later restamp diff are wrong, confusing operators.

---

**ROBUSTNESS: broadened plugin-list grep can yield duplicate or false rows**
- Location: everywhere the pattern changed to `grep -A3 'agentive-workflow'`
- Edge case: A disabled copy called `agentive-workflow-beta`, or the string appears in the CLI column “Description”.
- What happens: Multiple rows are returned; the follow-up status test (`must show: enabled`) may read the wrong row and mis-detect enablement.
- Expected: Anchor on the exact column (`^agentive-workflow[[:space:]]`) or additionally filter for the marketplace suffix.
- Test coverage: NOT covered.
- Severity: Latent – only trips when other similarly-named plugins are present.

---

**TESTING: colour-escape workaround only documented, never exercised**
- Location: Gotchas section – suggested `sed $'s/\x1b\\[[0-9;]*m//g'`
- Edge case: Future CLI introduces coloured output but the upgrader still pipes raw data (Phase 0, Phase 1, etc.).
- What happens: None of the greps include the strip stage; once colours arrive every check fails silently → false HALT or worse, a false PASS if the colour codes contain the pattern.
- Expected: Either integrate the strip into every pipeline or test for it now.
- Test coverage: NOT covered.
- Severity: Gap – will break the upgrader the moment the CLI adds colours.

### Edge Cases Verified Clean
• Empty `## Provenance` section handled (falls back to `plugin list`).
• Multiple CLI versions: grep now catches both “@agentive-skills” and “(agentive-skills)”.
• `grep -rinoE` correctly ignores case-drifted flat references.

### Test Gap Summary

| Edge Case | Function/Step | Tested? | Risk |
|-----------|---------------|---------|------|
| “Directory (…) github …” path | Phase 0a guard | No | High |
| sed range excluding body | Phase 1 pin read | No | Medium |
| Multiple plugin rows | Phase 0b guard / Version confirm | No | Medium |
| ANSI colour codes | All greps | No | Medium |

### Verdict
**FAIL** – The new GitHub-source grep lets a common local-directory path slip through, defeating the central version-pin guarantee. Fix that pattern (e.g. `grep -Ei '^\s*GitHub[[:space:]].*movito/agentive-skills'`) before merge. Also address the sed header bug to keep Provenance accurate.
