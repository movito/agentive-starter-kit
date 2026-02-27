---
description: How to run the adversarial code-review evaluator after bot rounds and before human review
user-invocable: false
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Code-Review Evaluator

Run after bot triage rounds are complete, before human review. Uses a different model family (o1/Gemini) to find edge-case bugs that bots and Claude miss.

## When to Run

- After all bot threads are resolved (0 unresolved)
- Before requesting human code review

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
  > .agent-context/reviews/<TASK-ID>-evaluator-review.md
```

**When in doubt, run it.** The fast variant costs ~$0.004 and takes 30 seconds.

## Step 1: Prepare Input

Create `.adversarial/inputs/<TASK-ID>-code-review-input.md` using the template at `.adversarial/templates/code-review-input-template.md`.

Use the PR's original task ID. If the input file already exists from a previous run, append `-r2`:

- First run: `<TASK-ID>-code-review-input.md`
- Follow-up: `<TASK-ID>-code-review-input-r2.md`

**CRITICAL: Include FULL file content, not diffs or excerpts.** The evaluator cannot
reason about imports, error handling context, or module-level state from partial code.
Diff-only inputs produce false positives (high false positive rate observed empirically).

Include:
- Full source of all new/changed files (complete files, not diffs)
- Full test file
- Summary of what bots found and how it was addressed

## Step 2: Run the Evaluator

```bash
# Deep analysis (recommended for substantial PRs)
adversarial code-reviewer .adversarial/inputs/<TASK-ID>-code-review-input.md

# Fast variant (for small changes or iteration)
adversarial code-reviewer-fast .adversarial/inputs/<TASK-ID>-code-review-input.md
```

## Step 3: Read and Address Findings

Output lands in `.adversarial/logs/`:

```bash
# First run:
cat .adversarial/logs/<TASK-ID>-code-review-input--code-reviewer.md.md

# Follow-up:
cat .adversarial/logs/<TASK-ID>-code-review-input-r2--code-reviewer.md.md
```

| Verdict | Action |
|---------|--------|
| **FAIL** | Fix the identified bugs, push, and re-run the evaluator |
| **CONCERNS** | Address test gaps and robustness issues, push |
| **PASS** | Proceed to human review |

## Step 4: Persist Output

Copy to `.agent-context/reviews/` so it's tracked in git:

```bash
# First run:
cp .adversarial/logs/<TASK-ID>-code-review-input--code-reviewer.md.md \
   .agent-context/reviews/<TASK-ID>-evaluator-review.md

# Follow-up:
cp .adversarial/logs/<TASK-ID>-code-review-input-r2--code-reviewer.md.md \
   .agent-context/reviews/<TASK-ID>-evaluator-review-r2.md
```

Include this file in your next commit.
