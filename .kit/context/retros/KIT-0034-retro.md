## KIT-0034 — Preflight & Bootstrap Hardening (PR #69)

**Date**: 2026-07-05
**Agent**: feature-developer-f5
**Mode**: single-repo
**Scorecard**: 7 threads, 0 regressions, 3 fix rounds, 6 commits

### What Worked

1. **Data-shape verification before coding the Gate 2 fallback** — the
   handoff's instruction to capture real `gh` output first surfaced the
   decisive fact in ~2 minutes: CodeRabbit reports via the legacy
   commit-status API (`context: "CodeRabbit"`), NOT check-runs. The task
   spec said "check-run is passing"; coding to the spec's words would have
   produced a fallback that never fires. Status is now the primary source,
   check-runs secondary.
2. **Stub-`gh` scenario matrix for a script with no test harness** — a
   throwaway `gh` shim on PATH (`/tmp/kit0034-stub/`) let the *real*
   `preflight-check.sh` run against 8 canned states (fallback PASS,
   no-review FAIL, unresolved-thread FAIL, CHANGES_REQUESTED, check-run
   source, N3 precedence, gh-error FAIL, empty-fetch PENDING). Re-ran in
   seconds after every bot fix. This is the cheapest credible verification
   for shell+gh gate logic and is worth codifying (see Should Change).
3. **Verify-before-believing on evaluator findings paid for itself** —
   o3's FAIL verdict contained 3 factually wrong claims (combined-status
   endpoint dedups per context; `str.split()` handles `\r`; `[^)]*`
   crosses newlines) and 1 pre-verified non-issue (exit code 2 callers).
   Checking each against docs/behavior took minutes and prevented ~4
   pointless "fixes", while still extracting 6 real hardening items.
4. **Shared PR_DATA snapshot fell out of reuse guidance** — the handoff's
   "reuse Gate 4's query" nudge became one GraphQL fetch for Gates 2/3/4,
   which eliminated the possibility of the fallback and the thread gate
   disagreeing mid-run (a race the original design allowed) and cut 3 API
   calls to 1.
5. **Batched thread fixes per round** — CodeRabbit round 1 (4 threads: 2
   stale paths + 2 script findings) landed as one commit with 4
   replies/resolves; total bot loop was 3 rounds, ~25 minutes wall-clock,
   ending in CodeRabbit APPROVED.

### What Was Surprising

1. **PR #58 — the canonical false-negative case — had drifted**: it now
   carries 2 unresolved medium-severity BugBot threads on
   `kit_markers.py` (opened at merge time), so it could no longer serve
   as the clean verification target the task spec assumed. PR #63 (the
   second recorded case) had the clean shape and was used instead.
   Lesson: retro-referenced PRs are snapshots, not stable fixtures.
2. **The final bookkeeping push live-demonstrated the fix** — the
   docs-only `da0b2dd` head recreated the exact scenario class that
   false-negatived three tasks running, and preflight passed all 7 gates
   on its own PR (Gate 2 matched CODE_SHA via the primary path).
3. **Bots kept finding real consistency gaps in freshly reviewed code** —
   round 2 (CodeRabbit: `|| true` made gh errors masquerade as PENDING)
   and round 3 (BugBot: check-run fallback used `tail -1` while the
   status branch required all-green) were both genuine, non-cosmetic
   findings in code that three evaluators had already reviewed. The
   bot rounds are not redundant with the evaluator gate.
4. **CodeRabbit re-flags bookkeeping paths on every status move** — the
   round-1 "stale 2-todo path" finding would have recurred for
   3-in-progress → 4-in-review; updating handoff metadata in the same
   commit as the task move preempted a round-4 nitpick.

### What Should Change

1. **Codify the stub-`gh` harness** — F5 was the "automatable part," but
   the throwaway shim proved gate logic is testable too: a pytest that
   puts a fake `gh` on PATH and runs the real script against canned
   states would turn this task's manual matrix into regression coverage.
   Candidate follow-up task; keeps N2 (script stays shell + gh).
2. **Task specs should record observed API shapes, not paraphrases** —
   "CodeRabbit's check-run is green" in the spec was wrong in a way that
   mattered (it's a commit status). When a spec names a bot/API signal,
   the planner should paste the actual query + one line of real output
   into the spec or handoff.
3. **Move task + update handoff metadata atomically** — `project move`
   changes the folder but not `details_link` in agent-handoffs.json or
   handoff files; CodeRabbit flags the drift within minutes. Either
   `project move` should rewrite known metadata paths, or the commit
   protocol should pair them explicitly.
4. **Planner: triage PR #58's 2 stale BugBot threads** — medium-severity
   findings on `kit_markers.py` (BEGIN-substring false positive;
   whitespace marker clobber), unresolved since the KIT-0033 merge.
   Resolving them opportunistically here would have been dishonest
   thread hygiene; they need a real look.

### Permission Prompts Hit

None.

### Process Actions Taken

- [ ] Create follow-up task: pytest harness for `preflight-check.sh` gate
      logic via PATH-stubbed `gh` (turns this session's manual scenario
      matrix into CI regression coverage)
- [ ] Planner: triage the 2 unresolved BugBot threads on merged PR #58
      (`scripts/local/kit_markers.py`)
- [ ] Consider making `./scripts/core/project move` rewrite task paths in
      `.kit/context/agent-handoffs.json` + handoff files, or document the
      pairing in COMMIT-PROTOCOL.md
- [ ] Planner: when a spec cites a bot/CI signal, include the verified
      API query + sample output (KIT-0034 F1 said "check-run"; reality
      was a commit status)
