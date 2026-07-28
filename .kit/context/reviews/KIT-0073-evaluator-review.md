# KIT-0073 Evaluator Review Record

**Date**: 2026-07-28
**Input**: `.adversarial/inputs/KIT-0073-code-review-input.md` (250KB, full diff vs main)
**Trio**: code-reviewer-fast-v2 (CONCERNS), code-reviewer/o3 (CONCERNS), claude-code (CHANGES_REQUESTED)
**Gate note**: This PR is a PROSE-DOMINATED sweep — per the Phase-7
prose-sweep exception (KIT-0069), the trio is RECORDED, and findings
were actioned only where reproduced against the working tree. The
planner's tree-grounded verification is this PR's merge gate.

## Triage (every finding reproduced-or-refuted against the tree)

| # | Evaluator | Claim | Reproduction | Disposition |
|---|-----------|-------|--------------|-------------|
| 1 | fast-v2 | create-project.md still cites TEST-SUITE-WORKFLOW | `grep -rn TEST-SUITE .claude/agents/` -> zero hits | REFUTED (pre-fix reconstruction) |
| 2 | fast-v2 | docs/PLUGIN-UPGRADE-GUIDE.md doesn't exist | `ls` -> exists (audit KEEP) | REFUTED |
| 3 | fast-v2 | KIT-0059 still references .kit/skills/ | KIT-0059 is the task that removes .kit/skills; the references are its scope | REFUTED (misread) |
| 4 | fast-v2 | Magic-number manifest counts brittle | Pre-existing deliberate design (CLAUDE.md: tests enforce entry counts) | OUT OF SCOPE, recorded |
| 5 | fast-v2 | ADR-CREATION:126 still has .kit/tasks/active/ | `grep -n 'active/'` -> zero hits | REFUTED (pre-fix reconstruction) |
| 6 | o3 | AGENT-TEMPLATE still links RESEARCH-QUALITY-STANDARDS | `grep -n RESEARCH-QUALITY` -> zero hits (section removed) | REFUTED (pre-fix reconstruction) |
| 7 | o3 | Heredoc regex fragile in test_core_manifest | Pre-existing test code, untouched by this PR (count edits only) | OUT OF SCOPE, recorded |
| 8 | o3 | create-project Step 5 still claims .adversarial/ includes docs | Text now reads "(config, templates, inputs)" | REFUTED (pre-fix reconstruction) |
| 9 | o3 | Trailing-slash drift guard missing | Pre-existing test design, untouched | OUT OF SCOPE, recorded |
| 10 | o3 | Hard-coded counts fragile | Same as #4 | OUT OF SCOPE, recorded |
| 11 | o3 | .adversarial/docs/ dir still on disk after file delete | `ls .adversarial/docs` -> No such file or directory | REFUTED |
| 12 | claude-code | PLUGIN-UPGRADE-GUIDE / CROSS-REPO-PATTERN / LINEAR-SYNC-BEHAVIOR may not exist | `ls` all three -> exist | REFUTED (diff-only blindness, self-acknowledged) |
| 13 | claude-code | F5 grep evidence not in diff | It's in the PR body per acceptance criteria | RESOLVED |
| 14 | claude-code | MANIFEST minimal snippet could be misread as complete manifest | Reproduced (snippet is structurally a full JSON doc) | ACTIONED: lead-in now says snippets show only that one field |
| 15 | claude-code | Task file Assigned To: unassigned while In Progress | Reproduced | ACTIONED: set to feature-developer-f5 |
| 16 | claude-code | Absolute worktree path in handoff file | Standing kit convention (LAUNCH blocks carry absolute paths); handoffs are internal coordination records | DECLINED, recorded |

**Pattern**: 7 of 8 correctness claims were reconstructions of the
pre-fix state from diff-only context — the exact KIT-0069 trio failure
mode this PR's gate design anticipates (trio 0-for-7 there; 0-for-7 on
correctness here too). The two actioned items were both prose-quality
notes on newly written text, reproduced against the tree.

---


## Full log — code-reviewer-fast-v2

#  Code Reviewer Fast V2

**Source**: .adversarial/inputs/KIT-0073-code-review-input.md
**Evaluator**: code-reviewer-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-07-28 11:53 UTC

---

### Findings

