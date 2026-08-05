# KIT-0083: Ship the adversarial CLI — Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-04
**From**: planner-f5
**To**: feature-developer
**Task**: `.kit/tasks/3-in-progress/KIT-0083-ship-adversarial-cli.md`
**Status**: READY NOW — KIT-0084 merged (`27813cf`, PR #105). Unblocked.
**Evaluation**: arch-review-fast APPROVED after 2 revision rounds —
`.adversarial/logs/KIT-0083-ship-adversarial-cli--arch-review-fast.md`

> ⚠️ **READ THE ADDENDUM AT THE BOTTOM FIRST** (2026-08-05). It resolves
> the F3 sequencing gate, corrects stale `bootstrap` line numbers, and
> removes one surface from scope. Where the addendum and the body below
> disagree, **the addendum wins**.

**Target Codebase**: This repo (agentive-starter-kit) — single-repo mode.

---

## Mission

`.adversarial/` config + evaluator library ship and pass doctor, but the
`adversarial` CLI binary is never installed and never checked — so the
planner's Phase 3 gate fails on first use in every fresh project. Install
the CLI as part of startup; add a doctor line that can't be masked by the
library's PASS. Full requirements F1–F4 in the spec; anchors below
verified 2026-08-04.

## Where each requirement lands

- **F1 (install step; preferred surface = `install-evaluators`)** —
  `scripts/core/project:799` `cmd_install_evaluators()`: today it
  git-clones the evaluator LIBRARY by ref (`--ref` flag parsing at
  `:804-812`, works without pyproject — planning shape, KIT-0068;
  `_get_evaluator_library_version()` at `:845` reads the pyproject pin).
  Extend it to also ensure the CLI: `command -v adversarial` → if absent
  and `uv` present, `uv tool install adversarial-workflow` (pin per F3);
  if `uv` absent, print the exact command and continue (the existing
  git-missing block at `:815-822` is the degradation pattern to mirror —
  one shared check-and-instruct helper, no duplication).
  Door side: the `--with-evaluators` offer (`bootstrap:594-602` prompt/
  skip-notice, `:691-692` flag parse, `:822` preset consumption) routes
  to `install-evaluators` unchanged in mechanism. Update BOTH help
  surfaces to say "evaluator library + CLI": the flag description around
  `bootstrap:53` and the usage line at `project:2512`.
- **F2 (doctor check)** — new file `scripts/core/doctor.d/` (name it to
  sort near `30-evaluators.sh`, e.g. `31-evaluator-cli.sh`): SKIP when
  `.adversarial/` absent (mirror `30-evaluators.sh:17-18`), FAIL when
  `.adversarial/` exists but `command -v adversarial` fails or
  `adversarial --version` exits non-zero, with the fix command in the
  message. Keep output to the `DOCTOR:<name>:<VERDICT>:<msg>` contract.
  Note: `adversarial --version` currently prints "Unknown fields in
  evaluator.yml" warnings to stderr on this machine — probe exit code,
  don't parse output.
- **F3 (pin coherence — SEQUENCING GATE)** — two pins exist:
  `pyproject.toml:42` (`adversarial-workflow>=1.0.1`, PyPI CLI) and
  `pyproject.toml:91` (`[tool.adversarial] library_version = "v0.10.0"`,
  library git ref). Per the spec: the canonical shape-independent home
  for BOTH pins is decided FIRST — in this PR or KIT-0079's, whichever
  lands first (candidates: `.adversarial/config.yml` or the CLAUDE.md
  kit-install region). If #60 is still open when you get here, install
  unpinned-latest with a `TODO(#60)` comment and say so in the PR body.
  Check #60 and KIT-0079 state before writing code.
- **F4 (KIT-0082 hook)** — only if KIT-0082's acceptance test has landed
  by then: add the evaluator-cli assertion. Otherwise note it in the PR
  body for KIT-0082 to pick up.

## Data-shape verification

- Doctor driver: check how `scripts/core/preflight-check.sh` /
  `project doctor` aggregate `doctor.d/*` exit codes before adding a new
  check — match the existing scripts' exit discipline (see how
  30-evaluators.sh terminates each path).
- `uv tool install` puts binaries in `~/.local/bin` — the doctor FAIL
  message should mention PATH if `command -v` misses right after an
  apparently-successful install.

