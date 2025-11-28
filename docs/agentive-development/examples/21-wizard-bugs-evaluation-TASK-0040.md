# Example A/D Hybrid: Wizard Bug Discovery with Adversarial Evaluation

**Layers:** Augmentation (Evaluation) + Delegation (Agent Assignment)
**Pattern:** Using External GPT-4o Evaluator to Catch Bugs Before Wasted Implementation
**Task ID:** TASK-0040-BUGFIX
**Outcome:** Success - Evaluation corrected our misdiagnosis, saved 4-6 hours of wrong fixes

---

## Context: User Testing Revealed Show-Stopping Bugs

**The Situation (October 31, 2025):**

We'd just completed TASK-2025-0040 (Timeline Assembly Wizard state management). The implementation looked good:
- TypeScript compiled with no errors ✅
- Build succeeded ✅
- No runtime exceptions in dev mode ✅

User launched the wizard for first real testing session...

### User Reports (via Slack, 2:15 PM):

> "Step 1 isn't working. When I select 'DaVinci Resolve Timeline' and click Next, nothing happens. The button just sits there."
>
> "Also tried Step 2, the Browse button doesn't do anything when I click it. Is this ready for testing?"

**Our initial reaction:** 😰 Panic. The wizard was supposed to be functional for Stage 1 MVP testing.

**The emotional context:**
- Pressure: User was waiting to test
- Confusion: "It worked in my quick manual test!"
- Fear: "What if this is a fundamental React/Electron issue?"
- Temptation: "Let's just start debugging and fixing things!"

---

## The Issues: What We Thought vs. What Was Real

### Initial Bug Analysis (Wrong!)

**Our first diagnosis (10 minutes of debugging):**

```typescript
// In WizardContext.tsx:
const setExportFormat = (format: ExportFormat) => {
  dispatch({ type: 'SET_EXPORT_FORMAT', payload: format });
  // ⚠️ THEORY: Maybe dispatch() is async and Next validation runs too soon?
};
```

**Coordinator's hypothesis:**
> "BUG-1/2: This is a race condition. React setState is asynchronous, so when we call `setExportFormat('resolve')`, the state hasn't updated yet when the validation runs. We need to use useEffect or callback refs."

**Estimated fix time:** 2-3 hours (refactor state management pattern)

**The Problem With This Theory:**
We were **completely wrong**. React `setState` in Context API is NOT async like promises. But we were about to waste hours implementing a complex fix for a problem that didn't exist.

---

## Our Decision: Request Adversarial Evaluation

Instead of immediately starting implementation, the coordinator said:

> "Wait. Let's spend $0.04 to have GPT-4o review our bug analysis. If we're wrong about the race condition, we'll waste hours fixing the wrong thing."

### Evaluation Request

**Created:** `delegation/tasks/active/TASK-2025-0040-BUGS-IDENTIFIED.md`

**Sent to evaluator:**
```markdown
# Bug Analysis for Review

## Reported Issues
1. Step 1: "DaVinci Resolve Timeline" option doesn't advance to Step 2
2. Step 2: Browse button doesn't respond to clicks
3. Step 2: Paste and Clipboard tabs also non-responsive

## Our Diagnosis
BUG-1/2: State synchronization race condition
- setState is async, validation runs before state updates
- Need useEffect or callback pattern

Estimated fix: 2-3 hours (refactor state management)

## Question for Evaluator
Is this diagnosis correct? Are we missing something simpler?
```

**Ran evaluation:**
```bash
$ adversarial evaluate delegation/tasks/active/TASK-2025-0040-BUGS-IDENTIFIED.md
```

**Cost:** $0.02 (2.8k tokens)
**Time:** ~30 seconds

---

## Evaluator Response: You're Wrong

**Verdict:** NEEDS_REVISION
**Confidence:** HIGH (0.85/1.0)

**Evaluator's critique (paraphrased):**

