# Testing

**Purpose:** Whether behavior is protected by tests that are clear, independent, and maintainable.

Report missing, weak, or misleading tests as Confirmed Violations when code evidence shows unprotected behavior or a testing burden. Report testing findings only at L3 and above. Hard-to-test production code is often a design problem as well as a testing one.

## What to inspect

### Behavior coverage

- Changed or critical behavior without a meaningful test that would fail if the behavior broke.
- Boundary conditions, error paths, and regressions near prior bugs.
- Bug fixes without a reproduction or regression test.
- Disabled, skipped, or ignored tests without a clear open question and plan.

Optional rule references: CC-194–202, PP-31, PP-70, PP-93, CC-199.

### Test quality (F.I.R.S.T.)

| Criterion | Check |
| --- | --- |
| Fast | Slow suites that block frequent runs |
| Independent | Order dependence, shared mutable fixtures, hidden coupling |
| Repeatable | Flakes from time, network, locale, or residual state |
| Self-validating | Pass/fail needs human interpretation |
| Timely | Tests written too late to shape design (when that is observable) |

One concept per test; assert noise that hides intent; names that do not describe behavior.

Optional rule references: CC-100–106, CC-102, CC-104–105.

### Design for testability

- Production code that cannot be exercised without full infrastructure (database, network, clock) when a seam is reasonable.
- Missing Humble Object / interface boundaries at hard-to-test edges.
- Property-based or state-focused tests useful for algorithms and invariants when example tests alone leave gaps.

Optional rule references: PP-67, PP-69, PP-71, PP-92, CA-32, CA-46, CA-48.

### What not to invent

- Do not invent coverage percentages from reading code. Cite a numeric coverage figure only when a repository report supplies it.
- Tool-owned formatting and unused-import noise in tests is out of runtime guidance.
- Missing or unrunnable machine checks never block Complete Review.

## Symptom index

| Symptom | Look for |
| --- | --- |
| No test for a bug fix | Regression test that fails without the fix |
| Test depends on another test | Independent setup |
| Test needs live DB/network | Seam, fake, or Humble Object |
| Multiple unrelated asserts | Split by concept |
| Flaky timing/concurrency tests | Deterministic control of time and scheduling |
| Unreadable test | Domain helpers; arrange-act-assert clarity |
