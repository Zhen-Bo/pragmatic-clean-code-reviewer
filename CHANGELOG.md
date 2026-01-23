# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
