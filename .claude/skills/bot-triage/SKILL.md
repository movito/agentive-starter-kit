---
description: How to triage, reply to, and resolve automated review comments from BugBot and CodeRabbit
user-invocable: false
version: 1.1.0
origin: dispatch-kit
origin-version: 0.3.2
last-updated: 2026-04-19
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
- **Exception**: when a Trivial nit is consistent with a theme you're already
  fixing in the same PR (e.g., the PR is a typography pass and the nit is one
  more spacing tweak in the same area), it's cheaper to apply than to justify
  declining. Treat it as Fix (easy) and batch with the other fixes.
- When in doubt on Medium severity, fix it — it's cheaper than debating
- **Check-run status is NOT review state** — `gh pr checks` reported
  `pass` twice while CodeRabbit had filed CHANGES_REQUESTED
  (KIT-0077, the fourth KIT-0062 face). They are different API
  objects. The ONLY truth for review state is the `reviewThreads`
  GraphQL query (+ review decision); never proceed on a green
  check-run without fetching threads.
  **Fifth face (KIT-0102): a bot check can show `pass` while the
  review is RATE-LIMITED** — "pass — Review rate limited" means the
  latest push may be unreviewed. Before certifying a PR on a bot's
  approval, verify BOTH: zero unresolved reviewThreads AND the
  approving review's commit SHA matches the PR head — an APPROVED
  filed against an earlier commit certifies nothing about the code
  being merged.
  **Sixth face (KIT-0104 PR 3): a bot check can show `skipping`
  while the bot is actively reviewing** — BugBot's check-run read
  `skipping` for an entire session during which it posted a
  Medium-severity thread. Statuses lie in every direction; the
  threads query is the only truth, in both the "clean" and the
  "reviewed" directions.
- **Class sweeps must be indentation-tolerant** — when sweeping a
  markdown/format class from one finding (e.g. MD040 bare fences), the
  pattern is `^\s*` + token, never `^` + token: KIT-0067's `^```$`
  sweep fixed 4 fences and missed a list-indented one three lines
  away. A zero-hit grep proves the anchored token, not the class.
- **GREP-FIRST sweeps (added 2026-08-12 — fourth incomplete-sweep
  occurrence across KIT-0098/0100/0102)**: write the class grep BEFORE
  editing anything; its hit list IS the work list, checked off site by
  site. The recurring failure is not a missed re-check at the end — it
  is a sweep DEFINED from the flagged site instead of from the class,
  so sibling sites were never on the list. End-state grep stays as the
  proof; the opening grep is what makes it provable.
  **Refinement (KIT-0102 retro): derive the class from the full
  surface of the THING being changed** — its names, commands,
  subcommands, aliases — not from the incident that flagged it. The
  #127 grep covered five machinery names but never `project sync`,
  the very command being retired; the closing grep came back clean
  only because it inherited the opening grep's blind spot. A clean
  end-state grep proves the pattern, not the class — the class
  definition itself is the reviewable artifact.
- **Syntax-verify committable suggestions touching shell before applying** —
  especially heredocs, quoting, or redirects: run `bash -n` (or a scratch
  execution test) on the suggested code first. Committable ≠ compilable:
  on KIT-0058 PR #91 a CodeRabbit committable suggestion was a bash syntax
  error (heredoc body swallowed the `&&`-chained lines). If it fails, decline
  and paste the test result into the thread.
- **Read the REVIEW BODIES, not only the inline threads** — CodeRabbit
  puts "outside diff range" findings in the review body where
  thread-based triage never sees them. On KIT-0083 PR #106, round 3's
  ONLY finding lived there: the shipped output claimed the library was
  installed immediately before exiting 1 having installed nothing, and
  it would have merged unread. After fetching threads, also fetch
  `reviews[].body` for the latest round and scan for findings; treat
  them with the same severity triage as threads.
- **Triage ALL threads before fixing ANY. Then batch all fixes into one commit.**

## Batch Strategy

0. **FIRST ACTION of every triage: the reviewThreads GraphQL query** —
   not `pulls/comments` REST, which returns only top-level review
   comments and silently under-counts (KIT-0102: REST showed 3
   threads; GraphQL showed 10 — a triage built on REST would have
   certified 7 unhandled threads). The endpoint-truth rule above is
   now a mandatory opening step, not a caveat.
