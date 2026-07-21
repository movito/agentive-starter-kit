## KIT-0057 — Canonical Homes + the Prune, ADR-0027 P6 (PR #90)

**Date**: 2026-07-21
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 5 threads, 0 regressions, 1 fix round, 9 commits

### What Worked

1. **Self-review caught the pull-sync symlink seam before any bot
   did** — the planned dir-level symlinks (`.kit/skills/<name>` →
   canonical) would have been invisible to
   `sync_from_manifest._read_dir` (rglob + `is_file()` does not
   descend into symlinked directories), making a kit_builder pull-sync
   read the path as empty and deletion-prune consumer copies. Switched
   to real dirs holding file-level `SKILL.md` symlinks and pinned the
   property with `test_sync_engine_reads_content_through_old_path`.
   The "data flow: does the shape match what consumers expect"
   checklist item earned its keep on a filesystem shape, not a JSON
   one.
2. **Evaluator-trio-before-PR again bought a light bot cycle** — 2
   rounds, 5 threads, exactly 1 substantive external fix. The o3 FAIL
   was fully triaged pre-PR (see 3), so the PR opened with the review
   record already answering the plausible objections.
3. **Verify-before-believing held against a hard o3 FAIL** — all six
   findings checked against code before acting: the two "correctness"
   claims quoted behavior the code does not have
   (`_dirty_touched_paths` explicitly collects both rename sides,
   lines 1153-1157; the door `die_usage`s on a conflicting `--bots`
   and never appends a second line). Refuted in the review record with
   line citations, zero churn. o3 FAIL track record is now 3 real
   blockers vs 2 full refutations — the verdict alone carries no
   signal; the code check is mandatory.
4. **Fixture-table conformance harness passed first run** — all 13
   rows × 3 readers agreed immediately, which is itself the finding:
   KIT-0056's pairwise pins had already converged the readers; the
   harness turns that state into a ratchet. Reusing the real harnesses
   via cross-module import (`from test_preflight_check import proj`)
   avoided duplicating the stub-gh machinery.
5. **Inventory-before-move (the ADR's F1 gate) made the merge
   boring** — every reference was known and dispositioned before the
   first `git mv`; post-move greps found nothing unplanned.

### What Was Surprising

1. **Pre-commit aborted two commits AFTER pytest passed** — black and
   isort rewrote the brand-new test files mid-hook, failing the run
   while the 70-second pytest-fast hook still completed and printed
   "N passed" as the last output. Both times the tail looked like
   success and the commit had not landed; worse, the first abort's
   stash/restore dance silently deleted the freshly created untracked
   symlinks. Lesson applied mid-session: run `black`/`isort` on new
   files before `git commit`, and verify `git log -1` after any hook
   run that modified files.
2. **BugBot found the one real gap: the SECOND seeding path** — F2
   reset the target name in `engine-export.sh` (--new) and I
   characterized it, but `engine-consumer.sh`'s top-level-file copy
   (adopt) also seeds `pyproject.toml` and would have handed fresh
   adopters `name = "agentive-starter-kit"`. Same bug class fixed
   once and missed once in the same PR — renames must be chased
   through EVERY path that copies the renamed file, not just the one
   the spec names.
3. **The consumer-boundary inventory assertion is one-directional** —
   `EXCLUDED_TESTS` in `test_bootstrap_consumer.py` verifies inventory
   ⊆ engine, so adding `test_bots_conformance.py` to the engine
   excludes without the inventory passed silently until CodeRabbit
   flagged it.
4. **zsh equals-expansion eats bare `===` separators** — `echo ===`
   in a compound Bash call dies with "== not found" and aborts the
   remainder of the command. Quote separator strings.

### What Should Change

1. **Identity-rename checklist rule** — when a task renames an
   identity-bearing file's content, grep every `cp`/`rsync`/heredoc
   that ships that file (`grep -rn 'pyproject.toml' scripts/`) and
   characterize EACH seeding path, not just the one in the spec. One
   grep would have pre-empted BugBot's round-1 finding.
2. **Pre-format new files before committing** — add to the
   feature-developer workflow (Phase 5): run `black`/`isort` on
   new/edited Python files before `git commit`, and after ANY
   pre-commit run that reports a mutating hook failure, confirm with
   `git log -1` + `git status` before proceeding (the pytest-passed
   tail reads as success, and the stash dance can drop untracked
   files created between staging and commit).
3. **Make the consumer-boundary inventory bidirectional** — extend
   `TestConsumerTestsRsyncBoundary` to also parse the engine's
   exclude list and assert engine ⊆ inventory, so the next engine-only
   addition fails loudly instead of waiting for a bot.
4. **Two noted observations need planner calls** — (a) the
   consumer-manifest seed heredoc bakes `core_version 2.0.0` dated
   2026-03-29 (self-healing via first sync, but its baked file list
   can mask newer files under KIT-0049 intersection semantics — same
   class F3 just closed for the planning heredoc); (b) `pyproject.toml`
   `description` still carries the template TODO after the name fix.

### Permission Prompts Hit

None — the full session (moves, symlinks, evaluator runs, GraphQL
mutations, pushes) ran without a single permission stall.

### Process Actions Taken

- [ ] Add identity-rename grep rule to the self-review skill (change 1)
- [ ] Add pre-format + post-hook-verify step to feature-developer Phase 5 (change 2)
- [ ] File the bidirectional-inventory extension (change 3)
- [ ] Planner: disposition the consumer-manifest 2.0.0 seed + description TODO (change 4)
- [ ] Planner arc-end actions on merge: 0.9.0 cuttable (KIT-0047+0054+0059), `rm -rf` allowlist reminder (third recurrence), downstream migration pass starts

### Incident Closure

1. **Pre-commit abort masking (linter-modified new files)** —
   triage-guide entry: documented here and queued for
   `.kit/context/workflows/COMMIT-PROTOCOL.md` via process action 2
   (symptom: pytest-fast "passed" tail + no new commit; cause: earlier
   mutating hook failed the run; check `git log -1`). Not cheaply
   doctor-checkable (it is a transient hook interaction, not an
   environment state).
2. **Dir-symlink invisibility to `_read_dir`** — closed structurally:
   the repo shape avoids it and
   `test_sync_engine_reads_content_through_old_path` pins the
   working shape permanently. No doctor check needed — the guard test
   IS the check, running in every CI cycle.
3. **zsh `===` equals-expansion** — not-checkable note: shell
   idiosyncrasy in the agent's own tooling, not project environment;
   recorded here as the triage note (quote separators in compound
   commands).
