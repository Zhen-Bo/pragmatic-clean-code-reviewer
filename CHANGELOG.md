# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## 2.0.0

### Added

- Scope Manifest, five-domain Coverage Ledger, Whole-Scope Checks, Coverage Reconciliation, and the `⛔ Review incomplete` verdict — coverage accounting is a mandatory report contract
- Point-coded exception ledger cells (`Pass`, `A2:F1`, `E1:Pass; E2:Gated:L4`) and required `Point:` field on every finding
- Three evidence forms: site, distributed, and negative
- Two-stage Scope Manifest: PENDING → DONE with exact LOC
- N/A allowlist for ledger cells
- Function-length ×1.5 multiplier for test functions only; production code excludes mechanical error-propagation/cleanup lines from the count (itemized, capped at 50% of raw)
- Nesting counting convention
- Minor findings capped at 10 with disclosed omissions
- Governed threshold overrides: raise-only, ≤2×, expiring
- Waiver-abuse minimum-sample rule
- `dominant_language` profile field
- Authoritative schema at `references/review-profile.md`
- TOCs for long reference files
- Consent-based per-project review profile (`docs/code-review-profile.md`, fallback `.code-review-profile.md`) with scoped, expiring waivers; Critical findings are never waivable
- Closed 19-point / five-group review checklist (adds KISS/YAGNI/over-engineering and public-API/compatibility points) and anti-anchoring contract: user-named principles set emphasis, never scope
- Verbatim evidence-quote requirement for Critical/Important findings; `[PROJECT:SCOPE]` meta-findings; `[pre-existing]` tagging; default exclusions; batching protocol for large scopes

### Changed

- Rebalanced the skill around observable coverage rather than finding-shaped output
- Bounded correctness review to concrete contract, safety, boundary, and logic defects evidenced by a reviewed code path
- DRY ladder: total occurrences Never/5/3/2/2 (L1–L5) with +1 for tests (L3 aligns with Rule of Three)
- Parameter limits: L4 3→4, L5 2→3
- Important verdict gate uses absolute bases 4/3/2 with per-finding verdict weight `min(affected_files, 3)` — grouping compresses the report, never the verdict; total scope size never affects a gate
- `[fundamental]` reclassified as an Important architecture tag (not a separate severity class); kept as an Important-tier architecture designation
- Same-root-cause grouping at ≥2 files
- A5 (state/concurrency) and C6 (public contracts) baselines active at every level; deeper analysis L3+/L4+
- Batching adds a 600-LOC bound (with ≤5 files)
- Frontmatter version moved to `metadata.version` with `license: MIT`
- Questionnaire and D/R/C lookup moved to `references/positioning.md` (mandatory load)
- README and docs made harness-neutral (Agent Skills format; Claude Code, Codex, OpenCode, and compatible runners)
- Consolidated metrics, report example, smells, and red flags into canonical locations; report example moved to `references/report-example.md`
- Minor severity: one line, no Effort/Benefit, never affects the verdict, operational reporting floor, cap 10
- Test coverage reframed: never estimate percentages; report changed behavior lacking tests
- Conflicting profile levels resolve to the stricter of declared and derived, keep exclusions, and revalidate waivers and overrides against the effective level

### Removed

- Generic bug-hunting triggers ("find bugs", "check for issues", "look at my code") and exhaustive bug-sweep language
- Redundant Rule Reference Codes, Common Principles Quick Reference, inline full report example, and duplicated positioning/threshold content
- Estimated static test-coverage percentages; vague same-file DRY exemption

### Fixed

