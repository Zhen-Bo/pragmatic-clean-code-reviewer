---
name: pragmatic-clean-code-reviewer
description: >
  Review changed code for contract and safety risks, architecture, maintainability, testing,
  and operational concerns using calibrated severity and explicit coverage accounting. Use for
  code review, architecture review, design review, maintainability review, refactor review, or
  merge-readiness assessment. Also triggers on: "review this PR", "pre-merge check",
  "code audit", "technical debt", "code smell", "is this production-ready?", "ready to merge?",
  "check code quality", "is this code good?", "clean up code", "best practices".
license: MIT
metadata:
  version: 2.0.0
---

# Pragmatic Clean Code Reviewer

## Purpose and Review Boundary

**Priority order:** security > correctness > design > style.

**Bounded correctness.** Report a defect only when a concrete code path in the reviewed
scope evidences it; speculative bugs are not findings.

**Not a substitute** for fuzzing, formal verification, a security audit, or
framework-specific static analysis.

**Do not review — the machine's job.** Formatting, indentation, naming conventions, unused
variables and imports, syntax errors, missing semicolons: linter territory.

## Review Integrity

A review is complete only when every in-scope file is in the Scope Manifest, every required
ledger cell is accounted for, all whole-scope checks are done, and every finding is
reconciled.

User-named principles are emphasis, never scope. Check every active checklist point even when
the user mentions only KISS, DRY, SOLID, or security; tag findings caused by the user's
emphasis `[user-emphasis]`.

Search hits, diff hunks, summaries, and remembered context do not qualify as checked. Never
mark a cell `Pass` without checking.

A findings-only response is invalid. If scope, context, or tool limits prevent completion,
report the completed work honestly, use `⛔ Review incomplete`, and issue no merge-readiness
verdict.

Do not omit, hide, or downplay a finding that meets its threshold; do not soften severity to
avoid confrontation; do not retract a finding without a factual correction that disproves it.
Anchor severity to the issue criteria, not the user's reaction. Zero findings is a valid
outcome.

## Profile Discovery and Calibration

Check `docs/code-review-profile.md`, then `.code-review-profile.md`; if both exist, use the
`docs/` copy and disclose the duplicate. Precedence: explicit session instruction > valid
profile > questionnaire answers > disclosed L3 fallback. Profile settings may change
thresholds and emphasis but may never disable mandatory points, completeness accounting,
evidence requirements, or Critical findings.

**Profile level conflict.** If a profile's `level` disagrees with the level derived from
D/R/C, the effective level is the STRICTER candidate — never fall back to L3. Header shows
both candidates: `profile conflict: stricter level selected`. Emit one Important
`[PROJECT:SCOPE]` governance finding (`Point: A1`). Keep profile exclusions; revalidate every
waiver and threshold override against the effective level (approver, expiry, scope, numeric
caps) — suspend entries that fail, keep valid ones. Never rewrite the profile without
consent; repeat the disclosure until the stored conflict is corrected.

**Stale profile.** `last_confirmed` older than 180 days, `skill_major` mismatch, or
`dominant_language` mismatch. Use the stored values, label the header source `(stale)`, ask
ONE non-blocking confirmation question, and never block the review.

**Questionnaire.** Q1 audience: D1 solo · D2 internal · D3 external. Q2 standard: R1 ship ·
R2 normal · R3 careful · R4 strict. Q3 criticality (C1 normal · C2 critical) is asked only
when (D2 or D3) and (R3 or R4). Load [positioning.md](references/positioning.md) before
deriving or validating a level — it holds the questionnaire and the canonical D/R/C→level
table.

Offer ONCE to save the answers as a profile; never write one without explicit consent, and
never into this skill's own repository. If the user skips calibration, apply the L3 fallback,
disclose it, and never persist a guess.

## Scope Manifest

```markdown
- Basis: `user-specified | changed-files | glob` · In scope: N · Excluded: M
- Review level: Lx · Profile source: path, questionnaire, or L3 fallback

| # | File | LOC | Language/Paradigm | Status |
|---|------|----:|-------------------|--------|
| 1 | path | 120 | TypeScript/OOP    | DONE   |

### Exclusions

| Path | Reason |
|------|--------|
| path | generated |
```

**Stage 1** — before any content review: enumerate every path, exclusion, language,
`Status: PENDING`, `LOC: —`. Estimated LOC is for batch planning only and must be labelled
`estimate`. No finding may be drafted before Stage 1 is complete.
**Stage 2** — after each batch is read in full: re-emit changed rows with exact LOC from the
opened file and `DONE` or `PARTIAL`.

