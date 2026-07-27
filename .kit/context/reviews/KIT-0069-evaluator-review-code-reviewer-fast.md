> **DISPOSITION (feature-developer, 2026-07-27): FAIL REFUTED.**
> The verdict rests entirely on `scripts/.core-manifest.json` still listing
> `.kit/skills/`. Two independent checks refute it as a blocker:
> 1. `.kit/skills/` **exists in the tree today**, so the manifest entry
>    resolves and sync works. The hazard appears only after KIT-0059
>    deletes the directory.
> 2. The remedy is already an explicit named Requirement in
>    `.kit/tasks/1-backlog/KIT-0059-remove-skills-read-both-symlinks.md`
>    ("Retarget the manifest: the `kit_builder` tier's `.kit/skills/`
>    entry ... keep `tests/test_core_manifest.py` counts in sync"), with a
>    matching Acceptance Criterion. Nothing is untracked.
>
> 0.9.0 removals are explicitly out of scope for KIT-0069 per the handoff.
> Note the evaluator reasoned about a file that was **not in the diff**.
> The other five findings describe problems this PR fixes.

---

#  Code Reviewer Fast

**Source**: .adversarial/inputs/KIT-0069-code-review-input.md
**Evaluator**: code-reviewer-fast
**Model**: gemini/gemini-2.5-flash
**Generated**: 2026-07-27 00:26 UTC

---

### Findings

**[CORRECTNESS]: Core Manifest Still References Retired `.kit/skills/`**
- **Location**: `scripts/.core-manifest.json` (configuration for distribution sync)
- **Edge case**: A kit-family consumer project (that pulls updates via the manifest sync) runs its sync process after the `.kit/skills/` directory has been removed (as part of KIT-0059).
- **What happens**: The `scripts/.core-manifest.json` (not included in this diff, but referenced in `docs/DISTRIBUTION-ARCHITECTURE.md`) still lists `.kit/skills/` as a path to be synced under `files.kit_builder`. When the sync engine runs on a consumer where `.kit/skills/` no longer exists, it will attempt to sync a non-existent path, leading to errors or warnings during the sync operation. This breaks the distribution contract and causes downstream failures.
- **Tested?**: No (The `KIT-0069-IMPLEMENTATION-NOTES.md` file (§11.1) identifies this as a new finding during the truth sweep and notes it "belongs in KIT-0059's checklist," indicating it is not addressed by this PR).

**[ROBUSTNESS]: `rg` (ripgrep) Limitations Undermine Truth Sweeps**
- **Location**: `.claude/skills/self-review/SKILL.md` (new item 16)
- **Edge case**: An agent or user attempts to perform a comprehensive "truth sweep" or class-wide search across the repository using `rg` (ripgrep) as their primary search tool.
- **What happens**: As detailed in `KIT-0069-IMPLEMENTATION-NOTES.md` (§1), `rg` in this repository has two failure modes: (A) it skips hidden directories (`.kit/`, `.claude/`, etc.) by default, leading to false negatives, and (B) it returned false-empties even with `--hidden` in some cases. Relying on `rg` without careful configuration or cross-verification would lead to an incomplete truth sweep, leaving outdated or incorrect information unaddressed and creating false confidence that issues are resolved.
- **Tested?**: No (This is a meta-finding documented as a new self-review item, based on empirical observation during this task. The recommended `grep -Rn` is a manual process).

**[CORRECTNESS]: `/check-spec` Command References Non-Existent Evaluator**
- **Location**: `.claude/commands/check-spec.md` (Step 3) and `.claude/skills/code-review-evaluator/SKILL.md` (note)
- **Edge case**: A user or agent attempts to use the `adversarial spec-compliance-fast` command as described in the previous version of `/check-spec.md`.
- **What happens**: The command would fail because the `spec-compliance-fast` evaluator was never part of the adversarial-evaluator-library. This prevented automated spec compliance checks from functioning. The current PR correctly updates the documentation to reflect this non-functional state and provides a manual workaround, while KIT-0072 is created to track upstreaming the evaluator. The documentation is now truthful about the broken capability.
- **Tested?**: No (The original problem was a correctness bug. This PR's fix is documentation. Automated end-to-end testing of the evaluator capability is pending KIT-0072).

**[ROBUSTNESS]: Destructive Advice for Evaluator Conflict Resolution**
- **Location**: `.kit/context/workflows/EVALUATOR-LIBRARY-WORKFLOW.md` (Conflict Resolution section)
- **Edge case**: A user or agent encounters an evaluator conflict (two definitions claiming the same name) and follows the previously documented resolution step: `rm -rf .adversarial/evaluators/<provider>/<evaluator-name>`.
- **What happens**: The advised `rm -rf` command would delete the *library-installed* evaluator, as that is precisely where it resides (`.adversarial/evaluators/<provider>/<name>/`). This leads to a broken evaluator setup rather than resolving the conflict, requiring reinstallation.
- **Tested?**: No (This is a documentation fix for a significant robustness flaw, identified as `KIT-0069 / A40`. The new advice to reinstall is robust).

**[CORRECTNESS]: Misleading `sync` Alias for Linear Task Synchronization**
- **Location**: `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` (Common Commands section)
- **Edge case**: A user or agent intends to synchronize tasks to Linear and, based on prior documentation or common aliases, uses `./scripts/core/project sync`.
- **What happens**: The documentation prior to this PR (and general intuition) might suggest `sync` is an alias for Linear synchronization. However, `scripts/core/project sync` was repurposed by KIT-0036 to mean "pull-based core-scripts sync," which rewrites files in the local repository from upstream. This could lead to unintended file changes, data loss, or significant confusion when the expected Linear sync does not occur.
- **Tested?**: No (This is a documentation clarity fix to prevent incorrect usage and potential data loss. The current PR explicitly adds a `⚠️` note).

**[ROBUSTNESS]: Pervasive Documentation Drift for Dynamic Values**
- **Location**: Multiple files and sections, including `AGENT-TEMPLATE.md` (model IDs, pricing), `README.md` (project version), `COMMIT-PROTOCOL.md` (coverage thresholds), `DISTRIBUTION-ARCHITECTURE.md` (manifest tier counts).
- **Edge case**: Hardcoded or manually maintained values in documentation become stale due to project evolution, external API changes, or internal configuration updates.
- **What happens**: Agents and human users relying on the documentation will receive incorrect information. This can lead to using deprecated model IDs, targeting incorrect coverage thresholds, misinterpreting the distribution architecture, or other operational errors.
- **Tested?**: Partial (This PR addresses many specific instances of this problem by either linking to the single source of truth (`pyproject.toml`) or providing a method to query live data (e.g., `curl` for model IDs). However, the general problem of preventing documentation drift for *all* dynamic values remains an ongoing manual vigilance issue, as highlighted by `KIT-0069-IMPLEMENTATION-NOTES.md` §8 and §10).

### Test Gap Summary

| Edge Case | Function/Section | Tested? | Risk |
|---|---|---|---|
| Untracked `.kit/skills/` in core manifest | `scripts/.core-manifest.json` (distribution) | No | **High**: Leads to sync failures for consumer projects. |
| `rg` (ripgrep) limitations for truth sweeps | `.claude/skills/self-review/SKILL.md` | No | **Medium**: Leads to missed findings in future audit tasks. |
| `/check-spec` command refers to a non-existent evaluator | `.claude/commands/check-spec.md` | No | **High**: Blocks automated spec compliance checks. |
| Destructive advice in `EVALUATOR-LIBRARY-WORKFLOW.md` | `EVALUATOR-LIBRARY-WORKFLOW.md` | No | **High**: Leads to user/agent breaking their evaluator setup. |
| Misleading `sync` alias for Linear sync | `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` | No | **High**: Leads to unintended file rewrites or data loss. |
| Documentation drift for dynamic values | Multiple documentation files | Partial | **Medium**: Leads to agents/users relying on incorrect information. |

### Verdict

- **FAIL**: Correctness bugs found. Must fix.

**Reasoning**:
While this pull request comprehensively addresses numerous instances of outdated and incorrect information across the repository—a significant achievement for a "truth sweep"—it fails to resolve a critical correctness bug explicitly identified during its implementation. The core manifest (`scripts/.core-manifest.json`) still contains a reference to the retired `.kit/skills/` directory. This unaddressed issue will lead to distribution sync failures or warnings for downstream consumer projects, violating the core principle of correctness. Although `KIT-0069-IMPLEMENTATION-NOTES.md` logs this finding and attributes it to KIT-0059's checklist, its continued presence means the system configuration is fundamentally incorrect in a way that impacts dependent projects. The presence of this active, known correctness bug warrants a **FAIL** verdict.
