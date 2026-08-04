# Task Starter: PLAY-0001

## Task Assignment: PLAY-0001 - Repo bootstrap, Effekt integration and first git deploy

**Task File**: `.kit/tasks/2-todo/PLAY-0001-repo-bootstrap-effekt-deploy.md`
**Handoff File**: `.kit/context/PLAY-0001-HANDOFF-feature-developer.md`

### Overview

The Varv playground (playground.varv.no) runs two simulators, but only one is live and neither is under version control — the production site has been deployed by direct file upload from a prototyping session, and at least two uncoordinated sessions have written into the same project. The complete, reviewed source tree exists as `varv-playground.zip` (clean-room build verified).

Your mission: make the git repository the single source of truth and single deploy path for playground.varv.no, and ship the second simulator (Effekt, at `/effekt/`) through it.

### Acceptance Criteria (Must Have)

- [ ] **Repo**: `varv-playground.zip` contents committed as the initial history; `npm run build` passes from a fresh clone
- [ ] **Vercel**: project `playground` (IXDA team) connected to the repo; a push to `main` produces a production deployment; file-upload deploys retired
- [ ] **No blank-site window**: the first pushed commit contains the full tree, so the production alias never serves an empty or partial site
- [ ] **Effekt live**: `https://playground.varv.no/effekt/` returns 200, renders, and appears on the playground index (derived from its `meta.json`)
- [ ] **Regression**: `/ev-queue-simulator/` still renders correctly after the shared-ui extraction included in the zip
- [ ] **Reconciliation**: any Effekt/playground files from the parallel session are diffed against the zip before push; the reviewed fixes (chart memoization, makeCar guard) survive
- [ ] **Cleanup**: `Effekt.jsx` imports `Slider`/`Stat`/`expRand` from `src/shared-ui.jsx` instead of duplicating them (extend `T` locally for its two extra colours)

### Success Metrics

**Quantitative**:
- Experiments listed on index: 2 (baseline: 1)
- Production deploys via git: 100% from this task onward (baseline: 0%)
- Clean-clone build: passes (baseline: no clone exists)
- Effekt bundle size: within ±10% of 25.4 kB (guard against accidental dependency growth)

**Qualitative**:
- One deploy path (verified: Vercel dashboard shows source = git for the latest production deployment)
- No duplicated UI atoms between simulators (verified: grep for `const Slider` returns one definition)
- meta.json contract still enforced (verified: a scratch dir with index.html and no meta.json fails the build)

### Time Estimate

3.5–5.5 hours total:
- Phase 1 (repo bootstrap + Vercel git connect): 1–1.5 h
- Phase 2 (reconcile, deploy, verify live): 1–2 h
- Phase 3 (shared-ui adoption in Effekt): 1–1.5 h
- Phase 4 (docs touch-up, task hygiene): 0.5 h

### Notes

- Source of truth: `varv-playground.zip` from the prototyping session (includes `PROTOTYPE-BRIEF.md` inside the tree). The brief's next-steps 2–3 (CI build check, metadata-contract tests) are deliberately **out of scope** here — they become PLAY-0002/0003.
- The Vercel `playground` project already exists with `playground.varv.no` aliased to production (details in handoff). Do not create a new project; connect the existing one.
- A parallel session has previously written into the same working tree. Treat any divergent copies as PRs to review, not as truth.
- Coordinator note: this starter was written outside the kit checkout, so the worktree was NOT pre-created and `agent-handoffs.json` is NOT yet updated — run the helper below and update the assignment record before opening the session tab.

**⚠️ LAUNCH** (un-skippable — see `WORKTREE-WORKFLOW.md`):
Open the session tab with its working directory set to
`../playground-worktrees/PLAY-0001` — branch
`feature/PLAY-0001-repo-bootstrap-effekt-deploy`, created and provisioned via
`./scripts/local/new-worktree.sh PLAY-0001 repo-bootstrap-effekt-deploy`.
(If the helper derives a different branch name from the task filename, the
LAUNCH block must be corrected to match what it actually created.)
Do NOT run the session from the primary clone.

**⚠️ FIRST ACTIONS** (in order):
1. `git branch --show-current` (expect: `feature/PLAY-0001-repo-bootstrap-effekt-deploy`)
2. `./scripts/core/project start PLAY-0001` (move task to `3-in-progress/`)

---

**Recommended agent**: `feature-developer` (infrastructure + integration work; no TDD phase in this task — the test suite is PLAY-0003's job)