- Unspecified scope defaults to the changed files.
- Default exclusions: generated files, vendored code, lockfiles, minified output, build
  output, snapshots, binaries. Migrations stay in scope unless explicitly excluded.
- `Status` is `PENDING`, `DONE`, `PARTIAL`, or `EXCLUDED`.
- Exclusions may never silently remove a file the user named.

## Review Protocol

Each phase is a hard gate.

0. **Calibrate.** Discover the profile or run the questionnaire; fix the level.
1. **Enumerate.** Emit the Stage 1 manifest. Never review an unenumerated scope.
2. **Read.** Read each in-scope file in full.
3. **Review.** Immediately after each file, emit its Coverage Ledger row. Never batch rows
   to the end.
4. **Whole-scope checks.** C1 cohesion, C2 duplication clusters, C3 dependency direction,
   and scope/PR size across the whole manifest.
5. **Write findings.** Every finding carries one `Point:` and at least one ledger reference.
6. **Reconcile.** Emit the Coverage Reconciliation block.
7. **Verdict.** Apply the verdict gates.

**Review-type adjustments.** Bug fix: regression tests. Refactor: behavior preservation. New
feature: design. Test code: relaxed DRY. A request for "short output" shortens findings,
never the accounting.

### Batching

Batch when scope exceeds 8 files or 1,500 estimated LOC. A batch holds at most 5 files and
at most 600 estimated LOC, whichever comes first; a single file over 600 LOC forms its own
batch. After each batch, update its manifest rows, ledger rows, and a one-line
batch reconciliation, then continue WITHOUT asking. If remaining context cannot hold another
complete batch, stop at the boundary and issue `⛔ Review incomplete`; never compress the
last batch.

## Nineteen-Point Review Checklist

Closed taxonomy: every finding maps to exactly one point; if none fits, use the nearest,
never a new category. Domains: **A** Contract & Safety · **B** Readability ·
**C** Design & Architecture · **D** Testing · **E** Performance & Operability.

- **A1 Contract integrity** — implementation honors the contract its name, signature, docs,
  and tests advertise. (CC-152, CC-170, PP-62)
- **A2 Boundaries, errors, and concrete logic paths** — boundary validation, failure
  behavior, error propagation; cues: unhandled boundary, swallowed error, null in or out.
  (CC-153, PP-36, CC-86~93)
- **A3 Security and secrets** — injection, authn/authz, hardcoded credentials, unsafe
  deserialization, sensitive-data exposure. Active at every level; Critical when confirmed.
  (PP-72, PP-73)
- **A4 Resource lifecycle** — files, sockets, locks, and handles released on every path,
  including error paths. (PP-40)
- **A5 State mutation and concurrency** — at every level, check concrete paths for state
  corruption, races, lost updates, unsafe mutation (confirmed corruption is Critical); at L3+,
  also shared-state invariants, ordering, atomicity, concurrency design. (PP-57, CC-137)
- **B1 Names reveal intent.** (CC-4, PP-74)
- **B2 Functions, control flow, and nesting** — length or parameter-count breach (CC-26,
  CC-147), function doing more than one thing, deep nesting. (CC-20, CC-21, CC-22, CC-178)
- **B3 Comments and dead code** — why, not what; cue: commented-out code. (CC-39, CC-43,
  CC-58, CC-144)
- **B4 Magic values and configuration.** (CC-175)
- **C1 SRP and cohesion** — cue: God class. (CA-8, CC-109, CC-110)
- **C2 Duplication / DRY** — whole-scope check. (PP-15, CC-37)
- **C3 Dependency direction** — whole-scope check. (CA-12, CA-31)
- **C4 Coupling, layer boundaries, and architecture smells** — feature envy (CC-164), train
  wreck (CC-81, PP-46), global state (PP-47, PP-48), inheritance deeper than 2 levels
  (PP-51), switch statements (CC-24, CC-173 — OOP only; see language-adjustments).
- **C5 KISS, YAGNI, and over-engineering** — speculative abstraction, one-use indirection,
  configuration for a value that never changes. (PP-43, CC-130)
- **C6 Public contracts and compatibility** — at every level, report confirmed breaking
  changes to visible APIs, schemas, protocols, or documented behavior; at L3+, also docs and
  backward compatibility of changed public contracts; at L4+, migration, deprecation,
  ecosystem impact. (CA-11)
