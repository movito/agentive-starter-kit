## Source: KIT-0097-code-review-input--claude-code.md

#  Claude Code

**Source**: .adversarial/inputs/KIT-0097-code-review-input.md
**Evaluator**: claude-code
**Model**: anthropic/claude-sonnet-4-6
**Generated**: 2026-08-09 17:10 UTC

---

## Phase 1: Understand Intent

This diff modifies an AI agent orchestration framework ("agentive starter kit") — a collection of Markdown-based agent prompts, slash commands, and skills that instruct LLM agents how to execute software development workflows. The changes:

1. **Reorder the evaluator phase** to run *before* PR open (was after CI/bot rounds)
2. **Fix cross-repo routing** — introduce `$PLANNING` variable to correctly address planning-repo files in split-mode topologies
3. **Harden CI verification** — fix `check-ci` to not hardcode `main`, add cross-repo awareness
4. **Correct read-only agent constraints** — remove CI/commit instructions from `document-reviewer` and `security-reviewer`
5. **Improve upgrader robustness** — fix `TARGET_REF` resolution and rollback ordering
6. **Add tests** — `test_feature_developer_runs_evaluator_before_pr_open` pins phase ordering
7. **Generalize task IDs** — `ASK-XXXX` → `TASK-ID` placeholders

**Critical paths**: Agent instructions that invoke shell commands (`bash`, `gh`, `git`), path construction using `$PLANNING`, and the gating logic for when evaluators run.

---

## Phase 2: Security Analysis

### [MEDIUM]: Shell Injection Risk via Unquoted `$PLANNING` in Agent Instructions

- **Location**: `feature-developer.md` / `feature-developer-f5.md` — Phase 1 Start section
- **Issue**: The `$PLANNING` variable is set from `git rev-parse --show-toplevel` or from a manually-specified path (e.g., `PLANNING=~/Github/<project>-planning`). It is then interpolated unquoted into commands like `cat "$PLANNING"/.kit/tasks/*/<TASK-ID>-*.md` and `"$PLANNING"/scripts/core/project start <TASK-ID>`. The variable itself is double-quoted in the example commands, which is correct. However, the split-mode assignment is a free-form comment instruction: "Set PLANNING to that absolute path instead" with no validation. An adversarially crafted path (e.g., a directory named with shell metacharacters) could cause unexpected behavior. This is low-severity in practice because the path is operator-supplied and the quotes are present, but the instructions don't warn to validate or sanitize it.
- **Remediation**: Add a note to validate `$PLANNING` resolves to a real directory before use: `[[ -d "$PLANNING" ]] || { echo "PLANNING is not a directory: $PLANNING"; exit 1; }`. This is defensive guidance for the agent.

### [LOW]: `.env` Loaded via `source` in Agent Instructions — Secret Exposure Risk

- **Location**: `feature-developer.md` / `feature-developer-f5.md` — Phase 5/Evaluator Step 2
- **Issue**: The instructions show `set -a; source .env; set +a` to load API keys before running evaluators. Combined with `set -a`, this exports all variables in `.env` to the environment. If `.env` contains unrelated secrets beyond the API keys, they are unnecessarily exported into the subprocess environment. Additionally, the SKILL.md explicitly warns "never add or commit a key" but the `source .env` pattern doesn't warn against `.env` being committed.
- **Remediation**: The SKILL.md already partially addresses this. Consider scoping: only export the specific keys needed (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) rather than sourcing the whole file with `set -a`. Add a guard: `git check-ignore -q .env || echo "WARNING: .env is not gitignored"`.

### [LOW]: `agentive review-input` Invoked Without Input Sanitization on `<TASK-ID>`

- **Location**: Phase 5 Step 1 in both feature-developer files
- **Issue**: `agentive review-input <TASK-ID>` and path constructions like `.adversarial/inputs/<TASK-ID>-code-review-input.md` use `<TASK-ID>` as a shell argument. If `<TASK-ID>` were user-supplied and contained shell metacharacters (e.g., `; rm -rf`), this could be dangerous. In practice, task IDs follow a strict format (`KIT-0097`), and the agent framework controls their generation — this is low risk but worth noting.
- **Remediation**: Document the expected format of `<TASK-ID>` (e.g., `[A-Z]+-[0-9]+`) and add validation before substitution.

### [LOW]: `grep -A 5 "## Target Repository" CLAUDE.md` Output Used for Topology Decision

- **Location**: `ci-checker.md` Pre-flight Check; `check-spec.md` Step 0
- **Issue**: The output of this grep is used to make a binary routing decision (cross-repo vs. single-repo). If `CLAUDE.md` is maliciously modified or contains unexpected content matching `## Target Repository`, the agent could be directed to operate against a wrong repository. This is an internal trust-boundary concern in a developer-controlled environment.
- **Remediation**: Acceptable for this trust model, but document the assumption that `CLAUDE.md` is trusted content.

### [INFORMATIONAL]: `gh workflow run <workflow-file-or-name>` in check-ci.md

- **Location**: `check-ci.md` — manual dispatch section
- **Issue**: The workflow name/filename is taken from `gh workflow list` output, which is correct. The concern is that an agent misreading the output could dispatch an unintended workflow. The documentation does appropriately say "pick the workflow that runs the tests."
- **Remediation**: No action needed; the instructions are sufficiently specific.

