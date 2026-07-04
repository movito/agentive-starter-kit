# KIT-ADR-0026: Pull-Based Consumer Sync — One Engine, Two Callers

**Status**: Proposed
**Date**: 2026-07-03 (amended same day after adversarial review — see
Evaluation trail)
**Author**: Claude Code + User
**Supersedes**: None
**Related**: KIT-ADR-0022 (manifest sync ownership — the push channel this
complements), KIT-ADR-0024 (plugin/manifest distribution topology),
KIT-ADR-0025 (agent localization; KIT-LOCAL markers constrain any future
agent sync), `docs/DISTRIBUTION-ARCHITECTURE.md` v1.0.0 (the system map),
KIT-0026 (backlog: agents/skills tiers), KIT-0033 (KIT-LOCAL marker
vendoring)

## Context

`docs/DISTRIBUTION-ARCHITECTURE.md` describes two distribution channels:
the `agentive-workflow` plugin (Channel A, install-based) and the manifest
sync Action (Channel B, vendored files). Channel A already has a fast
consumer-side update path — `claude plugin update` takes seconds. Channel B
does not, and that is the gap this ADR addresses.

The operational goal: **a consumer can pull a specific upgrade, or
everything it is entitled to, from its own terminal in under two minutes**
— review the diff, commit, get back to work.

### What exists today, and why it falls short

1. **Push-only, upstream-initiated.** `sync-core-scripts.yml` fires when
   watched paths change on the kit's `main`, and opens PRs into a
   **hardcoded matrix** of three downstream repos. A consumer cannot ask
   for a sync; it waits for one. A consumer created via
   `create-project.sh` is not in the matrix and receives nothing at all.

2. **The sync brain is trapped in workflow YAML.** All the real logic —
   `should_sync_tier()` (core tiers always; `kit_builder` only when
   `is_kit`; optional tiers only when opted in), `resolve_paths()` (tier →
   source/target path mapping), `opted_in` preservation, stale-directory
   cleanup, overwrite warnings — lives as an inline bash heredoc in
   `.github/workflows/sync-core-scripts.yml` (~110 lines). It can only
   execute on a GitHub runner, has no tests, and cannot be reused by any
   local tool.

3. **`check-sync.sh` diagnoses but does not treat.** The one consumer-side
   tool detects drift by diffing against a **local kit checkout**
   (`ASK_REPO` env var) and then instructs the operator to copy files by
   hand. It also re-implements its own file-walk logic instead of reading
   the manifest — a second, divergent notion of "what should be synced."

4. **Manual copying bypasses the contract.** The fallback today — rsync or
   hand-copy from a local checkout — ignores tier rules and `opted_in`
   preservation, which is exactly how consumer customizations get
   clobbered. The 20-minute manual path is also the unsafe path.

The root cause across 2–4 is the same: **there is one sync contract (the
manifest) but three partial implementations of it** (the workflow heredoc,
`check-sync.sh`, and ad-hoc copying), only one of which is complete, and
that one is unreachable from a consumer terminal.

## Decision

Add a **pull channel to Channel B** by extracting the sync logic into a
single tested engine that both the existing push Action and a new
consumer-side CLI invoke. Three parts:

### 1. Extract the sync engine — `scripts/core/sync_from_manifest.py`

Move the tier/path/opt-in logic out of the workflow heredoc into a
standalone **Python** script in the `scripts_core` tier:

```
python3 scripts/core/sync_from_manifest.py \
    --source <upstream-dir> --target <consumer-dir> \
    [--tier <name>]... [--only <entry>]... [--dry-run] [--is-kit]
```

**Python, not Bash** (per arch review): the engine's work is JSON
manipulation, path resolution, and — once an agents tier lands —
per-tier merge strategies around KIT-LOCAL markers. Bash needs `jq` and
case-statement sprawl for that; Python is stdlib-only, matches the
existing `scripts/core` culture (`pattern_lint.py`,
`validate_task_status.py`), and is directly testable with pytest. The
workflow and the `project` wrapper both invoke it via `python3`; no
Bash shim is needed (the workflow runner and every consumer already
have Python — it is a `scripts_core` prerequisite today).

- Reads the **upstream** manifest for tier membership, the **target**
  manifest for `opted_in` (preserved verbatim, as today).
- `--tier` / `--only` narrow the sync to named tiers or individual manifest
  entries; default is everything the target is entitled to.
- `--dry-run` reports what would change (added / modified / removed) —
  this **subsumes and retires `check-sync.sh`**.
- Behavior is a faithful port of the workflow logic, including
  directory-entry replacement and the not-previously-in-manifest
  overwrite warning.
- **Two-pass application** (temp-then-commit, the KIT-0034 F3 pattern):
  stage every file/directory operation into a temp tree first, then
  apply to the target in one final pass. A failed sync never leaves the
  consumer half-updated, and the engine overwriting *itself* mid-run is
  a non-issue (Python has loaded the source before any file changes;
  the apply pass is plain file moves).
