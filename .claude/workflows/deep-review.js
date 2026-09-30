// Tier-3 deep review — KIT-0116 FR-10.
//
// OPT-IN ONLY (FR-11): this workflow runs solely on an explicit human
// request per the Escalation contract in
// .kit/context/workflows/REVIEW-PIPELINE.md. The implementing agent
// never self-escalates to it. Invocation and evidence rules live in
// that contract — this file is the mechanism, not the policy.
//
// Shape: one scope agent maps the diff; three lenses (correctness,
// architecture-vs-kit-conventions, security) review it in a pipeline;
// every finding is adversarially verified refute-first before it may
// surface; plain code then filters to confirmed findings and counts
// refutations (cross-lens DUPLICATES are the persisting session's job
// to notice at triage — the contract says so). Agent budget is capped
// at MAX_AGENTS = 1 + LENSES.length * (1 + PER_LENS_CAP) = 13, inside
// the medium size guideline; capped drops are logged, never silent.
//
// Toolset note: these stages are ordinary Workflow-tool agents running
// with session permissions — NOT the KIT-ADR-0036 read-only reviewer
// roster. That ADR governs Agent-tool reviewer spawns; Workflow stages
// may run git reads because a Tier-3 run is operator-invoked and
// session-scoped. If a run ever hits a permission wall on git, pass
// the diff content in via args instead and file the observation.
//
// args: { taskId: "KIT-NNNN", base: "main" } — both optional
// (base defaults to main; taskId is used for labeling and the
// evidence record the caller writes afterwards).

export const meta = {
  name: 'deep-review',
  description: 'Tier-3 multi-lens diff review with refute-first adversarial verification (KIT-0116)',
  whenToUse: 'ONLY on explicit human opt-in per REVIEW-PIPELINE.md Escalation — never a default gate, never agent-initiated.',
  phases: [
    { title: 'Scope', detail: 'map the branch diff against base' },
    { title: 'Review', detail: 'correctness / architecture / security lenses in parallel' },
    { title: 'Verify', detail: 'one refute-first check per finding' },
  ],
}

const taskId = (args && args.taskId) || 'UNLABELED-TASK'
const base = (args && args.base) || 'main'
const PER_LENS_CAP = 3

const SCOPE_SCHEMA = {
  type: 'object',
  required: ['files', 'summary'],
  properties: {
    files: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
}

const FINDINGS_SCHEMA = {
  type: 'object',
  required: ['findings'],
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        required: ['file', 'title', 'claim', 'severity'],
        properties: {
          file: { type: 'string' },
          line: { type: 'integer' },
          title: { type: 'string' },
          claim: { type: 'string' },
          severity: { enum: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] },
        },
      },
    },
  },
}

const VERDICT_SCHEMA = {
  type: 'object',
  required: ['refuted', 'reason'],
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
}

phase('Scope')
const scope = await agent(
  `You are scoping a Tier-3 deep review for task ${taskId}. ` +
    `Run: git diff ${base}...HEAD --stat and git diff ${base}...HEAD --name-only. ` +
    `Return JSON: files = the changed-file list; summary = a 5-10 line ` +
    `structural description of what the diff does (subsystems touched, ` +
    `new vs modified, code vs instruction surfaces). Your final output ` +
    `is data for sibling reviewers, not a human-facing message.`,
  { schema: SCOPE_SCHEMA, label: 'scope' }
)

// Same null semantics as the lens stages: a scope agent that dies on a
// terminal error yields null — fail the run loudly rather than TypeError.
if (!scope) {
  throw new Error(
    `deep-review ${taskId}: scope agent returned no result — ` +
      'aborting before any lens fan-out (re-run, or pass the diff via args)'
  )
}

if (scope.files.length === 0) {
  log(
    `deep-review ${taskId}: empty diff vs ${base} — nothing to review, ` +
      'ending without fan-out (13-agent budget unspent)'
  )
  return { taskId, base, scope: scope.summary, confirmed: [], refutedCount: 0 }
}

