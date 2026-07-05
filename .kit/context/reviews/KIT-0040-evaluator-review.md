# KIT-0040 — Adversarial Evaluator Review

**Date**: 2026-07-05
**PR**: #70 (`feature/KIT-0040-kit-0034-retro-followups`)
**Input**: `.adversarial/inputs/KIT-0040-code-review-input.md`
(full diff + file contents vs `main`, regenerated after the round-1 fixes)

| Evaluator | Model | Verdict | Log |
|-----------|-------|---------|-----|
| `code-reviewer-fast-v2` | gemini-3-flash-preview | CONCERNS | `.adversarial/logs/KIT-0040-code-review-input--code-reviewer-fast-v2.md` |
| `code-reviewer` | o3 | CONCERNS | `.adversarial/logs/KIT-0040-code-review-input--code-reviewer.md` |
| `claude-code` | claude-sonnet-4-6 | **APPROVED** | `.adversarial/logs/KIT-0040-code-review-input--claude-code.md` |

## Triage (verify-before-believing applied to every finding)

### code-reviewer-fast-v2 (4 findings)

1. **File-name collision in `_sync_coordination_metadata`** — *non-issue*.
   The evaluator's own trace concludes the full-file-name constraint makes
   the substitution correct; rewriting every mention of the moved task's
   exact path is the intended sync behavior
   (`test_move_leaves_other_tasks_untouched` covers the collision case).
2. **Non-numbered custom folder names not rewritten** — *declined, by
   design*. The conservative `[0-9]+-[a-z-]+` scope was an explicit
   handoff requirement; `project move` can only write numbered folders
   from `STATUS_FOLDER_MAP`, so tooling-written paths always match.
3. **`\b` prefix collision on hyphenated marker names** — **REAL BUG,
   FIXED** in `dca46c8`. `_begin_marker_line_re("project-context")`
   matched a well-formed `project-context-extra` BEGIN line (word
   boundary at the `t→-` transition), falsely aborting merge as
   malformed. Name terminator changed from `\b` to `(?!-?\w)`; regression
   test `test_prefix_named_region_does_not_trip_malformed_check`.
4. **Line-anchored marker examples in docs still abort** — *declined,
   documented trade-off*. See o3 finding 1 below.

### code-reviewer / o3 (3 findings)

1. **Fenced code-block marker line → "malformed" abort** — *declined,
   deliberate fail-fast trade-off*. Mechanically true: a literal BEGIN
   marker line inside a fenced code sample, with no parseable region for
   that name, raises ValueError. This is the explicitly chosen behavior
   (loud abort with a clear message beats silently clobbering consumer
   content — the exact bug F3 fixes), the same input aborted before this
   PR too (raw substring check), and parsing Markdown fences is out of
   scope for a stdlib helper. Documented in `_begin_marker_line_re`'s
   docstring.
2. **EOF without trailing newline breaks region parsing** — **VERIFIED
   FALSE**. Empirical check: a file ending exactly at
   `<!-- END KIT-LOCAL: foo -->` (no final newline) parses and extracts
   correctly. The `\r?\n` in `_region_pattern` is the body/END-marker
   separator, not a trailing-newline requirement.
3. **Metadata regex clobbers non-path prose** — **VERIFIED FALSE as
   stated**. The pattern requires the full `.kit/tasks/<folder>/` prefix;
   the evaluator's own example (bare `KIT-1234-sample-task.md` in a note)
   does not match. Full-path mentions being rewritten to the new folder
   is the intended behavior (path references should track the move).

### claude-code (security)

APPROVED, no findings to triage.

## Outcome

One real finding across all three evaluators (fast-v2 #3), fixed with a
regression test before this review was persisted. o3 produced two
factually wrong claims (consistent with the KIT-0034 retro's
verify-before-believing observation). Final code: 408 tests green,
`ci-check.sh` green.
