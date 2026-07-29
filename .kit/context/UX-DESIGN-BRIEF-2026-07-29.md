# UX Design Brief — The Kit's Onboarding & Daily Flow

**For**: a Fable 5 design-session agent, working LIVE with Fredrik
(the operator) in this tab.
**Written by**: planner-f5, 2026-07-29.
**Your job**: co-design the ideal user experience. NOT to implement,
NOT to audit code, NOT to plan tasks — those come after, from your
deliverable.

## Session contract

- You are a design partner in conversation. Interview first, propose
  second, iterate with Fredrik until it feels right to him.
- Repo is READ-ONLY for you except ONE file: your deliverable at
  `.kit/context/ONBOARDING-UX-FLOW.md`. No other edits, no commits —
  the planner handles the repo.
- Design from the EXPERIENCE, not from the existing surfaces. You may
  propose flows that require deleting, merging, or inventing
  surfaces. Where a design step's technical feasibility is uncertain
  (can Claude Code do X?), mark it `[FEASIBILITY?]` in the deliverable
  and keep designing — the planner checks those later. Do not
  self-censor good UX because the current kit can't do it yet.

## What this thing is (60 seconds)

agentive-starter-kit (v0.9.0, just released) is a template + tooling
for running software projects WITH Claude Code agents: a planner
agent coordinates tasks, feature-developer agents implement in
isolated worktrees, adversarial evaluators and review bots gate
quality. A "setup door" (`scripts/local/bootstrap`) stamps out new
projects; an operator preset pre-answers its questions; a `doctor`
diagnoses environments; degraded modes let missing pieces report
instead of block. Users range from Fredrik (power operator, has
everything configured) to a stranger arriving from the GitHub README
with nothing installed.

## Why this session exists — the operator's verdicts, verbatim

- "Everything is backwards; we should tell the user what to do from
  the README, not ask them to guess how this works."
- "The user starts on the github page. They clone. They have to
  install lots of stuff. Finally, when Claude Code is running, they
  have to use arcane commands. We can and must do better, and lower
  the 'suck threshold' so every user gets to the plateau of
  productivity asap."
- "We need to start with the user experience and work from that."

## Evidence from yesterday's live cold-start test (5 snags)

1. A launched agent sat silent (sessions can't speak first under the
   current launcher), then answered "Are we ready?" as the WRONG
   persona (repo context beat agent identity).
2. Docs said "open a Claude Code session and run /X" — assuming the
   user knows slash-commands exist only inside sessions.
3. The intake flow demanded a "handoff brief" the user was never
   told to create.
4. A tool asked multiple-choice questions for free-text answers and
   errored.
5. Four competing entry surfaces (launcher menu, create-project
   agent, project-intake agent, /new-project command) with no stated
   hierarchy.

## Design material available (constraints ARE design tools)

- We fully control CLAUDE.md — the instructions every session in the
  repo loads. A session CAN be made to greet, orient, and drive from
  the very first user keystroke. (A session cannot literally speak
  before the user types anything.)
- Slash-commands, named agents, and skills exist inside sessions;
  shell scripts exist outside. The door + preset can create a full
  project non-interactively.
- Degraded modes + doctor mean NOTHING must be installed up front —
  installs can be deferred to the moment a step needs them, with a
  one-command remedy offered in place.
- The planner suspects the plateau can be: GitHub page → 2 shell
  lines → a conversation that does everything else. Treat that as a
  hypothesis to beat, not a spec.

## Suggested method (yours to adapt)

1. Interview Fredrik: who are the users (personas), what is each
   one's "plateau of productivity", what has annoyed him most.
2. Pick 2-3 journeys (suggested: stranger-with-nothing;
   prototyper-with-a-Cowork-session; Fredrik-with-preset).
3. Write each as a SCREENPLAY: every line the user sees, every
   keystroke they type, from GitHub page to first productive moment.
   Count the steps. This format is what makes the design testable.
4. Iterate the screenplays with Fredrik until he says done.
5. Deliverable: `.kit/context/ONBOARDING-UX-FLOW.md` — personas,
   final screenplays with step counts (vs. today's), the principles
   that emerged, `[FEASIBILITY?]` flags, and explicit non-goals.

## What happens with your deliverable

The planner turns it into an ADR (onboarding posture) + an
implementation task set, feasibility-checks your flags, and the
screenplays become the acceptance tests (a cold-start session must
be able to follow them verbatim). A related task (KIT-0078) is
deliberately ON HOLD awaiting your output.

## Addendum (2026-07-29, after the live ev-queue intake test)

Operator-established requirements — treat as design constraints:

1. **Two flow levels, one structure**: first-ever-run vs
   returning-user (prototype → proper project). Design the returning
   flow first; the structure must extend to first-run by PREPENDING
   an environment phase, not by being a different flow.
2. **Wizard posture**: every step says what's happening, asks exactly
   one thing, and previews what happens next. ("Maybe something a bit
   more wizard-like" — operator.)
3. **The handoff template instructs the exit**: its final section
   tells the PROTOTYPING agent to tell the user: put the brief + the
   most recent assets into ONE new folder somewhere Claude Code can
   access (e.g. ~/Github/<name>/), then what to say next. The
   template is the wizard's first step.
4. **One folder is the handoff unit** — never two paths. Proven in
   the live test ("I made a folder and said 'here it is' and things
   worked fine").
5. **Read before asking; ask at the informed moment**: the import
   wizard inventories the folder, plays back what it found (brief's
   self-identity vs folder name!), and asks the NAMING question
   there — the live test silently resolved a Varv-Playground vs
   ev-queue tension by derivation rule, which the operator wanted
   asked.
6. **Preview before execute**: show the plan (repos, visibility,
   backlog count) and confirm, then execute via subagent — the
   ev-queue experiment proved subagent execution works with zero
   permission stalls, so the tab-hop is optional; interactivity is
   the only thing the wizard must supply itself.
