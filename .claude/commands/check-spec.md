---
description: Check Spec Compliance
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Check Spec Compliance

Run the spec-compliance evaluator to verify all task requirements are implemented before committing.

**When**: After tests pass + self-review, BEFORE `/commit-push-pr`.

## Step 1: Identify the task

```bash
# Get task ID from branch name
git branch --show-current
```

```bash
# Find the task spec
ls delegation/tasks/3-in-progress/
```

## Step 2: Build the evaluator input

Create the input file at `.adversarial/inputs/<TASK-ID>-spec-compliance-input.md` using the template at `.adversarial/templates/spec-compliance-input-template.md`.

You MUST include:

1. **Full task spec** — copy the entire task file content
2. **Full source of every changed file** — use `git diff --name-only main` to find them, then include each file's complete content
3. **Full test file content** — for every test file that was modified

Use the Bash tool to read files and assemble the input. Do NOT summarize or truncate — the evaluator needs complete content to trace requirements to code.

## Step 3: Run the evaluator

```bash
adversarial spec-compliance-fast .adversarial/inputs/<TASK-ID>-spec-compliance-input.md
```

## Step 4: Read and act on results

The output lands in `.adversarial/logs/`. Read it and:

- **PASS** -> Proceed to `/commit-push-pr`
- **PARTIAL** -> Fix the gaps, re-run tests, re-run evaluator
- **FAIL** -> Fix critical gaps before proceeding

Report the verdict and any findings to the user.
