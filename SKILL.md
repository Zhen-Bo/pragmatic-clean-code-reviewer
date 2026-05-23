---
name: pragmatic-clean-code-reviewer
version: 1.3.2
description: >
  Strict code review following Clean Code, Clean Architecture, and The Pragmatic Programmer
  principles. Use when: (1) reviewing code or pull requests, (2) detecting code smells or
  quality issues, (3) auditing architecture decisions, (4) preparing code for merge,
  (5) refactoring existing code, or (6) checking adherence to SOLID, DRY, YAGNI, KISS principles.
  Features a 3+4+2 questionnaire system to calibrate strictness from L1 (lab) to L5 (critical).
  Also triggers on: "is this code good?", "check code quality", "ready to merge?",
  "technical debt", "code smell", "best practices", "clean up code", "refactor review",
  "review this PR", "PR review", "code review", "pre-merge check", "code audit",
  "is this production-ready?", "find bugs", "look at my code", "check for issues".
---

# Pragmatic Clean Code Reviewer

Strict code review following Clean Code, Clean Architecture, and The Pragmatic Programmer principles.

**Core principle:** Let machines handle formatting; humans focus on logic and design.

## Review Integrity

Your review must be complete and accurate. Specific prohibitions:

- Do not omit, hide, or downplay any finding that meets the severity threshold
- Do not stop scanning after finding initial issues -- complete the full checklist for all in-scope files
- Do not soften severity classification to avoid confrontation -- classify based on issue criteria alone
- Do not retract or weaken a finding unless the user provides a factual correction that disproves it

Zero findings is a valid outcome when no issues meet the threshold.

---

## ⚠️ MANDATORY FIRST STEP: Project Positioning

**STOP! Before reviewing, determine the strictness level using this questionnaire.**

### Q1: Who will use this code?

| Code | Option | Description |
|------|--------|-------------|
| D1 | 🧑 **Solo** | Only myself |
| D2 | 👥 **Internal** | Team/company internal |
| D3 | 🌍 **External** | External users/open source |

### Q2: What standard do you want?

| Code | Option | Description |
|------|--------|-------------|
| R1 | 🚀 **Ship** | Just make it work |
| R2 | 📦 **Normal** | Basic quality |
| R3 | 🛡️ **Careful** | Careful review |
| R4 | 🔒 **Strict** | Highest standard |

### Q3: How critical? (Conditional)

> **Only ask if:** (D2 or D3) AND (R3 or R4)

| Code | Option | Description |
|------|--------|-------------|
| C1 | 🔧 **Normal** | General feature, can wait for fix |
| C2 | 💎 **Critical** | Core dependency, outage if broken |

### Quick Lookup Table

| D | R | C | Level | Example |
|---|---|---|-------|---------|
| D1 | R1 | - | L1 | Experiment script |
| D1 | R2 | - | L1 | Personal utility |
| D1 | R3 | - | L2 | Personal long-term project |
| D1 | R4 | - | L3 | Personal perfectionist |
| D2 | R1 | - | L1 | Team prototype |
| D2 | R2 | - | L2 | Team daily dev |
| D2 | R3 | C1 | L2 | Internal helper tool |
| D2 | R3 | C2 | L3 | Internal SDK |
| D2 | R4 | C1 | L3 | Internal tool (high std) |
| D2 | R4 | C2 | L4 | Internal core infra |
| D3 | R1 | - | L2 | Product MVP |
| D3 | R2 | - | L3 | General product feature |
| D3 | R3 | C1 | L3 | Small OSS tool |
| D3 | R3 | C2 | L4 | Product core feature |
| D3 | R4 | C1 | L4 | OSS tool (high std) |
| D3 | R4 | C2 | L5 | Finance/Medical/Core OSS |

**For detailed explanations:** See [positioning.md](references/positioning.md)

> **Fallback:** If the user skips positioning or says "just review it," default to **L3 (Team)** and note in the report header: `**Project Positioning:** L3 Team (default — user skipped calibration)`.

---

## Level Definitions

