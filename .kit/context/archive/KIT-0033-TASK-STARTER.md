# Task Assignment: KIT-0033 — Make planner + feature-developer truly portable downstream

**Task File**: `.kit/tasks/1-backlog/KIT-0033-portable-agents-downstream.md`
**Handoff File**: *(none yet — task spec is self-contained; create
`.kit/context/KIT-0033-HANDOFF-feature-developer.md` only if you discover
clarifications worth capturing before implementing)*

### Overview

PR #57 consolidated planner and feature-developer agents into single canonical
V2 files and opted into shipping both downstream via `bootstrap-consumer.sh`.
Four separate bot review threads flagged that the downstream story is
under-scaffolded: `feature-developer.md` hardcodes ASK identity that consumers
would inherit, `planner.md` references `.kit/` infrastructure consumers do not
receive, and rsync's `--ignore-existing` means re-bootstrapping a consumer
cannot refresh the canonical agent file without clobbering local customizations.

Your mission: implement the marker-based overwrite mechanism (N2) and `.kit/`
skeleton provisioning (F1) so that a fresh consumer bootstrap, an opt-out
bootstrap, and a re-bootstrap of an existing consumer all behave correctly,
and all four PR #57 bot threads can be marked resolved.

### Acceptance Criteria (Must Have)

- [ ] **`.kit/` skeleton (F1)**: `bootstrap-consumer.sh` provisions
  `tasks/<status-folders>/`, `context/`, `templates/TASK-STARTER-TEMPLATE.md`,
  and a working `./scripts/core/project` in consumer repos
- [ ] **Marker-based overwrite (F2 + N2)**: `Project Context` and `Stack Notes`
  sections in the canonical agents wrapped in stable markers (e.g.,
  `<!-- BEGIN KIT-LOCAL --> ... <!-- END KIT-LOCAL -->`); bootstrap replaces
  marker content with consumer-derived values
- [ ] **F3 opt-out**: bootstrap with an explicit opt-out flag/answer yields
  no `.kit/` directory, no shipped planner/feature-developer, and a clean
  one-line summary of what was skipped
- [ ] **F4 re-bootstrap refresh**: re-running `bootstrap-consumer.sh` against
  an existing consumer picks up upstream changes outside marker regions but
  preserves consumer customization inside **both** marker regions
- [ ] **Lifecycle verification**: `./scripts/core/project start <ID>` AND
  `./scripts/core/project complete <ID>` work end-to-end in the consumer
  against a stub task
- [ ] **N1 no-regression**: ASK's own copies of the agents still load and work
  for kit development; the marker additions are the only ASK-visible change
- [ ] **PR #57 threads resolvable**: the four bot threads (see task spec
  Overview for IDs) reference behavior this task delivers

### Success Metrics

**Quantitative**:
- 0 references to ASK-specific identity (KIT-NNNN, kit-only paths) reach a
  freshly-bootstrapped consumer's agent files
- 100% preservation of inside-marker content across a re-bootstrap cycle
  (verified by byte-equality on a `diff` test)
- 1 bootstrap path covers all three modes (fresh / re-bootstrap / opt-out)

**Qualitative**:
- Marker scheme survives future agent edits — adding a new phase to
  `planner.md` upstream does not break a consumer's existing customization
- Opt-out path is obviously documented in bootstrap output, not silent
- Pre-commit + CI on ASK stays green after marker additions

### Time Estimate

**4–8 hours total**:
- Phase 1 — Marker scheme + agent file edits: 1–2 hours
- Phase 2 — `.kit/` skeleton provisioning in bootstrap-consumer.sh: 1–2 hours
- Phase 3 — Marker-replacement logic (sed/awk or small Python helper): 1–2 hours
- Phase 4 — Opt-out flow + end-to-end test against a scratch consumer: 1–2 hours

### Notes

- **Three design approaches** are documented in the task spec (markers,
  source-of-truth indirection, template/local split). Spec leans toward
  markers — confirm or pivot in the handoff before implementing.
- **Bot-review provenance**: this task absorbed insights from four PR #57
  threads (commits `f231b35`, `a990355`, `13038b3`). The task spec's
  Overview links them; the strengthened ACs (F3 opt-out check, re-bootstrap
  covers Stack Notes) came directly from those rounds.
- **Coordinate with KIT-0026** if cross-repo agent/skill sync changes
  overlap (different mechanism — that one targets peer kit repos, this one
  targets consumer projects bootstrapped from ASK).
- **Out of scope**: changing the canonical agents' workflow phases or
  adding new functional features; this task is purely about the
  downstream-portability mechanism.

**⚠️ FIRST ACTIONS** (in order):
1. `git checkout -b feature/KIT-0033-portable-agents-downstream`
2. `./scripts/core/project start KIT-0033`
3. Re-read `.kit/tasks/1-backlog/KIT-0033-portable-agents-downstream.md`
   (full spec — F1 has concrete path requirements, N2 explains why markers
   are necessary not preferred)
4. Read the four bot threads on PR #57 for source context — they are linked
   from the task spec Overview

---

**Recommended agent**: `feature-developer` (the V2 canonical) — the task
touches `bootstrap-consumer.sh`, agent definitions, and onboarding flow,
all of which are exactly the surface area this agent owns.
