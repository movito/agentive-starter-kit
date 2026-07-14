# KIT-ADR-0027: A Leaner, Language-Agnostic Kit — Simplification and Setup Proposals

**Status**: Proposed
**Date**: 2026-07-14
**Deciders**: operator + planner-f5
**Evidence base**: the v0.8.0 stabilization arc (PRs #69–#76) and its
incident log; repo inventory 2026-07-14.

## Context

The kit serves two audiences with one codebase: developing the kit
itself (ASK), and being adopted by other projects/agents. Three tensions
have accumulated:

**1. The kit conflates its own machinery with the project's toolchain.**
The kit's machinery is Python (`project`, `sync_from_manifest.py`,
`kit_markers.py`, `pattern_lint.py`) — that is an implementation detail.
But the kit also *imposes* a Python project toolchain on every adopter:
`ci-check.sh` carries 26 references to black/isort/flake8/pytest;
`verify-setup.sh` checks Python/venv/pytest as essential while marking
`gh` — the actual backbone of the bot/CI loop — "optional";
pre-commit runs a Python gauntlet; the coverage gate assumes pytest. A
JavaScript or Go product adopting the kit inherits a foreign toolchain
it must rip out by hand. Meanwhile the kit's own `pyproject.toml` still
says `name = "your-project-name"  # TODO` — the template/product
identity is blurred even at home.

**2. Setup truth drifts silently, and drift was our dominant failure
mode.** The v0.8.0 arc was effectively an assumption audit. Every major
incident was an undetected environment assumption, not a code bug:

| Incident | Assumption that failed |
|---|---|
| Phantom Black failure (KIT-0032) | venv matches pyproject pin |
| Evaluator mutated working tree (KIT-0044) | venv adversarial-workflow matches system (was aider-era 0.9.7) |
| 22/22 sync-workflow failures over 4 months | `CROSS_REPO_TOKEN` exists |
| Non-TTY evaluator runs died on a prompt | `ADVERSARIAL_UNATTENDED` exists (it never did) |
| Evaluator CLI "invalid choice" in worktree | `.adversarial/evaluators/` provisioned |
| Evaluator trio ran 2-of-3 (KIT-0032) | `ANTHROPIC_API_KEY` uncommented |
| CodeRabbit "internal error" ×3 rounds | prepaid credits exist |

**3. Artifact homes and setup doors have multiplied.** Skills live in
three homes (`.claude/skills/`, `.kit/skills/`, the plugin); commands in
two; agents in two. Setup has six doors: `create-project.sh` (new
project), `bootstrap-consumer.sh` (existing project), the onboarding
agent, plugin install, `install-evaluators`, and manifest sync. Each
door is individually documented; collectively they are the hardest part
of adoption — a fresh agent must discover which door it is standing in
front of.

**The split question.** Split mode (planning repo + target repo) exists
today as agent behavior — topology detection via `## Target Repository`
in CLAUDE.md, `git -C` routing, branch-isolation rules — and it works
(ID2 ran on it). But the *installation* is not split-aware: a
planning-only repo still receives the full Python scaffold (pyproject,
tests/, pre-commit gauntlet, coverage gate) that has nothing to
coordinate-only work. The target repo is correctly untouched; the
planning repo is over-provisioned.

## Decision Drivers

- Single operator, several projects; a new project or agent should
  onboard in minutes, not sessions.
- **KIT-ADR-0025's philosophy binds**: convention + runtime-read beats
  schema/enforcement machinery at this scale. Proposals must not
  reintroduce what that ADR declined.
- Channel boundaries stay meaningful (ADR-0022 manifest, ADR-0024
  topology, ADR-0026 pull sync).
- Prefer proposals that *retire* assumptions over ones that add
  configuration.

## Proposals

### P1 — Separate kit machinery from project toolchain (language profiles)

Keep the kit's machinery Python — invisible plumbing, stdlib-leaning,
runs on system `python3`. Make the *project* toolchain a replaceable
profile: `ci-check.sh` and `verify-setup.sh` become thin dispatchers
that execute a project-owned hook (`scripts/local/checks.sh`), and the
kit ships the current Python gauntlet as the default drop-in for that
hook. A JS project replaces one file (`npm test; npm run lint`); a
docs-only or planning repo uses a no-op profile. CLAUDE.md's "Project
Rules" section becomes a KIT-LOCAL region seeded by the chosen profile.
No schema, no config file — the hook IS the interface, consistent with
ADR-0025. Preflight needs nothing: it is already shell + `gh` and
language-agnostic.

