# KIT-0058 Handoff — feature-developer

**Task**: `.kit/tasks/4-in-review/KIT-0058-visible-config-home.md`
**Target Codebase**: This repo — NOT a target repo (single-repo mode)
**Prepared**: 2026-07-22 (planner-f5)
**Estimated effort**: 3–4 hours

You are the feature-developer. Implement this task directly — do not
delegate to another agent instance.

## ⚠️ LAUNCH

**Your repository root is
`/Users/broadcaster_three/Github/ask-worktrees/KIT-0058/`** — branch
`feature/KIT-0058-visible-config-home`, fully provisioned. Run
`git pull --ff-only` first. Absolute paths / `git -C` throughout.

## Mission

Post-arc fast-follow, two halves: relocate the operator config to a
VISIBLE sibling of the kit checkout
(`<kit-parent>/agentive-config/` — guardrails instead of dotfolder
obscurity), and ship the `/setup-preset` conversational builder so a
Claude agent can interview any user into a working preset. The
operator's real preset waits on this task — it is the last blocker
before the one-button goes live.

## Verified anchors (planner, 2026-07-22)

- Resolution point: `scripts/local/bootstrap:143` —
  `local file="${XDG_CONFIG_HOME:-$HOME/.config}/agentive-kit/preset"`
  inside the resolve chain's preset layer. This line (plus the two
  header comments at :65/:84) is F1's target.
- Doctor's reader: `scripts/core/project` ~:1286/:1442/:1494 — the
  `--against-preset` comparison reuses the same path logic; keep the
  "two can never disagree" property (one path-resolution helper both
  call, or shell/py equivalents pinned by a shared test).
- `docs/preset.example` header (:7-9) and its `env-source` example
  (:53) carry the old path — F5's targets, plus the new
  `/setup-preset` pointer line (F6).
- Skills/commands home note: KIT-0057 merged the canonical homes —
  the new command goes in `.claude/commands/setup-preset.md`
  (commands' canonical home; no read-both concerns for a NEW file).

## Context you must not lose

- **Resolve locates, orchestrate seeds** (accepted evaluation
  finding, F2): the path function writes NOTHING; first-use seeding
  (`.gitignore` + README, idempotent, never overwriting) is an
  orchestrate step. N3: no drive-by dir creation on preset-less runs.
- **Worktree-safe parent resolution** (F1): primary clone via
  `--git-common-dir`, then parent, then `/agentive-config/`.
  `AGENTIVE_KIT_CONFIG_DIR` is the ONLY override — never a search
  chain. Loaded path NAMED in output (existing loudness rule).
- **Legacy `~/.config` is a notice, never a fallback** (F4) — a read
  from there is a bug; test both directions. Notice retires at 0.9.0
  (join the removal set in the task you'd file... it's already noted
  in the spec — add it to KIT-0059's removal list rather than a new
  task).
- **Doctor `config-home` check** (F3, rides `doctor.d/` with a
  `# shapes:` header): remote present → visibility must be private
  (`gh repo view --json visibility`; WARN on public or gh failure,
  naming the risk); `env.source` tracked = FAIL (secret in git);
  no git = PASS naming the path. Incident citation per lifecycle rule.
- **`/setup-preset` (F6) — the three binding rules are structural**:
  (1) NO hardcoded question list — the command instructs the agent to
  run `./scripts/local/bootstrap --help` and derive the interview from
  the door's actual questions and matrix; (2) plain language, one
  question at a time, consequences explained, expert shortcut; (3)
  secrets never transit the chat — path references only, pasted keys
  refused, `chmod 600` as a user step. Finish loudly: show the file,
  validate keys against the door's accepted set, offer the
  private-repo pattern, name the first `--new` run as the proof.
  Self-review item 10 applies to the command's own text: every claim
  it makes about the door must be derived-at-runtime or verified.
- **HOME/`AGENTIVE_KIT_CONFIG_DIR` override in every test** (N1);
  stranger-path characterization first (N2).

## Test approach

- Ordering rule: local tests green → trio
  (`echo y | ADVERSARIAL_UNATTENDED=1 …`; log-file-with-verdict is the
  proof) → PR open; `git status` after every run.
- Extend `tests/test_setup_door.py` (resolution, override, seeding
  idempotence, legacy-notice both ways) and `tests/test_doctor.py`
  (config-home check fixtures: private/public/no-git/tracked-secret).
- One-button demo re-run from the new location — transcript in the PR.
- `pytest` directly; `./scripts/core/ci-check.sh` before pushing.

## Evaluation summary

`arch-review-fast`: REVISION_SUGGESTED — seeding moved to orchestrate
(accepted, in spec); `SourceControlService` abstraction declined
(third forge-abstraction decline); git-based resolution acknowledged
deliberate. Disposition in the task file; log:
`.adversarial/logs/KIT-0058-visible-config-home--arch-review-fast.md`.
No outstanding blockers.

## Out of scope

- Team/shared presets; any new preset keys; bot-app automation
- Executing the 0.9.0 removals; downstream repos
- KIT-0061/0062/0063

## PR sizing

Single PR (< 400 lines: path relocation + seeding + doctor check +
legacy notice + docs + the command + tests): branch
`feature/KIT-0058-visible-config-home` (already created).