- **D1 Tests for changed behavior**, including a regression test for every bug fix.
  (PP-70, CC-194)
- **D2 Test quality** — isolation, readability, FIRST. (CC-102, CC-106)
- **E1 Algorithmic complexity and material performance risks (L3+).** (PP-63, PP-64)
- **E2 Observability and operational failure behavior (L4+).**

### Point Tie-Breaks

Assign one primary point by root cause and remediation: security consequence, secrets,
authn/authz → A3 · state corruption, race, atomicity → A5 · other concrete behavior,
boundary, or error failure → A2 · complexity within one function → B2 · cohesion across
functions or modules → C1 · dependency direction → C3 · other coupling → C4. Never duplicate
one defect under two points; separate findings need distinct evidence and remediations.

## Levels, Thresholds, and Metrics

| Metric | L1 | L2 | L3 | L4 | L5 |
|--------|----|----|----|----|----|
| Function length (logic lines) | N/A | ≤80 | ≤50 | ≤30 | ≤20 |
| Parameter count | N/A | ≤7 | ≤5 | ≤4 | ≤3 |
| Nesting depth | N/A | ≤5 | ≤4 | ≤3 | ≤2 |
| PR / scope size (lines) | N/A | ≤800 | ≤500 | ≤300 | ≤200 |

**Function-length adjustments.** Test functions (framework-recognized: test path, naming
convention, or annotation) get the level threshold ×1.5, rounded up; production functions get
no multiplier. Before comparing a function against its threshold, exclude lines that only
perform mechanical error propagation or cleanup (immediate error returns, return-code checks
that exit at once, `goto cleanup`, rethrow-only catches, `defer`/`finally` release) —
never business decisions, state changes, transformations, logging policy, retries, or
recovery. Excluded ceremony is capped at 50% of raw nonblank non-comment body lines. A
finding using the subtraction shows the arithmetic: `62 raw, 14 excluded, 48 counted`.
Multiplier and subtraction apply to function length only, and may both apply to a test
function.

Nesting: the function body is depth 0; a top-level conditional is depth 1; consecutive guard
clauses at depth 1 do not count. A nesting-depth breach is Important, not Minor.

Emit at most one PR-size finding per review: `[PROJECT:SCOPE]`, `Point: C1`, verdict weight
1, Minor at L1–L2, Important at L3–L5, never `[fundamental]`.

### Duplication Threshold

Count total occurrences, including the original. Report when total occurrences reach: L1
never for duplication alone · L2 5 · L3 3 · L4 2 · L5 2. Test code: +1 occurrence. Never
report the first occurrence. File location does not change the threshold; this rule overrides
generic Rule of Three guidance. Accidental-duplication test: "if one changes, must the other
ALWAYS change?" If no, it is not duplicated knowledge — do not report it.

### Measurement Rules

1. Count logic lines only — exclude docstrings, comments, and blank lines.
2. Metrics are conversation starters, not hard gates.
3. Function-length exemptions: single-responsibility functions that cannot be meaningfully
   decomposed, pure data builders, large switch/match tables, configuration mappings.
4. Parameter-count exemptions: most parameters have defaults (count required parameters
   only), internal or private classes not instantiated by users, configuration functions,
   framework-controlled factory and builder signatures.
5. Never estimate a coverage percentage; cite coverage numbers only when a coverage report
   exists in the repository. Report changed behavior that lacks a meaningful test, naming
   file and function.

Before a paradigm-sensitive finding outside Java/C#, load the relevant subsection of
[language-adjustments.md](references/language-adjustments.md); in a polyglot repository,
resolve the paradigm per file.

## Severity, Noise Controls, and Waivers

| Severity | Criteria |
|----------|----------|
| 🔴 **Critical** | Confirmed security vulnerabilities, data-loss paths, authorization bypasses, state-corrupting correctness defects. Critical at every level; never waivable. |
| 🟡 **Important** | Material design, maintainability, testing, or performance failures, including metric-threshold breaches. |
| 🔵 **Minor** | One line only. No Effort/Benefit. Never affects the verdict. |

Minor floor: a competent maintainer would plausibly change the code after reading it;
otherwise omit.

- The same root cause in ≥2 in-scope files is ONE finding listing every affected file;
  distinct causes or remediations stay separate. Grouping compresses the report, never the
  verdict — its verdict weight is defined in the Verdict section.
- In diff reviews, tag pre-existing non-Critical issues `[pre-existing]`, demote them to
  Minor, and exclude them from the verdict. Critical is never demoted for being pre-existing.