- **Explicit exit-code contract**, so all callers can branch
  programmatically: `0` = clean / applied, `1` = drift found
  (`--dry-run`) or changes applied with warnings, `2` = usage error,
  `3` = manifest missing/unrecognized schema, `4` = source unreadable.
  Documented in `--help` and frozen by tests.
- **Library-first, CLI-thin** (per arch review round 2): the engine is
  an importable function — `sync(source, target, options) ->
  SyncReport` — and the CLI a thin argparse layer that maps
  `SyncReport.status` to the exit codes above. Tests, the `project`
  wrapper, and any future tooling compose in-process instead of parsing
  stdout. An optional `--report-json <file>` emits the `SyncReport`
  for machine consumers.
- **Per-tier strategy dispatch**: tier handling goes through one
  dispatch point whose only strategy today is copy/replace. When an
  agents tier arrives, merge-with-KIT-LOCAL-markers registers as a
  second strategy instead of `if tier == ...` branches spreading
  through the engine.

`sync-core-scripts.yml` is refactored to a thin shell: checkout source and
target, call the engine, commit, open the PR. **One implementation, two
callers** — the CLI and the Action cannot drift apart, because there is
nothing to drift.

The engine ships in `scripts_core`, so **the sync machinery updates itself
through the channel it implements** — every consumer's pull tool is
refreshed by both push PRs and its own pulls.

**Testing contract**: (a) characterization tests porting the workflow's
current behavior (same fixture in → same file operations out) gate the
extraction; (b) a **dual-caller contract test** runs the engine via both
entry points (direct CLI invocation as the Action will call it, and
through `project sync`) against one fixture repo and asserts identical
resulting trees and manifests, so wrapper flag-translation can never
drift from engine semantics. Characterization fixtures assert
**tree-level properties** (which files exist, with what content),
not console output, so internals can be improved later without
gold-file churn.

### 2. Add the pull wrapper — `./scripts/core/project sync`

A new subcommand on the existing consumer entry point:

```bash
./scripts/core/project sync --dry-run             # what would change (~15 s)
./scripts/core/project sync                       # pull everything entitled
./scripts/core/project sync --tier commands_core  # one tier
./scripts/core/project sync --only core/preflight-check.sh   # one file
./scripts/core/project sync --ref v0.7.0          # pin to a tag, not main
```

Mechanics: obtain the upstream at `--ref` (default `main`) into a temp
dir, run the engine against it, print a `git diff --stat`, and commit to
a `chore/core-sync-<version>` branch (`--no-branch` applies to the
working tree for operators who want to review before committing).
Nothing is pushed or merged by the tool; the consumer reviews with plain
`git diff` and merges on their own schedule — the same review contract
as the push PRs.

**Fetch is pluggable, not `gh`-welded** (per arch review). Resolution
order:

1. `--source <dir>` — an existing local checkout/unpacked tree; no
   network, no auth. Also the escape hatch for air-gapped or
   non-GitHub-hosted consumers.
2. `gh api repos/<source_repo>/tarball/<ref>` — default when `gh` is
   authenticated; works for private repos, ~10–15 s.
3. `git clone --depth 1 --branch <ref>` — fallback when `gh` is absent
   but git credentials exist.

If none is available the wrapper fails with exit code `4` and a message
naming all three options — the operator never hits a raw auth stack
trace. The `source_repo` slug comes from the local manifest, not a
hardcoded URL. The three modes sit behind a single
`resolve_source(ref) -> Path` seam in the wrapper, so a fourth
transport later is an added resolver, not a rewrite.

`--is-kit` is inferred from the local manifest/config rather than the
Action matrix, so repos outside the matrix are first-class citizens of the
pull channel.

### 3. Add `workflow_dispatch` to the push Action

A `workflow_dispatch` trigger with an optional repo filter, so
`gh workflow run sync-core-scripts.yml -f repo=movito/dispatch-kit` can
open an on-demand push PR without waiting for a merge to `main`. This is a
few lines, covers consumers that have not yet pulled the new tooling, and
gives the operator a remote-initiated path when working outside the
consumer checkout.

### Explicitly out of scope (fast-follow)

- **Agents in the pull path.** Agents remain outside Channel B (per
  KIT-ADR-0025 / the KIT-0026 backlog item). When an `agents_core` tier is
  added, agent entries must route through the KIT-LOCAL marker merge
  (`kit_markers.py`, currently `scripts/local/` — it would need promotion
  to `scripts/core/` at that point). The engine's `--tier` interface is
  designed so this lands as a new tier plus a per-tier merge strategy, not
  a redesign.
- **Auto-registration of new consumers in the push matrix.** The pull
  channel deliberately reduces the pressure on matrix membership; matrix
  hygiene stays a manual concern for now.

## Consequences

### Positive

- **Two-minute sync is real**: tarball fetch (~10–15 s) + engine run
  (seconds) + diff review + commit fits the budget with room to spare.
- **One source of truth for sync semantics**, tested with pytest like the
  rest of `scripts/core`, instead of an untestable workflow heredoc plus
  two divergent partial copies.
