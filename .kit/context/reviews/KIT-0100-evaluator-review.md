# KIT-0100 — Evaluator Review Record

**Task**: KIT-0100 — Canon fixes round 2 (F1–F6 + F8) + plugin 2.0.2
**Branch**: `feature/KIT-0100-canon-fixes-round-2`
**Date**: 2026-08-11
**Reviewer**: feature-developer (Opus 5)

## Tier decision — fast tier only, `--format diff`

Prose-dominated diff: 11 markdown agent/command/skill definitions, 197
changed lines, no executable code. The prose-sweep exception applies
(deep tier 0-for-15 across KIT-0069/0073; planner decision 2026-07-28,
reaffirmed by the three-data-point process note in `a2994c7`). Deep tier
(`code-reviewer`, `claude-code`) **skipped** — recorded here per the
skip-is-a-decision rule.

Note the irony worth keeping: this very task edits the Step 2 snippet so
that skip is explicit in the instruction rather than buried a few
paragraphs up. The run followed the rule the diff clarifies.

## Run

```
adversarial code-reviewer-fast .adversarial/inputs/KIT-0100-code-review-input.md
```

Model: `gemini/gemini-2.5-flash`. Verdict: **FAIL** (1 correctness, 3
robustness). Log:
`.adversarial/logs/KIT-0100-code-review-input--code-reviewer-fast.md`

## Findings and disposition

Each was reproduced against the tree before actioning — the prose-sweep
rule's requirement, and the reason two of KIT-0099's findings were
correctly rejected.

### F-A [CORRECTNESS] Unconditional `git push` after a blocked commit — ACCEPTED, fixed

Claim: in the F3 guard, `git push` sits on its own line, so a dirty index
blocks the commit but still pushes.

Reproduced: confirmed in the tree. My first form was

```
git diff --cached --quiet || { echo ...; git diff --cached --name-only; }
git diff --cached --quiet && git commit --allow-empty -m "..."
git push
```

The push is unguarded, so the command reports "retriggered" having pushed
the previous state and created no new commit. It also ran the same check
twice. **This is a defect I introduced while fixing F3** — the finding is
correct and the fix was incomplete.

Replaced both forms with a single `if/else` that guards commit AND push
together, and prints what is staged in the else branch. Good catch by the
cheap tier on exactly the kind of shell-logic slip prose review is
supposed to miss.

### F-B [ROBUSTNESS] `timeout` may be absent (exit 127 ≠ CI failure) — ACCEPTED, fixed

My F2 fix named exit 124 as TIMEOUT but left "no supervisor available" as
prose with no detection, and did not name 127. An agent could read
"command not found" as a CI result.

Now: three exit codes enumerated (124 timeout / 127 not-installed /
other = real failure), a `command -v timeout || command -v gtimeout`
resolution step, and an explicit ban on falling back to a bare
`gh run watch` — the unbounded hang F2 exists to prevent. Poll
`gh run view` instead and say so in the report.

### F-C [ROBUSTNESS] Path quoting inside the launch message — ACCEPTED, narrow fix

Real but narrow: `claude --agent project-intake "Begin the intake.
Brief: <path>  Code: <path>"` breaks if a path contains a double quote,
and paths with spaces are common.

Added one sentence: substitute real absolute paths before printing (the
command validated both moments earlier, so it has them), and switch to
single outer quotes if a path contains a double quote. Declined to write
an escaping tutorial — the command already validates the paths upstream,
and the failure is visible immediately on paste.

### F-D [ROBUSTNESS] Ambiguous prose-vs-logic classification — ACCEPTED, one-line tiebreaker

The tier rule had concrete criteria for each pole but no tiebreaker for a
mixed diff, so an ambiguous case could take the cheap gate by default.

Added to the block this task already edits: **mixed diff → treat as
logic-shaped**, because a needless deep run costs money while a missed
logic bug costs a defect in main. Kept to one sentence — widening the
tier policy further belongs to standing policy, not this task.

