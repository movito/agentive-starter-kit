## KIT-0071 — Worktree Provisioning Correctness (PR #96)

**Date**: 2026-07-27
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 11 threads, 4 regressions, 6 fix rounds, 9 commits

### What Worked

1. **Evaluator-before-PR + reproduce-or-refute** — the deep reviewer's
   FAIL headline ("`venv/` + `--force` will rm -rf the primary through
   the symlink") was refuted with a 10-line reproduction: `shutil.rmtree`
   refuses symlinks with `[Errno None]` — which is literally the
   KIT-0065 symptom from the spec. Same round, its `name:`-key claim was
   CONFIRMED against `scripts/core/project:429` and fixed. Verifying
   both directions prevented churn and caught a real parity bug pre-PR.
2. **Live-demo acceptance criteria** — the `venv --clear` transcript
   (fresh worktree venv 167→2 site-packages entries, primary 170→170
   untouched) is stronger evidence than any fixture test; re-provisioning
   my own hazardous worktree as the demo (doctor WARN → setup refusal →
   `rm .venv` + setup → all-PASS → 815 tests green through the new venv
   on Python 3.14) exercised every new surface end-to-end.
3. **The existing suite caught the live hazard by accident** —
   `TestPythonVersionCheck` runs `cmd_setup` in-process against the real
   repo root, so my new symlink guard fired on THIS worktree's real
   symlinked `.venv` and failed 5 tests. Annoying for a minute,
   then valuable: it proved the guard fires on exactly the state the
   task exists to kill.
4. **Inline ScheduleWakeup Phase 6 loop** — 9 polls at 270 s (cache-warm),
   6 fix rounds, zero sub-agents, zero busy-waits. The loop absorbed an
   11-thread review storm without losing state.

### What Was Surprising

1. **BugBot's check-status lies in BOTH directions** — it reported
   `skipping` for five consecutive scans while actively posting Medium-
   severity threads (and posted its round-1 thread DURING a `skipping`
   status), then flipped to `pass`. KIT-0062 F6 documented
   skipping-as-masked-terminal; this session shows the inverse too:
   the status field carries no signal — the threads are the truth.
2. **One class, five findings, four rounds too many** — bot rounds 2–6
   were all faces of ONE defect class: "a displayed remedy command is a
   contract — complete, root-scoped, quoted, note-as-comment, on every
   surface." I fixed instance-by-instance (prose → root-scope →
   shell-comment → %q → third surface), a textbook regression of
   KIT-0069's `fix_by_class_not_instance` pattern, freshly shipped to
   patterns.yml. Counting rounds 3–6 as regressions: 4.
3. **Pre-commit aborted with a green pytest tail, and push said
   "Everything up-to-date"** — the handoff commit died on
   validate-task-status (Status: Todo in 4-in-review, because my Edit
   to the just-`git mv`-ed path failed on the read-before-edit rule)
   while the hook tail printed `786 passed`. The KIT-0057 rule
   (`git log -1` + `git status` after every commit, never trust the
   tail) caught it in one step.
4. **A provisioning helper cannot demo its own payload pre-merge** —
   the fresh-worktree demo invoked the CHECKOUT's `project setup`
   (origin/main's old copy), which ignored `--no-hooks` and attempted a
   hook install (failed non-critically — had it succeeded it would have
   re-pointed the primary's shared hooks, confirming exactly why the
   flag exists). Inherent: the helper runs from the new branch, the
   payload comes from origin/main until merge.

### What Should Change

1. **patterns.yml: `displayed_commands_are_contracts`** — any echoed
   remedy/recovery command must be: complete (no embedded prose),
   root-scoped (`cd <root> &&`), `%q`/`shlex.quote`-escaped, rationale
   as a trailing `#` comment, and pinned by a `bash -n` parse test of
   the actual output. When ONE such finding lands, grep every
   `echo`/`print` carrying `&&`, `cd `, or `rm ` repo-wide and fix the
   class in one round — this session's rounds 3–6 were the cost of not
   doing that at round 2.
2. **Codify worktree-mode handoff bookkeeping** — preflight Gates 5–7
   read from cwd, which forces the branch to carry the task-move +
   review starter, while the primary needs a mirrored working-tree move
   for the planner. I derived this both-trees answer live; it belongs in
   WORKTREE-WORKFLOW.md (Closeout) or TASK-COMPLETION-PROTOCOL so the
   next fd doesn't re-derive it. Includes the stray-file note: after
   merge, the primary's untracked 4-in-review copy duplicates the merged
   file — planner deletes the stray.
3. **Extend KIT-0062 (bot-scope task) with the status-lies-both-ways
   data point** — Gate 2/3 logic and the bot-triage skill should treat
   BugBot's check-run status as advisory only and always fetch threads;
   this session's Gate 3 PASS ("check-run passed, no findings") was
   printed about a PR that BugBot had filed four threads against.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Add `displayed_commands_are_contracts` to `.kit/context/patterns.yml`
      (planner; wording in What Should Change #1)
- [ ] Add worktree-mode handoff bookkeeping (branch carries move+starter,
      primary mirrors, stray-file cleanup) to WORKTREE-WORKFLOW.md Closeout
- [ ] Feed the BugBot status-lies-both-ways observation into KIT-0062
- [ ] Planner closeout: commit primary-side bookkeeping (task move,
      handoff-file path updates, this retro), delete the stray task copy
      after merge, remove worktree post-retro (untracked venv/Serena
      artifacts regenerate — `--force` expected), delete branch

### Incident Closure

1. **BugBot status unreliable both directions** — triage-guide entry:
   rides KIT-0062 (bot-scope task, action above); detection is only
   possible at review time, so a doctor check does not fit.
2. **Pre-commit abort under green tail (validate-task-status face)** —
   already closed by the existing fd Phase 5 rule (KIT-0057/KIT-0066:
   verify `git log -1` + `git status` after every commit); this session
   is a third confirming instance, no new mechanism needed.
3. **Provisioning payload is the checkout's script until merge** —
   not-checkable note: documented in
   `.kit/context/reviews/KIT-0071-evaluator-review.md` ("Known blind
   spots"); transient by construction (resolves at merge), not worth a
   doctor check.
4. **The `.venv` symlink class itself** — closed by THIS task's doctor
   check (`doctor.d/55-worktree-provisioning.sh`, KIT-0065/KIT-0069
   cited in the header) plus the `cmd_setup` guard and helper fix.
