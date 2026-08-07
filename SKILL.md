---
name: pragmatic-code-review
description: >
  Reviews user-selected code and reports every confirmed violation with code evidence, consequence, and severity at a user-chosen strictness level (L1–L5).
  Use for code review, architecture review, design review, maintainability review, or refactor review.
  Also triggers on: "review this PR", "code audit", "technical debt", "code smell", "check code quality", "is this code good?", "clean up code", "best practices".
  Do not use for implementing fixes, writing new code, or lint/format-only passes.
license: MIT
metadata:
  version: 2.2.0
---

# Pragmatic Code Review

## Product Promise

Complete Review means all known required review work is accounted for in one Auditable Review Trace, and Final Recheck found no unfinished work.
Emit the final report only after Complete Review.

The final report claims only what the Auditable Review Trace evidences: confirmed findings.

Resolve missing information from repository evidence first; remaining uncertainty becomes a reported finding, and the review continues until Complete Review or a user stop.

On user stop: emit the findings so far, labeled a partial review.

## Review Scope and Paths

Review Scope is the user's explicit target.
Resolve it with repository tools into a complete file list before review begins.
Show the scope basis and file count at review start.

- Absent scope → ask the user for Review Scope and wait. This is the review's only question; every later open point becomes a finding.
- Nonexistent target → empty Review Scope; complete the review by reporting that fact.
- Read every in-scope path directly and fully, judging rule applicability yourself while reading.
- Never read paths ignored by `.gitignore` — they may hold secrets.
- Never execute the code under review, including its tests and any snippet written against it; every finding rests on reading the source. Listing files and reading history are not execution.

## Quality Level

Apply only the user-stated Quality Level, L1–L5; when none is supplied, apply L3 and state it before review.
Repository-policy breaches are ordinary findings under that level.
A level relaxes only what the trigger table and the rule packs explicitly state for it.

Inspection triggers — the only numeric triggers. A breach is a measured value strictly greater than the trigger at the applied Quality Level; a value equal to the trigger is not a breach. Every breach is a Confirmed Violation:

| Inspection trigger | L1 | L2 | L3 | L4 | L5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Function effective logic lines | none | 80 | 50 | 30 | 20 |
| Required parameters | none | 7 | 5 | 4 | 3 |
| Maximum nesting depth | none | 5 | 4 | 3 | 2 |
| Confirmed occurrences of the same duplicated knowledge | none | 3 | 2 | 1 | 1 |
| Source-file lines | none | 800 | 500 | 300 | 200 |

`none` means no numeric trigger; concrete structural problems remain reportable at every level. On a metric axis that has a numeric trigger, a measured value at or below the trigger is not a finding.

### Counting rules

1. **Logic lines** — each simple statement and each control-flow clause header counts once, however many physical lines it spans. Docstrings are documentation, not logic.
2. **Required parameters** — caller-mandatory parameters only (excludes defaults, variadic parameters, receiver, and type parameters).
3. **Nesting** — function body is depth 0; each control level adds 1.
4. **Duplicated knowledge** — reviewer-judged same-knowledge occurrences (semantic, not clone detection). A confirmed count strictly greater than the level's trigger is a Confirmed Violation.
5. **File lines** — physical lines of the source file.

## Rule Packs

Review Protocol step 3 loads all eight packs:

1. [Design and Maintainability](references/design-and-maintainability.md)
2. [Testing](references/testing.md)
3. [Security and Privacy](references/security-and-privacy.md)
4. [Contracts and Compatibility](references/contracts-and-compatibility.md)
5. [Reliability and Operations](references/reliability-and-operations.md)
6. [Dependencies and Build](references/dependencies-and-build.md)
7. [Documentation](references/documentation.md)
8. [Research Reproducibility](references/research-reproducibility.md)

Report every problem with evidence and consequence, whether or not a pack names it — including correctness, security, authorization, data integrity, and repository contracts on every review.

Supporting references — open them when a pack cites their rule IDs or a topic needs book-level detail: [clean-code.md](references/clean-code.md), [clean-architecture.md](references/clean-architecture.md), [pragmatic-programmer.md](references/pragmatic-programmer.md), and [principles-glossary.md](references/principles-glossary.md); open [language-adjustments.md](references/language-adjustments.md) when a counting or nesting question is language-specific.