### Test-gap table items not actioned

The evaluator's summary table lists three further speculative gaps
(`$PLANNING` unset, `begin` keyword comprehension, empty opening message
for a created agent). Declined: each asks for defensive scaffolding
around instructions an LLM reads, not executable code, and none is
reproducible as a defect in the current tree. Noted rather than silently
dropped.

## Mechanical verification

- `pytest`: 1206 passed, 13 skipped (full suite, pre-fix run) and
  contract tests green after each pair edit.
- Contract tests specifically: `test_agent_contracts.py` 8 passed —
  pair-identity (both feature-developer halves byte-identical below the
  SYNC marker) and evaluator-ordering pins intact.
- `pattern_lint.py` on all changed files: clean.
- Class greps quoted in the PR body for F1 (`see Phase 6` → zero), F2
  (every `run watch` invocation), F3 (every `--allow-empty`), and F8
  (every `claude --agent` in shipped prose).
- Review surface: 197 lines pre-fix, well under the ~500 budget.

## Bot rounds (PR #124) — 6 threads, all resolved

Two rounds, six findings, **all correct and all against text this PR
introduced**. Notably every one improved on a fix from the previous
round: the cheap-tier evaluator and the bots each caught a different
layer of the same three defects.

**Round 1 (4 findings):**

1. *Bugbot* — the no-supervisor poll fallback omitted `$GH_REPO_ARG`, so
   in split mode it would poll the planning repo and misreport CI status.
2. *CodeRabbit* — I added a `command -v timeout || command -v gtimeout`
   resolution step and then kept writing a **literal** `timeout 600` in
   all five watch commands. On macOS (resolved name `gtimeout`) each
   exits 127 and watches nothing — the exact failure the resolution step
   existed to prevent. Fixed with a `$TIMEOUT` placeholder following the
   file's own `$GH_REPO_ARG` convention.
3. *CodeRabbit* — `git -C <target_path>` unquoted splits on a path with
   spaces. Quoted at all six split-mode call sites.
4. *CodeRabbit* — my "switch to single quotes" advice was wrong-shaped:
   double quotes still evaluate `$(…)`/backticks, single quotes break on
   an apostrophe. Replaced with `printf '%q'` escaping of the whole
   argument. The template's sibling line got a clarifying note instead —
   a human fills that one in, so there is no generating agent to escape.

**Round 2 (2 findings):**

5. *CodeRabbit* — three prose `run watch` mentions got `$TIMEOUT` in
   round 1 but kept no routing and no `--exit-status`; sibling lines I
   touched without finishing. All eight references now consistent.
6. *CodeRabbit* — **the best finding of the task.** My F3 guard was a
   check-then-act sequence: `git diff --cached --quiet` reads the index
   once, and anything staged between that read and the commit rides along
   anyway. Suggested `--allow-empty --only` instead.

   Verified empirically before adopting (git 2.55, file `b.txt` staged):
   the commit lands empty (`git show --stat` lists no files) and `b.txt`
   remains staged afterwards. So the retrigger commit becomes
   *structurally* incapable of carrying staged work, rather than checking
   and hoping. The whole if/else guard collapsed into one chained command
   per mode — shorter and safer.

**Round 3**: clean. Both bots pass, zero open threads, tests green on
3.10/3.12/3.14.

## Scope

F7/F9/F10 untouched (KIT-0101) — verified: `project-intake`'s
doctor-verdict relay line is unchanged, and no transparency headers were
added to any user-invocable command.

## Note for the retro

The tier split worked exactly as the rule predicts, and this task is a
clean data point for it. The fast tier caught a shell-logic slip
(unguarded `git push`); the bots, which read the tree rather than a
diff, caught the *incompleteness* of each subsequent fix — routing left
off sibling lines, a resolution step whose result was then ignored.
Neither would have been found by re-reading my own diff, and the deep
evaluator tier was correctly skipped throughout on a prose-shaped change.