**Hook micro-contract** *(added after evaluation — two reviewers
independently flagged the unstated interface)*: the hook accepts
`--mode ci|local`, exits `0` (pass) or `1` (fail) only, writes
human-readable diagnostics to stdout, and may rely on being invoked
from the repo root with no other environment guarantees. The dispatcher
passes nothing else through. Bootstrap templates this contract as a
comment header in the seeded hook. One paragraph, not a schema — the
Python default profile is the reference implementation, by statement
rather than by imitation.

### P2 — A first-class planning-repo profile (the split, done properly)

Recognize three installation shapes instead of one:

| Shape | Gets installed | Toolchain |
|---|---|---|
| **single** (code + planning together) | full kit | language profile (P1) |
| **planning** (coordinates a target repo) | `.kit/`, agents, commands, lifecycle + preflight/gh scripts | none (no pyproject, no tests/, no venv, no pre-commit gauntlet) |
| **target** (the product repo) | **nothing** | its own, untouched |

The planning profile is the direct answer to "can we do a better job of
the split": the planning repo carries coordination artifacts only, and
the kit never imposes its toolchain on the product repo — agents reach
it via the existing `git -C` cross-repo pattern. Machinery scripts the
planning profile needs (`project`, `preflight-check.sh`,
`kit_markers.py`) already run stdlib-only or shell+gh. This absorbs
KIT-0027 (first-class cross-repo support) as its configuration half.

### P3 — One setup door

Keep the six mechanisms; consolidate the *entrances* into one:
`bootstrap` (or `kit init`) with `--shape single|planning` and
`--profile python|js|none`, which orchestrates the existing pieces
(export or rsync, plugin pin, evaluator install offer, doctor run —
P4). A fresh agent given a repo and one command can no longer pick the
wrong entrance.

**Shape × profile legality** *(added after evaluation — all three
reviewers flagged the undefined dependency between the axes)*:

| | `python` | `js`/other | `none` |
|---|---|---|---|
| **single** | ✔ (default) | ✔ | ✔ (docs-only repos) |
| **planning** | ✘ | ✘ | ✔ (forced — the only legal pair) |
| **target** | — | — | — (never installed to) |

`bootstrap` is the **single owner** of this matrix: it validates,
forces `planning→none`, and records the chosen pair as one line in a
KIT-LOCAL region of CLAUDE.md (runtime-read, per ADR-0025 — no
`install.toml`). Doctor and any future reader *read that record*; they
never re-derive the matrix.

**Old doors become shims, not deprecation notes** *(revised after
evaluation — documentation-only deprecation contradicts this ADR's own
drift thesis, the strongest finding of the review)*: on the same PR
that lands the new door, the six existing entrances become thin
`exec`-into-`bootstrap` shims with the equivalent flags. Convergence is
structural, not social; back-compat is preserved; the shims are
deletable one release later.

### P4 — `project doctor`: the incident table as a setup verifier

Generalize `verify-setup.sh` into a profile-aware `project doctor`
where every check maps to a documented incident (table above): `gh`
auth first (it is the backbone, not optional); `.env` keys present and
uncommented; evaluator library installed and **venv-vs-system version
skew** (would have caught both stale-venv incidents); plugin pin vs
marketplace source; push-sync secrets *only if* that channel is
enabled; `core.bare` canary. Doctor runs at onboarding and is cheap
enough for a planner session-start triage. This is the highest
value-per-line proposal: it converts the arc's whole incident class
from reactive debugging into a preventive check.

Two refinements from evaluation: **(a)** checks live as small
composable files in `scripts/core/doctor.d/`, included per
shape/profile, so the doctor stays cohesive as checks accumulate;
**(b)** a lifecycle rule keeps the incident mapping alive — closing any
retro/post-mortem requires either a new doctor check, an explicit
"not-checkable" note, or a triage-guide entry. Without (b), doctor
decays into a snapshot of 2026-07-14.

