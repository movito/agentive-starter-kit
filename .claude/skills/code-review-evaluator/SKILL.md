---
description: How to run the adversarial code-review evaluator once local tests pass, before the PR opens
user-invocable: false
version: 1.9.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-08-11
created-by: "@movito with planner2"
---

# Code-Review Evaluator

Run **after local tests pass and before the PR opens**. Uses a different
model family (o1/Gemini) to find edge-case bugs that bots and Claude miss.

## Where the artifacts live — resolve this FIRST

Every artifact below (inputs, logs, the Gate 5 record) belongs to the
**planning repo**, because that is where Gate 5 and `agentive preflight`
look for them. In split mode the session runs in the TARGET worktree, so
a relative `.kit/…` or `.adversarial/…` path lands in the wrong repo —
the record is written, the gate still fails, and nothing says why.

Resolve the planning root once, before running anything. Read the path
out of the output; do not assign it (`$()` is forbidden by the agents'
Shell Rules):

```bash
git rev-parse --show-toplevel
```

- **Single-repo mode**: that path IS the planning repo.
- **Split mode**: take the planning path from the handoff's Session
  topology instead — the target worktree's CLAUDE.md has no
  `## Target Repository` section.

Confirm it by checking the two markers that always exist in a planning
repo, then ensure the review directory is present — a fresh planning repo
can legitimately lack that empty directory, and both the skip record and
the Step 4 aggregation write into it:

```bash
ls /literal/planning/path/.kit/tasks /literal/planning/path/CLAUDE.md
mkdir -p /literal/planning/path/.kit/context/reviews
```

If the first `ls` fails, the root is wrong — stop and ask rather than
creating directories in the wrong repo.

**`"$PLANNING"` below is a placeholder for that literal path, not a shell
variable** — each Bash call is a fresh shell, so an assignment would not
survive to the next call. Type the path.

**Run the evaluators from the planning repo** (`cd` there first, or pass
absolute paths). `agentive review-input` writes
`.adversarial/inputs/…` relative to its working directory, so running it
elsewhere splits inputs and logs across two repos.

## When to Run

- **Local tests green** — evaluate working code, not a draft
- **Before opening the PR**, for all task types that do not meet the
  skip conditions in "When to Skip" below (see "Ordering" for why the
  pre-open position applies regardless of task type)
- Do NOT wait for CI or for bot threads: the signals are independent, and
  every evaluator-driven rewrite made after PR open burns a bot round

