---
description: How to run the adversarial code-review evaluator after bot rounds and before human review
user-invocable: false
version: 1.3.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-07-05
created-by: "@movito with planner2"
---

# Code-Review Evaluator

Run after bot triage rounds are complete, before human review. Uses a different model family (o1/Gemini) to find edge-case bugs that bots and Claude miss.

## When to Run

- After all bot threads are resolved (0 unresolved)
- Before requesting human code review
- **Exception — doc-heavy tasks run the evaluator BEFORE PR open** (see
  "Ordering for Doc-Heavy Tasks" below)

## Ordering: Run the Evaluator Trio Before PR Open (all tasks)

**Recommendation (adopted KIT-0035 for doc-dominated; widened to ALL
tasks 2026-07-14, KIT-0046 retro)**: run the evaluator trio **before**
opening the PR, regardless of task type. Local tests must pass first —
evaluate working code, not a draft — but do not wait for CI/bots.

Why:

- **KIT-0032**: each evaluator-driven rewrite after PR open triggered a
  fresh bot round — four review rounds for a single documentation file.
- **KIT-0033**: running the evaluator while CI was still pending worked
  well — the two signals don't depend on each other.
- **KIT-0040**: external-finding yield concentrates on freshly written
  content; addressing trio findings before bots first see it is where
  the round-saving is.
- **KIT-0035 + KIT-0044** (doc-dominated): pre-open trio produced
  zero-noise first bot rounds, twice.
- **KIT-0046** (code-dominated — the widening evidence): all three
  substantive round-1 bot findings were also evaluator findings. The
  original "code-heavy keeps CI/bots first" carve-out predicted CI
  would invalidate reviews; in practice local tests + pre-open trio
  gets the same protection without burning bot rounds.

The only remaining reason to defer the trio is when the diff genuinely
cannot be assembled pre-PR (rare); say so in the review record.

## When to Skip

### Auto-skip (<10 lines source)

Skip without deliberation when ALL are true:

- **< 10 lines of source changed** (not counting tests, docs, or config)
- **No new functions or classes**
- **No external integrations**

Running the evaluator on a trivial change (e.g., a 3-line contextlib.suppress fix) has zero ROI.

### Discretionary skip (10-20 lines source)

You may skip the evaluator when ALL of these conditions are true:

- **< 20 lines of logic changed** (not counting tests, docs, or config)
- **No new functions or classes** (only modifications to existing ones)
- **No external integrations** (no subprocess, API calls, or new dependencies)
- **Established patterns only** (all code follows existing patterns in the codebase)

### Always document the skip

```bash
echo "# Evaluator skipped: <N lines logic, no new functions, no external integrations" \
  > .kit/context/reviews/<TASK-ID>-evaluator-review.md
```

**When in doubt, run it.** The fast variant costs ~$0.004 and takes 30 seconds.

## Cross-Repo Mode

In the cross-repo pattern (planning repo separate from target repo) the
built-in `adversarial review` command **does not work** — it enforces a
"you have changed files" guardrail on CWD, and the planning repo has no
code changes (they live in the target repo). Use **file-based evaluators**
instead. They accept an input file and skip the guardrail.

To produce the input, run the helper from the planning repo:

```bash
./scripts/core/prepare-review-input.sh <TASK-ID>
```

It auto-detects the target repo from `CLAUDE.md` (`## Target Repository`
section), reads `git diff main...HEAD` over there, and writes
`.adversarial/inputs/<TASK-ID>-code-review-input.md` with the diff plus
the complete post-change contents of every changed file.

For single-repo projects (no target section in `CLAUDE.md`), the same
script reads from the current working-directory repo — no separate flag
needed.

See `docs/CROSS-REPO-PATTERN.md` for the full
cross-repo evaluator recipe.

## Step 1: Prepare Input

### Cross-repo / automated path (preferred)

```bash
./scripts/core/prepare-review-input.sh <TASK-ID>
# Optional flags: --base <branch> (default main), --format diff|full (default full)
```