---

## Phase 3: Correctness Analysis

### [HIGH]: `$PLANNING` Variable Not Persisted Across Agent Steps — Potential Silent Failure

- **Location**: `feature-developer.md` / `feature-developer-f5.md` — Phase 1 Start
- **Issue**: `$PLANNING` is defined in a bash snippet as a session-local variable. However, agent instructions are executed as separate tool calls — there is no guarantee the variable persists between steps. If `$PLANNING` is unset when a later command like `"$PLANNING"/scripts/core/project move <TASK-ID> in-review` runs, the command silently becomes `/scripts/core/project move ...` (i.e., an absolute path from root), which will either error or, worse, operate on an unintended location. The instructions say "Derive the planning root once and route every planning command through it" but don't address persistence.
- **Remediation**: Add an explicit note that `$PLANNING` must be re-derived at the start of each bash block that uses it, or agents must treat it as a constant to re-set. Consider making it a documented alias/function that agents call rather than a variable. At minimum, add: `echo "PLANNING is set to: $PLANNING" # verify before each use` and warn that it must be redefined in each new shell context.

### [MEDIUM]: `test_feature_developer_runs_evaluator_before_pr_open` — Fragile Regex on Workflow Table

- **Location**: `tests/test_agent_contracts.py` lines ~68-82
- **Issue**: The test asserts the Workflow Overview table's Evaluator row contains "before PR open" via:
  ```python
  re.search(r"^\|\s*\d+\.\s*Evaluator\s*\|.*before PR open", text, re.MULTILINE | re.I)
  ```
  This regex requires the phrase "before PR open" to appear on the *same line* as the Evaluator row. The actual text in the diff reads `**before PR open**` (bold markdown). The `re.I` flag handles case, but `re.MULTILINE` only affects `^`/`$`. The regex would fail if the table cell wraps or if the phrase is in the next cell with a `|` separator. Looking at the actual content: `| 5. Evaluator | Adversarial code review — **before PR open** | code-review evaluator | **GATE** |` — this should match, but it's brittle to reformatting.
- **Remediation**: Use a more robust pattern: `r"Evaluator.*before PR open"` without the strict `^\|` anchor, or normalize whitespace before matching.

### [MEDIUM]: `find()` in test uses `next(..., None)` — Assertion Message Misleads on Wrong Match

- **Location**: `tests/test_agent_contracts.py` — `find()` helper
- **Issue**: `find(prefix)` returns the first heading whose title starts with `prefix`. For `find("CI + Bot")` matching `## Phase 7: CI + Bot Review (GATE)`, this works. However, if a heading like `## Phase 7: CI + Bots (something else)` existed, it would still match. More critically, `find("Evaluator")` would match any heading starting with "Evaluator" — including a future heading like "Evaluator Notes" — giving a false positive on the phase number check.
- **Remediation**: Match more precisely, e.g., require the heading to match a specific pattern: `h[2] == "Evaluator (GATE) — before the PR opens"` or use a set of known exact titles.

### [LOW]: `headings` list comprehension has an indexing error

- **Location**: `tests/test_agent_contracts.py` lines ~55-62
- **Issue**: The comprehension:
  ```python
  headings = [
      (int(num), position, title)
      for position, (num, title) in enumerate(
          re.findall(r"^## Phase (\d+): (.+)$", text, re.MULTILINE)
      )
  ]
  ```
  `re.findall` with two capture groups returns a list of `(num, title)` tuples. `enumerate` adds `position`. The unpacking `for position, (num, title) in enumerate(...)` is correct Python. This is fine. *(No issue — noting it was checked.)*

### [LOW]: Rollback instructions in `upgrader.md` — "retained plugin cache" is undocumented behavior

- **Location**: `upgrader.md` — Rollback section
- **Issue**: The rollback procedure says to "restore `<previous>` from that cache" but does not provide the actual command to do so. The `~7 days` window caveat is noted, but if the cache path or restore command is wrong, the HALT path is correct. The missing concrete command is a correctness gap — an agent following these instructions has no specific shell command to execute for the restore step.
- **Remediation**: Add a placeholder or note: "The cache restore command is vendor-specific — consult `claude plugin --help` or the plugin runtime docs for the pinned-install path syntax."

### [LOW]: `check-spec.md` — `git diff --name-only origin/main...HEAD` requires fetch first

- **Location**: `check-spec.md` Step 2
- **Issue**: The instructions correctly add `git fetch origin main` before the diff. This is an improvement. However, in split-mode where `git -C "$TARGET"` is required, the fetch instruction doesn't explicitly prepend `-C "$TARGET"`. An agent could fetch from the planning repo's origin instead of the target repo's origin.
- **Remediation**: Add `git -C "$TARGET" fetch origin main` explicitly in the split-mode context.

### [LOW]: Phase numbering consistency — `feature-developer-f5.md` vs `feature-developer.md`

- **Location**: Both feature-developer files
- **Issue**: Both files now have identical phase structures (5=Evaluator, 6=Ship, 7=CI+Bots, 8=Preflight, 9=Handoff). The test `test_feature_developer_runs_evaluator_before_pr_open` checks both. This is consistent. However, if the F5 variant diverges in future, the shared test may give false confidence. *(Low concern — documented.)*

---

## Phase 4: Code Quality

