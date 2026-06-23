#  Arch Review

**Source**: .adversarial/inputs/KIT-ADR-0025-arch-input.md
**Evaluator**: arch-review
**Model**: o3
**Generated**: 2026-06-23 07:51 UTC

---

### Architecture Summary
This ADR introduces a localization mechanism for plugin-distributed Claude Code agents.  It splits immutable, upgrade-worthy workflow logic (kept inside the plugin) from mutable, project-specific detail (moved to a project-owned `.kit/PROJECT-CONTEXT.md` that agents read at runtime).  The proposal is directionally sound: it removes merge pain, restores upgradeability, and keeps the distributed system-prompt small.  However, the solution relies on conventions that are not yet enforced, leaves ambiguity around file format and duplication with `CLAUDE.md`, and provides only a hand-wavy path for the rare front-matter override.

### Design Adherence

| Aspect                | Rating                     | Notes |
|-----------------------|----------------------------|-------|
| Concept independence  | Adequate                  | Clean separation of “workflow body” vs “project specifics”, but enforcement relies on human discipline. |
| API surface quality   | Adequate                  | Simple API (`PROJECT-CONTEXT.md` at well-known path) but schema is only sketched; no contract for validation or versioning. |
| Coupling              | Moderate                  | Agents are tightly coupled to a file path and schema; coupling to plugin release remains indirect. |
| Cohesion              | High                      | ADR focuses on one problem and one solution; escape hatch is the only out-of-scope concern. |
| Pattern consistency   | Minor deviations          | Follows plugin distribution pattern from KIT-ADR-0024/0030, but introduces a new “Phase 0 read” convention that the codebase does not uniformly have yet. |

### Architectural Findings

**[STRUCTURAL]: Blurry Boundary Between `CLAUDE.md` and `PROJECT-CONTEXT.md`**
- Location: §Decision 3 and “Neutral” notes
- Issue: High-level topology rules now live partly in `CLAUDE.md`, partly in the new file. Without a crisp ownership rule, information will drift or duplicate.
- Impact: Editors won’t know where to place new context, leading to split-brain configuration and tooling confusion.
- Recommendation: Publish an explicit ownership table (field → home) and enforce it in lints; consider collapsing to one file if overlap cannot be explained cleanly.

**[API]: Weakly-Typed Markdown Schema**
- Location: §Decision 2 (“tech stack; task-ID prefix …”)
- Issue: The contract is prose; Markdown is difficult to validate and evolve.
- Impact: Tools cannot statically check correctness; breaking changes may slip into CI late.
- Recommendation: Move to a machine-readable, versioned format (YAML or TOML) with JSON-schema validation; leave human-readable commentary in Markdown if desired.

**[COUPLING]: Convention-Only Enforcement of Phase 0 File Read**
- Location: §Consequences / Negative
- Issue: Agents must remember to read the context. Nothing forces future agents (or maintainers) to honour the convention.
- Impact: Silent mis-configuration; bugs identical to the hard-coded Serena example will creep back.
- Recommendation: Ship a small helper library (`kit_agent_context.load()`) and make the lint check mandatory in CI. That turns a convention into code.

**[PATTERN]: Escape-Hatch Front-Matter Override Re-introduces Drift**
- Location: §Decision 4
- Issue: Thin local copies become “special”; history shows they never get re-synced.
- Impact: The very drift this ADR addresses re-emerges for the subset of agents that need overrides, undermining uniformity.
- Recommendation: Time-box the escape hatch: require a tracking issue and schedule to migrate the override into a first-class, versioned field in the context schema.

**[STRUCTURAL]: Versioning Strategy Not Defined**
- Location: Missing in ADR
- Issue: How will future, incompatible schema changes roll out?
- Impact: Upgrades may break running agents if a field is renamed or semantics change.
- Recommendation: Add a mandatory `schemaVersion` field and a deprecation window policy.

### Positive Architecture Decisions
• Clear split between upgradeable workflow logic (plugin) and local variability (context).
• Keeps system-prompt payload minimal, aligning with KIT-ADR-0001.
• Option A avoids code-generation complexity while preserving upgrade simplicity.
• Provides a single mechanism for all shared agents, eliminating ad-hoc forks.

### Growth Risk Assessment
Low risk
• Plugin upgrade path: pin-bump still works.
• Runtime file read scales linearly with agent count.

Medium risk
• Schema evolution and versioning—currently unspecified.
• Context vs `CLAUDE.md` duplication—manageable now, messy at 3× complexity.

High risk
• Reliance on convention for Phase 0 read; lack of automated enforcement.
• Escape-hatch copies can proliferate and fragment upgrade story.

### Verdict
REVISION_SUGGESTED — The architectural direction is solid, but the ADR should be amended to (1) formalise file format and validation, (2) specify concrete enforcement tooling for the Phase 0 read, (3) clarify the boundary with `CLAUDE.md`, and (4) define a versioning/deprecation strategy. Addressing these early will avert configuration drift and upgrade friction as the ecosystem grows.