This is the canonical path. It handles the diff extraction, the header
block, and the full-file appendix in one step, and it works in both
cross-repo and single-repo modes.

### Manual path (special cases only)

If the helper can't infer the right diff (e.g. reviewing a stacked PR or
an arbitrary commit range), create
`.adversarial/inputs/<TASK-ID>-code-review-input.md` by hand using the
template at `.adversarial/templates/code-review-input-template.md`.

Use the PR's original task ID. The helper always writes the single
canonical name `<TASK-ID>-code-review-input.md` and overwrites it on
re-run. If you need to preserve an earlier round's input for
comparison, rename it manually before re-running:

- First run: `<TASK-ID>-code-review-input.md`
- Preserve before re-run: `mv <TASK-ID>-code-review-input.md <TASK-ID>-code-review-input-r1.md`

The evaluators only consume the input at invocation time, so this
manual rename is only necessary if you want the earlier input file
retained on disk.

**CRITICAL: Include FULL file content, not diffs or excerpts.** The evaluator cannot
reason about imports, error handling context, or module-level state from partial code.
Diff-only inputs produce false positives (high false positive rate observed empirically).
ID2-0002 retro documented a concrete example: Claude Sonnet flagged
`homeSponsorsQuery` as a non-existent export (HIGH severity) because the
diff didn't include the line where it was defined.

Include:
- Full source of all new/changed files (complete files, not diffs)
- Full test file
- Summary of what bots found and how it was addressed

## Step 2: Run the Evaluator

### Discover installed evaluators first

Availability varies per install, and v2 variants exist for some
evaluators but not others (e.g. `code-reviewer-fast-v2` exists while
`code-reviewer` has no v2). List what is actually installed before
choosing:

```bash
adversarial list-evaluators
# Fallback if the installed CLI predates list-evaluators:
ls .adversarial/evaluators/*/
```

Prefer a `-v2` variant wherever one is installed; v1 names are
deprecated in the evaluator library.

### Available evaluators

| Command | Model | Focus | Cost | API Key Env Var |
|---------|-------|-------|------|-----------------|
| `adversarial code-reviewer-fast` | Gemini Flash | Quick correctness gate | ~$0.004/run | `GEMINI_API_KEY` |
| `adversarial code-reviewer` | OpenAI o3 | Deep adversarial, edge cases | ~$0.33/run | `OPENAI_API_KEY` |
| `adversarial claude-code` | Claude Sonnet | Security, data handling | ~$0.05/run | `ANTHROPIC_API_KEY` |

**Cross-repo evaluator trio (recommended)**: run `code-reviewer-fast` on
every PR as a fast gate, add `code-reviewer` for non-trivial changes, and
add `claude-code` for security-sensitive code. Each model catches
different classes of issues with minimal overlap (validated empirically
across projects: distinct models surface largely non-overlapping findings).

**Note**: `spec-compliance-fast` is NOT available — use manual spec checks or `/check-spec` (Gemini Flash via API) instead.

**`claude-code` requires `ANTHROPIC_API_KEY` *uncommented* in `.env`.**
A commented-out key does not error at launch — the evaluator fails
mid-run (KIT-0032 hit this as a mid-session blocker: the trio ran 2-of-3
until the operator uncommented the key). Verify before running the trio:
`grep -E '^ANTHROPIC_API_KEY=' .env` must match. Never add or commit a
key — surface the gap to the operator instead.

If the required API key is missing, fall back to another evaluator. If none of the keys are set, document the failure and proceed to human review.

### Single-key (degraded) mode

Not every project carries all three provider keys (KIT-0056, ADR-0027
P5). With exactly ONE key available, the trio degrades to a documented
mode — never a silent partial trio:

1. Run the one evaluator your key supports (see the table above for
   the key→evaluator mapping).
2. Run the self-review checklist (`.kit/skills/self-review/SKILL.md`)
   in full — it substitutes for the missing models' breadth, not for
   the one evaluator you can run.
