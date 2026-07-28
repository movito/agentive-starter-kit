# Linear Integration

**Purpose**: Optional sync between `.kit/tasks/` files and Linear issues
**Audience**: Operators who want team visibility on kit-managed tasks
**Related**: `.kit/tasks/README.md` (folder structure and status
mapping), `.kit/docs/LINEAR-SYNC-BEHAVIOR.md` (sync semantics in depth)

---

The kit's task system is markdown files in `.kit/tasks/` status
folders. Tasks work fine without Linear — agents create, track, and
complete them using the folder structure alone. Syncing to
[Linear](https://linear.app) adds team visibility and project
management on top; it is more involved than just adding an API key,
which is why it gets this page.

## Setting up Linear

**1. Create a Linear account**

Sign up at [linear.app](https://linear.app) if you don't have an
account.

**2. Create a new team**

Go to Settings → Teams → [Create new team](https://linear.app/settings/new-team).

**Important:** use the same identifier for your Linear team as you use
for task prefixes in the codebase. For example:

- If your task files are named `ABC-0001-feature.md`, `ABC-0002-bugfix.md`
- Set your Linear team identifier to `ABC`

This keeps task IDs consistent between your codebase and Linear.

**3. Get your Linear API key**

Go to your Linear workspace settings:
`https://linear.app/{workspace}/settings/account/security`
(replace `{workspace}` with your Linear workspace name).

- Scroll down to "Personal API keys"
- Click "Create new API key"
- Give it a name (e.g., your project's name)
- Copy the key (starts with `lin_api_`)

**4. Get your Team ID**

Your Team ID is the identifier you chose in step 2 (e.g., `ABC`).

**5. Configure your `.env` file**

```bash
LINEAR_API_KEY=lin_api_your-key-here
LINEAR_TEAM_ID=ABC
```

## How sync works

When configured, the task system:

- Syncs task files in `.kit/tasks/` folders to Linear issues
- Maps folder locations to Linear statuses (e.g., `2-todo/` → "Todo") —
  the full mapping table lives in `.kit/tasks/README.md`, and the
  precedence rules (status field vs. folder vs. Linear state) in
  `.kit/docs/LINEAR-SYNC-BEHAVIOR.md`
- Adds GitHub links to task files in Linear issue descriptions

**Manual sync:**

```bash
./scripts/core/project linearsync
```

**Auto-sync:** pushing to `main` or `develop` triggers the GitHub
Actions workflow.

**GitHub Actions setup:**

1. Go to your repo Settings → Secrets and variables → Actions
2. Add `LINEAR_API_KEY` secret
3. Add `LINEAR_TEAM_ID` secret (optional)

## Without Linear

Tasks work fine without Linear — they're just markdown files. Agents
can create, track, and complete tasks using the folder structure
alone. Linear adds team visibility and integrations, but isn't
required.

---

**Source**: moved from README.md (KIT-0073 doc curation)
