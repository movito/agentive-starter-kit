# KIT-0125: wait-for-bots.sh resolves the PR against its own repo, not the caller's — false READY

**Status**: Todo
**Priority**: high (silent false-positive gate: exit 0 for the wrong PR)
**Type**: Script fix (`scripts/core/wait-for-bots.sh`, `scripts/core/check-bots.sh`)
**Estimated Effort**: ~1-2 h
**Created**: 2026-10-18
**Source**: Observed during KIT-0124 (agentive-skills#13 babysit, 2026-10-18).

## Observed

Run from `~/Github/agentive-skills` (no `scripts/core/` of its own) as
`~/Github/agentive-starter-kit/scripts/core/wait-for-bots.sh 13`:

```text
REVIEW:coderabbitai:CHANGES_REQUESTED:58ed0eddf841355164bc84b96a1373353331dc5b:2026-02-10T17:51:47Z
THREADS:Total:45,Resolved:13,Unresolved:32
BOT_STATUS:CodeRabbit:CURRENT
BOT_STATUS:BugBot:CURRENT
[exited with code 0]
```

That is the **kit's** PR #13 (February 2026). At the same moment
agentive-skills#13 had both bots `pending` and 0 review threads
(`gh pr checks 13` and GraphQL against `movito/agentive-skills`). The
gate reported READY for a PR nobody asked about, and printed nothing
that names the repo it checked.

## Root cause

Both scripts `cd "$PROJECT_ROOT"` — derived from the script's own
location (`$SCRIPT_DIR/../..`), not the caller's working directory —
before any `gh` call (`wait-for-bots.sh:22-24`, `check-bots.sh:43-45`).
With no `## Target Repository` in that root's CLAUDE.md,
`check-bots.sh:136` falls back to `gh repo view` in the script's repo.
`wait-for-bots.sh` has no `--repo` flag and does not forward one, so
the caller cannot override it even though `check-bots.sh` accepts
`--repo owner/name` (ID2-0014).

Normal consumer use (script inside the project it checks) is
unaffected. It bites whenever the script runs against a repo other
than its own: the marketplace repo (agentive-skills ships no
`scripts/core/`), a sibling checkout, or a plugin-installed command
invoking a script by absolute path.

## Scope

- R1 — `wait-for-bots.sh` accepts `--repo owner/name` and forwards it
  to every `check-bots.sh` call and to its own `gh pr view`
  auto-detect (line ~102).
- R2 — Both scripts print the resolved `owner/name` on the first
  output line (e.g. `REPO:movito/agentive-skills`), so a wrong-repo
  check is visible in the transcript.
- R3 — Decide (and record) whether the `cd "$PROJECT_ROOT"` should
  remain the default when the caller's CWD is a different git repo.
  Candidate: resolve the repo from the caller's CWD first, and only
  `cd` for sourcing `lib/` — or refuse with a clear error when CWD's
  repo differs from `$PROJECT_ROOT`'s and no `--repo` is given.
- R4 — Class grep: every `scripts/core/*.sh` that `cd`s to
  `$PROJECT_ROOT` before a `gh` call (`verify-ci.sh` likely shares the
  shape); fix or list each.
- R5 — `agentive review-helper` also refuses outside a kit project
  ("Not inside an agentive project"); add `--repo` there too, or
  document `gh`-direct as the supported path for non-kit repos (the
  babysit-pr command currently assumes it always works).

## Acceptance

- [ ] Red-first test: run `wait-for-bots.sh` from a different git repo
      with a PR number that exists in both → asserts it checks the
      caller's repo (or errors), never the script's own
- [ ] `wait-for-bots.sh --repo movito/agentive-skills 13` checks that
      repo's PR, from any CWD
- [ ] First output line names the repo checked, in both scripts
- [ ] R4 class grep recorded in the PR with each hit's disposition
- [ ] babysit-pr / wait-for-bots command docs mention `--repo`