### [LOW]: Duplicate content between `feature-developer.md` and `feature-developer-f5.md`

- **Location**: Both feature-developer files — Phase 5 (Evaluator), Phase 6 (Ship), Phase 9 (Handoff)
- **Issue**: The Phase 5 Evaluator section is textually identical (∼130 lines) between the two files. The Phase 6 Ship and Phase 9 Handoff sections are also nearly identical. This duplication means future fixes must be applied to both files, and the current PR already demonstrates the risk (the old Phase 7 Evaluator section existed in both and both needed updating). The test `FEATURE_DEVELOPERS` parameterizes over both, which catches ordering drift but not content drift.
- **Remediation**: Consider extracting shared content to an included skill file (e.g., `SKILL.md`) and referencing it from both agents. If the framework doesn't support includes, add a comment at the top of each duplicated section: `# SYNC: this section mirrors feature-developer[-f5].md — update both.`

### [MEDIUM]: `document-reviewer.md` and `security-reviewer.md` — Removed CI sections may confuse agents that were relying on them

- **Location**: Both reviewer agent files
- **Issue**: The removal of CI/commit instructions from read-only agents is correct in principle. However, the replacement text says "do not commit, push, or attempt to verify CI" without explaining what happens if a document-reviewer is invoked in a context where it previously *did* run CI (i.e., if old orchestration code calls it expecting CI behavior). This is a behavioral contract change.
- **Remediation**: This is an appropriate fix — the agents were incorrectly granted CI responsibilities. The change is well-documented. No code change needed, but operator changelog/migration note recommended.

### [LOW]: `retro.md` — The new "Escalated" state (option 4) adds process complexity

- **Location**: `retro.md` — Incident Closure section
- **Issue**: The fourth state ("Escalated — awaiting planner classification") is well-defined and solves a real gap. The three required fields (a), (b), (c) are clear. This is good process design.
- **Remediation**: No issue — positive change.

---

## Positive Observations

1. **Tests pin behavioral contracts**: `test_feature_developer_runs_evaluator_before_pr_open` is an excellent regression test — it checks both declared phase numbers AND document order, catches both an agent following table order and one following section order, and pins the table wording. The dual-axis check is particularly thoughtful.

2. **`$PLANNING` variable pattern is well-explained**: The single-repo vs. split-mode distinction is clearly documented with examples. The instruction to "derive once and route every planning command through it" is the right mental model.

3. **`TARGET_REF` resolution loop in `upgrader.md`**: The probe-before-assume pattern (trying `v$TARGET`, then `$TARGET`, then `main`, verifying against plugin.json content) is robust and prevents the silent-wrong-version failure mode. The HALT-on-no-match is correct.

4. **Read-only agent constraints enforced**: Removing CI/commit instructions from `document-reviewer` and `security-reviewer` correctly aligns agent capabilities with their tool grants. The explanation ("its granted tools are Read, Grep, Glob... it cannot commit") is clear.

5. **Gate integrity for missing API keys**: The new "No keys at all — the gate does NOT auto-open" section correctly prevents self-certification past a failed gate. The four-step required sequence (write failure record → run self-review → surface gap → explicit approval to proceed) is sound security process.

6. **`check-ci` fix for hardcoded `main`**: Changing `/check-ci main` to `/check-ci` (auto-detect current branch) is a meaningful correctness fix — verifying the base branch instead of the feature branch gives false confidence.

7. **`agentive review-input` format selection guidance**: The `--format diff|full` guidance based on change shape (logic vs. strings/docs) is practical and backed by cited retro data (KIT-0092).

8. **`wrap-up.md` Variant A/B summary**: Distinguishing COMPLETE from IN REVIEW in the completion summary prevents a real operator confusion. The "every line is a claim — verify before printing" instruction is a good discipline.

---

## Context Required / Unverifiable

- **`$PLANNING` persistence across tool calls**: Whether LLM agent runtimes persist shell variables between tool invocations is runtime-dependent and cannot be determined from these docs alone.
- **`agentive review-input` CLI implementation**: The `--format` flag behavior, default values, and error handling are not visible in this diff.
- **Plugin cache behavior**: The `~7 days` rollback window claim in `upgrader.md` is marked as "verify; this may change" — correctness depends on the external plugin runtime.
- **`ScheduleWakeup` runtime behavior**: The polling loop's clamp behavior (`[60, 3600]`) is asserted without the runtime implementation being visible.
- **Whether `FEATURE_DEVELOPERS` in tests includes all relevant agent files**: The parametrize list is not fully visible in the diff.

---

## Overall Assessment

**CHANGES_REQUESTED**

The PR is directionally sound and fixes several real defects (evaluator ordering, cross-repo routing, CI branch targeting, read-only agent constraints). The test additions are well-designed. However:

1. **HIGH**: The `$PLANNING` variable persistence issue is a real correctness risk — if the variable is undefined when later phase commands run, the commands silently target wrong paths. This needs explicit mitigation in the agent instructions (re-derive at each use or add a guard).

2. **MEDIUM**: The test regex for the Workflow Overview table is brittle to markdown reformatting and could give false positives on partial heading matches. Tighten the assertions.

3. **MEDIUM**: The massive duplication between `feature-developer.md` and `feature-developer-f5.md` (identical ~130-line Evaluator section) creates a maintenance hazard — the current PR demonstrates this risk by requiring synchronized changes to both files. At minimum, add sync comments; ideally extract to a shared skill.