3. **NAME the mode in the persisted review record** (Step 4's
   artifact). First line of the record, e.g.:

   ```
   Mode: degraded single-key (only GEMINI_API_KEY present) —
   code-reviewer-fast only + self-review checklist; code-reviewer and
   claude-code not run.
   ```

Gate 5 is unchanged: a review record is still required, and a degraded
record that names its mode satisfies it. What is NOT acceptable is a
record that looks like a full trio ran when it didn't — every degraded
surface names its mode (the `intersection_names_drops` pattern applied
to service presence).

```bash
# Fast gate (every PR)
adversarial code-reviewer-fast .adversarial/inputs/<TASK-ID>-code-review-input.md

# Deep adversarial (non-trivial PRs)
adversarial code-reviewer .adversarial/inputs/<TASK-ID>-code-review-input.md

# Security focus (security-sensitive code)
adversarial claude-code .adversarial/inputs/<TASK-ID>-code-review-input.md
```

### Large-input prompt workaround

The `adversarial` CLI prints `Continue anyway? [y/N]` for input files
larger than ~700 lines and waits for stdin. In a non-TTY context (sub-agent,
CI, automation), the prompt hangs indefinitely. Pipe `yes` in to bypass:

```bash
echo y | ADVERSARIAL_UNATTENDED=1 adversarial code-reviewer-fast .adversarial/inputs/<TASK-ID>-code-review-input.md
```

Belt-and-braces (final resolution 2026-07-17): multiple adversarial
builds coexist all claiming the same version — PyPI builds read the
piped `y` from stdin; the operator's editable dev build reads the
`ADVERSARIAL_UNATTENDED` env flag and otherwise auto-cancels **with
exit 0**. Use both; each is inert where unneeded. **Never trust exit 0
alone** — a cancelled run also exits 0; the proof an evaluation ran is
the log file existing with a verdict. Symptom→cause: "evaluation
'succeeded' but no log verdict" = auto-cancelled non-TTY large input.

## Step 3: Read and Address Findings

**First: run `git status` immediately after every evaluator invocation,
before staging anything.** During KIT-0044, an evaluator running through
a stale venv (adversarial-workflow 0.9.7, the aider-era engine) applied
its suggested edit directly to a script mid-review. The root cause was
fixed (venv upgraded to the aider-free 1.0.1), but the check stays as
defense in depth: an unexpected working-tree change after a review run
must be inspected and consciously kept or reverted — never silently
swept into the next commit.

Output lands in `.adversarial/logs/`, one file per evaluator:

```bash
cat .adversarial/logs/<TASK-ID>-code-review-input--code-reviewer-fast.md
cat .adversarial/logs/<TASK-ID>-code-review-input--code-reviewer.md
cat .adversarial/logs/<TASK-ID>-code-review-input--claude-code.md
```

| Verdict | Action |
|---------|--------|
| **FAIL** | Fix the identified bugs, push, and re-run the evaluator |
| **CONCERNS** | Address test gaps and robustness issues, push |
| **PASS** | Proceed to human review |

## Step 4: Persist Output

Concatenate all evaluator outputs into a single review artifact tracked
in git. Use the aggregation pattern (fail-fast when no logs match) so
an empty review file can't silently mask evaluator failures:

```bash
shopt -s nullglob
logs=(.adversarial/logs/<TASK-ID>-code-review-input--*.md)
shopt -u nullglob
if [ "${#logs[@]}" -eq 0 ]; then
    echo "ERROR: no evaluator logs found for <TASK-ID>" >&2
    exit 1
fi
{
    for log in "${logs[@]}"; do
        echo "## Source: $(basename "$log")"
        echo
        cat "$log"
        echo
    done
} > .kit/context/reviews/<TASK-ID>-evaluator-review.md
```

Include this file in your next commit. The same recipe appears in
`docs/CROSS-REPO-PATTERN.md` — keep the two in
sync when updating.
