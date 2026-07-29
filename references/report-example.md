# Full Report Example

Canonical worked examples of the required report contract. Block order is fixed:
Header · Scope Manifest · Coverage Ledger · Whole-Scope Checks · 🔴 Critical ·
🟡 Important · 🔵 Minor · Waiver Disclosure · Coverage Reconciliation · 📝 Verdict.

Omit empty severity sections. Accounting blocks are always present.

## Table of Contents

- [Example 1 — Complete Review](#example-1--complete-review)
- [Example 2 — Incomplete Review](#example-2--incomplete-review)
- [Arithmetic notes](#arithmetic-notes)

---

## Example 1 — Complete Review

Scenario: TypeScript checkout service. Positioning D2 / R3 / C2 → **L3** (Internal
SDK). Three in-scope files, five unique findings (one waived). Domain cells =
3 files × 5 domains = 15.

The Scope Manifest is emitted twice: Stage 1 enumerates the scope **before** any
file is opened (LOC unknown, every row `PENDING`); Stage 2 re-emits the rows with
exact LOC and a per-row `DONE` / `PARTIAL` status once review has run.

### Ledger cell grammar

One cell per file × domain. A bare `Pass` asserts that **every point active at
this level** in that domain passed; only deviations are named, `; `-separated.
The forms below are generic; the ledger further down pairs its own points and IDs.

| Form | Meaning |
|------|---------|
| `Pass` | All active points in this domain pass |
| `A2:F1` | Point A2 produced finding F1 |
| `E2:Gated:L4` | Point E2 is not active at this level; it activates at L4 |
| `D1:N/A:no-executable-behavior-change` | Point does not apply (allowlisted reason) |
| `C2:Waived:F3/W1` | Point C2 produced finding F3, suppressed by waiver W1 |
| `B4:CappedMinor:2` | 2 Minor items in this point were omitted under the Minor cap of 10 |

Two hard rules:

- **Bare `Gated` is forbidden** in a domain that holds both active and gated
  points. Performance & Operability at L3 must read `E1:Pass; E2:Gated:L4`, never
  `Gated:L4` alone — that would hide E1's result.
- **N/A allowlist, exhaustive:** `D1:N/A:no-executable-behavior-change` ·
  `D2:N/A:no-test-code-in-scope` · `E1:N/A:no-executable-path` ·
  `E2:N/A:no-runtime-operation`. No other N/A reason is valid; any other domain
  must record `Pass` or a named finding.

`Pass` asserts only the points that are active at the current level, so read the
gating before the cell. At L3 the single fully gated point is E2, which the rule
above already forces the Performance & Operability cell to name. C6 is **not**
gated out here: its baseline — confirmed breaking changes to visible APIs,
schemas, protocols, or documented behavior — is active at every level, its
documentation and backward-compatibility checks activate at L3+, and only
migration, deprecation, and ecosystem impact wait for L4. The Design &
Architecture cells below therefore do assert C6 — a bare `Pass` covers C1
through C6, and `C2:Waived:F3/W1` names C2 as the only deviation while still
asserting that C1, C3, C4, C5, and C6 passed.

### Report output

````markdown
## 📋 Code Review Report

**Level:** L3 Team
**Positioning:** D2 / R3 / C2 (Internal SDK)
**Source:** profile
**Profile path:** docs/code-review-profile.md

### Scope Manifest — Stage 1 (enumerated, nothing read yet)

- Basis: `user-specified`
- In scope: 3 · Excluded: 1
- Review level: L3
- Profile source: docs/code-review-profile.md
- Scope size: ~290 lines (`estimate`, from diff stat — superseded by measured LOC)

| # | File | LOC | Language/Paradigm | Status |
|---|------|-----|-------------------|--------|
| 1 | src/services/checkout-service.ts | — | TypeScript/OOP | PENDING |
| 2 | src/services/payment-gateway.ts | — | TypeScript/OOP | PENDING |
| 3 | src/repositories/order-repo.ts | — | TypeScript/OOP | PENDING |

#### Exclusions

| Path | Reason |
|------|--------|
| src/generated/openapi.ts | generated |

### Scope Manifest — Stage 2 (files read; exact LOC)

| # | File | LOC | Language/Paradigm | Status |
|---|------|----:|-------------------|--------|
| 1 | src/services/checkout-service.ts | 142 | TypeScript/OOP | DONE |
| 2 | src/services/payment-gateway.ts | 88 | TypeScript/OOP | DONE |
| 3 | src/repositories/order-repo.ts | 65 | TypeScript/OOP | DONE |

Measured scope size: 295 lines (L3 ceiling 500).

### Coverage Ledger

| File | Contract & Safety | Readability | Design & Architecture | Testing | Performance & Operability | Status |
|------|-------------------|-------------|-----------------------|---------|---------------------------|--------|
| src/services/checkout-service.ts | Pass | B2:F2 | C2:Waived:F3/W1 | D1:Pass; D2:N/A:no-test-code-in-scope | E1:Pass; E2:Gated:L4 | DONE |
| src/services/payment-gateway.ts | Pass | B4:F4 | C2:Waived:F3/W1 | D1:Pass; D2:N/A:no-test-code-in-scope | E1:Pass; E2:Gated:L4 | DONE |
| src/repositories/order-repo.ts | A3:F1 | Pass | Pass | D1:F5; D2:N/A:no-test-code-in-scope | E1:Pass; E2:Gated:L4 | DONE |

### Whole-Scope Checks

| Check | Result | Finding |
|-------|--------|---------|
| C1 module cohesion | Pass | — |
| C2 duplication clusters | Finding | F3 (waived by W1) |
| C3 dependency direction | Pass | — |
| Scope/PR size | Pass (295 ≤ 500) | — |

### 🔴 Critical Issues (Must Fix)

- **[src/repositories/order-repo.ts:41] F1 — Order lookup builds SQL by string concatenation**
  - Point: A3 (security & secrets)
  - Rule: PP-72 (Keep It Simple and Minimize Attack Surfaces)
  - Principle: An untrusted order ID reaches the query text, so a caller can alter the predicate and read or mutate another tenant's orders.
  - Suggestion: Bind `orderId` as a query parameter and reject non-UUID input at the repository boundary.
  - Evidence (site):
    ```ts
    const sql = `SELECT * FROM orders WHERE id = '${orderId}'`;
    return this.db.query(sql);
    ```
  - Effort: Low
    - Single call site; signature and callers stay the same
    - Driver already supports bound parameters
  - Benefit: High
    - Checkout loads an order on every request
    - Confirmed injection enables cross-tenant data access

---

### 🟡 Important Issues (Should Fix)

- **[src/services/checkout-service.ts:71] F2 — `finalizeCheckout` runs 62 logic lines across pricing, inventory, and payment**
  - Point: B2 (functions/control flow/nesting)
  - Rule: CC-20 (Small Functions)
  - Principle: `finalizeCheckout` spans lines 71–139 of a 142-line file and holds 62 logic lines — comments and blank lines excluded — against the L3 ceiling of 50; the ×1.5 test-function multiplier does not apply and no mechanical error-ceremony lines qualify for exclusion (62 raw, 0 excluded, 62 counted). Its body is partitioned by numbered section dividers into three responsibilities, which hide the failure paths and block focused tests.
  - Suggestion: Extract pricing adjustment, inventory reservation, and payment capture into named private helpers so `finalizeCheckout` only sequences steps.
  - Evidence (site: lines 101–103):
    ```ts
    // ---- 2 of 3: inventory ----
    const holds = await this.inventory.reserve(priced.lines, opts.warehouse);
    const reserved = await this.inventory.commit(holds, order.id);
    ```
  - Effort: Medium
    - Touches the service module and its unit tests
    - No public API change if the helpers stay private
  - Benefit: Medium
    - Checkout is a common path; defects here affect paid orders
    - Decomposition unblocks isolated regression tests per step

- **[src/repositories/order-repo.ts:41] F5 — Changed order-lookup behavior ships without a test**
  - Point: D1 (tests for changed behavior & regressions)
  - Rule: PP-93 (Find Bugs Once)
  - Principle: `findById` changed in this diff and carries the query construction flagged by F1; with no test the parameterized-query behavior can regress silently.
  - Suggestion: Add a repository test asserting that `findById` passes `orderId` as a bound parameter and rejects a non-UUID input.
  - Evidence (negative): searched `src/**/*.test.ts`, `src/**/*.spec.ts`, and `tests/**/*.ts` for `order-repo` and `findById`; no file matched — the repository has no test module in the search scope.
  - Effort: Low
    - One new test file; the repository already takes an injectable db client
    - No production code changes required by the test itself
  - Benefit: Medium
    - Locks in the F1 fix against silent regression on a hot path
    - Prevention rather than an active fault, so impact is deferred

---

### 🔵 Minor Issues (Nice to Have)

- **[src/services/payment-gateway.ts:22] F4 — Retry delay uses unnamed literal `250`** · Point: B4 · Rule: CC-175 · Suggestion: name a constant such as `RETRY_BASE_DELAY_MS`

### Waiver Disclosure

| Waiver | Point | Paths | Finding | Expires | Approver |
|--------|-------|-------|---------|---------|----------|
| W1 | C2 | src/services/** | F3 | 2026-12-01 | team-lead |

- **F3** · Point: C2 · Pricing-rule validation duplicated at 3 total occurrences (L3 threshold 3) across `checkout-service.ts` and `payment-gateway.ts` · suppressed by W1.

### Coverage Reconciliation

- Manifest files completed: 3/3 (every row DONE)
- Domain cells accounted: 15/15 (3 files × 5 domains; Gated, allowlisted N/A, Waived, and CappedMinor cells all count as accounted)
- Whole-scope checks completed: 4/4
- Unique finding IDs: 5 (F1, F2, F3, F4, F5)
- Ledger finding references matched to report: 5/5
- Report findings referenced by ledger: 5/5
- Findings suppressed by valid waivers: 1
- Status: COMPLETE

### 📝 Verdict

⚠️ Needs fixes at L3 — 1 Critical, 2 Important, 1 Minor · 3/3 files · 15/15 domain cells · 4/4 whole-scope checks

Counted: Critical F1; Important F2 and F5. F3 is waived by W1 and is excluded
from verdict totals. Minor never affects the verdict.
````

### Evidence forms used

Every Critical and Important finding carries exactly one evidence form.

| Finding | Form | What it shows |
|---------|------|---------------|
| F1 | site | ≤3 quoted lines at one location |
| F2 | site | ≤3 quoted lines at one location |
| F5 | negative | Exact search scope (globs + symbols) and the absent artifact |
| F3 | distributed | ≤3 locations, ≤6 lines total — recorded during checking, not printed because W1 suppresses reporting |

F3's recorded evidence was `checkout-service.ts:96`, `checkout-service.ts:131`,
`payment-gateway.ts:41`. A waived finding is disclosed as one line with its ID,
point, description, and waiver ID — never with Evidence, Effort, or Benefit.

---

## Example 2 — Incomplete Review

Scenario: same calibration, two files — a scope well under the batching trigger,
so the whole review is a single batch. Part way through the second file the agent
determined that the remaining context could not complete that batch, stopped, and
reported the work actually finished instead of compressing the rest. One row
finished, one row `PARTIAL` with a single valid cell. No merge-readiness verdict
is possible.

````markdown
## 📋 Code Review Report

**Level:** L3 Team
**Positioning:** D2 / R3 / C2 (Internal SDK)
**Source:** questionnaire
**Profile path:** —

### Scope Manifest — Stage 1 (enumerated, nothing read yet)

- Basis: `changed-files`
- In scope: 2 · Excluded: 0
- Review level: L3
- Profile source: questionnaire
- Scope size: ~230 lines (`estimate`, from diff stat — superseded by measured LOC)

| # | File | LOC | Language/Paradigm | Status |
|---|------|-----|-------------------|--------|
| 1 | src/services/checkout-service.ts | — | TypeScript/OOP | PENDING |
| 2 | src/services/payment-gateway.ts | — | TypeScript/OOP | PENDING |

### Scope Manifest — Stage 2 (files read; exact LOC)

| # | File | LOC | Language/Paradigm | Status |
|---|------|----:|-------------------|--------|
| 1 | src/services/checkout-service.ts | 142 | TypeScript/OOP | DONE |
| 2 | src/services/payment-gateway.ts | 88 | TypeScript/OOP | PARTIAL |

### Coverage Ledger

| File | Contract & Safety | Readability | Design & Architecture | Testing | Performance & Operability | Status |
|------|-------------------|-------------|-----------------------|---------|---------------------------|--------|
| src/services/checkout-service.ts | Pass | Pass | Pass | D1:Pass; D2:N/A:no-test-code-in-scope | E1:Pass; E2:Gated:L4 | DONE |
| src/services/payment-gateway.ts | Pass | — | — | — | — | PARTIAL |

### Whole-Scope Checks

| Check | Result | Finding |
|-------|--------|---------|
| C1 module cohesion | not run | — |
| C2 duplication clusters | not run | — |
| C3 dependency direction | not run | — |
| Scope/PR size | not run | — |

### Waiver Disclosure

- No waivers (no profile in this review).

### Coverage Reconciliation

- Manifest files completed: 1/2 (DONE rows only; a PARTIAL row is not a completed file)
- Domain cells accounted: 6/10 (5 valid cells on the DONE row + 1 valid cell on the PARTIAL row)
- Whole-scope checks completed: 0/4
- Unique finding IDs: 0
- Ledger finding references matched to report: 0/0
- Report findings referenced by ledger: 0/0
- Findings suppressed by valid waivers: 0
- Status: INCOMPLETE (COMPLETE requires every manifest row DONE)

### 📝 Verdict

⛔ Review incomplete — 1/2 files reviewed · 6/10 domain cells accounted

Remaining work:
- src/services/payment-gateway.ts — Readability, Design & Architecture, Testing, Performance & Operability (4 cells)
- Whole-scope checks: C1 module cohesion, C2 duplication clusters, C3 dependency direction, Scope/PR size

No merge-readiness claim is permitted while reconciliation is incomplete. The
remaining context could not hold the rest of this batch's accounting, so the
review stopped rather than compressing it; the unfinished file is reported as
PARTIAL and credited only for the cell completed before the stop. Reporting
honest incompleteness is the required successful outcome when a review cannot be
finished.
````

**Maintainer note:** the 6/10 is not a typo. Valid cells on a `PARTIAL` row count
toward the accounted numerator — partial work is credited where it was actually
done. What a PARTIAL row cannot do is count as a completed file or unlock
`COMPLETE`, which is why the same report reads 6/10 cells but 1/2 files and
Status INCOMPLETE.

**Maintainer note — where the stop is allowed:** the batching rule stops at a
batch boundary whenever the remaining context cannot hold another complete
batch, and never compresses the last batch. A two-file scope is one batch, so no
later boundary existed to stop at; when even the current batch cannot be
finished, the same rule's fallback is exactly this report — credit the cells
actually completed, mark the unfinished row `PARTIAL`, and issue ⛔ instead of a
thinned-out review that reads as complete.

---

## Arithmetic notes

### Unique-ID counting

Reconciliation counts finding **IDs**, not references to them. A whole-scope
finding appears once in the Whole-Scope Checks table and once in the relevant
cell of every affected file, so F3 in Example 1 is referenced three times (two
ledger cells plus the whole-scope row) and still counts as one finding. Both
directions must resolve: every ID named anywhere in the ledger or whole-scope
table has a report block, and every reported finding is named by at least one of
them.

### Domain-cell counting

Denominator = in-scope files × 5 domains. Numerator = valid, nonblank cells on
**every** manifest row, PARTIAL rows included. A cell is valid when it reads
`Pass` or names a deviation: a finding, an allowlisted `N/A`, `Gated`, `Waived`,
or `CappedMinor`. A blank or `—` cell is unaccounted. `COMPLETE` requires every
manifest row to be DONE, independently of the cell fraction.

| Quantity | Example 1 | Example 2 |
|----------|----------:|----------:|
| Files in scope | 3 | 2 |
| Files DONE | 3 | 1 |
| Domain cells (files × 5) | 15 | 10 |
| Valid cells | 15 | 6 |
| Whole-scope checks run | 4 | 0 |
| Unique finding IDs | 5 | 0 |
| Bidirectional match | 5/5 | 0/0 |
| Suppressed by valid waivers | 1 | 0 |
| Status | COMPLETE | INCOMPLETE |

Example 1 cells: 5 + 5 + 5 = 15. Example 2 cells: 5 (DONE row) + 1 (PARTIAL row,
Contract & Safety only) = 6 of 10.

### Verdict gates (Example 1)

Gates are evaluated in order; the first match wins.

| # | Gate | Example 1 | Fires |
|---|------|-----------|-------|
| 1 | ⛔ reconciliation incomplete | 3/3 files, 15/15 cells, 4/4 checks | no |
| 2 | 🚫 ≥3 Critical | 1 Critical | no |
| 3 | 🚫 ≥1 Important `[fundamental]` | none tagged | no |
| 4 | ⚠️ 1–2 Critical | 1 Critical (F1) | **yes** |
| 5 | ⚠️ active Important weight ≥ gate(level) | L3 gate 3; F2 (1 file) + F5 (1 file) = weight 2 | not reached |
| 6 | ✅ Ready to merge | — | not reached |

Active severity totals exclude waived findings: Critical 1 (F1), Important 2
(F2, F5 — F3 waived), Minor 1 (F4, never verdict-affecting). Both active
Important findings touch one file each, so their summed verdict weight is 2 —
equal to the count, which is why the verdict line carries no weight annotation.

### Important-gate weight

The Important gate is an absolute number fixed by level — 4 at L1–L2, 3 at L3,
2 at L4–L5. The total in-scope file count never moves it. What accumulates
instead is breadth: every active Important finding carries
`verdict_weight = min(affected_files, 3)`, and the weights sum. A grouped
finding stays ONE ID everywhere else on this page — unique IDs, ledger
references, reconciliation — while still contributing its breadth weight here.
Minor, capped-Minor, `[pre-existing]`, and validly waived findings carry no
weight at all.

| Case | Scope | Active Important | Weight | Gate | Verdict |
|------|-------|------------------|-------:|-----:|---------|
| A | L4, 2 files | two findings, one file each | 1 + 1 = 2 | 2 | ⚠️ Needs fixes |
| A′ | L4, 3 files — the third touched by no finding | the same two findings | 1 + 1 = 2 | 2 | ⚠️ Needs fixes, unchanged |
| B | L3, 20 files | one root cause in all 20 | min(20, 3) = 3 | 3 | ⚠️ Needs fixes |

A′ is the reason scope scaling was dropped: widening the scope with a file that
no finding touches moves neither the weight nor the gate, so a review can no
longer dilute its own verdict by enumerating more files.

Case B is one finding with one ID and one remediation, and the ×3 cap is what
it is worth: 3 reaches the gate at L3 (3) and at L4–L5 (2), so it fires ⚠️
Needs fixes on its own there. At L1–L2 the gate is 4, so a lone grouped finding
can never reach it — it needs a second active Important finding. Reaching gate
5 is never Major rework; only gates 2 and 3 are.

Example 1 under this model: F2 and F5 affect one file each, weight 2 against
the L3 gate of 3, so gate 5 does not fire. F3 is grouped across two files and
would carry weight 2 if it were active, but W1 suppresses it and a waived
finding has no verdict weight — which is why F3 needs no weight annotation
anywhere in the report. The ⚠️ comes from gate 4, one active Critical, which is
evaluated first regardless.

### Calibration inputs

| Input | Value used | Effect in Example 1 |
|-------|------------|---------------------|
| Positioning D2 / R3 / C2 | L3 (Internal SDK) | Sets every threshold below |
| DRY total occurrences at L3 | 3 (test code +1; never the first alone) | F3 breaches at the third occurrence: two in `checkout-service.ts`, one in `payment-gateway.ts`; no test-code occurrence, so no +1 |
| Function length at L3 | ≤50 logic lines (×1.5 for test functions only; mechanical error-propagation lines excluded, capped at 50%) | F2 at 62 logic lines breaches; no multiplier applies |
| Parameter count at L3 | ≤5 | `finalizeCheckout` has 3 parameters — not a finding |
| Minor cap | 10 reported, omissions disclosed | 1 Minor reported, 0 omitted, so no `CappedMinor` cell appears |
