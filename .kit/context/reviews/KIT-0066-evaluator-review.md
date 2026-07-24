# KIT-0066 Evaluator Review Record

**Date**: 2026-07-24
**Input**: `.adversarial/inputs/KIT-0066-code-review-input.md` (full-file
context, `git diff main...HEAD` at the pre-fix implementation commits)
**Trio**: code-reviewer-fast (gemini-2.5-flash) CONCERNS ·
code-reviewer (o3) FAIL · claude-code (sonnet-4-6) CHANGES_REQUESTED
**Run order**: local suite green → trio → fixes → PR (KIT-0035/0046
ordering rule). `git status` verified clean after every run.

## Disposition (feature-developer-f5)

### Accepted — fixed in the follow-up commit (agent text hardening)

1. Input validation before shell use (claude HIGH; also covers the
   `gh repo create` injection MEDIUM): name must match
   `^[a-z][a-z0-9-]{0,60}$`; absolute existing code path.
2. Mandatory staged-content secret scan before the first commit
   (claude HIGH; upgrades fast-gate's "heuristics" finding from
   reactive to a named gate); tracked-`.env` `git rm --cached` rule.
3. `.gitignore`: create-or-append + expanded patterns + `check-ignore`
   verification (fast + claude MEDIUM). Note: o3's claim that the
   ignore file is written after `add -A` was WRONG (order was already
   ignore-then-add); the tracked-.env variant was real and is fixed.
4. Owner derivation failure → ask, never empty (fast).
5. Kit-checkout-as-code-folder guard (fast).
6. Sibling re-assertion before the door run, with the why (o3
   "nested path" finding — the flow already forced siblings by
   construction; the assertion makes it checkable).
7. Duplicate/long slug rule for backlog stubs (o3).
8. Clean-tree skip + dirty-tree ask for pre-existing repos (o3 +
   claude LOW).
9. Missing/malformed KIT-LOCAL markers → stop, report, never
   free-hand edit (fast).
10. `mv` failure → stop (fast). Missing git identity → surface, don't
    invent (o3). Ambiguous remotes → `origin`, else ask (fast).
11. Line-anchor rot warning surfaced in the agent text itself
    (claude MEDIUM).
