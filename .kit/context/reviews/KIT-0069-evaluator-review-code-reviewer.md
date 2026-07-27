> **DISPOSITION (feature-developer, 2026-07-27): FAIL REFUTED — 0 of 6
> findings reproduce.** Every claim was checked against the tree:
>
> | Claim | Measured |
> |---|---|
> | `scripts/core/project` hard-codes `delegation/tasks/` | 0 occurrences of `delegation`; 8 `.kit/tasks` references |
> | `linear_sync_utils.py` scans `delegation/` | 0 occurrences; `sync_tasks_to_linear.py:517` reads `.kit/tasks` |
> | `create-agent.sh` copies `.claude/agents/AGENT-TEMPLATE.md` | line 42 reads `.kit/templates/AGENT-TEMPLATE.md` |
> | Tests use `@pytest.mark.integration`/`.unit`; `--strict-markers` breaks collection | 0 usages; full suite passed 799/12s **after** marker removal |
> | Helper error text prints `./scripts/<name>.sh --help` | all print `./scripts/core/...` |
> | Two diverging `AGENT-TEMPLATE.md` copies | `.claude/agents/AGENT-TEMPLATE.md` does not exist — its absence *was* finding A21 |
>
> Failure mode: the input was diff-only, and the model reconstructed the
> unchanged side from assumption — reproducing the **pre-fix** state. On a
> truth-sweep PR that reads as "the old paths are still there".
> No action taken. See `.kit/context/KIT-0069-IMPLEMENTATION-NOTES.md` §12.

---

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0069-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-27 00:28 UTC

---

### Summary
Reviewed all code changes across 54 files (~1 200 LOC).  Main executable surfaces touched were
`scripts/core/project`, `scripts/optional/create-agent.sh`, the pytest configuration, and multiple test
fixtures.  Most edits are documentation-only, but three behavioural mismatches and two latent traps
were introduced.  Findings: 3 correctness, 1 robustness, 2 test-gaps.

### Findings

**[CORRECTNESS]: Task-path mismatch breaks every project command**
- **Location**: `scripts/core/project` – functions `move_task`, `validate_all_tasks`, `sync-status`, etc.
- **Edge case**: Repository now stores tasks under `.kit/tasks/…`; code still hard-codes `delegation/tasks/…`.
- **What happens**:
  • `project move`, `validate`, `complete`, `sync-status`, `linearsync` cannot find the file ⇒ “file not found / status mismatch”.
  • `project start / complete` silently make a *second* copy in `delegation/tasks`, so the same task exists twice with divergent status.
- **Expected**: All commands operate on the single canonical tree `.kit/tasks/`.
- **Test coverage**: NOT covered (tests were migrated to `.kit/tasks`, so they will now fail at runtime rather than during collection).
- **Severity**: Bug (broken now).

---

**[CORRECTNESS]: Linear-sync utilities still search old folder**
- **Location**: `scripts/optional/linear_sync_utils.py` – `determine_status_from_path`, `scan_tasks`, etc.
- **Edge case**: Task fixture resides in the new `.kit/tasks` tree.
- **What happens**: Functions return `None` for every task; sync treats them as “unknown folder”, causing
  skipped sync or default status.  New tests updated to `.kit/…` will fail.
- **Expected**: Utility should recognise all `1-backlog … 8-archive` folders under `.kit/tasks`.
- **Test coverage**: Gap (new tests exercise `.kit/` path but code not updated).
- **Severity**: Bug.

---

**[CORRECTNESS]: `create-agent.sh` copies obsolete template**
- **Location**: `scripts/optional/create-agent.sh` (lines ≈ 170, 410)
- **Edge case**: Repository moved canonical template to `.kit/templates/AGENT-TEMPLATE.md`; script still
  pulls from `.claude/agents/AGENT-TEMPLATE.md`.
- **What happens**: New agents are generated from the *stale* template (still Sonnet-4, outdated links).
  If `.claude/agents/AGENT-TEMPLATE.md` is deleted in a future clean-up, the script aborts with
  “template not found”.
- **Expected**: Script should read `.kit/templates/AGENT-TEMPLATE.md` (single source of truth).
- **Test coverage**: NOT covered – integration test mocks agent content, not source path.
- **Severity**: Latent (breaks as soon as old template is removed; currently re-introduces stale content).

---

**[ROBUSTNESS]: Un-registered pytest markers may break collection**
- **Location**: `pyproject.toml` – `[tool.pytest.ini_options].markers`
- **Edge case**: Existing tests still use `@pytest.mark.integration` and `@pytest.mark.unit`
  (search shows at least `tests/test_ci_check.py`, `tests/integration/*`).
- **What happens**: With `--strict-markers` on, pytest aborts at collection:
  `PytestUnknownMarkWarning: unknown mark 'integration'`.
- **Expected**: Either keep the registration or remove the marks from tests.
- **Test coverage**: Covered indirectly in CI (collection will fail).
- **Severity**: Bug.

---

**[TESTING]: Help strings updated inconsistently**
- **Location**: Several `scripts/core/*.sh` (`check-bots.sh`, `gh-review-helper.sh`, `wait-for-bots.sh`, etc.)
- **Edge case**: User follows example `./scripts/core/gh-review-helper.sh …`, but error
  messages still print “Run: ./scripts/gh-review-helper.sh --help”.
- **What happens**: Copy-pasted command from error message fails, causing confusion.
- **Expected**: All usage / error prints reference the same canonical path.
- **Test coverage**: NOT covered
- **Severity**: Latent.

---

**[TEST GAP]: Duplicate templates diverge silently**
- Two versions of `AGENT-TEMPLATE.md` now exist (`.kit/templates/` and `.claude/agents/`).
  No test asserts they stay in sync.  This will regress again unless guarded.

### Edge Cases Verified Clean
- `create-agent.sh` default model change propagated to tests and help text.
- Shebangs & execution bits preserved on all modified shell scripts.
- `project --help` prints updated paths without traceback.
- `.env.template` path corrections are comment-only (no runtime effect).

### Test Gap Summary
| Edge Case | Function | Tested? | Risk |
|-----------|----------|---------|------|
| `.kit/tasks` vs `delegation/tasks` | project CLI | No | High |
| `.kit/tasks` vs `delegation/tasks` | linear_sync_utils | No | High |
| Missing template path | create-agent.sh | No | Medium |
| Unregistered markers | pytest collect | Indirect | High |
| Mixed help paths | shell helpers | No | Low |

### Verdict
**FAIL**

Critical project-management commands (`project …`, Linear sync, agent creation) are
broken or will re-introduce stale data due to hard-coded old paths / templates.
Pytest collection is also at risk from removed markers.  Fix the three
correctness bugs before merging.