- A repository-level finding with no truthful `file:line` uses a `[PROJECT:SCOPE]` header.
- Report at most 10 Minor findings: group first, rank by maintenance impact, disclose omitted
  candidates by point (`Minor omitted: N (B4 ×n, B3 ×m)`), and use `B4:CappedMinor:2` cells.
  The one exception to the no-omission rule; Critical and Important are never capped.

### Waivers and Overrides

Critical findings are never waivable; an attempt is a Critical governance finding. Waivers
suppress reporting, never checking — the cell still reads `C2:Waived:F#/W#`, and the finding
appears in the Waiver Disclosure and the Reconciliation. Expired waivers, and invalid ones
(blanket, `**`, category-wide, or `self`-approved at L4–L5), are inactive; each invalid
waiver produces an Important governance finding. More than 10 active waivers, or over 30%
of candidate findings suppressed (minimum 10 candidates), is an Important waiver-abuse
finding. Threshold overrides are raise-only, at most 2× the level default, and never more
permissive than L2; L5 DRY is not overridable; overrides carry the same governance fields as
waivers and never change severity definitions, verdict gates, evidence requirements, or
completeness accounting. Full schema: [review-profile.md](references/review-profile.md).

## Evidence and Effort/Benefit

Every Critical and Important finding uses one permitted evidence form:

1. Site: exact location, at most 3 quoted lines.
2. Distributed/project: at most 3 locations and 6 quoted lines total, or a reproducible
   project metric with its scope. Required for duplication, cycles, grouped, and
   `[PROJECT:SCOPE]` findings.
3. Negative: the exact files, symbols, or search scope checked and the expected artifact
   absent.

If no permitted form supports the claim, do not report it. A validly waived finding uses one
disclosure line and omits Evidence and Effort/Benefit; an invalid or expired waiver restores
the full finding.

**Effort:** Low = a few lines · Medium = moderate refactor · High = architectural or
wide-reaching. **Benefit:** High = hot path plus severe consequence · Medium = common path
plus moderate impact · Low = edge case plus minor impact. Give 1–3 reason bullets under each
rating; unresolved dimensions are Medium; full rubric and calibration questions in
[positioning.md](references/positioning.md).

## Required Report Format

Block order: 1 Header (positioning, level, source, profile path) · 2 Scope Manifest ·
3 Coverage Ledger · 4 Whole-Scope Checks · 5 🔴 Critical Issues · 6 🟡 Important Issues ·
7 🔵 Minor Issues · 8 Waiver Disclosure · 9 Coverage Reconciliation · 10 📝 Verdict.

Omit an empty severity section (blocks 5–7). The accounting blocks (2, 3, 4, 8, 9, 10) are
mandatory: never softening, never dropped for brevity. No praise or positive observations, no
hedging phrases ("overall the code is good", "nitpick"); severity labels and factual
qualifiers are not hedging.

Finding field order:

```markdown
- **[file:line] Title**
  - Point: A3 · Rule: PP-72 (Keep It Simple and Minimize Attack Surfaces)
  - Principle: … · Suggestion: … · Evidence: …
  - Effort: Low + reasons · Benefit: High + reasons
```

A Minor finding carries the title, `Point`, `Rule`, and `Suggestion` only.

### Coverage Ledger

| File | Contract & Safety | Readability | Design & Architecture | Testing | Performance & Operability | Status |
|------|-------------------|-------------|-----------------------|---------|---------------------------|--------|
| path | A2:F1 | Pass | C2:Waived:F3/W1 | D1:N/A:no-executable-behavior-change | E1:Gated:L3; E2:Gated:L4 | DONE |

### Coverage Cell Grammar

A bare `Pass` means every active point in that domain was checked and passed; only deviations
name individual points (`A2:F1`, `C2:Waived:F3/W1`, `B4:CappedMinor:2`, `E2:Gated:L4`,
`D1:N/A:no-executable-behavior-change`). Separate multiple deviations with `; `. A bare
`Pass` must appear alone in its cell. A point-qualified `Pass` (`E1:Pass`) is valid inside a
multi-point cell and asserts that point passed. In a domain containing both active and gated
points, name every point (`E1:Pass; E2:Gated:L4`) — a bare `Gated` value is forbidden.

Never assign one finding to two points merely to satisfy coverage.

### N/A Rules