**Rule Authority:** use the most directly relevant source; on conflict, inspect the repository; if conflict remains, report the finding with the conflicting evidence for the user to rule out.

Leave formatting, naming conventions, and unused imports to linters and formatters; report one only with a concrete consequence beyond style.

## Review Protocol

1. **Fix Quality Level.** Done when the level (L1–L5, default L3) is stated.
2. **Enumerate scope.** Resolve Review Scope to a complete file list. Done when the basis and file count are shown.
3. **Load Rule Packs.** Load all eight packs once and keep them available. Done when every pack file has been read.
4. **Read and review.** Read each in-scope file completely, applying relevant guidance. Done when every scope file is read, its metrics are recorded, and its findings are traced.
5. **Whole-scope checks.** Cross-file effects, duplication of knowledge, dependency direction, contracts, and other scope-wide concerns. Done when each check is traced.
6. **Final Recheck.** Done when it finds no new gap (see Final Recheck).
7. **Report findings.** Emit the final report (Product Promise).

Scale workers to scope: the main agent alone for a small file set; one subagent for a medium batch; parallel subagents only when independent file groups can run without shared state.
Explicitly instruct every spawned subagent to load and use this skill and state which Quality Level applies.
The main agent enumerates the complete scope, assigns file groups, integrates results, performs whole-scope checks, runs Final Recheck, and owns the single Auditable Review Trace; subagents report results back.

## Auditable Review Trace

One trace. It accounts for:

- every in-scope file and its actual complete read
- every computed metric value
- every required cross-boundary or whole-scope check
- every Confirmed Violation
- all known unfinished work

Update the trace immediately after each completed file read, required check, and Confirmed Violation.

The trace records only work actually performed — the goal is complete work, never a complete-looking trace.

## Final Recheck

Run Final Recheck before the final response:

1. Reconcile Review Scope against the Auditable Review Trace.
2. Check for missed files, test code, cross-file effects, and required checks, reconsidering all eight pack purposes.
3. A discovered gap continues the review; the next recheck covers only the newly covered work.
4. No new gap → Complete Review is reached.

## Findings

A Confirmed Violation needs concrete code evidence and a credible consequence. For an inspection-trigger breach, the measurement (metric, measured value, trigger value, location) is the evidence; no separate consequence sentence is required.
Project-policy violations are ordinary Confirmed Violations under the same evidence rule.

Documentation-versus-code contradictions and misleading code comments are findings; code comments and code-related documentation are in review scope.

### Finding Severity

Severity follows the most severe supported consequence:

- **Critical** — authorization bypass, sensitive-data disclosure, authoritative-data loss or corruption, unavailable core service, physical harm, substantial financial loss.
- **Important** — incorrect external behavior, reduced reliability, required workaround, serious performance degradation, concrete maintainability or testing burden.
- **Minor** — limited local inconvenience or a small maintainability or testing burden.

An inspection-trigger breach with only the measurement as evidence is **Important** (concrete maintainability burden). Raise severity only when a stronger supported consequence applies; never Critical from the metric alone.

Quality Level decides whether a maintainability concern becomes a Confirmed Violation, including by whether a measured metric is strictly greater than its trigger.

### Report format

Emit the report in the response and write it to `docs/reviews/<timestamp>-report.md` in the reviewed project; write the trace beside it as `docs/reviews/<timestamp>-trace.md`. The timestamp is `YYYYMMDD-HHMMSSZ`.

The report carries findings only. A measurement at or below its trigger belongs in the trace. Scope basis, Quality Level, output paths, and a failed write are operational lines, not findings, and stay in the report.

One heading per severity class with at least one finding, ordered Critical → Important → Minor; order findings under each heading by code location:

```markdown
### Critical

- `path/to/file:line` Problem summary
  - Evidence: relevant code and supporting reasoning
  - Consequence: supported consequence
```

Put citations inside Evidence only when the finding depends on the external source.