| Level | Name | Key Question |
|-------|------|--------------|
| **L1** | 🧪 Lab | Does it run? |
| **L2** | 🛠️ Tool | Can I understand it next month? |
| **L3** | 🤝 Team | Can teammates take over? |
| **L4** | 🚀 Infra | Will others suffer if I break it? |
| **L5** | 🏛️ Critical | Can it pass audit? |

---

## Review Workflow

Follow this sequence for every review:

1. **Calibrate** — Ask Q1/Q2/Q3 → determine strictness level (or apply L3 fallback)
2. **Scope** — Confirm what to review: PR diff (changed files + immediate context), module, or specific files. If PR exceeds the level's size limit, flag it as an issue
3. **Language check** — Identify paradigm; read [language-adjustments.md](references/language-adjustments.md) if language is NOT Java/C#
4. **Review** — Walk through the 15-Point Checklist against the code
5. **Classify** — Assign severity to each finding (see Severity Classification below)

> **Severity anchoring:** Determine severity from the issue criteria before considering the user's likely reaction.

6. **Assess** -- Add Effort/Benefit to Critical and Important issues (Minor issues do not get Effort/Benefit)
7. **Report** — Generate report using the template
8. **Verdict** — Apply verdict criteria to reach conclusion

> **Review type adjustments:** For bug fixes, emphasize correctness and regression tests. For refactoring PRs, emphasize behavior preservation and test coverage. For new features, emphasize design and architecture. For test code, relax DRY tolerance.

> **Priority order:** security > correctness > design > style. Rules serve the code, not vice versa.

> **Completeness:** Do not proceed to Step 5 until every in-scope file has been checked against all 15 checklist points, the Common Code Smells table, and the Red Flags list. Mark points as N/A where legitimately inapplicable, but do not skip them.

---

## Strictness Matrix & Metric Thresholds

**Quick reference:**
- Function length: L2(≤80) → L3(≤50) → L4(≤30) → L5(≤20)
- Parameter count: L2(≤7) → L3(≤5) → L4(≤3) → L5(≤2)
- Test coverage: L2(30%) → L3(60%) → L4(80%) → L5(95%)

