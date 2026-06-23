#  Mistral Arch

**Source**: .adversarial/inputs/KIT-ADR-0025-arch-input.md
**Evaluator**: mistral-arch
**Model**: mistral/mistral-large-2512
**Generated**: 2026-06-23 07:52 UTC

---

## Architectural Analysis

### Architecture Summary
This ADR proposes a structural solution to decouple plugin-distributed agent workflows (owned by the plugin) from project-specific localization (owned by individual projects). The core idea is to introduce a runtime context file (`.kit/PROJECT-CONTEXT.md`) that agents read early in their execution, allowing plugin upgrades without clobbering project specifics. The design addresses a critical tension between upgradability and localization in Claude Code's agent system, with a focus on minimal machinery and clear boundaries.

Overall, the structural quality is strong: the solution is well-scoped, respects runtime constraints, and introduces a clean separation of concerns. However, there are coupling and boundary risks that need attention before this pattern is widely adopted.

---

### Design Quality Assessment

| Dimension            | Rating          | Note |
|----------------------|-----------------|------|
| Responsibility       | Clear           | The ADR cleanly separates plugin-owned workflows from project-owned context, with a narrow escape hatch for frontmatter. |
| Coupling             | Moderate        | Introduces a new coupling point (`.kit/PROJECT-CONTEXT.md`) that agents must read, creating a convention-dependent interface. |
| Cohesion             | High            | The runtime context file has a singular purpose (agent-specific depth), and the escape hatch is narrowly scoped. |
| API surface          | Clean           | The schema for `.kit/PROJECT-CONTEXT.md` is well-defined, and the escape hatch is explicitly documented as an exception. |
| Pattern consistency  | Consistent      | Aligns with existing patterns (e.g., `CLAUDE.md` injection, `.kit/` conventions) and avoids introducing new machinery. |
| Growth readiness     | Needs attention | The convention-based interface and overlap with `CLAUDE.md` may degrade under scale without enforcement mechanisms. |

---

### Architectural Findings

**[COUPLING]: Convention-Dependent Interface Without Enforcement**
- **Location**: Runtime context file mechanism (`.kit/PROJECT-CONTEXT.md`)
- **Issue**: The solution relies on agents *voluntarily* reading the context file as an early step. This is a convention, not an enforced contract, and there is no mechanism to validate that agents comply (unlike the `## Target Repository` check in KIT-ADR-0024 §2). Over time, this could lead to drift if agents skip the read step or misinterpret the schema.
- **Impact**:
  - Short-term: Agents may fail to localize correctly if the convention is not followed.
  - Long-term: The system accumulates "implicit contracts" (like the undocumented task spec/CLAUDE.md reliance in `feature-developer-v6`), making it harder to reason about agent behavior.
- **Recommendation**:
  - Introduce a **preflight check** (e.g., a lint rule or plugin validation step) that verifies:
    1. The context file exists when a project enables a plugin agent.
    2. The agent’s workflow includes a "Phase 0" step to read the file (e.g., via static analysis of the agent’s Markdown or a required `## Phase 0: Load Project Context` section).
  - Add a **runtime warning** if the context file is missing or malformed, logged to the agent’s output for observability.

---

**[BOUNDARY]: Overlap Between `CLAUDE.md` and `.kit/PROJECT-CONTEXT.md`**
- **Location**: Schema design for `.kit/PROJECT-CONTEXT.md`
- **Issue**: The ADR proposes splitting high-level context (topology, project rules) into `CLAUDE.md` and agent-specific depth into `.kit/PROJECT-CONTEXT.md`. However, the boundary is fuzzy:
  - `CLAUDE.md` is already injected into every session, so duplicating topology/layout there *and* in the context file is redundant.
  - The "agent-specific depth" (e.g., stack-specific footguns) may overlap with defensive-coding patterns in `.kit/context/patterns.yml`.
- **Impact**:
  - Projects may struggle to decide where to put information, leading to duplication or inconsistency.
  - Agents may read conflicting data from the two sources, especially if `CLAUDE.md` is updated but the context file is not.
- **Recommendation**:
  - **Clarify the boundary explicitly**:
    - `CLAUDE.md`: *Validated* high-level context (topology, project rules, target repository). This is the source of truth for the project’s identity and must be kept in sync with reality (e.g., via the KIT-ADR-0024 §2 check).
    - `.kit/PROJECT-CONTEXT.md`: *Agent-specific* depth (stack notes, local test commands, Serena project name). This is *not* validated and is only read by agents that need it.
    - `.kit/context/patterns.yml`: *Defensive-coding* patterns (e.g., "never merge without a test plan"). This is read by *all* agents and is not agent-specific.
  - **Deprecate topology/layout in `.kit/PROJECT-CONTEXT.md`**: Since `CLAUDE.md` is already injected, agents should read topology from there and only use the context file for agent-specific details. This avoids duplication and ensures consistency.

