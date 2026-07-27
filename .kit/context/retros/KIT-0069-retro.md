## KIT-0069 — Audit truth sweep: every live surface tells the truth (PR #95)

**Date**: 2026-07-27
**Agent**: feature-developer
**Mode**: single-repo
**Scorecard**: 6 threads, 6 regressions, 1 fix round, 8 commits

Merged `1bdceac` 2026-07-27T14:24:48Z. 54 owned findings: 47 fixed,
2 already-fixed by KIT-0068 (verified, not assumed), 2 refuted by
measurement, 3 deferred. Spawned KIT-0072.

**Post-merge correction**: the planner's 8-agent tree-verification
(`c120538`, record `.kit/context/reviews/KIT-0069-TREE-VERIFICATION.md`)
confirmed 54/57 dispositions and COMPLETE coverage of all 54 owned
A-numbers, but found **3 more sibling-instance residuals** I missed. The
regression count above is 6, not 3: three found by CodeRabbit, three by the
verification — **all six the same failure mode**. Details in "What Was
Surprising" #5. This retro was revised after that verification rather than
shipped with the flattering number.

### What Worked

1. **Fix-by-class beat fix-by-instance, measurably.** F1's "grep the class
   repo-wide" found roughly 15% more sites than the audit's 92-finding
   instance list: `.env.template:41,63` (in no finding at all), the project
   script's own bare `./project <cmd>` help form (invisible to a
   `scripts/project` pattern), prose mentions of "procedural index" with no
   filename, and two stale evaluator log-path citations. An audit
   enumerates instances; only a class grep closes a class.

2. **`replace_in_files` dry-run prevented corrupting the evidence base.**
   The `AGENT-TEMPLATE.md` path sweep matched **26 occurrences across 10
   files; only 6 should change**. Among the 20 that must not: the
   cruft-audit record itself, which quotes the stale paths *as evidence*. A
   blind `sed -i` repo-wide would have rewritten the audit and inverted its
   before/after quotes — silently, and plausibly enough to survive review.
   Dry-run-then-select is the right tool for any class spanning live
   surfaces and historical records.

3. **Verifying model IDs against the live API rather than any cached list.**
   Three sources disagreed: the harness environment block, the bundled
   `claude-api` skill catalog (cached 2026-06-04), and project memory.
   `GET /v1/models` settled it — `claude-opus-5`/`claude-sonnet-5` are
   current; `claude-sonnet-4-20250514` and `claude-3-5-haiku-20241022` are
   retired. Memory was right and both cached sources were stale. Hardcoded
   per-token prices were **removed** rather than guessed, since IDs were
   verifiable and 5-series pricing was not.

4. **Writing the implementation notes during the work, not after.** The
   planner had already actioned §2/§3/§4 (`dbe687f`, widening KIT-0071 to
   the worktree-provisioning class plus an evidence-append-only rule)
   before this retro was written. Notes written live are actionable;
   notes reconstructed afterwards are anecdote.

### What Was Surprising

1. **`rg` is not trustworthy in this repo — two distinct false-empty
   modes.** (a) It skips hidden directories by default, and nearly every
   kit surface lives in one (`.kit/`, `.claude/`, `.adversarial/`,
   `.serena/`). The first ghost-citation sweep returned **zero hits across
   four patterns** on a class that actually had 20+ live citations — that
   would have shipped as "already fixed by #93/#94". (b) Later, `rg
   --hidden` with multiple `-e` patterns and several `-g` excludes returned
   zero on a pattern `grep -Rn` matched in four files. A third variant of
   the same trap: `find` does not follow symlinks without `-L`, and
   `.adversarial/evaluators` is a symlink, so a plain `find` reported
   installed evaluators as missing.

2. **The evaluator trio scored 0-for-7; CodeRabbit scored 6-for-6.**
   `code-reviewer-fast` FAIL (1 finding, refuted — it reasoned about
   `scripts/.core-manifest.json`, a file not in the diff). `claude-code`
   could not run at all (Anthropic API credit balance). `code-reviewer`
   (o3) FAIL with 6 findings, **none of which reproduce** — it asserted
   `delegation/` scanning in two files containing zero occurrences of that
   string, and two diverging `AGENT-TEMPLATE.md` copies when the second
   does not exist (its absence *was* finding A21). Root cause: a diff-only
   input invites the model to reconstruct the unchanged side from
   assumption, and it reconstructs the **pre-fix** state — so a truth-sweep
   PR reads as "the old paths are still there". Meanwhile every CodeRabbit
   finding reproduced.