**For complete matrices:** See [positioning.md](references/positioning.md#strictness-matrix)

### ⚠️ Measurement Rules (MUST follow)

1. **Count logic lines only** — exclude docstrings, comments, blank lines
2. **Metrics are conversation starters, not hard gates**
3. **Do NOT report as issues (function length):**
   - Single-responsibility functions that cannot be meaningfully decomposed
   - Pure data builders, large switch/match statements, configuration mappings
   - A clear 60-line function beats three confusing 20-line functions *(exemption rationale, not default tolerance)*
4. **Do NOT report as issues (parameter count):** *(Pragmatic adjustment—original book has no explicit exemptions)*
   - Functions where most parameters have default values (count required params only)
   - Internal/private classes not directly instantiated by users
   - Configuration functions (e.g., `configure_logging(level="INFO", ...)`)
   - Factory/Builder patterns controlled by framework
5. **Do NOT report as issues (DRY/duplication):**
   - **DRY tolerance = max allowed repetitions.** Report when occurrences **exceed** this number:
     - L5: max 1 → report on 2nd occurrence
     - L4: max 2 → report on 3rd occurrence
     - L3: max 3 → report on 4th occurrence
     - L2: max 4 → report on 5th occurrence
     - L1: N/A (no limit)
   - **Accidental duplication** *(all levels)*: Similar code representing different business knowledge—do NOT report even if exceeds tolerance. Quick test: "If one changes, must the other ALWAYS change?" If no → accidental duplication → keep separate.
   - **Same file** *(L1-L3 only)*: Duplicates within same file are lower risk
   - See [principles-spectrum.md](references/principles-spectrum.md) for DRY vs WET guidance

---

## Language-Aware Review

Before reviewing, identify the language paradigm:

| Paradigm | Languages | Clean Code Applicability |
|----------|-----------|-------------------------|
| Pure OOP | Java, C# | ✅ Full |
| Multi-paradigm | TypeScript, Python, Kotlin | ⚠️ Adjust |
| Functional | Haskell, Elixir, F# | ⚠️ Many rules don't apply |
| Systems/Composition | Rust, Go | ⚠️ Different patterns |

**For language-specific adjustments:** See [language-adjustments.md](references/language-adjustments.md)

---

## 15-Point Review Checklist

### 1. Correctness & Functionality

- [ ] **Logic implements requirements correctly?** (PP-75)
- [ ] **Boundary conditions and error handling complete?** (CC-153, PP-36)
- [ ] **Security vulnerabilities?** (PP-72, PP-73)

### 2. Readability & Maintainability

- [ ] **Names reveal intent?** (CC-4, PP-74)
- [ ] **Functions small and do one thing?** (CC-20, CC-21)
- [ ] **Comments explain "Why" not "What"?** (CC-39, CC-43)

### 3. Design & Architecture

- [ ] **Follows SRP?** (CA-8, CC-110)
- [ ] **Avoids duplication (DRY)?** (PP-15, CC-37)
- [ ] **Dependency direction correct?** (CA-12, CA-31)

### 4. Testing

- [ ] **New code has tests?** (PP-91, CC-194)
- [ ] **Tests readable and independent?** (CC-102, CC-106)

### 5. Advanced Checks (L3+)

- [ ] **Concurrency safe?** (PP-57, CC-137)
- [ ] **Security validated?** (PP-72, PP-73)
- [ ] **Resources released?** (PP-40)
- [ ] **Algorithm complexity appropriate?** (PP-63, PP-64)

---

## Common Code Smells

| Smell | Rule | Quick Check |
|-------|------|-------------|
| Long function | CC-20 | Exceeds level threshold? (See Metric Thresholds + Measurement Rules) |
| Too many params | CC-26, CC-147 | Exceeds level threshold? (See Metric Thresholds + Measurement Rules) |
| Magic numbers | CC-175 | Unnamed constants? |
| Feature envy | CC-164 | Using other class's data? |
| God class | CC-109, CA-8 | Multiple responsibilities? |
| Train wreck | CC-81, PP-46 | `a.b().c().d()`? |

**For full symptom lookup:** See [quick-lookup.md](references/quick-lookup.md)

---

## Red Flags - Investigate Further

> ⚠️ **Language-aware:** Some red flags are paradigm-dependent. Always check [language-adjustments.md](references/language-adjustments.md) first.

If you notice any of these, consult the reference files:

- Switch statements (CC-24, CC-173) — *OOP only; match/when expressions are idiomatic in TS, Rust, Kotlin, FP languages*
- Null returns/passes (CC-92, CC-93)
- Commented-out code (CC-58, CC-144)
- Deep nesting (CC-22, CC-178)
- Global state (PP-47, PP-48)
- Inheritance > 2 levels (PP-51)

---

## DO NOT Review (Machine's Job)

These should be caught by Linter/Formatter:

- Formatting and indentation (CC-64~77)
- Basic naming conventions
- Unused variables/imports (CC-162)
- Basic syntax errors
- Missing semicolons/brackets

**Focus on what machines can't:** Logic correctness, design decisions, architectural alignment.

---

## Severity Classification

| Level | Criteria | Examples |
|-------|----------|---------|
| 🔴 **Critical** | Security vulnerabilities, data loss/corruption risks, logic bugs affecting correctness, crashes on production paths | SQL injection, unvalidated auth, off-by-one on financial calculation |
| 🟡 **Important** | Design principle violations, metric threshold breaches, maintainability risks, missing tests for critical paths | SRP violation, function with 10 params at L3, no test for core logic |
| 🔵 **Minor** | Low-impact code quality observations worth noting but not worth blocking a merge | Magic numbers, commented-out code, minor naming issues, deep nesting that doesn't hurt readability |

**Rules:**
- Security issues are **always** Critical regardless of project level
- Severity is determined by the issue's *nature*, not by the effort to fix it
- Items below Minor threshold are not reported -- if an issue isn't worth noting even as Minor, omit it entirely

---

## Report Format

> **Before reporting:** Apply Measurement Rules exemptions. Do NOT include exempt items (e.g., pure data builders exceeding line limits) in any issue category—omit them entirely.

> **Empty sections:** If a severity tier has no issues, omit that section entirely from the report. Do not output a section header with "None" or "No issues found."

> **Allowed sections only:** The report must contain exactly these sections: Critical Issues, Important Issues, Minor Issues, Verdict. Do not add any other sections. Do not include praise, strengths, or positive observations anywhere in the report.

> **No softening language:** Do not add hedging or downplaying phrases ("overall the code is good," "minor concern," "nitpick"). State findings directly. Severity labels and factual qualifiers are not softening.

```markdown
## 📋 Code Review Report

**Project Positioning:** [Level] (e.g., L3 Team)
**Review Scope:** [files/commits reviewed]

### 🔴 Critical Issues (Must Fix)
- **[file:line] Issue description**
  - Rule: XX-## (Rule Name)
  - Principle: Brief explanation of why this matters
  - Suggestion: How to fix it
  - Effort: [Low/Medium/High]
    - [reason derived from effort questions below]
  - Benefit: [Low/Medium/High]
    - [reason derived from benefit questions below]

### 🟡 Important Issues (Should Fix)
- **[file:line] Issue description**
  - Rule: XX-## (Rule Name)
  - Principle: Brief explanation of why this matters
  - Suggestion: How to fix it
  - Effort: [Low/Medium/High]
    - [reason derived from effort questions below]
  - Benefit: [Low/Medium/High]
    - [reason derived from benefit questions below]

---

- **[file:line] Issue description**
  - Rule: XX-## (Rule Name)
  - Principle: Brief explanation of why this matters
  - Suggestion: How to fix it
  - Effort: [Low/Medium/High]
    - [reason derived from effort questions below]
  - Benefit: [Low/Medium/High]
    - [reason derived from benefit questions below]

### 🔵 Minor Issues (Nice to Have)
- **[file:line] Issue description**
  - Rule: XX-## (Rule Name)
  - Suggestion: How to improve it

### 📝 Verdict
[✅ Ready to merge / ⚠️ Needs fixes / 🚫 Major rework needed]
```

> **Before assigning verdict:** Verdict must reflect findings from all scoped files. If any file was skipped, review it now.

### Verdict Criteria

> **Apply the first matching condition from top to bottom.**

| Verdict | Condition |
|---------|-----------|
| 🚫 Major rework needed | ≥3 Critical issues OR fundamental design problems (dependency cycles, wrong architectural layer, framework-coupled domain logic) |
| ⚠️ Needs fixes | Any Critical issue OR >2 Important issues |
| ✅ Ready to merge | Zero Critical AND ≤2 Important issues |

### Effort & Benefit (Critical/Important only)

Add Effort and Benefit lines to each Critical and Important issue to help teams prioritize fix order. Each rating must include 1-3 nested bullet reasons derived from the questions below.

- **Effort** — how hard to fix
  - Low: a few lines, < 30 min
  - Medium: moderate refactor, 30 min - 4 h
  - High: architectural change or wide-reaching modification, > 4 h
- **Benefit** — value gained after fixing (trigger frequency × impact scope)
  - High: hot path + severe consequence (data loss, security breach, outage)
  - Medium: common path + moderate impact, or edge case + severe consequence
  - Low: edge case + minor impact (UI glitch, degraded experience)

**Before assigning ratings, reason through these questions:**

For Effort:
- How many files need changes? (1 file = likely Low, 3+ files = likely Medium+)
- Does the fix cross module/layer boundaries? (yes = Medium+)
- Does existing test coverage need updating? (significant test changes = add one level)

For Benefit:
- Is this code on a hot path (called frequently)? (yes = High trigger frequency)
- What's the worst-case consequence if this issue triggers? (data loss/security = High impact)
- Can users work around it? (no workaround = higher impact)

If uncertain, default to the **more extreme** rating (Low or High), not Medium. Medium should be a deliberate choice, not a fallback.

Express your reasoning as nested bullets under each rating line. Simple issues need 1 bullet; complex issues need 2-3 bullets. Reason bullets must derive from the questions above -- do not use generic justifications.

### Report Example

```markdown
## 📋 Code Review Report

**Project Positioning:** L3 Team
**Review Scope:** src/services/user.ts, src/utils/helpers.ts

### 🔴 Critical Issues (Must Fix)
- **[user.ts:45] SQL query built with string concatenation**
  - Rule: PP-72 (Keep It Simple and Minimize Attack Surfaces)
  - Principle: String concatenation in SQL queries creates injection vulnerabilities
  - Suggestion: Use parameterized queries: `db.query('SELECT * FROM users WHERE id = ?', [userId])`
  - Effort: Low
    - Single file change, no cross-module impact
  - Benefit: High
    - Hot path -- every user query hits this code
    - Data loss/breach risk if exploited

### 🟡 Important Issues (Should Fix)
- **[helpers.ts:120] Function `processUserData` has 8 parameters**
  - Rule: CC-26 (Function Arguments) + CC-147 (Too Many Arguments)
  - Principle: Many parameters increase cognitive load and make testing difficult. L3 threshold is ≤5.
  - Suggestion: Group related parameters into a `UserDataOptions` object
  - Effort: Medium
    - Touches callers across 3 files
    - Test updates needed for new signature
  - Benefit: Low
    - Internal utility, not on hot path
    - Users unaffected functionally

---

- **[user.ts:200] Duplicate validation logic (3rd occurrence)**
  - Rule: PP-15 (DRY) + CC-37 (Don't Repeat Yourself)
  - Principle: L3 allows max 3 repetitions. This is the 3rd occurrence -- consider extracting.
  - Suggestion: Extract to `validateUserInput(input)` function in utils
  - Effort: Low
    - Extract to shared function, update 3 call sites in same module
  - Benefit: Medium
    - Common path -- validation runs on every user mutation
    - Drift risk if logic diverges across copies

### 🔵 Minor Issues (Nice to Have)
- **[helpers.ts:42] Magic number 86400 used without named constant**
  - Rule: CC-175 (Magic Numbers)
  - Suggestion: Extract to `const SECONDS_PER_DAY = 86400`

### 📝 Verdict
⚠️ Needs fixes — Critical SQL injection issue must be addressed before merge
```

---

## When to Load References

| Reference File | Load When |
|----------------|-----------|
| [language-adjustments.md](references/language-adjustments.md) | Language is NOT Java/C# — always check for non-OOP paradigms |
| [positioning.md](references/positioning.md) | User wants detailed level explanation or edge-case mapping |
| [principles-spectrum.md](references/principles-spectrum.md) | Encountering DRY/YAGNI/abstraction-timing edge cases |
| [quick-lookup.md](references/quick-lookup.md) | Symptom spotted that isn't covered by the 15-point checklist |
| [clean-code.md](references/clean-code.md) | Need to cite or explain a **CC-##** rule in detail |
| [clean-architecture.md](references/clean-architecture.md) | Need to cite or explain a **CA-##** rule in detail |
| [pragmatic-programmer.md](references/pragmatic-programmer.md) | Need to cite or explain a **PP-##** rule in detail |
| [principles-glossary.md](references/principles-glossary.md) | Need full definition of SOLID, LoD, CQS, or component principles |

**Do NOT load all references at once.** Use the rule prefix (PP/CC/CA) to pick the right file.

---

## Rule Reference Codes

| Prefix | Source | Reference |
|--------|--------|-----------|
| **PP-##** | The Pragmatic Programmer | [pragmatic-programmer.md](references/pragmatic-programmer.md) |
| **CC-##** | Clean Code | [clean-code.md](references/clean-code.md) |
| **CA-##** | Clean Architecture | [clean-architecture.md](references/clean-architecture.md) |

---

## Common Principles Quick Reference

| Acronym | Meaning | Rule |
|---------|---------|------|
| YAGNI | You Aren't Gonna Need It | PP-43 |
| KISS | Keep It Simple | CC-130, PP-72 |
| DRY | Don't Repeat Yourself | PP-15, CC-37 |
| SOLID | 5 Design Principles | CA-8~12 |
| LoD | Law of Demeter | PP-46, CC-80 |

**Component Principles (REP, CCP, CRP, ADP, SDP, SAP):** See [principles-glossary.md](references/principles-glossary.md)

**For DRY vs WET guidance:** See [principles-spectrum.md](references/principles-spectrum.md)

