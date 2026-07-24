# Pre-0.9.0 Architectural Cruft Audit — 2026-07-24

**Run**: planner-f5 orchestrated workflow (9 subsystem readers + 9 adversarial
verifiers, 18 agents, ~1.9M tokens). Readers were given the ADR-0027 end-state
and the already-tracked backlog (KIT-0047/51/52/54/55/59/60/61/62/63/64/65) as
exclusions; every finding below survived per-area adversarial verification.
Verdict caveat: verdict-to-finding join fell back to file-level matching where
issues were paraphrased, so per-finding `verifier_reason` text may belong to a
sibling finding in the same file; the verdicts themselves are area-verified.

**Totals**: 92 confirmed, 2 uncertain, 2 refuted.

| Area | Files read | Findings |
|---|---|---|
| core-scripts | 27 | 12 |
| local-optional-scripts | 17 | 10 |
| agents | 17 | 15 |
| skills-commands | 24 | 4 |
| kit-dir | 30 | 15 |
| top-docs | 19 | 14 |
| adversarial-dir | 12 | 9 |
| tests | 30 | 8 |
| ci-plugin | 20 | 9 |

## Confirmed findings

### A00 [contradiction/high] `scripts/core/project`
**Where**: line 2127 (linearsync command)
**Issue**: `project linearsync` invokes `scripts/sync_tasks_to_linear.py`, but that file lives at `scripts/optional/sync_tasks_to_linear.py` since the v0.4.0 core/local/optional restructure — the advertised command runs python3 on a nonexistent path.
**Evidence**: Line 2127: `str(project_dir / "scripts" / "sync_tasks_to_linear.py")`. Verified: `ls scripts/sync_tasks_to_linear.py` → No such file; actual location `scripts/optional/sync_tasks_to_linear.py`. Live surfaces advertise the command: CLAUDE.md:54 'Optional Linear sync: ./scripts/core/project linearsync' and CLAUDE.md:103; `print_help()` lists 'linearsync, linear'.
**Suggested disposition**: Point the command at scripts/optional/sync_tasks_to_linear.py (or resolve across optional/ and local/), and add a friendly error when the optional script is absent on consumers.

### A01 [contradiction/high] `scripts/core/project`
**Where**: lines 2464-2475 (create-agent command)
**Issue**: `project create-agent` looks for `scripts/create-agent.sh`, which does not exist — the script moved to `scripts/optional/create-agent.sh` (v0.4.0). The command always errors with '❌ scripts/create-agent.sh not found', while help still advertises it.
**Evidence**: Line 2466: `script = project_dir / "scripts" / "create-agent.sh"`. Verified `ls scripts/create-agent.sh` → No such file; `scripts/optional/create-agent.sh` exists and even honors the CREATE_AGENT_PROJECT_ROOT env this command sets (create-agent.sh:26-27). CLAUDE.md Key Scripts table names `./scripts/optional/create-agent.sh`; print_help() (lines 2521-2524) still advertises `create-agent`.
**Suggested disposition**: Fix the path to scripts/optional/create-agent.sh; create-agent.sh:217's own usage line ('scripts/create-agent.sh') is stale too but is outside this area.

### A02 [contradiction/high] `scripts/core/project`
**Where**: lines 496-501 (reconfigure_project replacements)
**Issue**: reconfigure targets `scripts/logging_config.py` for the identity rewrite, but the file lives at `scripts/core/logging_config.py` — the replacement silently reports 'not found (skipped)' in every real repo, leaving the 'infrastructure for the agentive-starter-kit' string un-reconfigured. The unit test masks this: its mock tree creates the file at the pre-v0.4.0 path.
**Evidence**: project:497 replacement tuple `("scripts/logging_config.py", r"infrastructure for the agentive-starter-kit", ...)`; `ls scripts/logging_config.py` → No such file; the target string exists at scripts/core/logging_config.py:5 ('Configurable logging infrastructure for the agentive-starter-kit'). tests/test_project_script.py:594-603 writes the fixture at `scripts/logging_config.py` (old layout), so test_logging_config_replaced passes against a layout that no longer exists.
**Suggested disposition**: Change the replacement path to scripts/core/logging_config.py and update the test fixture to the real layout.

### A03 [stale-doc/high] `scripts/core/project`
**Where**: cmd_setup, lines 632, 646-669
**Issue**: The Python <3.13 upper bound in `project setup` is attributed to the retired aider-chat dependency: '(3.10+ required, <3.13 due to aider-chat constraint)', '# Upper bound (aider-chat constraint: Python <3.13)', and the user-facing message 'adversarial-workflow requires Python >=3.10,<3.13 (constraint from aider-chat dependency)'. Aider is fully retired (adversarial-workflow>=1.0.1); pyproject.toml:42 itself says the floor 'excludes 0.9.x aider-era builds'.
**Evidence**: grep 'aider' scripts/core/ → project:632, project:646, project:657 (plus the historical incident note in doctor.d/40-version-skew.py, which is fine). pyproject.toml:19 still pins requires-python = ">=3.10,<3.13" with no aider rationale; pyproject.toml:42 comment contradicts the setup message's attribution. Not covered by KIT-0065 (that tracks .adversarial/scripts + create-project.md aider refs).
**Suggested disposition**: Re-derive or re-justify the <3.13 bound (verify whether adversarial-workflow 1.0.1+ still needs it) and rewrite the three messages/comments; keep behavior aligned with pyproject's requires-python.

### A04 [version-drift/high] `scripts/core/project`
**Where**: lines 2204-2207 (version command)
**Issue**: `project version` prints 'Project CLI v1.1.0' followed by a redundant 'Project CLI' line, while scripts/core/VERSION says 3.5.0 and the manifest says core_version 3.5.0 — the command's version string has not tracked the core-scripts version through six minor releases.
**Evidence**: Lines 2205-2206: `print("Project CLI v1.1.0")` / `print("Project CLI")`. scripts/core/VERSION = '3.5.0'; scripts/.core-manifest.json core_version = '3.5.0'.
**Suggested disposition**: Make `version` read scripts/core/VERSION (single source of truth) and drop the duplicate line.

### A05 [stale-doc/high] `scripts/core/__init__.py`
**Where**: lines 1-7 (module docstring)
**Issue**: The scripts/core package docstring claims the package 'Contains: sync_tasks_to_linear ... linear_sync_utils', but both modules live in scripts/optional/, not scripts/core/ — the docstring describes the pre-v0.4.0 flat scripts/ layout.
**Evidence**: __init__.py lists 'sync_tasks_to_linear: Sync task files to Linear' and 'linear_sync_utils: Helper functions for Linear sync'; `ls scripts/core/` contains neither; both are in scripts/optional/. The file is a synced scripts_core manifest entry, so consumers receive the wrong description too.
**Suggested disposition**: Rewrite the docstring to describe what scripts/core actually holds (project CLI, sync engine, preflight/CI helpers, doctor.d).