> **CRITICAL CONCERN: Your race condition theory is incorrect.**
>
> React Context API `dispatch()` is NOT async like promises. State updates are synchronous within the React render cycle. Your "race condition" hypothesis doesn't match React's actual behavior.
>
> **The REAL bugs are simpler:**
>
> **BUG-1 (ACTUAL):** Step 1 validation array is missing 'resolve'
> ```typescript
> // In WizardContext.tsx line 125:
> ['json', 'aaf', 'both'].includes(state.exportFormat)
> //  ^^^ MISSING 'resolve' - but Step1 UI offers it!
> ```
>
> **BUG-2 (ACTUAL):** Missing IPC handlers for file operations
> ```typescript
> // Step2 calls window.electron.showOpenDialog()
> // But preload.ts doesn't define showOpenDialog!
> // Missing: showOpenDialog, readFile, readClipboard handlers
> ```
>
> **Fix time: 1 hour (not 2-3 hours)**
> - BUG-1: Add 'resolve' to array (5 minutes)
> - BUG-2: Add 4 IPC handlers (45 minutes)
>
> **Your race condition refactor would have:**
> - Taken 2-3 hours
> - Not fixed either bug
> - Added unnecessary complexity
> - Still left wizard broken

**Additional bugs found by evaluator:**
- BUG-3: Steps 5 & 6 also need IPC handlers (same issue)
- BUG-4: TypeScript type definitions missing for IPC methods

---

## The Correct Solution (Based on Evaluation)

### Fix 1: Validation Array (5 minutes)

**File:** `src/context/WizardContext.tsx`

```typescript
// BEFORE (BROKEN):
case 1:  // Step 1 validation
  return state.exportFormat !== null &&
         ['json', 'aaf', 'both'].includes(state.exportFormat);
         //  ^^^ User selected 'resolve', this returns FALSE

// AFTER (FIXED):
case 1:
  return state.exportFormat !== null &&
         ['resolve', 'json', 'aaf', 'both'].includes(state.exportFormat);
         //  ^^^ Now includes 'resolve' - matches UI options
```

**Why we missed this:**
- We were looking for "complex" problems (race conditions!)
- Didn't check the obvious (is the validation correct?)
- Fresh eyes (GPT-4o) saw the simple error immediately

### Fix 2: IPC Handlers (45 minutes)

**File:** `electron/preload.ts`
```typescript
contextBridge.exposeInMainWorld('electron', {
  // Existing methods...

  // NEW: File dialog operations
  showOpenDialog: (options: any) =>
    ipcRenderer.invoke('dialog:open', options),
  showSaveDialog: (options: any) =>
    ipcRenderer.invoke('dialog:save', options),

  // NEW: File system operations
  readFile: (path: string) =>
    ipcRenderer.invoke('fs:read', path),

  // NEW: Clipboard operations
  readClipboard: () =>
    ipcRenderer.invoke('clipboard:read'),
});
```

**File:** `electron/main.ts`
```typescript
// Add handlers for each IPC method
ipcMain.handle('dialog:open', async (_event, options) => {
  const result = await dialog.showOpenDialog(
    BrowserWindow.getFocusedWindow()!,
    options
  );
  return result;
});

ipcMain.handle('fs:read', async (_event, filePath: string) => {
  // Security: Validate file path
  const resolvedPath = path.resolve(filePath);

  // Check file size (max 10MB)
  const stats = await fs.stat(resolvedPath);
  if (stats.size > 10 * 1024 * 1024) {
    throw new Error(`File too large: ${stats.size} bytes`);
  }

  // Read as UTF-8
  const content = await fs.readFile(resolvedPath, 'utf-8');
  return content;
});

// ... other handlers ...
```

---

## The Results

### Time Comparison

**Without evaluation (our original plan):**
1. Implement race condition fix: 2-3 hours
2. Test it: 30 minutes
3. Realize it didn't fix the bugs: 😱
4. Debug again: 1-2 hours
5. Find the real bugs: 1 hour
6. Implement real fixes: 1 hour
7. **Total: 5.5-7.5 hours**

**With evaluation (what actually happened):**
1. Write bug analysis: 10 minutes
2. Request evaluation: 30 seconds ($0.02)
3. Read evaluation: 5 minutes
4. Implement correct fixes: 1 hour
5. Test: 15 minutes
6. **Total: 1 hour 25 minutes**

