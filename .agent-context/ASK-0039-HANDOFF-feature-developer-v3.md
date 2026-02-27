# ASK-0039 Handoff — Full TDD Lifecycle Verification

**Task**: ASK-0039 — Workflow Verification: Full TDD Lifecycle (All 11 Phases)
**Task File**: `delegation/tasks/2-todo/ASK-0039-workflow-verify-full-tdd-lifecycle.md`
**Agent**: feature-developer-v3
**Created**: 2026-02-27

## Serena Activation

```text
mcp__serena__activate_project("agentive-starter-kit")
```

## Mission

This is the **comprehensive workflow verification task**. It exercises ALL 11 phases
of the v3 workflow on a real Python code change with TDD. If this completes
successfully, the upgraded workflow is fully validated for agentive-starter-kit.

**Dependencies**: ASK-0037 ✅ (docs-only workflow), ASK-0038 ✅ (architecture overview)

## What to Build

Add a new lint rule **DK004** to `scripts/pattern_lint.py` that detects bare
`except Exception` clauses that silently swallow errors (pass or empty body).

### Key Technical Details

1. **Existing rules**: DK001 (str.replace for extensions), DK003 (string containment).
   Study them in `scripts/pattern_lint.py` (248 lines) for the AST visitor pattern.

2. **Tests exist**: `tests/test_pattern_lint.py` (164 lines) has tests for DK001 and
   DK003. Add DK004 tests to the same file, following the same class structure
   (e.g., `class TestDK004`).

3. **Pattern registry**: `.agent-context/patterns.yml` — consult before implementing.

4. **AST-based approach**: DK001 and DK003 use AST visitors. DK004 should too —
   no regex. Look for `ast.ExceptHandler` nodes where:
   - `handler.type` is `Exception` or `BaseException`
   - Body is `[ast.Pass]` or empty (no statements)
   - NOT when body contains `raise`, `logging.*`, `logger.*`, or `return`

5. **noqa suppression**: Check for `# noqa: DK004` on the except line. The existing
   rules have a `_has_noqa` helper — reuse it.

## Evaluator Setup

The adversarial evaluators are installed and ready:
- `adversarial code-reviewer` — o1 deep review
- `adversarial code-reviewer-fast` — Gemini Flash quick check
- Template: `.adversarial/templates/code-review-input-template.md`

Both are functional. Use `code-reviewer-fast` for this task (code change is small).

## Workflow Notes from Prior Tasks

Lessons from ASK-0037 and ASK-0038:

1. **Always use repo-relative paths** in review starters (never `/Users/...`)
2. **Wait for bots to finish BEFORE claiming ready** — run `/check-bots` until CURRENT
3. **Black is pinned to 23.12.1** — use `pre-commit run black --files` not bare `black`
4. **`ruff format`** after every Serena symbol edit
5. **Don't hardcode version numbers** in generated docs — reference `pyproject.toml`

## Phase Checklist (All 11)

The task spec lists all phases and verification criteria. Every phase must be
exercised — no skips. Document any phase that fails.

## Files You'll Touch

| File | Action |
|------|--------|
| `scripts/pattern_lint.py` | Add DK004 rule + update docstring |
| `tests/test_pattern_lint.py` | Add TestDK004 class with 6+ tests |
| `.adversarial/inputs/ASK-0039-code-review-input.md` | Evaluator input |
| `.agent-context/reviews/ASK-0039-evaluator-review.md` | Evaluator output |
| `.agent-context/ASK-0039-REVIEW-STARTER.md` | Review starter |
