# KIT-0044 — Adversarial Evaluator Review

**Date**: 2026-07-14
**Input**: `.adversarial/inputs/KIT-0044-code-review-input.md` (full-file, 8 files, ~17.5k tokens)
**Ordering**: evaluators run BEFORE PR open (doc-dominated rule, KIT-0035 F3)

| Evaluator | Model | Verdict |
|-----------|-------|---------|
| code-reviewer-fast-v2 | gemini-3-flash-preview | CONCERNS |
| code-reviewer | o3 | CONCERNS |
| claude-code | claude-sonnet-4-6 | APPROVED |

Raw logs: `.adversarial/logs/KIT-0044-code-review-input--*.md.md`

## Disposition

| # | Finding (source) | Disposition | Evidence / change |
|---|------------------|-------------|-------------------|
| 1 | Multiple task specs for one ID → first glob hit wins (o3 + claude-code, convergent) | **ACCEPTED** | Helper now collects all matches and refuses with the file list when >1 (tested live with a temp duplicate: clean error, exit 1) |
| 2 | `PRIMARY_ROOT` dirname math silently wrong for a bare primary (claude-code, MEDIUM) | **ACCEPTED** | Guard added: refuse if `$PRIMARY_ROOT/.git` doesn't exist — thematically apt given the pilot's core.bare damage |
| 3 | No friendly error when `origin/main` missing after fetch (claude-code, LOW) | **ACCEPTED** | `show-ref --verify refs/remotes/origin/main` guard with actionable message |
| 4 | Unmatched glob passes literal string into loop (fast-v2) | **ACCEPTED (already mitigated)** | `[ -f "$f" ]` made the original safe (the "corrupted SLUG" claim was wrong), but the evaluator's nullglob edit is clearer — kept. Note: the aider-based evaluator APPLIED this edit to the working tree itself; see review note below |
| 5 | Git < 2.43 lacks `--path-format` → hard fail (o3) | **DECLINED — disproven** | `--path-format` landed in git 2.31; verified live on git 2.39.2: `git rev-parse --path-format=absolute --git-common-dir` succeeds |
| 6 | Nested-worktree invocation resolves `PRIMARY_ROOT` "one level too high" (o3) | **DECLINED — disproven** | `dirname /repo/.git` = `/repo`, which is correct, not "too high". Verified from both primary and worktree: common-dir → `<primary>/.git`, dirname → primary root. The helper was exercised live from inside the KIT-0044 worktree and symlinked correctly |
| 7 | `ln -s` "File exists" on re-run after partial deletion (o3) | **DECLINED — structurally impossible** | Any pre-existing worktree path is refused before `ln` can run; `dst` lives inside the just-created worktree, so it cannot pre-exist |
| 8 | Script invoked via symlink from `~/bin` corrupts paths (fast-v2) | **DECLINED — fails safe** | If `SCRIPT_DIR` is outside the repo, `git -C "$SCRIPT_DIR" rev-parse` errors and `set -e` aborts — loud failure, not corruption. Invocation convention is `./scripts/local/…` (same pattern as `bootstrap-consumer.sh`) |
| 9 | Slug prefix-strip wrong if TASK-ID appears elsewhere in filename (fast-v2) | **DECLINED — structurally impossible** | The glob `"$TASK_ID"-*.md` guarantees the basename starts with `TASK_ID-`; `${SLUG#…}` strips exactly that anchored prefix |
| 10 | `mkdir -p` failure yields generic error (fast-v2) | **DECLINED — acceptable** | `set -e` aborts before any mutation beyond the worktree; local operator tool, generic OS error is sufficient |
| 11 | Broken-symlink provisioning source (fast-v2) | **DECLINED — handled** | `[ ! -e "$src" ]` follows symlinks, so a broken source hits the warn-and-skip path |
| 12 | `trap ERR` + `continue` interplay (claude-code, LOW) | **DECLINED — no change per reviewer** | Reviewer's own remediation: "No change required; behavior is correct" |
| 13 | `.gitignore` scope widening to files named `evaluators` (claude-code, LOW) | **DECLINED — acknowledged** | Intentional; the in-file comment covers it (reviewer agreed no change needed) |

## Review notes

- **Evaluator mutated the working tree**: `code-reviewer-fast-v2` (aider-based)
  *applied* its nullglob SEARCH/REPLACE edit directly to
  `scripts/local/new-worktree.sh` during the review run ("Applied edit to…"
  in the log), despite the input file being added read-only. The edit was
  benign and kept, but evaluator runs must be followed by a `git status`
  check. Filed as a retro item.
- **`ADVERSARIAL_UNATTENDED` does not exist**: all three first-round runs
  died on the interactive large-input prompt (`EOFError` under non-TTY).
  The env flag advertised by `prepare-review-input.sh` 1.5.0 appears
  nowhere in the installed library source (verified by grep of the
  package). Fixed in 1.5.1: the hint now prescribes `echo y |` piping.
  Related upstream: movito/adversarial-workflow#74.
