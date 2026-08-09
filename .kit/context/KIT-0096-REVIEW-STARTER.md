# Review Starter — KIT-0096: Plugin release refresh (agentive-workflow 2.0.0)

**Task**: `.kit/tasks/4-in-review/KIT-0096-plugin-release-refresh.md`
**Evaluator record**: `.kit/context/reviews/KIT-0096-evaluator-review.md`
**Date**: 2026-08-09

## Two PRs — merge order matters

1. **MERGE FIRST**: https://github.com/movito/agentive-skills/pull/4 —
   the content release (plugin 2.0.0: 10 agents incl. planner/-f5,
   12 commands, 5 skills, roster.yaml, CHANGELOG, metadata). **No bots
   on that repo — your review IS the gate.** This is a prose-dominated
   sweep: prefer tree-grounded spot checks over evaluator
   reconstructions. Per-file generalization judgment calls are listed
   in the PR body.
2. **THEN**: https://github.com/movito/agentive-starter-kit/pull/119 —
   the kit-side CI drift guard. Tests/Lint/CodeRabbit/BugBot all green;
   7 bot threads triaged and resolved over 2 rounds. The `Plugin Drift
   Guard` check is EXPECTED RED (roster 404 → exit 4) until PR #4
   merges, then it goes green against the published roster.

## Verification already done

- Full kit suite green per push (1196+ passed; 17 drift-guard tests).
- Falsification AC: kit-newer → guard FAILS (live run in PR body +
  automated test); in-sync → exit 0 against the staged roster.
- Sentinel `VERIFY the worktree/branch, never create it` present in
  both shipped feature-developer variants.
- Zero flat cross-references; zero kit-specific leaks (grep sweeps).

## Flags for the operator

- **plugin.json/marketplace.json carry your personal email** in a
  public repo (pre-existing since 1.1.0). Say the word to strip it
  before publishing 2.0.0.
- **Kit-backport candidates** (plugin copies were hardened; kit
  canonical still has the defects): `check-ci main` hardcode in
  code-reviewer/test-runner/document-reviewer/security-reviewer;
  ci-checker missing the Cross-Repo Mode section the plugin carries.
  Worth a small follow-up task.

## Remaining after merge of PR #4 (F5 — say the word and I run it)

```bash
claude plugin marketplace update agentive-skills
claude plugin update agentive-workflow
claude plugin list   # expect 2.0.0
# fresh --new project; then grep its plugin feature-developer:
grep "VERIFY the worktree/branch, never create it" <plugin cache path>
```

Plus: record the native plugin-agent invocation experience in the test
project (KIT-0075 F4 evidence) in the completion note.
