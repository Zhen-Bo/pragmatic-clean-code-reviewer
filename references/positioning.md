# Project Positioning System

Determines the review strictness level (L1–L5) from a 3+4+2 questionnaire.

This file is the canonical source for the questionnaire wording, the D/R/C
option codes, the 16-row level lookup, the level definitions, and the
Effort/Benefit calibration questions. SKILL.md loads this file during
calibration.

[SKILL.md](../SKILL.md) is the operating source for metric thresholds and
protocol rules; its inline tables win where the threshold tables below disagree.
[docs/metrics.md](../docs/metrics.md) is the explanatory rationale inventory.

## Table of Contents

- [Assessment Flow](#assessment-flow)
- [Question Definitions](#question-definitions)
- [Level Lookup Table](#level-lookup-table)
- [Level Definitions](#level-definitions)
- [Profile Consistency Rule](#profile-consistency-rule)
- [Metric Thresholds](#metric-thresholds)
- [Test Coverage](#test-coverage)
- [Quality Gates](#quality-gates)
- [Fix Effort and Benefit](#fix-effort-and-benefit)
- [Effort and Benefit Calibration Questions](#effort-and-benefit-calibration-questions)

---

## Assessment Flow

```
Q1: Who will use this code? (3 options)
│
├── D1: Solo
├── D2: Internal
└── D3: External
        │
        ▼
Q2: What standard do you want? (4 options)
│
├── R1: Ship
├── R2: Normal
├── R3: Careful
└── R4: Strict
        │
        ▼
┌─────────────────────────────────────────────────
│ CONDITIONAL: ask Q3 only if (D2 or D3) AND (R3 or R4)
└─────────────────────────────────────────────────
        │
        ▼
Q3: How critical is this code? (2 options)
│
├── C1: Normal
└── C2: Critical
        │
        ▼
┌─────────────────────────┐
│ LOOKUP TABLE            │
│ → L1, L2, L3, L4, L5    │
└─────────────────────────┘
```

Two questions answer most projects; a third applies to internal or external
code held to a careful or strict standard.

---

## Question Definitions

The D/R/C identifiers below are the canonical values stored in a project
profile's `positioning` field (see
[references/review-profile.md](review-profile.md)).

### Q1: Who will use this code?

| Code | Label | Description | Examples |
|------|-------|-------------|----------|
| **D1** | Solo | Only myself | Personal scripts, experiments |
| **D2** | Internal | Team/company internal | Internal tools, SDKs |
| **D3** | External | External users/open source | Products, OSS libraries |

### Q2: What standard do you want?

| Code | Label | Description | Mindset |
|------|-------|-------------|---------|
| **R1** | Ship | Just make it work | "Demo tomorrow" |
| **R2** | Normal | Basic quality | "Standard development" |
| **R3** | Careful | Careful review | "This matters" |
| **R4** | Strict | Highest standard | "Zero tolerance" |

### Q3: How critical is this code? (conditional)

> Asked only when: (D2 or D3) AND (R3 or R4).

| Code | Label | Description | Impact if broken |
|------|-------|-------------|------------------|
| **C1** | Normal | General feature | Can wait for a fix |
| **C2** | Critical | Core dependency | Causes an outage or significant loss |

---

## Level Lookup Table

Sixteen valid combinations. Rows without a Q3 code never ask Q3.

| Q1 | Q2 | Q3 | Level | Typical Case |
|----|----|----|-------|--------------|
| D1 | R1 | — | **L1** | Experiment script |
| D1 | R2 | — | **L1** | Personal utility |
| D1 | R3 | — | **L2** | Personal long-term project |
| D1 | R4 | — | **L3** | Personal perfectionist project |
| D2 | R1 | — | **L1** | Team prototype |
| D2 | R2 | — | **L2** | Team daily development |
| D2 | R3 | C1 | **L2** | Internal helper tool |
| D2 | R3 | C2 | **L3** | Internal SDK |
| D2 | R4 | C1 | **L3** | Internal tool, high standard |
| D2 | R4 | C2 | **L4** | Internal core infrastructure |
| D3 | R1 | — | **L2** | Product MVP |
| D3 | R2 | — | **L3** | General product feature |
| D3 | R3 | C1 | **L3** | Small OSS tool |
| D3 | R3 | C2 | **L4** | Product core feature |
| D3 | R4 | C1 | **L4** | OSS tool, high standard |
| D3 | R4 | C2 | **L5** | Finance, medical, or core OSS infrastructure |

**Canonical worked example: D2 / R3 / C2 → L3.** Documentation, report samples,
and profile examples use these codes when they need a concrete L3 case.

---

## Level Definitions

| Level | Name | Key Question | Typical Projects |
|-------|------|--------------|------------------|
| **L1** | 🧪 Lab | Does it run? | Experiments, throwaway scripts |
| **L2** | 🛠️ Tool | Can I understand it next month? | Personal tools, team prototypes |
| **L3** | 🤝 Team | Can teammates take over? | Team projects, small OSS |
| **L4** | 🚀 Infra | Will others suffer if I break it? | Internal SDK, core services, popular OSS |
| **L5** | 🏛️ Critical | Can it pass audit? | Finance, medical, critical infrastructure |

### Level Characteristics

| Level | API Stability | Backward Compat | Documentation | Review Required |
|-------|---------------|-----------------|---------------|-----------------|
| L1 | None | None | None | Optional |
| L2 | Informal | None | Minimal | Self |
| L3 | Documented | Best effort | README + comments | 1 reviewer |
| L4 | Semver | Migration path | Full API docs | 2+ reviewers |
| L5 | Strict semver | Mandatory | Complete + audit trail | Team + security |

---

## Profile Consistency Rule

A profile's `level` must equal the level derived from its `positioning` codes
through the lookup table above. Disagreement does not reject the profile. The
review runs at the **stricter** of the two candidates — the higher one on the
L1→L5 scale — and never at an L3 fallback for this case.

The header discloses both candidates, one Important A1 governance finding is
raised, `exclude` globs stay active, and every waiver and threshold override is
revalidated against the effective level. Full handling is defined in
[references/review-profile.md](review-profile.md).

---

## Metric Thresholds

| Metric | L1 | L2 | L3 | L4 | L5 |
|--------|-----|-----|-----|-----|-----|
| Function length (logic lines) | N/A | ≤80 | ≤50 | ≤30 | ≤20 |
| Parameter count | N/A | ≤7 | ≤5 | ≤4 | ≤3 |
| Nesting depth | N/A | ≤5 | ≤4 | ≤3 | ≤2 |
| PR / scope size (lines) | N/A | ≤800 | ≤500 | ≤300 | ≤200 |
| DRY duplication (report at total occurrences) | N/A | 5 | 3 | 2 | 2 |

Notes:

- DRY counts **total occurrences**, including the original. In test files the
  reporting threshold is the level value **plus one**, because fixture-shaped
  repetition is often clearer than a shared helper.
- Measurement rules and exemptions live in [docs/metrics.md](../docs/metrics.md).
- Thresholds may be raised for specific paths through profile
  `threshold_overrides`; the bounds are defined in
  [references/review-profile.md](review-profile.md).

---

## Test Coverage

Coverage percentages are CI targets, never review measurements. The review never
estimates a percentage and never asserts one from reading code.

The review reports changed behavior that lacks a meaningful test, naming the
file and the function. Cite a numeric coverage value only when an actual
coverage report exists in the repository, and attribute it to that report.

---

## Quality Gates

| Gate | L1 | L2 | L3 | L4 | L5 |
|------|----|----|----|----|-----|
| Linter pass | Optional | Required | Required | Required | Required |
| Type check | Optional | Optional | Required | Required | Required |
| Unit tests | None | Some | Core paths | Core + edge paths | All paths |
| Integration tests | None | None | Optional | Required | Required |
| Security scan | None | None | Optional | Required | Required + audit |
| Code review | None | Self | 1 person | 2+ people | Team + security |

---

## Fix Effort and Benefit

For each Critical and Important issue, assess two dimensions to help teams
prioritize fix order. These dimensions are supplementary information. They never
change the severity of an issue.

### Effort (how hard to fix)

| Rating | Description | Examples |
|--------|-------------|----------|
| **Low** | A few lines changed, < 30 min | Swap string concat for parameterized query, add input validation, rename variable |
| **Medium** | Moderate refactor, 30 min – 4 h | Extract parameter object, split function, add error handling layer |
| **High** | Architectural change or wide-reaching modification, > 4 h | Redesign module boundaries, change data flow, replace framework component |

### Benefit (value gained after fixing)

Benefit combines **trigger frequency** (how often users hit the issue) and
**impact scope** (how bad it is when triggered).

| Rating | Trigger Frequency | Impact Scope | Examples |
|--------|-------------------|--------------|----------|
| **High** | Hot path / every request | Data loss, security breach, full outage | SQL injection on login endpoint, null pointer in request handler |
| **Medium** | Common but not every request, OR edge case + severe | Feature malfunction, partial user impact | Missing validation on settings page, race condition under load |
| **Low** | Edge case / specific conditions | UI glitch, degraded experience | Parameter count smell in internal helper, naming issue in rarely-called function |

---

## Effort and Benefit Calibration Questions

Reason through these questions before assigning ratings.

For Effort:

- How many files need changes? (1 file = likely Low, 3+ files = likely Medium+)
- Does the fix cross module or layer boundaries? (yes = Medium+)
- Does existing test coverage need updating? (significant test changes = add one level)

For Benefit:

- Is this code on a hot path (called frequently)? (yes = High trigger frequency)
- What is the worst-case consequence if this issue triggers? (data loss or security = High impact)
- Can users work around it? (no workaround = higher impact)

If the evidence is unknown or genuinely split, resolve to **Medium**. This
default is intentional: it keeps an unresearched guess from inflating or
deflating a fix priority. Express reasoning as 1–3 nested bullets under each
rating line, derived from these questions. Do not use generic justifications.