Security posture is appropriate for a developer-tooling context: no hardcoded credentials, no externally-facing attack surfaces, and the new gate-integrity rules (no self-certification past failed evaluator, read-only agents can't commit) are improvements. The risks are operational correctness risks, not traditional security vulnerabilities.
## Source: KIT-0097-code-review-input--code-reviewer-fast.md

#  Code Reviewer Fast

**Source**: .adversarial/inputs/KIT-0097-code-review-input.md
**Evaluator**: code-reviewer-fast
**Model**: gemini/gemini-2.5-flash
**Generated**: 2026-08-09 17:08 UTC

---

### Findings

**[ROBUSTNESS]: `ci-checker`: Missing `CLAUDE.md` or `## Target Repository` section**
- **Location**: `.claude/agents/ci-checker.md:Pre-flight Check`
- **Edge case**: The `grep -A 5 "## Target Repository" CLAUDE.md 2>/dev/null` command is run in an environment where `CLAUDE.md` does not exist or the "## Target Repository" section is absent (e.g., a new project, malformed `CLAUDE.md`, or a project that explicitly doesn't use this section).
- **What happens**: The `grep` command will exit with a non-zero status code and print "SINGLE_REPO_MODE". While this might seem correct for a single-repo, it's based on the *absence* of the file/section rather than its content. If `CLAUDE.md` is missing for other reasons (e.g., deleted), the logic still assumes "SINGLE_REPO_MODE" which might be incorrect and lead to an agent trying to run `gh` commands against the wrong repo with misleading "mismatch" reports if it interprets the output as single-repo mode when it should have failed earlier. The current logic `|| echo "SINGLE_REPO_MODE"` explicitly handles the non-zero exit code of `grep`, but it doesn't distinguish *why* it exited non-zero (file not found vs. section not found). This is robust *for the stated goal*, but an agent could miss a critical file.
- **Tested?**: No

**[ROBUSTNESS]: `ci-checker`: Empty `CLAUDE.md` or empty "Target Repository" section**
- **Location**: `.claude/agents/ci-checker.md:Pre-flight Check`
- **Edge case**: `CLAUDE.md` exists but is empty, or the `## Target Repository` section exists but contains no content (e.g., no path or GitHub repo defined).
- **What happens**:
    - If `CLAUDE.md` is empty, `grep` will not find the section, leading to "SINGLE_REPO_MODE". This correctly falls back, but might indicate an incomplete setup that the agent doesn't flag.
    - If the section exists but is empty, the `grep` will find the heading, and the `if` condition for "SINGLE_REPO_MODE" will not be met. The agent is then instructed to "SKIP the origin check entirely and go to Cross-Repo Mode" and "Prefer `./scripts/core/verify-ci.sh [branch] --wait` — it auto-detects the `## Target Repository` section in `CLAUDE.md` and routes `gh` to the target repo". If the section is empty, this script (or manual `gh --repo <target_github>`) will not find a target repo value. This will likely lead to subsequent `gh` commands failing or defaulting to the current repo, effectively behaving like single-repo mode but after a "skip" instruction that assumes a valid target repo exists. The instructions assume a *valid* `## Target Repository` implies cross-repo mode, not just its *presence*.
- **Tested?**: No

**[ROBUSTNESS]: `ci-checker`: `gh` not installed or misconfigured**
- **Location**: `.claude/agents/ci-checker.md:Pre-flight Check`
- **Edge case**: The `gh` CLI tool is not installed, not in the PATH, or not authenticated.
- **What happens**: The commands like `gh repo view --json name,owner` will fail. The `fi` block will not be reached, and the agent might halt or produce unexpected errors without a clear instruction for this scenario. The `if [ "$GH_REPO_NAME" != "$ORIGIN_REPO_NAME" ];` check would also likely fail or receive empty strings, leading to incorrect "repos don't match" messages or errors.
- **Tested?**: No

**[CORRECTNESS]: `code-reviewer`: Hardcoded `main` for CI check**
- **Location**: `.claude/agents/code-reviewer.md:Phase 9: CI Verification`
- **Edge case**: The agent is reviewing a PR on a feature branch (`feature/my-new-feature`) against a base branch that is *not* `main` (e.g., `develop`, `release/v1.0`).
- **What happens**: The instructions `"/check-ci main"` or `"./scripts/core/verify-ci.sh main"` will check the CI status of the `main` branch, not the feature branch that contains the changes being reviewed. This means the agent might report CI as passing (if `main` is green) even if the feature branch's CI is failing, or vice-versa, providing an incorrect verdict regarding the PR's CI status.
- **Tested?**: Yes, implicitly by the addition of the new text in the diff that specifically corrects this.

**[ROBUSTNESS]: `feature-developer(-f5)`: `$PLANNING` not correctly set in all scenarios**
- **Location**: `.claude/agents/feature-developer*.md:Phase 1: Start`
- **Edge case**:
    1.  The `CLAUDE.md` file *does not* contain the `## Target Repository` section, but the agent believes it's in split mode (e.g., due to a misconfigured handoff or previous state).
    2.  The `CLAUDE.md` file *does* contain the section, but the `Path` value is missing or malformed, preventing `PLANNING=~/Github/<project>-planning` from resolving correctly.
- **What happens**:
    1.  If the agent *thinks* it's in split mode but the `grep` indicates single-repo, the instructions for setting `$PLANNING` in split mode might be applied incorrectly, leading to `PLANNING` pointing to a non-existent or wrong path, causing subsequent commands like `cat "$PLANNING"/.kit/tasks/*/<TASK-ID>-*.md` to fail.
    2.  If the path is missing/malformed, `$PLANNING` might be set to an invalid path. The agent assumes a valid absolute path will be set. Commands relying on `$PLANNING` will then fail with "No such file or directory". The instructions mention `derive the planning root once and route every planning command through it`, but don't specify how to derive it if the `## Target Repository` path is malformed/missing.
- **Tested?**: No

**[ROBUSTNESS]: `feature-developer(-f5)`: `agentive review-input` with uncommitted changes**
- **Location**: `.claude/agents/feature-developer*.md:Phase 5: Evaluator (GATE) — before the PR opens -> Step 1 — Prepare the input`
- **Edge case**: The agent forgets to run `git commit` before `agentive review-input <TASK-ID>`, or there are untracked files.
- **What happens**: The instructions explicitly state: "**Commit the tree first.** The helper (and any manual `git diff main...HEAD`) reads committed state — uncommitted work is invisible to it and silently absent from the review input." However, an agent could still make this mistake. The `agentive review-input` command would then generate a review input that *does not include the latest changes*, leading the evaluators to review an outdated version of the code. This results in missing findings or irrelevant findings based on pre-commit state, effectively bypassing the gate's intent without an explicit failure.
- **Tested?**: No (The test `test_feature_developer_runs_evaluator_before_pr_open` verifies ordering, not this specific operational robustness).

**[ROBUSTNESS]: `feature-developer(-f5)`: Evaluator `--format` choice for mixed changes**
- **Location**: `.claude/agents/feature-developer*.md:Phase 5: Evaluator (GATE) — before the PR opens -> Step 1 — Prepare the input`
- **Edge case**: The change includes both logic changes (requiring `full` format) and string/docs-only changes (requiring `diff` format). For example, a new function is added, and its inline documentation is also updated, along with some unrelated string literals in other files.
- **What happens**: The instructions say: "Choose `--format` by the SHAPE of the change, not by default". If the change is mixed, the agent must make a subjective choice.
    - Choosing `full` might lead to "noise that costs a disposition round each" from doc-only parts of the PR (as per KIT-0092).
    - Choosing `diff` might cause "models to hallucinate 'missing' symbols" for the logic changes.
    This creates an ambiguous situation where the agent cannot satisfy both criteria optimally, potentially leading to suboptimal evaluator results (either too much noise or missing context for critical parts).
- **Tested?**: No

**[CORRECTNESS]: `feature-developer(-f5)`: `project move` rename handling**
- **Location**: `.claude/agents/feature-developer*.md:Phase 9: Handoff`
- **Edge case**: The agent moves the task file using `"$PLANNING"/scripts/core/project move <TASK-ID> in-review`, then attempts to `git add` the original path or `git add .` without realizing the file was *renamed* (moved).
- **What happens**: The instructions now explicitly warn: "`project move` RELOCATES the task file — `.kit/tasks/3-in-progress/…` becomes `.kit/tasks/4-in-review/…`. A follow-up `git add` that names the OLD path stages nothing, and the rename goes uncommitted." If the agent is not careful (e.g., `git add .` might not always correctly stage the rename across all git versions/configurations without an explicit `git add -u` or similar for renamed/deleted files, or if there are new untracked files. `git add -A` is explicitly discouraged earlier). This could lead to the task status change not being committed, causing a discrepancy between the local state and the intended state.
- **Tested?**: No (the test checks phase ordering, not `project move` side effects).

**[ROBUSTNESS]: `test-runner`: `project start` on non-`main` branch in split mode**
- **Location**: `.claude/agents/test-runner.md:Starting a Task — check before you move`
- **Edge case**: In a split-repo setup, the planning repo is separate. The agent is in the *target* repo worktree on a feature branch, and the *planning* repo's `main` branch (which holds the task file) has the task still in `2-todo/`.
- **What happens**: The instruction states: "**Split mode**: `.kit/tasks/` lives in the PLANNING repo — run the command there, never against the target repo." However, if the agent `cd`'s to the planning repo's root to run `project start`, and that planning repo is *also* on a feature branch (not `main`), the instruction "Task in `2-todo/` but you are on a feature branch or in a worktree → do NOT move it from here. The move belongs on `main`..." applies. This correctly prevents a branch-specific status update. However, if the agent *only* has the target repo open and needs to `project start` in the planning repo, it would need instructions on how to access/interact with the planning repo from its current session (e.g., `git -C "$PLANNING" ...`). The current phrasing `run the command there` assumes the agent can easily switch context or has the planning root configured.
- **Tested?**: No

**[CORRECTNESS]: `test-runner`: Undefined project test commands/thresholds**
- **Location**: `.claude/agents/test-runner.md:Primary Testing Protocol` & `Test Suite Location` & `Success Criteria`
- **Edge case**: `CLAUDE.md` and/or `pyproject.toml`/`package.json` do not explicitly define the test commands, framework, or coverage thresholds.
- **What happens**: The instructions state "Test commands, framework, and thresholds are project-owned — read them from `CLAUDE.md` and the task spec before running anything". If these are missing or incomplete, the agent won't know *how* to run tests or what "success" means, leading to ambiguity or arbitrary choices (e.g., falling back to `pytest tests/ -v` even if the project uses `jest`). This could lead to incomplete testing or incorrect success reporting.
- **Tested?**: No

**[ROBUSTNESS]: `upgrader`: `TARGET_REF` resolution for very old `CURRENT` versions**
- **Location**: `.claude/agents/upgrader.md:Phase 1: Verify Current and Target Versions`
- **Edge case**: The currently installed version (`CURRENT`) is very old and predates the explicit tagging scheme (`vX.Y.Z` or `X.Y.Z`) on the marketplace, or its `plugin.json` doesn't accurately report its version at the time of publication (e.g., initial versions might have been less strict).
- **What happens**: The `CURRENT_REF` resolution loop (implied to be similar to `TARGET_REF`) `for ref in "v$CURRENT" "$CURRENT" main; do ...` might fail to find a ref whose `plugin.json` matches `$CURRENT`. The instructions explicitly state for `TARGET_REF`: `echo "TARGET_REF=${TARGET_REF:?could not resolve a ref whose plugin.json reports $TARGET}"`. A similar implicit failure for `CURRENT_REF` would block the process. If it falls through, the `diff` in Phase 2a might not work correctly (`diff "/tmp/$dir-current.txt" "/tmp/$dir-target.txt"`) if `CURRENT_REF` is unset or wrong. The text later acknowledges: "If `CURRENT_REF` cannot be resolved... report that plainly and diff only what you can — an unresolvable current ref makes the name-diff unavailable, not optional to fake." This is good, but the initial resolution loop might still be brittle to very old, untagged, or inconsistent `plugin.json` definitions.
- **Tested?**: No

**[ROBUSTNESS]: `upgrader`: Rollback when plugin cache is empty/evicted**
- **Location**: `.claude/agents/upgrader.md:Phase 5: Revert (if needed)`
- **Edge case**: The agent attempts to roll back to a previous version, but the plugin cache has been evicted or the previous version directory is no longer present.
- **What happens**: The instructions state: "The supported local path is the retained plugin cache: it keeps prior version directories for a short window (~7 days at time of writing — **verify; this may change**), so an immediate rollback is local and fast." and then provides a clear `HALT and tell the operator plainly` instruction if the rollback did not happen. This is a very robust handling of the edge case, *provided the agent strictly follows the HALT instruction*. An adversarial agent might try to proceed by trying to reinstall the old version via `gh api` or similar, which is not instructed.
- **Tested?**: No (The instructions describe the expected outcome and mitigation, but there's no automated test for it.)

**[ROBUSTNESS]: `check-ci`: Workflow not dispatchable**
- **Location**: `.claude/commands/check-ci.md:Manually Triggering a Workflow Run`
- **Edge case**: The identified test workflow (`<workflow-file-or-name>`) does *not* declare `workflow_dispatch:` in its `on:` triggers.
- **What happens**: The instructions clearly state: "Dispatch only works if the workflow declares `workflow_dispatch:` in its `on:` triggers. If it does not, `gh workflow run` errors — in that case push an empty commit...". This is a robust instruction set. However, an agent could misinterpret "push an empty commit" as a *fix* that makes the workflow dispatchable, rather than an alternative trigger. The risk is more in the agent's interpretation and its ability to distinguish between "workflow is not dispatchable" and "workflow dispatch failed for other reasons".
- **Tested?**: No

**[ROBUSTNESS]: `check-spec`: `git diff` fails due to detached HEAD or missing `origin/main`**
- **Location**: `.claude/commands/check-spec.md:Step 1: Identify the task`
- **Edge case**:
    1.  The `git` repository is in a detached HEAD state.
    2.  The `origin` remote does not exist, or `origin/main` branch does not exist (e.g., `main` is named `master`, or the remote is named differently).
- **What happens**:
    1.  If in detached HEAD, `git diff origin/main...HEAD` might behave unexpectedly or report no changes, potentially misleading the agent into thinking there are no diffs.
    2.  If `origin/main` is missing, `git fetch origin main` will fail, and subsequent `git diff` commands will likely also fail, leading to an unclear failure for the agent. The command `git fetch origin main` is presented as a command without explicit error handling or checks for success before proceeding to `git diff`.
- **Tested?**: No

**[ROBUSTNESS]: `preflight`: `--task` and `--pr` auto-detection failures**
- **Location**: `.claude/commands/preflight.md:Run preflight`
- **Edge case**: The auto-detection for `--task` (from branch name) or `--pr` (from `gh pr view`) fails or provides incorrect values (e.g., malformed branch name, no open PR, multiple open PRs).
- **What happens**: The instructions state: "Every flag has a fallback (`--pr` auto-detects, `--task` derives from the branch), so a bare `agentive preflight` works in the common case; pass them explicitly whenever the auto-detection could be wrong." If auto-detection fails, the `agentive preflight` script might run with incorrect or missing arguments, leading to an incomplete or irrelevant preflight check, but still reporting "PASS" for the check itself, based on potentially wrong inputs. The agent might not realize the auto-detection was faulty.
- **Tested?**: No

**[ROBUSTNESS]: `retro`: Incomplete "Escalated" incident closure**
- **Location**: `.claude/commands/retro.md:Step 3: Classify each incident`
- **Edge case**: An agent chooses the "Escalated" option but fails to provide (a) what happened, (b) why options 1-3 don't fit, or (c) the specific question for the planner.
- **What happens**: The instructions explicitly state: "An escalation without (a), (b), and (c) is not a closure — it is the incident going unrecorded with extra words." An agent *could* still provide an incomplete escalation due to misunderstanding or oversight. This would result in a retro entry that appears to close the incident but lacks the necessary information for the planner to actually classify it, essentially "punting" without proper context. While the instructions are clear on what *should* happen, an adversarial agent might exploit this by providing minimal or vague details to satisfy the surface-level requirement without genuinely addressing the problem.
- **Tested?**: No

**[CORRECTNESS]: `wrap-up`: Agent choosing wrong completion variant**
- **Location**: `.claude/commands/wrap-up.md:Step 4: Confirm completion`
- **Edge case**: The agent's session concludes, but the PR is not yet merged, however the agent prints "Variant A — PR merged, Step 3 ran `project complete`".
- **What happens**: The instructions state: "The header line depends on what Step 3 actually did — pick the variant that matches, never print COMPLETE by default." If an agent mistakenly chooses Variant A when the PR is still open, the summary will incorrectly state "COMPLETE" and "PR: <PR-URL> (merged)", contradicting the actual PR status and leading the operator to believe the task is fully done when it's still in review. This is explicitly highlighted as an anti-pattern.
- **Tested?**: No

**[ROBUSTNESS]: `code-review-evaluator`: Agent ignores "STOP" instruction for missing API keys**
- **Location**: `.claude/skills/code-review-evaluator/SKILL.md:No keys at all — the gate does NOT auto-open`
- **Edge case**: All required API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) are unset, and the agent, despite the explicit "STOP" instruction, decides to "document the failure and proceed to human review" without explicit coordinator approval.
- **What happens**: The instructions are *very* clear: "Do not 'document the failure and proceed' on your own authority... Surface the gap to the coordinator/operator and STOP... Proceed to human review only on explicit approval, and record that approval." An adversarial agent might rationalize that documenting *is* surfacing, and proceed anyway, bypassing a critical gate and marking work complete when it shouldn't. The explicit "STOP" and "only on explicit approval" are strong, but reliance on agent adherence is still a point of failure.
- **Tested?**: No

**[ROBUSTNESS]: `test_agent_contracts.py`: Regex robustness to phase title variations**
- **Location**: `tests/test_agent_contracts.py:test_feature_developer_runs_evaluator_before_pr_open`
- **Edge case**: A future update slightly changes the wording of a phase title (e.g., "CI + Bots" becomes "CI/CD + Bot Review") or adds extra whitespace/punctuation.
- **What happens**: The regex `re.findall(r"^## Phase (\d+): (.+)$", text, re.MULTILINE)` specifically looks for the exact pattern "## Phase N: Title". If a title like "## Phase 7: CI + Bot Review (GATE)" becomes "## Phase 7: CI/CD & Bot Review [GATE]", the regex might fail to match, causing `find("CI + Bot")` to return `None`, leading to an assertion failure that the heading doesn't exist, rather than failing on the ordering itself. While the test is effective for current titles, it's brittle to minor variations.
- **Tested?**: Yes, this is a test. The edge case is about the test's robustness.

### Test Gap Summary

| Edge Case | Function | Tested? | Risk |
|---|---|---|---|
| Missing `CLAUDE.md` or `## Target Repository` section | `ci-checker` | No | High |
| Empty `CLAUDE.md` or empty "Target Repository" section | `ci-checker` | No | Medium |
| `gh` not installed or misconfigured | `ci-checker` | No | High |
| `$PLANNING` not correctly set in all scenarios | `feature-developer(-f5)` | No | High |
| `agentive review-input` with uncommitted changes | `feature-developer(-f5)` | No | High |
| Evaluator `--format` choice for mixed changes | `feature-developer(-f5)` | No | Medium |
| `project move` rename handling | `feature-developer(-f5)` | No | Medium |
| `project start` on non-`main` branch in split mode | `test-runner` | No | Medium |
| Undefined project test commands/thresholds | `test-runner` | No | High |
| `TARGET_REF` resolution for very old `CURRENT` versions | `upgrader` | No | High |
| Rollback when plugin cache is empty/evicted | `upgrader` | No | Medium |
| Workflow not dispatchable | `check-ci` | No | Medium |
| `git diff` fails due to detached HEAD or missing `origin/main` | `check-spec` | No | High |
| `--task` and `--pr` auto-detection failures | `preflight` | No | Medium |
| Incomplete "Escalated" incident closure | `retro` | No | Medium |
| Agent choosing wrong completion variant | `wrap-up` | No | High |
| Agent ignores "STOP" instruction for missing API keys | `code-review-evaluator` | No | High |
| Regex robustness to phase title variations | `test_agent_contracts.py` | Yes (Self-test) | Medium |

### Verdict

- **CONCERNS**: Multiple untested edge cases and robustness gaps found across various agents and commands. While some instructions provide explicit warnings or mitigation steps, the lack of automated testing for these critical scenarios means agent adherence is the only safeguard. The `feature-developer` phase reordering is correctly identified and tested, which is good, but the operational robustness of the new evaluator flow still has significant gaps. Specifically, scenarios where files are missing/malformed, tools are misconfigured, or explicit "HALT" instructions are ignored pose a high risk of incorrect agent behavior or silent failures.
## Source: KIT-0097-code-review-input--code-reviewer.md

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0097-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-08-09 17:11 UTC

---

### Summary
Reviewed the single code change that actually executes at run-time – the new test `test_feature_developer_runs_evaluator_before_pr_open` in `tests/test_agent_contracts.py` – plus the shell snippets embedded in the updated markdown “agent/command” specs.  One medium-severity correctness bug and four robustness / test-fragility issues were found.  No blocking defects in production code paths, but the new test can mis-classify future documents and the added shell snippets contain regex / quoting pitfalls.

### Findings

**ROBUSTNESS: brittle heading regex in new test**
- **Location**: `tests/test_agent_contracts.py:test_feature_developer_runs_evaluator_before_pr_open` (line 20)
- **Edge case**: heading written as `### Phase 5:`, or extra spaces (`##  Phase 5:`) or an md-style HTML comment directly before the `##`.
- **What happens**: `re.findall(r"^## Phase (\d+): (.+)$", …, re.MULTILINE)` fails to capture the heading, so `evaluator is None` → test error although the document is semantically correct.
- **Expected**: The check should tolerate any amount of whitespace and `#` level, or use a markdown parser instead of a hand-rolled regex.
- **Test coverage**: NOT covered – this is the test itself.
- **Severity**: Latent

**ROBUSTNESS: table-row assertion can false-fail**
- **Location**: same test, last `assert re.search(...)`
- **Edge case**: the overview table is indented two spaces (common inside list items) or uses smart quotes (`“before PR open”`).
- **What happens**: Regex anchors on `^|`, so one leading space breaks the match; fancy quotes break the literal `before PR open` substring.
- **Expected**: Strip optional whitespace and match case-insensitively on `PR` + `open` tokens, or parse pipe tables structurally.
- **Test coverage**: NOT covered
- **Severity**: Latent

**CORRECTNESS: possible false-positive branch order test**
- **Location**: loop `for axis, idx in (("declared…"), ("document…"))`
- **Edge case**: Docs contain two “## Phase 5: Evaluator …” headings (historical notes, change log). `find()` picks the first, so the later real section could still be after Ship → evaluator really after PR open but test believes order correct.
- **Expected**: Only consider headings inside the “Workflow” section or the first heading of each unique phase number.
- **Test coverage**: NOT covered
- **Severity**: Latent

**CORRECTNESS: `TARGET_REF` resolution grep is too permissive**
- **Location**: `.claude/agents/upgrader.md`, shell snippet in Phase 1
- **Edge case**: target version `1.2.3` and master branch also contains `"version": "1.2.30"` (a later dev tag). Regex `grep -q "\"version\": *\"$TARGET\""` treats dots as “any char”, so `"1X2X3"` matches.
- **What happens**: Loop accepts the wrong ref, leading the agent to reconcile against the wrong version. Subsequent upgrade steps act on mismatched artefacts.
- **Expected**: Quote dots (`"${TARGET//./\\.}"`) or anchor the JSON field (`"version":[[:space:]]*"$TARGET"$`).
- **Test coverage**: NOT covered
- **Severity**: Bug

**ROBUSTNESS: cross-repo topology probe prints data instead of using exit status**
- **Location**: `.claude/agents/ci-checker.md` (and other docs) – `grep -A 5 … || echo "SINGLE_REPO_MODE"`
- **Edge case**: In split mode the command prints the header lines; scripts that expect the sentinel string now receive non-empty output and may mis-classify mode if they do `if [[ -n "$(…)"]]; then …`.
- **What happens**: Down-stream shell logic that relies on content instead of exit status can skip the origin check even in single-repo projects.
- **Expected**: Decide on exit status (use `grep -q`) or guarantee the sentinel string appears on *both* branches.
- **Test coverage**: NOT covered
- **Severity**: Latent

### Edge Cases Verified Clean
- Heading text “Evaluator (GATE) — before the PR opens” still matches `.startswith("Evaluator")`.
- Mix of “CI + Bot Review” heading and “CI + Bots” table row passes regex.
- Path handling in the test (`REPO / agent`) matches existing patterns used earlier in the file.

### Test Gap Summary

| Edge Case | Function/Test | Tested? | Risk |
|-----------|---------------|---------|------|
| headings with extra `#` or spaces | order test | No | Low/annoyance |
| duplicated phase headings | order test | No | Medium |
| smart-quotes / indent in table | row regex | No | Low |
| `1.2.30` vs `1.2.3` version grep | upgrader shell | No | Medium-High |
| grep mode sentinel ambiguity | ci-checker topology | No | Medium |

### Verdict
**CONCERNS**

No immediate production breakage, but:

1. `upgrader` version-resolution bug can point an upgrade at the wrong plugin tag.
2. New ordering test is brittle and may create false failures for innocuous markdown edits.
3. Cross-repo detection command may give wrong topology classification to downstream scripts.

Recommend tightening the shell regex, using `grep -q` / anchored patterns, and hardening the new test with a markdown parser or more tolerant regexes.
