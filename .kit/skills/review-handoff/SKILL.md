---
description: How to hand off a PR for human code review after automated reviews pass
user-invocable: false
version: 1.1.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-07-13
created-by: "@movito with planner2"
---

# Review Handoff

After automated review is complete, you **MUST** request human code review before moving task to `5-done`. Never skip `4-in-review`.

## Process

1. **Verify automated review is complete**: PR has no unresolved threads, evaluator run persisted
2. **Move task**: `./scripts/core/project move <TASK-ID> in-review`
3. **Create review starter**: Write `.kit/context/<TASK-ID>-REVIEW-STARTER.md`
4. **Add Review section to task file**: Append review index to the task file
5. **Notify user**: Include thread count proof (mandatory)
6. **Address feedback**: Fix any issues from human reviewer
7. **After approval**: `./scripts/core/project complete <TASK-ID>`

## Bundled PR? Do this FIRST (multiple task IDs, one PR)

Preflight Gates 5/6 check for artifacts named exactly
`<TASK-ID>-REVIEW-STARTER.md` and `<TASK-ID>-evaluator-review.md` —
**per task ID**, deliberately (KIT-0042: the gates stay strict; the
bundle intelligence lives here, in process). When one PR ships several
tasks, follow the lead-task + pointer-files convention **up front**, not
after a gate failure:

1. **Pick the lead task** (usually the lowest ID) and write the full
   review starter and evaluator record under the lead's name, covering
   the whole bundle.
2. **For every other bundled task**, create two short pointer files with
   the exact solo-task names:
   - `.kit/context/<TASK-ID>-REVIEW-STARTER.md` — a few lines: names the
     bundle + PR, points at the lead's starter, and states this task's
     slice of the change.
   - `.kit/context/reviews/<TASK-ID>-evaluator-review.md` — points at the
     lead's evaluator record (and notes any per-task skip rationale).

Reference shape: the KIT-0037/38/39 bundle (PR #71) —
`.kit/context/KIT-0038-REVIEW-STARTER.md` and
`.kit/context/reviews/KIT-0038-evaluator-review.md` are the canonical
examples of pointer files.

If you forget, Gates 5/6's FAIL output names this convention — but doing
it here, before preflight, is the intended path.

## Creating Review Starter

Copy template from `.kit/context/templates/review-starter-template.md` to `.kit/context/<TASK-ID>-REVIEW-STARTER.md` and fill in.

**IMPORTANT**: All file paths in the review starter MUST be repo-relative (e.g., `CLAUDE.md`, `scripts/core/pattern_lint.py`). Never use absolute paths like `/Users/.../project/file.py` — they leak local machine info and are non-portable.

```markdown
# Review Starter: <TASK-ID>

**Task**: <TASK-ID> - [Task Title]
**Task File**: `.kit/tasks/4-in-review/<TASK-ID>-*.md`
**Branch**: [feature-branch] -> main
**PR**: [URL]

## Implementation Summary
- [What was built]
- [Key decisions made]

## Files Changed
- path/to/file.py (new/modified)   ← MUST be repo-relative paths (never absolute)
- ...

## Test Results
- X tests passing
- Y% coverage

## Automated Review Summary
- BugBot: [result]
- CodeRabbit: [result]
- Code-review evaluator: [verdict + key findings]

## Areas for Review Focus
- [Any concerns you have]
- [Tricky implementations]

## Related ADRs
- [List relevant ADRs]

---
**Ready for human review**
```

## Adding Review Section to Task File

Append a `## Review` section to the task file in `.kit/tasks/4-in-review/`:

```markdown
## Review

**PR**: #[number]
**Branch**: [feature-branch] -> main

### Artifacts
- Review starter: `.kit/context/<TASK-ID>-REVIEW-STARTER.md`
- Evaluator review: `.kit/context/reviews/<TASK-ID>-evaluator-review.md`

### Files Changed
- `path/to/file.py` (new)
- `path/to/other.py` (modified)
- `tests/test_file.py` (new)
```

Keep the files list flat — just path and (new/modified/deleted).

## Notifying the User

Include the **actual thread count output** from your verification. This is mandatory — it proves you checked.

```text
Implementation complete. All automated reviews passed. Ready for human review.

PR: [URL]
Review starter: `.kit/context/<TASK-ID>-REVIEW-STARTER.md`
Evaluator review: `.kit/context/reviews/<TASK-ID>-evaluator-review.md`
Threads: [total]/[total] resolved, 0 unresolved
```

If you cannot produce "0 unresolved", do NOT send this notification — go back and resolve open threads first.

## Handling Review Feedback

| Verdict | Action |
|---------|--------|
| **Approved** | Move task to `5-done` with `./scripts/core/project complete <TASK-ID>` |
| **Changes requested** | See fix process below |

## Handling Fix Prompts

When you receive a fix prompt after CHANGES_REQUESTED:

1. **Read the review file** — understand all findings in detail
2. **Read the original task file** — refresh on acceptance criteria
3. **Address required changes** — focus on HIGH severity first
4. **Run tests**: `pytest tests/ -v`
5. **Verify CI**: `/check-ci`
6. **Update review-starter** — note what was fixed
7. **Notify user** — ready for re-review (Round 2)

**Key points:**
- Task stays in `4-in-review/` — don't move it
- Max 2 review rounds — Round 2 is final
- Update, don't create new review-starter file

**Full workflow**: `.kit/context/workflows/REVIEW-FIX-WORKFLOW.md`
