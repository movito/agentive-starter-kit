# KIT-0066 Demo Transcript — project-intake end-to-end run

**Date**: 2026-07-24
**Runner**: feature-developer-f5 (executing the `project-intake`
procedure exactly as written in `.claude/agents/project-intake.md`)
**Demo root**: `/tmp/kit0066-intake-demo/` (uniquely named; no
`rm -rf` allowlist exists — leftovers listed at the end)
**Scratch inputs**: prototype folder `snip-stash/` (single-file Python
CLI: `snip.py`, `README.md`) + `PROTOTYPE-BRIEF.md` written to the
section list in `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md`
(purpose, languages, architecture, vocabulary, prefix SNIP, decisions,
solid/rough, issues, deps + secret names only, 3 next steps with
done-when lines).

## Step 0 — Read the brief

Brief parsed: name `snip-stash`, Python 3.11+ stdlib, prefix `SNIP`
(brief's suggestion; matches the derivation rule), 3 next-steps
entries, secrets by name only (`GITHUB_TOKEN`, future).

## Step 2 — Code repo

```
$ git -C /tmp/kit0066-intake-demo/snip-stash init
Initialized empty Git repository in /private/tmp/kit0066-intake-demo/snip-stash/.git/
# seeded .gitignore (.env, __pycache__/, .venv/)
$ git -C ... add -A && commit -m "chore: import prototype from Cowork handoff"
1b78609 chore: import prototype from Cowork handoff
```

**Deviation (demo only)**: `gh repo create` skipped to avoid external
side effects; visibility decision recorded as the default (private),
pointer `demoowner/snip-stash` used for the planning repo. In a real
run the agent asks the visibility question and pushes.

**No kit install** performed against the code folder (per the agent's
Step 2.6).

## Step 3 — Door run 1 (stranger path: `--no-preset`, flags only, non-TTY)

```
$ ./scripts/local/bootstrap --new /tmp/kit0066-intake-demo/snip-stash-planning \
    --shape planning --target-path ../snip-stash \
    --target-github demoowner/snip-stash --no-preset
door exit: 0
```

Door tail (doctor verdict relayed verbatim, per the exit contract —
exit 0 = installed, verdict reported not encoded):

```
Offer skipped (non-interactive): evaluators — pass --with-evaluators to install
DOCTOR:gh-auth:PASS:gh installed and authenticated
DOCTOR:env-keys:FAIL:.env not found — copy .env.template and fill in keys
DOCTOR:evaluators:PASS:evaluator library installed (7 entries)
DOCTOR:40-version-skew.py:SKIP:not applicable to profile 'none' (check declares: python)
DOCTOR:plugin-source:PASS:agentive-skills marketplace is GitHub-sourced
DOCTOR:push-sync-token:SKIP:sync-core-scripts.yml not present
DOCTOR:core-bare:PASS:primary clone is a normal checkout (core.bare=false)
DOCTOR:bot-presence:SKIP:cannot list PRs (unauthenticated or no remote)
DOCTOR:config-home:SKIP:no config home at /private/tmp/kit0066-intake-demo/agentive-config …
Doctor: 4 pass, 0 warn, 1 fail, 4 skip
Doctor verdict: FAILURES (see above) — install still succeeded; fix before working
Install complete: shape=planning profile=none → /tmp/kit0066-intake-demo/snip-stash-planning
```

The env-keys FAIL is the expected fresh-scratch-repo state (no keys);
the door's contract explicitly installs anyway and reports.

## Step 4 — Seed from the brief

- **4a**: `project-context` region filled in ALL FOUR seeded agents
  (`planner.md`, `planner-f5.md`, `feature-developer.md`,
  `feature-developer-f5.md`), marker lines kept intact; `stack-notes`
  filled in both feature-developer variants (explicit TODO lines left
  only where the brief was silent, per the agent text).
- **4b**: 3 backlog stubs transcribed 1:1 from the brief's next steps
  (titles, what/why, done-when → first acceptance criterion; no
  elaboration): `SNIP-0001-pytest-suite-cli-round-trip.md`,
  `SNIP-0002-handle-corrupt-stash-files.md`,
  `SNIP-0003-add-delete-and-search-commands.md`.
- **4c**: committed on the planning repo's `main`
  (`0d34f2f chore: seed project context and backlog from prototype brief`).

## Verification

```
## Target Repository            ← filled by the door from the flags
- **Path**: `../snip-stash`
- **GitHub**: `demoowner/snip-stash`

TODO count in planner.md project-context region: 0
SNIP-NNNN present in: all 4 seeded agents
backlog stubs: SNIP-0001, SNIP-0002, SNIP-0003
code repo kit-free (no .kit/.claude/scripts): confirmed
code repo top level: .git .gitignore PROTOTYPE-BRIEF.md README.md snip.py
```

## Preset-resolved run (operator-path proof)

Second door run WITHOUT `--no-preset` and WITHOUT `--shape` — the live
operator preset answered everything except the per-project pointers:

```
$ ./scripts/local/bootstrap --new /tmp/kit0066-intake-demo/snip-stash-planning2 \
    --target-path ../snip-stash --target-github demoowner/snip-stash
door exit: 0
Preset: ~/Github/agentive-config/preset (pass --no-preset to ignore it)   [path abbreviated]
planning shape → profile none (forced; the only legal pair)
  kit-install region written (shape: planning, profile: none, bots: coderabbit bugbot)
Seeded .env from preset env-source (mode 0600, gitignored; contents never printed)
DOCTOR:env-keys:FAIL:ANTHROPIC_API_KEY missing in .env
Doctor: 4 pass, 0 warn, 1 fail, 4 skip
Doctor verdict: FAILURES (see above) — install still succeeded; fix before working
Install complete: shape=planning profile=none → /tmp/kit0066-intake-demo/snip-stash-planning2
```

Shape and bots came from the preset; `.env` was seeded from
`env-source` without printing contents. The doctor FAIL is accurate —
the operator's env-source keys are deliberately unfilled. The seeded
`.env` was deleted from the demo dir immediately after capture.

## Observations

1. **Pre-existing, not from this task**: the scaffold copies
   `.claude/projects/-Users-broadcaster-three-Github-agentive-starter-kit/memory/feedback_evaluator_script_flow.md`
   into every consumer repo — a session-memory file tracked since
   ASK-0044 (PR #41, `2974e27`). Follow-up candidate: `git rm` +
   ignore pattern.
2. `project-intake.md` itself ships into consumer scaffolds via the
   `.claude/` rsync (same precedent as `bootstrap.md` /
   `create-project.md`, which are also kit-side); its text states it
   runs from a kit checkout.
3. Doctor's config-home line anchors to the DEMO repo's parent
   (`/private/tmp/kit0066-intake-demo/agentive-config`) — documented
   behavior (doctor anchors to the project it diagnoses), worth
   knowing when reading demo output.

## Cleanup

Demo repos deleted after the run (`/tmp/kit0066-intake-demo/` and its
four children). Any leftovers are listed in the PR/session report for
the operator (no `rm -rf` allowlist — deletion may require a manual
sweep of `/tmp/kit0066-intake-demo/`).

## Result vs acceptance criteria

- Pair created end-to-end in one procedure pass: ✅ (two local repos)
- Door exit 0 with doctor verdict relayed: ✅ (both runs)
- Context region filled from brief + prefix present: ✅ (4 agents)
- ≥1 backlog stub from next-steps: ✅ (3 stubs, transcription only)
- Code repo kit-free: ✅
- Zero changes to `scripts/local/bootstrap`: ✅ (composition only)
