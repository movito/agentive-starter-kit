# KIT-0118: Packaged-door fresh-install fixes + agentive-kit 0.4.0 release

**Status**: In Progress
**Priority**: high
**Assigned To**: feature-developer
**Estimated Effort**: 4-6 hours
**Created**: 2026-08-24
**Linear ID**: (automatically backfilled after first sync)

## Related Tasks

**Related**: KIT-0108 (engine consolidation — owns the engine-consumer.sh twin seam), KIT-0111 (version-bump guard — absorbs #144's CI-guard suggestion), KIT-0104/KIT-0105 (door-in-package arc this repairs)
**Closes**: GitHub issues #144, #145, #146

## Overview

An operator-driven from-scratch project setup (ixda-services, 2026-08-20)
filed three issues against the packaged setup door. All three are verified
against source. This task fixes the two code defects (#145, #146), then
bumps `agentive-kit` to **0.4.0** and publishes, which closes #144 —
one release train, so the published wheel carries the fixes.

**Why 0.4.0 now matters most (#144)**: the PyPI wheel (published
2026-08-09) predates KIT-ADR-0030's acceptance (2026-08-16) and contains
**no door** — no `agentive new`/`adopt` — yet reports the same
`agentive version` → `0.3.1` as main, which has both. This falsifies
`docs/STARTING-A-PROJECT.md:42` ("No kit clone is required to create a
project") for every PyPI install, and makes any bug report against
"0.3.1" ambiguous.

## Verified Facts (planner-verified 2026-08-24, kit main @ cb9ad4f)

Each claim below was re-verified against source this session; commands shown.

1. **Version + PyPI state**:
   `grep -n __version__ packages/agentive-kit/src/agentive_kit/__init__.py`
   → `7:__version__ = "0.3.1"`.
   PyPI JSON API → latest `0.3.1`, releases `['0.1.0','0.2.0','0.3.0','0.3.1']`.
   Package version is **single-sourced**: `packages/agentive-kit/pyproject.toml:15`
   `dynamic = ["version"]`, `:58` `version = { attr = "agentive_kit.__version__" }`.
   One bump point.
2. **Publish flow**: `.github/workflows/publish-agentive-kit.yml` —
   tag-triggered (`agentive-kit-v*`), trusted publishing (OIDC), guards
   tag == `__version__` only. Nothing guards "main changed under an
   already-published version" (that guard → KIT-0111, out of scope here).
3. **#145 placeholder** (`engine-consumer.sh`, planning shape):
   ```sh
   TP="${TARGET_PATH:-../<target-repo>  # TODO: set the product repo path}"
   TG="${TARGET_GITHUB:-<owner>/<repo>  # TODO: set the product repo}"
   ```
   Written verbatim into the kit-install region body via
   `KIT_INSTALL_BODY` printf (`target_path: %s` / `target_github: %s`).
   `load_record()` in `door/__init__.py` has no `#` handling — the prose
   becomes the recorded machine-read identity.
4. **#146.1 evaluators**: record body carries `shape/profile/target_path/
   target_github` + conditional `bots:` — the evaluator answer
   (`--without-evaluators`) is never persisted. `doctor/checks/30-evaluators.sh`
   SKIPs only when `.adversarial/` is absent; the consumer engine copies
   `.adversarial/` unconditionally → declined evaluators still FAIL
   (both `30-evaluators.sh` and `31-evaluator-cli.sh`).
   The `bots:` mechanism (door `normalize_bots`, doctor `_normalize_bots`
   + `_parse_record`) is the model to mirror.
5. **#146.2 TASK_PREFIX masking**: `doctor/checks/20-env-keys.py` —
   required-key loop (`REQUIRED_KEYS = ["ANTHROPIC_API_KEY"]`) hits
   `print(FAIL); return 0` **before** the `TASK_PREFIX` warn block.
   Seeded `.env.template` ships `ANTHROPIC_API_KEY` commented out and
   `TASK_PREFIX=` empty → on every fresh install the FAIL pre-empts the
   WARN the door explicitly promises (`door/__init__.py` prints
   "doctor warns until then"). Planning shape has no `--prefix` flag, so
   this warning is the only safety net for empty task-prefix identity.
6. **Twins are byte-identical today** (`diff -q` clean on both pairs):
   - `scripts/local/engine-consumer.sh` ↔ `packages/agentive-kit/src/agentive_kit/door/engines/engine-consumer.sh`
   - `scripts/core/doctor.d/*.{sh,py}` ↔ `packages/agentive-kit/src/agentive_kit/doctor/checks/*`
     (incl. `20-env-keys.py`, `30-evaluators.sh`, `31-evaluator-cli.sh`)

## Requirements

### Part A — #145: derive target_path, keep prose out of the record

1. In `engine-consumer.sh` (BOTH twins): when `TARGET_PATH` is empty and
   `TARGET_GITHUB` is set, default `TP` to `../${TARGET_GITHUB#*/}`
   (sibling-layout convention per `docs/STARTING-A-PROJECT.md`).
2. When neither flag is given, the recorded value must contain no `#`
   prose — bare `../<target-repo>` / `<owner>/<repo>` placeholders only
   (move any TODO hint to the console output or a comment line OUTSIDE
   the recorded value). Same treatment for `TG`.
3. Re-adoption path: `load_record()` must round-trip the new values
   cleanly (it already does for clean `key: value` lines — verify, don't
   assume; add/extend a test if the package has record-parse tests).

### Part B — #146.1: persist the evaluator answer; doctor SKIPs on declined

1. Door: record `evaluators: yes|no` in the kit-install region alongside
   `bots:` (write it in `engine-consumer.sh`'s `KIT_INSTALL_BODY`, or at
   the equivalent seam the door uses — follow how `bots:` flows from the
   door flag into the region, and mirror it).
2. Doctor: teach `_parse_record` to read `evaluators:`; `30-evaluators.sh`
   and `31-evaluator-cli.sh` SKIP with a "declined at install" message
   when `evaluators: no` is recorded. Absent line = legacy install =
   current behavior (fail-open to FAIL is correct there).
3. Tolerance rules match the `bots:` reader (case/whitespace normalization).

### Part C — #146.2: unmask the TASK_PREFIX warning

1. In `20-env-keys.py` (BOTH twins): collect the `TASK_PREFIX` finding
   independently of the required-key result. Preferred shape per the
   issue: fold the prefix problem into the FAIL detail string when both
   co-occur, OR emit both verdict lines — implementer's choice, but the
   fresh-install co-occurrence case MUST surface the prefix problem.
2. Do not change the check's verdict semantics otherwise (FAIL stays FAIL
   for missing required keys; prefix-only remains WARN).

### Part D — #144: version bump + release

1. Bump `packages/agentive-kit/src/agentive_kit/__init__.py:7` to
   `0.4.0` (feature addition — the door — under semver; single-sourced,
   no other version field edits in the package).
2. After merge to main: tag `agentive-kit-v0.4.0` → publish workflow runs
   (trusted publishing; verify the run goes green and PyPI shows 0.4.0).
3. Verify `docs/STARTING-A-PROJECT.md:42`'s promise is true post-publish:
   `uv tool install agentive-kit` (or upgrade) on a clean env exposes
   `agentive new` / `agentive adopt` and `agentive version` → `0.4.0`.
4. CHANGELOG entry for the package if one exists at package level;
   otherwise the repo-level convention applies.

### Out of scope

- CI guard "main changed under a published version" → **KIT-0111** (widen
  that spec's scope note; do not build it here).
- Engine twin consolidation → **KIT-0108**.
- New doctor checks from #142/#143 (gitignored-core-file, bare-CI-tool) —
  separate task, not this PR.
- Uninstalling/upgrading the globally-installed 0.3.1 on operator
  machines — operator chore, post-release.

## Twin discipline (MANDATORY)

Every edit to `engine-consumer.sh`, `20-env-keys.py`, `30-evaluators.sh`,
`31-evaluator-cli.sh` lands in BOTH copies, by **copy, not re-derivation**
(patterns.yml `harden_twins_by_copy_not_rederivation`). Twins are
byte-identical at task start; they must be byte-identical at PR time —
verify with `diff -q` per pair and paste the output in the PR body.
Doctor `_parse_record` lives only in the package (`doctor/__init__.py`) —
check whether `scripts/core/doctor.d/` has a driver-side twin of the
record reader before assuming single-copy.

## Test Requirements

- [ ] Record round-trip: planning-shape install with `--target-github`
      only → recorded `target_path` is `../<repo>`, no `#` in any value;
      `load_record()` returns the clean path.
- [ ] `--without-evaluators` install → region carries `evaluators: no`;
      doctor run on that tree → both evaluator checks emit SKIP.
- [ ] Evaluators accepted (or flag omitted + interactive yes) → checks
      behave as today.
- [ ] Legacy record (no `evaluators:` line) → current FAIL behavior
      preserved.
- [ ] `20-env-keys.py`: fresh-install fixture (API key commented,
      TASK_PREFIX empty) → output surfaces BOTH problems.
- [ ] Existing doctor/door test suites pass; coverage 80%+ on changed code.

## Acceptance Criteria

### Must Have
- [ ] Parts A–C implemented in both twins, `diff -q` clean per pair
- [ ] `__version__` = 0.4.0
- [ ] All tests passing, no regressions; CI green on GitHub
- [ ] Post-merge: tag pushed, publish workflow green, PyPI serves 0.4.0,
      wheel smoke-tested (`agentive new --help` works from a PyPI install)
- [ ] Issues #144, #145, #146 closed with commit/release references

### Should Have
- [ ] KIT-0111 spec updated with the package-side guard scope note
- [ ] Handoff note to KIT-0108 about the engine edits (seam awareness)

## Risks & Mitigations

- **Risk: record-format change breaks re-adoption on existing installs.**
  Mitigation: `evaluators:` is additive; absent line preserves current
  behavior. Test the legacy path explicitly.
- **Risk: publish is one-shot per version (PyPI accepts each version
  once).** Mitigation: tag only after CI green on main; the workflow
  already smoke-tests the wheel before publish.
- **Risk: doctor record reader has an undiscovered twin.** Mitigation:
  grep `scripts/core/doctor.d/` and the driver for a second `_parse_record`
  before editing.

## Time Estimate

| Phase | Time |
|-------|------|
| Pre-implementation checks + twin survey | 0.5 h |
| Part A (derive TP, clean placeholders) + tests | 1 h |
| Part B (evaluators record + SKIP) + tests | 1.5 h |
| Part C (unmask TASK_PREFIX) + tests | 0.5 h |
| Part D (bump, PR, tag, publish verify) | 1 h |
| Review rounds | 0.5–1.5 h |
| **Total** | **5–6.5 h** |

## Evaluation

**Round 1** (arch-review-fast, gemini-2.5-flash, 2026-08-24):
REVISION_SUGGESTED. Log:
`.adversarial/logs/KIT-0118-packaged-door-fresh-install-fixes--arch-review-fast.md`

Both findings are strategic debt, not defects in this plan; disposition:

1. **Twin discipline as manual sync** — acknowledged; consolidating the
   twins is KIT-0108's charter (the evaluator concedes this). This task
   keeps the twins byte-identical rather than consolidating mid-fix,
   deliberately. No spec change.
2. **Custom string record format** — acknowledged as a known missing
   abstraction. This task's `evaluators:` line is additive within the
   existing format; migrating the kit-install record to a standard
   serialization is deferred (candidate rider for KIT-0108 or a future
   record-format task). No spec change.

Gate disposition: findings recorded, plan unchanged — proceeding
(strategic-only findings; both tracked elsewhere).

## References

- GitHub issues: movito/agentive-starter-kit #144, #145, #146
- KIT-ADR-0030 (door ships in the package), KIT-ADR-0028 (packaging)
- `.github/workflows/publish-agentive-kit.yml`
- patterns.yml → `harden_twins_by_copy_not_rederivation`
- `.kit/context/workflows/COMMIT-PROTOCOL.md`, `TESTING-WORKFLOW.md`
