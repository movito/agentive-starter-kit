---
description: Check Spec Compliance
version: 1.2.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-08-09
created-by: "@movito with planner2"
---

# Check Spec Compliance

Verify that all task requirements are implemented before committing.

**When**: After tests pass + self-review, BEFORE `/commit-push-pr`.

## Step 0: Resolve the repos

In cross-repo mode the spec lives in the planning repo while the code
lives in the target repo, so a bare `git` command answers about the
wrong one. Detect the topology and fix both roots before Step 1:

```bash
grep -A 5 "## Target Repository" CLAUDE.md 2>/dev/null || echo "SINGLE_REPO_MODE"
```

- **SINGLE_REPO_MODE** → `TARGET` is the current repo; `git` commands
  below need no routing.
- **Split mode** → `TARGET` is the `- **Path**:` value from that
  section. Route every code-side command as `git -C "$TARGET" …`.
  Task specs stay in the planning repo (the current directory).

## Step 1: Identify the task

```bash
# Get task ID from the code branch (split mode: git -C "$TARGET")
git branch --show-current
```

```bash
# Find the task spec — always in the planning repo
ls .kit/tasks/3-in-progress/
```

## Step 2: Assemble the material

Gather everything the trace needs. The template at
`.adversarial/templates/spec-compliance-input-template.md` gives the
structure; write the assembled material to
`.adversarial/inputs/<TASK-ID>-spec-compliance-input.md` if you want a
durable record (KIT-0072 will feed this same file to the evaluator).

You MUST have in front of you:

1. **Full task spec** — the entire task file content
2. **Full source of every changed file** — discover them against the real
   merge base, in the repo the code lives in:

   ```bash
   # Split mode: prefix every git call with -C "$TARGET".
   # Three dots, not two: `main...HEAD` diffs against the merge base, so
   # commits landed on main since you branched are not misreported as
   # your changes. `origin/main` (not local `main`) is the honest base —
   # a stale local main silently widens or narrows the set.
   git fetch origin main
   git diff --name-only origin/main...HEAD
   ```

   Then read each file completely.
3. **Full test file content** — for every test file that was modified

Do NOT summarize or truncate — tracing requirements to code needs complete
content, and a partial read is how a requirement gets marked implemented
when it isn't.

## Step 3: Trace the spec yourself

> **The `spec-compliance` evaluator is not installed** (KIT-0069 / A35).
> It was never a library evaluator — it originated as a dispatch-kit
> project-local custom evaluator and did not survive the port into this
> kit. `adversarial spec-compliance-fast` therefore matches nothing;
> do not run it. **KIT-0072** tracks upstreaming it into the
> adversarial-evaluator-library, after which this step becomes an
> evaluator call again.

Until then, do the trace directly. For each numbered requirement and each
acceptance criterion in the task spec, record:

- **Implemented?** YES / PARTIAL / NO — with the `file:function` that
  implements it
- **Tested?** YES / NO — with the test that covers it
- **Evidence**: a brief code reference

Then check for spec drift in both directions:

- Does the implementation add behavior the spec never asked for?
- Does it change the spec's intent rather than satisfy it?
- Were there implicit requirements the spec assumed but never stated?

## Step 4: Report

- **PASS** — every requirement traced to code AND a test -> proceed to
  `/commit-push-pr`
- **PARTIAL** — some requirements traced; list the gaps, fix them, re-run
  tests, re-trace
- **FAIL** — core requirements unimplemented; fix before proceeding

Report the verdict and the per-requirement trace to the user. State
plainly that this was a manual trace, not an evaluator run.
