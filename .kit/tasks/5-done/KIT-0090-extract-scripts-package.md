# KIT-0090: ADR-0028 phase 1 — extract the lifecycle scripts into a published PyPI package

> **Disposition (planner, 2026-08-07)**: DELIVERED — agentive-kit 0.1.0
> live on PyPI (tag `agentive-kit-v0.1.0` on d11075f, trusted
> publishing, run 31209733516). Four stacked PRs #108–#111 merged in
> order, fully gated. KIT-0086 and KIT-0079 closed by reference. The
> F1 surfaces deferred in PR #110 (preflight / review-input / worktree
> lib — a rewrite, not an extraction) are split to **KIT-0091** (phase
> 1b, evaluated + in todo). Phases 2–4 of ADR-0028 are separate tasks,
> specced sequentially. Retro owed by the implementing session; the
> worktree stays until it lands.

**Status**: Done
**Priority**: high (the accepted architecture's first work item; everything parked in the queue waits on it)
**Type**: Infrastructure / migration
**Estimated Effort**: 2-4 days (stacked PRs — see PR Plan)
**Created**: 2026-08-06
**Source**: KIT-ADR-0028 (Accepted 2026-08-06), Decision §2 + Consequences §Migration step 1
**Evaluation**: arch-review-fast APPROVED 2026-08-06 after 1 revision round (typed boundary models accepted; SCM interface declined as YAGNI — `gitio` single-module encapsulation instead; evaluator scope resolved by boundary statement). Log: `.adversarial/logs/KIT-0090-extract-scripts-package--arch-review-fast.md`

## Overview

Extract `scripts/core/` — the project lifecycle (`project`), doctor +
`doctor.d/`, preflight, review-input helpers, and the worktree helper —
into a versioned Python package, distributed exactly like
`adversarial-workflow`: installed and updated with
`uv tool install <name>`. This is the step that ends the copy-machinery
era for scripts AND the step that fixes the maintainability complaint
(2,564-line `project`, 2,000-line test files): a real package means
modules of normal size with per-module tests (KIT-0089 F3 rides here).

**Package name**: `agentive-kit` — verified available on PyPI
2026-08-06 (HTTP 404; the bare `agentive` is TAKEN, HTTP 200). The
console-script name is decided at implementation: `agentive` as a
binary name risks colliding with the existing `agentive` PyPI project's
entry points — check what that dist installs before claiming the name;
`akit` is the fallback.

## Requirements

- **F1 — package skeleton + module split.** A `src/agentive_kit/`
  package: `lifecycle` (start/move/complete + coordination metadata),
  `doctor/` (one module per check, replacing the doctor.d shell files
  where practical — shell checks may remain as data files run by a
  Python driver; decide per check and record), `evaluators` (install-
  evaluators incl. the KIT-0083 CLI half), `preflight`, `review_input`,
  `worktree`, and `gitio` — ALL git invocations live in `gitio`, one
  module (this is where the KIT-0080 portable resolvers land; it keeps
  the portability discipline greppable in one place — deliberately NOT
  a pluggable SCM interface: no other SCM is on any horizon, and the
  single-module boundary already buys the encapsulation an interface
  would, without the framework; evaluation finding declined as YAGNI
  with this rationale). No module over ~800 lines (KIT-0089's guideline
  becomes real here). Data crossing module boundaries or emitted by the
  CLI uses explicit typed models (`dataclasses` + type hints — not
  loose dicts), so the internal contracts are readable and testable
  (evaluation finding, accepted).
- **F2 — CLI compatibility.** A console entry exposing the existing
  subcommand surface (`<cli> start|move|complete|doctor|
  install-evaluators|linearsync|…`). **Root discovery changes**: the
  script today resolves the project from its own file location; a
  global tool must resolve from CWD (walk up to a `.kit/` + CLAUDE.md
  kit-install marker; refuse with a clear message when none found —
  never operate on a guessed root). This is the highest-risk behavioral
  change in the extraction; test it explicitly (nested dirs, worktrees,
  split-pair planning repos, non-kit dirs).
- **F3 — tests migrate WITH the split.** Per-module test files replace
  the monoliths for extracted code (KIT-0089 F3; its acceptance
  criterion closes by reference to this PR). Existing behavior is the
  spec: the current test suite passes against the package before any
  behavior change is allowed in.
- **F4 — publish.** PyPI release with a versioned tag and a minimal
  publish workflow (the `adversarial-workflow` release shape is the
  precedent). First release 0.1.x; the kit's README/docs note it is
  pre-consumer-migration.
- **F5 — the kit dogfoods it.** The kit repo consumes the package
  (dev-install in the venv); `./scripts/core/project` becomes a thin
  shim delegating to the installed CLI, kept for exactly one release
  cycle with a deprecation note. `scripts/.core-manifest.json` and the
  sync engine are NOT touched in this phase (retirement is phase 4).
- **F6 — carried fixes land inside, not alongside.** KIT-0086's
  skip-when-not-on-main handoffs guard and KIT-0079's config.yml pin
  reader (+ deleting `test_library_pin_mirrors_agree`) are implemented
  IN the extracted modules — closing both tasks by reference — rather
  than patched into the legacy script first and extracted second.

## Acceptance Criteria

- [ ] `uv tool install agentive-kit` on a clean machine + any existing
      kit-made repo → `<cli> doctor` runs correctly from the repo root
      and from a subdirectory; refuses loudly outside a kit repo
- [ ] Full existing test suite green against the package (behavior
      unchanged); new per-module test layout; no module > ~800 lines
- [ ] Package published on PyPI; install + upgrade path documented in
      README Requirements
- [ ] The kit repo itself runs on the package (shim in place, one-cycle
      deprecation note)
- [ ] KIT-0086 and KIT-0079 closed by reference (guard + pin reader
      inside the package; drift test deleted)
- [ ] Portability holds: the package's git resolution keeps the
      KIT-0080 portable pattern and the 2.30 floor; stub-git fixtures
      migrate with their modules

## PR Plan (required — this exceeds one PR)

Stacked or sequential: (1) package skeleton + lifecycle module + shim,
(2) doctor migration, (3) evaluators/preflight/review-input/worktree,
(4) publish workflow + README + dogfood switch. Each PR green and
shippable; STACKED-PR-WORKFLOW.md governs.

## Out of Scope

- Phase 2 (door switches to package-install mode for new projects),
  phase 3 (consumer migration via upgrader), phase 4 (sync-machinery
  retirement + dissolved-task dispositions) — each is its own task,
  specced after this lands
- The plugin channel (agents/skills/commands) — already exists; its
  "only channel" switch is phase 2 door work
- Linear sync behavior changes, evaluator library contents
- Evaluator EXECUTION: the `evaluators` module's scope is provisioning
  only (install the library + CLI, read pins). Running evaluations is
  and remains `adversarial-workflow`'s job — an external package with
  its own release cycle. No evaluator framework, interface, or plugin
  mechanism lands here (evaluation finding resolved by boundary
  statement: the extensibility home is the external package, not this
  one).

## Notes

- Open per-repo question deferred to phase 2: where the CLI pin is
  recorded per-repo (config.yml adjacency vs floating floor).
- Sequencing within the queue: this is the ONLY active assignment;
  KIT-0085/0075/0078/0087 stay parked until phases 1-2 clarify what
  survives of their surfaces.