### P5 — Degraded modes for paid/external services

New adopters should not need CodeRabbit + BugBot + three model-provider
keys on day one. Preflight Gates 2/3 report **SKIP-with-notice** (not
FAIL) when a bot is declared absent; the evaluation gate degrades to
self-review + single-model review when only one API key exists. The
gates stay honest by naming the mode in their output — degraded, never
silently green (the same loud-not-silent principle the gates already
follow). The declaration lives in the **same named KIT-LOCAL region P3
records shape/profile in**, parsed via `kit_markers.py` — one region,
one reader library, no ad-hoc regex over CLAUDE.md (evaluation finding:
multiple readers grepping free text is the fragile pattern kit_markers
exists to prevent).

### P6 — One canonical home per artifact type, plus a prune

Declare canonical homes and converge: agents → `.claude/agents/`
(plugin = distribution copy); commands → `.claude/commands/` (plugin =
distribution); skills → **one** repo home (merge `.claude/skills/` and
`.kit/skills/`; the builder/implementation distinction has not paid its
rent — both are consumed the same way). The merge is gated on a
consumer-impact inventory (which pinned plugin versions and downstream
repos reference the old paths) and ships with a read-both-paths
deprecation cycle for one release — never a hard move (evaluation
finding). Prune the identity blur: fix the kit's own pyproject name,
sweep `__pycache__`/egg-info artifacts, and audit `scripts/optional/`
for strays. Small, mostly mechanical PR.

## Recommended sequence

**P4 → P2 → P1 → P3 → P5 → P6.** Doctor first (immediate value, zero
design risk, evidence already tabulated). Planning profile second (the
strategic split win; unblocks adopting the kit for non-Python products
immediately, before P1 lands). Language profiles third. One door fourth
(it needs P1/P2's shapes to exist). Degraded modes fifth. The prune is
continuous background.

## Consequences

**Positive**: adoption drops to one command + doctor; non-Python and
planning-only repos become first-class; the arc's incident class gets a
standing preventive check; no channel redesign — ADR-0022/0024/0026
boundaries are untouched.

**Negative / risks**: "shape" and "profile" are two new concepts to
document (mitigation: the one door asks two questions and picks for
you). P1's hook risks profile divergence (mitigation: the Python
profile remains the kit's own tested default — ASK dogfoods it). P3
becomes a seventh door if the old six don't converge (mitigation: docs
reference only the new door from day one; old doors get deprecation
notes, not removal).

**Explicitly not proposed**: schema/validation machinery for
localization (ADR-0025 stands); bare-hub topology (declined in
WORKTREE-WORKFLOW.md); multi-tenant control systems; non-GitHub forge
support — including a `forge.sh` abstraction layer over `gh`
(evaluation suggestion, declined: for a single-operator, GitHub-only
reality an adapter layer is speculative generality; the dependency is
consciously accepted and the forge question stays a revisit trigger,
not a pre-built seam).

## Open Questions

- Should the planning profile ship the adversarial evaluators at all,
  or treat evaluation as a single-repo-only concern? (Planner runs
  spec evaluations today — suggests yes, but via P5's degraded mode.)

## Evaluation Record (2026-07-14)

Reviewed pre-acceptance by three provider families via adversarial-
workflow 1.0.1 (logs:
`.adversarial/logs/KIT-ADR-0027-lean-language-agnostic-kit--{arch-review-fast,claude-arch,arch-review}.md`).
All three: REVISION_SUGGESTED, design judged sound. Convergent findings
**accepted and folded in**: shape×profile legality matrix with a single
owner; hook micro-contract; old doors become exec shims (doc-only
deprecation contradicted this ADR's own drift thesis); `doctor.d/`
composability + incident-closure lifecycle rule; named KIT-LOCAL region
via `kit_markers.py` for P5; skills-merge back-compat cycle.
**Declined with reasoning**: `install.toml` contract file (KIT-LOCAL
record instead, per ADR-0025); `forge.sh` abstraction (above).

## Revisit Triggers

- Third-party distribution of the kit (revives ADR-0025's enforcement
  question and hardens P1 profiles into contracts)
- A second operator
- A non-GitHub forge requirement
- Claude Code changing its per-path scoping model
