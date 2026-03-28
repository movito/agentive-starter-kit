---
name: Evaluator script doesn't work with committed code
description: review_implementation.sh uses git diff (unstaged) which is empty after commit — needs a --branch or --pr flag to diff against main
type: feedback
---

The `review_implementation.sh` evaluator script aborts with "No changes detected in git diff!" when all code is already committed and pushed. This breaks the feature-developer-v5 Phase 8 flow because the evaluator runs AFTER the PR is created and bot-reviewed (Phase 6-7).

**Why:** The script was designed for a pre-commit review workflow, but the gated workflow commits code before running the evaluator. By Phase 8, there are no unstaged changes — only committed diffs against main.

**How to apply:** The script needs one of these fixes:
1. Add a `--branch` flag that makes it use `git diff main...HEAD` instead of `git diff`
2. Add a `--pr` flag that fetches the PR diff from GitHub
3. Auto-detect: if `git diff` is empty but `git diff main...HEAD` has changes, use the branch diff
4. Accept a pre-generated diff file as input alongside the review input

Until fixed, Phase 8 evaluator reviews must be written manually based on bot review outcomes (as was done for KIT-0024). This is a valid workaround since CodeRabbit and BugBot provide thorough automated review, but it means the cross-model adversarial review step is effectively skipped.