**[CORRECTNESS]: Broken Reference to deleted `TEST-SUITE-WORKFLOW.md`**
- **Location**: `.claude/agents/create-project.md:243` (and potentially other agent files)
- **Edge case**: Agent attempts to provide documentation links for its own role.
- **What happens**: The agent instructions still point to `.kit/context/workflows/TEST-SUITE-WORKFLOW.md`. This file was deleted in the PR (merged into `TESTING-WORKFLOW.md`). The agent will fail to find its own procedure manual.
- **Tested?**: No.

**[CORRECTNESS]: Dead Links in `docs/UPDATING-YOUR-PROJECT.md`**
- **Location**: `docs/UPDATING-YOUR-PROJECT.md:5`
- **Edge case**: User attempts to follow the guide to upgrade plugins.
- **What happens**: The header references `docs/PLUGIN-UPGRADE-GUIDE.md`. This file does not appear in the changed files list as added, moved, or existing. It is likely a broken reference to a non-existent or renamed file.
- **Tested?**: No.

**[ROBUSTNESS]: Missing link repointing in `KIT-0059-remove-skills-read-both-symlinks.md`**
- **Location**: `.kit/tasks/1-backlog/KIT-0059-remove-skills-read-both-symlinks.md`
- **Edge case**: Execution of the 0.9.0 cleanup task.
- **What happens**: The task instructions still reference `.kit/skills/` as a destination. While the PR updates `MANIFEST-UPGRADE-GUIDE.md`, it misses updating the internal logic of this specific backlog task to reflect that `.kit/skills/` is being purged in favor of `.claude/skills/`.
- **Tested?**: No.

**[TESTING]: Hardcoded Manifest Count Fragility**
- **Location**: `tests/test_core_manifest.py:test_kit_builder_count`
- **Edge case**: Addition or removal of any file in the `.kit/` or `.adversarial/` directories.
- **What happens**: The test asserts a magic number (`10`). While the PR correctly updates this from `11` to `10` because of the deletion of `.adversarial/docs/`, this "magic number" testing strategy will break every time documentation is curated. It does not verify *which* files are there, only the count.
- **Tested?**: Yes (but logic is brittle).

**[CORRECTNESS]: `ADR-CREATION-WORKFLOW` points to stale task folder structure**
- **Location**: `.kit/context/workflows/ADR-CREATION-WORKFLOW.md:126`
- **Edge case**: Agent/User follows ADR template to link back to a task.
- **What happens**: The template suggests `.kit/tasks/active/TASK-YYYY-####.md`. However, the kit has migrated to numbered folders (`1-backlog`, `2-todo`, `3-in-progress`). The "active" directory no longer exists.
- **Tested?**: No.

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| Broken file references in Agent prompts | `.claude/agents/*.md` | No | Medium - Agents will hallucinate instructions or fail to find docs. |
| Non-existent file in documentation header | `docs/UPDATING-YOUR-PROJECT.md` | No | Low - User confusion during updates. |
| Path collisions in backlog tasks | `.kit/tasks/1-backlog/` | No | Low - Task instructions out of sync with repo reality. |

### Verdict

**CONCERNS**

The PR successfully executes a massive curation of the documentation, significantly reducing the "noise" in the README and consolidating testing workflows. However, it introduces several **dead links** and **broken references** across the agent instruction files (`.md`) because it deleted `TEST-SUITE-WORKFLOW.md` and `EVALUATION-WORKFLOW.md` without performing a comprehensive grep-and-replace on the agent prompts. These agents rely on these paths to function within their "Quick Reference" sections.

**Recommended Action**: Perform a global grep for `TEST-SUITE-WORKFLOW.md` and `EVALUATION-WORKFLOW.md` across all `.md` files to ensure all pointers are updated to `TESTING-WORKFLOW.md` and the `code-review-evaluator` skill respectively.

## Full log — code-reviewer (o3)

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0073-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-28 11:54 UTC

---

### Summary
Reviewed all code‐affecting changes in KIT-0073 (mainly: core-manifest.json, tests/test_core_manifest.py, Agent / workflow markdown).  No production Python logic altered, but the manifest/test pair is safety-critical and several template / doc changes can break downstream automation.  I found 3 correctness issues, 2 robustness gaps, and 4 un-tested link-break cases.

### Findings

