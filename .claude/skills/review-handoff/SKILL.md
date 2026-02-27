---
description: How to hand off a PR for human code review after automated reviews pass
user-invocable: false
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Review Handoff

After automated review is complete, you **MUST** request human code review before moving task to `5-done`. Never skip `4-in-review`.

## Process

1. **Verify automated review is complete**: PR has no unresolved threads, evaluator run persisted
2. **Move task**: `./scripts/project move <TASK-ID> in-review`
3. **Create review starter**: Write `.agent-context/<TASK-ID>-REVIEW-STARTER.md`
4. **Add Review section to task file**: Append review index to the task file
5. **Notify user**: Include thread count proof (mandatory)
6. **Address feedback**: Fix any issues from human reviewer
7. **After approval**: `./scripts/project complete <TASK-ID>`

## Creating Review Starter

Copy template from `.agent-context/templates/review-starter-template.md` to `.agent-context/<TASK-ID>-REVIEW-STARTER.md` and fill in:

```markdown
# Review Starter: <TASK-ID>

**Task**: <TASK-ID> - [Task Title]
**Task File**: `delegation/tasks/4-in-review/<TASK-ID>-*.md`
**Branch**: [feature-branch] -> main
**PR**: [URL]

## Implementation Summary
- [What was built]
- [Key decisions made]

## Files Changed
- path/to/file.py (new/modified)
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

Append a `## Review` section to the task file in `delegation/tasks/4-in-review/`:

```markdown
## Review

**PR**: #[number]
**Branch**: [feature-branch] -> main

### Artifacts
- Review starter: `.agent-context/<TASK-ID>-REVIEW-STARTER.md`
- Evaluator review: `.agent-context/reviews/<TASK-ID>-evaluator-review.md`

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
Review starter: `.agent-context/<TASK-ID>-REVIEW-STARTER.md`
Evaluator review: `.agent-context/reviews/<TASK-ID>-evaluator-review.md`
Threads: [total]/[total] resolved, 0 unresolved
```

If you cannot produce "0 unresolved", do NOT send this notification — go back and resolve open threads first.

## Handling Review Feedback

| Verdict | Action |
|---------|--------|
| **Approved** | Move task to `5-done` with `./scripts/project complete <TASK-ID>` |
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

**Full workflow**: `.agent-context/workflows/REVIEW-FIX-WORKFLOW.md`