Absence is usually evidence of a completed check, not inapplicability. Use `Pass` when the
point was checked and no defect exists. The only permitted N/A reasons:
`D1:N/A:no-executable-behavior-change` · `D2:N/A:no-test-code-in-scope` ·
`E1:N/A:no-executable-path` · `E2:N/A:no-runtime-operation`. If executable behavior changed
without a relevant test, use `D1:F<ID>`. Never valid: no tests, no docs, not found, unknown,
skipped, partial, not checked, out of scope.

### Whole-Scope Checks

| Check | Result | Finding |
|-------|--------|---------|
| C1 module cohesion | Pass | - |
| C2 duplication clusters | Finding | F2 |
| C3 dependency direction | Pass | - |
| Scope/PR size | Pass | - |

## Coverage Reconciliation

```markdown
- Manifest files completed: X/Y
- Domain cells accounted: X/Y
- Whole-scope checks completed: X/4
- Ledger finding references matched to report: X/Y
- Report findings referenced by ledger: X/Y
- Findings suppressed by valid waivers: N · Minor omitted by cap: N
- Status: COMPLETE | INCOMPLETE
```

Denominator: 5 × in-scope files. Count every syntactically valid nonblank cell, PARTIAL rows
included — `Pass` (bare or point-qualified), point-specific `Gated`, valid `N/A`, `Finding`,
`Waived`, and `CappedMinor` all count. COMPLETE still requires every in-scope row
DONE. Finding counts use unique IDs: a finding referenced from several cells counts once,
including a whole-scope finding, which appears in the Whole-Scope table and in every affected
file's relevant cell. Every reported or waived finding needs at least one ledger or
whole-scope reference; every reference resolves.

Never change the ledger to make a short report look complete; add the missing findings or
mark the review incomplete.

## Verdict

Evaluate the gates in order; the first match wins:

1. ⛔ Review incomplete — any file not DONE, any required cell or whole-scope check
   unaccounted, or finding reconciliation fails.
2. 🚫 Major rework — ≥3 active Critical findings.
3. 🚫 Major rework — ≥1 active Important architecture finding tagged `[fundamental]`.
4. ⚠️ Needs fixes — 1–2 active Critical findings.
5. ⚠️ Needs fixes — total Important verdict weight ≥ 4 at L1–L2 / 3 at L3 / 2 at L4–L5.
6. ✅ Ready to merge — otherwise.

Each active Important finding has `verdict_weight = min(affected_files, 3)` — distinct
in-scope files demonstrably affected, 1 for a `[PROJECT:SCOPE]` finding without a bounded
file set. Gate 5 sums those weights; Minor, capped-Minor, validly waived, and `[pre-existing]`
findings have no weight. **Total in-scope file count never affects a gate.** When the weighted
total differs from the finding count, show both.

- A) Two single-file Important at L4: weight 2 ≥ gate 2 → ⚠️.
- A′) Adding an unaffected 5th file changes nothing.
- B) One finding across 20 files: `min(20, 3)` = 3 → blocks at L3–L5, not alone at L1–L2.

`[fundamental]` requires evidence that a cross-module architecture defect demands redesign
before safe implementation; ordinary layer violations never carry it.

An incomplete review names the remaining files and checks; honest incompleteness is the
required successful outcome. Every verdict line states the level, severity counts, file
coverage, cell coverage, and whole-scope coverage:

`⚠️ Needs fixes at L3 — 1 Important (verdict weight 3), 2 Minor · 20/20 files · 100/100 domain cells · 4/4 whole-scope checks`

## Reference Loading

| Reference | Load when |
|-----------|-----------|
| [positioning.md](references/positioning.md) | MANDATORY: deriving or validating a level |
| [review-profile.md](references/review-profile.md) | Creating or validating a profile |
| [language-adjustments.md](references/language-adjustments.md) | Paradigm-sensitive finding outside Java/C# |
| [principles-spectrum.md](references/principles-spectrum.md) | DRY, YAGNI, or abstraction-timing edge cases |
| [quick-lookup.md](references/quick-lookup.md) | Symptom → rule and point |
| [clean-code.md](references/clean-code.md) · [clean-architecture.md](references/clean-architecture.md) · [pragmatic-programmer.md](references/pragmatic-programmer.md) | Citing a **CC-##**, **CA-##**, or **PP-##** rule |
| [principles-glossary.md](references/principles-glossary.md) | SOLID, LoD, CQS, component principles |
| [report-example.md](references/report-example.md) | First full report |

**Do NOT load all references at once.**
