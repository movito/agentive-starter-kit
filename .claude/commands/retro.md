---
description: Run a structured session retrospective after completing a task
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Session Retrospective

Run a structured retro for the current task session. Collects metrics from the PR and produces formatted output for the planner to archive.

## Step 1: Identify the session

Determine the task ID and PR number. Try auto-detection first:

```bash
git branch --show-current
```

```bash
gh pr view --json number,title,headRefOid --jq '{pr: .number, title: .title, sha: .headRefOid}' 2>/dev/null || echo "No PR found"
```

If not on a feature branch or no PR exists, ask the user for the task ID and PR number.

## Step 2: Collect scorecard metrics

Run these commands and capture the results:

**Thread count** (total review threads on the PR):

```bash
gh api graphql -f query='{ repository(owner: "OWNER", name: "REPO") { pullRequest(number: PR_NUM) { reviewThreads(first: 100) { nodes { isResolved } } } } }' --jq '[.data.repository.pullRequest.reviewThreads.nodes[]] | length'
```

(Replace OWNER, REPO, PR_NUM with actual values. Get owner/repo from `gh repo view --json nameWithOwner --jq .nameWithOwner`.)

**Commit count** (on the feature branch):

```bash
git log --oneline origin/main..HEAD | wc -l
```

**Bot round count**: Count the distinct pushes that triggered bot re-reviews. Approximate by counting commits that were followed by bot activity. If uncertain, ask the user.

**Regression count**: How many bot findings were regressions of previously known patterns (from `.agent-context/patterns.yml` if it exists). If uncertain, report 0 and note it.

## Step 3: Reflect on the session

Think carefully about the session and answer these questions. Be specific — name exact files, functions, tools, and situations. Generic reflections are not useful.

### What Worked

What went well? What decisions paid off? What tools or processes saved time or caught real issues? Number each point and bold the key phrase.

### What Was Surprising

What was unexpected — positively or negatively? Things that took longer or shorter than expected, tools that behaved differently, edge cases nobody anticipated. Number each point and bold the key phrase.

### What Should Change

Concrete, actionable improvements. Each item should be something the planner can turn into a process fix, spec amendment, or tooling change. Number each point and bold the key phrase.

### Permission Prompts Hit

Were you blocked by any permission prompts during this session? For each one, note:
- The exact command or tool call that triggered it
- How long (approximately) you were blocked before the user approved
- Whether this is already in `.claude/settings.json` allow list or is a new pattern

If none, state "None." This data is used by the planner to proactively expand the allow list and reduce future stalls.

### Process Actions Taken

List action items as unchecked checkboxes. The planner will check them off as they're implemented.

## Step 4: Output the retro

Format the complete retro as a single markdown block. Use this exact structure:

```text
## [TASK-ID] — [Task Title] (PR #[number])

**Date**: [YYYY-MM-DD]
**Agent**: [agent version, e.g. feature-developer-v3]
**Scorecard**: [N] threads, [N] regressions, [N] fix rounds, [N] commits

### What Worked

1. **[Key phrase]** — [Details]

### What Was Surprising

1. **[Key phrase]** — [Details]

### What Should Change

1. **[Key phrase]** — [Details]

### Permission Prompts Hit

[List each prompt, or "None"]

### Process Actions Taken

- [ ] [Action item]
```

Print the formatted retro so the user can copy it to the planner session for archival.

## Guidelines

- **Be honest, not diplomatic.** If a tool produced garbage results, say so. If the spec was missing something, name it.
- **Be specific.** "BugBot caught a real bug in `_validate_config()` line 42" is useful. "BugBot was helpful" is not.
- **Limit to 3-5 items per section.** If you have more, pick the most important. Keep it scannable.
- **Scorecard accuracy matters.** The planner uses these numbers for trend analysis. Double-check thread and commit counts with the actual commands.