## Test approach

- Doctor check: new cases in `tests/test_doctor.py` following existing
  fixtures (present-config/missing-binary → FAIL; no `.adversarial/` →
  SKIP; binary present → PASS via a stub `adversarial` on PATH).
- `install-evaluators`: extend its existing tests (grep tests/ for
  install_evaluators) with a stubbed `uv`/`command -v` path — do NOT
  hit the network or actually install in tests.
- Known local red herring: 8 test_doctor.py failures on Apple git 2.30.1
  (KIT-0080) are pre-existing; CI is the gate.
- `./scripts/core/ci-check.sh` before push; verify CI on GitHub.

## Out of scope — do not touch

- Resolving #60 itself (consume its decision or TODO it)
- KIT-0079's library-pin relocation (coordinate the home decision only)
- KIT-0080 (git 2.30.1), KIT-0084's .env work (should already be merged)
- While in the installer output: KIT-0081 F4 notes its tail says
  `GOOGLE_API_KEY` where the kit standard is `GEMINI_API_KEY`
  (`.env.template:110`, `20-env-keys.py:31`) — fix in passing ONLY if
  you're already editing that print block; otherwise leave for KIT-0081.

## Evaluation summary

APPROVED (round 3) after: pin-home candidates named + first-lander
sequencing rule (round-2 COUPLING finding); both help surfaces made
explicit (round-2 API finding); shared uv-fallback helper, no framework
(round-1 STRUCTURAL_RISK finding). No outstanding concerns.

---

**Task File**: `.kit/tasks/3-in-progress/KIT-0083-ship-adversarial-cli.md`
**Evaluation Log**: `.adversarial/logs/KIT-0083-ship-adversarial-cli--arch-review-fast.md`
**Source Issue**: movito/agentive-starter-kit#103 — comment there when the PR opens

---

# ADDENDUM — 2026-08-05 (operator session)

**This section supersedes the body above wherever they disagree.**
Everything here was verified against source on 2026-08-05.

## 1. F3 is RESOLVED — build against it, do not re-open

The body tells you to check #60 and pick between "decide now" and
`TODO(#60)`. That decision is **made**. Do not re-litigate it:

> **Canonical pin home = `.adversarial/config.yml`** (operator decision,
> 2026-08-05). This PR is the first lander and makes the call; KIT-0079
> consumes it.

Rationale to carry into the PR body — the constraint eliminates the
alternatives rather than us weighing preferences:

- `pyproject.toml` is **disqualified**: `engine-consumer.sh:294`
  deliberately never ships it to planning-shape repos
- the CLAUDE.md kit-install region is readable in both shapes but is an
  *install-record* surface (shape, profile, bots — facts about how the
  project was made). Pins are *config*, not record.
- `.adversarial/config.yml` ships in both shapes, already owns
  evaluator-suite configuration, and is the file F2's doctor check
  already keys off (`.adversarial/` present → check applies). Same file,
  same lifetime, same shape-independence.

Shape to write:

```yaml
# .adversarial/config.yml
adversarial_cli_version: "1.0.1"        # PyPI dist — uv tool install
evaluator_library_version: "v0.10.0"    # git tag — KIT-0079 moves this here
```

Read the CLI pin from there, with `pyproject.toml:42` kept as a
**fallback mirror** so the kit's own checkout keeps working. Do NOT
install unpinned-latest — that is the KIT-0068 A08 class (a silent
fallback installed a five-versions-old library).

**Also do**: leave a comment in `config.yml` recording *why* #60 is not
a consistency bug, so the next reader doesn't re-open it — the two pins
were never inconsistent, they name different artifacts:
`adversarial-workflow>=1.0.1` is a PyPI distribution (the CLI),
`v0.10.0` is a git tag on `adversarial-evaluator-library`. **#60 is a
location bug wearing a consistency costume.** Say this in the PR body
too; #60 should be updated with the reframing (see item 5).

### Root cause, for the PR body

Both pins landed in `pyproject.toml` at `c851276` (KIT-0035), when the
kit was **single-shape** — every project had one, so it was a fine home.
The planning shape arrived later at `924a5bb` (KIT-0053), which never
ships `pyproject.toml`. **The split did not create a bad location; it
turned a previously-fine one into an unreadable one for half of all
projects.** Any surface predating `924a5bb` is suspect for the same
class.

