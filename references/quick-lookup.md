# Quick Lookup by Symptom

Find the right rules quickly by searching for the symptom you observe.

## Code Smells

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Function too long** | CC-20, CC-21, CC-180 | Extract smaller functions |
| **Too many parameters** | CC-26, CC-29, CC-147 | Use parameter object |
| **Deep nesting** | CC-22, CC-178, CC-20 | Extract methods, early return |
| **Duplicate code** | PP-15, CC-37, CC-128, CC-155 | Extract shared function (after Rule of Three) |
| **Magic numbers** | CC-175 | Extract named constant |
| **Long method chains** | PP-46, CC-80, CC-81, CC-186 | Add delegate methods |
| **God class** | CC-109, CC-110, CA-8 | Split by responsibility |
| **Feature envy** | CC-164 | Move method to data owner |
| **Primitive obsession** | CC-29 | Create value object |
| **Data clumps** | CC-29 | Extract parameter object |
| **Switch statements** | CC-24, CC-173 | Consider polymorphism |
| **Parallel inheritance** | PP-51, CA-10 | Use composition |
| **Lazy class** | CC-130 | Inline or merge |
| **Speculative generality** | PP-43, CC-130 | Remove unused abstraction (YAGNI) |
| **Dead code** | CC-150, CC-159 | Delete it |
| **Comments explaining code** | CC-39, CC-40 | Improve naming/structure |

---

## Naming Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Meaningless name** | CC-4, CC-187 | Rename to express intent |
| **Single-letter variable** | CC-8, CC-191 | Use descriptive name |
| **Misleading name** | CC-5, CC-190 | Rename to match behavior |
| **Similar names** | CC-6 | Make distinction clear |
| **Encodings in names** | CC-9, CC-192 | Remove Hungarian notation |
| **Name doesn't match behavior** | CC-170, CC-193 | Rename or fix behavior |
| **Using "Manager/Handler/Processor"** | CC-11, CA-8 | Find more specific name |

---

## Error Handling Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Returning null** | CC-92 | Return Optional/empty collection |
| **Passing null** | CC-93 | Use Null Object pattern |
| **Empty catch block** | CC-86, PP-38 | Handle or rethrow |
| **Generic exception** | CC-89, CC-90 | Use specific exception |
| **Exception without context** | CC-89 | Add meaningful message |
| **Error codes instead of exceptions** | CC-34, CC-86 | Use exceptions (in OOP) |
| **Try-catch mixed with logic** | CC-35, CC-36 | Extract error handling |

---

## Testing Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Test depends on other tests** | CC-106 | Make tests independent |
| **Test requires external resource** | CC-106, PP-69 | Mock dependencies |
| **Test is slow** | CC-202 | Optimize or separate |
| **Multiple asserts** | CC-104, CC-105 | One concept per test |
| **Test name doesn't describe behavior** | CC-102 | Rename to express intent |
| **Hard to test** | PP-67, PP-69, CA-47 | Redesign (DI, interfaces) |
| **No tests for bug fix** | PP-31, PP-93, CC-199 | Add regression test |
| **Low coverage on critical paths** | CC-194, CC-195 | Add tests for core logic |

---

## Architecture Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Tight coupling** | PP-17, PP-44, CC-114, CA-12 | Introduce interface |
| **Dependency points wrong way** | CA-12, CA-31 | Invert dependency |
| **Business logic in controller** | CA-29, CA-31 | Move to use case layer |
| **Framework everywhere** | CA-38, CA-47 | Isolate framework |
| **Can't test without DB** | CA-46, CA-47, CA-48 | Add repository interface |
| **Circular dependency** | CA-18 | Break cycle with interface |
| **One change = many files** | CA-15 | Improve component cohesion |
| **Hard to add new feature** | CA-9, CA-21 | Check OCP violations |
| **Structure doesn't reveal purpose** | CA-30 | Reorganize by domain |

---

## Component/Package Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Circular dependencies between packages** | CA-18 (ADP) | Break cycle with interface (DIP) or extract shared component |
| **Changing one package requires changing another** | CA-15 (CCP) | Move related classes together |
| **Using package brings unwanted dependencies** | CA-16 (CRP) | Split package into smaller focused ones |
| **Can't release package independently** | CA-14 (REP) | Restructure for independent versioning |
| **Stable package is all concrete classes** | CA-20 (SAP) | Add abstractions/interfaces |
| **Depending on frequently changing package** | CA-19 (SDP) | Invert dependency, depend on stable abstractions |
| **Package has unrelated classes** | CA-15, CA-16 | Split by cohesion (CCP/CRP) |
| **Too many packages to coordinate** | CA-14, CA-17 | Consider merging related packages |

---

## Concurrency Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Shared mutable state** | PP-57, CC-133 | Use immutable or sync |
| **Race condition** | PP-58, CC-139 | Proper synchronization |
| **Deadlock potential** | CC-136 | Minimize sync scope |
| **Large synchronized block** | CC-137 | Reduce critical section |
| **Thread-unsafe collection** | CC-134 | Use concurrent collection |
| **Shutdown issues** | CC-138 | Proper cleanup |

---

## Security Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Hardcoded secrets** | PP-55, PP-72 | Use environment/config |
| **No input validation** | PP-36, PP-72 | Validate all inputs |
| **SQL injection risk** | PP-72 | Use parameterized queries |
| **Excessive public API** | CC-108, CC-158, PP-72 | Minimize surface |
| **Outdated dependencies** | PP-73 | Update dependencies |

---

## Performance Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **O(n²) where O(n) possible** | PP-63, PP-64 | Optimize algorithm |
| **Premature optimization** | PP-64 | Measure first |
| **Resource leak** | PP-40 | Ensure cleanup |
| **N+1 query** | PP-63 | Batch or eager load |

---

## Documentation Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Outdated comment** | CC-141 | Update or delete |
| **Redundant comment** | CC-49, CC-142 | Delete |
| **Commented-out code** | CC-58, CC-144 | Delete (use VCS) |
| **No explanation for "why"** | CC-43 | Add intent comment |
| **Missing API documentation** | PP-13, CC-63 | Add doc comments |

---

## Process Issues

| Symptom | Related Rules | Quick Fix |
|---------|---------------|-----------|
| **Build requires multiple steps** | CC-145, PP-94 | Automate |
| **Tests require multiple steps** | CC-146, PP-94 | Automate |
| **No version control** | PP-28 | Add VCS |
| **Large PR/commit** | PP-42 | Break into smaller changes |
| **No CI/CD** | PP-88, PP-89 | Set up automation |

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
