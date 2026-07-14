# Changelog

All notable changes to the Agentive Starter Kit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2026-07-14

The kit-stabilization release: seven hardening tasks (KIT-0034 →
KIT-0044), the worktree session topology, and a clean board — downstream
project upgrades were deliberately deferred to the next phase.

### Added

- **Preflight completion gates hardened across three passes** (KIT-0034,
  KIT-0042, KIT-0043):
  - Gate 2 (CodeRabbit) gains a fallback — commit-status pass + latest
    review APPROVED + zero unresolved threads — ending the SHA-exact
    false negatives that hit three consecutive tasks. (Verified surfaces:
    CodeRabbit = commit statuses, BugBot = check-runs.)
  - Gate 1 distinguishes PENDING from FAIL: unregistered runs and
    non-terminal unknown statuses are PENDING, an at-cap run list is
    PENDING (never PASS, `CI_RUN_LIMIT` knob), and a completed
    non-success run still FAILs.
  - Gates 5/6 support multi-task bundle PRs via the lead-task +
    pointer-files convention; FAIL messages name the convention (and the
    multi-PR-task case), and zero-byte pointer files no longer satisfy
    the gates (`-type f -size +0c`). Gate 7 prefix boundary fixed
    (`KIT-0004` can no longer match `KIT-0040-*`).
- **`upgrader` agent** (KIT-0032) — automates the ongoing plugin-upgrade
  runbook (`docs/PLUGIN-UPGRADE-GUIDE.md`): pin bumps, manifest sync,
  local `model:` pin refresh, Provenance restamp.
- **Worktree-based implementation sessions** (KIT-0044, piloted in
  KIT-0043): `scripts/local/new-worktree.sh` creates a fully-provisioned
  per-task worktree from fresh `origin/main` (enumerated artifact list:
  `.venv`, `.env`, `.adversarial/evaluators/`); un-skippable LAUNCH block
  in the task-starter template; `WORKTREE-WORKFLOW.md` documents
  topology, the pre-commit `GIT_DIR` contract with its `core.bare`
  canary, closeout, and lifecycle; the bare-hub layout is evaluated and
  declined with recorded revisit triggers. Eliminates the
  shared-clone/wrong-branch hazard class.
- **Suite-wide `GIT_*` test isolation** (`tests/conftest.py`) — after a
  pre-commit-in-worktree subprocess leak flipped `core.bare` on the real
  repo, all tests now run under a cleaned git environment; validated by
  a hostile-`GIT_DIR` canary run.
