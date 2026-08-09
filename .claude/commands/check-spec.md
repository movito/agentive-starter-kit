---
description: Check Spec Compliance
version: 1.4.0
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
wrong one. Resolve both roots before Step 1.

**Use the canonical parser; do not hand-roll a `grep`.**
`scripts/core/lib/target_repo.sh` is the runtime source of truth for what
counts as split mode: it requires BOTH `- **Path**:` and `- **GitHub**:`
under the `## Target Repository` heading, validates the GitHub value as
`owner/name`, and fails loudly otherwise. Accepting a `Path` alone can
enter split mode on a malformed section and read the wrong repo.

```bash
. scripts/core/lib/target_repo.sh
target_repo_init || exit 1     # non-zero = malformed config; report and stop
TARGET="${TARGET_PATH:-$(git rev-parse --show-toplevel)}"
echo "TARGET=$TARGET"
```

- **`TARGET_PATH` non-empty** → split mode; `TARGET` is the target repo.
- **`TARGET_PATH` empty** → single-repo mode; `TARGET` falls back to the
  current repo, so the commands below are unchanged.
- **Non-zero exit** → the section exists but is malformed (missing field,
  or a GitHub value that isn't `owner/name`). Report what the parser said
  and stop; do not guess which repo to read.

If the helper is unavailable (a consumer project that didn't install
`scripts/core/lib/`), require both fields and an `owner/name`-shaped
GitHub value yourself before treating it as split mode.

Every code-side command below is written `git -C "$TARGET"`, which is
correct in BOTH modes — that is why `TARGET` is set in single-repo mode
too. Task specs are always read from the planning repo (the current
directory), never through `$TARGET`.

> `$TARGET` does not survive between tool calls — each runs a fresh
> shell. Resolve it once and substitute the literal path into the
> commands you issue.

## Step 1: Identify the task

```bash
# The task ID comes from the CODE branch — in split mode that is the
# target's branch, not the planning repo's (which sits on main).
git -C "$TARGET" branch --show-current
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
   # Resolve the default branch instead of assuming `main`.
   BASE=$(git -C "$TARGET" remote show origin | sed -n 's/.*HEAD branch: //p')

   # Three dots, not two: `origin/$BASE...HEAD` diffs against the merge
   # base, so commits landed on the base since you branched are not
   # misreported as your changes. `origin/$BASE` (not the local branch)
   # is the honest base — a stale local copy silently widens or narrows
   # the set.
   git -C "$TARGET" fetch origin "$BASE"
   git -C "$TARGET" diff --name-only "origin/$BASE...HEAD"
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
