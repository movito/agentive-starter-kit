# Coverage Workflow

**Purpose**: Measure test coverage and hold the line the project
actually enforces
**Replaces**: the source-project original (archived:
`docs/archive/COVERAGE-WORKFLOW.md` — KIT-0067 D2/A41)

---

## The rule

Two related thresholds, one enforced and one reviewed:

- **Enforced — 80% aggregate.** `pyproject.toml` pins
  `[tool.coverage.report] fail_under = 80`: the test suite FAILS when
  *project-wide* reported coverage drops below it. That pin is the
  single source of the number; this doc deliberately does not restate
  exclusions or omit-lists (read `[tool.coverage.run]` /
  `[tool.coverage.report]` in `pyproject.toml`).
- **Reviewed — 80% for new code.** There is no per-diff mechanical
  gate; new-code coverage is held in review: the `Missing` column for
  files you touched is the evidence, and uncovered new logic needs a
  documented reason in the PR (see Judgment calls).

## The commands

```bash
# Coverage report with uncovered lines (what CI runs, step 6):
pytest tests/ --cov=scripts --cov-report=term-missing

# The full local gauntlet — includes the coverage-gated suite:
./scripts/core/ci-check.sh
```

Reading the report: `Miss` = statements never executed; `Missing` =
their line numbers. Add `--cov-report=html` and open
`htmlcov/index.html` when you want line-by-line detail.

## Judgment calls

- Document any acceptable gap (with the reason) in the PR — never
  silently ship uncovered new logic.
- `# pragma: no cover` is for genuinely unreachable or
  platform-excluded lines only; the pragma is the documentation.
- Don't chase 100% with tests that assert implementation details;
  the gate is 80% for a reason.

---

**Related**: [TESTING-WORKFLOW.md](./TESTING-WORKFLOW.md) ·
`pyproject.toml` → `[tool.coverage.*]`