- Report example certified gated-but-active E1 cells and invalid D2/R3/C1→L3 mapping (now D2/R3/C2)
- `N/A:no tests` D1 bypass
- Unbounded threshold overrides
- Reconciliation arithmetic: unique IDs; PARTIAL-row cells count (6/10 case)
- Residual coverage percentages in positioning reference
- Empty Critical-architecture verdict class
- DRY occurrence calibration made explicit and the worked example corrected to the 4th occurrence at L3 (superseded by Never/5/3/2/2 ladder above)
- Misattributed rule IDs: PP-91→PP-70, PP-75→PP-62 (SKILL.md), Plugin Architecture CA-48→CA-47 and Humble Object CA-47→CA-46 (glossary), Hard-to-test CA-47→CA-46/CA-48 (quick-lookup)
- Documentation drift: severity model, valid-combination count (20→16), report-flow diagram, version/changelog mismatch

## 1.3.2

### Added

- **Review Integrity**: Anti-sycophancy, severity anchoring, completeness gates, and pre-verdict gate — do not omit/downplay findings, complete the full checklist, classify from criteria alone, and do not retract findings without factual correction
- **Completeness Gate Expansion**: Require every in-scope file against all checklist points, the Common Code Smells table, and the Red Flags list before classification
- **Minor Severity Tier Restored**: Reintroduced 🔵 Minor (Nice to Have) with simplified Rule + Suggestion format (no Effort/Benefit); allowed report sections now include Minor Issues

### Changed

- **Severity Floor**: Items below Minor threshold are not reported (was: below Important)
- **Workflow Notes**: Severity anchoring before user reaction; Minor excluded from Effort/Benefit assessment; pre-verdict check that all scoped files were reviewed

## 1.3.1

### Added

- **Issue Separators**: `---` horizontal rules between issues within the same severity section for visual breathing room
- **Strengths Suppression Whitelist**: Explicit allowed-sections-only instruction prevents LLM from generating praise under alternate headings
- **Effort/Benefit Inline Rationale**: Each rating now includes nested bullet reasons derived from calibration questions (file count, cross-boundary, hot path, consequence, workaround)

### Changed

- **Effort/Benefit Format**: Replaced single-line `Fix: Effort: X | Benefit: Y` with separate `Effort:` and `Benefit:` lines, each with 1-3 nested reason bullets
- **E/B Section Title**: Renamed from "Fix Effort & Benefit" to "Effort & Benefit" throughout

### Removed

- **Single-line Fix format**: `Fix: Effort: X | Benefit: Y` replaced by multi-line format with rationale

## 1.3.0

### Added

- **Fix Effort & Benefit Analysis**: Each Critical and Important issue includes `Fix: Effort: [L/M/H] | Benefit: [L/M/H]` with step-by-step reasoning guidance to prevent Medium/Medium defaults
- **Severity Classification**: Explicit 2-tier criteria table (Critical vs Important) with clear definitions and examples
- **Review Workflow**: Explicit 8-step sequence (Calibrate → Scope → Language → Review → Classify → Assess → Report → Verdict)
- **Verdict Criteria**: Deterministic "first matching condition" table — same inputs always produce same verdict
- **L3 Fallback**: When user skips positioning, defaults to L3 (Team) with note in report header
- **When to Load References**: Routing table for lazy-loading reference files by context
- **Empty Section Guidance**: Empty severity sections are omitted entirely from the report
- **Expanded Trigger Phrases**: Added "review this PR", "PR review", "code review", "pre-merge check", "code audit", "is this production-ready?", "find bugs", "look at my code", "check for issues"

### Changed

- **Report Formatting**: Bold only on issue title lines; sub-item labels (Rule, Principle, Suggestion, Fix) are now plain text for cleaner TUI readability
- **Go Language**: Enriched description — noted interface-based polymorphism, struct embedding, composition philosophy
- **Paradigm Labels**: "Systems" → "Systems/Composition", "Procedural" → "Procedural/Composition"

### Removed

