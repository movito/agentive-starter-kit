#  Arch Review Fast V2

**Source**: .adversarial/inputs/KIT-ADR-0025-arch-input.md
**Evaluator**: arch-review-fast-v2
**Model**: gemini/gemini-3-flash-preview
**Generated**: 2026-06-23 07:50 UTC

---

This architectural review focuses on the proposed strategy for decoupling plugin-distributed agent workflows from project-specific localizations.

### Quick Assessment

| Dimension | Rating | One-Line Note |
|-----------|--------|---------------|
| Responsibility | Clear | Distinctly separates "Workflow Logic" from "Project Data." |
| Coupling | Low | Uses a "Configuration over Code" approach via a flat file. |
| Cohesion | High | Consolidates localization into a single, well-known project file. |
| API quality | Acceptable | Interface is a file schema; schema definition needs more rigor. |
| Pattern fit | Consistent | Extends the existing `CLAUDE.md` and plugin-manifest pattern. |
| Growth readiness | Ready | Supports upgrades without merging; scales to many projects. |

---

### Findings

**[COUPLING]: Implicit Contract via File I/O**
- **What**: Option A relies on agents being "disciplined" to perform a Phase 0 read of a specific file path (`.kit/PROJECT-CONTEXT.md`).
- **Why it matters**: Since Claude Code doesn't enforce a lifecycle, an agent could easily "forget" to read this file or fail silently if the path changes. This creates a brittle dependency on the agent's prose instructions rather than a system-level guarantee.
- **Suggestion**: Create a "Bootstrap" snippet (a standardized Markdown block) that must be included at the top of every distributed agent. Use a Linter/Pre-commit hook to verify that all agents in `.claude/agents/` contain the "Load Project Context" instruction.

**[COHESION]: The "Context Fragment" Problem**
- **What**: The ADR splits context across `CLAUDE.md` (injected), `.kit/PROJECT-CONTEXT.md` (read at runtime), and `task-specs` (runtime).
- **Why it matters**: Information fragmentation makes it harder for humans to know where to update a project rule. If a user updates the tech stack in `CLAUDE.md` but not in `PROJECT-CONTEXT.md`, the agent may receive conflicting instructions.
- **Suggestion**: Strictly define `CLAUDE.md` as "Static Identity" (who we are) and `PROJECT-CONTEXT.md` as "Operational Config" (how we run). Specifically, move all "Command" strings (test, lint, etc.) into a structured format (JSON/YAML) inside the context file to allow for future machine-validation.

**[API/STRUCTURE]: Machine-Parseable vs. Prose**
- **What**: The ADR leans toward a Markdown file for project context, but lists a "fixed schema."
- **Why it matters**: Agents are better at extracting data from structured formats (YAML/JSON) than variable Markdown headers, especially when those values need to be passed into shell commands (like test loops).
- **Suggestion**: Use `.kit/project-context.json` or `.yml`. This allows the "Kit" to provide a JSON Schema for validation, ensuring that a project hasn't missed a required field (like `serena_project_id`) before the agent even starts.

**[RISK]: The Frontmatter "Escape Hatch" is a Drift Trap**
- **What**: The proposal allows "thin" local agents to override frontmatter.
- **Why it matters**: This is the "Thin End of the Wedge." Users will eventually add "just one behavioral rule" to that thin file, and soon the project has a forked agent again.
- **Suggestion**: If frontmatter overrides are rare, consider if Option B (Render-on-pin) should actually be the *implementation detail* of Option A. The "Source of Truth" is the plugin + the local JSON config; the "Runtime Artifact" is a generated `.md` file. This solves the frontmatter issue without manual forks.

---

### What's Good
- **Separation of Lifecycles**: Correctly identifies that "How to Review Code" (workflow) changes at a different frequency than "What command runs tests" (localization).
- **No-Build-Step Bias**: Respecting the "edit-and-run" nature of Claude Code keeps the developer experience frictionless.
- **Dependency Inversion**: Instead of the plugin knowing about projects, the plugin defines an interface that projects must implement.

---

### Verdict

**REVISION_SUGGESTED**

The architecture is fundamentally sound, but the **"Context Fragment"** risk is high. To move to APPROVED, the ADR should:
1.  **Harden the Schema**: Prefer a structured data format (YAML/JSON) over Markdown for `.kit/PROJECT-CONTEXT.md` to facilitate validation.
2.  **Explicitly Define the Boundary**: Provide a clear table of what belongs in `CLAUDE.md` vs. the new context file to prevent duplication.
3.  **Formalize the "Phase 0" Requirement**: Include a requirement for a linter check to ensure plugin agents actually implement the context-load step.