const LENSES = [
  {
    key: 'correctness',
    prompt:
      'Review for CORRECTNESS: logic errors, broken edge cases, ' +
      'contract violations between the changed files, tests that pin ' +
      'the wrong behavior. Ignore style.',
  },
  {
    key: 'architecture',
    prompt:
      'Review for KIT-CONVENTION ARCHITECTURE: read ' +
      '.kit/context/patterns.yml, .kit/context/workflows/REVIEW-PIPELINE.md ' +
      'and any ADRs the diff touches FIRST; then find single-authority ' +
      'violations (KIT-0101 R5), twin/mirror drift, boundary leaks, and ' +
      'pattern re-derivations. Ground every finding in a named decision.',
  },
  {
    key: 'security',
    prompt:
      'Review for SECURITY: injection via interpolated values, ' +
      'fail-open gates, secrets handling, permission-boundary widening ' +
      '(especially agent toolsets vs KIT-ADR-0036).',
  },
]

const lensPrompt = (lens) =>
  `Tier-3 ${lens.key} lens for task ${taskId}, branch diff vs ${base}. ` +
  `Diff summary from the scope pass: ${scope.summary} ` +
  `Changed files: ${scope.files.join(', ')}. ` +
  `Read the files from the working tree (run git diff ${base}...HEAD -- <file> ` +
  `for hunk context where needed). ${lens.prompt} ` +
  `Report at most ${PER_LENS_CAP} findings — your strongest, ranked; ` +
  `each with file, line where known, a one-line title, the precise claim, ` +
  `and severity. No filler findings: fewer is fine, zero is fine.`

const refutePrompt = (f, lens) =>
  `Adversarially verify this Tier-3 ${lens} finding for ${taskId} — your job ` +
  `is to REFUTE it. Finding: [${f.severity}] ${f.title} @ ${f.file}` +
  (f.line ? `:${f.line}` : '') +
  `. Claim: ${f.claim} ` +
  `Read the actual file(s) in the working tree and check the claim against ` +
  `what is really there. Default to refuted=true if the evidence is ` +
  `ambiguous or the claim rests on assumed content. reason = the decisive ` +
  `evidence, one or two sentences, citing file:line.`

const results = await pipeline(
  LENSES,
  (lens) =>
    agent(lensPrompt(lens), {
      schema: FINDINGS_SCHEMA,
      phase: 'Review',
      label: `review:${lens.key}`,
    }).then((r) => ({ lens: lens.key, findings: r.findings })),
  (review) => {
    // agent() returns null when a run is skipped mid-flight or dies on
    // a terminal API error — the pipeline hands that null to the next
    // stage, so this guard is live, not defensive decoration.
    if (!review) return null
    const kept = review.findings.slice(0, PER_LENS_CAP)
    if (kept.length === 0) return [] // clean lens — nothing to verify
    if (review.findings.length > kept.length) {
      log(
        `deep-review: ${review.lens} lens returned ` +
          `${review.findings.length} findings; verifying the top ` +
          `${kept.length} (cap) — dropped titles: ` +
          review.findings
            .slice(PER_LENS_CAP)
            .map((f) => f.title)
            .join(' | ')
      )
    }
    return parallel(
      kept.map((f) => () =>
        agent(refutePrompt(f, review.lens), {
          schema: VERDICT_SCHEMA,
          phase: 'Verify',
          label: `verify:${review.lens}:${f.file.split('/').pop()}`,
        }).then((v) => ({ ...f, lens: review.lens, verdict: v }))
      )
    )
  }
)

const verified = results
  .filter(Boolean)
  .flat()
  .filter(Boolean)
const confirmed = verified.filter((f) => f.verdict && f.verdict.refuted === false)
const refuted = verified.length - confirmed.length

log(
  `deep-review ${taskId}: ${confirmed.length} confirmed / ${refuted} refuted ` +
    `across ${verified.length} verified findings`
)

// The CALLER persists this into the review-pass record's deep-review
// section per the Escalation contract — the workflow leaves data.
return {
  taskId,
  base,
  scope: scope.summary,
  confirmed,
  refutedCount: refuted,
}