**Time saved:** 4-6 hours (78-84% faster)
**Cost of evaluation:** $0.02
**ROI:** ~250-400x return on investment

### Quality Comparison

**Our approach (without evaluation):**
- Would have added unnecessary complexity (callback refs, useEffect)
- Would have made codebase harder to maintain
- Would not have fixed the actual bugs
- Would have required second debugging round

**Evaluator-corrected approach:**
- Fixed actual bugs with minimal changes
- Added necessary IPC infrastructure
- Kept code simple (one-line validation fix)
- No technical debt introduced

---

## Lessons Learned: The Value of External Perspective

### 1. We Had "Expert Blindness"

**Our mental model:**
"React state is tricky, must be a state management issue"

**Reality:**
Simple typo in validation array

**Why this happened:**
- We were experts in React → looked for expert-level problems
- Missed the obvious → validation array doesn't match UI
- Fresh eyes (GPT-4o) aren't biased by expertise

**Key insight:** Sometimes beginners catch bugs experts miss because they check the obvious first.

### 2. Cost-Benefit of Evaluation is Lopsided

**Evaluation cost:** $0.02 (< 3 cents)
**Time saved:** 4-6 hours (our hourly rate × 4-6 hours = $$$)
**ROI:** Hundreds to thousands percent

**Even if evaluation is wrong:** It forces you to think through your assumptions.

**When evaluation is right:** It saves massive time and prevents bad code.

**Decision rule:** If task >1 hour and you're unsure, evaluate. The $0.02 is insurance.

### 3. Adversarial Review Catches Different Bugs

**Humans reviewing our code would likely:**
- Assume React knowledge is correct
- Trust our race condition diagnosis
- Review the proposed fix, not question the diagnosis

**GPT-4o evaluator:**
- Has no ego investment in our diagnosis
- Checks our assumptions against React docs
- Points out the simple error we missed

**Key difference:** Adversarial reviewers question your premises, not just your execution.

### 4. Evaluation Forces Clarity

Writing the bug analysis for evaluation made us:
- Document our assumptions
- State our hypothesis clearly
- Provide evidence for our theory

**This process revealed gaps:**
- "Do we actually know React setState is async in Context API?"
- "Have we checked the validation array?"
- "Wait, did we even test the Browse button in isolation?"

**Even if we hadn't sent it to GPT-4o,** writing it down would have helped.

### 5. Multi-Model Collaboration Works

**Claude (us) strengths:**
- Fast implementation
- Good at following patterns
- Integrates project context well

**Claude (us) weaknesses:**
- Can have confirmation bias
- Might miss simple errors
- Assumes expertise is correct

**GPT-4o (evaluator) strengths:**
- Fresh perspective
- Questions assumptions
- Systematic checking

**Pattern that emerged:**
- Claude does first-pass implementation and diagnosis
- GPT-4o reviews and critiques
- Claude implements corrected solution

This is **agentive development** in action - using multiple AI models for their different strengths.

---

## How Our Evaluation Practice Evolved

### Before This Task (Naive Approach)

**Our workflow:**
1. Identify bug
2. Guess solution
3. Implement
4. Test
5. If broken → repeat from step 2

**No evaluation step.** We trusted our first diagnosis.

### After This Task (Mature Approach)

**Our workflow:**
1. Identify bug
2. **Write analysis document** (forces clarity)
3. **If uncertain or complex: Request evaluation** ($0.02-0.08)
4. **Read evaluation critically** (agree/disagree with reasoning)
5. Implement corrected or confirmed solution
6. Test
7. If broken → evaluation may have missed something, escalate to human

**Evaluation is now a standard step for:**
- Bugs with unclear root cause
- Tasks estimated >2 hours
- Architectural decisions
- When we're unsure but feel pressure to "just fix it"

### Cultural Shift

**Before:**
- Evaluation felt like "extra work"
- "Just start coding and see what happens"
- Admitting uncertainty felt like weakness

**After:**
- Evaluation feels like "insurance"
- "Spend 5 minutes to save 5 hours"
- Requesting evaluation is good judgment, not weakness