3. **Two audit findings were wrong despite surviving adversarial
   verification.** A74 was backwards: the audit said the library emits
   PASS/CONCERNS/FAIL, but **22 of 25** evaluators use the APPROVED family
   and only 3 use PASS/CONCERNS/FAIL — it generalised from the single
   evaluator it sampled. Rewriting as suggested would have broken the doc
   for 22 evaluators. The real bug it *missed*: the kit's own recommended
   trio spans both vocabularies, so an agent grepping a fixed token misses
   a verdict. A48's "the manifest has no tiers at all" was also false.

4. **My "operator owes an rm-rf allowlist" framing was wrong, and I
   inherited it from memory.** Memory had accumulated it across five
   tasks. Operator decision `5497bf6` settled it: the tracked
   `Bash(rm -rf*)` deny is **deliberate standing policy**; `mktemp -d` plus
   listing leftovers for manual sweep is the intended pattern — exactly
   what I did, but I reported it as a debt. Inherited framing from memory
   deserves the same verify-before-believing treatment as a doc citation.

5. **Six sibling-instance misses, not three — and my class greps reported
   the classes closed.** Post-merge verification (`c120538`) found three
   residuals beyond CodeRabbit's three:
   - `validate_task_status.py:9` — I fixed the pre-v0.4.0 path in the
     **print statement at :118** and missed the **module docstring at :9**.
     Same file. Even item 15 *as originally written* would have caught this
     had I actually run it after the edit.
   - `test_linear_sync.py:136` — a second RED-phase remnant
     (`# Import will fail until implementation exists`) left behind when I
     removed the docstring's RED line.
   - `engine-materials.sh` — **my T6 fix introduced a new false claim**: it
     asserted a "testing guide" that does not exist and preserved dead
     `proposals/` and `TESTING.md` excludes for paths removed in
     ASK-0044/0047. Second time in this task I made a citation *more
     precise while leaving it false* (T3 was the first).

   The uncomfortable part: my class greps returned zero and I reported the
   classes closed. They were pattern-shaped (`scripts/project`,
   `delegation`) and these residuals were the same *claim* in different
   wording — a docstring phrasing, a comment, a dead exclude. **A grep
   closes a token, not a class.** Closing a class needs the token sweep
   *plus* a read of each file I touched.

### What Should Change

