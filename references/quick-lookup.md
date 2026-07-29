# Quick Lookup by Symptom

Find the right rules quickly by searching for the symptom you observe.

## Table of Contents

- [Code Smells](#code-smells)
- [Naming Issues](#naming-issues)
- [Error Handling Issues](#error-handling-issues)
- [Testing Issues](#testing-issues)
- [Architecture Issues](#architecture-issues)
- [Component/Package Issues](#componentpackage-issues)
- [Concurrency Issues](#concurrency-issues)
- [Security Issues](#security-issues)
- [Performance Issues](#performance-issues)
- [Documentation Issues](#documentation-issues)
- [Process Issues](#process-issues)
- [Quick Rule Reference](#quick-rule-reference)

Checklist IDs: **A1** contract integrity · **A2** boundaries/errors/logic paths · **A3** security & secrets · **A4** resource lifecycle · **A5** state mutation & concurrency (baseline all levels; deep L3+) · **B1** names · **B2** functions/control flow/nesting · **B3** comments & dead code · **B4** magic values · **C1** SRP/cohesion · **C2** duplication/DRY · **C3** dependency direction · **C4** coupling/layer boundaries/architecture smells · **C5** KISS/YAGNI/over-engineering · **C6** public API & compatibility (baseline all levels; docs/compat L3+, migration L4+) · **D1** tests for changed behavior & regressions · **D2** test quality/FIRST · **E1** algorithmic complexity (L3+) · **E2** observability (L4+).

DRY report thresholds (total occurrences including original): L1 never · L2 5 · L3 3 · L4 2 · L5 2. Test code: +1 before reporting. Never report the first occurrence as duplication.

## Code Smells

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Function too long** | CC-20, CC-21, CC-180 | B2 | Extract smaller functions |
| **Too many parameters** | CC-26, CC-29, CC-147 | B2 | Use parameter object |
| **Deep nesting** | CC-22, CC-178, CC-20 | B2 | Extract methods, early return |
| **Duplicate code** | PP-15, CC-37, CC-128, CC-155 | C2 | Extract when total occurrences hit level threshold (L1 never · L2 5 · L3 3 · L4–L5 2; test +1; never first alone) |
| **Magic numbers** | CC-175 | B4 | Extract named constant |
| **Long method chains** | PP-46, CC-80, CC-81, CC-186 | C4 | Add delegate methods |
| **God class** | CC-109, CC-110, CA-8 | C1 | Split by responsibility |
| **Feature envy** | CC-164 | C4 | Move method to data owner |
| **Primitive obsession** | CC-29 | C1 | Create value object |
| **Data clumps** | CC-29 | C1 | Extract parameter object |
| **Switch statements** | CC-24, CC-173 | C4 | Consider polymorphism |
| **Parallel inheritance** | PP-51, CA-10 | C4 | Use composition |
| **Lazy class** | CC-130 | C5 | Inline or merge |
| **Speculative generality** | PP-43, CC-130 | C5 | Remove unused abstraction (YAGNI) |
| **Dead code** | CC-150, CC-159 | B3 | Delete it |
| **Comments explaining code** | CC-39, CC-40 | B3 | Improve naming/structure |

---

## Naming Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Meaningless name** | CC-4, CC-187 | B1 | Rename to express intent |
| **Single-letter variable** | CC-8, CC-191 | B1 | Use descriptive name |
| **Misleading name** | CC-5, CC-190 | B1 | Rename to match behavior |
| **Similar names** | CC-6 | B1 | Make distinction clear |
| **Encodings in names** | CC-9, CC-192 | B1 | Remove Hungarian notation |
| **Name doesn't match behavior** | CC-170, CC-193 | B1 | Rename or fix behavior |
| **Using "Manager/Handler/Processor"** | CC-11, CA-8 | B1 | Find more specific name |

---

## Error Handling Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Returning null** | CC-92 | A2 | Return Optional/empty collection |
| **Passing null** | CC-93 | A2 | Use Null Object pattern |
| **Empty catch block** | CC-86, PP-38 | A2 | Handle or rethrow |
| **Generic exception** | CC-89, CC-90 | A2 | Use specific exception |
| **Exception without context** | CC-89 | A2 | Add meaningful message |
| **Error codes instead of exceptions** | CC-34, CC-86 | A2 | Use exceptions (in OOP) |
| **Try-catch mixed with logic** | CC-35, CC-36 | A2 | Extract error handling |

---

## Testing Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Test depends on other tests** | CC-106 | D2 | Make tests independent |
| **Test requires external resource** | CC-106, PP-69 | D2 | Mock dependencies |
| **Test is slow** | CC-202 | D2 | Optimize or separate |
| **Multiple asserts** | CC-104, CC-105 | D2 | One concept per test |
| **Test name doesn't describe behavior** | CC-102 | D2 | Rename to express intent |
| **Hard to test** | PP-67, PP-69, CA-46, CA-48 | D2 | Redesign (DI, interfaces) |
| **No tests for bug fix** | PP-31, PP-93, CC-199 | D1 | Add regression test |
| **Low coverage on critical paths** | CC-194, CC-195 | D1 | Add tests for core logic |

---

## Architecture Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Tight coupling** | PP-17, PP-44, CC-114, CA-12 | C4 | Introduce interface |
| **Dependency points wrong way** | CA-12, CA-31 | C3 | Invert dependency |
| **Business logic in controller** | CA-29, CA-31 | C4 | Move to use case layer |
| **Framework everywhere** | CA-38, CA-47 | C4 | Isolate framework |
| **Can't test without DB** | CA-46, CA-47, CA-48 | C4 | Add repository interface |
| **Circular dependency** | CA-18 | C3 | Break cycle with interface |
| **One change = many files** | CA-15 | C1 | Improve component cohesion |
| **Hard to add new feature** | CA-9, CA-21 | C4 | Check OCP violations |
| **Structure doesn't reveal purpose** | CA-30 | C4 | Reorganize by domain |

---

## Component/Package Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Circular dependencies between packages** | CA-18 (ADP) | C3 | Break cycle with interface (DIP) or extract shared component |
| **Changing one package requires changing another** | CA-15 (CCP) | C1 | Move related classes together |
| **Using package brings unwanted dependencies** | CA-16 (CRP) | C1 | Split package into smaller focused ones |
| **Can't release package independently** | CA-14 (REP) | C1 | Restructure for independent versioning |
| **Stable package is all concrete classes** | CA-20 (SAP) | C3 | Add abstractions/interfaces |
| **Depending on frequently changing package** | CA-19 (SDP) | C3 | Invert dependency, depend on stable abstractions |
| **Package has unrelated classes** | CA-15, CA-16 | C1 | Split by cohesion (CCP/CRP) |
| **Too many packages to coordinate** | CA-14, CA-17 | C1 | Consider merging related packages |

---

## Concurrency Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Shared mutable state** | PP-57, CC-133 | A5 | Use immutable or sync |
| **Race condition** | PP-58, CC-139 | A5 | Proper synchronization |
| **Deadlock potential** | CC-136 | A5 | Minimize sync scope |
| **Large synchronized block** | CC-137 | A5 | Reduce critical section |
| **Thread-unsafe collection** | CC-134 | A5 | Use concurrent collection |
| **Shutdown issues** | CC-138 | A5 | Proper cleanup |

---

## Security Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Hardcoded secrets** | PP-55, PP-72 | A3 | Use environment/config |
| **No input validation** | PP-36, PP-72 | A3 | Validate all inputs |
| **SQL injection risk** | PP-72 | A3 | Use parameterized queries |
| **Excessive public API** | CC-108, CC-158, PP-72 | C6 | Minimize surface |
| **Outdated dependencies** | PP-73 | A3 | Update dependencies |

---

## Performance Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **O(n²) where O(n) possible** | PP-63, PP-64 | E1 | Optimize algorithm |
| **Premature optimization** | PP-64 | C5 | Measure first |
| **Resource leak** | PP-40 | A4 | Ensure cleanup |
| **N+1 query** | PP-63 | E1 | Batch or eager load |

---

## Documentation Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Outdated comment** | CC-141 | B3 | Update or delete |
| **Redundant comment** | CC-49, CC-142 | B3 | Delete |
| **Commented-out code** | CC-58, CC-144 | B3 | Delete (use VCS) |
| **No explanation for "why"** | CC-43 | B3 | Add intent comment |
| **Missing API documentation** | PP-13, CC-63 | C6 | Add doc comments |

---

## Process Issues

| Symptom | Related Rules | Checklist | Quick Fix |
|---------|---------------|-----------|-----------|
| **Build requires multiple steps** | CC-145, PP-94 | E2 | Automate |
| **Tests require multiple steps** | CC-146, PP-94 | D2 | Automate |
| **No version control** | PP-28 | E2 | Add VCS |
| **Large PR/commit** | PP-42 | C1 | Break into smaller changes |
| **No CI/CD** | PP-88, PP-89 | E2 | Set up automation |

---

## Quick Rule Reference

### By Book

| Prefix | Book |
|--------|------|
| **PP-##** | The Pragmatic Programmer |
| **CC-##** | Clean Code |
| **CA-##** | Clean Architecture |

### Most Common Rules

| Rule | Name | One-liner |
|------|------|-----------|
| CC-20 | Small Functions | Functions should be small |
| CC-21 | Do One Thing | Functions do one thing |
| PP-15 | DRY | Don't repeat yourself |
| PP-43 | YAGNI | Avoid fortune-telling |
| CA-8 | SRP | Single responsibility |
| CA-12 | DIP | Depend on abstractions |
| CC-4 | Intention-Revealing Names | Names express intent |
| CC-92 | Don't Return Null | Use Optional/empty |
| PP-38 | Crash Early | Fail fast |
| CC-106 | F.I.R.S.T. | Test quality |