**[CORRECTNESS]: AGENT template now links to a deleted file**
- Location: `.kit/templates/AGENT-TEMPLATE.md` (≈ line 250)
- Edge case: Any new agent generated from the template clicks the link to `.kit/context/workflows/RESEARCH-QUALITY-STANDARDS.md`.  That file was moved to `docs/archive/…`, so the link 404s.
- What happens: Generated agents instruct users and evaluators to open a path that no longer exists; automated link-lint and human readers will flag errors.
- Expected: Update the reference to `docs/archive/RESEARCH-QUALITY-STANDARDS.md` or, better, move the doc to an official live location.
- Test coverage: NOT covered (template files are not exercised).
- Severity: Latent – manifests when someone uses the template.

---

**[ROBUSTNESS]: `_planning_heredoc_core_version` fragile to spacing**
- Location: `tests/test_core_manifest.py` lines 138-167
- Edge case: If `engine-consumer.sh` changes its heredoc opener from
  `<<'MANIFEST'` (no space) to the far more common `<<'MANIFEST'` (no extra space) **or** `<<MANIFEST`, the regex `"<< 'MANIFEST'"` will not match, returning `None` and silently skipping the consistency test.
- What happens:  The baked-version test will pass even when the heredoc is present but modified, defeating the guard it was added for.
- Expected: Use a regex that allows any amount of whitespace between `<<` and the quote, e.g. `r"<<\s*'MANIFEST'"`.
- Test coverage: Partially – the current engine keeps a space so the bug does not surface.
- Severity: Latent – next edit to the engine can silently break the guard.

---

**[CORRECTNESS]: create-project bullet list still omits archived evaluator template**
- Location: `.claude/agents/create-project.md` Step 5
- Edge case: Door exports a project **with** `.adversarial/docs/` when the upstream kit still contains that directory.  The new guidance says “Do not run adversarial init” because the export already has a working `.adversarial/` – but we just removed that docs folder from the manifest.
- What happens: A fresh project created after this PR *will* be missing the docs directory; the checklist will incorrectly claim it is present, and a future `adversarial` upgrade that expects the docs may try to recreate it.
- Expected: Either stop mentioning the directory or make the door export it via the manifest again.
- Test coverage: None (no E2E for create-project).
- Severity: Latent.

---

**[ROBUSTNESS]: Manifest existence tests don’t guard against future trailing-slash drift**
- Location: `tests/test_core_manifest.py::test_all_*_entries_exist`
- Edge case: If a new directory entry is added **without** a trailing slash (e.g. `.kit/templates`) the helper treats it as a file and only calls `Path.exists()`, which returns True on directories *and* files in most OSes, so the test still passes – but later logic (sync engine) assumes the slash semantics.
- What happens:  Sync may attempt to copy a directory as a file.
- Expected: Explicit `path.is_dir()` / `is_file()` tests regardless of the “/” sentinel.
- Test coverage: This test itself masks the problem.
- Severity: Gap.

---

**[TESTING]: New manifest counts hard-coded, no guard for additions**
- Location: `tests/test_core_manifest.py` hard-wired numbers (27,6,5,10,48)
- Edge case: Any later file-addition to an existing tier fails the test even though it is legitimate; maintainers will forget to update constants.
- What happens: Spurious CI failures or, worse, developers comment out the assertion.
- Expected: Derive expected counts from directory globbing or assert *minimums* only.
- Test coverage: The test itself is the coverage; logic gap remains.
- Severity: Gap.

---

**[INTERACTION]: Removed `.adversarial/docs/` dir still present on disk**
- Location: Repo tree vs manifest
- Edge case: Manifest no longer lists `.adversarial/docs/`, but the directory still exists (only the file inside was deleted).  Sync will **never update or prune** that directory in downstream repos, causing drift between what the manifest claims and what real projects have.
- What happens:  Consumers running `project sync --clean` will keep stale files; some tools rely on presence/absence of directory rather than manifest tier.
- Expected: Either delete the directory outright or keep it in the manifest until the physical deletion release.
- Severity: Latent.

### Edge Cases Verified Clean
- Manifest JSON validates; counts align with tests after path removal.
- Path objects with trailing “/” resolve correctly on POSIX & Windows.
- Updated tests no longer expect `.adversarial/docs/` – suite passes locally.
- CLI scripts untouched; door still exports `.adversarial/config.yml`.

### Test Gap Summary

