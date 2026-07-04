# KIT-0036: Pull-based consumer sync — engine extraction + `project sync`

**Status**: In Progress
**Priority**: high
**Assigned To**: unassigned
**Estimated Effort**: 6-10 hours (two PRs)
**Created**: 2026-07-03
**Target Completion**: TBD
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Parent ADR**: KIT-ADR-0026 (Pull-Based Consumer Sync — One Engine, Two
Callers) — **Accepted design; this task implements it. Read it first.**
**Related**: KIT-0026 (backlog: agents/skills tiers — lands later as a new
tier strategy on this engine), KIT-0034 (F3 temp-then-commit pattern this
engine embodies), KIT-0033 (KIT-LOCAL markers — constraint on the future
agents tier, not this task)

## Overview

Channel B (manifest sync) is push-only today: consumers wait for the kit
to merge to `main`, and all sync logic lives untested inside the
`sync-core-scripts.yml` heredoc. KIT-ADR-0026 decided to extract that
logic into one Python engine invoked by both the push Action and a new
consumer-side pull command, so any consumer can sync — selectively or
fully — from its own terminal in under two minutes.

This task delivers the engine, the tests, the workflow refactor, the
`project sync` wrapper, the `workflow_dispatch` trigger, and the
retirement of `check-sync.sh`. The ADR's Decision section is the design
spec; this file adds sequencing, acceptance criteria, and repo-specific
constraints.

## Implementation Phases (two PRs)

### PR 1 — Engine + tests + workflow refactor