The ordering rule and the skip policy answer different questions: skip
decides *whether* the trio runs, ordering decides *when*. A skipped
evaluation still needs its persisted record (see "Always document the
skip") — that record is what Gate 5 checks.

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

### Mixed-shape tasks never skip (added 2026-08-12)

The skip rules above are for trivially small LOGIC changes. A task that
mixes deletions with authored records, messages, or sweeps (retirement
tasks, release tasks, canon fixes) always runs at least the fast tier
pre-open — first-draft authored content is where self-introduced
defects concentrate, and skipping the trio makes the BOTS the first
reviewers, which converts catchable defects into post-open fix rounds
(KIT-0102 PR #127: skip granted for "pure deletion", ten bot threads
followed, the two substantive ones self-introduced authored content).

### Always document the skip

```bash
echo "# Evaluator skipped: <N lines logic, no new functions, no external integrations" \
  > "$PLANNING"/.kit/context/reviews/<TASK-ID>-evaluator-review.md
```

> **The record goes in the PLANNING repo.** Gate 5 reads it there. In
> split mode the session runs in the TARGET worktree, so a relative
> `.kit/…` path writes to the wrong repo — the record is never found and
> preflight fails a gate the work actually satisfied. Resolve the
> planning root once and substitute the literal path (it does not
> survive between tool calls).

**When in doubt, run it.** The fast variant costs ~$0.004 and takes 30 seconds.

## Cross-Repo Mode

In the cross-repo pattern (planning repo separate from target repo) the
built-in `adversarial review` command **does not work** — it enforces a
"you have changed files" guardrail on CWD, and the planning repo has no
code changes (they live in the target repo). Use **file-based evaluators**
instead. They accept an input file and skip the guardrail.

To produce the input, run the helper from the planning repo:

```bash
agentive review-input <TASK-ID>
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
agentive review-input <TASK-ID>
# Optional flags: --base <branch> (default main), --format diff|full (default full)
```

This is the canonical path. It handles the diff extraction, the header
block, and the full-file appendix in one step, and it works in both
cross-repo and single-repo modes.

**Choose `--format` by the SHAPE of the change, not by default**
(KIT-0092 — third recorded case of input format distorting evaluator
output, after the KIT-0069/KIT-0073 prose-sweep shutouts):

- **Logic changes** (behavior, control flow, new code) → `full`: the
  evaluators need surrounding context to judge correctness.
- **Strings/docs-only changes** (renames, printed text, doc sweeps,
  deletions) → `diff`: with `full`, evaluators review the WHOLE module
  and return findings about unchanged code — noise that costs a
  disposition round each. On KIT-0092, `--format full` made two of
  three evaluators review entire modules for a strings-only diff.

The pattern: trio value depends on input shape matching change shape.
If a round returns mostly findings about code the diff never touched,
the input format was wrong — re-run with `diff` before disposing.

**Prose-shaped diffs: run the FAST tier only — skip the deep evaluator
(planner decision 2026-08-10, three consecutive data points).** On
instruction-prose changes (agent definitions, skills, workflow docs),
the deep evaluator's findings were dominated by reconstructions of the
pre-fix state and hallucinated removed safeguards, while tree-reading
bots went essentially 1-for-1 on real defects: KIT-0092 (whole-module
noise on a strings diff), KIT-0097 (o3 oscillations across the 2.0.0
review), KIT-0098 (trio: 14 findings, 3 accepted, 1 real miss the bot
then caught; bots: 1-for-1). Deep evaluators reason about CODE
semantics; prose coherence is not their instrument. Rule: prose-shaped
diff → `code-reviewer-fast` (or `-v2`) only, `--format diff`; the deep
tier stays for logic diffs. Note the skip in the review record with
this section as the citation.

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

**Note**: there is no spec-compliance evaluator, and there never was one
in this library. It originated as a dispatch-kit project-local custom
evaluator and did not survive the port into this kit, so
`adversarial spec-compliance-fast` matches nothing — do not run it.
`/check-spec` now performs a **manual** requirement-to-code trace instead
of an evaluator call; use it for spec compliance. KIT-0072 tracks
upstreaming the evaluator into the library, after which `/check-spec`
becomes an evaluator call again and gains a row in the table above.

**`claude-code` requires `ANTHROPIC_API_KEY` *uncommented* in `.env`.**
A commented-out key does not error at launch — the evaluator fails
mid-run (KIT-0032 hit this as a mid-session blocker: the trio ran 2-of-3
until the operator uncommented the key). Verify before running the trio:
`grep -qE '^ANTHROPIC_API_KEY=.+$' .env` must succeed — the `-q` keeps
the secret off the transcript. Never add or commit a key — surface the
gap to the operator instead.

If the required API key is missing, fall back **within the tier the change
shape allows** — never upward. On a prose-dominated diff the tier is
fast-only, so a missing fast-tier key means the gate is blocked (see
below); it does NOT license `code-reviewer` or `claude-code` as
substitutes. Reaching the deep tier through a degraded path is still
reaching the deep tier — the spend the prose rule exists to avoid, now
arrived at by accident rather than by decision.

Substitution is legitimate only sideways: another evaluator **in the same
tier** whose provider key IS set (e.g. a `-v2` variant of the same
evaluator). Record which evaluator actually ran and why the intended one
did not — a review record that names an evaluator nobody ran is a false
claim about the gate.

### No keys at all — the gate does NOT auto-open

If **none** of the provider keys are set, the trio cannot run and Gate 5
has no evidence. This is a blocked gate, not a passed one. Do not
"document the failure and proceed" on your own authority — a documented
failure is still a failure, and a session that self-certifies past it
removes the gate for every future task that copies the pattern.

Required sequence:

1. **Write the failed record** at
   `"$PLANNING"/.kit/context/reviews/<TASK-ID>-evaluator-review.md`
   (the PLANNING repo — see above), first line
   naming the mode explicitly:

   ```text
   Mode: FAILED — no provider API keys present (GEMINI_API_KEY,
   OPENAI_API_KEY, ANTHROPIC_API_KEY all unset); trio not run.
   ```

2. **Run the self-review checklist** (`.claude/skills/self-review/SKILL.md`)
   in full and record its output in the same file. It is a partial
   substitute, and the record must say so — never present it as a trio.
3. **Surface the gap to the coordinator/operator and STOP.** State that
   Gate 5 is unsatisfied, that the cause is missing keys (an environment
   problem they can fix in a minute), and ask whether to wait for a key
   or proceed without the gate.
4. **Proceed to human review only on explicit approval**, and record
   that approval — who approved, when — in the review record.

The one thing that must never happen is a review record that reads like
a gate was satisfied when no evaluator ran.

**Loading `.env` in unattended/worktree runs**: use the POSIX dot form
inside `bash -c`, not the `source` keyword — the worktree-isolation
permission hook can refuse `source`-in-command-string while the
equivalent passes (KIT-0091):

```bash
bash -c 'set -a; . ./.env; set +a; adversarial <evaluator> <target>'
```

### Single-key (degraded) mode

Not every project carries all three provider keys (KIT-0056, ADR-0027
P5). With exactly ONE key available, the trio degrades to a documented
mode — never a silent partial trio:

1. Run the one evaluator your key supports (see the table above for
   the key→evaluator mapping).
2. Run the self-review checklist (`.claude/skills/self-review/SKILL.md`)
   in full — it substitutes for the missing models' breadth, not for
   the one evaluator you can run.
3. **NAME the mode in the persisted review record** (Step 4's
   artifact). First line of the record, e.g.:

   ```text
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
a stale venv (adversarial-workflow 0.9.7, whose engine edited files
in place) applied its suggested edit directly to a script mid-review.
The root cause was fixed (venv upgraded to 1.0.1, whose engine never
writes to the working tree), but the check stays as
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

> ⚠️ **Verdict vocabulary is per-evaluator, not library-wide** — do
> not grep a single token across logs. Across the installed set
> (v0.10.0, 25 verdict-declaring evaluators; measured, KIT-0069/A74):
>
> | Vocabulary | Evaluators | Examples |
> |---|---|---|
> | `APPROVED` / `NEEDS_REVISION` / `REJECT` | majority | `claude-adversarial`, `mistral-adversarial`, `gpt55-synthesis` |
> | `APPROVED` / `REVISION_SUGGESTED` | several | `arch-review`, `arch-review-fast`, `mistral-arch` |
> | `APPROVED` / `REJECT` (no middle) | several | `claude-code`, `gemini-code`, `gpt5-codex` |
> | `PASS` / `CONCERNS` / `FAIL` | three | `code-reviewer`, `code-reviewer-fast(-v2)` |
>
> The recommended trio itself spans two vocabularies (`claude-code`
> emits APPROVED/REJECT). **Read each log and interpret the verdict;
> never pattern-match a fixed token.** To preview an evaluator's
> vocabulary, grep its prompt text — `evaluator.yml` declares no
> structured vocabulary field, so the bold uppercase tokens in the
> prompt are the only mechanical signal (a heuristic: it can
> over-match other bold caps; the read-the-log rule above is the
> binding one):
> `grep -o -E '\*\*[A-Z_]+\*\*' .adversarial/evaluators/<provider>/<name>/evaluator.yml | sort -u`

## Oscillation protocol: disposition tables + the deep-round cap (KIT-0090)

Deep evaluators can REVERSE their own instructions across rounds — on
KIT-0090, o3 demanded a boundary block in round 4 and called that same
block a regression in round 5, and forbade-then-demanded generic
`ImportError` catching across PRs. Chasing a green verdict through
oscillation loops forever. The named procedure:

1. **Keep a per-PR disposition table** in the review record: every
   finding → ACCEPTED (with the fix commit) or DECLINED (with the
   repro/reason). Refuting a repeated or reversed finding then costs a
   one-line citation of your own record, not a re-investigation.
2. **Cap deep-evaluator rounds at ~2 per PR.** After two rounds,
   further deep rounds show diminishing returns (both KIT-0090
   oscillations occurred past that point). Stop, record the final
   disposition of anything open, and cite the table in the PR body.
   The cheap evaluator can keep running — cost≠signal (KIT-0084
   insight): the fast tier finds real bugs without oscillating.
3. A verdict below APPROVED with all findings dispositioned-and-cited
   is a legitimate gate-pass; say so explicitly in the merge-go.

## Step 4: Persist Output

Concatenate all evaluator outputs into a single review artifact tracked
in git. Use the aggregation pattern (fail-fast when no logs match) so
an empty review file can't silently mask evaluator failures. **The
snippet is bash-only** (`shopt`): harness shells may be zsh — run it
via `bash -c '…'` (KIT-0056 retro):

Both sides of this recipe are planning-repo paths — the glob reads the
logs the trio wrote there, and the redirect writes the Gate 5 record
beside them. Substitute the literal planning path for `"$PLANNING"`.

```bash
shopt -s nullglob
logs=("$PLANNING"/.adversarial/logs/<TASK-ID>-code-review-input--*.md)
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
} > "$PLANNING"/.kit/context/reviews/<TASK-ID>-evaluator-review.md
```

Include this file in your next commit. The same recipe appears in
`docs/CROSS-REPO-PATTERN.md` — keep the two in
sync when updating.