| Edge Case | Function / Area | Tested? | Risk |
|-----------|-----------------|---------|------|
| Deleted research standards doc reference | Agent template generation | No | Medium |
| Heredoc opener without space | `_planning_heredoc_core_version` | No | Medium |
| Door export missing `.adversarial/docs/` | create-project workflow | No | Medium |
| Directory entry without “/” | manifest validation tests | No | Low |
| Manifest size drift | manifest count tests | Manual update only | Low |

### Verdict
**CONCERNS** – No immediate runtime breakage, but template and guard issues introduce latent bugs and broken links.  Fix references, harden the heredoc matcher, and reconsider manifest/tests brittleness before merge.

## Full log — claude-code

#  Claude Code

**Source**: .adversarial/inputs/KIT-0073-code-review-input.md
**Evaluator**: claude-code
**Model**: anthropic/claude-sonnet-4-6
**Generated**: 2026-07-28 11:55 UTC

---

## Phase 1: Understand Intent

This PR is a **documentation curation** task (KIT-0073). It:
- Reduces README.md from ~580 to ~120 lines
- Archives/deletes stale documentation files
- Merges `TEST-SUITE-WORKFLOW.md` content into `TESTING-WORKFLOW.md`
- Creates two new reference pages (`docs/LINEAR-INTEGRATION.md`, `docs/UPDATING-YOUR-PROJECT.md`)
- Updates internal cross-references from deleted/moved paths to current locations
- Updates manifest count assertions in tests to match the removed entry

**Critical paths**: No executable code is changed. All changes are documentation, configuration (`.core-manifest.json`), and test assertions (`test_core_manifest.py`). The only "security surface" is procedural — agent instructions and workflow documentation.

---

## Phase 2: Security Analysis

**Injection Vectors**: Not applicable — no executable code modified.

**Authentication & Authorization**: Not applicable to this diff.

**Data Handling — Hardcoded Paths in Agent Instructions**

The agent files contain hardcoded absolute paths referencing a specific user's filesystem:

```markdown
**Your repository root is `/Users/broadcaster_three/Github/ask-worktrees/KIT-0073/`**
```

This appears in `.kit/context/KIT-0073-HANDOFF-feature-developer.md`. This is a task-specific handoff file (not a template), so the path is intentional and scoped. However, it is worth flagging.

**Secrets Management**: The `docs/LINEAR-INTEGRATION.md` file correctly shows the API key placeholder format (`lin_api_your-key-here`) without embedding real credentials. No credentials are present in the diff.

---

## Phase 3: Correctness Analysis

### [HIGH]: Broken Reference in `docs/UPDATING-YOUR-PROJECT.md`

- **Location**: `docs/UPDATING-YOUR-PROJECT.md`, line 7
- **Issue**: The file references `docs/PLUGIN-UPGRADE-GUIDE.md` as a related document:
  ```markdown
  **Related**: `docs/MANIFEST-UPGRADE-GUIDE.md` (scripts/manifest surface),
  `docs/PLUGIN-UPGRADE-GUIDE.md` (plugin surface)
  ```
  `docs/PLUGIN-UPGRADE-GUIDE.md` does not appear in the diff, is not listed in changed files, and is not verifiable as existing in the repository from the provided context. If it doesn't exist, this is a dead reference in a document whose explicit purpose is guiding operators on update paths.

  The same pattern appears in `docs/UPDATING-YOUR-PROJECT.md`:
  ```markdown
  Agents, skills, and commands distributed via the plugin channel are
  upgraded by the `upgrader` agent, which executes
  `docs/PLUGIN-UPGRADE-GUIDE.md` step-for-step
  ```
  If this file is absent, the `upgrader` agent workflow described here has a broken documentation anchor.
- **Remediation**: Verify `docs/PLUGIN-UPGRADE-GUIDE.md` exists. If not, either create a stub, change the reference to an existing file, or remove the reference until the document exists.

---

### [MEDIUM]: `scripts/.core-manifest.json` Still Lists `.kit/skills/` (Deprecated Symlinks)

- **Location**: `scripts/.core-manifest.json`, `kit_builder` tier
- **Issue**: The manifest still includes `.kit/skills/` in `kit_builder`:
  ```json
  "kit_builder": [
    ".kit/templates/",
    ".kit/skills/",
    ...
  ]
  ```
  The PR removes `.adversarial/docs/` from the manifest (correct), but `.kit/skills/` remains. KIT-0059 (backlog) notes that `.kit/skills/` contains read-both deprecation symlinks scheduled for removal in 0.9.0. The deprecation note is moved from the inline example to the live manifest reference, but the manifest itself still lists this entry. The `test_kit_builder_count` assertion was updated from 11 to 10 (reflecting the removal of `.adversarial/docs/`), which is consistent. This is not a bug introduced by this PR — it pre-existed — but the KIT-0059 task file updated in this PR explicitly calls out that this entry "retargets when the symlinks are removed in 0.9.0," confirming the known debt.
