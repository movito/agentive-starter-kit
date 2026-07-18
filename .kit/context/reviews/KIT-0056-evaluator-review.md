# KIT-0056 Evaluator Review Record

Mode: full trio (all three provider keys present) — code-reviewer-fast
(gemini-2.5-flash), code-reviewer (o3), claude-code (claude sonnet).
Run BEFORE PR open (KIT-0035 F3 / KIT-0046 ordering rule). Five rounds
of code-reviewer-fast; one round each of the deep pair against the
post-round-3 code. `git status` verified clean after every run.

## Round history and dispositions

### code-reviewer-fast round 1 — FAIL (all addressed)
- One tolerance rule for every bots reader (comma/case divergence
  between door bash, project Python, preflight shell) → FIXED, tests.
- Doctor comparison silently last-wins on duplicate preset keys →
  FIXED (INFO + comparison skipped, matching the door's loud rule).
- Unreadable preset / env-source diagnose themselves → FIXED, tests.
- Doctor comparison should WARN on unknown preset keys → DECLINED:
  the door owns the preset-key vocabulary (unknown keys WARN there);
  duplicating the key list in the comparator is a second source of
  truth that drifts. Documented in _print_preset_comparison.

### round 2 — FAIL (addressed/declined)
- Present-but-empty `bots:` line: doctor FAILed it, preflight read it
  as absent → FIXED (preflight NOTICEs and fails closed), tests both
  sides.
- SKIP+PENDING verdict priority untested → test added.
- env-source 0600 warn-not-fail → BY DESIGN (F6: "chmod 600
  expected"; the target copy is always 0600) — warning now pinned by
  a test.
- cmd_sync unsafe-path check untested → OUT OF DIFF (KIT-0049 code,
  covered by its own suite).
- load_record tolerates kit_markers failure → DECLINED: the door's
  record preload is advisory; the ENGINE is the loud enforcement
  point (its Step 2.5 `kit_markers regions/extract` guards exit 1 on
  any reader failure before writing).

### round 3 — CONCERNS (test gaps, all closed)
- gitignore-refusal path, empty normalize_bots input, invalid preset
  bots value in comparison, unreadable preset file in comparison →
  four tests added.

### round 4 — CONCERNS (all refuted or previously dispositioned)
- "Empty bots: passes _doctor_install as both-expected" → REFUTED:
  _normalize_bots("") returns None → bots-record FAIL; pinned by
  test_empty_bots_line_fails_loud.
- "Preset target-github unvalidated" → REFUTED: the preset fill runs
  BEFORE the owner/repo regex check, so preset values are validated.
- Preflight NOTICE-not-FAIL on invalid declaration → BY DESIGN:
  preflight fails closed (gates run and FAIL if bots absent); doctor
  is the loud record-validity surface.
- Typo-distance detection for unknown keys → DECLINED (v1 flat-format
  boundary, documented).

### code-reviewer (o3) — FAIL (1 real, fixed; rest refuted/declined)
- Leading-whitespace divergence (Python strip() vs shell ^-anchors;
  the engine would append a SECOND bots line) → REAL, FIXED: all
  shell readers whitespace-tolerant (record_field helper, engine sed,
  preflight grep/sed); pinned by three tests (doctor, preflight, door
  no-duplicate e2e).
- Duplicate record keys first-wins → DECLINED: pre-existing KIT-0048
  shape/profile behavior, and CONSISTENT across readers (all take
  first match) once whitespace tolerance landed. Record-strictness is
  a possible follow-up, not this diff.
- Duplicate UNKNOWN preset key not an error → REFUTED by spec F5:
  unknown keys are never an error (forward compatibility); each
  occurrence warns loudly.
- apply_env_source truncates existing .env → REFUTED: --new refuses
  existing targets; the path is unreachable with a pre-existing .env.
- normalize_bots keeps duplicate names → REFUTED by reading both
  implementations (bash flags / Python membership dedupe); pinned by
  new canonical-form params + doctor test.

### claude-code (security) — no verdict line; findings dispositioned
- preset_get sed injection surface → FIXED: pure parameter expansion,
  no sed.
- .env creation permissions window → FIXED: born 0600 under umask 077.
- Engine's baked planning manifest still 3.3.0 → REAL MISS, FIXED to
  3.4.0 (the KIT-0050 bump precedent).
- Misplaced test class → FIXED (moved to TestPresetUnits).
- run_doctor_tail verdict-swap comment → VERIFIED empirically (demo
  run: 4 FAILs → exit 1 → was labeled WARNINGS pre-fix).
- Preset file size limit → DECLINED (evaluator itself: acceptable
  operational constraint for an operator-owned file).
- Positives noted: secrets handling, preflight injection defenses, no
  hardcoded credentials.

### code-reviewer-fast round 5 (final) — CONCERNS
Three fault-injection test suggestions on paths whose logic the
evaluator calls correct (empty region = absent by design; engine
extract guarded and loud; --new commit-failure path is pre-existing
KIT-0053 code with explicit handling) → DECLINED, diminishing returns.

## Known blind spot
Evaluators reliably miss CSS/dual-render-path issues — not applicable
to this shell/Python diff.

---

## Source: KIT-0056-code-review-input--claude-code.md

#  Claude Code

**Source**: .adversarial/inputs/KIT-0056-code-review-input.md
**Evaluator**: claude-code
**Model**: anthropic/claude-sonnet-4-6
**Generated**: 2026-07-18 08:47 UTC

---

## Phase 1: Understand Intent

This PR implements KIT-0056 "Degraded modes + operator presets" for an agentive starter kit. The two main features are:

1. **P5 (Degraded modes)**: A `bots:` declaration in `CLAUDE.md` lets projects declare absent bots, causing preflight Gates 2/3 to SKIP rather than FAIL.
2. **P7 (Operator presets)**: A `~/.config/agentive-kit/preset` file pre-answers setup questions, enabling "one-button" project creation. Includes `env-source` to copy a `.env` template with secrets.

Critical paths: preset loading, bots declaration parsing, `env-source` secret handling, preflight gate evaluation, and doctor `--against-preset`.

---

## Phase 2: Security Analysis

### MEDIUM: `preset_get()` uses unanchored sed pattern — key name injection

**Location**: `scripts/local/bootstrap`, `preset_get()` function
```bash
hit="$(printf '%s' "$PRESET_DATA" | sed -n "s/^$1=//p" | head -1)"
```
**Issue**: `$1` (the key name) is interpolated unquoted into a sed expression. A key name containing sed metacharacters (e.g., `.*`, `/`, `&`) could alter the sed program. In practice, all callers pass literal strings like `"shape"`, `"profile"`, `"bots"`, but the function is exposed in sourced tests where arbitrary strings could be passed. The sed delimiter `/` in the key name would break the command. For the shipped code paths this is low-risk, but it's a latent injection in the function contract.

**Remediation**: Use a fixed-string grep approach or escape the key:
```bash
hit="$(printf '%s' "$PRESET_DATA" | grep "^$1=" | head -1 | cut -d= -f2-)"
```
Or restrict to known keys before calling `preset_get`.

---

### LOW: `apply_env_source` race condition on file creation

**Location**: `scripts/local/bootstrap`, `apply_env_source()`
```bash
: > "$TARGET/.env"
chmod 600 "$TARGET/.env"
cat "$src" >> "$TARGET/.env"
```
**Issue**: There is a TOCTOU window between creating the empty file (world-readable until `chmod` runs) and applying permissions. Under `set -e`, if `chmod` fails the file remains at default umask permissions (typically 0644). The comment says "create-then-fill so the file never exists with looser permissions" but the empty file does briefly exist at default permissions.

**Remediation**: Use `install` which sets permissions atomically:
```bash
install -m 600 "$src" "$TARGET/.env"
```
Or use `umask 0177` in a subshell:
```bash
(umask 0177; cat "$src" > "$TARGET/.env")
```

---

### LOW: `preset_get` sed pattern could match substring keys

**Location**: `scripts/local/bootstrap`, `preset_get()`
```bash
hit="$(printf '%s' "$PRESET_DATA" | sed -n "s/^$1=//p" | head -1)"
```
**Issue**: The PRESET_DATA format uses `key=value\n` lines (set in `load_preset` as `data="$data$key=$value"$'\n'`). A lookup for key `"sh"` would match a line starting `"shape="` because the pattern `^sh=` would not match `shape=`—actually this is fine due to the `=` delimiter. However, the sed pattern lacks word anchoring and the key value in PRESET_DATA could theoretically be multi-line if a value contained a newline. In practice `sed` strips these at the whitespace trim step, so risk is low.

---

### POSITIVE: Secrets handling
- `apply_env_source` correctly checks `.env` is gitignored before copying
- Contents are never printed or logged
- Pre-validates `env-source` exists and is readable before any install work begins
- Mode 0600 on the target copy

### POSITIVE: Injection defenses in preflight
- `REPO` validated with regex before being interpolated into GraphQL
- `PR_NUMBER` validated as numeric before use in GraphQL
- Bot declaration validated against a known vocabulary before skipping gates
- Fail-closed: invalid/unknown declarations fall back to expecting both bots

### POSITIVE: No hardcoded credentials anywhere in the diff

---

## Phase 3: Correctness Analysis

### MEDIUM: `run_doctor_tail` exit code swap was present before this PR — the fix is correct but the comment needs verification

**Location**: `scripts/local/bootstrap`, `run_doctor_tail()`
```bash
# doctor's exit contract (KIT-0046 F3): 1 = at least one FAIL,
# 2 = warnings only. (The two were swapped here until KIT-0056 —
# a FAILing doctor reported as "WARNINGS".)
case "$doctor_exit" in
    0) verdict="all checks passed" ;;
    1) verdict="FAILURES (see above) — install still succeeded; fix before working" ;;
    2) verdict="WARNINGS (see above) — install still succeeded" ;;
```
**Issue**: The comment is correct—this was a pre-existing bug now fixed. The diff confirms 1 and 2 were previously swapped. This is a correctness fix, not a new issue.

---

### LOW: `normalize_bots` in bootstrap doesn't guard against empty string token from space-only input

**Location**: `scripts/local/bootstrap`, `normalize_bots()`
```bash
raw="$(printf '%s' "$1" | tr ',' ' ' | tr '[:upper:]' '[:lower:]')"
for tok in $raw; do
```
**Issue**: The `for tok in $raw` loop with unquoted `$raw` will produce zero iterations for empty/whitespace-only input, falling through to `return 1`. This is actually the correct behavior per the spec ("empty → unanswered"), and the test `test_empty_input_is_unanswered_not_error` verifies this. No bug, just confirming the behavior is tested.

---

### LOW: `_print_preset_comparison` passes `record_errors` as positional arg but the function signature uses it

**Location**: `scripts/core/project`, `_print_preset_comparison()`
```python
def _print_preset_comparison(shape, profile, bots, record_errors):
```
Called as:
```python
_print_preset_comparison(shape, profile, bots, record_errors)
```
**Issue**: No issue—the call matches the signature. Confirmed correct.

---

### LOW: `bot_declared_absent()` case statement pattern assumes BOTS_DECLARED contains no leading/trailing spaces after rebuild

**Location**: `scripts/core/preflight-check.sh`
```bash
BOTS_DECLARED="${_BOTS_TOKENS% }"
...
case " $BOTS_DECLARED " in
    *" $1 "*) return 1 ;;
esac
```
**Issue**: The trailing-space strip `${_BOTS_TOKENS% }` is correct. The `case " $BOTS_DECLARED "` pattern with surrounding spaces correctly handles single-token and multi-token values. Logic is sound.

---

### LOW: Planning-shape manifest in `engine-consumer.sh` still references `core_version: 3.3.0` while the kit bumped to `3.4.0`

**Location**: `scripts/local/engine-consumer.sh`, the heredoc MANIFEST for planning shape:
```json
{
  "core_version": "3.3.0",
  ...
  "synced_at": "2026-07-14T00:00:00Z",
```
**Issue**: The kit's own manifest was bumped to `3.4.0` in `scripts/.core-manifest.json`, but the planning-shape manifest baked into `engine-consumer.sh` still says `3.3.0`. A freshly bootstrapped planning repo would show version skew against the kit. This was likely pre-existing (note `synced_at: 2026-07-14`) and not introduced by this PR, but it's a correctness gap.

**Remediation**: Update the baked manifest version to `3.4.0` and `synced_at` to match.

---

### LOW: `apply_env_source` in bootstrap is `--new` only, but `ENV_SOURCE` is only set when `MODE = "new"` — yet `apply_env_source` is called unconditionally if `ENV_SOURCE` is set

**Location**: `scripts/local/bootstrap`, preset validation block:
```bash
if [ "$MODE" = "new" ] && offer="$(preset_get env-source)"; then
    ENV_SOURCE="${offer/#\~/$HOME}"
    ...
fi
```
And later:
```bash
if [ -n "$ENV_SOURCE" ]; then
    apply_env_source "$ENV_SOURCE"
fi
```
**Issue**: The guard is correct—`ENV_SOURCE` can only be set when `MODE = "new"`. The call is safe. No bug.

---

### LOW: `TestNormalizeBots.test_env_not_gitignored_refuses_secret_copy` is misclassified under `TestNormalizeBots`

**Location**: `tests/test_setup_door.py`
**Issue**: A test about `apply_env_source` behavior is placed inside `TestNormalizeBots`. This is a test organization issue only—the test itself is correct. It will still run and pass.

---

### MEDIUM: `load_preset` in bootstrap reads entire file into `PRESET_DATA` variable with no size limit

**Location**: `scripts/local/bootstrap`, `load_preset()`
```bash
data="$data$key=$value"$'\n'
...
PRESET_DATA="$data"
```
**Issue**: No file size check exists. A multi-MB preset file would read entirely into a shell variable. This is a developer-operated file at a known path, making this an acceptable operational constraint rather than a security issue. Low practical risk.

---

## Phase 4: Code Quality

### POSITIVE: Architecture
- Single resolver pattern is well-enforced; the preset is one layer of `resolve_setting`, not a parallel path
- Fail-closed everywhere for declaration parsing
- Consistent normalization across all three bots readers (door, project script, preflight)
- `intersection_names_drops` pattern correctly applied: every degraded surface names its mode

### POSITIVE: Test coverage
- Comprehensive parametric coverage of `normalize_bots`
- N1 (no-migration) explicitly tested
- Hermetic XDG isolation in all preset tests
- `TestPresetNeverDistributed` structural test catches accidental preset path references

### LOW: `_demo_preset_xdg` in test file creates `(xdg / "agentive-kit").mkdir()` without `parents=True`

**Location**: `tests/test_setup_door.py`
```python
xdg = _git_identity(tmp_path)  # xdg-config/ with git/config
...
(xdg / "agentive-kit").mkdir()
```
**Issue**: `_git_identity` returns `tmp_path / "xdg-config"` and creates `xdg/git/`. The call `.mkdir()` on `xdg / "agentive-kit"` assumes `xdg` already exists, which it does since `_git_identity` creates `xdg/git/config`. However, if `_git_identity`'s internals change, this could break silently. Should use `parents=True, exist_ok=True` defensively.

---

### LOW: `BASH` variable used in `TestCoreBareCheck.test_git_config_env_override_cannot_fake_bare` is resolved at module import time

**Location**: `tests/test_doctor.py`
```python
BASH = shutil.which("bash")  # absolute — restricted-PATH runs still need it
```
Used in `TestCoreBareCheck` but defined outside those classes at module level. If bash is not found (already guarded by the module-level `pytest.skip`), `BASH` would be `None`, causing a confusing error. The existing `pytest.skip` guard covers this, so it's a minor style concern.

---

## Findings Summary

### [MEDIUM]: Unescaped key interpolation in `preset_get` sed expression
- **Location**: `scripts/local/bootstrap`, `preset_get()`
- **Issue**: `sed -n "s/^$1=//p"` interpolates the key name unquoted into a sed expression. Keys containing sed metacharacters would alter the regex.
- **Remediation**: Use `grep "^$1=" | cut -d= -f2-` or escape the key before sed interpolation.

### [MEDIUM]: TOCTOU race on `.env` file creation in `apply_env_source`
- **Location**: `scripts/local/bootstrap`, `apply_env_source()`
- **Issue**: Empty file created at default umask permissions, then `chmod 600` applied. Brief window where file exists at looser permissions.
- **Remediation**: Use `install -m 600 "$src" "$TARGET/.env"` or `(umask 0177; cat "$src" > "$TARGET/.env")`.

### [LOW]: Planning-shape manifest baked into `engine-consumer.sh` not bumped to `3.4.0`
- **Location**: `scripts/local/engine-consumer.sh`, planning MANIFEST heredoc
- **Issue**: `core_version: 3.3.0` while kit is at `3.4.0`, causing immediate version skew for new planning-shape installs.
- **Remediation**: Update baked manifest to `core_version: 3.4.0`.

### [LOW]: Test `test_env_not_gitignored_refuses_secret_copy` placed in wrong test class
- **Location**: `tests/test_setup_door.py`, `TestNormalizeBots`
- **Issue**: Test about `apply_env_source` is in `TestNormalizeBots`. Not a defect, just misleading organization.
- **Remediation**: Move to `TestPresetE2E` or a new `TestApplyEnvSource` class.

---

### Positive Observations
- **Fail-closed discipline throughout**: invalid declarations, malformed presets, and unreadable files all fail closed to the safe behavior
- **Single resolver pattern**: the preset is strictly one layer of `resolve_setting`, never a parallel path
- **Consistent bots normalization**: all three readers (door, project script, preflight) share identical tolerance rules—cross-reader validation is well-tested
- **Secrets never surface**: `env-source` contents are never echoed, logged, or staged; `.gitignore` check is a hard prerequisite
- **Hermetic test isolation**: `_HERMETIC_XDG` prevents real `~/.config` from leaking into test runs
- **Structural test for non-distribution**: `TestPresetNeverDistributed` mechanically enforces the F7 requirement
- **Thorough exit code contract**: all three exit codes documented, tested, and the pre-existing swap bug is correctly fixed

---

## Context Required / Unverifiable
- Whether `kit_markers.py` `replace --stdin` correctly handles the `printf '%s\nbots: %s'` (no trailing newline) input as described in the engine comment—cannot verify without running the actual kit_markers implementation
- Whether the `git check-ignore -q .env` check in `apply_env_source` works correctly for all gitignore configurations (e.g., global gitignore, nested `.gitignore` files)
- Runtime behavior of the `stat -f '%Lp'` (macOS) vs `stat -c '%a'` (Linux) fallback chain

---

## Overall Assessment

**CHANGES_REQUESTED**

The implementation is architecturally sound with strong security discipline throughout. The two MEDIUM findings are the `preset_get` sed injection (low practical risk given controlled callers, but a latent hazard) and the `apply_env_source` TOCTOU race (brief window of looser file permissions). The planning-shape manifest version inconsistency (LOW) should be fixed to avoid confusing new users.

The core security invariants—secrets never printed, fail-closed bots handling, no distribution of the preset—are correctly implemented and well-tested. The degraded mode naming and single-resolver constraints are faithfully implemented. The test coverage is thorough and the hermetic XDG isolation properly protects against test environment pollution.
## Source: KIT-0056-code-review-input--code-reviewer-fast.md

#  Code Reviewer Fast

**Source**: .adversarial/inputs/KIT-0056-code-review-input.md
**Evaluator**: code-reviewer-fast
**Model**: gemini/gemini-2.5-flash
**Generated**: 2026-07-18 08:55 UTC

---

### Findings

**[ROBUSTNESS]: Empty `kit-install` region in CLAUDE.md for bots**
- **Location**: `scripts/core/preflight-check.sh`
- **Edge case**: `CLAUDE.md` exists and `kit_markers.py` is available, but the `kit-install` region itself is entirely missing.
- **What happens**: The `python3 scripts/local/kit_markers.py extract CLAUDE.md kit-install` command will exit with an error (e.g., "region not found"). The `|| true` suppresses the error, `KIT_INSTALL_REGION` remains empty. Consequently, `BOTS_LINE_PRESENT` remains `false`, and `BOTS_DECLARED` remains empty. The `bot_declared_absent()` function will return 1 for both bots, meaning they are expected to run. This behavior is correct per the spec ("Absent line, absent region, or unreadable record = both bots expected").
- **Tested?**: No (Explicitly). The `TestGate23BotsDeclaration` fixture `_install_declaration` *always* creates the `kit-install` region. While implicitly correct behavior, an explicit test that ensures a missing region is handled as if no bots line is present would provide stronger coverage.

**[ROBUSTNESS]: `kit_markers.py` failure during `engine-consumer.sh` bot line insertion**
- **Location**: `scripts/local/engine-consumer.sh`: Bot Declaration Writing logic block (around line 720)
- **Edge case**: `kit_markers.py` (used for `extract` and `replace`) fails unexpectedly when trying to read/update the `kit-install` region for bot declaration (e.g., due to a Python interpreter error, corrupted `kit_markers.py`, or unexpected `CLAUDE.md` format that `kit_markers.py` can't parse).
- **What happens**: The `if ! REGION_NOW="$(python3 "$KIT_MARKERS" extract ...)"` check will catch the failure, print an "Error: kit_markers extract kit-install failed" message, and `exit 1`. This will cause the entire `bootstrap` process to fail, preventing potentially corrupted `CLAUDE.md` files or incorrect bot declarations. This is a robust fail-fast behavior.
- **Tested?**: No (Explicitly). While the code correctly handles this with an `exit 1`, there isn't a dedicated test case that explicitly simulates `kit_markers.py` failing during this step (e.g., by making `kit_markers.py` temporarily corrupt or unexecutable).

**[ROBUSTNESS]: `git commit` failure in `bootstrap` for new single-shape project**
- **Location**: `scripts/local/bootstrap`: `main()` function, `MODE="new" && SHAPE="single"` branch (around line 790)
- **Edge case**: After the `engine-consumer.sh` successfully writes the `CLAUDE.md` record, the subsequent `git -C "$TARGET" add ... && git -C "$TARGET" commit ...` command fails (e.g., due to a full disk, a `git` binary issue, or a `pre-commit` hook that was not properly set up for a new project and prevents the commit).
- **What happens**: The `if git -C ... commit ...; then` block will fall to the `else` branch, printing an "Error: install record commit failed" and `exit 1`. The `CLAUDE.md` file in the target directory will contain the correct `kit-install` record, but it will be uncommitted. The `bootstrap` script correctly reports an installation failure. This is robust.
- **Tested?**: No (Explicitly). The existing tests for `test_new_single_exports_and_records` ensure the commit is successful. A test simulating a `git commit` failure at this stage would verify the robustness of the `exit 1` path and the state of the target repo.

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|---|---|---|---|
| Missing `kit-install` region in CLAUDE.md | `scripts/core/preflight-check.sh` | No | Medium - Logic is implicitly correct but not explicitly tested. |
| `kit_markers.py` fails during bot line insertion | `scripts/local/engine-consumer.sh` | No | Medium - Code has a fail-fast mechanism, but it's not verified by test. |
| `git commit` fails after record write for `--new` | `scripts/local/bootstrap` | No | Medium - Code handles failure, but test ensures success, not failure path. |

### Verdict

**CONCERNS**: Untested edge cases or robustness gaps. While the logic appears correct and designed for robustness in these cases, explicit test coverage for these failure/edge conditions would provide stronger guarantees. The current tests are extensive for success paths and specific failure modes, but these three gaps were identified.
## Source: KIT-0056-code-review-input--code-reviewer.md

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0056-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-18 08:47 UTC

---

### Summary
Reviewed the new KIT-0056 “degraded modes + presets” surface: bootstrap door, consumer
engine, doctor, project-sync helper and pre-flight script.  Implementation is mostly
sound, but several subtle edge cases let the three readers (door ↔ doctor ↔ pre-flight)
disagree, or allow malformed input to slip through silently.  Found 6 issues
(3 correctness bugs, 2 robustness gaps, 1 test gap).

### Findings

**[CORRECTNESS]: Leading-whitespace makes bots / shape / profile invisible**
- **Location**: `preflight-check.sh` (≈ 212 – 250), `bootstrap` (≈ 2220), `project:_doctor_install`
- **Edge case**: `kit-install` region lines indented, e.g. `"   bots: none"`.
- **What happens**:
  * doctor strips the line (`line.strip().startswith("bots:")`) → reads it;
  * bootstrap’s sed (`sed -n 's/^bots:[[:space:]]*//p'`) and pre-flight’s
    grep / sed (`grep '^bots:'`) ignore the indented line → think the
    declaration is absent and add a second `bots:` or run the gates.
- **Expected**: All three readers recognise the same record regardless of harmless
  indentation.
- **Test coverage**: NOT covered (no test uses indented lines).
- **Severity**: Bug.

---

**[CORRECTNESS]: Duplicate `shape:` / `profile:` / `bots:` lines silently accepted**
- **Location**: `project:_doctor_install` (≈ 1323 ff)
- **Edge case**: Record contains two `shape:` lines with different values.
- **What happens**: First value wins, second ignored; no `DOCTOR:*-record:FAIL`
  produced, so consumers quietly diverge.
- **Expected**: Duplicate keys are invalid → one `FAIL` covering the poisoned record.
- **Test coverage**: NOT covered.
- **Severity**: Latent (becomes visible when duplicates appear).

---

**[CORRECTNESS]: Duplicate *unknown* preset key not treated as error**
- **Location**: `bootstrap:load_preset` (≈ 130 ff)
- **Edge case**:
  ```
  coffee: espresso
  coffee: latte
  ```
- **What happens**:  First line warns, second line *also* warns; duplicate
  detection is skipped because the unknown key is never added to `seen`.
- **Expected**: “duplicate preset key” error for *any* key, known or not.
- **Test coverage**: Gap (tests cover duplicate *known* key only).
- **Severity**: Robustness gap.

---

**[ROBUSTNESS]: `apply_env_source` overwrites existing secrets silently**
- **Location**: `bootstrap:apply_env_source` (≈ 420 ff)
- **Edge case**: Target already has a populated `.env`.
- **What happens**: `: > .env` truncates the file before copy; original secrets
  are lost with no prompt or backup.
- **Expected**: Abort, or require `--force`, or append without truncation.
- **Test coverage**: NOT covered.
- **Severity**: Latent (data-loss for repeat `--new` on same dir).

---

**[ROBUSTNESS]: `normalize_bots` lets repeated names through**
- **Location**: `bootstrap:normalize_bots`, `project:_normalize_bots`
- **Edge case**: `coderabbit coderabbit`
- **What happens**: Function returns `"coderabbit coderabbit"` (duplicates kept).
  The canonical form is no longer canonical; string equality checks in doctor /
  pre-flight may mis-compare.
- **Expected**: Duplicates collapsed to single occurrence.
- **Test coverage**: NOT covered.
- **Severity**: Gap.

---

**[TESTING]: Unknown-key duplicate not exercised**
- **Location**: tests – `tests/test_setup_door.py`
- **Edge case**: see duplicate-unknown finding above.
- **What happens**: No test; bug would ship unnoticed.
- **Expected**: A failing test asserting that duplicate unknown keys abort with exit 2.
- **Severity**: Gap.

### Edge Cases Verified Clean
• Mixed-case/comma bots declarations.
• PATH-leaked venv pip masking (version-skew check).
• `.env` template permission warning vs refusal when unreadable.
• Gate-1 cap-limit vs failure precedence logic.

### Test Gap Summary

| Edge Case | Function / Script | Tested? | Risk |
|-----------|------------------|---------|------|
| Indented `bots:` / `shape:` lines | bootstrap / pre-flight | No | High – duplicate lines & skipped gates |
| Duplicate record keys | _doctor_install | No | Medium |
| Duplicate unknown preset keys | load_preset | No | Medium |
| Duplicate bots names | normalize_bots | No | Low |
| `.env` already exists | apply_env_source | No | Medium |

### Verdict

**FAIL** – at least one correctness bug that can break real workflows:
leading-space on `bots:` causes pre-flight to run the wrong gates or
bootstrap to write a second declaration.  Fix findings 1 & 2 before merge.