- **Minor Issues tier (🔵)**: Consolidated to 2-tier severity (Critical + Important). Below-threshold items are not reported — if it's not worth actioning, omit it entirely *(Correction 2.0.0: this removal was never applied — the Minor tier remained in SKILL.md and is intentionally retained as verdict-neutral from 2.0.0 onward.)*
- **Strengths section (✅)**: Removed from report template, example, and workflow. Code review is purely problem-focused — no AI sycophancy
- **"Common Mistakes to Avoid" section**: Guidance integrated into workflow and reference loading table
- **"The Bottom Line" section**: Redundant with the explicit Review Workflow
- **Component Principles inline table**: Moved to reference link (`principles-glossary.md`)

## 1.2.0

### Changed

- **Expanded Description Triggers**: Added more natural language triggers ("is this code good?", "check code quality", "ready to merge?", "technical debt", "code smell", "best practices", "clean up code", "refactor review") to improve skill discoverability
- **Leaner SKILL.md**: Moved detailed Strictness Matrix and Metric Thresholds tables to `references/positioning.md`, keeping only quick reference in main skill file (359 → 343 lines)
- **Progressive Disclosure**: SKILL.md now references `positioning.md` for complete matrices, following skill-creator best practices

## 1.1.0

### Added

- **GitHub Actions Release Workflow**: Auto-trigger on `v*` tags, validate skill, generate `.skill` and `.zip` packages
- **Detailed Report Format**: Each issue now includes Rule Name, Principle explanation, and Suggestion
- **Language-aware Warning**: Switch statements section now warns about FP/TS paradigm differences
- **Quick Test for DRY**: Added "If one changes, must the other ALWAYS change?" test for accidental duplication
- **Installation Guide**: Support for Claude Code, OpenCode, and Codex with verification steps

### Changed

- **Reference Files Reorganization**: Split `reference-manual.md` into 8 focused files:
  - `clean-code.md` (CC-1 to CC-202)
  - `clean-architecture.md` (CA-1 to CA-48)
  - `pragmatic-programmer.md` (PP-1 to PP-100)
  - `principles-glossary.md` (SOLID, DRY, YAGNI, etc.)
  - `principles-spectrum.md` (DRY vs WET guidance)
  - `language-adjustments.md` (per-language rule adjustments)
  - `positioning.md` (3+4+2 questionnaire system)
  - `quick-lookup.md` (symptom → rule lookup)
- **DRY Tolerance Format**: Changed from ambiguous "2×" to explicit "max 2 → report on 3rd occurrence"
- **L1 Test Coverage**: Changed from "0%" to "N/A" for consistency with other L1 metrics
- **60-line Example**: Added "(exemption rationale, not default tolerance)" clarification

### Fixed

- **Code Smells Table**: Removed hardcoded numbers, now references Metric Thresholds
- **CC-75 Invalid Reference**: Changed to CC-22, CC-178 for deep nesting (CC-75 was in skipped Formatting chapter)
- **Parameter Count Inconsistency**: Code Smells now references level thresholds instead of fixed ">3"
- **Function Length Inconsistency**: Code Smells now references level thresholds instead of fixed ">30-50"

### Removed

- `reference-manual.md` (replaced by 8 focused files in `references/`)

## 1.0.1

### Changed

- **Mandatory Project Positioning**: Added prominent "MANDATORY FIRST STEP" section at top of skill
- **Stronger Emphasis**: Use "STOP!" and "DO NOT proceed" language for project positioning requirement

### Fixed

- Removed duplicate positioning question from Step 1

## 1.0.0

### Added

- Initial release of Pragmatic Clean Code Reviewer skill
- **Rule Sources**: 
  - The Pragmatic Programmer (PP-1 to PP-100)
  - Clean Code (CC-1 to CC-202)
  - Clean Architecture (CA-1 to CA-48)
- **3+4+2 Questionnaire System**: Project positioning with L1-L5 strictness levels
- **15-Point Review Checklist**: Comprehensive code review coverage
- **Language-Aware Adjustments**: Rules adapted for Java, Python, TypeScript, Rust, Go, etc.
- **Standardized Report Format**: Consistent output with emoji indicators
- **350+ Rules**: Complete reference manual with review points