- **Fable-5 agent variants** — `feature-developer-f5` and `planner-f5`
  (PRs #66, #68), plus semver `version:` frontmatter and refreshed model
  pins across all agents (#61) and a distribution-architecture overview
  (`docs/DISTRIBUTION-ARCHITECTURE.md`, #62).
- **Workflow codification** (KIT-0037/38/39, KIT-0034):
  `STACKED-PR-WORKFLOW.md` (retarget-after-squash-merge recipe, the
  base-retarget-doesn't-trigger-CI gotcha), `TEMP-THEN-COMMIT-PATTERN.md`
  (atomic multi-file script mutations), and self-review checklist items
  8–10 (wrapper exit-code convention, scoped staging, verify shipped
  hints against installed tools).

### Changed

- **`ci-check.sh` warns on venv Black version drift** against the
  `pyproject.toml` pin (KIT-0035) — stale-venv phantom failures now read
  as environment issues; warn-only, the format gate is unchanged.
- **Evaluator trio runs before PR open for doc-dominated tasks**
  (KIT-0035, adopted into the code-review-evaluator skill and both
  feature-developer agents) — validated twice with zero-noise first bot
  rounds.
- **`prepare-review-input.sh` 1.5.1** — non-TTY large-input evaluator
  runs use the verified `echo y |` confirm pattern; the previously
  advertised `ADVERSARIAL_UNATTENDED` flag never existed in the installed
  library (KIT-0035 → KIT-0044).
- **`docs/PLUGIN-UPGRADE-GUIDE.md` detection greps hardened** and
  `.claude/agents/upgrader.md` re-synced in lockstep (KIT-0035).
- **`sync-core-scripts.yml` push trigger parked** — `CROSS_REPO_TOKEN`
  was never provisioned (22/22 failed runs since 2026-03-09);
  dispatch-only until KIT-0045 re-enables it deliberately, with the
  re-enable checklist embedded in the workflow file. Matrix `fail-fast`
  disabled so one leg can't mask the others.
- **Dependency floors refreshed** (dependabot #46–#50, #55):
  `pytest>=9.1.1`, `pytest-asyncio>=1.3.0`, `ruff>=0.15.21`,
  `python-dotenv>=1.2.2`, `gql>=4.0.0`; `actions/checkout@v7`.
- **Core scripts 3.1.0** (two consumer-visible script changes on top of
  the 3.0.0 sync-engine major).

### Fixed

- **`kit_markers.py` marker-merge robustness** (KIT-0040 F3, resolves the
  two BugBot findings open on PR #58 since the KIT-0033 merge):
  - A prose mention of a region's BEGIN marker inside another (preserved)
    region no longer aborts re-bootstrap as "malformed" — the malformed
    check is now line-anchored instead of a raw substring test.
  - Benign whitespace drift inside a marker line (extra spaces/tabs) no
    longer makes the region unparseable — previously a drifted marker
    silently replaced customized consumer content with placeholder TODO
    text on re-bootstrap. Drift beyond the whitespace tolerance is now
    *detected* by a deliberately looser line-anchored check and fails
    fast instead of clobbering. Well-formed and drifted regions still
    round-trip byte-for-byte.

### Added

- **Stub-`gh` regression harness for `preflight-check.sh`**
  (`tests/test_preflight_check.py`, KIT-0040 F1) — runs the real script
  against canned `gh` payloads via a fake `gh` on PATH, covering the
  KIT-0034 8-state verification matrix (Gate 2 status/check-run fallback,
  fail-closed paths, Gate 1 PENDING vs FAIL precedence) in CI. The script
  itself stays shell + gh; the stub pattern is reusable for other
  shell+gh scripts.
- **Task moves now sync coordination metadata** (KIT-0040 F2) —
  `./scripts/core/project move|start|complete|block` rewrites the moved
  task's numbered-folder path in `.kit/context/agent-handoffs.json` and
  the task's `HANDOFF-*.md` files, so status moves no longer strand stale
  paths for CodeRabbit to flag. Re-running a move for a task already in
  place doubles as a metadata repair.

- **Pull-based consumer sync — one engine, two callers** (KIT-0036,
  KIT-ADR-0026). Core scripts sync (Channel B) gains a consumer-initiated
  pull path alongside the existing push Action.
  - New `scripts/core/sync_from_manifest.py` — a single, tested Python engine
    (`sync(source, target, options) -> SyncReport`; thin argparse CLI) that
    both the push Action and the new pull command invoke, so the two cannot
    drift. Two-pass temp-then-commit apply (safe self-update, exec-bit
    preserving), engine-computed `partial_sync` completeness, a frozen
    exit-code contract (0 clean/applied · 1 drift/warnings · 2 usage · 3
    manifest · 4 I/O), and path-traversal / destructive-misuse guards.
  - New `./scripts/core/project sync` subcommand — pull core files on demand:
    `--dry-run`, `--ref <tag>`, `--source <dir>`, `--tier`, `--only`,
    `--no-branch`. Fetch resolves `--source` dir → `gh api` tarball → shallow
    clone. Defaults to a `chore/core-sync-<version>` branch; nothing is pushed
    or merged — the consumer reviews a plain diff.
  - `workflow_dispatch` on `sync-core-scripts.yml` with an optional `repo`
    input (guarded by a `validate-dispatch` job) for on-demand pushes.
- **Portable downstream agents via KIT-LOCAL markers** (KIT-0033) — resolves
  the four PR #57 bot threads on under-scaffolded consumer bootstrap.
  - `planner.md` and `feature-developer.md` wrap their consumer-customizable
    sections (Project Context, and Stack Notes for feature-developer) in
    stable `<!-- BEGIN/END KIT-LOCAL: <region> -->` markers. ASK's own filled
    content is unchanged — only the markers and a short mechanism note are
    added.
  - New `scripts/local/kit_markers.py` (stdlib-only) merges marker regions:
    fresh bootstrap seeds them with consumer-neutral placeholders (no kit
    identity); re-bootstrap preserves the consumer's filled regions
    byte-for-byte while refreshing agent structure *outside* the markers.
    Without markers the only safe rsync mode is `--ignore-existing`, which
    leaves consumers stuck on whatever agent version they first bootstrapped.
  - `bootstrap-consumer.sh` provisions a working `.kit/` skeleton
    (`tasks/1-backlog … 7-blocked`, `context/`,
    `templates/TASK-STARTER-TEMPLATE.md`) so the shipped V2 planner +
    feature-developer workflows run on day one, and marker-merges the two
    agents instead of rsyncing them blindly.
  - New `--no-kit` opt-out flag: skips the `.kit/` scaffold and drops
    `planner.md` / `feature-developer.md`, with a one-line summary of what
    was skipped.
  - `tests/test_kit_markers.py` covers the merge logic, including the
    re-bootstrap byte-preservation guarantee.

### Changed

- **`./scripts/core/project sync` now means core-file sync, not Linear sync**
  (KIT-0036) — **BREAKING**. `sync` was previously an alias for `linearsync`;
  it now runs the manifest sync engine. Use `linearsync` (or `linear`) for
  Linear task sync. Reflected in the core-scripts major bump to **3.0.0**.
- **`sync-core-scripts.yml` refactored to a thin shell around the sync engine**
  (KIT-0036) — all tier/path/opt-in/cleanup logic now lives in the tested
  `sync_from_manifest.py`; behavior is gated by characterization tests.
- **Planner and feature-developer agents consolidated** (PR #57) — versioned
  suffixes dropped, one canonical agent per role.
  - `planner.md` rewritten as **v2.0.0**: phased + gated workflow modeled on
    feature-developer-v6, with first-class single-repo / split-repo topology
    detection, 8 phases (triage → spec → eval → handoff → assignment →
    monitor → review → completion), gates on evaluation and review, and
    explicit branch-isolation guardrails for split mode.
  - `feature-developer.md` rewritten as **v2.0.0**: canonical Opus-class
    agent (`claude-opus-4-8`) consolidating v6's template structure with
    v7's filled-in ASK Project Context and Stack Notes (pytest, DK
    pattern_lint, pre-commit gauntlet, defensive coding rules, evaluator
    paths, task lifecycle).
  - Both adopt EXTENSION POINTs for downstream customization and the same
    Repository Topology detection (`grep '## Target Repository' CLAUDE.md`).
  - `bootstrap-consumer.sh` now ships `planner.md` downstream alongside
    `feature-developer.md` (was: `planner.md` excluded), and sweeps retired
    agent variants with `rm -f` before rsync so re-runs against existing
    consumer checkouts do not leave legacy defs side-by-side.
- **Live invocations repointed** to the canonical agents in `bootstrap.md`,
  `create-project.md`, `scripts/local/bootstrap.sh`,
  `scripts/optional/create-project.sh`, `retro.md`, and
  `.kit/docs/LINEAR-SYNC-BEHAVIOR.md`. Top-level docs refreshed: `CLAUDE.md`
  agent table, `README.md` create-project blurb, `.kit/docs/tmux-tips.md`
  example commands.

### Removed

- **`scripts/core/check-sync.sh`** (KIT-0036) — retired in core **3.0.0**. It
  diagnosed drift against a local kit checkout but could not treat it and
  re-implemented its own file-walk. Replaced by `./scripts/core/project sync
  --dry-run` (reports drift) and `./scripts/core/project sync` (applies it),
  both driven by the manifest. Consumers are notified via the sync engine's
  generic `removed_entries` announcement.
- **`.claude/agents/planner2.md`** and **`.claude/agents/planner3.md`** —
  content consolidated into the canonical `planner.md`.
- **`.claude/agents/feature-developer-v3.md`**,
  **`.claude/agents/feature-developer-v6.md`**, and
  **`.claude/agents/feature-developer-v7.md`** — content consolidated into
  the canonical `feature-developer.md`.

### Added

- **KIT-0033 backlog task** (`.kit/tasks/1-backlog/`) — portable agents
  downstream: marker-based Project Context / Stack Notes overwrite,
  `.kit/` skeleton scaffolding during bootstrap, F3 opt-out, and
  re-bootstrap refresh that survives both consumer customization regions.
  Captures the deferred work that surfaced via PR #57 bot review.
- **`bootstrap-consumer.sh --no-kit` now prunes pre-existing kit agents**
  on re-run (#68), `feature-developer-f5` wired into
  `KIT_AGENTS`/`AGENT_EXCLUDES` (#66), and a marker-membership test
  guards the whole class mechanically (KIT-0034).
- **Worktree provisioning symlinks gitignored** so `git worktree remove`
  works cleanly after a session (KIT-0044).

## [0.7.0] - 2026-06-13

### Fixed

- **`setup_logging` idempotency guard** — now keys on its own tagged
  handlers rather than "any handler present." A foreign handler (e.g. the
  log-capture handler pytest 9.1.x attaches to the logger under test) no
  longer makes `setup_logging` return early and skip level/handler
  configuration, which had made `tests/test_logging.py` fail under the
  CI pytest version while passing on older local pytest.
- **CI lint step** — `flake8` added to the `[dev]` extras in
  `pyproject.toml`. The `test.yml` Lint job invokes bare `flake8` after
  `pip install -e ".[dev]"`, but flake8 was missing from the extra, so
  the lint job failed with exit 127 (`command not found`) on every PR.

### Added

- **Cross-repo config preflight check** (KIT-0030, KIT-ADR-0024 §2) —
  `scripts/core/check_cross_repo_config.py` fails CI when a repo
  *declares* the cross-repo split (a concrete `../<name>-code` sibling
  path or planning-split prose in README/CLAUDE.md) but CLAUDE.md lacks a
  parseable `## Target Repository` section; warns when the section exists
  but the target is not checked out locally (planning repo stays usable
  without it). Wired as step 6 of `scripts/core/ci-check.sh`. The portable
  cross-repo *tooling* is deliberately not treated as a declaration, so
  single-repo projects (including this kit) pass. 100% test coverage.
- **`scripts/core/lib/target_repo.sh` + `prepare-review-input.sh`**
  upstreamed from suwinex so the kit carries the helper scripts its
  cross-repo commands depend on (manifest `scripts_core`: 14 → 17;
  `core_version` 2.0.0 → 2.1.0).

### Changed

- **Kit brought to the canonical cross-repo generation** (KIT-0030) —
  the kit was a stale snapshot while the newest generation stranded in
  suwinex (KIT-ADR-0024's "improvements strand where invented"). Commands
  `check-bots`/`check-ci`/`preflight`/`retro`/`triage-threads` upgraded to
  1.1.0 and `wrap-up` to 1.3.0 (cross-repo Step 0 auto-detection with
  graceful `SINGLE_REPO_MODE` fallback + planning-repo exception); the
  `check-bots`/`verify-ci`/`preflight-check`/`gh-review-helper`/
  `wait-for-bots`/`ci-check` scripts replaced with their cross-repo-aware
  versions. Skills upgraded: `bot-triage` 1.1.0, `pre-implementation`
  1.2.0, `code-review-evaluator` 1.2.0. Project-specific `ixda-services`/
  `ID2-` examples genericized; dangling `.kit/context` links repointed to
  `docs/CROSS-REPO-PATTERN.md`.
- **`feature-developer-v7` extension points filled for the kit repo
  itself** (2.1.1) — `## Project Context` and `### Stack Notes` now
  carry the kit's own conventions (KIT-NNNN, `.kit/` layout, pre-commit
  gauntlet, DK rules, manifest consistency) so the agent can be
  launched in this repo. The filled sections double as the worked
  example; the unfilled template survives in `feature-developer-v6.md`
  for KIT-0030 distribution.

### Notes

- **Two distribution channels coexist** (KIT-0030 / KIT-ADR-0024 §3 vs.
  KIT-0026): the `agentive-workflow` plugin is the *outbound* channel that
  ships skills/commands/agents to planning/consumer projects; the
  `.core-manifest.json` sync (KIT-0026) remains the *kit-to-kit* channel
  for scripts plus kit-internal copies of the same artifacts. The kit is
  the single canonical authoring source feeding both. Consolidating to one
  channel is possible later but is explicitly out of scope here.

## [0.6.0] - 2026-06-12

### Added

- **Canonical `feature-developer-v7` agent** (KIT-0029) — reconciles the
  forked variants (kit/label-maker v6 1.1.0, suwinex v6 1.3.0, moss v7
  2.0.0) into one portable definition in `.claude/agents/`. Retains the
  v7 innovations as portable content: inline CI/bot polling via
  ScheduleWakeup with prompt-cache-window guidance (bot-watcher
  sub-agent deprecated), verify-before-believing reflex for evaluator
  claims, evaluator trio table, and the five-gate phase workflow. Adds
  topology detection (split mode via `## Target Repository`, single-repo
  fallback, planning-repo exception) so one file serves both monorepo
  and cross-repo projects. Project-specific content moved to mandatory
  extension points (`## Project Context`, `### Stack Notes`,
  `### Recurring Footguns`) filled at bootstrap/onboarding. Two new
  portable learnings from downstream retros: batch same-category bot
  fixes into one commit; evaluators miss CSS/cascade and
  dual-render-path bugs — flag for manual review.
- **Agent model-pin policy** — canonical agents pin a model ID plus
  `last-updated`; upgrade procedure documented in
  `docs/MANIFEST-UPGRADE-GUIDE.md` (new "Agent Model Pins" section).

### Changed

- **`feature-developer-v6.md` retained as the Opus-class variant** —
  rewritten (1.2.0) as a content-identical copy of canonical v7 v2.1.0
  with the model pin `claude-opus-4-8`. Not all projects can run
  `claude-fable-5`, which v7 pins. The rewrite removes the deprecated
  bot-watcher sub-agent pattern and stale ixda-services strings that
  the old 1.1.x lineage carried; a banner instructs editors to improve
  v7 first and re-copy, so the two files cannot drift on workflow
  content.

### Removed

- **`feature-developer-v5.md`** — superseded by canonical v7. Downstream
  copies are untouched; adoption is KIT-0030 (plugin) / KIT-0026 (agents
  manifest tier) scope.

## [0.5.1] - 2026-06-12

### Changed

- **adversarial-workflow upgraded to v1.0.0** — Fixes Gemini evaluator verdict extraction (bold markdown patterns like `**FAIL**` now parsed correctly). No config changes needed.
- **Canonical cross-repo pattern doc** (KIT-0028) — `docs/CROSS-REPO-PATTERN.md` absorbed all fork-only content (suwinex-planning's field-testing revisions and the 2026-04-22 adversarial evaluator recipe); project forks in suwinex-planning and label-maker-planning replaced with link stubs carrying only project deltas. `## Provenance` stamps added to the three active planning repos; label-maker-planning regained its machine-readable `## Target Repository` section.
- **Evaluator library pin bumped to v0.10.0** — was v0.5.3. Adds the `-v2` evaluators (`arch-review-fast-v2`, `code-reviewer-fast-v2`, `claude-arch`, …) which pin explicit model IDs; the v1 names are deprecated upstream.

### Fixed

- **Serena MCP server command updated** — Serena upstream renamed the package to `serena-agent` and the executable entry point from `serena-mcp-server` to `serena start-mcp-server`. Updated all setup scripts, documentation, ADRs, and troubleshooting guides to use the new command format.
- **Evaluator installer wrote to a path the CLI never reads** — `install-evaluators` still targeted `.kit/adversarial/evaluators/` after `.adversarial/` was restored to the repo root (0.5.0). Installs silently landed where `adversarial` could not find them, leaving deprecated v0.5.2 evaluators in use. Now installs to `.adversarial/evaluators/`.

### Related

- KIT-0028 channel note: doc canonicalization is convention repair only; the cross-repo helper scripts (`prepare-review-input.sh`, `lib/target_repo.sh`) referenced by the canonical doc still live downstream and upstream via KIT-0026/KIT-0030.

## [0.5.0] - 2026-03-30

### Changed

- **Builder/Project separation via `.kit/` boundary** (ASK-0044) — All builder-layer infrastructure (templates, skills, context, tasks, ADRs, launchers, docs) moved into `.kit/`. Implementation-layer files (agents, commands, skills in `.claude/`) stay where Claude Code expects them. Clean separation between "how we build" and "what we build".
- **ADR directory structure flattened** (ASK-0047) — `docs/decisions/adr/` simplified to `docs/adr/`, `.kit/decisions/starter-kit-adr/` simplified to `.kit/adr/`. Shorter paths, less nesting.
- **Tiered manifest for cross-repo sync** (KIT-0024) — `.core-manifest.json` upgraded from flat file list to tiered format (`scripts_core`, `commands_core`, `commands_optional`, `kit_builder`). Sync workflow now copies per-tier with directory auto-creation. Core scripts v1.3.0.
- **`.adversarial/` restored to repo root** — ASK-0044 moved it into `.kit/adversarial/`, but `adversarial-workflow` v0.9.9 hardcodes the path. Moved back until upstream supports configurable directories (ADV-0053, movito/adversarial-workflow#58).
- **`actions/checkout` upgraded to v6** — CI workflow updated via Dependabot

### Added

- **Root-resolution preamble for all shell scripts** (ASK-0043) — Every shell script now resolves `PROJECT_ROOT` via `SCRIPT_DIR` chain and validates with `pyproject.toml` guard. Prevents silent failures when scripts move to different directory depths.
- **`/babysit-pr` command** — Monitors PR bot reviews (CodeRabbit, BugBot) and triages findings
- **KIT-0026 task spec** — Planned: sync agent definitions and skills to downstream repos via new manifest tiers
- **ADV-0053 task spec** — Planned: make `adversarial-workflow` CLI directory configurable (upstream issue filed)

### Fixed

- **Linear sync import paths** (ASK-0045) — Fixed broken imports in Linear sync modules after v0.4.0 scripts restructure. Added stdlib logging fallback for direct script execution.
- **Repo root cleanup** — Removed stale `.env.example` (canonical is `.env.template`), archived `UPSTREAM-CHANGES-2025-01-28.md`, relocated `tmux-tips.md` to `.kit/docs/`, added `.ruff_cache/` to `.gitignore`
- **Test fixture for identity leak scanner** — Updated to match new `.adversarial/` location at repo root

## [0.4.0] - 2026-03-09

### Changed

- **BREAKING: Scripts restructured into `core/` + `local/` + `optional/`** (ASK-0042) - All shared scripts moved from `scripts/` to `scripts/core/`, project-specific scripts to `scripts/local/`, and opt-in scripts to `scripts/optional/`. See `docs/UPGRADE-0.4.0.md` for migration guide.
- **Core scripts versioned independently** - `scripts/core/VERSION` tracks the shared scripts version (currently 1.2.0), decoupled from the project version
- **`verify-setup.sh` reads Python constraints from `pyproject.toml`** - No longer hardcoded; dynamically reads `requires-python` for version range and project name
- **`verify-ci.sh` self-references corrected** - Help text now points to `./scripts/core/verify-ci.sh`
- **Black upgraded to v26.1.0** - Formatter updated via Dependabot
- **`actions/upload-artifact` upgraded to v7** - CI workflow updated via Dependabot
- **Evaluator library bumped to v0.5.2** - Fixes gemini-3-pro deprecation

### Added

- **Cross-repo sync workflow** - GitHub Action (`.github/workflows/sync-core-scripts.yml`) auto-opens PRs in downstream repos when `scripts/core/` changes on main
- **Core manifest** - `scripts/.core-manifest.json` tracks core version, source repo, and file inventory for sync verification
- **Drift detection script** - `scripts/core/check-sync.sh` compares local core scripts against upstream, reports drift in both directions
- **DK002 lint rule** - Pattern lint now flags `open()`, `.read_text()`, and `.write_text()` without explicit `encoding=` kwarg
- **DK002 test coverage** - 12 new tests covering all DK002 scenarios (bare open, text mode, binary mode, read_text, write_text, noqa suppression)
- **Python 3.10 compatibility** - `verify-setup.sh` and `project` script use `tomllib`/`tomli` fallback for Python < 3.11

### Fixed

- **`project_dir` path resolution** - `scripts/core/project` now correctly resolves repo root via `.parent.parent.parent` (was `.parent.parent` before the move)
- **Nonexistent `start-daemons.sh` references removed** - Three agent files (planner, planner2, tycho) referenced a script that never existed
- **`feature-developer.md` stale path** - Updated `./project complete` to `./scripts/core/project complete`
- **Sync workflow correctness** - Uses `git status --porcelain` (not `git diff`) to detect untracked files; sets git user identity for commits; uses step outputs for conditional PR creation

## [0.3.3] - 2026-03-04

### Added

- **Project bootstrap script and agent** - New `scripts/bootstrap.sh` overlays starter kit scaffolding onto existing projects; bootstrap agent reads design materials, configures pyproject.toml, agents, Serena, and creates initial backlog tasks
- **DK004 lint rule for bare except** (ASK-0039) - Pattern lint now flags `except Exception: pass` and `except BaseException: pass` that silently swallow errors, with noqa suppression support
- **Root-level CLAUDE.md architecture overview** (ASK-0038) - Primary entry point for agents entering the project, covering directory structure, project rules, agent context, and key scripts
- **Linear sync behavior reference** (ASK-0037) - Documentation of Linear sync status determination, task monitor behavior, and legacy status migration
- **Retro command saves to file** - `/retro` now persists retrospective output to `.agent-context/retros/`
- **Dispatch-kit workflow integration** - Skills, commands, scripts, and agents ported from dispatch-kit for event-driven coordination

### Changed

- **Expanded reconfigure to catch all identity leaks** (ASK-0036) - `reconfigure_project()` now replaces 8 additional identity patterns (pyproject.toml, conftest.py, CHANGELOG URLs, CLAUDE.md, README, logging config, planner URL). Adds `--verify` flag, git remote URL derivation, and title-case project names
- **Canonical env template consolidated** (ASK-0040) - `.env.template` is now the single source of truth; `.env.example` synced with header comment, all references updated
- **Linear dependencies made optional** (ASK-0035) - `gql[requests]` and `python-dotenv` moved to `[linear]` extra; base install no longer requires them
- **Template cleaned for downstream use** (ASK-0034) - Archived 34 completed tasks, removed starter-kit-specific SETUP.md and branding, moved legacy docs to `docs/archive/`
- **dispatch-kit moved to optional `[local]` extra** - Prevents CI failures since dispatch-kit is not on PyPI

### Fixed

- **Agent launcher delegates to standalone scripts** - `agents/launch onboard` now correctly delegates to `agents/onboarding` instead of launching a blank session without the initial prompt
- **Corrected create-agent.sh path references** - Agent-creator and workflow docs pointed to old `.agent-context/scripts/` location instead of `scripts/`
- **Corrected evaluator names in agent definitions** - Replaced non-existent `architecture-planner` / `architecture-planner-fast` with actual library names `arch-review` / `arch-review-fast`
- **Prevented feature-developer-v3 self-delegation** - Anti-delegation instructions added so the agent implements tasks directly instead of trying to spawn another instance of itself
- **CI coverage restored** - Added pattern lint tests that were missing after refactoring

## [0.3.2] - 2026-02-11

### Changed

- **Agent models upgraded to Opus 4.6** - Updated planner, feature-developer, security-reviewer, and AGENT-TEMPLATE to use `claude-opus-4-6`
- **Evaluators now installed via library** - Evaluators directory (`.adversarial/evaluators/`) is now gitignored; install with `./scripts/project install-evaluators`
- **Removed deprecated `evaluator_model` config** - Use `adversarial list-evaluators` and `--evaluator NAME` flag instead

### Added

- **UV auto-detection** (ASK-0032) - Setup script automatically detects UV package manager and uses it to create Python 3.12 venvs on Python 3.13+ systems
- **Agent creation automation** (ASK-0033) - New `scripts/create-agent.sh` with concurrent-safe locking, icon patterns, and force overwrite support

## [0.3.1] - 2026-02-02

### Added

- **Multi-provider evaluator configs** - 10 pre-configured evaluators across 4 providers (Anthropic, Google, Mistral, OpenAI) with index.json registry
- **Anthropic evaluator support** - Added claude-adversarial evaluator for critical review

### Fixed

- **Python version ceiling check** (ASK-0030) - Setup now validates `>=3.10,<3.13` upfront with clear error messages and remediation options (pyenv, brew, python.org). Prevents cryptic pip errors on Python 3.13+ due to aider-chat constraint.
- **Shell-aware venv activation** - Onboarding now shows fish/csh alternatives alongside bash/zsh
- **Python version references** - Updated all documentation from "3.9+" to "3.10+" to match actual constraints

### Changed

- **Simplified README setup** - Removed redundant "Set Up Development Environment" section; onboarding handles setup automatically

## [0.3.0] - 2026-02-01

### Changed

- **Upgraded adversarial-workflow to v0.7.0** - Now requires `>=0.7.0` with multi-evaluator support, configurable timeouts, and custom evaluator definitions
- **Provider-agnostic documentation** - Replaced all model-specific language (e.g., "GPT-4o") with evaluator-agnostic descriptions throughout prompts and documentation

### Added

- **Multi-evaluator architecture** (ASK-0029) - Support for multiple evaluation providers via custom evaluators. Users can now use Gemini, Mistral, Anthropic, or local models alongside OpenAI.
- **Evaluator library installer** - New `./scripts/project install-evaluators` command installs pre-built evaluators from adversarial-evaluator-library with version pinning and commit hash tracking.
- **Project setup command** (ASK-0028) - New `./scripts/project setup` creates virtual environment, installs dependencies, and configures pre-commit hooks. Includes Python version check, corrupted venv detection, and `--force` flag for recreation.
- **Evaluator setup in onboarding** - New optional phase in onboarding for installing additional evaluators
- **Custom evaluators directory** - `.adversarial/evaluators/` with README explaining how to create custom evaluators
- **Evaluator discovery** - Documented `adversarial list-evaluators` command to discover built-in and custom evaluators

### Fixed

- **Linear sync no longer breaks test collection** - Changed `sys.exit(1)` at import time to runtime check with `GQL_AVAILABLE` flag. Tests now skip gracefully when gql package not installed instead of failing during pytest collection.
- **Added `requires_gql` marker** - Tests that need the gql package are now marked and can be skipped with `-m "not requires_gql"`. Pattern documented in KIT-ADR-0005.

## [0.2.2] - 2025-12-06

### Added

- **Upstream tracking option in onboarding** - Users can now opt to add the original starter kit as an upstream remote during onboarding, making it easy to pull future updates with `git fetch upstream && git merge upstream/main`.

### Changed

- **Simplified Serena activation instructions** - Removed confusing placeholder references and redundant fallback sections from all 6 agent files. Activation section is now consistent and minimal across all agents.
- **Enhanced CI verification script** - `verify-ci.sh` now uses jq for proper JSON parsing, filters to push events only, reports on latest commit SHA, and provides clear verdicts (PASS/FAIL/IN PROGRESS/MIXED). Added `--wait` flag to block until workflows complete. Exit codes: 0 for pass, 1 for fail.
- **CI-checker model upgraded to Sonnet** - Switched from Haiku to Sonnet (`claude-sonnet-4-20250514`) for more reliable tool invocation behavior.

### Fixed

- **CI-checker agent tool execution** - Added explicit CRITICAL instruction requiring use of Bash tool to execute gh commands, fixing issue where Haiku would sometimes show commands in markdown without actually running them.
- **Code-reviewer Serena activation** - Removed explicit Serena MCP tools from frontmatter (caused activation to be skipped) and added code-reviewer to launcher's serena_agents list. Agents should discover Serena tools after activation, not via frontmatter listing.

## [0.2.1] - 2025-12-04

### Added

- **Structured knowledge capture from code reviews** (KIT-ADR-0019) - Code review insights are now captured in `.agent-context/REVIEW-INSIGHTS.md`, organized by module with recommended patterns and anti-patterns. Future agents can learn from past reviews.
- **Mandatory code review workflow** (KIT-ADR-0014) - Implementation agents now create review starters and request code review before task completion. Reviews are versioned (round 1, round 2) to preserve history.
- **Review fix workflow** - Streamlined process for handling CHANGES_REQUESTED verdicts with lightweight fix prompts instead of full task starters.

### Changed

- **Removed Thematic project-specific content** - Cleaned DaVinci Resolve, SMPTE, Electron references from agent templates for cleaner starter kit experience.
- **Improved Serena activation instructions** - Code-reviewer and other agents now have clearer, more direct activation instructions.

### Fixed

- **Reconfigure command handles upstream project name** - `./scripts/project reconfigure` now uses regex to replace any `activate_project()` call, not just the `"your-project"` placeholder. This fixes the case where downstream projects merge upstream and get `"agentive-starter-kit"` in their agent files instead of their configured project name.
- **Code-reviewer no longer overwrites existing reviews** - Reviews are now versioned (`-round2.md` suffix) to preserve review history.

## [0.2.0] - 2025-12-03

### Added

- **Task lifecycle management** - Agents now run `./scripts/project start <TASK-ID>` when picking up tasks, automatically moving them to `3-in-progress/` and updating status headers for visibility
- **TDD infrastructure out of the box** - pytest, pre-commit hooks, and test workflows ship ready to use
- **Startup task scanning** - Planner agent checks `delegation/tasks/2-todo/` on session start and summarizes pending work
- **CI verification script** - `./scripts/ci-check.sh` for local pre-push validation
- **Browser warning for Serena** - Dashboard flash warning added to prevent confusion during LSP initialization

### Changed

- **Project CLI location** - Moved from `./project` to `./scripts/project` for cleaner root directory
- **Simplified planner startup** - Planner now asks what to build when no tasks exist, recognizes TDD is pre-configured
- **Improved onboarding** - Clearer Linear API key instructions, better Serena activation guidance for new projects
- **Updated adversarial-workflow** - Upgraded to v0.5.0

### Fixed

- Custom task prefix support in glob patterns (e.g., `ASK-*`, `TASK-*`)
- Invalid model ID `claude-sonnet-4-5` corrected to `claude-sonnet-4`
- Dependencies `gql` and `python-dotenv` moved to main dependencies (were missing)
- Various path inconsistencies in documentation and agent instructions

## [0.1.0] - 2025-11-25

### Added

- Initial release of the Agentive Starter Kit
- Multi-agent coordination system with specialized agents (planner, feature-developer, test-runner, etc.)
- Linear task synchronization with bidirectional status updates
- Serena MCP integration for semantic code navigation
- Adversarial evaluation workflow with GPT-4o
- Task delegation system with numbered folder workflow
- Agent handoff protocol via `.agent-context/`
- Pre-configured Claude Code settings and permissions

[0.5.0]: https://github.com/movito/agentive-starter-kit/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/movito/agentive-starter-kit/compare/v0.3.3...v0.4.0
[0.3.3]: https://github.com/movito/agentive-starter-kit/compare/v0.3.2...v0.3.3
[0.3.2]: https://github.com/movito/agentive-starter-kit/compare/v0.3.1...v0.3.2
[0.3.1]: https://github.com/movito/agentive-starter-kit/compare/v0.3.0...v0.3.1
[0.3.0]: https://github.com/movito/agentive-starter-kit/compare/v0.2.2...v0.3.0
[0.2.2]: https://github.com/movito/agentive-starter-kit/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/movito/agentive-starter-kit/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/movito/agentive-starter-kit/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/movito/agentive-starter-kit/releases/tag/v0.1.0
