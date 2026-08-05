# Documentation

**Purpose:** Comments and documentation-versus-code consistency.

Code comments and code-related documentation are in review scope. Documentation-versus-code contradictions are findings.

## Comments and inline docs

- Prefer names and structure over comments that restate the next line.
- Keep comments that explain *why*, external constraints, safety limits, or non-obvious algorithms.
- Report obsolete, misleading, or contradictory comments.
- Commented-out code belongs in version control history, not the working tree.
- TODO/FIXME without ownership or tracking when they block understanding of correctness.

Optional rule references: CC-39–63, CC-140–144, PP-11–13.

## Project documentation

- README, ADRs, API docs, and runbooks that describe behavior the code no longer implements.
- Missing documentation for a public interface the project claims to document.
- Documentation bolted on in a separate, stale channel when the project integrates docs with code (and vice versa: code that cannot be used from the documented entry points).
- Terminology that disagrees with a project glossary or ubiquitous language.

Optional rule references: PP-13, PP-80, CC-50, CC-141.

## Scope note

Never invent exclusions for documentation paths. Read every in-scope path fully. Judge applicability while reading. Paths ignored by `.gitignore` are never read.

## Symptom index

| Symptom | Look for |
| --- | --- |
| Doc says required, code defaults | Align doc or code |
| Comment describes old algorithm | Update or delete comment |
| Public API without any doc in a doc-heavy repo | Add or generate accurate docs |
| ADR contradicts implementation | Update ADR or code; report conflict |
