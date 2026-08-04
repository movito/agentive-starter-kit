# PLAY-0001: Repo bootstrap, Effekt integration and first git deploy - Implementation Handoff

**You are the feature-developer. Implement this task directly. Do not delegate or spawn other agents.**

**Date**: 2026-08-04
**From**: Claude (prototyping session, claude.ai)
**To**: feature-developer (Claude Code)
**Task**: `.kit/tasks/2-todo/PLAY-0001-repo-bootstrap-effekt-deploy.md`
**Status**: Ready for implementation
**Evaluation**: N/A (spec written directly from the prototyping session; see PROTOTYPE-BRIEF.md inside the source tree for the fuller project record)

---

## Task Summary

Put the Varv playground under version control, connect the existing Vercel
project to the repo, and ship the second simulator ("Effekt") through that
pipeline so `https://playground.varv.no/effekt/` is live. Then remove the one
piece of code duplication the prototyping session left behind (Effekt's copies
of the shared UI atoms).

## Current Situation

Two simulators exist in one Vite multi-page project:

1. **The phantom queue** (`/ev-queue-simulator/`) — EV charging as a queueing
   system. **Live in production.** Six iterations of history, none of it in git.
2. **Effekt** (`/effekt/`) — a fast-charging site as a power system: real EV
   models with charge curves, Norwegian grid-connection tiers, site battery
   containers, and a greedy-vs-protect dispatch policy. **Built, reviewed,
   browser-tested — not yet deployed.**

Everything so far was deployed by direct file upload to Vercel from a
prototyping conversation. There is no repository, and at least two sessions
have written into the same working tree (the Effekt implementation itself
appeared from a parallel session and was then code-reviewed and patched).
This task ends that mode of operation.

The authoritative source tree is **`varv-playground.zip`** (from the
prototyping session, 2026-08-04). It has been verified with a clean-room
build: unzip → `npm install` → `npm run build` → passes.

## Your Mission

- **Phase 1 — Repo bootstrap.** Initialise the repo from the zip contents
  (`git init`, single initial commit, e.g. `chore: import playground
  prototype (two simulators)`), push to the remote (`movito/varv-playground`
  or as the coordinator directs). In the Vercel dashboard, connect the
  existing project `playground` (team **IXDA**, project id
  `prj_PLACEHOLDER00000000000000000`) to the repo, production branch `main`,
  framework Vite (auto-detected previously).
- **Phase 2 — Reconcile and deploy.** If any other checkout or session has a
  divergent copy of these files, diff it against the zip and fold in only
  what survives review (see Critical Details §4). Push; confirm Vercel builds
  from git; verify both routes live.
- **Phase 3 — shared-ui adoption.** `src/Effekt.jsx` currently defines its
  own `T`, `Slider`, `Stat`, `expRand` because it was written minutes before
  `src/shared-ui.jsx` was extracted. Make it import the shared atoms; keep
  its two extra colours (`mw: "#7A4FA3"`, `red: "#B0402A"`) in a local
  extension object (e.g. `const TX = { ...T, mw: …, red: … }`). Do **not**
  try to unify `CarTimeline` — Effekt's variant is deliberately simpler
  (windowed only, no fumbling segment); note it as future work instead.
- **Phase 4 — Hygiene.** Update README if any commands changed; confirm the
  meta.json failure modes still fail the build; close out task bookkeeping.

## Acceptance Criteria (Must Have)

As in the task starter, plus detail:

- "Renders correctly" for both routes means: page loads with no console
  errors, the Varv header/footer shell is present, and the simulation clock
  advances. A Playwright smoke check is welcome but not required by this
  task (formal tests are PLAY-0003).
- "Reviewed fixes survive" means, concretely: `PowerChart`/`SocChart`/
  `WaitChart` are wrapped in `memo` with comparators keyed on the `stamp`
  prop; `makeCar` clamps `goal` to ≥ 0.15 and `soc` to `goal - 0.05`; the
  chart-frame helper is named `chartFrame`, not `useChartFrame`.

## Critical Implementation Details

### 1. The meta.json contract is load-bearing

The build (`scripts/experiments.mjs`, called from `vite.config.js`) discovers
experiments by globbing top-level directories containing `index.html`, and
**fails the build** if any lacks a valid `meta.json` (`title`, `summary`,
ISO `added`, `status` ∈ live/draft/archived). The index page is generated
from the same discovery pass. Consequences for you:

- Never add a scratch directory with an `index.html` at the repo root.
- The Effekt entry already exists (`effekt/meta.json`, status `live`); pushing
  the tree is all that's needed for it to appear on the index.