- **Selective upgrades** (`--tier`, `--only`) become possible for the
  first time; today's channel is all-or-nothing per push.
- **Version-pinned pulls** (`--ref vX.Y.Z`) let a consumer align with a
  known-good kit release instead of whatever `main` holds.
- **Consumers outside the Action matrix** (anything from
  `create-project.sh`) get a working Channel B for the first time.
- `check-sync.sh` retires; one fewer parallel implementation to maintain.

### Negative / accepted costs

- The engine must be a **byte-faithful port** of the workflow logic before
  any behavior change; a subtle porting difference would produce
  different results via push vs pull. Mitigation: port first with
  characterization tests (same inputs → same file operations), refactor
  the workflow to call it in the same PR, change behavior only after.
- The fastest fetch path still wants authenticated `gh`; the fallbacks
  (`--source` dir, shallow clone) keep the tool usable everywhere but
  add a support surface of three fetch modes to document and test.
- Two initiation paths (push PRs and local pulls) can race: a pull
  branch and a push PR touching the same files. Low harm — both derive
  from the same upstream state, so the later merge is a no-op or a
  trivial conflict — but the runbook should say "close the stale one."
- Partial pulls create a mixed-version tree, and the manifest must say
  so **explicitly and mechanically** (per both reviews — a stale
  `core_version` that silently misdescribes the tree is worse than no
  version). Rule: the **engine computes completeness itself** by
  comparing the effective sync set against the target's full
  entitlement — callers never assert "this was a full pull." A complete
  sync updates `core_version` + `synced_at` and clears any partial
  marker; an incomplete one leaves `core_version` untouched and writes
  `"partial_sync": true` into the manifest. `--dry-run` reports the
  mixed state, and the next complete pull (or push PR) clears it.

### Risks

- **Manifest schema evolution**: engine and manifest now version together
  across two repos' timelines (upstream engine vs downstream manifest).
  The engine must fail loudly on a manifest whose shape it does not
  recognize, never guess. Corollary invariant: **the engine's contract
  is with the manifest schema, not with the source's engine version** —
  a pull always runs the *consumer's* engine against the *source's*
  manifest (so `--ref` can point at any ref, including ones predating
  the engine), and any manifest-schema change must trip the loud-fail
  path rather than be reinterpreted.
- **Partial-pull drift**: `--only` makes it possible to hold a mixed-version
  tree indefinitely. `--dry-run`'s drift report is the countermeasure;
  the push PRs remain the periodic "converge everything" forcing function.

## Alternatives considered

1. **git subtree / submodule for `scripts/core`.** Rejected: fights the
   KIT-LOCAL vendoring model and the "consumer reviews a plain PR"
   contract; submodules leak into every consumer clone/CI; subtree merges
   are notoriously confusing for exactly the audience this kit serves.
2. **Blind rsync from a local kit checkout.** Rejected: fast but bypasses
   tier rules and `opted_in` preservation — it is the failure mode this
   ADR exists to eliminate, not a solution.
3. **A second, independent pull script (leave the workflow untouched).**
   Rejected: two implementations of the sync contract *will* drift; the
   whole lesson of `check-sync.sh` is that partial reimplementations rot.
4. **Plugin-only distribution (drop Channel B).** Rejected: Channel B
   exists because some files must physically live in the consumer tree
   (scripts consumers execute, `.kit/` scaffolding); a plugin install
   cannot satisfy that (KIT-ADR-0024).
5. **Widening the push matrix instead of adding pull.** Rejected as the
   primary fix: it keeps sync upstream-initiated (the 2-minute goal is
   consumer-initiated), requires `CROSS_REPO_TOKEN` scope for every new
   repo, and still offers no selective or pinned sync. Retained only as
   the `workflow_dispatch` convenience (§3).

## Evaluation trail

- **Round 1** (2026-07-03): `arch-review-fast-v2` (gemini-3-flash) →
  APPROVED; `arch-review` (o3) → REVISION_SUGGESTED. Amendments folded
  in: engine implemented in Python not Bash; pluggable fetch resolution
  (`--source` dir / `gh` tarball / shallow clone) replacing the hard
  `gh` dependency; explicit exit-code contract; engine-computed
  completeness with a `partial_sync` manifest marker replacing the
  caller-asserted partial-pull rule; two-pass temp-then-commit
  application (atomicity + safe self-update); dual-caller contract test.
- **Round 2** (2026-07-03): `arch-review` (o3) on the amended text →
  REVISION_SUGGESTED, explicitly "none are blocking for the initial
  extraction." All five findings folded in: library-first engine API
  (`sync() -> SyncReport`) with thin CLI; optional `--report-json`;
  per-tier strategy dispatch point; `resolve_source()` seam in the
  wrapper; tree-property (not gold-file) characterization fixtures.
  `arch-review-fast-v2` re-check on the final text → APPROVED.

  Review logs: `.kit/context/reviews/KIT-ADR-0026-evaluator-review.md`.