**Coordinator now says:**
> "Before we implement, let's evaluate. I'd rather spend $0.08 than waste a Saturday debugging."

---

## Additional Discovery: Implementation Revealed More Bugs

Even after evaluation, implementation revealed issues:

**BUG-5 (Discovered during implementation):** Preload script module format
```
Error: Cannot use import statement outside a module
```

**Root cause:** Vite was compiling preload.ts to ES modules, but Electron requires CommonJS.

**Fix:** Update vite.config.ts to force CommonJS format for preload scripts.

**Time to fix:** 10 minutes (Googled error message)

**Why evaluation didn't catch this:** This is a build/runtime issue, not visible in code review.

**Lesson:** Evaluation catches logic bugs, not environment bugs. You still need to run the code!

---

## Applicable Domains

This evaluation pattern works especially well for:

### 1. User-Reported Bugs (Like This Example)
- Symptoms are clear, cause is uncertain
- Pressure to "fix it now" can lead to wrong solution
- Evaluation provides calm, systematic analysis

### 2. Cross-Framework Integration
- Electron + React (like us)
- Mobile + backend API
- Frontend + ML model
- When expertise spans multiple domains, blind spots emerge

### 3. Complex State Management
- React Context, Redux, MobX
- Async state updates
- Race conditions (real or imagined!)

### 4. Architecture Decisions
- "Should we refactor this?"
- "Is this pattern correct?"
- "Are we missing something obvious?"

**When NOT to use evaluation:**
- Trivial bugs with obvious causes (typos, syntax errors)
- Well-understood patterns (you've done this 100 times)
- Rapid prototyping (speed > correctness)

---

## Reflection Questions

1. **Why did we assume complexity (race condition) instead of checking simplicity (validation array)?**
   - Do experts have a bias toward complex problems?
   - How do we train ourselves to check obvious things first?

2. **Would a human code reviewer have caught this?**
   - Maybe, but would they have questioned our race condition theory?
   - Or would they have reviewed the race condition fix?

3. **When should we trust our intuition vs. request evaluation?**
   - If task >1 hour and confidence <80%, evaluate?
   - What's the decision threshold?

4. **How do we prevent "evaluation dependence"?**
   - Should we try to solve it first, then evaluate?
   - Or evaluate when uncertain, to avoid wasted work?

5. **What if evaluation had agreed with our wrong diagnosis?**
   - Would we have wasted 4-6 hours?
   - How do we handle evaluator errors?

6. **Is $0.02-0.08 per evaluation sustainable at scale?**
   - 100 tasks × $0.05 = $5
   - If each evaluation saves 2 hours, ROI is 400x
   - But psychologically, do we still balk at "paying for opinions"?

---

## Template: How to Request Evaluation for Bugs

Based on this experience, here's a template for bug evaluation requests:

```markdown
# Bug Evaluation Request: [Bug Description]

## Reported Symptoms
1. [What user reports or what we observe]
2. [Specific steps to reproduce]
3. [Expected vs actual behavior]

## Our Diagnosis
**Hypothesis:** [What we think is causing this]

**Evidence:**
- [Code snippet or behavior supporting hypothesis]
- [Log output or error messages]

**Proposed fix:** [What we plan to implement]
**Estimated time:** [X hours]

## Questions for Evaluator
1. Is our diagnosis correct?
2. Are we missing a simpler explanation?
3. Are there edge cases we haven't considered?
4. Is our proposed fix the right approach?

## Additional Context
[Relevant code files, framework versions, constraints]
```

**This forces clarity and helps evaluation be more effective.**

---

**Example Status:** Complete
**Task ID:** TASK-0040-BUGFIX
**Completion Date:** October 31, 2025
**Agents:** Coordinator (evaluation request) + Feature-developer (implementation)
**Evaluator:** GPT-4o (via Aider)
**Cost:** $0.02
**Time Saved:** 4-6 hours
**Documentation Date:** November 14, 2025

---

*This example shows real adversarial evaluation in action, including our misdiagnosis, the evaluator's correction, and the dramatic time savings. The bugs were real, the pressure was real, and the temptation to "just start coding" was real. Evaluation saved us from wasting a day on the wrong fix.*
