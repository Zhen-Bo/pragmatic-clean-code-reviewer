# Contracts and Compatibility

**Purpose:** Public interfaces, compatibility promises, and schema or protocol stability.

Repository contracts and external behavior promises are review-wide obligations. Report breaking changes and unclear contracts with code evidence, not preference.

## Interface contracts

- Preconditions, postconditions, and invariants expressed in types, assertions, validation, or documented API behavior (Design by Contract).
- Callers able to violate preconditions silently; callees swallowing contract failures.
- Return and error shapes inconsistent with documented or established caller expectations.
- Command Query Separation: methods that both mutate and return in ways that surprise callers.

Optional rule references: PP-37, PP-38, PP-39, CC-33, CC-89–90.

## Public API and surface

- Accidental public surface (exported symbols, routes, events) wider than intended use.
- Semantic versioning or project versioning policy violated by the change (when the repository states a policy).
- Removed or renamed fields, endpoints, or CLI flags without migration path when consumers exist.
- Default-value or nullability changes that alter external behavior.

Optional rule references: CC-108, CC-158, PP-72.

## Compatibility and evolution

- Backward-incompatible schema, protocol, or file-format changes without version negotiation or migration.
- Database migrations that destroy or rewrite authoritative data unsafely.
- Feature flags or compatibility shims that are permanent with no removal plan when they accumulate risk.
- "Compatible" claims in docs that contradict code (report as findings).

## Liskov and substitutability

- Subtypes that strengthen preconditions, weaken postconditions, or throw unexpected errors.
- Type checks or special cases that reveal inheritance used for reuse rather than substitution.

Optional rule references: CA-10, PP-51–53.

## Project policy

Project-policy violations (lint config, API guidelines, ADR constraints) are ordinary Confirmed Violations under the same evidence rule. No separate finding class.

## Symptom index

| Symptom | Look for |
| --- | --- |
| Silent null / error code | Explicit result type or exception with context |
| Breaking field rename | Version, deprecation, dual-read |
| Undocumented required param | Types, validation, docs aligned |
| Subclass breaks parent use | Fix hierarchy or use composition |
| Migration drops column with data | Expand/contract or backfill plan |