12. Demo transcript: operator absolute path abbreviated (claude
    MEDIUM, partial — see declined #5).

### Declined — with reasoning

1. **Non-TTY/CI operation for AskUserQuestion steps** (o3): the agent
   is user-invoked in an interactive tab by design (operator rule);
   unattended CI runs are out of scope for this component.
2. **Absolute target pointers** (o3): contradicts the canonical
   convention — `docs/CROSS-REPO-PATTERN.md` mandates relative
   sibling paths ("never hardcode absolute paths").
3. **Doctor-tail length assertion** (o3): the door owns its output
   contract; the agent relays, it does not parse-assert prose.
4. **`bootstrap --help` runtime skew check** (claude LOW): the door's
   exit-2 contract already fails loudly on wrong flags; the new
   anchor-rot note covers the guidance side.
5. **Full path anonymization of committed artifacts** (claude MEDIUM,
   remainder): planning artifacts across this repo already carry
   operator paths (pre-existing pattern); the preset line in the
   transcript was abbreviated as the cheap part.
6. **Template "NAMES ONLY" rule not in the paste-able block** (claude
   LOW): REFUTED — the block's "Dependencies and required secrets"
   section contains the rule verbatim.
7. **`/tmp` persistence/permissions for demo dirs** (claude LOW):
   demo hygiene was handled in-run (seeded `.env` deleted
   immediately); demo dirs carry no secrets afterwards.
8. **`agent-handoffs.json` `task_started: null`** (claude LOW):
   machine-managed by `scripts/core/project`; out of scope here —
   noted for the retro.

Evaluator blind-spot reminder (standing): trio reliably catches logic
edge cases; CSS/dual-render classes don't apply to this doc-only diff.

---

# Appended evaluator logs

## Source: KIT-0066-code-review-input--code-reviewer-fast.md

#  Code Reviewer Fast

**Source**: .adversarial/inputs/KIT-0066-code-review-input.md
**Evaluator**: code-reviewer-fast
**Model**: gemini/gemini-2.5-flash
**Generated**: 2026-07-24 12:00 UTC

---

### Findings

**[ROBUSTNESS]: GitHub owner derivation failure**
- **Location**: `.claude/agents/project-intake.md:Inputs`
- **Edge case**: The `gh api user --jq .login` command fails (e.g., `gh` not installed, not authenticated, network error, or returns an empty string).
- **What happens**: The `GitHub owner` variable will be empty or malformed. This will cause `gh repo create` in Step 2 to fail with an invalid `owner/<name>` argument. Subsequently, the `bootstrap` command in Step 3 will also fail due to a malformed `--target-github` flag, as it will receive an invalid owner. The agent does not explicitly prompt the user for a GitHub owner if the automatic derivation fails.
- **Tested?**: No

**[ROBUSTNESS]: Code folder is the kit checkout itself**
- **Location**: `.claude/agents/project-intake.md:Step 1: Sibling layout`
- **Edge case**: The user provides the `agentive-starter-kit` checkout directory (where the `project-intake` agent is running from) as the "Code folder path".
- **What happens**: The agent will attempt to create the planning repo as a sibling to the kit checkout (e.g., `agentive-starter-kit-planning/`). This could lead to a conflict with the kit's own operational assumptions, or in the worst case, attempt to `mv` the kit checkout itself if it were deemed "transient", severely disrupting the environment.
- **Tested?**: No

**[ROBUSTNESS]: Insufficient `.gitignore` augmentation for existing repos**
- **Location**: `.claude/agents/project-intake.md:Step 2: Code repo — init, commit, GitHub`
- **Edge case**: The code folder is not already a git repo and contains a pre-existing, but minimal or insufficient, `.gitignore` file (e.g., only `.DS_Store`).
- **What happens**: The instruction "Seed a minimal `.gitignore` if none exists (at minimum `.env`; add the obvious artifacts...)" implies the agent only acts if *no* `.gitignore` exists. If one already exists, even if insufficient, the agent will not augment it, potentially leaving the code repo in a state where common build artifacts or sensitive files (beyond `.env`) are not ignored.
- **Tested?**: No

**[ROBUSTNESS]: Lack of error handling for file system operations**
- **Location**: `.claude/agents/project-intake.md:Step 1: Sibling layout`
- **Edge case**: Moving the code folder to the intended parent directory fails (e.g., due to permissions, disk full, target directory already exists with the same name, or other I/O errors).
- **What happens**: The agent's procedure states "ask the user for the intended parent directory and move it there first." It does not specify error handling if this `mv` operation fails. Subsequent steps would then operate on an incorrect or non-existent path, leading to cascading failures.
- **Tested?**: No

**[CORRECTNESS/ROBUSTNESS]: Ambiguous remote for existing git repo**
- **Location**: `.claude/agents/project-intake.md:Step 2: Code repo — init, commit, GitHub`
- **Edge case**: The code folder is already a git repo, `gh repo create` is skipped, but the existing repo has *no* remotes configured or has *multiple* remotes.
- **What happens**: The instruction "confirm the existing `owner/repo` and use it for `--target-github`" is vague. If no remote is configured, there's no `owner/repo` to confirm. If multiple remotes exist, it's unclear which one the agent should choose. Without explicit user interaction or a defined fallback (e.g., always `origin`), the `--target-github` value for Step 3's `bootstrap` command will be empty or incorrect, leading to its failure.
- **Tested?**: No (demo explicitly skips `gh repo create` and manually sets the `--target-github` value, thus not testing this logic path).

**[ROBUSTNESS]: Missing `project-context` markers in planning repo agents**
- **Location**: `.claude/agents/project-intake.md:Step 4a. Fill the KIT-LOCAL project-context regions.`
- **Edge case**: The scaffolded agent files (`planner.md`, etc.) are missing the `<!-- BEGIN/END KIT-LOCAL: project-context -->` marker lines, or these markers are malformed.
- **What happens**: The agent's `Edit` operation (which relies on these markers to identify the region to replace) will fail to locate the target or will perform an incorrect modification. This would leave the planning repo's agents without their crucial `project-context` information, severely impacting their effectiveness.
- **Tested?**: No (demo verifies "marker lines kept intact" in the *output*, but doesn't test the agent's resilience to *missing* markers).

**[ROBUSTNESS]: Secrets detection heuristics**
- **Location**: `.claude/agents/project-intake.md:Step 0: Read the brief, verify the inputs`
- **Edge case**: The brief or code folder contains sensitive information that is a "real credential value" but is not in an easily recognizable `KEY=VALUE` format (e.g., base64 encoded strings, long random strings that don't look like typical API keys but are sensitive).
- **What happens**: The agent's heuristic for "spot what looks like a real credential value" might fail to detect it. This could lead to sensitive, non-public information being inadvertently committed to version control.
- **Tested?**: No (demo confirms the brief *was* compliant, but not the agent's ability to detect non-compliance).

### Test Gap Summary

| Edge Case | Function | Tested? | Risk |
|---|---|---|---|
| GitHub owner derivation fails | `project-intake`: Inputs | No | High |
| Code folder is the kit checkout itself | `project-intake`: Step 1 | No | High |
| Existing git repo has no/multiple remotes | `project-intake`: Step 2 | No | High |
| Missing `project-context` markers | `project-intake`: Step 4a | No | High |
| Lack of error handling for `mv` | `project-intake`: Step 1 | No | Medium |
| Insufficient `.gitignore` augmentation | `project-intake`: Step 2 | No | Medium |
| `gh repo create` fails for other reasons | `project-intake`: Step 2 | No | Medium |
| Secrets detection heuristics limited | `project-intake`: Step 0 | No | High (Security) |

### Verdict

**CONCERNS**: Several critical robustness and potential correctness issues have been identified, particularly around error handling for external commands, assumptions about user input, and interactions with Git/GitHub. The demo transcript primarily covers the happy path, leaving significant gaps in testing for these edge cases. Failure in these areas could lead to incorrect repo setup, data exposure, or agent workflow failures requiring manual intervention.
## Source: KIT-0066-code-review-input--code-reviewer.md

#  Code Reviewer

**Source**: .adversarial/inputs/KIT-0066-code-review-input.md
**Evaluator**: code-reviewer
**Model**: o3
**Generated**: 2026-07-24 12:01 UTC

---

### Summary
Reviewed the new `project-intake` flow (agent spec, template, docs).  The change is prose-heavy but it drives real shell commands, so small wording slips become runtime faults.  I found 8 distinct edge-case/logic risks (2 high-severity correctness bugs, 4 latent robustness issues, 2 test gaps).

### Findings

**[CORRECTNESS]: Wrong `--target-path` is recorded when code folder is nested**
- **Location**: `.claude/agents/project-intake.md` – Step 3 (`--target-path ../<name>`)
- **Edge case**: User keeps prototype in `~/work/prototypes/alpha/snip-stash/` and asks to create the planning repo in the *same* directory (`snip-stash-planning`).  Relative `../<name>` now points to `../snip-stash` *one level above* the real code repo.
- **What happens**: Door happily records the wrong pointer in `CLAUDE.md`; all later slash-commands (`/wrap-up`, `prepare-review-input.sh`, etc.) act on a non-existent repo, silently corrupting the workflow.
- **Expected**: Pass the *absolute* code path (`$CODE_PATH`) or compute the relative path *after* `cd $PARENT/$NAME-planning` – e.g. `--target-path ../$NAME` only if the repos truly are siblings.
- **Test coverage**: NOT covered – demo transcript only shows the simplest sibling layout.
- **Severity**: Bug (breaks now).

---

**[CORRECTNESS]: Duplicate/long “slug” filenames break backlog seeding**
- **Location**: Step 4b (task file creation rule)
- **Edge case**: Two “next steps” both titled “Add logging”.  Naïve slugging makes
  `SNIP-0001-add-logging.md` and silently overwrites it with `SNIP-0002-add-logging.md`, losing one task.
  On Windows the 260-char path limit will be exceeded for very long titles.
- **What happens**: Missing backlog tasks or OS error → agent stops on `cp`/`touch` failure.
- **Expected**: De-duplicate slugs (append a counter) and truncate to a safe length (<100 chars).
- **Test coverage**: NOT covered.
- **Severity**: Bug (data loss under common conditions).

---

**[ROBUSTNESS]: `.gitignore` seeding can stage secrets on first commit**
- **Location**: Step 2.2/2.3
- **Edge case**: Prototype already contains an `.env` with real keys (very common).
  Flow seeds `.gitignore`, *then* `git add -A` – staging `.env` **before** the ignore rule takes effect (git only respects ignores that existed *before* the add).
- **What happens**: Real credentials are committed and pushed.
- **Expected**: Add `.env` to `.gitignore`, then run `git rm --cached .env` (if present) *before* the first commit.
- **Test coverage**: NOT covered.
- **Severity**: Latent security risk.

---

**[ROBUSTNESS]: Interactive questions hang in unattended runs**
- **Location**: Step 0 (ask for next step) & Step 2.4 (visibility)
- **Edge case**: Operator runs the agent in a non-TTY CI job (or sets `ADVERSARIAL_UNATTENDED=1` as in evaluator gates).
- **What happens**: `AskUserQuestion` blocks forever; pipeline times out.
- **Expected**: Respect `$CI`/`ADVERSARIAL_UNATTENDED` or expose `--yes --visibility private` flags so the run is non-interactive.
- **Test coverage**: NOT covered.
- **Severity**: Latent.

---

**[ROBUSTNESS]: Commit may fail with “nothing to commit”**
- **Location**: Step 2.3 – unconditional `git add -A && git commit -m …`
- **Edge case**: Folder was already a git repo and *already committed*; the working tree is clean.
- **What happens**: `git commit` exits 1 (“nothing to commit”) → agent aborts the whole flow.
- **Expected**: Check `git status --porcelain` and skip the commit when clean.
- **Test coverage**: NOT covered.
- **Severity**: Latent.

---

**[ROBUSTNESS]: Git user identity missing causes door to fail after seeding**
- **Location**: Step 3 – planning repo commit 4c
- **Edge case**: Fresh machine without global `user.name` / `user.email`.
- **What happens**: Door succeeds (it doesn’t commit), but later `git commit -m …` in planning repo fails; flow stops mid-way.
- **Expected**: Detect and set temp identity (`git -C $PLAN config user.name "Project Intake"` …) or surface a clear message *before* Step 3.
- **Severity**: Latent.

---

**[TESTING]: Doctor-tail capture not asserted**
- **Location**: Step 3 interface contract
- **Gap**: Demo transcript shows doctor tail *printed*, but no automated check asserts that the captured tail is the last ~15 lines (contract says “tail”).  A future door change that moves the verdict higher will silently truncate it.
- **Severity**: Gap.

---

**[INTERACTION]: Relative path recording breaks if user later moves the pair**
- **Location**: Throughout – design choice to store `../<name>` in `CLAUDE.md`
- **Edge case**: After creation operator moves both repos into a deeper folder (`~/work/2026/`).  The relative pointer in `CLAUDE.md` is now wrong; commands fail until manually edited (easy to forget).
- **Expected**: Store an *absolute* path plus a comment recommending manual update if moved, or at least warn during the move (doctor check).
- **Severity**: Latent usability hazard.

### Edge Cases Verified Clean
• Existing remote ⇒ flow skips `gh repo create` (spec covers).
• Door exit 2 (“target exists”) ⇒ user prompt, never deletes automatically.
• Brief with real vs code-reported language mismatch ⇒ trust code, record rule.
• Preset absent ⇒ `--no-preset` path demonstrated.
• Kit never installed in code repo – enforced by spec and demo.

### Test Gap Summary

| Edge Case | Function/Step | Tested? | Risk |
|-----------|---------------|---------|------|
| Nested code path (`--target-path`) | Step 3 | ❌ | High |
| Duplicate next-step titles | Step 4b | ❌ | High |
| `.env` already present | Step 2 | ❌ | Med-High |
| Non-interactive run | Steps 0, 2 | ❌ | Med |
| Clean repo already committed | Step 2 | ❌ | Med |
| Missing git identity | Step 4c | ❌ | Med |
| Doctor tail length change | Step 3 | ❌ | Low |

### Verdict

**FAIL**

Two correctness bugs (wrong target pointer, task-file overwrite) can corrupt the planning workflow or lose data on a perfectly common input.  Fix these and the listed robustness gaps before merge.
## Source: KIT-0066-code-review-input--claude-code.md

#  Claude Code

**Source**: .adversarial/inputs/KIT-0066-code-review-input.md
**Evaluator**: claude-code
**Model**: anthropic/claude-sonnet-4-6
**Generated**: 2026-07-24 12:03 UTC

---

## Phase 1: Understand Intent

This diff introduces a **prototype graduation workflow** for an AI agent toolkit called "agentive-starter-kit." The deliverables are:

1. `PROTOTYPE-HANDOFF-TEMPLATE.md` — a paste-able prompt template users copy into Claude/Cowork sessions to extract a structured brief
2. `project-intake.md` — an AI agent definition (markdown instructions for Claude) that automates creation of a "split pair" (plain code repo + private planning repo)
3. Supporting documentation updates (README, CROSS-REPO-PATTERN.md, task status files)

**Critical paths**: The agent executes shell commands (`git`, `gh`, `./scripts/local/bootstrap`) against user-supplied paths and processes user-supplied content (the handoff brief). The template solicits sensitive metadata from AI sessions. No application code (Python, JS, etc.) is introduced — this is entirely an agent/documentation artifact.

---

## Phase 2: Security Analysis

### [HIGH]: Path Traversal / Arbitrary Directory Targeting via User-Supplied Paths

- **Location**: `project-intake.md` — Steps 1, 2, 3 (all `git -C <code-path>` and `--new <parent>/<name>-planning` invocations)
- **Issue**: The agent constructs shell commands using user-supplied values (`<code-path>`, `<parent>`, `<name>`) with no explicit validation or sanitization guidance. A project name like `../../sensitive-dir` or a code folder path pointing to `/etc` would be passed directly to `git -C` and `gh repo create`. The agent instructions say "infer what you can" and default the name to the brief's project name or folder basename — both user-controlled. For example: `git -C /etc init` or `--new ../../some-other-repo` are structurally reachable.
- **Remediation**: Add an explicit validation step before Step 2: require `<name>` to match `^[a-z][a-z0-9-]{0,99}$` (kebab-case only, no path separators); require `<code-path>` to be an absolute path that exists and is not a system directory; validate that `<parent>/<name>-planning` does not escape the intended parent. Add this to the "Inputs" and "Step 0" sections as named checks the agent must perform.

---

### [HIGH]: Credential Scanning — Reactive Only, No Proactive Scan Instruction

- **Location**: `project-intake.md` — Step 0, Restrictions section; `PROTOTYPE-HANDOFF-TEMPLATE.md` — "Rules the brief must follow"
- **Issue**: The agent's secrets discipline is **reactive**: "If you spot what looks like a real credential value in the brief or the code folder, stop and tell the user." The agent also commits `git -C <code-path> add -A` — a blanket add of all files in the prototype folder — before any scan. If `PROTOTYPE-BRIEF.md` or any prototype source file contains a credential (pasted API key, token, connection string) that the agent fails to recognize as a credential, it will be committed and potentially pushed to GitHub. Pattern recognition of credentials is imperfect for LLMs — this is a known failure mode.
- **Remediation**: Add a mandatory pre-commit scan step using `git -C <code-path> diff --cached` piped through a tool like `truffleHog`, `gitleaks`, or at minimum `grep -rE '(sk-|ghp_|xoxb-|AKIA|eyJ)' <code-path>` before any `git commit`. Make this a named, non-optional step between "add -A" and the commit. The agent should also explicitly instruct users (in the template's rules) that `.env` files containing values must be confirmed absent before handoff.

---

### [MEDIUM]: `git add -A` Without Pre-Exclusion of Sensitive Files

- **Location**: `project-intake.md` — Step 2, item 3
- **Issue**: The agent seeds `.gitignore` with `.env` (and stack-specific patterns) in Step 2 item 2, but the `git add -A` in item 3 runs immediately afterward. If the prototype folder contains `.env`, `.env.local`, secrets files, or large binaries that are not yet matched by the just-seeded `.gitignore` (e.g., due to gitignore caching, or files with non-standard names like `secrets.json`, `credentials.yaml`), they will be staged. The instruction "at minimum `.env`" is not exhaustive.
- **Remediation**: After seeding `.gitignore` and before `add -A`, run `git -C <code-path> check-ignore -v .env` to verify the ignore is active. Expand the mandatory ignore list to include `*.key`, `*.pem`, `*credentials*`, `*secrets*`, `.env.*`. Explicitly mention these in the agent step.

---

### [MEDIUM]: Absolute Path of Operator's Config Exposed in Demo Transcript

- **Location**: `.kit/context/KIT-0066-DEMO-TRANSCRIPT.md` — "Preset-resolved run" section
- **Issue**: The demo transcript hardcodes `/Users/broadcaster_three/Github/agentive-config/preset` — a real, operator-specific absolute path identifying the operator's username and filesystem layout. This is committed into the repository and will appear in git history permanently. While this is a local path rather than a credential, it leaks PII (username) and filesystem structure. The handoff file also contains `/Users/broadcaster_three/Github/ask-worktrees/KIT-0066/`.
- **Remediation**: Replace operator-specific absolute paths in committed artifacts with anonymized placeholders (e.g., `~/Github/agentive-config/preset` or `/Users/<operator>/Github/agentive-config/preset`). Apply to both the demo transcript and the handoff file before merge. Add a pre-commit note to the demo transcript template warning authors to redact personal paths.

---

### [MEDIUM]: `gh repo create` Command Injection via Project Name

- **Location**: `project-intake.md` — Step 2, item 5
- **Issue**: The agent constructs: `gh repo create <owner>/<name> --private --source <code-path> --push`. If `<name>` contains shell metacharacters (spaces, semicolons, backticks, `$(...)`) the `Bash` tool invocation could be exploited. While the agent is instructed to derive `<name>` from the brief or folder basename, the brief is user-supplied markdown and the folder path is user-supplied — no sanitization requirement is stated.
- **Remediation**: The validation fix from the first finding (enforcing `^[a-z][a-z0-9-]{0,99}$`) would also mitigate this. Additionally, the agent should use the `gh` CLI's own validation (`gh repo create` will reject invalid names) as a secondary gate, but rely on name validation first.

---

### [LOW]: Bootstrap Script Invoked With Relative `--target-path`; No Validation of Sibling Layout

- **Location**: `project-intake.md` — Step 3
- **Issue**: The bootstrap command uses `--target-path ../<name>` — a relative path. If the planning repo is not created as a sibling of the code repo (e.g., if the user places it elsewhere), this relative path will resolve incorrectly and be silently recorded in CLAUDE.md as the wrong pointer. The agent confirms sibling layout in Step 1 but does not re-validate it when constructing the flag.
- **Remediation**: After Step 1 confirms the sibling layout, explicitly assert that `<parent>/<name>-planning/../<name>` resolves to the code folder before invoking the door. Print both resolved absolute paths for the user to confirm before executing.

---

### [LOW]: No Secret-Value Pattern Guidance in Template Prompt

- **Location**: `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md` — "Dependencies and required secrets" section
- **Issue**: The template instructs the prototyping agent to include "the NAMES of any required secrets or API keys (e.g. OPENAI_API_KEY). Secret NAMES ONLY — never paste values." However, this instruction is in the outer template instructions, not in the paste-able block itself. A user who only copies the inner fenced block (the paste-able prompt) will send a prompt to the prototyping agent that includes the instruction, but the receiving AI agent (in the prototyping session) may not be reliably constrained from including values if the conversation context contains them.
- **Remediation**: Move the "Secret NAMES ONLY — never paste values, tokens, or any part of them" instruction explicitly into the paste-able block, within the "Dependencies and required secrets" section description. Example: add `(NAMES ONLY — if you see a value in our conversation, do NOT include it here)` inline in that section's instruction text.

---

### [LOW]: Demo Transcript Uses `/tmp` Without Noting OS-Specific Persistence Risk

- **Location**: `.kit/context/KIT-0066-DEMO-TRANSCRIPT.md` — "Demo root" and "Cleanup" sections
- **Issue**: The demo creates repositories under `/tmp/kit0066-intake-demo/` and notes "no `rm -rf` allowlist exists — leftovers listed at the end." On macOS (which the transcript implies, given `/private/tmp/`), `/tmp` survives reboots within a session and is world-readable for the directory listing. If the demo `.env` seeded by `env-source` was not deleted promptly, another local user could read it. The transcript says "The seeded `.env` was deleted from the demo dir immediately after capture" — but this is manual and relies on discipline.
- **Remediation**: Note in the demo template and the agent's edge-cases section that demo directories under `/tmp` should use `chmod 700` or use `mktemp -d` and delete immediately after the run. Alternatively, mandate that demo runs occur under `~/` in a private directory.

---

## Phase 3: Correctness Analysis

### [MEDIUM]: Step Ordering — `.gitignore` Written After Potential File Scan

- **Location**: `project-intake.md` — Step 0 ("If you spot what looks like a real credential value in the brief **or the code folder**") and Step 2 items 2-3
- **Issue**: Step 0 asks the agent to skim the code folder for credentials, but Step 2 item 2 seeds the `.gitignore`. The code folder scan (Step 0) happens before `.gitignore` exists, which is actually correct ordering — but the agent's credential check in Step 0 is described as "spot what looks like a real credential value" during a "skim," not a systematic scan. The brief parse and folder skim happen in the same step. If the skim misses a credential, it flows directly to `add -A` with no second gate.
- **Remediation**: Make the credential check a separate named sub-step with explicit patterns, not a byproduct of the initial skim. See HIGH finding above.

---

### [MEDIUM]: Line Anchor References Will Rot

- **Location**: `project-intake.md` — Step 3 (`scripts/local/bootstrap:385-386`, `kit_markers.py:173-202`, `kit_markers.py:187`); handoff file (`bootstrap:385-386, 397-398`)
- **Issue**: The agent's instructions hard-reference specific line numbers in `scripts/local/bootstrap` and `scripts/local/kit_markers.py` with the caveat "as of 2026-07-24." These will silently become incorrect as the scripts evolve, causing agents following the instructions to mis-explain or mis-locate behavior. The handoff explicitly warns "re-verify before coding" but the shipped agent file does not carry this warning to future users.
- **Remediation**: Either (a) remove line-number anchors from the agent file and replace with behavior descriptions + function/variable names that are more stable, or (b) add a prominent "**Line anchors are dated 2026-07-24 — verify against current file before relying on them**" note at the top of Steps 3 and 4a. The task spec already accepts this risk via the evaluation disposition; the agent file itself should surface it.

---

### [LOW]: Missing Idempotency Guard for Existing Git Repo With Uncommitted Changes

- **Location**: `project-intake.md` — Step 2, item 1-3
- **Issue**: The procedure handles "already a git repo — keep its history." However, if the existing repo has uncommitted changes (dirty working tree), `git add -A && commit` will commit those changes alongside the prototype import. This may include work-in-progress files or editor artifacts the user did not intend to commit. The agent note "this is a fresh export, not a working tree with unrelated changes" may not hold if the user ran the intake on an actively-edited folder.
- **Remediation**: Before `git add -A`, run `git -C <code-path> status --short` and present it to the user. If the repo is dirty, ask explicitly: "The folder has uncommitted changes — commit all of them as the initial import, or stop so you can review first?"

---

### [LOW]: `agent-handoffs.json` — `task_started: null` for "In Progress" Task

- **Location**: `.kit/context/agent-handoffs.json`
- **Issue**: Both `planner` and `feature-developer` entries show `"status": "handoff_ready"` and `"task_started": null` while the task is `In Progress`. This is a data-correctness issue in the coordination state — the timestamp was never set when the task moved from todo to in-progress.
- **Remediation**: Set `task_started` to the actual start date (`"2026-07-24"` or an ISO datetime) when transitioning to in-progress. If this field is machine-managed, the transition script has a bug that should be filed.

---

## Phase 4: Code Quality

### [LOW]: Agent File Contains No Version-Skew Guard for Bootstrap Flags

- **Location**: `project-intake.md` — Step 3
- **Issue**: The agent says "Do NOT pass `--name` or `--prefix`: the door refuses them for the planning shape (`scripts/local/bootstrap:385-386`, as of 2026-07-24)." If bootstrap is updated to accept these flags (or new flags are added), the agent's prohibition becomes incorrect guidance. There is no runtime verification step.
- **Remediation**: Add a Step 3 pre-check: run `./scripts/local/bootstrap --help 2>&1 | grep -E '(name|prefix)'` and note whether the flags appear; if they do, stop and inform the user the agent's guidance may be outdated before proceeding.

---

### [LOW]: Template's Inner Paste-able Block Loses Outer Context Rules

- **Location**: `.kit/templates/PROTOTYPE-HANDOFF-TEMPLATE.md`
- **Issue**: The outer document has three rules ("Secrets by name only," "Self-contained," "Next steps seed the backlog"). These are for the *user's* benefit, not the prototyping agent. A user who pastes only the inner fenced block may follow these rules themselves but the prototyping agent receiving the prompt is not given them. The inner prompt is clean and well-written, but the "next steps seed the backlog" rule — which shapes how specific the steps should be — is particularly important for the prototyping agent to internalize.
- **Remediation**: Embed the specificity guidance directly in the "Suggested next steps" section of the inner prompt. Already partially done ("write them specific enough that someone could start work from the entry alone") — this is adequate; the outer rules are for the human operator. This is a low-concern observation, not a defect.

---

### Positive Observations

1. **Explicit secrets discipline throughout**: "never print, stage, or commit secret values — names only" appears in the Restrictions, Step 0, the template's rules, and the demo transcript. The `.env` mode-0600 handling and non-printing of env-source contents are specifically called out.
2. **Clear door exit contract**: using exit codes 0/1/2 as the interface and explicitly prohibiting re-derivation of install state is a sound design. Relaying the doctor tail verbatim prevents information loss.
3. **No-kit-in-code-repo enforcement**: the restriction is stated in four places (Restrictions, Step 2.6, "Why the split pair," and docs), with rationale. Hard to miss.
4. **Non-TTY safety by design**: flags-only bootstrap invocation ensures the agent never hangs on an interactive prompt. Good operational discipline.
5. **Sibling layout convention**: the explicit parent-directory layout with a concrete ASCII tree reduces ambiguity for both agents and humans.
6. **Task-seeding scope boundary**: "transcription only — no elaboration, no re-prioritization, no decomposition" is a well-defined and correctly conservative constraint.
7. **Anti-self-delegation pattern**: the "never delegate via the Task tool" restriction is explicit and the reason is given.
8. **Demo transcript covers both stranger and preset paths**: two door runs (with and without preset) provide meaningful coverage evidence.

---

## Context Required / Unverifiable

- The `Bash` tool's execution environment (sandboxing, allowed paths, user permissions) is not visible — the injection and path traversal findings assume the tool executes shell commands without additional OS-level sandboxing.
- Whether `./scripts/local/bootstrap` performs its own input validation on `--new`, `--target-path`, and `--target-github` cannot be confirmed from this diff — the bootstrap script is referenced but not shown.
- Whether Claude Code's `Bash` tool shells expand metacharacters or passes arguments as arrays cannot be confirmed — this affects severity of the command injection finding.
- The `gh` CLI's own input validation for `gh repo create` argument handling cannot be confirmed from this diff.
- The operator preset file's contents and security posture (private git repo, permissions) are not shown.
- Whether `/tmp` on the operator's macOS is actually world-accessible cannot be confirmed from this diff alone.

*None of the above affect the verdict.*

---

## Overall Assessment

**CHANGES_REQUESTED**

The diff introduces a well-structured, clearly reasoned workflow with good documentation discipline and explicit security principles in the right places. However, two high-severity gaps exist that must be addressed before production use:

1. **No input validation on user-supplied paths and project names** before they are passed to shell commands. A malicious or malformed brief/path can reach `git -C`, `gh repo create`, and `./scripts/local/bootstrap` without sanitization.
2. **`git add -A` executes before any systematic credential scan**. The reactive "spot if you see something" guidance is insufficient — if the prototype folder contains an unrecognized credential format, it will be committed and potentially pushed to GitHub under the operator's account.

The operator-path exposure (absolute paths in committed artifacts) and missing idempotency guards are lower priority but should be addressed in this PR given they are straightforward fixes. The line-anchor rot issue is documented risk; adding a visible warning to the agent file is a one-line fix.
