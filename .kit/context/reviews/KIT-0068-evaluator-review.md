# KIT-0068 Evaluator Review Record

**Date**: 2026-07-24
**Input**: `.adversarial/inputs/KIT-0068-code-review-input.md`
(full-format, 14,392 lines — diff + full contents of all 32 changed files)
**Ordering**: trio run BEFORE PR open (KIT-0035/KIT-0046 rule).
`git status` verified clean after every run.

## Verdicts

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast-v2 | gemini-3-flash-preview | CONCERNS |
| code-reviewer | o3 | FAIL |
| claude-code | claude-sonnet-4-6 | APPROVED |

## Triage — code-reviewer-fast-v2 (CONCERNS, 4 findings)

1. **Regex fallback fragility** (`_get_evaluator_library_version`) —
   ACCEPTED in part: added `^\s*` indent tolerance to the 3.10 regex
   fallback. The "fails inside [tool.adversarial] table" claim was
   wrong (`re.MULTILINE` + `^` matches any line start), but the
   tolerance is free. Its "missing VERSION file untested" side-claim
   was false — `test_version_missing_file_fails_loud` exists.
2. **new-worktree.sh guard race / broken symlink** — DECLINED:
   single-operator tool, no concurrent provisioning path; a broken
   symlink is caught by the `-L` test and refused loudly, which is the
   designed behavior.
3. **Linear task-ID first-match collision** — DECLINED: first-match
   semantics are unchanged from the old TASK-|ASK- code; a filename
   with two IDs is operator error the sync surfaces in Linear.
4. **`_flake8_args` is a change detector** — DECLINED: byte-matching
   is the point (A91 — the header claims a CI mirror). A stylistic
   shell change that breaks the parse fails loudly and names the pair.

## Triage — code-reviewer / o3 (FAIL, 6 findings)

1. **`--ref` cannot override a missing pyproject pin** — REAL, FIXED:
   `cmd_install_evaluators` called the pin reader before parsing
   `--ref`, so on planning-shape repos (no pyproject.toml) the command
   died even though its own error message says "pass --ref". Now
   `--ref` is parsed first and the pin reader only runs without it.
   Regression test: `TestRefBypassesPinRead`.
2. **Planning shape cannot install evaluators** — same root cause as
   #1; with the fix, `--ref` works and the no-flag path fails loud
   with the actionable `--ref` hint (spec F7's intended behavior —
   the old code silently installed v0.5.3 instead).
3. **`--flag=value` unsupported in cmd_sync** — OUT OF SCOPE:
   `cmd_sync` is untouched by this diff (full-file input exposed
   pre-existing code to review). Candidate for a backlog note.
4. **4-digit exclude misses KIT-10000** — REFUTED: the patterns are
   rsync GLOBS, not regex; the trailing `*` matches any suffix
   including a fifth digit.
5. **`_check_declared` 30-line header scan** — OUT OF SCOPE:
   pre-existing doctor driver code, untouched by this diff.
6. **Root-level `.kit/tasks/KIT-0001.md` leaks** — REFUTED: the edit
   added a root-level exclude (`tasks/[A-Z]*-[0-9][0-9][0-9][0-9]*`)
   alongside the nested one; the reviewer missed the second line.

o3 track record note upheld: verdict label carries no signal — of six
findings, one was real, two refuted by reading the code, two out of
diff, one duplicate. The one real find (a bug in THIS diff's new code)
justifies the run.

## Triage — claude-code (APPROVED)

MEDIUM findings (unquoted `$PY_FILES` in the pattern-lint step,
`tarfile.extractall` filter deprecation) are pre-existing code outside
this diff; flagged as follow-up candidates, non-blocking. No findings
against the new code.

## Post-review changes

- `scripts/core/project`: `--ref` parsed before pin read; regex
  fallback tolerates leading whitespace.
- `tests/test_project_script.py`: `TestRefBypassesPinRead` added.
