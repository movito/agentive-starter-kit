# KIT-0118 — Review Starter

**PR**: https://github.com/movito/agentive-starter-kit/pull/147
**Branch**: `feature/KIT-0118-packaged-door-fixes` → `main`
**Head**: `9da0223`
**Task**: `.kit/tasks/4-in-review/KIT-0118-packaged-door-fresh-install-fixes.md`
**Review record**: `.kit/context/reviews/KIT-0118-evaluator-review.md`
**Closes**: GitHub issues #144, #145, #146

## What changed

Three fresh-install defects in the packaged setup door, plus the version
bump that puts them on PyPI — one release train, because a fix that
doesn't ship in the wheel doesn't reach the operator who filed it.

- **#145** — the planning scaffold wrote `# TODO` prose *inside* the
  machine-read identity record, so the hint became the recorded target
  path. Values are bare now; `--target-github` alone derives
  `../<repo>` per the documented sibling layout.
- **#146.1** — the `--without-evaluators` answer was never persisted
  while `.adversarial/` is copied unconditionally, so doctor FAILed
  every project that took the door up on its own offer. An **answered**
  offer is now recorded as `evaluators: yes|no` and both checks SKIP on
  `no`.
- **#146.2** — the TASK_PREFIX warning was unreachable on fresh
  installs (the required-key FAIL returned first, and the shipped
  `.env.template` makes both conditions co-occur). Folded into the FAIL
  detail; still one protocol line.
- **#144** — `__version__` 0.3.1 → 0.4.0.

## Gate status

| Gate | State |
|------|-------|
| Tests (3.10 / 3.12 / 3.14) | ✅ pass |
| Lint & format | ✅ pass |
| CodeRabbit | ✅ `reviewDecision: APPROVED` on head `9da0223` (SHA-matched) |
| Cursor BugBot | ✅ clean |
| Review threads | ✅ 4/4 replied + resolved, `hasNextPage` false |
| Evaluators | ✅ full trio pre-PR, all findings dispositioned |
| Twin parity | ✅ `diff -q` clean, all four pairs |
| Suite | 1145 → 1210, coverage 90.15% |

No plugin-drift guard on this PR — it touches no rostered `.claude/`
component.

## What a reviewer should look hardest at

1. **The answered-vs-defaulted distinction** (`resolve_evaluator_offer`,
   `door/__init__.py`). This is the load-bearing design decision. Only
   an *answered* offer — flag, preset, or interactive prompt — writes
   `evaluators:`. A non-interactive run that merely defaults to "no"
   records nothing, because recording it would let a plain
   `agentive adopt` tell doctor to skip the evaluator checks on a
   project that never declined anything. If you disagree with that
   asymmetry, this is the place to say so.

2. **The prompt moved earlier in the interactive flow.** The evaluator
   answer must exist before the consumer engine writes the record (the
   engine is the record's one writer), so resolution was split out of
   `run_offers` and now runs before the scaffold. Interactive operators
   see the evaluator question sooner than before. The venv prompt did
   NOT move, so the two offers are no longer adjacent — deliberate, but
   worth a second opinion on the UX.

3. **The legacy-prose strip** (`engine-consumer.sh`, `_LEGACY_TODO`).
   It rewrites values read out of an existing `## Target Repository`
   section on adopt. Narrowed after review to the literal `# TODO`
   marker so a real `../target #1` survives, with a test asserting the
   expression under test is still the one in the engine.

4. **`DOCTOR_EVALUATORS` as the transport.** Checks never parse
   CLAUDE.md; the driver stays the single reader and passes the
   declaration down like `DOCTOR_ROOT`. Both drivers (packaged +
   `scripts/core/project`'s inline fallback) changed together, with a
   conformance table pinning them to one meaning.

## Review-process notes worth reading

**The bots beat the evaluator trio on this diff.** The trio ran pre-PR
on a full-content input and passed; CodeRabbit then found two real bugs,
one of them Major — `--evaluators=` skipped validation entirely, so an
explicitly-passed flag was silently dropped. That is the exact masking
class this task exists to close, sitting in the code the task added.

Meanwhile the deep evaluator (o3) returned FAIL on five findings, of
which **three were factually false** and verifiably so: it claimed
`GIT_CONFIG_*` leaks through a filter that strips anything starting with
`GIT_`; that `--with-evaluators=YES` records mixed case, when the flag
is boolean and the `=VALUE` form is refused at parse; and that duplicate
`evaluators:` lines accumulate, when the append is gated on the flag
being given. Each was checked against the tree before being dismissed,
and two were turned into regression tests anyway.

Per-finding dispositions are in the review record.

## Known gap, filed not fixed

`agentive doctor --against-preset` still ignores `evaluators:`, so a
preset/record divergence is invisible on the surface built to report
divergence. Filed as **KIT-0119** (`.kit/tasks/1-backlog/`).

`--bots` has the same empty-value hole that CodeRabbit found in
`--evaluators` (`--bots=` skips validation). Deliberately not changed
here — it is pinned by many tests and KIT-0108 owns collapsing this
engine's duplication — but it is real and now recorded.

## After merge — needs an operator decision

The release is **not** done by merging. Post-merge:

1. Tag `agentive-kit-v0.4.0` on green main → triggers
   `.github/workflows/publish-agentive-kit.yml` (OIDC trusted
   publishing; guards tag == `__version__`).
2. Verify the run goes green and PyPI serves 0.4.0.
3. Clean-env smoke: `uv tool install agentive-kit` → `agentive version`
   → `0.4.0`, and `agentive new --help` exists. **The workflow's own
   smoke test only runs `agentive version`**, so the door-presence check
   — the entire point of #144 — is a manual step.

**PyPI accepts each version exactly once.** The tag goes up only after
main is green, and only on your say-so.
