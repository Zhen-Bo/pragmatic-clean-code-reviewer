# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 2.1.0 - 2026-08-05

### Changed

- **Logic lines counting rule**: each simple statement and each control-flow clause header counts once (regardless of physical line span); docstrings are documentation, not logic. Replaces the prior "every nonblank, non-comment line" rule.
- **Inspection-trigger breaches are findings**: measured value strictly greater than the trigger at the applied Quality Level is a Confirmed Violation (equal is not a breach); evidence is the measurement; bare breach severity defaults to Important. Replaces "starts closer inspection and is not a finding by itself".
- **Duplication trigger row**: Confirmed occurrences of the same duplicated knowledge is now L1 none / L2 3 / L3 2 / L4 1 / L5 1 (was none / 5 / 3 / 2 / 2); L4 and L5 zero-tolerate a second confirmed copy.
- **At-or-below trigger is not a finding**: on a metric axis with a numeric trigger, a measured value at or below the trigger is not a finding (clarifies the triggers footnote).
- **Level relaxation is explicit**: "Lower levels relax only maintainability strictness" is replaced by "A level relaxes only what the trigger table and the rule packs explicitly state for it"; the testing pack now states "Report testing findings only at L3 and above", so L1/L2 reviews no longer report missing, weak, or misleading tests.
- **Generated-file special handling removed**: the documentation pack no longer defines any generated-artifact rules; every in-scope file is reviewed as ordinary code, whatever its header or origin claims. Users who do not want generated files reviewed exclude them from Review Scope. The pack is renamed from Documentation and Generated Artifacts to Documentation (`references/documentation.md`).

## 2.0.0 - 2026-08-04

### Added

- **Auditable Review Trace + Final Recheck**: one trace accounts for every file read, metric, check, and finding; the final report is emitted only after Complete Review, or labeled a partial review on user stop.
- **Eight Rule Packs** under `references/` (design and maintainability, testing, security and privacy, contracts and compatibility, reliability and operations, dependencies and build, documentation and generated artifacts, research reproducibility), linked from SKILL.md together with the book-based Rule Corpus files.
- **README notices** for token cost and large-scope context limits.

### Changed

- **Review contract rewritten (v2)**: pick a Quality Level L1–L5 directly in the request (default L3); inspection triggers and counting rules are explicit; severity (Critical / Important / Minor) follows the supported consequence only.
- **Findings**: every Confirmed Violation carries code evidence and a credible consequence; rule IDs are optional pointers.
- `scripts/validate_skill.py` rewritten as deterministic v2 contract checks.

### Removed

- 3+4+2 positioning questionnaire, verdict machinery, profiles, waivers, threshold overrides, and the emoji report format.
- `references/positioning.md`, `references/principles-spectrum.md`, `references/quick-lookup.md`, and the top-level `docs/` user guides (features, metrics, project-positioning, rule-sources).

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

- **Minor Issues tier (🔵)**: Consolidated to 2-tier severity (Critical + Important). Below-threshold items are not reported — if it's not worth actioning, omit it entirely
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
