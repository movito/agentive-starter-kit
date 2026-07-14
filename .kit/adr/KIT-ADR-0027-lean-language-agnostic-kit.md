# KIT-ADR-0027: A Leaner, Language-Agnostic Kit — Simplification and Setup Proposals

**Status**: Accepted (2026-07-14, operator)
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
structural, not social; back-compat is preserved. The shims' removal is
not left to memory: the PR that creates them also files the removal
task, pinned to the next minor release (round-2 evaluation finding —
an unenforced "one release later" is how six doors became six).

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

### P7 — Operator presets: the one-button layer *(added 2026-07-14 after operator review)*

P5's degraded modes are the **floor** for unknown adopters. The kit's
primary operator wants the **ceiling** every time — BugBot + CodeRabbit,
the full evaluator library, the complete agent set including the Fable-5
variants, Linear sync. Hard-coding that ceiling into the kit would
re-create the identity leak ADR-0025 eliminated, just in the opposite
direction (operator specifics inside a distributable kit). So the
ceiling becomes a **preset**: operator-owned data layered over the same
mechanism, never new mechanism.

- **A preset is a pre-answered questionnaire.** It may supply default
  answers for exactly the inputs the one door (P3) asks — shape,
  profile, bots-present declaration, evaluator install, plugin
  channel/pin, Linear on/off, agent set, model-pin policy — and nothing
  else. If bootstrap doesn't ask it, a preset cannot set it. This keeps
  the preset from becoming a shadow config system.
- **It lives outside every repo**: `~/.config/agentive-kit/preset`
  (plus an optional `env.source` secrets file, `chmod 600`, *referenced*
  by the preset, never embedded in it). Presets are never committed to
  any repo and never travel on any sync channel; the kit ships only a
  commented example.
- **Resolution order follows the git-config precedent**: CLI flags >
  preset > kit-neutral defaults, with interactive prompts only for
  questions nothing answered. A stranger with no preset gets the P5
  floor and the wizard; the operator with a preset gets
  `bootstrap --new <name>` as a genuine one-button "new project with my
  usual prefs".
- **The project records resolved choices, not the preset.** The
  KIT-LOCAL region from P3 captures what was actually chosen; the
  preset is never consulted again after creation. Projects stay
  self-describing, and a project deliberately created leaner than the
  preset is not "wrong". Doctor (P4) validates the project's record;
  an optional `doctor --against-preset` reports divergence as
  information, never failure.
- **Bot enablement note**: installing CodeRabbit and BugBot **org-wide
  ("all repositories")** makes bot coverage automatic for every new
  repo — the real one-button enabler for the bots' half. Documented as
  a preset-setup step, not automated (GitHub App installation is an
  operator-auth surface the kit should not drive).

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

**P4 → P2 → P1 → P3 → P5+P7 → P6.** Doctor first (immediate value, zero
design risk, evidence already tabulated). Planning profile second (the
strategic split win; unblocks adopting the kit for non-Python products
immediately, before P1 lands). Language profiles third. One door fourth
(it needs P1/P2's shapes to exist). Floor and ceiling land together
fifth — P5 (degraded modes) and P7 (operator presets) are the same
resolution mechanism read from opposite ends, and P7 is only a preset
file plus the door honoring it. The prune is continuous background.

## Rollout & Downstream Compatibility *(added 2026-07-14, operator review)*

**The kit stays usable at every stage.** Consumers are pinned (semver
plugin pin, manifest `core_version`) and the push channel is parked —
mid-transformation states cannot reach a downstream repo uninvited;
consumers move only by pulling (`project sync --ref <tag>`) or bumping a
pin. Each stage additionally ships a behavior-preserving default:

| After | Downstream effect | New capability |
|---|---|---|
| P4 | `doctor` arrives via normal core-scripts sync | env-drift detection everywhere |
| P2 | none (new shapes affect new installs only) | **planning repos for non-Python products — earliest new-capability point** |
| P1 | Python profile seeded as the hook = current `ci-check.sh` behavior; functional no-op | non-Python profiles |
| P3 | old doors keep working as shims | the one door |
| P5+P7 | none (no bots-declaration ⇒ today's "bots expected" behavior; presets are operator-side) | floor + ceiling |
| P6 | skills merge — the only real consumer-facing move; gated on inventory + read-both cycle | — |

**Migration paths** reuse existing vehicles: kit-family repos pull via
the manifest channel per release tag; plugin consumers migrate via the
**upgrader agent** (KIT-0032), whose runbook gains a post-upgrade
`doctor` step; re-shaping an existing product into planning+target is
opt-in via a fresh planning repo, never forced.

**Migrate downstream at two checkpoints, not per stage**: `doctor`
everywhere after P4 (cheap, catches consumer-side drift), then one
coordinated upgrader pass per repo after P3. The second checkpoint *is*
the deferred downstream-upgrade phase — the transformation completes in
the kit first, and each downstream repo migrates once.

## Consequences

**Positive**: adoption drops to one command + doctor; non-Python and
planning-only repos become first-class; the arc's incident class gets a
standing preventive check; no channel redesign — ADR-0022/0024/0026
boundaries are untouched. The floor/ceiling pairing (P5+P7) serves both
audiences from one mechanism: a stranger onboards with zero paid
services, the operator gets a one-button full-stack project — and the
kit itself stays neutral in both cases.

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

**Round 2 (post-P7 amendment)**: arch-review-fast REVISION_SUGGESTED —
one minor finding (shim-removal deadline must be enforced, not hoped
for), accepted into P3 as a filed-with-the-PR removal task. P7 itself
(operator presets) drew no findings. Zero evaluator working-tree
mutations, all four runs total.

## Revisit Triggers

- Third-party distribution of the kit (revives ADR-0025's enforcement
  question and hardens P1 profiles into contracts)
- A second operator
- A non-GitHub forge requirement
- Claude Code changing its per-path scoping model
