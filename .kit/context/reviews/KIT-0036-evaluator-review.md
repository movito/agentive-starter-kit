# KIT-0036 PR #63 — Evaluator Review Triage (Phase 7)

**Date**: 2026-07-04
**Input**: `.adversarial/inputs/KIT-0036-code-review-input.md` (11 files, full context)
**Evaluators run**: `code-reviewer-fast` (gemini-2.5-flash, CONCERNS),
`code-reviewer` (o3, FAIL), `claude-code` (claude-sonnet-4-6, findings + many POSITIVE).
Raw logs: `KIT-0036-evaluator-code-reviewer-fast.md`,
`KIT-0036-evaluator-code-reviewer.md`, `KIT-0036-evaluator-claude-code.md`.

This PR had already cleared two automated bot rounds (Cursor Bugbot ×5,
CodeRabbit ×8) before the evaluator pass; those are resolved on the PR.

## Accepted and fixed

| Finding | Source | Fix |
|---|---|---|
| Manifest entry path-traversal (`..`) / absolute paths | claude-code MED, — | `_validate_files_section` rejects `..`/absolute entries → exit 3 |
| Tier value not a `list` crashes `_all_entries` | fast | same validator rejects non-list tiers → exit 3; `_all_entries` made defensive for the (leniently-read) target manifest |
| `target` is an existing file → `FileExistsError` | fast, o3 | guard `target exists and not is_dir` → UsageError (exit 2) |
| `source == target` (or nested) destroys live tree via rmtree | o3 (Bug) | resolve both, refuse equal/overlapping roots → UsageError (exit 2) |
| Stray `OSError` leaks a traceback (exit 1 → workflow reads as success) | o3 (Bug) | `main()` catches `OSError` → clean exit 4 |
| Duplicate `--tier` double-counts the plan | o3 | dedup requested tiers in `_select_tiers` |
| `_read_dir` keys use OS separator (report instability) | o3 | normalize keys with `as_posix()` |
| CLI exit-code contract only tested via `main()`, not a real process | o3 | added `test_exit_codes_via_real_subprocess` |
| `_tree_snapshot` reads UTF-8, breaks on binary files | claude-code Q | snapshot via `read_bytes().hex()` |
| `_entry_key_for_relpath` / `SyncReport.complete` doc clarity | claude-code LOW | comments/docstrings added |

New tests: `TestHardening` (traversal, absolute, non-list tier, target-is-file,
source==target, nested, dup-tier) + subprocess exit-code test. Coverage 96%.

## Declined (with reasoning)

- **Recompute `complete` after the plan so a missing source file marks the
  sync partial** (claude-code MED). Declined: `complete` is defined by the ADR
  as *entitlement scope* (did the caller request everything it's entitled to),
  not physical file existence. `test_core_manifest.py` CI-guarantees every
  source manifest entry exists on disk, so this case **cannot occur for a real
  kit source**; a hand-crafted broken source is already surfaced by a warning
  (exit 1). The proposed change would set a *sticky* `partial_sync` on the
  consumer driven by an upstream anomaly — worse than the warning path.
- **`str.removesuffix` breaks Python 3.8** (o3). Declined: the project requires
  Python 3.10–3.12 (pyproject/CLAUDE.md), and DK001 *mandates* `removesuffix`.
- **`_rel_path` fall-through for a future tier** (fast, o3). Declined:
  the `else: return entry` branch *is* the intended `kit_builder` (root-relative)
  behavior. A future tier needing a different base adds an explicit `if` — this
  is the KIT-0026 fast-follow, not a bug.
- **`os.chmod` may raise on Windows non-admin** (o3). Covered by the new
  `main()` `OSError` catch (clean exit rather than traceback).
- **Overlapping dir + file manifest entries are undefined** (o3). Declined for
  PR 1: no overlap exists in the manifest and entries are upstream-controlled;
  detection is scope creep. Noted as a possible future validator.
- **Staging dir visible to git / `--report-json` arbitrary path** (claude-code
  LOW). Declined: the `finally` cleans staging even on exception (and a hard
  failure stops the workflow before `git add`); `--report-json` is operator
  tooling and the workflow passes a fixed relative path.
- **`sys.path.insert` in the test is fragile** (claude-code LOW). Declined:
  consistent with the existing repo pattern (`test_pattern_lint.py`).

## Confirmed clean by evaluators (POSITIVE)

Two-pass atomic apply; safe self-overwrite on POSIX; `opted_in` preservation;
frozen exit-code contract with tests; scoped `git add`; randomized
`GITHUB_OUTPUT` delimiter; corrupt-target-manifest loud-fail; no hardcoded
secrets; per-repo workflow concurrency; library-first design; documentation.