### A06 [stale-doc/high] `scripts/core/project`
**Where**: usage/help strings throughout (e.g. lines 661, 668, 689, 718, 725, 822, 2212, 2505) and validate_task_status.py:118
**Issue**: User-facing usage strings still name the pre-v0.4.0 entry point `./scripts/project` (e.g. 'Usage: ./scripts/project <command>', 'Run with --force to recreate: ./scripts/project setup --force', 'Then run: ./scripts/project setup', and validate_task_status.py's fix hint './scripts/project move'). That path has not existed since the core/local/optional restructure; CLAUDE.md's canonical path is ./scripts/core/project.
**Evidence**: project:2505 'Usage: ./scripts/project <command> [options]'; project:2212 'Usage: ./scripts/project move <task-id> <status>'; project:689/718/725 './scripts/project setup --force'; project:661/668 'Then run: ./scripts/project setup' / 'python3.12 scripts/project setup'; project:822 './scripts/project help'; validate_task_status.py:118 './scripts/project move <task-id> <status>'. `ls scripts/project` → No such file. Memory/CLAUDE.md: 'Key path: ./scripts/core/project (was ./scripts/project before v0.4.0)'.
**Suggested disposition**: Sweep all emitted usage strings to ./scripts/core/project.

### A07 [stale-doc/high] `scripts/core/check-bots.sh`
**Where**: check-bots.sh:3,57,100; wait-for-bots.sh:3,34,53-56,77; verify-ci.sh:3; gh-review-helper.sh:3,39,58-61
**Issue**: The header/usage/help text of four core helper scripts still gives the pre-v0.4.0 invocation path `./scripts/<name>.sh` (e.g. 'Usage: ./scripts/check-bots.sh', './scripts/gh-review-helper.sh summary 53'), while the scripts live at scripts/core/ and every live caller (.claude/commands/, skills) uses ./scripts/core/<name>.sh.
**Evidence**: check-bots.sh:3 '# Usage: ./scripts/check-bots.sh [PR_NUMBER]...' and :57/:100 in --help output; wait-for-bots.sh:3/:34 './scripts/wait-for-bots.sh'; verify-ci.sh:3 './scripts/verify-ci.sh' (its line 105 already says the correct ./scripts/core/verify-ci.sh — internally inconsistent); gh-review-helper.sh:3/:39/:58-61. Cross-check: .claude/commands/check-bots.md, babysit-pr.md, triage-threads.md all use ./scripts/core/... paths.
**Suggested disposition**: Update the header comments and --help/example text to the scripts/core/ paths.

### A08 [version-drift/medium] `scripts/core/project`
**Where**: lines 29-46 (_get_evaluator_library_version)
**Issue**: The evaluator-library version fallback is 'v0.5.3' while pyproject.toml pins [tool.adversarial] library_version = 'v0.10.0'. The fallback fires not only when pyproject.toml is missing but on any Python 3.10 interpreter (`import tomllib` → ImportError, no tomli fallback), silently installing a five-minor-versions-old evaluator library. doctor.d/40-version-skew.py already solves this exact 3.10 case with a tomli/regex fallback; this reader does not.
**Evidence**: project:39-42 `.get("library_version", "v0.5.3")` / `except (FileNotFoundError, ImportError): return "v0.5.3"`; pyproject.toml:84 `library_version = "v0.10.0"`; requires-python = ">=3.10,<3.13" means 3.10 (no stdlib tomllib) is a supported interpreter. Contrast doctor.d/40-version-skew.py lines 37-43 (tomli fallback + regex scan).
**Suggested disposition**: Bump the fallback to match the pin (or better: reuse the tomli/regex fallback pattern so 3.10 reads the real pin) and print which source the version came from.

### A09 [orphan/medium] `scripts/core/project`
**Where**: line 299 (_verify_identity_leaks exclude_dirs)
**Issue**: `exclude_dirs = {".git", ".venv", ".aider"}` — the `.aider` scratch-directory exclusion is an orphan of the retired aider toolchain; nothing in the post-1.0.1 stack creates a .aider directory.
**Evidence**: project:299. grep -rn 'aider' scripts/core/ shows no other mechanism producing .aider dirs; adversarial-workflow floor >=1.0.1 (pyproject.toml:42) excludes aider-era builds. Harmless (an exclusion of a dir that never exists) but it is a live-code remnant of the retired feature, not a historical record.
**Suggested disposition**: Drop '.aider' from the exclusion set when touching this function (bundle with the cmd_setup aider-message cleanup).

### A10 [contradiction/medium] `scripts/core/project`
**Where**: lines 2102-2105 and 2493-2495 (main venv resolution / FileNotFoundError hint)
**Issue**: main() prefers a legacy `venv/bin/python3` over `.venv/bin/python3`, and the FileNotFoundError help text tells users to run `python3 -m venv venv` — while `project setup` (the kit's own setup path) creates `.venv` and ci-check.sh checks `.venv` first. The recovery advice creates a venv at a location the rest of the tooling treats as secondary.
**Evidence**: project:2102-2104 checks `project_dir / "venv" / "bin" / "python3"` before `.venv`; project:2495 'python3 -m venv venv && source venv/bin/activate'; cmd_setup:628 `venv_dir = project_dir / ".venv"`; ci-check.sh:61-66 activates .venv first, venv second.
**Suggested disposition**: Prefer .venv first in main() (matching ci-check.sh and doctor.d/40's venv_bin order, which also prefers .venv) and fix the hint to 'python3 -m venv .venv' or './scripts/core/project setup'.

### A11 [contradiction/high] `scripts/optional/sync_tasks_to_linear.py`
**Where**: invoked from scripts/core/project:2127
**Issue**: `project linearsync` (advertised in CLAUDE.md 'Task Workflow' and in the project script's own help at lines 10/2537/2551) builds its command as `project_dir / "scripts" / "sync_tasks_to_linear.py"`, but the script has lived at scripts/optional/sync_tasks_to_linear.py since the v0.4.0 restructure. No file exists at scripts/sync_tasks_to_linear.py (verified: `ls scripts/` shows only README.md, __init__.py, __pycache__, core, local, optional). The GitHub workflow .github/workflows/sync-to-linear.yml:55 uses the correct scripts/optional/ path, so the two callers disagree and the CLI one is broken.
**Evidence**: scripts/core/project:2125-2128: `cmd = [python_cmd, str(project_dir / "scripts" / "sync_tasks_to_linear.py")]` with project_dir = Path(__file__).resolve().parent.parent.parent (line 2099) = repo root. .github/workflows/sync-to-linear.yml:55: `python scripts/optional/sync_tasks_to_linear.py`.
**Suggested disposition**: Fix the path in scripts/core/project to scripts/optional/sync_tasks_to_linear.py (or route through the optional/ layer explicitly).

### A12 [contradiction/high] `scripts/local/engine-materials.sh`
**Where**: lines 93, 96
**Issue**: The materials engine rsyncs `$PROJECT_ROOT/scripts/` and `$PROJECT_ROOT/tests/` wholesale into the consumer — including scripts/local/ (the door, all three engines, bootstrap shims) and the seven kit-only tests. This directly contradicts two live contracts: the door header (scripts/local/bootstrap:8-9, 'Kit-side only: ... never ships on any sync tier or consumer rsync') and engine-consumer.sh's own exclusion machinery (lines 464-485: rm+exclude of test_setup_door.py, test_entrance_shims.py, test_kit_markers.py, test_bootstrap_consumer.py, test_bootstrap_shapes.py, test_bots_conformance.py, test_check_hook_seeds.py, with the comment 'scripts/local is an ASK-only layer that is never synced to consumers ... shipping these tests would break consumer pytest at collection time').
**Evidence**: engine-materials.sh:93: `"${RSYNC_BASE[@]}" "$PROJECT_ROOT/scripts/" "$TARGET/scripts/"` (no local/ exclude); line 96: `"${RSYNC_BASE[@]}" "$PROJECT_ROOT/tests/" "$TARGET/tests/"` (no kit-only test excludes). Compare engine-consumer.sh:464-485 and bootstrap:8-9. The engine is live: the door execs it on --design-materials (bootstrap:819, 915).
**Suggested disposition**: Bring engine-materials.sh's copy lists in line with engine-consumer.sh (exclude scripts/local except checks-hook seeding, and the seven kit-only tests) — or have the materials flow delegate its scaffolding step to engine-consumer.

### A13 [contradiction/high] `scripts/local/engine-materials.sh`
**Where**: lines 74-80
**Issue**: The .kit/ rsync exclusion list predates the ASK->KIT task-prefix rename and the .adversarial move: it excludes `context/ASK-*` and `tasks/ASK-*` but not KIT-*, so a --design-materials adopt copies the kit's own planning corpus into the consumer — 44 KIT-* task specs (verified via git ls-files .kit/tasks) and 104 KIT-* context files (handoffs, review starters) — the exact identity leak engine-export.sh strips (lines 115-126) and engine-consumer.sh avoids by shipping only a skeleton. The exclude names for `adversarial/logs/` etc. also point at .kit/adversarial/, which is not a tracked builder dir anymore (git ls-files .kit shows no adversarial/ files; the config home is root .adversarial/), so untracked local .kit/adversarial content would be copied too.
**Evidence**: engine-materials.sh:74-80: `--exclude='adversarial/logs/' ... --exclude='context/ASK-*' ... --exclude='tasks/ASK-*' ... "$PROJECT_ROOT/.kit/" "$TARGET/.kit/"`. `git ls-files .kit/tasks | grep -c KIT-` = 44; `git ls-files .kit/context | grep -c KIT-` = 104; `git ls-files .kit | grep adversarial` matches nothing under .kit/adversarial/ (dir exists only untracked, per git status `?? .kit/adversarial/`).
**Suggested disposition**: Update the exclusion list to prefix-agnostic task/context excludes (or replace the wholesale .kit/ rsync with engine-consumer's enumerated skeleton).

### A14 [contradiction/high] `scripts/optional/linear_sync_utils.py`
**Where**: lines 287-293, 299-301
**Issue**: parse_task_metadata hardcodes TASK-\d{4} and ASK-\d{4} as the only valid task-ID prefixes (raising ValueError otherwise), and the title regex likewise only matches `# TASK-...` / `# ASK-...`. Every current kit task uses the KIT- prefix (44 KIT-* specs in .kit/tasks), CLAUDE.md's 'Task Naming' names KIT-XXXX as first-class, and engine-export.sh derives arbitrary consumer prefixes (--prefix, e.g. MNP) — so linearsync would refuse every live task in the kit and in any exported consumer.
**Evidence**: linear_sync_utils.py:288: `re.search(r"(TASK-\d{4})", filename)`; 290-293: fallback `re.search(r"(ASK-\d{4})", filename)` else `raise ValueError(f"No valid task ID found in filename: {filename}")`; 299-301: title regex `^#\s+(?:TASK-\d{4}|ASK-\d{4})...`. CLAUDE.md: 'Optional Linear sync: ./scripts/core/project linearsync' + memory of KIT-prefix tasks; git ls-files .kit/tasks shows 44 KIT-* IDs and zero TASK-* IDs.
**Suggested disposition**: Generalize the ID pattern to `[A-Z]+-\d{4}` (matching new-worktree.sh's PREFIX-NNNN rule) or read the prefix from current-state.json; sync docstring/tests accordingly.

### A15 [stale-doc/high] `scripts/optional/sync_tasks_to_linear.py`
**Where**: lines 18-19, 59
**Issue**: Post-restructure path drift inside the script itself: (a) `env_path = Path(__file__).parent.parent / ".env"` resolves to scripts/.env now that the file lives in scripts/optional/ — the repo-root .env is never loaded, so the documented 'LINEAR_API_KEY ... loaded from .env file' behavior silently fails for local runs; (b) the usage docstring still cites the pre-v0.4.0 entrances `python scripts/sync_tasks_to_linear.py` and `./scripts/project linearsync` (canonical is ./scripts/core/project linearsync per CLAUDE.md).
**Evidence**: Line 59: `env_path = Path(__file__).parent.parent / ".env"` (__file__ = scripts/optional/sync_tasks_to_linear.py, so parent.parent = scripts/; no scripts/.env exists). Lines 18-19: 'python scripts/sync_tasks_to_linear.py' / './scripts/project linearsync'. Docstring line 22 claims the key is 'loaded from .env file'.
**Suggested disposition**: Change to parent.parent.parent / ".env" and update the usage lines.

### A16 [stale-doc/high] `scripts/optional/setup-dev.sh`
**Where**: lines 3, 235-236
**Issue**: Live script (invoked by the door's venv offer, bootstrap:635, and engine-materials.sh:134) still documents pre-v0.4.0 script locations as current: header 'Usage: ./scripts/setup-dev.sh' and closing next-step './scripts/ci-check.sh  # run CI checks'. Canonical paths are scripts/optional/setup-dev.sh and ./scripts/core/ci-check.sh (CLAUDE.md Key Scripts; the ci-check dispatcher is an ADR-0027 P1 surface).
**Evidence**: setup-dev.sh:3: `# Usage: ./scripts/setup-dev.sh`; :235-236: `echo "  ./scripts/ci-check.sh        # run CI checks"`. Both paths nonexistent: ls scripts/ shows only README.md/__init__.py/core/local/optional.
**Suggested disposition**: Update the two path strings.

### A17 [version-drift/high] `scripts/optional/create-agent.sh`
**Where**: line 23 (with .kit/templates/AGENT-TEMPLATE.md:4 as the second surface)
**Issue**: Model-pin drift across three surfaces: create-agent.sh DEFAULT_MODEL="claude-sonnet-4-5-20250929", AGENT-TEMPLATE.md frontmatter `model: claude-sonnet-4-20250514`, while every shipped agent in .claude/agents/ pins claude-sonnet-5, claude-opus-4-8, or claude-fable-5. The script's sed (`-e "s|model: .*|model: ${model}|"`, line 279) stamps the superseded 4.5 pin onto every newly created agent, so the documented creation path (CLAUDE.md Key Scripts, agent-creator.md) produces agents two model generations behind the fleet.
**Evidence**: create-agent.sh:23: `DEFAULT_MODEL="claude-sonnet-4-5-20250929"`; :224 help text repeats it. AGENT-TEMPLATE.md:4: `model: claude-sonnet-4-20250514`. grep 'model:' .claude/agents/*.md: all claude-sonnet-5 / claude-opus-4-8 / claude-fable-5, none sonnet-4-x.
**Suggested disposition**: Bump DEFAULT_MODEL (and the template frontmatter) to the current fleet pin, or read the default from an existing agent so it can't drift again.

### A18 [stale-doc/medium] `scripts/optional/setup-dev.sh`
**Where**: lines 131-157, 196-219
**Issue**: Steps 3 and 6 (of 6) install dispatch-kit from a hardcoded operator-machine clone (`DISPATCH_KIT_PATH:-$HOME/Github/dispatch-kit`, 'not yet on PyPI') and run `dispatch init` to create .dispatch/config.yml. dispatch-kit is pre-ADR-0027 coordination tooling that appears nowhere in the end-state (door/engines/doctor/profiles); the only remaining core-script uses are 'optional, fire-and-forget' event emissions. Every fresh consumer running the door's venv offer gets a warning telling them to clone movito/dispatch-kit. engine-materials.sh:21 advertises this step ('Runs setup-dev.sh (Python, venv, dispatch-kit, deps, tmux, dispatch init)') as current behavior.
**Evidence**: setup-dev.sh:135-137: '# dispatch-kit is not yet on PyPI — install from local clone. DISPATCH_KIT_PATH="${DISPATCH_KIT_PATH:-$HOME/Github/dispatch-kit}"'; :154-155 warning text. Repo-wide grep: only 'origin: dispatch-kit' metadata headers and optional emit-event comments in scripts/core/*; no doctor.d check, no ADR-0027 surface, no manifest tier references dispatch-kit. Script header metadata itself is frozen at 'version: 1.0.0 ... last-updated: 2026-02-27'.
**Suggested disposition**: Drop (or clearly gate behind an env flag) the dispatch-kit install/init steps and update engine-materials.sh's step-3 description; renumber the 6-step banner.

### A19 [stale-doc/high] `scripts/optional/create-agent.sh`
**Where**: line 217
**Issue**: show_help documents the pre-v0.4.0 invocation path 'Usage: scripts/create-agent.sh <name> <description>' while the script lives at scripts/optional/create-agent.sh (the path CLAUDE.md and agent-creator.md use).
**Evidence**: create-agent.sh:217: `Usage: scripts/create-agent.sh <name> <description> [options]`. CLAUDE.md Key Scripts: `./scripts/optional/create-agent.sh`; .claude/agents/agent-creator.md:129/359/439 all use scripts/optional/.
**Suggested disposition**: Update the usage string.

### A20 [stale-doc/medium] `scripts/local/engine-materials.sh`
**Where**: lines 73, 89, 156
**Issue**: Comments describe a pre-ADR-0027 .kit layout as current: line 73 calls .kit/ the 'builder layer (adversarial, context, delegation, agents, etc.)' — .kit/delegation/ does not exist (the relocation task ASK-0046 was canceled; handoffs live in .kit/context/) and .kit/ contains no tracked adversarial/ or agents/ dirs; line 156 still excludes '*/delegation/*' from the material-file scan; line 89 says docs/ ships 'the structural parts (decisions, testing guide)' though docs/decisions/ was flattened to docs/adr/ in ASK-0047.
**Evidence**: engine-materials.sh:73: `# .kit/ — builder layer (adversarial, context, delegation, agents, etc.)`; :156: `-not -path '*/delegation/*'`; :89: `# docs/ — only the structural parts (decisions, testing guide)`. ls .kit/ = adr adversarial(untracked) context docs launchers skills tasks templates; git ls-files .kit shows no delegation/ path; docs/adr/ exists, docs/decisions/ does not.
**Suggested disposition**: Refresh the comments and drop the dead delegation exclude when the engine's copy lists are reworked (see the two contradiction findings on this file).

### A21 [stale-doc/high] `.claude/agents/agent-creator.md`
**Where**: lines 41, 255, 342, 353
**Issue**: References the agent template at `.claude/agents/AGENT-TEMPLATE.md` four times ('Use `.claude/agents/AGENT-TEMPLATE.md` as starting point', 'cat .claude/agents/AGENT-TEMPLATE.md'). That file does not exist; the canonical home is `.kit/templates/AGENT-TEMPLATE.md`.
**Evidence**: `ls .claude/agents/AGENT-TEMPLATE.md` -> No such file or directory; `ls .kit/templates/AGENT-TEMPLATE.md` -> exists. The automation script the agent runs agrees with the new home: scripts/optional/create-agent.sh:42 `TEMPLATE_FILE="$PROJECT_ROOT/.kit/templates/AGENT-TEMPLATE.md"`. CLAUDE.md also documents `.kit/templates/` as the template home.
**Suggested disposition**: Update the four references to `.kit/templates/AGENT-TEMPLATE.md`.

### A22 [stale-doc/high] `.claude/agents/agent-creator.md`
**Where**: lines 361-366 (Quick Commands)
**Issue**: Instructs editing the agent launcher at `agents/universal-agent-launcher.sh` with specific line anchors ('agent_order array (lines ~39-54)', 'serena_agents array (lines ~148-157)'). Neither the `agents/` directory nor that script exists; the launcher is `.kit/launchers/launch`.
**Evidence**: `ls agents/` -> No such file or directory. Repo-wide grep for 'universal-agent-launcher' (excluding done-tasks/retros/archive) returns only this one reference in agent-creator.md. `.kit/launchers/launch` exists and is the launcher named by CLAUDE.md and by agent-creator's own Phase 5 ('Run your agent launcher: ./.kit/launchers/launch').
**Suggested disposition**: Delete the block or point it at .kit/launchers/launch.

### A23 [version-drift/high] `.claude/agents/agent-creator.md`
**Where**: lines 99, 268-280, 424
**Issue**: Model-selection guidance tells users to pin new agents to `claude-sonnet-4-5-20250929` or `claude-3-5-haiku-20241022` — two-generations-old dated model IDs. Every live agent in the kit pins `claude-sonnet-5`, `claude-opus-4-8`, or `claude-fable-5` (including this file's own frontmatter, line 4: `model: claude-sonnet-5`).
**Evidence**: grep across .claude/agents/ shows the only occurrences of `claude-sonnet-4` / `claude-3-5` are these four lines in agent-creator.md; all 17 agent frontmatters use claude-sonnet-5 / claude-opus-4-8 / claude-fable-5. The file body contradicts its own frontmatter pin.
**Suggested disposition**: Rewrite the Model Selection Guide around the current model family names used elsewhere in the kit.

### A24 [stale-doc/high] `.claude/agents/powertest-runner.md`
**Where**: lines 188, 278
**Issue**: Task Starter Protocol points at `.claude/agents/TASK-STARTER-TEMPLATE.md` ('Template: `.claude/agents/TASK-STARTER-TEMPLATE.md`', 'See ... for complete example'). The file does not exist; the canonical home is `.kit/templates/TASK-STARTER-TEMPLATE.md`.
**Evidence**: `ls .claude/agents/TASK-STARTER-TEMPLATE.md` -> No such file or directory; `.kit/templates/TASK-STARTER-TEMPLATE.md` exists. Sibling agents already use the correct path: security-reviewer.md:61 and document-reviewer.md:62 both reference `.kit/templates/TASK-STARTER-TEMPLATE.md`.
**Suggested disposition**: Update both references to `.kit/templates/TASK-STARTER-TEMPLATE.md`.

### A25 [orphan/high] `.claude/agents/security-reviewer.md`
**Where**: lines 113-117, 159-164
**Issue**: Carries orphaned context from a completely different application: 'Don't break LinkedIn integration', 'LinkedIn CORS must work', 'Dropbox and Notion integrations are critical', 'This app already had security issues from hasty implementation', 'Local-only deployment (not public facing)'. None of this describes the kit, and the file is distributed downstream as a canonical agent.
**Evidence**: grep -rli 'linkedin|dropbox' across scripts/, tests/, docs/, .kit/context/workflows/ returns nothing — no such integration exists anywhere in the repo. The Review Guidelines and Important Context sections were copied from a prior project and never genericized (the kit's project-context rule in feature-developer.md explicitly forbids project-specific strings in canonical agents).
**Suggested disposition**: Replace the Review Guidelines / Important Context sections with kit-generic or extension-point content.

### A26 [contradiction/high] `.claude/agents/agent-creator.md`
**Where**: lines 34, 189, 244, 374, 386
**Issue**: Core responsibility and Phase 4B instruct updating `.kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md`, and the QA checklist blocks completion on it ('Procedural index updated'). The file does not exist anywhere in the repo, so the agent is required to maintain a nonexistent artifact.
**Evidence**: `find . -name PROCEDURAL-KNOWLEDGE-INDEX.md -not -path ./.git/*` returns nothing. Several live workflow docs (.kit/context/workflows/TESTING-WORKFLOW.md, COMMIT-PROTOCOL.md, AGENT-CREATION-WORKFLOW.md, .kit/templates/AGENT-TEMPLATE.md) also reference it, so the missing file is pointed to by multiple live surfaces, not just historical records.
**Suggested disposition**: Either create the index or strip the references from agent-creator.md (and flag the workflow-doc references to the docs-area pass).

### A27 [stale-doc/high] `.claude/agents/test-runner.md`
**Where**: line 139
**Issue**: Claims the evaluator runs unattended via a CLI flag: 'External AI via adversarial-workflow (`--yes` flag)'. No such flag exists on the installed CLI — this is the same phantom-flag class as the ADVERSARIAL_UNATTENDED saga.
**Evidence**: `adversarial evaluate --help` output: options are only `-h/--help`, `--timeout/-t`, `--check-citations`, `--evaluator NAME`. No `--yes`. The file's own How-to-Run block (lines 126-129) correctly uses `echo y | adversarial evaluate ...` for large files, contradicting the `--yes` claim three paragraphs later.
**Suggested disposition**: Replace the parenthetical with the actual pattern (`echo y |` piping / ADVERSARIAL_UNATTENDED note).

### A28 [contradiction/high] `.claude/agents/powertest-runner.md`
**Where**: lines 413-425 (Invoking Code Reviewer)
**Issue**: Instructs spawning the code-reviewer via `Task tool with subagent_type: "code-reviewer"`. This contradicts three live surfaces: ci-checker.md line 15 ('Do NOT invoke via Task(subagent_type=...) — it will fail with Permission to use Bash has been denied'; code-reviewer also carries the Bash tool), planner.md's Sub-agent permission trap footgun ('agents launched via the Task tool do not inherit .claude/settings.json allow patterns ... the user invokes agents in new tabs instead'), and powertest-runner's OWN line 379 ('Do NOT use the ci-checker subagent via Task tool — it fails due to Bash permission denial').
**Evidence**: Direct quotes above; code-reviewer.md frontmatter lists Bash in tools (line 13), so the Task-tool invocation hits exactly the failure ci-checker documents. The kit-wide convention (planner.md, feature-developer.md 'NEVER delegate', project-intake.md 'Never delegate via the Task tool') is user-invoked tabs.
**Suggested disposition**: Rewrite the section to hand off via a review starter / user-invoked tab like the rest of the kit.

### A29 [stale-doc/high] `.claude/agents/document-reviewer.md`
**Where**: document-reviewer.md:53; also security-reviewer.md:52, test-runner.md:132, powertest-runner.md:181, agent-creator.md:182
**Issue**: Five agents tell the reader to fetch evaluator results with `cat .adversarial/logs/TASK-*-PLAN-EVALUATION.md`. That log-naming scheme is from the aider-era adversarial-workflow; the current CLI writes `<input-name>--<evaluator-name>.md`, so the glob matches nothing.
**Evidence**: `ls .adversarial/logs/` shows only the new convention (e.g. `ASK-0043-code-review-input--code-reviewer-fast.md`, `KIT-0024-core-scripts-standardization--arch-review-fast.md`); `find . -name '*PLAN-EVALUATION*'` returns zero files. planner.md line 184 already documents the correct pattern: `cat .adversarial/logs/<task-name>--<evaluator-name>.md`.
**Suggested disposition**: Update the read-results snippet in all five agents to the `<input>--<evaluator>.md` pattern.

### A30 [stale-doc/high] `.claude/agents/onboarding.md`
**Where**: line 383
**Issue**: Describes `./scripts/core/project setup` as 'Verifies Python 3.10+ is available (and <3.13 due to aider-chat constraint)'. Aider is fully retired (pyproject floor `adversarial-workflow>=1.0.1` exists specifically to exclude aider-era builds), so the stated rationale for the Python ceiling is false, and aider-chat is not a dependency.
**Evidence**: pyproject.toml:42 `"adversarial-workflow>=1.0.1",  # Floor excludes 0.9.x aider-era builds...`; requires-python is still `>=3.10,<3.13` (pyproject.toml:19) but with no aider dependency anywhere. The same stale rationale survives in scripts/core/project:632,646,657 ('constraint from aider-chat dependency') — outside this area but confirming the text predates aider retirement. KIT-0065's tracked scope is .adversarial/scripts + create-project.md, not onboarding.md or the project script.
**Suggested disposition**: Re-derive or drop the ceiling rationale in onboarding.md (and flag scripts/core/project:632-657 to the scripts-area pass).

### A31 [contradiction/high] `.claude/agents/create-project.md`
**Where**: Step 1 (lines 81-83) vs Step 8 (line 240)
**Issue**: Internal contradiction about the export's commit count. Step 1: 'Verify it succeeded by checking that the target directory has a clean git repo with two commits (export + install record).' Step 8's push-failure diagnostics: 'Check `git log --oneline` — should be exactly 1 commit.' At Step 8 the repo has the two commits Step 1 created (customization commit lands later, in Step 9), so the 1-commit check would misdiagnose a healthy export as broken.
**Evidence**: Both lines quoted verbatim from the file read in full. The one-door flow (scripts/local/bootstrap --new) makes the export + install-record pair the current behavior; the 'exactly 1 commit' text is a leftover from the pre-door create-project.sh single-commit export.
**Suggested disposition**: Fix Step 8 to expect two commits (or 'the door's commits only').

### A32 [contradiction/high] `.claude/agents/bootstrap.md`
**Where**: Important Rules #3 (line 316-317) vs Step 12 (line 259)
**Issue**: Rule 3 says 'Only ask for GitHub repo creation (Step 11)', but GitHub repo creation is Step 12 (Step 11 is 'Git Commit'). Step 12's own text also calls itself 'the ONE interactive step', confirming the rule points at the wrong step number.
**Evidence**: Line 243 '### Step 11: Git Commit'; line 257 '### Step 12: Offer GitHub Repo ... this is the ONE interactive step'; line 316-317 'Only ask for GitHub repo creation (Step 11).' A step was inserted without renumbering the cross-reference.
**Suggested disposition**: Change the rule's reference to Step 12.

### A33 [shim-undue/medium] `.claude/agents/onboarding.md`
**Where**: whole file (Phases 1-8), esp. Phase 7 lines 584-618
**Issue**: The onboarding agent is a complete second setup entrance that bypasses the one setup door: it hand-configures pyproject/env/serena/README and assumes the clone-based flow ('this project is still connected to the original agentive-starter-kit repository ... git remote remove origin'). It never runs `scripts/local/bootstrap`, so a project set up this way gets no install record, no shape/profile, and no doctor tail — contradicting the ADR-0027 one-door end-state, yet it is not in the tracked shim-removal set (KIT-0047/0054 cover verify-setup and the door entrance shims only).
**Evidence**: onboarding.md line 585: 'The project is currently connected to the original agentive-starter-kit repository'; no occurrence of 'bootstrap' or 'doctor' anywhere in the file (grep). Launcher `.kit/launchers/onboarding` is live, and README Options C still routes users here — so this is a live parallel entrance, not a historical record. (Its exec-shim peers bootstrap-consumer.sh / create-project.sh flagless ARE tracked; this one is not.)
**Suggested disposition**: Decide: either fold onboarding into the door (have it call `bootstrap --adopt`) with a removal task like its peers, or explicitly document it as the sanctioned interactive front-end to the door.

### A34 [version-drift/medium] `.claude/agents/agent-creator.md`
**Where**: lines 495-497 (footer)
**Issue**: Footer metadata contradicts the frontmatter: 'Template Version: 1.0.0 / Last Updated: 2025-11-06' while the frontmatter (line 7) says `last-updated: 2026-07-03`. Two version/date stamps on one live surface disagreeing.
**Evidence**: Frontmatter lines 5-7: `version: 1.0.0`, `last-updated: 2026-07-03`; footer lines 495-496: '**Template Version**: 1.0.0 / **Last Updated**: 2025-11-06'. No other kit agent carries a duplicate footer stamp.
**Suggested disposition**: Drop the footer stamp block; the frontmatter is the canonical metadata.

### A35 [contradiction/high] `.claude/commands/check-spec.md`
**Where**: Step 3 (line 43) vs .claude/skills/code-review-evaluator/SKILL.md line 181
**Issue**: /check-spec instructs running `adversarial spec-compliance-fast`, an evaluator that is not installed anywhere, while the code-review-evaluator skill simultaneously declares it unavailable and redirects users to /check-spec — a circular contradiction between two live surfaces.
**Evidence**: check-spec.md line 43: `adversarial spec-compliance-fast .adversarial/inputs/<TASK-ID>-spec-compliance-input.md`. code-review-evaluator/SKILL.md line 181: "**Note**: `spec-compliance-fast` is NOT available — use manual spec checks or `/check-spec` (Gemini Flash via API) instead." — but /check-spec IS the adversarial spec-compliance-fast invocation, not a Gemini-via-API path. Searches: `find .adversarial/evaluators -name "*spec*"` → empty; `grep -n spec .adversarial/config.yml` → empty; installed evaluators are code-reviewer, code-reviewer-fast(+v2), arch-review(+fast), claude-code, etc. — no spec-compliance variant. Whole-repo grep for spec-compliance-fast outside logs/tasks/retros hits ONLY these two files. `.adversarial/templates/spec-compliance-input-template.md` still exists solely to feed the nonexistent evaluator.
**Suggested disposition**: Either rewrite /check-spec to a manual spec-trace or an installed evaluator, or delete the command and fix the skill's parenthetical; the orphaned spec-compliance-input-template.md goes with it.

### A36 [stale-doc/high] `.claude/skills/self-review/SKILL.md`
**Where**: Step 3 item 7 (line 97)
**Issue**: Live checklist item directs the consumer-tests rsync exclusion edit at `scripts/local/bootstrap-consumer.sh`, but since KIT-0053 that file is a deprecated exec shim with no rsync; the `--exclude` list and `rm -f` stale-copy sweep now live in `scripts/local/engine-consumer.sh`. Following the instruction as written targets a file scheduled for deletion in 0.9.0 (KIT-0054), after which the pointer dangles entirely.
**Evidence**: SKILL.md line 97: "must be excluded from the consumer `tests/` rsync in `scripts/local/bootstrap-consumer.sh` (both the `--exclude` and the stale-copy `rm -f` sweep)". bootstrap-consumer.sh header: "DEPRECATED shim (KIT-0053): use scripts/local/bootstrap --adopt instead... execs the setup door"; grep of bootstrap-consumer.sh for rsync/--exclude finds no rsync command. engine-consumer.sh lines 471–484 contain the actual `rm -f "$TARGET/tests/test_kit_markers.py" ...` sweep and `--exclude='test_kit_markers.py' --exclude='test_bootstrap_consumer.py' ...` rsync.
**Suggested disposition**: Edit item 7 to name scripts/local/engine-consumer.sh (the KIT-0054 removal task will not catch this reference — it lives in a skill, not the shim set).

### A37 [contradiction/medium] `.claude/commands/preflight.md`
**Where**: Lines 43-44 (gate line format), Step 2 table (lines 55-66) and prescriptive actions (lines 75-76)
**Issue**: The command documents the gate contract as `GATE:<number>:<name>:PASS|FAIL|PENDING:<detail>` with "PENDING (Gate 1 only, KIT-0034)" and a PASS/FAIL-only presentation table — but preflight-check.sh has emitted a fourth status, SKIP, for Gates 2/3 since KIT-0056 (bots declared absent). An agent literal-following this doc has no instruction for parsing/presenting SKIP, and the "Gate 2/3 fails: wait for the bot" remedies are wrong advice on a declared-no-bots project.
**Evidence**: preflight.md line 43: "outputs structured `GATE:<number>:<name>:PASS|FAIL|PENDING:<detail>` lines". preflight-check.sh line 20: `#   GATE:<number>:<name>:PASS|FAIL|PENDING|SKIP:<detail>`; lines 26-28: "SKIP (KIT-0056, ADR-0027 P5): the gate does not apply — a `bots:` declaration..."; line 485: `GATE:2:CodeRabbit:SKIP:declared absent in kit-install...`; line 549: same for Gate 3; line 33: "0 — All gates pass (SKIP counts as satisfied)".
**Suggested disposition**: Update preflight.md to add SKIP to the format string, the table legend, and a "SKIP = satisfied by bot declaration" note. Possible partial overlap with KIT-0062 (preflight Gate 2-3 honesty) — verify before filing separately, but KIT-0062 is scoped to gate behavior, not this command doc.

### A38 [version-drift/medium] `.claude/commands/commit-push-pr.md`
**Where**: Step 2, line 55
**Issue**: Live command hardcodes the commit trailer `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` — every agent following /commit-push-pr signs commits as Opus 4.6 regardless of the actual model, while the agent roster has moved on (canonical agents documented as Opus 4.8, plus Fable 5 `-f5` variants).
**Evidence**: commit-push-pr.md line 55: "Include `Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>` trailer". .claude/agents/planner-f5.md line 13: "A fork of the canonical `planner` (V2, Opus 4.8)"; .claude/agents/feature-developer-f5.md line 14: "(V2, Opus 4.8) pinned to `claude-fable-5`". Three live surfaces name three different model versions for the same authorship function.
**Suggested disposition**: Make the trailer model-agnostic (e.g. "the model you are running as") or drop the pinned version from the command.

### A39 [contradiction/high] `.kit/docs/LINEAR-SYNC-BEHAVIOR.md`
**Where**: lines 18-21, 108, 146-147
**Issue**: Documents `./scripts/project linearsync    # or: ./scripts/project sync` — but `project sync` was repurposed by KIT-0036 as the pull-based core-scripts sync. Following this doc runs a completely different (repo-mutating) command. Also every command uses the pre-v0.4.0 `./scripts/project` path, and it cites `scripts/sync_tasks_to_linear.py` / `scripts/linear_sync_utils.py` which now live in `scripts/optional/`.
**Evidence**: Doc line 108: '`./scripts/project linearsync`    # or: ./scripts/project sync'. Live code scripts/core/project:2115-2121: `if command == "sync":` with comment 'an alias for `linearsync`; it now means core sync. Use `linearsync`'. `ls scripts/core/sync_tasks_to_linear.py` → No such file; actual: scripts/optional/sync_tasks_to_linear.py.
**Suggested disposition**: Update all paths to ./scripts/core/project, delete the 'or: sync' alias claim, fix script locations to scripts/optional/.

### A40 [contradiction/high] `.kit/context/workflows/EVALUATOR-LIBRARY-WORKFLOW.md`
**Where**: lines 33, 43-49
**Issue**: Claims library-installed evaluators land 'as flat YAML files (e.g. google-arch-review-fast.yml)' and that provider subdirectories (e.g. `.adversarial/evaluators/google/arch-review-fast/`) are duplicate manual copies to `rm -rf`. The actual installed layout is exclusively provider/name/ directories with evaluator.yml; zero flat *.yml files exist. Following the doc's conflict-resolution advice would delete the entire installed evaluator set.
**Evidence**: Doc line 33: 'Installed evaluators land in `.adversarial/evaluators/` as flat YAML files'; line 46: 'rm -rf .adversarial/evaluators/<provider>/<evaluator-name>'. Verified: `ls .adversarial/evaluators/*.yml` → no matches; tree is anthropic/, google/, mistral/, openai/ each containing <name>/evaluator.yml.
**Suggested disposition**: Rewrite the install-layout and Conflict Resolution sections to match the provider-subdirectory layout that adversarial-workflow >=1.0.x actually uses.

### A41 [contradiction/high] `.kit/context/workflows/COVERAGE-WORKFLOW.md`
**Where**: lines 20-36, 42, 55-65, 111-137, 145
**Issue**: Entire workflow is written for the thematic-cuts source project: every command is `--cov=thematic_cuts` (package does not exist here), baseline is '≥53% must not decrease' (pyproject pins fail_under=80), acceptable-gap examples are 'DaVinci API integration (requires DaVinci Resolve)'.
**Evidence**: Line 22: 'pytest tests/ --cov=thematic_cuts --cov-report=term-missing'; line 56: 'Project Baseline | ≥53%'. pyproject.toml:99: 'fail_under = 80'. `grep -rl thematic_cuts` shows no such package in this repo — only doc references.
**Suggested disposition**: Replace thematic_cuts with plain `--cov`, set baseline to the pyproject value (80), drop DaVinci-specific examples.

### A42 [stale-doc/high] `.kit/context/workflows/* + .kit/templates/AGENT-TEMPLATE.md (shared broken reference)`
**Where**: ADR-CREATION:205, COVERAGE:161, COMMIT-PROTOCOL:332, TESTING:352, TEST-SUITE:155, TASK-COMPLETION:118, AGENT-CREATION:330/396/724, AGENT-TEMPLATE:193
**Issue**: Eight live kit-dir surfaces cite `.kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md` as the current 'Quick Reference' / require updating it when creating agents — the file does not exist anywhere in the repo. AGENT-CREATION-WORKFLOW Step 13 even instructs `git add .kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md`. (TASK-COMPLETION-PROTOCOL:128 additionally links `../../adversarial/docs/EVALUATION-WORKFLOW.md`, which resolves to nonexistent .kit/adversarial/docs/ instead of .adversarial/docs/.)
**Evidence**: `ls .kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md` → No such file or directory. Repo-wide grep shows only references, no file; referencing files include seven workflow docs, AGENT-TEMPLATE.md, and .claude/agents/agent-creator.md.
**Suggested disposition**: Delete or replace the reference in all eight files (CLAUDE.md is the de facto quick reference now); fix the relative EVALUATION-WORKFLOW link.

### A43 [stale-doc/high] `.kit/context/workflows/AGENT-CREATION-WORKFLOW.md`
**Where**: lines 88, 423, 616, 653, 796, 945; DaVinci examples throughout
**Issue**: Describes retired flows as current: template at `.claude/agents/AGENT-TEMPLATE.md` (actual home is `.kit/templates/AGENT-TEMPLATE.md`, which create-agent.sh uses); Evaluator 'Non-Negotiable Elements' require documenting 'GPT-4o, Aider' (aider fully retired, adversarial-workflow >=1.0.1); test tasks go in `.kit/tasks/active/` (folder layout is 1-backlog..9-reference); example push targets a leftover branch `claude/review-adversarial-workflow-docs-011CUrJoZmtBvWYGwiyvibxK`; examples are DaVinci-Resolve-specific.
**Evidence**: Line 88: 'cp .claude/agents/AGENT-TEMPLATE.md ...' vs scripts/optional/create-agent.sh:42: 'TEMPLATE_FILE="$PROJECT_ROOT/.kit/templates/AGENT-TEMPLATE.md"'. Line 423: '**Technical details** - GPT-4o, Aider, cost, autonomy note'. Line 616: 'Create .kit/tasks/active/TASK-2025-TEST-...'. `ls .claude/agents/` contains no AGENT-TEMPLATE.md.
**Suggested disposition**: Refresh paths (template home, task folders), strip Aider/GPT-4o mandates and DaVinci examples; not covered by KIT-0065 (which names .adversarial/scripts + create-project.md only).

### A44 [stale-doc/high] `.kit/context/AGENT-SYSTEM-GUIDE.md`
**Where**: lines 67-74, 145-162, 1029, 1051, 1188-1195
**Issue**: Presented as the current architecture guide (Status: Production-ready) but describes the pre-kit layout: `delegation/tasks/{active,completed,analysis,logs}` and `delegation/handoffs/` as the task system, and 'aider + GPT-4o' as the Stage-1 evaluation mechanism. Still pointed to as current guidance by AGENT-CREATION-WORKFLOW.md:948 ('Agent System Guide: .kit/context/AGENT-SYSTEM-GUIDE.md') and .claude/agents/create-project.md, so it is a live surface, not a historical record.
**Evidence**: Lines 67-74 diagram 'delegation/ ├── tasks/ │ ├── active/ ...'; line 1029: 'Uses aider + GPT-4o for evaluation'. No delegation/ directory exists in the repo; task folders are .kit/tasks/1-backlog..9-reference.
**Suggested disposition**: Rewrite the directory/evaluation sections for the .kit layout and current adversarial CLI, or demote the file to an archive and remove the live pointers to it.

### A45 [stale-doc/high] `.kit/launchers/preflight, .kit/launchers/onboarding, .kit/launchers/launch`
**Where**: preflight:6,235,241; onboarding:50,57,75; launch:139
**Issue**: All three live launcher scripts still print their pre-migration root location `agents/` in user-facing instructions: preflight says 'Usage: ./agents/preflight' and 'Next step: ./agents/onboarding'; onboarding says 'Run ./agents/preflight again after fixing', 'Run ./agents/onboarding again when ready', 'Use ./agents/launch for regular agent access'; launch's menu tip says 'edit agents/launch'. The scripts moved to .kit/launchers/ (ASK-0044) and no agents/ dir exists.
**Evidence**: preflight line 6: '# Usage: ./agents/preflight'; line 235/241: 'Next step: ./agents/onboarding'. onboarding line 50: 'Run ${CYAN}./agents/preflight${NC} again after fixing.' launch line 139: 'edit ${YELLOW}agents/launch${NC}'. `ls agents/` at repo root → directory does not exist; README/CLAUDE.md document .kit/launchers/*.
**Suggested disposition**: Update the printed paths to .kit/launchers/*. Also worth fixing while there: preflight's 'adversarial: pip install -e ".[dev]" / GPT-4o task evaluation' guidance predates the PyPI >=1.0.1 floor, and its Python check accepts 3.9 while the project pins 3.10-3.12.

### A46 [contradiction/high] `.kit/context/workflows/COMMIT-PROTOCOL.md`
**Where**: line 137
**Issue**: States ci-check runs a 'Coverage threshold check (53%+)' — contradicts pyproject.toml fail_under=80 and CLAUDE.md's 80% target. TESTING-WORKFLOW.md repeats the same 53% claim (line 223) plus `--cov=thematic_cuts` (line 37) and names two DaVinci-project slow tests (lines 137-139) that don't exist in this suite — notable because that file was otherwise updated as recently as 2026-07-17.
**Evidence**: COMMIT-PROTOCOL.md:137 'Coverage threshold check (53%+)'; TESTING-WORKFLOW.md:223 'Coverage check (53%+ threshold)', :37 'pytest tests/ --cov=thematic_cuts', :137 'test_error_handling_cascade (10.01s - DaVinci API integration)'. pyproject.toml:99 'fail_under = 80'.
**Suggested disposition**: Align both files with the pyproject threshold and this repo's actual suite.

### A47 [stale-doc/high] `.kit/templates/AGENT-TEMPLATE.md`
**Where**: lines 4, 182-186, 197, 332-338
**Issue**: The template every new agent is generated from (via create-agent.sh) bakes in retired facts: 'Runs: Non-interactively with `aider --yes` flag' (aider retired at adversarial-workflow >=1.0.1); 'Complete guide: .adversarial/docs/EVALUATION-WORKFLOW.md (347 lines)' (file is 936 lines); frontmatter default model `claude-sonnet-4-20250514` does not appear in the template's own Model Selection table (Opus 4.6 / Sonnet 4.5 / Haiku 4.5).
**Evidence**: Line 183: '- **Runs**: Non-interactively with `aider --yes` flag'; line 4: 'model: claude-sonnet-4-20250514' vs line 333 table listing `claude-sonnet-4-5-20250929` as Sonnet's ID; `grep -c '' .adversarial/docs/EVALUATION-WORKFLOW.md` → 936. create-agent.sh:42 confirms this template actively seeds new agents.
**Suggested disposition**: Drop the aider sentence, the line-count, and reconcile the default model with the table (distinct from KIT-0065's named file scope).

### A48 [stale-doc/high] `.kit/docs/KIT-MIGRATION-PLAYBOOK.md`
**Where**: lines 42, 146, 500-501; overall currency
**Issue**: The playbook (v1.0.0, 2026-03-30) directs downstream migrators to create and populate `.kit/skills/` as the home for 'builder-only skills (self-review, review-handoff, etc.)' — contradicting the shipped end-state where ALL skills live in .claude/skills/ and .kit/skills/ is deprecated symlinks (removal pinned in KIT-0059, which covers the symlinks, not this doc's instruction to build the old split downstream). It also claims 'the kit_builder tier in the manifest already syncs .kit/ contents' — the 3.5.0 manifest has no tiers at all (files + opted_in), and sync is now pull-based/shape-scoped.
**Evidence**: Line 42: '├── skills/  #   builder-only skills (self-review, review-handoff, etc.)'; line 146 mkdir includes 'skills'; lines 500-501: 'The kit_builder tier in the manifest already syncs .kit/ contents.' Verified scripts/.core-manifest.json keys: ['core_version','source_repo','synced_at','files','opted_in'] — no tiers. CLAUDE.md: '.kit/skills/ DEPRECATED — read-both symlinks, removed in 0.9.0 (KIT-0059)'.
**Suggested disposition**: Revise for the KIT-0057 skills home and sync-v3 manifest before any downstream migration pass (memory says downstream migrations are the next phase, so this doc is about to be load-bearing).

### A49 [stale-doc/high] `.kit/context/workflows/TEMP-THEN-COMMIT-PATTERN.md`
**Where**: lines 65-66
**Issue**: Cites as the pattern's live implementation 'the marker-merge step in `scripts/local/bootstrap-consumer.sh` (Step 2, kit workflow agents)' — bootstrap-consumer.sh is now a deprecated exec shim (KIT-0053/KIT-0054) containing no marker-merge; the live implementation moved to scripts/local/engine-consumer.sh.
**Evidence**: Doc line 65: 'Live implementation: the marker-merge step in scripts/local/bootstrap-consumer.sh'. bootstrap-consumer.sh header: '# DEPRECATED shim (KIT-0053): use scripts/local/bootstrap --adopt instead... execs the setup door'. engine-consumer.sh:301-302 contains the marker-merge step ('marker-bearing agents ... handled by the marker-merge').
**Suggested disposition**: Point the 'Live implementation' line at engine-consumer.sh; the doc reference will dangle entirely when KIT-0054 executes the shim removal in 0.9.0.

### A50 [stale-doc/high] `.kit/docs/tmux-tips.md`
**Where**: lines 14, 147, 193-195, 202, 237
**Issue**: Presents retired paths and a nonexistent script as the current recipe: starter files at `delegation/tasks/2-todo/`, wrapper scripts `./scripts/ci-check.sh` and `./scripts/lint-all.sh` labeled 'GOOD — runs without permission prompts' (lint-all.sh exists nowhere in the repo; ci-check is at scripts/core/), and spawn_command `env -u CLAUDECODE agents/launch $AGENT_NAME` (launcher moved to .kit/launchers/).
**Evidence**: Line 14: '--starter delegation/tasks/2-todo/DSP-0061-task.md'; lines 193-195: './scripts/ci-check.sh ... ./scripts/lint-all.sh'; line 237: 'spawn_command: env -u CLAUDECODE agents/launch $AGENT_NAME'. Searches: `ls scripts/lint-all.sh scripts/core/lint-all.sh` → No such file (both); no delegation/ or root agents/ directories exist.
**Suggested disposition**: Update paths (scripts/core/ci-check.sh, .kit/launchers/launch, .kit/tasks/) and drop or replace the lint-all.sh recommendation.

### A51 [stale-doc/high] `.kit/context/workflows/ADR-CREATION-WORKFLOW.md`
**Where**: lines 180-185, plus TEST-SUITE-WORKFLOW.md metrics
**Issue**: Points readers at example ADRs `docs/adr/0001-exact-timecode-arithmetic.md`, `0002-two-phase-consistent-assembly.md`, `0011-adversarial-workflow-integration.md` — none exist; docs/adr/ contains only ADR-0007, ADR-0008, about-adr.md and a template. (Same thematic-cuts residue as TEST-SUITE-WORKFLOW.md's 298/350 baselines and 53% coverage example.)
**Evidence**: Doc lines 182-184 list the three example files; `ls docs/adr/` → ADR-0007-unified-artifact-registry.md, ADR-0008-tiered-manifest-sync.md, ASK-UNIFIED-REGISTRY-TASK-STARTER.md, TEMPLATE-FOR-ADR-FILES.md, about-adr.md. AGENT-CREATION-WORKFLOW.md:949 likewise cites nonexistent 'docs/adr/0011-adversarial-workflow-integration.md'.
**Suggested disposition**: Point examples at the two real ADRs (or .kit/adr/ examples).

### A52 [version-drift/medium] `.kit/context/workflows/RESEARCH-QUALITY-STANDARDS.md + TASK-STARTER-TEMPLATE.md (minor residue)`
**Where**: RESEARCH-QUALITY:105-110; TASK-STARTER:349, 377
**Issue**: RESEARCH-QUALITY's evaluator-selection table (gpt52-reasoning / mistral-content / o3-chain) survives, but the kit's own docs (memory, EVALUATOR-LIBRARY-WORKFLOW) name code-reviewer/arch-review as the installed set — the table's picks do exist on disk so this is only drift, and TASK-STARTER-TEMPLATE still addresses 'For Coordinators (Tycho)' — Tycho is AEL's project-specific coordinator, not a kit agent — and its footer cross-references OPERATIONAL-RULES.md whose Task-tool-permission content is dated 2025-01/2025-11 pre-.kit vintage.
**Evidence**: RESEARCH-QUALITY lines 106-110 table; verified .adversarial/evaluators/openai/{gpt52-reasoning,o3-chain} and mistral/mistral-content exist (so not broken, just unmaintained selection guidance). TASK-STARTER-TEMPLATE.md:349 '### For Coordinators (Tycho)'; KIT-MIGRATION-PLAYBOOK.md:457 identifies tycho.md as AEL-specific.
**Suggested disposition**: Low-priority tidy: refresh evaluator guidance to the maintained set, replace 'Tycho' with 'planner'.

### A53 [version-drift/high] `README.md`
**Where**: lines 591-592 (footer)
**Issue**: README footer says '**Version**: 0.5.0 / **Last Updated**: 2026-03-30' while pyproject.toml says version = "0.8.0" (released 2026-07-14) and scripts/core/VERSION is 3.5.0. Three releases behind on the kit's front page.
**Evidence**: README.md:591-592: '**Version**: 0.5.0 / **Last Updated**: 2026-03-30'. pyproject.toml:16: 'version = "0.8.0"'. CHANGELOG.md has released sections for 0.6.0, 0.7.0, 0.8.0.
**Suggested disposition**: Update the footer to 0.8.0 (or drop the hand-maintained stamp and point at pyproject.toml like CLAUDE.md does).

### A54 [stale-doc/high] `README.md`
**Where**: lines 230, 325, 547-550
**Issue**: Three commands use the pre-v0.4.0 path `./scripts/project ...` (`install-evaluators` line 230, `linearsync` line 325, `reconfigure` lines 547-550). `scripts/project` does not exist; the script moved to `scripts/core/project` in v0.4.0 (2026-03-09). Every command as printed fails with 'no such file'.
**Evidence**: README.md:230 './scripts/project install-evaluators', :325 './scripts/project linearsync', :547 './scripts/project reconfigure'. `ls scripts/` shows only README.md, __init__.py, core/, local/, optional/ — no `project`. Subcommands exist in scripts/core/project (lines 2121, 2253, 2270). CLAUDE.md and CHANGELOG both use `./scripts/core/project`.
**Suggested disposition**: Change all three to `./scripts/core/project ...`.

### A55 [stale-doc/high] `README.md`
**Where**: line 392 (Documentation section)
**Issue**: Documentation index points to 'Agentive Development Guide: `docs/agentive-development/README.md`' — that tree was archived to `docs/archive/agentive-development/` (ASK-0034 era). The path does not exist; this is the only live surface pointing into the archive as current guidance.
**Evidence**: README.md:392: '- **Agentive Development Guide**: `docs/agentive-development/README.md`'. find docs/ shows the guide only under docs/archive/agentive-development/. Repo-wide grep for 'agentive-development' outside docs/archive hits only this README line.
**Suggested disposition**: Either repoint to `docs/archive/agentive-development/README.md` (labelled archived) or drop the bullet.

### A56 [version-drift/high] `CLAUDE.md`
**Where**: line 33 (Project Rules, KIT-LOCAL project-rules region)
**Issue**: Project Rules pin 'Black (v26.1.0, line-length=88)' but pyproject.toml pins `black==26.5.1`. Since ci-check.sh specifically warns on venv-vs-pyproject Black drift (KIT-0035), the injected-every-session CLAUDE.md naming the wrong pin is live misinformation.
**Evidence**: CLAUDE.md:33: '**Formatter**: Black (v26.1.0, line-length=88)'. pyproject.toml:36: '"black==26.5.1"'.
**Suggested disposition**: Update to 26.5.1, or reword to 'Black (pin in pyproject.toml)' so dependabot bumps can't strand it again.

### A57 [version-drift/high] `docs/DISTRIBUTION-ARCHITECTURE.md`
**Where**: section 3, lines 137-146
**Issue**: States the manifest `core_version` is 'currently `3.0.0`' and `scripts_core` has 17 files. The live manifest says core_version 3.5.0 and scripts_core has 26 entries. This doc is presented as **Status: Current**.
**Evidence**: docs/DISTRIBUTION-ARCHITECTURE.md:137-144: '`core_version` is the semver of the sync unit (currently `3.0.0`)' and tier table '| `scripts_core` | 17 |'. scripts/.core-manifest.json: core_version=3.5.0, files.scripts_core has 26 entries (commands_core 6, commands_optional 5, kit_builder 14 do still match).
**Suggested disposition**: Update the version and count, or replace hardcoded numbers with 'see scripts/.core-manifest.json' so the doc can't drift each core bump.

### A58 [stale-doc/high] `docs/CROSS-REPO-PATTERN.md`
**Where**: lines 371-376 ('Helper availability' callout)
**Issue**: Canonical doc claims `prepare-review-input.sh` and `lib/target_repo.sh` 'currently ship in projects bootstrapped since 2026-04' and that 'Upstreaming them into this kit's scripts/core/ is tracked via KIT-0026 / KIT-0030'. They were upstreamed into this kit in 0.7.0 (2026-06-13) and exist at scripts/core/. The doc's own line 325 even invokes `./scripts/core/prepare-review-input.sh`, contradicting the callout two paragraphs later.
**Evidence**: docs/CROSS-REPO-PATTERN.md:372-376 vs ls scripts/core/ (prepare-review-input.sh, lib/ present) and CHANGELOG 0.7.0: '`scripts/core/lib/target_repo.sh` + `prepare-review-input.sh` upstreamed from suwinex... manifest scripts_core 14→17'. Same doc line 325 uses the scripts/core path directly.
**Suggested disposition**: Delete the 'Helper availability' callout — the helpers ship in the kit's scripts_core tier now.

### A59 [contradiction/high] `docs/CROSS-REPO-PATTERN.md`
**Where**: lines 408-413 (Open Questions #1)
**Issue**: Open question says first-class `target_repo` config is 'Tracked as KIT-0027' — but KIT-0027 sits in `.kit/tasks/6-canceled/` (retired at KIT-0048 when the planning-repo shape shipped exactly this: `bootstrap --shape planning --target-path --target-github`, shown as the recommended setup in this same doc's Setup §1). The doc cites a canceled task as the live tracker for a question the kit already answered.
**Evidence**: docs/CROSS-REPO-PATTERN.md:410-412: 'Tracked as KIT-0027; the `## Target Repository` CLAUDE.md section is the current convention.' find .kit/tasks -name '*KIT-0027*' → .kit/tasks/6-canceled/KIT-0027-cross-repo-first-class-support.md. Same doc lines 99-105 document the shipped `--shape planning` door with target pointers.
**Suggested disposition**: Rewrite Open Question 1 as resolved by ADR-0027 P2 (planning shape) or delete it.

### A60 [contradiction/medium] `docs/DISTRIBUTION-ARCHITECTURE.md`
**Where**: TL;DR line 20-23, diagrams lines 58/90, section 4 lines 158-169
**Issue**: Describes Channel B push as live current behavior: 'merging to `main` fires the sync Action, which opens PRs downstream' / 'fires on push to `main` when any watched path changes'. The workflow's push trigger was parked 2026-07-14 (CROSS_REPO_TOKEN never provisioned, 22/22 failures); it is workflow_dispatch-only. KIT-0045 tracks re-enablement, but nothing tracks this doc asserting the push path works today — a reader would expect downstream PRs that will never open.
**Evidence**: docs/DISTRIBUTION-ARCHITECTURE.md:20-22, 158-160 vs .github/workflows/sync-core-scripts.yml header: '── PARKED (2026-07-14...) The push trigger is disabled... workflow_dispatch is kept for deliberate runs once the token exists' and `on: workflow_dispatch:` only.
**Suggested disposition**: Add a one-line 'push trigger currently parked (KIT-0045); pull path and workflow_dispatch are the live mechanisms' note at the Channel B mentions, to be reverted when KIT-0045 lands.

### A61 [orphan/medium] `docs/adr/ASK-UNIFIED-REGISTRY-TASK-STARTER.md`
**Where**: whole file
**Issue**: A live-voiced task starter ('Your mission: Read ADR-0007 in full, then implement Phase 1... and Phase 2 as separate PRs') sitting in docs/adr/ — the directory about-adr.md defines as the downstream project's fresh ADR space. Its owning feature is gone: ASK-0048 / PR #45 was closed unmerged 2026-07-14 and parked with a needs-re-evaluation disposition. Nothing in the repo references this file; task starters otherwise live under .kit/, not docs/adr/, and this one exports to every consumer as instruction to build a parked feature.
**Evidence**: docs/adr/ASK-UNIFIED-REGISTRY-TASK-STARTER.md:16: 'Your mission: ... implement Phase 1 (metadata adoption) and Phase 2 (CLI tooling) as separate PRs.' Repo-wide grep for 'ASK-UNIFIED-REGISTRY' finds zero references outside the file itself. .kit/tasks/1-backlog/ASK-0048-unified-artifact-registry.md carries the parked/re-evaluate disposition.
**Suggested disposition**: Remove it or move it next to the parked ASK-0048 spec with a superseded banner; docs/adr/ should hold ADRs only.

### A62 [contradiction/medium] `docs/adr/about-adr.md`
**Where**: lines 3, 61-65 vs directory contents
**Issue**: The index doc declares 'This directory is for **your project's** architectural decisions. Start fresh with `ADR-0001`' and its ADR table is empty ('*Start with ADR-0001*'), but the directory actually contains two kit-authored ADRs (ADR-0007 Proposed, ADR-0008 Accepted — ADR-0008 is cited as live governance by DISTRIBUTION-ARCHITECTURE and MANIFEST-UPGRADE-GUIDE) plus a task starter. A consumer following the doc would collide with ADR-0007/0008 numbering; the doc and the tree disagree about what lives here.
**Evidence**: docs/adr/about-adr.md:3 'Start fresh with `ADR-0001`', :63-65 empty table. ls docs/adr/ → ADR-0007-unified-artifact-registry.md, ADR-0008-tiered-manifest-sync.md, ASK-UNIFIED-REGISTRY-TASK-STARTER.md, TEMPLATE-FOR-ADR-FILES.md, about-adr.md. ADR-0007:9 even says 'This ADR lives in adversarial-evaluator-library'.
**Suggested disposition**: Either move ADR-0007/0008 to .kit/adr/ (their governance role is kit-side; ADR-0008 already originated as KIT-ADR-0022) or list them in about-adr.md and tell consumers to start at ADR-0009.

### A63 [stale-doc/medium] `docs/CROSS-REPO-PATTERN.md`
**Where**: lines 401-406 ('Fitting into the agent workflow')
**Issue**: References 'The feature-developer agent's evaluator gate (Phase 7 in v6/v7)' as current guidance. feature-developer-v6/-v7 were consolidated into the canonical `feature-developer.md` (plus `-f5`) and the versioned files removed in the 0.8.0 cycle (CHANGELOG 'Removed: feature-developer-v3/v6/v7'). No v6/v7 agent files exist.
**Evidence**: docs/CROSS-REPO-PATTERN.md:403: 'evaluator gate (Phase 7 in v6/v7) expects...'. ls .claude/agents/ shows feature-developer.md and feature-developer-f5.md only. CHANGELOG.md:331-334 records removal of the v3/v6/v7 files.
**Suggested disposition**: Reword to 'the feature-developer agent's evaluator gate' without version suffixes.

### A64 [version-drift/medium] `docs/DISTRIBUTION-ARCHITECTURE.md`
**Where**: lines 6-8 (header stamp)
**Issue**: Header still reads 'Version: 1.1.0 / Last updated: 2026-07-04' although KIT-0057 (commit 7ae8c6a, 2026-07-22) added the 14-line 'Canonical homes (KIT-ADR-0027 P6)' section without bumping either field — violating the doc's own §6 rule that 'Documents (like this one) are semver-stamped too'.
**Evidence**: Header lines 6-8 vs `git log -- docs/DISTRIBUTION-ARCHITECTURE.md` (top: 7ae8c6a feat(KIT-0057)... (#90)) and `git show 7ae8c6a --stat` → 14 insertions in this file, none touching the Version/Last-updated lines.
**Suggested disposition**: Bump to 1.2.0 / 2026-07-22 (content addition = minor per its own convention).

### A65 [contradiction/low] `README.md`
**Where**: lines 180-193 (Agents table)
**Issue**: The 'Agents (`.claude/agents/`)' table lists 10 agents but the directory holds 16 — missing `project-intake` (which the same README's Consumer Project section relies on at line 501), `upgrader`, `bootstrap`, `onboarding`, `feature-developer-f5`, `planner-f5`. Presented as the inventory of what's included.
**Evidence**: README.md:180-193 table (10 rows) vs ls .claude/agents/ (16 files incl. project-intake.md, upgrader.md, bootstrap.md, onboarding.md, feature-developer-f5.md, planner-f5.md). README.md:501 tells users to invoke the `project-intake` agent that the inventory table omits.
**Suggested disposition**: Add the missing rows (at minimum project-intake and upgrader) or caption the table as a selection with a pointer to `.claude/agents/`.

### A66 [stale-doc/low] `CHANGELOG.md`
**Where**: lines 671-680 (link definitions)
**Issue**: Keep-a-Changelog link definitions stop at 0.5.0 — no [0.5.1], [0.6.0], [0.7.0], [0.8.0], or [Unreleased] compare links, so the four most recent release headings render as dead references while older ones link.
**Evidence**: CHANGELOG.md:671-680 defines links only for 0.1.0-0.5.0; headings [0.5.1] (line 453), [0.6.0] (413), [0.7.0] (350), [0.8.0] (139) and [Unreleased] (8) have no matching definitions.
**Suggested disposition**: Add the missing compare links (v0.5.0...v0.5.1 through v0.8.0...HEAD) — one-line fix per release, ideally as part of the 0.9.0 cut.

### A67 [contradiction/high] `.adversarial/config.yml`
**Where**: lines 5, 8, 13
**Issue**: The live, git-tracked config the adversarial CLI reads disagrees with its own template and with the tree: `task_directory: tasks/` (no such directory — tasks live in .kit/tasks/), `evaluator_model: gpt-4o` (config.yml.template lines 31-32 declare 'evaluator_model field is deprecated'), and `test_command: pytest` vs template's `pytest tests/ -v`. config.yml appears to predate the template rewrite (both 2026-03-30) and was never re-generated.
**Evidence**: config.yml lines 5/8/13: `evaluator_model: gpt-4o`, `task_directory: tasks/`, `test_command: pytest`. config.yml.template line 15: `task_directory: .kit/tasks/`; line 24: `test_command: pytest tests/ -v`; lines 31-32: 'Note: evaluator_model field is deprecated.' `ls` confirms no top-level tasks/ dir. Both files are git-tracked (git ls-files).
**Suggested disposition**: Regenerate config.yml from config.yml.template (or hand-fix task_directory/test_command and drop evaluator_model). One-line fix; could ride along with KIT-0065 but is not in its spec.

### A68 [stale-doc/high] `.adversarial/docs/EVALUATION-WORKFLOW.md`
**Where**: lines 349-380, 466, 826, 888-900, 908, 917
**Issue**: Live guidance doc (README.md:395 and five agents cite it as the 'Complete Guide') is built around a `delegation/` tree that does not exist and cites eight companion documents that do not exist: delegation/tasks/2-todo|3-in-progress paths (9 occurrences), .adversarial/docs/BUGFIX-OUTPUT-CAPTURE.md, docs/adr/ADR-0011-adversarial-workflow-integration.md, .kit/context/ADVERSARIAL-VERIFICATION.md, delegation/handoffs/EVALUATOR-WORKFLOW-VERIFICATION-2025-10-24.md, .kit/context/PROCEDURAL-KNOWLEDGE-INDEX.md, documentation-style-guide.md, agentive-development-glossary.md. Also asserts CLI location /Library/Frameworks/.../3.11/bin/adversarial as canonical (line 885). This staleness is broader than KIT-0065 F3, which only re-points the aider-script references.
**Evidence**: grep -c 'delegation' on the doc = 9; `ls delegation` → 'No such file or directory'; .adversarial/docs/ contains only EVALUATION-WORKFLOW.md; docs/adr/ contains only ADR-0007/ADR-0008 (+templates); grep of .kit/context/ for procedural|adversarial|style-guide|glossary filenames returned nothing. Live referencers: README.md:395, .claude/agents/{document-reviewer,security-reviewer,test-runner,agent-creator,create-project}.md.
**Suggested disposition**: Fold a full doc refresh into KIT-0065 F3 (widen its scope) or file a separate doc-refresh task: replace delegation/ paths with .kit/tasks/, drop or fix the eight dead cross-references, point the ADR line at .kit/adr/KIT-ADR-0004-adversarial-workflow-integration.md.

### A69 [orphan/high] `.adversarial/evaluators/evaluators`
**Where**: symlink at directory root
**Issue**: Self-referential symlink: .adversarial/evaluators/evaluators -> /Users/broadcaster_three/Github/agentive-starter-kit/.adversarial/evaluators, i.e. it points at its own parent, creating an infinite-recursion path for any tool that follows symlinks. Created 2026-07-14 19:53, the same timestamp as the v0.10.0 evaluator-library install — almost certainly a botched copy/link step in an install-evaluators run.
**Evidence**: `ls -la .adversarial/evaluators/evaluators` → `lrwxr-xr-x ... evaluators -> /Users/broadcaster_three/Github/agentive-starter-kit/.adversarial/evaluators`. `git ls-files -s .adversarial/evaluators/evaluators` → empty (untracked). Repo-wide grep found nothing referencing an `evaluators/evaluators` path.
**Suggested disposition**: Delete the symlink (untracked, so a plain rm; no git change needed). Optionally check cmd_install_evaluators in scripts/core/project for the copy bug that produced it.

### A70 [stale-doc/high] `.adversarial/config.yml.template`
**Where**: line 7
**Issue**: Header comment instructs `Run ./scripts/project install-evaluators` — the pre-v0.4.0 script path retired by ASK-0042. Current path is ./scripts/core/project, which EVALUATION-WORKFLOW.md line 245 itself uses, so the two .adversarial surfaces also disagree with each other.
**Evidence**: config.yml.template line 7: `# - Library: Run ./scripts/project install-evaluators`. CLAUDE.md and scripts/.core-manifest.json confirm scripts/core/project as the current path; no scripts/project exists at repo root.
**Suggested disposition**: One-word fix: ./scripts/core/project. Bundle with the config.yml regeneration.

### A71 [contradiction/high] `.adversarial/config.yml.template`
**Where**: template line 33; also EVALUATION-WORKFLOW.md line 261
**Issue**: Both live surfaces point readers at `.adversarial/evaluators/README.md` ('See: .adversarial/evaluators/README.md') but no such file exists — evaluators/ contains only .gitkeep, .installed-version, and per-provider subdirectories (each provider evaluator has its own README, but there is no top-level one).
**Evidence**: find over .adversarial/evaluators listed .gitkeep, .installed-version, and anthropic/google/mistral/openai subdirs only. grep -rln '.adversarial/evaluators/README.md' → live hits: .adversarial/config.yml.template, .adversarial/docs/EVALUATION-WORKFLOW.md (rest are historical task/handoff records).
**Suggested disposition**: Either point both references at the library repo docs (https://github.com/movito/adversarial-evaluator-library) or drop the reference.

### A72 [stale-doc/high] `.adversarial/templates/spec-compliance-input-template.md`
**Where**: line 5
**Issue**: Live template (used by .claude/commands/check-spec.md and the code-review-evaluator skill) tells the author to paste the spec 'from `delegation/tasks/3-in-progress/`' — the delegation/ tree does not exist; specs live in .kit/tasks/3-in-progress/.
**Evidence**: Template line 5: 'Paste the FULL task spec below (from `delegation/tasks/3-in-progress/`).' `ls delegation` → No such file or directory. Live referencers found via grep: .claude/commands/check-spec.md, .claude/skills/code-review-evaluator/SKILL.md.
**Suggested disposition**: Change the path to .kit/tasks/3-in-progress/. The other two templates (code-review, arch-assess) are clean.

### A73 [version-drift/high] `.adversarial/docs/EVALUATION-WORKFLOW.md`
**Where**: lines 7, 52, 760-780
**Issue**: Doc pins itself to 'adversarial CLI (v0.7.0+)' and 'As of adversarial-workflow v0.7.0, three built-in evaluators…', while pyproject.toml enforces `adversarial-workflow>=1.0.1` specifically to exclude 0.9.x-and-earlier builds; Known Issues 2 and 4 document 0.7-era Aider fallback/OpenRouter behavior of a dependency version the project now forbids installing.
**Evidence**: Doc line 7: 'Tool: `adversarial` CLI (v0.7.0+)'; line 52: 'As of adversarial-workflow v0.7.0…'. pyproject.toml line 42: `"adversarial-workflow>=1.0.1",  # Floor excludes 0.9.x aider-era builds that mutate the working tree during review`.
**Suggested disposition**: Update version claims to >=1.0.1 and delete/replace the aider-era Known Issues as part of the same doc refresh (partially overlaps KIT-0065 F3's re-pointing, but the version pins themselves are not in that spec).

### A74 [contradiction/high] `.adversarial/docs/EVALUATION-WORKFLOW.md`
**Where**: lines 639-661 (Verdict Types)
**Issue**: Doc teaches agents to expect APPROVED / NEEDS_REVISION / REJECT verdicts, but the installed evaluator library (v0.10.0) emits PASS / CONCERNS / FAIL (and the CLI's exit-code behavior keys on PASS). An agent grepping a log for 'APPROVED' per this guide will never match a current evaluator verdict.
**Evidence**: Doc lines 642/649/656: '✅ APPROVED', '⚠️ NEEDS_REVISION', '❌ REJECT'. .adversarial/evaluators/openai/code-reviewer/evaluator.yml lines 109-113: '**PASS**: No correctness bugs found…', '**FAIL**: One or more correctness bugs…', 'For CONCERNS and FAIL, list the specific findings…'. .installed-version = v0.10.0, matching pyproject [tool.adversarial] library_version.
**Suggested disposition**: Rewrite the Verdict Types section to the library's actual vocabulary during the doc refresh; note that different evaluators may use PASS/REVISION_SUGGESTED/FAIL variants.

### A75 [orphan/medium] `.adversarial/artifacts/`
**Where**: 6 files: ASK-0048-* (2026-04-02), KIT-0024-* (2026-03-28)
**Issue**: Only contents of the artifacts directory are leftover intermediate files from two long-closed evaluation runs — four of the six are zero bytes (empty diffs/change summaries). KIT-0024 shipped 2026-03; ASK-0048's PR #45 was closed unmerged 2026-07-14. Nothing references them; they are untracked local residue of the aider-era review_implementation.sh flow.
**Evidence**: ls -la shows ASK-0048-code-review-input-{change-summary.txt,implementation.diff} and KIT-0024 equivalents at 0 bytes, file-status.txt at 53 bytes. `git ls-files .adversarial/artifacts` → empty (untracked). Repo-wide grep found no live references to these filenames.
**Suggested disposition**: Safe local rm when KIT-0065 executes (they were produced by the scripts that task deletes). No git change involved; low urgency.

### A76 [contradiction/high] `tests/test_project_script.py`
**Where**: line 356 (test_python_too_new_error), anchoring scripts/core/project lines 632/646/657
**Issue**: Test pins the Python >=3.13 rejection message as citing 'aider-chat' — a fully retired dependency. The live script it tests, scripts/core/project, still prints '(constraint from aider-chat dependency)' (line 657) and carries comments 'due to aider-chat constraint' (632, 646) plus '.aider' in exclude_dirs (299). Aider was retired (pyproject pins adversarial-workflow>=1.0.1 with a comment explicitly excluding aider-era builds; requires-python = '>=3.10,<3.13' is the real constraint).
**Evidence**: test_project_script.py:356: assert "aider-chat" in captured.out or "adversarial-workflow" in captured.out  # 'Should explain the constraint source'. scripts/core/project:657: print("   (constraint from aider-chat dependency)") — grep for 'aider' across scripts/ hits only these lines and a historical note in doctor.d/40-version-skew.py. KIT-0065 covers only .adversarial/scripts + create-project.md aider refs, not this message or test.
**Suggested disposition**: Reword the project-script constraint message to cite requires-python / adversarial-workflow; then tighten the test to assert the new wording and drop the 'aider-chat' disjunct (which currently keeps an aider-era message green).

### A77 [stale-doc/high] `tests/test_check_hook_seeds.py`
**Where**: lines 9-12 (module docstring)
**Issue**: Docstring states this module 'is excluded from the consumer tests/ rsync in bootstrap-consumer.sh (exclude + rm -f sweep)'. Since KIT-0053 the exclude and sweep live in engine-consumer.sh; bootstrap-consumer.sh is an exec shim with no rsync logic.
**Evidence**: grep of scripts/local/bootstrap-consumer.sh finds no 'exclude' or 'rm -f' lines (only the shim header). engine-consumer.sh:475 has "$TARGET/tests/test_check_hook_seeds.py" sweep and :482 --exclude='test_check_hook_seeds.py'. Sibling modules (test_bootstrap_shapes.py:11-13, test_entrance_shims.py:16-18, test_setup_door.py:15-17) were all updated to say 'engine-consumer.sh' / 'the consumer engine' — this one was missed.
**Suggested disposition**: One-word docstring fix: bootstrap-consumer.sh -> engine-consumer.sh.

### A78 [stale-doc/high] `tests/test_create_agent.py`
**Where**: lines 1-6 (module docstring), line 55 (test_script_file_exists docstring); also tests/integration/test_concurrent_agent_creation.py line 2
**Issue**: Header says 'Tests for scripts/create-agent.sh' and 'TDD Red Phase: The script does NOT exist yet; all tests that invoke it will fail until the Green Phase implementation is complete.' The script has shipped for many releases and lives at scripts/optional/create-agent.sh (moved in the v0.4.0 core/local/optional restructure). Both the path and the red-phase claim describe a long-gone state as current.
**Evidence**: conftest.py:282: CREATE_AGENT_SCRIPT = PROJECT_ROOT / "scripts" / "optional" / "create-agent.sh" — and ls scripts/optional/ confirms create-agent.sh exists there. test_create_agent.py:55 docstring: 'Script file exists at scripts/create-agent.sh.' integration/test_concurrent_agent_creation.py:2 repeats the old path.
**Suggested disposition**: Update both docstrings to scripts/optional/create-agent.sh and delete the 'script does NOT exist yet' red-phase paragraph.

### A79 [stale-doc/medium] `tests/test_linear_sync.py`
**Where**: line 17 (docstring) and fixture paths at lines 111, 125, 136, 198, 213, 229, 285-342, 485
**Issue**: Docstring says 'TDD Phase: RED (tests written, implementation pending)' though the implementation shipped long ago (scripts/optional/linear_sync_utils.py + sync_tasks_to_linear.py). All fixtures build task trees under 'delegation/tasks/...', the pre-ASK-0044 layout name; the live code reads .kit/tasks/. Tests only pass because the parser takes explicit file paths, so the retired layout name is silently pinned in every fixture.
**Evidence**: test_linear_sync.py:17 'TDD Phase: RED (tests written, implementation pending)'; :111 tmp_path / "delegation" / "tasks" / "2-todo" (and ~15 more). sync_tasks_to_linear.py:5 'reads task markdown files from all workflow folders in .kit/tasks/' and :513 base_dir = Path(".kit/tasks"). No non-test file references 'delegation' paths.
**Suggested disposition**: Drop the RED-phase line; rename fixture path segments delegation/tasks -> .kit/tasks so the tests model the current layout.

### A80 [contradiction/medium] `pyproject.toml`
**Where**: lines 59-64 ([tool.pytest.ini_options] markers)
**Issue**: Three of the four registered markers are dead or misleading: 'unit' and 'integration' are applied by zero tests (tests/integration/ uses only pytest.mark.slow), and 'requires_gql' is documented as deselectable via -m "not requires_gql" — but test_linear_sync.py implements it as a pytest.mark.skipif alias, so no test ever carries a marker literally named requires_gql and the advertised -m expression matches nothing.
**Evidence**: pyproject.toml:59-63 registers slow/integration/unit/requires_gql with the deselect hint. grep -rn 'pytest.mark.unit\|pytest.mark.integration' tests/ returns nothing; tests/integration/test_concurrent_agent_creation.py:28 uses pytestmark = pytest.mark.slow. test_linear_sync.py:34: requires_gql = pytest.mark.skipif(not GQL_AVAILABLE, ...) — applies a 'skipif' mark, not a 'requires_gql' mark.
**Suggested disposition**: Either apply real @pytest.mark.requires_gql marks alongside the skipif (making the -m hint true) and use/remove unit+integration, or prune the three unused marker registrations.

### A81 [version-drift/medium] `tests/conftest.py`
**Where**: line 214 (MINIMAL_TEMPLATE frontmatter)
**Issue**: The fallback agent template used when .kit/templates/AGENT-TEMPLATE.md is absent (CI containers, partial checkouts) pins 'model: claude-sonnet-4-5-20250929', while the real canonical template pins 'model: claude-sonnet-4-20250514'. The two template surfaces disagree, so create-agent tests exercise different frontmatter depending on which copy is present.
**Evidence**: conftest.py:214 'model: claude-sonnet-4-5-20250929' inside MINIMAL_TEMPLATE; .kit/templates/AGENT-TEMPLATE.md:4 'model: claude-sonnet-4-20250514'. setup_temp_project() (conftest.py:257-265) copies the real template when present, else writes MINIMAL_TEMPLATE — same test suite, two divergent model pins.
**Suggested disposition**: Pick one model string for both (or derive MINIMAL_TEMPLATE's model from the real template file when deciding drift policy); both pins predate current model IDs and should be reviewed together.

### A82 [dead-code/low] `tests/test_logging.py`
**Where**: lines 21 and 23
**Issue**: import tempfile and from pathlib import Path are unused in the module — their only occurrences are the import lines themselves. They survive because the CI flake8 step runs critical-errors-only selection.
**Evidence**: grep -n 'tempfile\|Path' tests/test_logging.py returns only lines 21 and 23 (the imports); no other use in the 301-line file.
**Suggested disposition**: Delete the two imports.

### A83 [stale-doc/low] `tests/test_project_script.py`
**Where**: line 2 (module docstring)
**Issue**: Docstring says 'Tests for scripts/project CLI commands' — the pre-v0.4.0 path. The script has lived at scripts/core/project since the core/local/optional restructure (the module itself loads it from scripts/core/project at line 39).
**Evidence**: test_project_script.py:2 'Tests for scripts/project CLI commands.' vs :39 _script_path = Path(__file__).parent.parent / "scripts" / "core" / "project". CLAUDE.md 'Key path: ./scripts/core/project (was ./scripts/project before v0.4.0)'.
**Suggested disposition**: One-line docstring fix: scripts/project -> scripts/core/project.

### A84 [version-drift/high] `.pre-commit-config.yaml`
**Where**: line 29
**Issue**: Black version drift across three live surfaces: pre-commit pins `rev: 26.1.0`, pyproject.toml line 36 pins `black==26.5.1`, and CLAUDE.md Project Rules state 'Formatter: Black (v26.1.0, line-length=88)'. Local commits format with 26.1.0 while CI (`pip install -e .[dev]` then `black --check`) uses 26.5.1 — the exact phantom-formatting-failure class ci-check.sh's own drift warning (lines 83-96) was added to catch.
**Evidence**: .pre-commit-config.yaml:28-29 `repo: https://github.com/psf/black / rev: 26.1.0`; pyproject.toml:36 `"black==26.5.1",`; CLAUDE.md '**Formatter**: Black (v26.1.0, line-length=88)'
**Suggested disposition**: Bump pre-commit black rev to 26.5.1 and update the CLAUDE.md version string (or drop the literal version from CLAUDE.md so pyproject stays the single pin)

### A85 [orphan/high] `.serena/claude-code/verify-serena.sh`
**Where**: whole file (esp. lines 3, 28, 55, 122-141)
**Issue**: Tracked, exported-to-consumers verification script targets Claude *Desktop*, not Claude Code: 'Run this after restarting Claude Desktop', checks `/Users/broadcaster_three/Library/Application Support/Claude/claude_desktop_config.json` (hardcoded operator home dir), and expects Swift+TypeScript LSPs — while the sibling SETUP-GUIDE.md:6 says 'Target: Claude Code CLI (not Claude Desktop)' and .serena/project.yml configures python only. Nothing references it.
**Evidence**: verify-serena.sh:124 `CONFIG_FILE="/Users/broadcaster_three/Library/Application Support/Claude/claude_desktop_config.json"`; :3 'Run this after restarting Claude Desktop'; :151 'Language servers configured for: Python, Swift, TypeScript'. Searches: `grep -rn "verify-serena"` across the repo (excluding .serena itself, .venv, .git) returned zero hits.
**Suggested disposition**: Delete, or rewrite as a Claude Code `claude mcp list`-based check without hardcoded personal paths (it ships to every consumer via git-archive export)

### A86 [stale-doc/high] `.serena/memories/project_overview.md`
**Where**: lines 18-31 (plus siblings style_and_conventions.md:27,34; task_completion_checklist.md:15; suggested_commands.md:24,32)
**Issue**: Serena memory files — served to every agent via list_memories/read_memory in the registered 'agentive-starter-kit' project — describe the pre-ASK-0044 layout as current: `agents/` launcher dir (now .kit/launchers/), `.agent-context/` (now .kit/context/), `delegation/tasks/` (now .kit/tasks/), `.agent-context/workflows/COMMIT-PROTOCOL.md`, `agents/launch <agent-name>`, and 'Version Current: 0.3.1' (actual 0.8.0). suggested_commands.md:24 also recommends `./scripts/core/verify-setup.sh — Validate development environment` although doctor is the health surface and verify-setup is a shim.
**Evidence**: project_overview.md:19-22 `agents/ - Agent launcher scripts`, `.agent-context/`, `delegation/tasks/`; :31 'Current: 0.3.1'; style_and_conventions.md:34 'Reference `.agent-context/workflows/COMMIT-PROTOCOL.md`'; suggested_commands.md:32 '`agents/launch <agent-name>`'. Verified: no `agents/` dir at repo root (`ls agents` → not found); pyproject version 0.8.0. Note: .serena/.gitignore excludes `memories/`, so these are local-only files — but they are live agent-facing guidance, not history.
**Suggested disposition**: Regenerate all four Serena memories (serena onboarding rerun or manual edit) to the .kit/ layout, v0.8.0, and doctor-first guidance

### A87 [stale-doc/high] `.serena/claude-code/CONTEXT-CONFIGURATION-GUIDE.md`
**Where**: lines 152, 169, 725, 946-992 (plus CONTEXT-CHANGE-CHECKLIST.md:128-129, TYPESCRIPT-SETUP.md:56)
**Issue**: Tracked serena docs give Claude-Desktop-era configuration (editing claude_desktop_config.json) with the operator's hardcoded machine paths (`/Users/broadcaster_three/.local/bin/uvx`, `/Users/broadcaster_three/.nvm/...`, `/Users/broadcaster_three/Github/other-project`) presented as the current setup recipe — contradicting the kit's own setup-serena.sh, which configures via `claude mcp add --scope user`, and SETUP-GUIDE.md's 'Target: Claude Code CLI (not Claude Desktop)'.
**Evidence**: CONTEXT-CONFIGURATION-GUIDE.md:152 `"command": "/Users/broadcaster_three/.local/bin/uvx"`; :169 '`command` uses full path: /Users/broadcaster_three/.local/bin/uvx'; TYPESCRIPT-SETUP.md:56 'Expected: /Users/broadcaster_three/.nvm/versions/node/v22.18.0/bin/typescript-language-server'; setup-serena.sh:84 `claude mcp add --scope user serena ...`
**Suggested disposition**: Purge or genericize the .serena/claude-code/ guides (remove Desktop config paths and personal home-dir references); these export verbatim into every new consumer project

### A88 [contradiction/high] `pyproject.toml`
**Where**: lines 37, 71-77 (with CLAUDE.md Project Rules)
**Issue**: Ruff is declared a project linter on three surfaces — CLAUDE.md ('Linting: Ruff (E, F, I, N, W rules), flake8'), `[tool.ruff]`/`[tool.ruff.lint]` config, and dev dep `ruff>=0.15.22` — but no enforcement surface runs it: test.yml lint job runs only black/isort/flake8, .pre-commit-config.yaml has no ruff hook, and ci-check.sh's built-in gauntlet (steps 1-6) never invokes ruff. Whole-repo search for ruff invocations in *.sh/*.yml/*.py found only the pyproject config block (plus an advisory line in the gitignored serena memory).
**Evidence**: pyproject.toml:37 `"ruff>=0.15.22",`; :75-76 `[tool.ruff.lint] select = ["E", "F", "I", "N", "W"]`; test.yml:67-77 (Black/isort/flake8 only); ci-check.sh:98-177 (6 steps, no ruff); grep -rn "ruff" over sh/yml/toml/py excluding .venv/.adversarial/inputs → pyproject.toml only
**Suggested disposition**: Either wire ruff into ci-check.sh/pre-commit/test.yml, or drop the ruff dep+config and the CLAUDE.md claim so docs match the actual gate set

### A89 [version-drift/high] `.serena/project.yml.template`
**Where**: lines 33-38
**Issue**: Template (seeded into project.yml by setup-serena.sh steps 3) uses the old Serena config schema key `languages:`, while the actual live .serena/project.yml — generated by current Serena — uses `language_servers:` (line 182-183) and a substantially different field set (base_modes, ls_workspace_folders, etc.). A consumer running setup-serena.sh gets a config in a schema current Serena no longer documents.
**Evidence**: project.yml.template:33-34 `languages:\n  - python`; .serena/project.yml:182-183 `language_servers:\n- python`; setup-serena.sh:110-118 copies template → project.yml
**Suggested disposition**: Regenerate project.yml.template from the current Serena default project.yml (keeping the ${PROJECT_NAME} substitution)

### A90 [stale-doc/medium] `.serena/claude-code/SETUP-GUIDE.md`
**Where**: line 542 (also lines 299-316)
**Issue**: Live setup guide points to 'ADR-0040: Architectural decision for Serena adoption' as the project-specific reference, but no ADR-0040 exists anywhere in this repo (docs/adr/ has only ADR-0007/ADR-0008; the actual serena decision record is .kit/adr/KIT-ADR-0002-serena-mcp-integration.md). The guide (dated 2025-11-19, 'Serena Version: 0.1.4') also states MCP config lives at `~/.config/claude/mcp_settings.json` via `claude mcp add-json`, while the kit's own setup-serena.sh uses `claude mcp add --scope user`.
**Evidence**: SETUP-GUIDE.md:542 '- **ADR-0040**: Architectural decision for Serena adoption'; `ls docs/adr/` → ADR-0007, ADR-0008, templates only; .kit/adr/KIT-ADR-0002-serena-mcp-integration.md exists; SETUP-GUIDE.md:301-303 '~/.config/claude/mcp_settings.json'
**Suggested disposition**: Repoint the reference to KIT-ADR-0002 and align the install instructions with setup-serena.sh (or fold the guide's install section into the script's --help)

### A91 [contradiction/medium] `scripts/core/ci-check.sh`
**Where**: lines 2, 128 vs .github/workflows/test.yml:77
**Issue**: ci-check.sh's header claims it 'mirrors GitHub Actions test.yml', but the flake8 steps diverge: CI runs `flake8 scripts/ tests/ --exclude=scripts/optional ...` while the local gauntlet runs `python3 -m flake8 scripts/ tests/ ...` with no exclusion. An E9/F-class error in scripts/optional/ fails locally but passes CI (and vice-versa the local run lints code CI deliberately skips).
**Evidence**: test.yml:77 `flake8 scripts/ tests/ --exclude=scripts/optional --max-line-length=88 --extend-ignore=E203,W503 --select=E9,F63,F7,F82`; ci-check.sh:128 `python3 -m flake8 scripts/ tests/ --max-line-length=88 --extend-ignore=E203,W503 --select=E9,F63,F7,F82` (no --exclude)
**Suggested disposition**: Add `--exclude=scripts/optional` to ci-check.sh step 3 (or remove it from test.yml) so the mirror claim holds

## Uncertain (operator/planner call)

### (?) [version-drift] `scripts/.core-manifest.json`
**Issue**: The kit's own manifest carries core_version 3.5.0 (current, files last touched 2026-07-24) but synced_at '2026-06-13T00:00:00Z' — a frozen placeholder timestamp that predates six weeks of core changes (doctor.d additions, 90-config-home.sh, project 3.5.0). For the source-of-truth repo the field is vestigial, but any tooling or human reading it gets a false 'last synced' date.
**Evidence**: Manifest lines 2-4: "core_version": "3.5.0", "synced_at": "2026-06-13T00:00:00Z"; ls -la shows scripts/core/project and doctor.d/90-config-home.sh modified Jul 24. The engine only rewrites synced_at on a sync INTO a target (sync_from_manifest.py:588), so the kit's own copy never updates.
**Verifier note**: Facts verified (synced_at 2026-06-13T00:00:00Z, core_version 3.5.0, manifest last committed in KIT-0058 fda0174). But the concrete-harm claim is partly refuted: sync_from_manifest.py:588-596 and :790 ('synced_at alone never counts as drift') show the engine deliberately treats synced_at as target-only and ignores it for drift — so no kit tooling reads a false date. Checked KIT-0061 (baked core_version seeds in engines) and KIT-0063 (rsync-boundary inventory): neither covers this field, so it is untracked — but whether a target-only field left as a seed placeholder in the source repo is cruft or by-design is a human/design call. Auditor's own 'low' confidence is warranted.

### (?) [shim-undue] `.kit/launchers/onboarding (+ launch) vs the one setup door`
**Issue**: ADR-0027's end-state is ONE setup door (scripts/local/bootstrap) with old entrances demoted to tracked exec shims — but `.kit/launchers/onboarding` remains a fully live, README-advertised second setup entrance (writes .env-era ONBOARDING-STATE, runs its own 7-phase config flow) that never routes through the door and is in no tracked removal set (KIT-0047/0054 cover verify-setup and the bootstrap/create-project shims only). It also hardcodes fallback model `claude-sonnet-4-20250514` while launch defaults `claude-sonnet-4-5-20250929`.
**Evidence**: onboarding lines 94-126 create ONBOARDING-STATE.md with 'Phase 3: API keys configured / Phase 6: Configuration files created / Phase 7: GitHub repository setup'; line 92 model fallback. README.md:77 'Option C — Launcher-based: ... run the onboarding launcher'; CLAUDE.md Key Scripts table lists .kit/launchers/onboarding as 'First-time project setup'. No reference to it in scripts/local/bootstrap (grep 'onboarding' → no hits).
**Verifier note**: All facts verified: onboarding:96-122 writes a 7-phase ONBOARDING-STATE.md (incl. 'Phase 6: Configuration files created', 'Phase 7: GitHub repository setup'), line 92 fallback claude-sonnet-4-20250514 vs launch:110 claude-sonnet-4-5-20250929, `grep onboarding scripts/local/bootstrap` → no hits, README.md:77/140-164 advertises Option C, CLAUDE.md Key Scripts lists it as 'First-time project setup', and no known removal task names it. But whether this violates the end-state is a human call: ADR-0027 P3's shim set was explicitly bootstrap-consumer/create-project-flagless/verify-setup — onboarding was never named an 'old entrance', and both README and CLAUDE.md present it as a current, documented surface, consistent with it being a deliberately blessed agent-driven onboarding layer rather than an undisposed leftover. It is also not a 'compatibility layer', so the shim-undue class is misapplied even though the model-drift and no-disposition facts stand.