- **Remediation**: No action required in this PR; tracked in KIT-0059. The deprecation note in `docs/MANIFEST-UPGRADE-GUIDE.md` is accurate.

---

### [MEDIUM]: Dead Link in `README.md` — `docs/CROSS-REPO-PATTERN.md`

- **Location**: `README.md`, Pointers table
- **Issue**: The new README references `docs/CROSS-REPO-PATTERN.md` in the Pointers table:
  ```markdown
  | The split-pair pattern | [docs/CROSS-REPO-PATTERN.md](docs/CROSS-REPO-PATTERN.md) |
  ```
  This file is not listed among changed files, not added in this diff, and not verifiable as existing from the provided context. `docs/STARTING-A-PROJECT.md` also references it (`docs/CROSS-REPO-PATTERN.md`). The old README also referenced it, so if it was broken before, it remains broken — but the README rewrite is an opportunity to fix or flag it.
- **Remediation**: Confirm `docs/CROSS-REPO-PATTERN.md` exists. If not, create a stub or remove the reference.

---

### [MEDIUM]: `docs/LINEAR-INTEGRATION.md` References `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` — Unverifiable

- **Location**: `docs/LINEAR-INTEGRATION.md`, header block and body
- **Issue**: The new file references `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` twice:
  ```markdown
  **Related**: `.kit/tasks/README.md` ..., `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` (sync semantics in depth)
  ```
  and later:
  ```markdown
  precedence rules (status field vs. folder vs. Linear state) in
  `.kit/docs/LINEAR-SYNC-BEHAVIOR.md`
  ```
  This file is not present in the diff and cannot be confirmed to exist from the provided context. If absent, two references in a newly created document will be immediately broken.
- **Remediation**: Confirm `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` exists. If not, remove the references or create the file.

---

### [LOW]: `MANIFEST-UPGRADE-GUIDE.md` — Minimal JSON Snippet May Mislead

- **Location**: `docs/MANIFEST-UPGRADE-GUIDE.md`, Step 2
- **Issue**: The "Minimal upgrade" example now shows only:
  ```json
  {
    "opted_in": ["commands_optional"]
  }
  ```
  The accompanying text says "Use the live upstream manifest as your starting point" and explicitly notes that the full manifest is not inlined to avoid drift. However, a reader who copies this snippet verbatim and treats it as a complete replacement (rather than just the `opted_in` field) will produce a malformed manifest missing `core_version`, `source_repo`, `synced_at`, and `files`. The surrounding prose does explain this, but the example is structurally indistinguishable from a complete manifest.
- **Remediation**: Add a comment or label the snippet explicitly, e.g., `// Merge this into the upstream copy — do not use standalone`. Or add a note directly above the code block reinforcing that this is the only field to set, not a complete manifest.

---

### [LOW]: Task Status `Assigned To: unassigned` While Status Is `In Progress`

- **Location**: `.kit/tasks/3-in-progress/KIT-0073-doc-curation-and-readme.md`
- **Issue**: The task file shows `**Status**: In Progress` but `**Assigned To**: unassigned`. This is a minor internal consistency issue in the task tracking system — a task in progress with no owner. The handoff file assigns it contextually, but the task file itself is inconsistent.
- **Remediation**: Update `**Assigned To**` to `feature-developer` or the agent currently executing the task.

---

### [LOW]: Hardcoded Absolute Path in Handoff File

- **Location**: `.kit/context/KIT-0073-HANDOFF-feature-developer.md`
- **Issue**: The handoff contains:
  ```markdown
  **Your repository root is `/Users/broadcaster_three/Github/ask-worktrees/KIT-0073/`**
  ```
  This is a task-specific artifact that will be committed to the repository. While the `.kit/context/` tree is presumably not consumer-facing, if this repo is public or shared, it exposes a local filesystem path and username (`broadcaster_three`). This is low-risk but is an information disclosure of local environment details.
