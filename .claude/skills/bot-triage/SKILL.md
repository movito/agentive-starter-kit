---
description: How to triage, reply to, and resolve automated review comments from BugBot and CodeRabbit
user-invocable: false
version: 1.0.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-02-27
created-by: "@movito with planner2"
---

# Bot Review Triage

Reference knowledge for triaging automated review comments. Use `/triage-threads` to begin a triage session.

## API Endpoints (CRITICAL — read every word)

> **Reply endpoint** (the ONLY way to reply to a review thread):
>
> ```bash
> gh api repos/{owner}/{repo}/pulls/{pr_number}/comments/{comment_id}/replies -f body="..."
> ```
>
> - `{comment_id}` is a **numeric** ID (e.g., `2506713600`), NOT a node ID (NOT `PRRC_...`)
> - Get numeric IDs from REST: `gh api repos/{owner}/{repo}/pulls/{pr}/comments --jq '.[].id'`
> - Or from GraphQL: the `databaseId` field (NOT `id` — that's the node ID)
>
> **WRONG — these all fail:**
>
> ```bash
> # WRONG: in_reply_to on /comments endpoint — creates orphan, not thread reply
> gh api repos/{owner}/{repo}/pulls/{pr}/comments -f body="..." -F in_reply_to=12345
>
> # WRONG: node ID instead of numeric ID — API rejects non-numeric values
> gh api repos/{owner}/{repo}/pulls/{pr}/comments/{PRRC_abc123}/replies -f body="..."
>
> # WRONG: missing PR number — 404
> gh api repos/{owner}/{repo}/pulls/comments/{id}/replies -f body="..."
> ```
>
> **Fetch comments**: `gh api repos/{owner}/{repo}/pulls/{pr_number}/comments`

## Severity-Based Triage

| Verdict | Criteria | Action |
|---------|----------|--------|
| **Fix** | Major/Critical severity, real bug, security issue, compatibility problem | Implement fix (batch with other fixes) |
| **Fix (easy)** | Medium severity, reasonable suggestion, quick to implement | Implement fix (batch with other fixes) |
| **Resolve without fixing** | Trivial nitpick, low severity cosmetic, platform-irrelevant concern | Post brief justification, resolve thread |

### Guidelines

- **Fix** anything Major/Critical severity or that is a real bug
- **Fix** anything that breaks the graceful-degradation contract
- **Fix** Medium severity suggestions if they're quick and improve the code
- **Resolve without fixing** Trivial/Low severity cosmetic issues (naming style preferences, minor formatting)
- **Resolve without fixing** concerns that are platform-irrelevant (e.g., Windows CRLF) or physically impossible
- When in doubt on Medium severity, fix it — it's cheaper than debating
- **Triage ALL threads before fixing ANY. Then batch all fixes into one commit.**

## Batch Strategy

1. Read every comment from both bots before fixing anything
2. Categorize each as Fix or Resolve-without-fixing
3. Implement all fixes together
4. Commit once, push once — one re-review instead of N re-reviews

## Fix-Everything Policy

**Fix all legitimate findings. No round cap. Track revision count in retro.**

Each round follows the same loop:

1. Wait for both bots (`/wait-for-bots` or `/check-bots`)
2. Triage ALL new threads — categorize as Fix or Resolve-without-fixing (see Severity-Based Triage above)
3. Batch all fixes into one commit
4. Push once → next round

**Resolve-without-fixing** is still valid for:
- Findings that are factually wrong (false positives)
- Platform-irrelevant concerns (e.g., Windows CRLF on a macOS-only project)
- Findings that contradict project conventions (with justification)

**Never resolve a finding just because it's "too many rounds."** If the finding is legitimate and improves the code, fix it. The retro tracks total rounds and threads — that's where cascade patterns surface and get addressed at the root cause (e.g., better spec templates, new pattern registry entries).

### Batching discipline (prevents cascade amplification)

- **Triage ALL threads before fixing ANY** — don't fix one and push, then discover three more
- **One push per round** — batch all fixes into a single commit
- **Only triage NEW findings each round** — don't re-triage resolved threads

## Reply Format

Use `./scripts/gh-review-helper.sh` for all reply and resolve operations.
The wrapper validates inputs and bypasses Claude Code's permission heuristic
on complex `gh api` arguments.

### Reply to a thread

```bash
./scripts/gh-review-helper.sh reply {pr_number} {comment_id} \
  'Fixed in {commit_sha}: {1-2 sentence description of what changed and where}.'
```

- `{comment_id}` is **numeric** (e.g., `2861292837`) — from REST `.id` or GraphQL `.databaseId`
- If the reply returns a 404 error, the comment is on an outdated diff — use `resolve` with the GraphQL thread ID instead

### Declining to fix

Same command, different body:

```bash
./scripts/gh-review-helper.sh reply {pr_number} {comment_id} \
  'Acknowledged, but won'\''t fix: {clear technical justification}.'
```

**Rules:**
- Always reference the commit SHA where the fix was made
- Cite specific line numbers in the current code
- Keep it to 1-3 sentences — the code diff speaks for itself
- Reply to ALL threads before pushing — batch fixes, batch replies, push once
- **Each reply = one separate Bash call** (no batching in one call)

## Resolving Threads

After posting a reply, resolve the thread using its GraphQL node ID:

```bash
./scripts/gh-review-helper.sh resolve PRRT_abc123
```

To resolve multiple threads, issue separate calls:

```bash
./scripts/gh-review-helper.sh resolve PRRT_abc123
```

```bash
./scripts/gh-review-helper.sh resolve PRRT_def456
```

## Verifying Zero Unresolved

```bash
./scripts/gh-review-helper.sh summary {pr_number}
```

Output: `Total:N Resolved:N Unresolved:N`

Target: `Unresolved:0` before proceeding.

## Fetching Thread Status

```bash
./scripts/gh-review-helper.sh threads {pr_number}
```

Tab-separated output: `isResolved\tdatabaseId\tauthor\tthreadNodeId\tbody_excerpt`

This gives: `isResolved`, root comment `databaseId` (for replies), author, GraphQL `id` (for resolving), and body excerpt.