1. Read every comment from both bots before fixing anything
2. Categorize each as Fix or Resolve-without-fixing
3. Implement all fixes together
4. Commit once, push once — one re-review instead of N re-reviews

## Evaluator + CodeRabbit Convergence

When an adversarial evaluator finding (e.g., `code-reviewer`, `code-reviewer-fast`)
and a CodeRabbit (or BugBot) finding target the **same underlying issue**, treat
the fix as **confirmed from two independent sources**. Rather than solving it
twice:

1. Implement the fix **once** — but make sure it addresses the **union** of both
   findings' concerns. If one tool flagged a style issue and the other flagged a
   deeper architectural or security concern in the same code, resolve the deeper
   concern; the style fix is not a substitute.
2. Reply to the CodeRabbit/BugBot thread citing the commit SHA
3. Note the convergence in the evaluator review artifact
   (`.kit/context/reviews/<TASK-ID>-*.md`) — "Addressed, also flagged by CodeRabbit"
4. Resolve the bot thread as normal

**"Same issue" test**: two findings converge if a single code change can
legitimately resolve both root concerns. If the two findings describe different
problems that happen to touch the same line, treat them as separate findings.

Convergence is a **quality signal**: when two independent reviewers surface the
same concern, prioritize it — skip the "is this worth fixing?" debate and go
straight to the fix. This also helps the retro surface patterns (e.g., recurring
evaluator/bot overlap may indicate a spec-template gap).

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

**CIRCUIT BREAKER — self-inflicted churn (added 2026-08-10, KIT-0097
PR #120: nine rounds, later rounds dominated by defects introduced by
earlier fixes).** The no-round-cap policy assumes rounds CONVERGE. When
they stop converging, stop the loop:

- After each round, classify the new findings: original-defect vs
  **in text this review already changed** (self-inflicted).
- When a round's findings are MAJORITY self-inflicted — or from round
  4 onward regardless — STOP. Do not run another fix round. Resolve or
  disposition what's open, report honestly, and escalate to the
  operator: the remaining repair belongs to a FRESH session with a
  tight enumerated scope (context contamination is real; nine rounds
  of patch-on-patch degrades the very edits being reviewed).
- This does not license leaving legitimate findings unfixed — it moves
  the fixing to a session that can still see straight.

### Batching discipline (prevents cascade amplification)

- **Triage ALL threads before fixing ANY** — don't fix one and push, then discover three more
- **One push per round** — batch all fixes into a single commit
- **Only triage NEW findings each round** — don't re-triage resolved threads

## Reply Format

Use `agentive review-helper` for all reply and resolve operations.
The wrapper validates inputs and bypasses Claude Code's permission heuristic
on complex `gh api` arguments.

### Reply to a thread

```bash
agentive review-helper reply {pr_number} {comment_id} \
  'Fixed in {commit_sha}: {1-2 sentence description of what changed and where}.'
```

- `{comment_id}` is **numeric** (e.g., `2861292837`) — from REST `.id` or GraphQL `.databaseId`
- If the reply returns a 404 error, the comment is on an outdated diff — use `resolve` with the GraphQL thread ID instead

### Declining to fix

Same command, different body:

```bash
agentive review-helper reply {pr_number} {comment_id} \
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
agentive review-helper resolve PRRT_abc123
```

To resolve multiple threads, issue separate calls:

```bash
agentive review-helper resolve PRRT_abc123
```

```bash
agentive review-helper resolve PRRT_def456
```

## Verifying Zero Unresolved

```bash
agentive review-helper summary {pr_number}
```

Output: `Total:N Resolved:N Unresolved:N`

Target: `Unresolved:0` before proceeding.

## Fetching Thread Status

```bash
agentive review-helper threads {pr_number}
```

Tab-separated output: `isResolved\tdatabaseId\tauthor\tthreadNodeId\tbody_excerpt`

This gives: `isResolved`, root comment `databaseId` (for replies), author, GraphQL `id` (for resolving), and body excerpt.