- **D1: `scripts/core/sync_from_manifest.py`** — faithful port of the
  workflow heredoc logic per ADR §1:
  - Library-first: `sync(source, target, options) -> SyncReport`; CLI is
    a thin argparse layer. Stdlib only.
  - Tier rules: `*_core` always; `kit_builder` iff `--is-kit`; optional
    tiers iff in target `opted_in` (preserved verbatim).
  - Path mapping, directory-entry replacement **including stale-file
    cleanup** (files removed upstream inside a directory entry are
    removed downstream), and the not-previously-in-manifest overwrite
    warning — as the workflow does today.
  - `--tier` / `--only` narrowing; `--dry-run` (drift report, no
    writes). `--only` takes a **manifest entry key, exactly as it
    appears in the manifest JSON** (file entries: the path; directory
    entries: with trailing `/`) — never an arbitrary filesystem path.
    Unknown keys are a usage error (exit 2) whose message shows the
    near-miss (e.g. user typed the directory without the trailing
    slash). Test both slash forms: one accepted, one rejected clearly.
  - Two-pass application: stage to temp tree, apply in one final pass
    (KIT-0034 F3). No half-updated targets on failure. The full plan
    (every read of source + manifests) must be resident in memory
    before the first write — no disk reads of `scripts/core/` during
    the apply pass, since the engine may be overwriting itself.
  - Engine-computed completeness: complete sync updates `core_version` +
    `synced_at` and clears `partial_sync`; incomplete sync leaves
    `core_version` and writes `"partial_sync": true`. Under `--dry-run`
    the same verdict is computed and reported in the SyncReport
    (`would_bump_core_version` / `would_set_partial_sync`); nothing is
    written.
  - `SyncReport` includes a `removed_entries` field (entries present in
    the target's old manifest but absent upstream). This is the general
    mechanism behind the D6 removal announcement, not a one-off hack.
  - Exit codes: 0 clean/applied, 1 drift or applied-with-warnings,
    2 usage, 3 manifest missing/unrecognized, 4 source unreadable.
    Exit 1 deliberately conflates "drift found" and "applied with
    warnings" — both mean *human attention needed*; machine consumers
    needing finer discrimination read `--report-json`, whose
    `SyncReport.status` distinguishes them. State this in `--help`.
  - Per-tier strategy dispatch point (single strategy today:
    copy/replace).
  - Optional `--report-json <file>` emitting the SyncReport.
- **D2: pytest coverage** —
  - Characterization tests: fixture source+target trees in →
    tree-level property assertions out (files present, content, manifest
    fields). Not gold-file console output.
  - Dual-**entrypoint** contract test (PR 1 scope): same fixture through
    the library API (`sync()`) and through the CLI (as the Action calls
    it) → identical trees + manifests. PR 2 extends this to the third
    entrypoint (`project sync`) — only then is it a true dual-*caller*
    test; that extension is an explicit PR 2 acceptance criterion, not
    an implied one.
  - Self-sync test: a fixture whose source contains a **modified
    `scripts/core/sync_from_manifest.py`**; run the engine from that
    source against a target, assert the run succeeds and the target's
    engine file matches source. This is the one scenario production
    will always hit (the engine upgrading itself) — fixtures alone
    don't cover it.
  - Exit-code contract frozen by tests.
  - Edge cases: missing target manifest (fresh consumer), unknown
    manifest schema (exit 3), `--only` entry not in any tier (usage
    error), opted_in preservation, `partial_sync` set/cleared,
    **directory entry shrinks** (file removed upstream disappears
    downstream).
- **D2b: manifest entry for the engine lands in PR 1, not PR 2** — add
  `core/sync_from_manifest.py` to the `scripts_core` tier and bump
  `core_version` 2.1.0 → **2.2.0** (additive → minor) in the same
  commit as D1, or PR 1 fails its own manifest-count pre-commit hook.
  PR 2's D7 then carries only the `check-sync.sh` removal and the
  major bump.
- **D3: refactor `sync-core-scripts.yml`** — thin shell: checkout
  source+target, `python3 source/scripts/core/sync_from_manifest.py
  --source source --target target --is-kit ...`, commit, open PR.
  Behavior identical (characterization tests are the gate).
- **D4: `workflow_dispatch`** trigger on the Action with an optional
  `repo` input filtering the matrix.

### PR 2 — Pull wrapper + retirement + docs

- **D5: `project sync` subcommand** in `scripts/core/project` per ADR §2:
  - `resolve_source(ref) -> Path` seam; resolution order: `--source
    <dir>` → `gh api repos/<source_repo>/tarball/<ref>` → `git clone
    --depth 1 --branch <ref>`. `source_repo` read from the local
    manifest. Exit 4 + guidance message if none available.
  - `resolve_source` must **normalize to the repo root** regardless of
    transport: GitHub tarballs unpack into a nested
    `<owner>-<repo>-<sha>/` directory, clones don't. The engine always
    receives a path whose child is `scripts/` — transport quirks never
    leak into D1.
  - Flags: `--dry-run`, `--tier`, `--only`, `--ref` (default `main`),
    `--source`, `--no-branch`.
  - Default applies to a `chore/core-sync-<version>` branch and prints
    `git diff --stat`; never pushes or merges. `--no-branch` **refuses
    to run (exit 2)** if the working tree has uncommitted changes in
    paths the sync would touch — never overlay onto dirty work.
  - The wrapper branches its UX on `SyncReport.status` (via the library
    API or `--report-json`), **not** on the exit code — exit 1 covers
    both "drift found" and "applied with warnings", which need
    different messages.
  - On any non-empty `SyncReport.removed_entries`, print a prominent
    `Removed from sync unit:` block naming each entry and (where known)
    its replacement — this is how the `check-sync.sh` removal (D6)
    reaches consumers.
  - Complete the dual-caller contract test with the real wrapper path.
- **D6: retire `check-sync.sh`** — delete the script, remove its
  `scripts_core` manifest entry, add `sync_from_manifest.py`. Grep for
  references (docs, skills, commands, workflows) and repoint them to
  `project sync --dry-run`. The removal must be **announced, not
  silent**: the v3.0.0 sync PR body states it, and consumers see it via
  the generic `removed_entries` announcement in D5 — no one-off
  detection logic.
- **D7: version bumps** — `core_version` 2.2.0 (post-D2b) → **3.0.0**
  (removing `check-sync.sh` from the sync unit is a breaking removal);
  `scripts/core/VERSION` likewise. Manifest entry-count tests updated in
  the same commit as the removal.
- **D8: docs** — update `docs/DISTRIBUTION-ARCHITECTURE.md` (new pull
  channel; bump doc version to 1.1.0), `docs/MANIFEST-UPGRADE-GUIDE.md`
  (pull path + partial_sync semantics), and CHANGELOG per Keep a
  Changelog.

## Non-Goals

- No `agents_core` / `skills_core` tier (KIT-0026) — but the strategy
  dispatch point must make it addable without engine redesign.
- No auto-registration of consumers in the push matrix.
- No changes to Channel A (plugin) mechanics.

## Acceptance Criteria

- [ ] `pytest` green, incl. characterization, dual-caller, and
      exit-code tests; new-code coverage ≥ 80%
- [ ] Engine run against a local `--source` fixture completes in
      **under 5 seconds** (mechanical gate); the network tarball path
      is observed end-to-end on a real consumer checkout and recorded
      in the PR (best-effort, network-dependent — the 2-minute goal)
- [ ] `--tier commands_core` pull touches only that tier's files and
      sets `partial_sync: true`; a following full pull clears it and
      bumps `core_version`
- [ ] Push Action on a scratch branch produces a **file-tree-identical**
      result to the pre-refactor behavior for the same input, ignoring
      the `synced_at` timestamp (characterization fixtures); PR body
      and commit message may change and are asserted separately
- [ ] The dual-entrypoint contract test is extended to cover
      `project sync` as the third entrypoint (PR 2)
- [ ] `gh workflow run sync-core-scripts.yml -f repo=<one>` syncs only
      that repo
- [ ] `check-sync.sh` gone; no dangling references
      (`grep -rn "check-sync" --include="*.md" --include="*.sh" .`)
- [ ] `pattern_lint.py` clean on all new Python; DK rules followed
      (`encoding=` on open, no bare except, `==` for identifiers)
- [ ] Docs + CHANGELOG updated; `core_version`/`VERSION` bumped to 3.0.0

## Constraints & Footguns (repo-specific)

- **Manifest count tests**: tests enforce manifest entry counts against
  `scripts/core/` contents — update manifest and file adds/removes in
  the same commit or pre-commit fails.
- **`$()` subshells and `&&` chains** trigger permission prompts in
  agent sessions — keep new shell fragments in the workflow simple; the
  point is to move logic *out* of shell anyway.
- **`gh api` does not accept `--repo`** — tarball fetch must inline the
  owner/name path.
- **Two-pass rule is load-bearing**: per-item `mv` inside the apply loop
  reintroduces the KIT-0033 atomicity bug class. Stage everything, then
  move.
- **The engine syncs itself**: `sync_from_manifest.py` is in
  `scripts_core`. Ensure the apply pass doesn't re-read source files
  mid-apply (load plan fully before writing).
- **`--ref` predating the engine**: pulling a ref whose source tree
  lacks `sync_from_manifest.py` is fine (the *local* engine runs — it
  only needs the source's manifest and files), but a ref predating the
  tiered manifest itself must fail loudly with exit 3, not guess.
- **Don't touch `.kit/adversarial/`** (user-owned, untracked).

## References

- KIT-ADR-0026 — `.kit/adr/KIT-ADR-0026-pull-based-consumer-sync.md`
- Evaluator trail — `.kit/context/reviews/KIT-ADR-0026-evaluator-review.md`
- Current push logic — `.github/workflows/sync-core-scripts.yml:54-168`
- Retiree — `scripts/core/check-sync.sh`
- Manifest — `scripts/.core-manifest.json`