---

**[RISK]: Escape Hatch Could Reintroduce Drift**
- **Location**: Frontmatter escape hatch (thin local agent override)
- **Issue**: The escape hatch allows projects to override an agent’s frontmatter (e.g., model pin) by creating a local agent that defers to the plugin workflow. While this is scoped as an exception, it:
  - Reintroduces a local copy of the agent (even if thin), which could diverge over time.
  - Creates a maintenance burden for projects that use it (they must manually re-sync the local agent on upgrades).
- **Impact**:
  - Projects may overuse the escape hatch for minor customizations, leading to drift.
  - The "thin" local agent could grow over time, defeating the purpose of plugin distribution.
- **Recommendation**:
  - **Narrow the escape hatch further**:
    - Restrict it to *only* frontmatter overrides (e.g., `model`, `disallowedTools`). Do not allow workflow or behavior changes.
    - Require the local agent to include a `## Provenance` section explicitly stating that it is an override and must be re-synced on upgrades.
  - **Add a warning to the escape hatch**:
    - Include a comment in the generated local agent: `# WARNING: This agent overrides frontmatter and will not auto-upgrade. Re-sync with the plugin after upgrades.`
    - Add a preflight check that flags local agents using the escape hatch, reminding projects to re-sync.

---

**[PATTERN]: Schema Stability Risk**
- **Location**: `.kit/PROJECT-CONTEXT.md` schema
- **Issue**: The schema for the context file is defined in prose (tech stack, task prefix, etc.), but there is no machine-readable schema or versioning. If the schema changes (e.g., new fields are added), agents may break or misinterpret the file.
- **Impact**:
  - Schema changes could require updates to all agents that read the file, creating a coordination problem.
  - Projects may write malformed context files, leading to silent failures or incorrect agent behavior.
- **Recommendation**:
  - **Add a lightweight schema**:
    - Define the schema in a machine-readable format (e.g., JSON Schema or a YAML template) and ship it with the plugin.
    - Include a `version` field in the context file to allow backward-compatible changes.
  - **Add validation**:
    - Include a `kit validate-context` command that checks the context file against the schema.
    - Add a preflight check that runs this validation when a project enables a plugin agent.

---

### Positive Architecture Decisions
1. **Runtime Context File**: The decision to use a runtime context file (Option A) is well-justified. It avoids codegen, keeps the distributed agent body project-agnostic, and aligns with existing patterns (e.g., `CLAUDE.md` injection).
2. **Narrow Escape Hatch**: The escape hatch for frontmatter is scoped as an exception, not the default, which preserves the benefits of plugin distribution for the common case.
3. **Deduplication with `CLAUDE.md`**: The decision to keep high-level context in `CLAUDE.md` (already injected) and agent-specific depth in `.kit/PROJECT-CONTEXT.md` avoids redundancy and leverages existing infrastructure.

---

### Growth Risk Assessment
- **Low risk**:
  - The runtime context file mechanism scales well for behavioral localization (95% of the problem).
  - The escape hatch is narrowly scoped and unlikely to grow in usage.
- **Medium risk**:
  - The convention-based interface (agents must read the context file) may degrade without enforcement mechanisms.
  - Schema changes to `.kit/PROJECT-CONTEXT.md` could require updates to all agents.
- **High risk**:
  - Overlap between `CLAUDE.md` and `.kit/PROJECT-CONTEXT.md` could lead to confusion or inconsistency if the boundary is not strictly enforced.
  - The escape hatch could be overused, reintroducing drift for frontmatter overrides.

---

### Verdict
**Verdict**: REVISION_SUGGESTED

The ADR proposes a sound structural solution to a critical problem, but the coupling, boundary, and risk findings should be addressed before widespread adoption. The revisions are minor but necessary to prevent drift and ensure long-term maintainability. Key actions:
1. Add enforcement mechanisms for the convention-based interface (preflight checks, runtime warnings).
2. Clarify and enforce the boundary between `CLAUDE.md` and `.kit/PROJECT-CONTEXT.md`.
3. Narrow the escape hatch further and add warnings to prevent misuse.
4. Add a machine-readable schema and validation for the context file.
