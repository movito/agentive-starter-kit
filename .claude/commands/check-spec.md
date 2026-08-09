---
description: Check Spec Compliance
version: 1.6.0
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

**Use the canonical parser rather than hand-rolling a `grep`** — it
resolves `CLAUDE.md`, extracts the fields, and validates the GitHub value
as `owner/name`:

```bash
if ! . scripts/core/lib/target_repo.sh 2>/dev/null; then
    echo "target_repo.sh unavailable — using the manual fallback below" >&2
else
    target_repo_init || exit 1   # bad owner/name format: report and stop

    # The helper does NOT reject a half-filled section (verified
    # 2026-08-09): with `Path` but no `GitHub` it returns 0 and sets
    # GIT_DIR_ARG while leaving GH_REPO_ARG empty. Split mode needs BOTH.
    if { [ -n "$TARGET_PATH" ] && [ -z "$TARGET_REPO" ]; } || \
       { [ -n "$TARGET_REPO" ] && [ -z "$TARGET_PATH" ]; }; then
        echo "ERROR: '## Target Repository' has only one of Path/GitHub — split mode needs both" >&2
        exit 1
    fi
fi
TARGET="${TARGET_PATH:-$(git rev-parse --show-toplevel)}"
echo "TARGET=$TARGET"
```

- **Both `Path` and `GitHub` set** → split mode; `TARGET` is the target repo.
- **Both absent** → single-repo mode; `TARGET` falls back to the current
  repo, so the commands below are unchanged.
- **Exactly one set, or a bad `owner/name`** → the section is malformed.
  Report which field is missing and stop; do not guess which repo to read.

**Manual fallback** (consumer projects without `scripts/core/lib/` — the
`if !` above routes here rather than exiting): read both values from the
`## Target Repository` section yourself, require BOTH plus an
`owner/name`-shaped GitHub value, and set `TARGET` to the `Path` value
(or the current repo when the section is absent).

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

   **Fail closed at each step.** Every command here can fail in a way
   that still produces a plausible-looking file list, and a wrong list
   means tracing the spec against the wrong changes — silently.

   ```bash
   # Resolve the default branch instead of assuming `main`.
   BASE=$(git -C "$TARGET" remote show origin | sed -n 's/.*HEAD branch: //p')

   # `remote show` prints `(unknown)` when the remote has no HEAD, and
   # nothing at all when it is unreachable — either way BASE is unusable.
   if [ -z "$BASE" ] || [ "$BASE" = "(unknown)" ]; then
       echo "ERROR: could not determine the default branch for origin" >&2
       exit 1
   fi

   # A failed fetch leaves the OLD origin/$BASE in place, so the diff
   # below would still 'work' and report a stale changed-file set. Stop.
   git -C "$TARGET" fetch origin "$BASE" || exit 1

   # Three dots, not two: `origin/$BASE...HEAD` diffs against the merge
   # base, so commits landed on the base since you branched are not
   # misreported as your changes. `origin/$BASE` (not the local branch)
   # is the honest base — a stale local copy silently widens or narrows
   # the set.
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