- **Remediation**: For handoff files committed to shared repositories, consider omitting absolute machine-specific paths, or note the pattern as something to strip before the handoff is committed. Since this is already committed in the diff, acknowledge the exposure and establish a policy for future handoffs.

---

## Phase 4: Code Quality

### Positive Observations

1. **Test assertions updated atomically with manifest**: `test_core_manifest.py` count assertions (`test_kit_builder_count`: 11→10, `test_total_entry_count`: 49→48) are updated in the same PR as the manifest change. This is the correct pattern and prevents a broken test state.

2. **"Evidence files are append-only" discipline documented and enforced**: The handoff file and task spec both explicitly call out that audit and curation records are read-only. This is a good epistemic hygiene pattern.

3. **README reduction is well-executed**: The new README (~96 lines) is navigable, avoids duplication, and uses a pointer table rather than inlining content from other docs. The prose is direct and accurate.

4. **Merge provenance tracked**: The new `TESTING-WORKFLOW.md` section notes its origin (`2026-07-28 (KIT-0073 — merged from TEST-SUITE-WORKFLOW.md)`), and `UPDATING-YOUR-PROJECT.md` carries a `**Source**: moved from README.md` footer. This aids future auditors.

5. **`docs/MANIFEST-UPGRADE-GUIDE.md` "live manifest" improvement**: Replacing the frozen inline example with a pointer to the live `scripts/.core-manifest.json` is the right call — the old inline copy was a known drift risk and this PR eliminates it.

6. **Dead reference pruning is thorough**: All internal references to deleted files (`TEST-SUITE-WORKFLOW.md`, `.adversarial/docs/EVALUATION-WORKFLOW.md`, `.adversarial/docs/` in manifest) are updated across all citers found in the diff. The approach is systematic.

7. **No executable code changed**: The PR correctly limits itself to documentation and test-count assertions, keeping the blast radius well-defined.

---

## Context Required / Unverifiable

- **`docs/PLUGIN-UPGRADE-GUIDE.md`**: Whether this file exists cannot be confirmed from the diff. Two new references to it appear in `docs/UPDATING-YOUR-PROJECT.md`.
- **`docs/CROSS-REPO-PATTERN.md`**: Referenced in both `README.md` and `docs/STARTING-A-PROJECT.md`. Cannot confirm existence from provided context.
- **`.kit/docs/LINEAR-SYNC-BEHAVIOR.md`**: Referenced twice in the new `docs/LINEAR-INTEGRATION.md`. Cannot confirm existence.
- **`.kit/tasks/README.md`**: Referenced in `README.md` and `docs/LINEAR-INTEGRATION.md`. Cannot confirm existence from the diff.
- **F5 link-integrity grep**: The task spec requires a repo-wide grep proving no live surface cites moved/deleted paths. This grep output is not included in the diff. Its completion is a merge gate per the task spec, but cannot be verified here.
- **`adversarial evaluate` command behavior** and the `code-review-evaluator` skill: The skill is referenced throughout but its content is not in the diff.

*These observations do not affect the verdict.*

---

## Overall Assessment

**Verdict: CHANGES_REQUESTED**

The PR is well-structured, internally consistent, and the documentation reduction is clean. The test changes are correctly paired with the manifest change. The core issue is **three references to files whose existence cannot be confirmed** — `docs/PLUGIN-UPGRADE-GUIDE.md`, `docs/CROSS-REPO-PATTERN.md`, and `.kit/docs/LINEAR-SYNC-BEHAVIOR.md`. One of these (`PLUGIN-UPGRADE-GUIDE.md`) appears in a newly created file that describes a user-facing upgrade workflow, making it a functional broken link if absent, not merely a cosmetic one.

**Required before merge:**
1. Confirm or fix the `docs/PLUGIN-UPGRADE-GUIDE.md` reference in `docs/UPDATING-YOUR-PROJECT.md`
2. Confirm or fix the `docs/CROSS-REPO-PATTERN.md` reference in README and STARTING-A-PROJECT
3. Confirm or fix the `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` reference in `docs/LINEAR-INTEGRATION.md`
4. Include or link the F5 repo-wide grep evidence in the PR body per the task spec's own acceptance criteria

**Recommended (non-blocking):**
- Clarify the minimal JSON snippet in MANIFEST-UPGRADE-GUIDE cannot be used standalone
- Update `Assigned To` in the task file
