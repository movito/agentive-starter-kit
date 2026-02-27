---
description: Create feature branch and start a task (move from todo to in-progress)
argument-hint: "<TASK-ID>"
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Start Task

Start working on task `$ARGUMENTS`.

## Step 1: Check current state

Run these commands to understand the current situation:

```bash
git branch --show-current
```

```bash
ls delegation/tasks/2-todo/ 2>/dev/null | head -10 || echo "No tasks in 2-todo/"
```

```bash
ls delegation/tasks/3-in-progress/ 2>/dev/null | head -10 || echo "None in progress"
```

## Step 2: Preflight checks

1. **Verify not already on a feature branch**: If the current branch is already `feature/*`, refuse with: "Already on a feature branch. Finish current work first or switch to main."
2. **Verify task exists in `2-todo/`**: If the task file isn't in `2-todo/`, report where it is and refuse.
3. **Ensure main is up to date**: Run `git fetch origin main` and check if local main is behind.

## Step 3: Create branch and start task

1. **Ensure on main**: If not on `main`, run `git checkout main && git pull origin main`
2. **Create feature branch**:

   ```bash
   git checkout -b feature/$ARGUMENTS-short-description
   ```

   Derive `short-description` from the task filename (e.g., `TASK-0017-add-search-feature.md` -> `add-search-feature`).

3. **Start the task**:

   ```bash
   ./scripts/project start $ARGUMENTS
   ```

   This moves the task from `2-todo/` to `3-in-progress/` and updates the status field.

4. **Verify**: Confirm the task file is now in `3-in-progress/` and report:

   ```text
   Started $ARGUMENTS on branch feature/$ARGUMENTS-[description]
   Task moved to 3-in-progress/

   Tip: Name this session for easy recall later:
   /rename $ARGUMENTS [short description]
   ```

5. **Capture repo identity** (for later API calls):

   ```bash
   gh repo view --json nameWithOwner --jq .nameWithOwner
   ```

   Note the output (e.g., `owner/repo-name`) — use this for all `gh api` calls
   throughout the session. The repo owner may differ from your GitHub username.

6. **Emit milestone event** (optional, fire-and-forget — requires dispatch-kit):

   ```bash
   dispatch emit task_started --agent feature-developer --task $ARGUMENTS --payload '{"branch":"BRANCH_NAME"}' 2>/dev/null || true
   ```

   Replace `BRANCH_NAME` with the actual branch name from step 3.
