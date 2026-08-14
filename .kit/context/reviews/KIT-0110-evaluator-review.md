# KIT-0110 — Evaluator Review Record (PR 1, kit repo)

**Date**: 2026-08-14
**Agent**: feature-developer-f5
**Diff shape**: logic (new tool + tests) → full trio, `--format full`
**Input**: `.adversarial/inputs/KIT-0110-code-review-input.md`
(commit `1426ec3`)

## Verdicts

| Evaluator | Model | Verdict |
|---|---|---|
| code-reviewer-fast | gemini-2.5-flash | CONCERNS |
| code-reviewer | o3 | FAIL |
| claude-code | claude-sonnet-4-6 | APPROVED |

Logs: `.adversarial/logs/KIT-0110-code-review-input--{code-reviewer-fast,code-reviewer,claude-code}.md`

## Dispositions (every finding verified against code before acting)

### Actioned

1. **`_entry_bounds` unanchored matching** (claude-code, LOW —
   CONFIRMED latent): a `why: >-` continuation line beginning
   `- name:` could open/close an entry early. Fixed: both start and
   end matches are now anchored to the roster's 2-space list indent;
   regression test `test_entry_bounds_ignores_lookalike_in_why_text`.
2. **Missing `git` binary → raw traceback** (kernel of o3 F2):
   `subprocess.run` raises `FileNotFoundError` uncaught. Fixed: both
   `_git()` and `merge_three_way()` convert it to a named
   `ResyncError` ("git is not on PATH"), caught by the `main()`
   wrapper → clean `EXIT_INTEGRITY`.
3. **`_spec is None` on the guard import** (claude-code, LOW): now an
   explicit `ImportError` naming the path.
4. **`ResyncError` escaping `main()` as traceback** (self-review,
   pre-trio): `main()` wraps `_main()` and converts to
   `EXIT_INTEGRITY`.

### Refuted (with reason)

1. **o3 F1 "indented `version:` frontmatter silently ignored"** — an
   indented `version:` is not a top-level YAML key; the zero-indent
   regex matches the only legal form. The cited "legal YAML with
   optional indentation" is not legal YAML for a mapping key.
2. **o3 F2 as stated ("merge-file rc=1 with empty stdout classified as
   conflict")** — rc 1 means exactly 1 conflict by the documented
   contract, and conflict output always carries the merged content;
   the only real failure shape (missing git binary) is fixed above.
3. **o3 F3 "spaces/control chars in source reach git"** — list-arg
   subprocess, no shell; git receives the pathspec literally. A
   nonexistent path fails the rev walk → loud base-not-found, never
   silent.
4. **fast F1 `plugin_body_relpath` KeyError** — `name` is guaranteed
   by the guard's `_validate_components` before any call.
5. **fast F4 / claude-code "YAML injection via set_entry_field"** —
   evaluator self-refuted: hashes are hex-only, `kit_version` is
   quoted, the version regex excludes quotes/newlines.

### Declined (out of contract, recorded)

1. **CRLF preservation on roster rewrite** (o3) — the roster is
   LF-committed in movito/agentive-skills; newline-convention
   detection is speculative surface.
2. **History-walk depth limit** (claude-code) — infrequent local tool;
   walk length is bounded by per-file commit count.
3. **4-space field indent assumption** (claude-code) — the roster's
   established format is the tool's documented contract; the guard's
   parser and this tool share it.
4. **Import-time `exec_module` of the guard** (claude-code, MEDIUM) —
   the guard is `__main__`-guarded with no module-level side effects;
   the pattern is the kit's established scripts/local convention
   (same load in `tests/test_plugin_drift.py`).

## Known blind spot note

No CSS/dual-render surface in this diff; the known evaluator blind
spot does not apply.