1. **Self-review item 15 was too narrow — already widened in this PR, but
   the planner should know why.** Three of six bot findings were violations
   of the rule *as I wrote it earlier in the same PR*. It failed on two
   axes: it said grep "that file" (T2's sibling was in a *different* file),
   and it implicitly assumed prose (T1's sibling was a table, T5's were two
   diagrams and a table). Now reads: grep **repo-wide**, and check
   diagrams, tables, help text and comments — a prose-shaped grep does not
   match a Mermaid edge label.

2. **A remedy is a citation — execute it before documenting it.** T3
   (Major): while fixing A40, whose old advice was *destructive*
   (`rm -rf` on the very directory the library installs into), I replaced
   it with advice that does nothing — `install-evaluators` returns early
   unless `--force`. I verified paths and versions relentlessly and never
   verified the *behaviour* of a command I was recommending. Self-review
   item 16 should explicitly cover commands, not just paths/versions.

   **This happened twice.** The `engine-materials.sh` residual is the same
   shape: correcting `docs/decisions/` → `docs/adr/` made the comment more
   precise while leaving it false about the "testing guide" and the dead
   excludes. **Rule: when you edit a line to fix one false claim, verify
   every other claim on that same line.** A partially-corrected citation
   reads as freshly-verified and is therefore worse than an obviously
   stale one — it launders the error.

3. **"Class closed" needs a stronger proof than a zero-hit grep.** I
   reported five classes closed on the strength of pattern greps; six
   sibling instances survived, because the same claim was worded
   differently (docstring vs print, comment vs table, prose vs diagram). A
   token grep proves a *token* is gone. Closing a *class* additionally
   requires reading every file the sweep touched — which for this task
   was 54 files, and is the real cost the next sweep task should budget
   for. The planner's 8-agent tree-verification is what actually caught
   these; that step should be part of the sweep, not a post-merge check.

4. **Reconsider the evaluator trio as a gate for prose-only PRs.** It cost
   three runs and produced zero actionable findings while the class greps
   and the 799-test suite produced the real evidence. If it stays, the
   input must either carry full-file context or state explicitly that
   unchanged regions must not be reasoned about — and reviewers should
   expect FAIL verdicts that are artifacts of the input form. **Never
   action an evaluator finding without reproducing it**; this is the tenth
   recorded o3 data point in that direction.

5. **When an audit derives a sweep task, budget for findings that are
   wrong.** Two of 54 were refuted by measurement despite adversarial
   verification. Dispositions should require measured evidence, not "as the
   audit says" — and the ownership rule should flag jointly-owned files in
   the handoff (`COVERAGE-WORKFLOW.md` is A41/KIT-0067 *and* A42/mine;
   `EVALUATION-WORKFLOW.md` is A68/KIT-0067 *and* A71/mine) so the
   implementer expects the seam rather than discovering it.

### Permission Prompts Hit

1. **`rm -rf` in the F3 scratch-generation command** — blocked once,
   worked around immediately with `mktemp -d` (no user wait). **Do not add
   this to the allow list**: operator decision `5497bf6` makes the tracked
   `Bash(rm -rf*)` deny standing policy, and tooling must not nag about an
   allowlist. The correct agent behaviour is `mktemp -d` plus listing
   leftovers for manual sweep — now codified in KIT-0071 F3.

No other prompts. Note the deny also means agents cannot clean up their own
scratch dirs; leftovers this session: `/tmp/kit0069-gen.ZZga30/` and
`/tmp/kit0069-pr-body.md`.

### Process Actions Taken

- [ ] Correct the memory entry that framed the `rm -rf` deny as an
      operator debt (now settled policy per `5497bf6`) — it misled five
      consecutive tasks
- [ ] Extend self-review item 16 to cover **commands/remedies**, not just
      paths, versions and file citations (T3 class)
- [ ] Decide whether the evaluator trio remains a gate for prose-only PRs;
      if so, mandate full-file context or an explicit
      "do-not-reason-about-unchanged-regions" instruction in the input
- [ ] Add `fix_by_class_not_instance` to `patterns.yml` — an audit
      enumerates instances, only a class grep closes a class (+15% sites
      here)
- [ ] Flag jointly-owned files in handoffs when a task splits an audit by
      A-number rather than by file
- [ ] Add a "verify every claim on a line you edit" rule — two residuals
      this session were citations made *more precise while left false*
      (T3's non-functional remedy, engine-materials' phantom "testing
      guide"). A partially-corrected citation reads as freshly-verified,
      so it launders the error
- [ ] Move tree-grounded verification INTO the sweep rather than after
      merge — the planner's 8-agent pass (`c120538`) caught 3 residuals my
      class greps reported closed; that is the step that actually closes a
      class, and it should gate the PR, not follow it
- [ ] KIT-0072 (upstream the spec-compliance evaluator) — filed, in
      `1-backlog`, unblocks restoring `/check-spec` to a real gate

### Incident Closure

Per the KIT-0046 / ADR-0027 P4 lifecycle rule:

1. **`rg` false-empties (hidden dirs + multi-pattern) and `find` without
   `-L` on the symlinked evaluators dir** → **Triage-guide entry**, landed
   in this PR: `.claude/skills/self-review/SKILL.md` item 16 documents both
   traps and mandates `grep -Rn` for class-closure evidence. Not a doctor
   check — it is agent search behaviour, not environment state.

2. **Serena's project root resolved to the primary clone while working in
   a worktree** → **Doctor check**, deferred to KIT-0071, which the planner
   widened to the worktree-provisioning class in `dbe687f`. The check
   should enumerate what a worktree shares or misdirects: `.venv` symlink,
   `.adversarial/evaluators` symlink, and Serena's registered-project root.
   Four instances of one class hit this session.

3. **`claude-code` evaluator failed at run time with a valid API key —
   zero credit balance** → **Not-checkable note**, recommended in
   `scripts/core/doctor.d/30-evaluators.sh` (which today only checks the
   evaluator tree is installed) or `20-env-keys.py` (which only checks key
   *presence*). Neither notes that a present, valid key still fails when the
   balance is zero, and balance has no cheap API — the same shape as the
   existing CodeRabbit-quota note in `80-bot-presence.sh`, which is the
   pattern to copy. **Not yet written — planner action.**

4. **Commit aborted by `end-of-file-fixer` while printing a passing pytest
   tail** → **Already closed**; the KIT-0057 Phase-5 rule (verify with
   `git log -1` + `git status`, never trust the hook output tail) caught it
   within one command. Cause was self-inflicted: my trailing-whitespace
   pre-strip dropped the terminating newline. Reinforced in the commit
   message; no new check needed.

5. **`rm -rf` deny** → **Explicitly NOT an incident.** Settled policy per
   operator decision `5497bf6`; recorded here to stop it being re-raised as
   a gap a sixth time.
