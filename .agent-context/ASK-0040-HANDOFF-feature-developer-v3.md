# ASK-0040 Handoff: Consolidate .env.example and .env.template

## Mission

Make `.env.template` the single canonical env template. Sync `.env.example` to match, update all references.

## Task File

`delegation/tasks/2-todo/ASK-0040-consolidate-env-templates.md`

## Scope

**Config/docs-only task** — no Python code changes, no new tests needed.

6 files to modify + 1 file to sync:

| # | File | Change |
|---|------|--------|
| 1 | `.env.example` | Replace content with `.env.template` content + sync header comment |
| 2 | `.claude/agents/feature-developer-v3.md` (line 349) | `.env.example` → `.env.template` |
| 3 | `.claude/agents/feature-developer.md` (line 566) | `.env.example` → `.env.template` |
| 4 | `.adversarial/scripts/evaluate_plan.sh` (line 27) | `.env.example` → `.env.template` |
| 5 | `.adversarial/scripts/proofread_content.sh` (line 27) | `.env.example` → `.env.template` |
| 6 | `.adversarial/scripts/review_implementation.sh` (line 27) | `.env.example` → `.env.template` |
| 7 | `.adversarial/scripts/validate_tests.sh` (line 27) | `.env.example` → `.env.template` |

## Key Constraints

- Do NOT delete `.env.example` — adversarial-workflow's `init` command expects it
- Do NOT change `.venv/` references — those are in the adversarial-workflow package
- `.env.template` is canonical (20+ references in ADRs, README, onboarding)

## Verification Command

After all changes, run:

```bash
grep -rn "\.env\.example" . --include="*.md" --include="*.sh" --include="*.py" \
  | grep -v ".git/" | grep -v "5-done/" | grep -v "8-archive/" | grep -v ".venv/" \
  | grep -v "ASK-0040"
```

Expected: zero results.

## Workflow Notes

- **Docs-only workflow applies**: skip pre-implementation skill, evaluator, self-review boundary audit
- Keep: spec check, bots, CI, preflight
- Serena activation: `mcp__serena__activate_project("agentive-starter-kit")`

## First Steps

```bash
# 1. Create feature branch
git checkout -b feature/ASK-0040-consolidate-env-templates

# 2. Start the task
./scripts/project start ASK-0040
```