## 2. Stale line numbers — KIT-0084 shifted `bootstrap`

The body's `bootstrap` anchors (`:594-602`, `:691-692`, `:822`) are
**wrong** post-KIT-0084. Verified 2026-08-05:

| What | Real line |
|---|---|
| `--with-evaluators` flag help | `:53` |
| the offer block (prompt / non-TTY skip / dispatch) | `:753-763` |
| flag parse (`--with-evaluators` / `--without-evaluators`) | `:850-851` |
| preset key consumption (`evaluators`) | `:981-984` |

`scripts/core/project` anchors in the body are still correct:
`cmd_install_evaluators()` at `:799`, `--ref` parse `:804-812`,
git-missing degradation block `:815-822`, `_get_evaluator_library_version()`
at `:845`, usage text `:2512`. Re-verify before editing regardless —
that is what caught this.

## 3. `create-project.md` is OUT OF SCOPE — deliberately

`.claude/agents/create-project.md` contains three contradictions with
the install path you are building (`pipx` at `:180`/`:317`,
per-evaluator `adversarial library install` at `:214-217`, and an
unearned `adversarial-workflow: <version> verified` summary at `:260`).

**Do not fix them.** KIT-0087 F3 is their sole owner, and KIT-0078 F2
may delete the agent outright — a deleted file carries no
contradictions. This was considered and explicitly declined (operator
decision 2026-08-05, commit `041f75d`). Note them in the PR body; touch
nothing.

## 4. Verified environment facts

- `adversarial --version` **exits 0** but prints `Unknown fields in
  evaluator.yml` warnings to **stderr**. The doctor check must probe the
  **exit code**; a check that parses output will be fooled.
- `uv` and `adversarial` are both present at `~/.local/bin/` on this
  machine — so a naive `command -v` test passes locally and proves
  nothing about a fresh project. Test with a controlled `PATH`
  (`_restricted_bin` / `_stub_executable` in `tests/test_doctor.py:710`
  are the house helpers).
- **KIT-0080 red herring**: 3 `test_doctor.py` failures on this machine
  (`TestCoreBareCheck::test_bare_config_fails`,
  `TestConfigHomeCheck::test_derivation_without_override_names_the_sibling`,
  `TestWorktreeProvisioningCheck::test_worktree_missing_serena_config_warns`)
  are **pre-existing** — Apple git 2.30.1, tell is `dirname: illegal
  option -- -` in stderr. Verified against a clean HEAD on 2026-08-05.
  CI is the gate. Do not chase them; do not let them mask a real
  regression either — re-verify against a clean HEAD if the set changes.
- Pre-commit runs pytest-fast and takes **~3 minutes**. Budget for it;
  a 2-minute tool timeout kills the commit mid-hook (happened twice this
  session). Per KIT-0057: after any aborted hook run, `git log -1` +
  `git status` before proceeding — never trust the output tail.

## 5. Deliverables the body doesn't mention

- **F4 is deferred**: KIT-0082 (scaffold acceptance test) is still in
  `1-backlog`, so there is no test to add the assertion to. Note it in
  the PR body for KIT-0082 to pick up.
- **KIT-0055 overlap**: it needs the same `command -v adversarial`
  probe your F2 check introduces, plus editable-install detection. Keep
  them separate — F2 answers "does a binary exist", KIT-0055 answers
  "*which* binary is it", and the second is meaningless before the
  first. Note the overlap in the PR body.
- **Comment on #103** when the PR opens (already in the body).
- **Update #60** with the location-vs-consistency reframing from item 1.
- **Manifest**: `scripts/.core-manifest.json` enumerates
  `core/doctor.d/*` (see `:11-20`) and tests assert entry counts — add
  `core/doctor.d/31-evaluator-cli.sh` **in the same commit** as the new
  check, or the manifest test fails.

## 6. Suggested commit sequencing

Per the Phase 7 ordering rule, run the evaluator trio **before** opening
the PR — local tests green → trio → PR. This is a code task, so the full
trio applies (not the prose-sweep exception).

---

**Addendum author**: feature-developer session 2026-08-05, from the
operator conversation that specced KIT-0087 (`37cd1dc`) and recorded the
scope boundary (`041f75d`).
