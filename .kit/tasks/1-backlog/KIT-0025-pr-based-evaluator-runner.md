# KIT-0025: PR-Based Evaluator Runner

- **Status**: Backlog
- **Priority**: High
- **Type**: Feature
- **Estimate**: M (half-day)
- **Depends on**: KIT-0024 (tiered manifest, for core script sync)

## Problem

The adversarial evaluator system (`review_implementation.sh`) uses `git diff`
to collect changes, which only captures unstaged modifications. In the
feature-developer-v5 gated workflow, code is committed and pushed (Phase 6)
before the evaluator runs (Phase 8). This means the evaluator always sees an
empty diff and aborts with "No changes detected — PHANTOM WORK."

Current workaround: manually write the evaluator review based on bot outcomes.
This skips the cross-model adversarial review step entirely.

## Solution

Create `scripts/core/run-evaluator.sh` — a PR-based evaluator runner that
collects diffs from GitHub PRs instead of the working tree.

### Interface

```bash
./scripts/core/run-evaluator.sh <evaluator-name> <PR-number> [--task TASK-ID]
```

### Behavior

1. **Collect diff**: `gh pr diff <PR-number>` (exact diff bots and humans see)
2. **Collect context**: If `--task` given, read `.kit/context/<TASK-ID>-REVIEW-STARTER.md`
3. **Load evaluator config**: Parse `.kit/adversarial/evaluators/*/<evaluator-name>/evaluator.yml`
4. **Assemble prompt**: Inject diff + context into the evaluator's prompt template
5. **Call model**: Use the API key from `api_key_env` in the evaluator config
6. **Write output**: `.kit/context/reviews/<TASK-ID>-<output_suffix>` (suffix from evaluator.yml)
7. **Extract verdict**: Parse APPROVED / CONCERNS / FAIL from output
8. **Exit code**: 0 = APPROVED, 1 = CONCERNS/FAIL, 2 = error (timeout, API failure)

### Evaluator Discovery

The script should find evaluators by name across all providers:
```
.kit/adversarial/evaluators/
  openai/code-reviewer/evaluator.yml
  google/arch-review-fast/evaluator.yml
  ...
```

`run-evaluator.sh code-reviewer 39` finds `openai/code-reviewer/evaluator.yml`
by matching the directory name. Error if ambiguous (same name in multiple providers).

## Gate Integration

### Phase 1: Script only (this task)

- `run-evaluator.sh` works standalone
- Feature-developer Phase 8 calls it instead of `review_implementation.sh`
- Preflight Gate 5 unchanged (checks file existence)

### Phase 2: Verdict-aware preflight (follow-up task)

- Preflight Gate 5 reads the output file and parses the verdict
- APPROVED = pass, CONCERNS/FAIL = fail with prescribed action
- Multiple evaluator outputs supported (all must be APPROVED)

### Phase 3: Configurable evaluator list (follow-up task)

- `.kit/adversarial/config.yml` gains `required_evaluators` list
- Preflight iterates the list and checks each has an APPROVED review file
- Per-project override via the config file

## Acceptance Criteria

- [ ] `run-evaluator.sh code-reviewer <PR>` produces a review file with verdict
- [ ] `run-evaluator.sh arch-review-fast <PR> --task KIT-XXXX` includes review starter context
- [ ] Exit code reflects verdict (0/1/2)
- [ ] Works with any evaluator in `.kit/adversarial/evaluators/` without hardcoding
- [ ] Handles missing API key gracefully (clear error message, exit 2)
- [ ] Handles model timeout gracefully (exit 2, partial output preserved)
- [ ] Output file follows existing naming convention (`<TASK-ID>-<suffix>.md`)
- [ ] Script is added to `.core-manifest.json` under `scripts_core`
- [ ] Feature-developer-v5 Phase 8 documentation updated to reference new script

## Out of Scope

- Changing `review_implementation.sh` (legacy, keep for backward compat)
- Verdict-aware preflight (Phase 2, separate task)
- Configurable evaluator lists (Phase 3, separate task)
- Running evaluators in parallel (nice-to-have, not required)

## Technical Notes

- Use `gh pr diff` not `git diff main...HEAD` — PR diff is canonical and works post-rebase
- The evaluator config already has `model`, `api_key_env`, `timeout`, `prompt` — reuse all of it
- Template variable in prompt is `{content}` — replace with assembled diff + context
- Consider a `{review_starter}` template variable for structured context injection
- API calls: curl to OpenAI/Google/Anthropic/Mistral endpoints based on provider directory
- Keep it shell-based (consistent with other core scripts), not Python

## References

- Evaluator configs: `.kit/adversarial/evaluators/`
- Current (broken) script: `.kit/adversarial/scripts/review_implementation.sh`
- Feature-developer-v5 Phase 8: `.claude/agents/feature-developer-v5.md`
- Preflight Gate 5: `scripts/core/preflight-check.sh`
- Memory note: `feedback_evaluator_script_flow.md`