### 2. The first push must be the full tree

The production alias `playground.varv.no` is attached to the Vercel project
and rolls to every new production deployment. If the first pushed commit is a
scaffold rather than the complete tree, the live site goes blank until the
next push. Commit the zip contents wholesale before connecting, or connect
and then push the complete tree as the first `main` commit.

### 3. Vercel specifics

- Team: IXDA (`team_PLACEHOLDER0000000000000`); project `playground`
  (`prj_PLACEHOLDER00000000000000000`).
- `playground.varv.no` is already attached to **this** project with a correct
  CNAME at one.com. Do not touch domain settings. Historical trap, in case
  something regresses: the parent `varv` project has a wildcard, and an
  unattached hostname falls through to it, silently serving the main Varv
  site. Exact-match assignment on this project is what prevents that.
- Build command `vite build`, output `dist/`, Node 24.x — all already set on
  the project; auto-detection handled it last time.
- No environment variables or secrets exist or are needed.

### 4. Reconciliation rules (parallel-session divergence)

If you find another copy of `Effekt.jsx` or the playground tree:

- The zip is the reviewed baseline. Diff *toward* it.
- Accept improvements only if they preserve: the memoized charts (see above),
  the dispatch accounting in the sim loop (energy balance: `battE +=
  (g2b − b2c)·dt/60`, greedy vs protect semantics, hysteresis on the protect
  threshold), and the module-scope placement of `Slider`/`Stat` (defining
  them inside the component remounts inputs every animation frame and breaks
  slider dragging — this bug has been fixed twice already; don't let it back).

### 5. What NOT to "fix" while you're in there

Known modelling simplifications that are deliberate for teaching and
documented in the UI: kVA ≈ kW on grid tiers, 100% battery round-trip
efficiency, the "containers to avoid curtailment" stat being first-order
(ignores battery power rating and refill competition), one car per charger,
no fumbling friction in Effekt. Leave them; they're candidates for later
tasks with the course owner's input, not drive-by corrections.

## Resources for Implementation

- `varv-playground.zip` — authoritative source tree (contains
  `PROTOTYPE-BRIEF.md` and `README.md` with the experiment-publishing
  convention).
- Skill: `varv-playground` (installed in the coordinator's Claude account)
  documents the publishing contract; the README in-repo carries the same.
- Live reference: `https://playground.varv.no/ev-queue-simulator/` (current
  production, pre-Effekt).
- PROTOTYPE-BRIEF.md "Decisions made and why" — read before refactoring
  anything; two decisions are reversals of approaches that looked cleaner
  and weren't.

## Time Estimate

3.5–5.5 h (breakdown in the task starter).

## Starting Point

```bash
unzip varv-playground.zip && cd varv-playground
npm install && npm run build          # expect: clean pass, 3 asset bundles
git init && git add -A && git commit -m "chore: import playground prototype (two simulators)"
# create remote, push, then: Vercel dashboard → playground → Settings → Git → connect
```

## Questions for Coordinator

Blockers to raise rather than resolve unilaterally: remote repo name/owner if
not `movito/varv-playground`; anything requiring Vercel dashboard actions the
agent cannot perform (the git connection itself is dashboard-side and may need
the coordinator's hands); any divergent tree whose changes are substantive
enough that "diff toward the zip" would discard real work.

## Success Looks Like

`git log` shows the import commit plus your changes; the Vercel deployment
list shows the newest production deployment with a commit SHA; the playground
index lists two experiments; `playground.varv.no/effekt/` renders the Effekt
simulator with the Varv shell; `grep -rn "const Slider" src/` returns exactly
one definition; and nobody ever runs a file-upload deploy against this
project again.

## Notes

- Follow-ups seeded, not started here: PLAY-0002 (CI: build on PR),
  PLAY-0003 (tests for the metadata contract + Playwright smoke),
  PLAY-0004 (Effekt model refinements: effective-ρ, queue-length-dependent
  balking, session CSV export — see brief and Effekt's known-issues note).
- The phantom queue's own open issues (utilisation ρ uses offered load;
  aligned-sort shuffle) are catalogued in PROTOTYPE-BRIEF.md "Known issues"
  and are not part of this task.

---

**Task File**: `.kit/tasks/2-todo/PLAY-0001-repo-bootstrap-effekt-deploy.md`
**Evaluation Log**: N/A
**Handoff Date**: 2026-08-04
**Coordinator**: Claude (claude.ai prototyping session), on behalf of Fredrik
