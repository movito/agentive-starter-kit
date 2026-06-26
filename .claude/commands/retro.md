---
description: Run a structured session retrospective after completing a task
version: 1.1.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-04-17
created-by: "@movito with planner2"
---

# Session Retrospective

Run a structured retro for the current task session. Collects metrics from the PR and produces formatted output for the planner to archive.

## Step 0: Detect cross-repo mode

Check if `CLAUDE.md` contains a `## Target Repository` section with `Path` and `GitHub` fields.

```bash
grep -A 5 "## Target Repository" CLAUDE.md 2>/dev/null || echo "SINGLE_REPO_MODE"
```

If found, extract:
- **target_path**: the value after `- **Path**:` (e.g., `../my-project-code`)
- **target_github**: the value after `- **GitHub**:` (e.g., `your-org/my-project-code`)

If `SINGLE_REPO_MODE`, skip all cross-repo logic — run every command below against the current repo exactly as before.

**For the rest of this document:**
- `GIT_TARGET` means: use `git -C <target_path>` in cross-repo mode, or plain `git` in single-repo mode
- `GH_TARGET` means: use `gh --repo <target_github>` in cross-repo mode, or plain `gh` in single-repo mode

> **Caveat — `gh api` does not accept `--repo`.** The `GH_TARGET` macro is for porcelain commands (`gh pr view`, `gh run list`, etc.). For GraphQL/REST calls, do **not** prefix `gh api` with the macro — resolve owner/name from `target_github` and inline them into the query (or pass via `-F` query variables).

## Step 1: Identify the session

Determine the task ID and PR number. Try auto-detection first:

```bash
# In cross-repo mode, the feature branch is in the target repo
GIT_TARGET branch --show-current
```

```bash
GH_TARGET pr view --json number,title,headRefOid --jq '{pr: .number, title: .title, sha: .headRefOid}' 2>/dev/null || echo "No PR found"
```

If not on a feature branch or no PR exists, ask the user for the task ID and PR number.

If in cross-repo mode, note which repo the PR belongs to in your output.

## Step 2: Collect scorecard metrics

Run these commands and capture the results:

**Thread count** (total review threads on the PR):

Resolve owner/name first (note: `gh api` does **not** accept `--repo`, so we inline the values into the GraphQL query):

```bash
# Re-detect target_github inline so this snippet is self-contained — do not
# rely on a shell variable possibly set in a previous step (Step 0 documents
# extraction as a markdown value, not a shell export, so a literal-follower
# would otherwise silently fall back to the planning repo).
target_github=$(grep -A 8 '## Target Repository' CLAUDE.md 2>/dev/null \
  | grep -E '\*\*GitHub\*\*' \
  | sed -E 's/.*`([^`]+)`.*/\1/' \
  | head -n1)

if [ -n "$target_github" ]; then
  # Cross-repo mode
  OWNER=${target_github%%/*}
  NAME=${target_github##*/}
else
  # Single-repo mode — use the current repo
  OWNER_NAME=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
  OWNER=${OWNER_NAME%%/*}
  NAME=${OWNER_NAME##*/}
fi

# Fail fast if either is empty — prevents a confusing GraphQL error downstream.
if [ -z "$OWNER" ] || [ -z "$NAME" ]; then
  echo "ERROR: Could not resolve OWNER/NAME for thread-count query" >&2
  exit 1
fi

gh api graphql -f query="{ repository(owner: \"$OWNER\", name: \"$NAME\") { pullRequest(number: <PR_NUM>) { reviewThreads(first: 100) { nodes { isResolved } } } } }" --jq '[.data.repository.pullRequest.reviewThreads.nodes[]] | length'
```

(Replace `<PR_NUM>` with the PR number from Step 1.)

**Commit count** (on the feature branch):

```bash
GIT_TARGET log --oneline origin/main..HEAD | wc -l
```

Note: In cross-repo mode, if the feature branch has already been merged, you may need to reconstruct the count from the merge commit. Ask the user if uncertain.

**Bot round count**: Count the distinct pushes that triggered bot re-reviews. Approximate by counting commits that were followed by bot activity. If uncertain, ask the user.

**Regression count**: How many bot findings were regressions of previously known patterns (from `.kit/context/patterns.yml` if it exists). If uncertain, report 0 and note it.

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

In cross-repo mode, check both `.claude/settings.json` (planning repo) and `<target_path>/.claude/settings.json` (target repo) for the allow list.

If none, state "None." This data is used by the planner to proactively expand the allow list and reduce future stalls.

### Process Actions Taken

List action items as unchecked checkboxes. The planner will check them off as they're implemented.

## Step 4: Save the retro

Format the complete retro as a single markdown block using the structure below, then **save it to a file**.

**File path**: `.kit/context/retros/[TASK-ID]-retro.md` (always in the planning repo, even in cross-repo mode)

Create the `.kit/context/retros/` directory if it doesn't exist:

```bash
mkdir -p .kit/context/retros
```

Use this exact structure for the file content:

```text
## [TASK-ID] — [Task Title] (PR #[number])

**Date**: [YYYY-MM-DD]
**Agent**: [agent name, e.g. feature-developer]
**Mode**: [single-repo | cross-repo (target: <target_github>)]
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

After saving, confirm the file path so the planner can find and review it.

## Guidelines

- **Be honest, not diplomatic.** If a tool produced garbage results, say so. If the spec was missing something, name it.
- **Be specific.** "BugBot caught a real bug in `_validate_config()` line 42" is useful. "BugBot was helpful" is not.
- **Limit to 3-5 items per section.** If you have more, pick the most important. Keep it scannable.
- **Scorecard accuracy matters.** The planner uses these numbers for trend analysis. Double-check thread and commit counts with the actual commands.
- **In cross-repo mode**, always note which repo each data point came from if there's any ambiguity.
