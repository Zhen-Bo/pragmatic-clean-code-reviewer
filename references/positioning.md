# Project Positioning System

Determine the appropriate strictness level through a 3+4+2 questionnaire system.

## Table of Contents

- [Quick Assessment Flow](#quick-assessment-flow)
- [Question Definitions](#question-definitions)
- [Complete Mapping Table](#complete-mapping-table)
- [Level Definitions](#level-definitions)
- [Strictness Matrix](#strictness-matrix)
- [Metric Thresholds](#metric-thresholds)

---

## Quick Assessment Flow

```
Q1: Who uses this code? (3 options)
│
├── D1: Solo
├── D2: Internal
└── D3: External
        │
        ▼
Q2: What standard? (4 options)
│
├── R1: Ship
├── R2: Normal
├── R3: Careful
└── R4: Strict
        │
        ▼
┌─────────────────────────────────────────────────
│ CONDITIONAL: Only ask Q3 if (D2 or D3) + (R3 or R4)
└─────────────────────────────────────────────────
        │
        ▼
Q3: How critical? (2 options)
│
├── C1: Normal
└── C2: Critical
```

---

## Question Definitions

### Q1: Who will use this code?

| Code | Label | Description | Examples |
|------|-------|-------------|----------|
| **D1** | 🧑 Solo | Only myself | Personal scripts, experiments |
| **D2** | 👥 Internal | Team/company internal | Internal tools, SDKs |
| **D3** | 🌍 External | External users/open source | Products, OSS libraries |

### Q2: What standard do you want?

| Code | Label | Description | Mindset |
|------|-------|-------------|---------|
| **R1** | 🚀 Ship | Just make it work | "Demo tomorrow" |
| **R2** | 📦 Normal | Basic quality | "Standard development" |
| **R3** | 🛡️ Careful | Careful review | "This matters" |
| **R4** | 🔒 Strict | Highest standard | "Zero tolerance" |

### Q3: How critical is this code? (Conditional)

> **Only asked when:** (D2 or D3) AND (R3 or R4)

| Code | Label | Description | Impact if broken |
|------|-------|-------------|------------------|
| **C1** | 🔧 Normal | General feature | Can wait for fix |
| **C2** | 💎 Critical | Core dependency | Causes outage or significant loss |

---

## Complete Mapping Table

### D1: Solo (No Q3 needed)

| Q1 | Q2 | Q3 | Level | Typical Case |
|----|----|----|-------|--------------|
| D1 | R1 | - | **L1** | Experiment script |
| D1 | R2 | - | **L1** | Personal utility |
| D1 | R3 | - | **L2** | Personal long-term project |
| D1 | R4 | - | **L3** | Personal perfectionist project |

### D2: Internal

| Q1 | Q2 | Q3 | Level | Typical Case |
|----|----|----|-------|--------------|
| D2 | R1 | - | **L1** | Team quick prototype |
| D2 | R2 | - | **L2** | Team daily development |
| D2 | R3 | C1 | **L2** | Internal helper tool |
| D2 | R3 | C2 | **L3** | Internal SDK |
| D2 | R4 | C1 | **L3** | Internal tool (high standard) |
| D2 | R4 | C2 | **L4** | Internal core infrastructure |

### D3: External

| Q1 | Q2 | Q3 | Level | Typical Case |
|----|----|----|-------|--------------|
| D3 | R1 | - | **L2** | Product MVP |
| D3 | R2 | - | **L3** | General product feature |
| D3 | R3 | C1 | **L3** | Small OSS tool |
| D3 | R3 | C2 | **L4** | Product core feature |
| D3 | R4 | C1 | **L4** | OSS tool (high standard) |
| D3 | R4 | C2 | **L5** | Finance/Medical/Core OSS infra |

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

## Strictness Matrix

| Check Item | L1 | L2 | L3 | L4 | L5 |
|------------|----|----|----|----|-----|
| Functional correctness | ★★★ | ★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |
| Error handling | ★ | ★★ | ★★★ | ★★★★ | ★★★★★ |
| Naming & readability | ★ | ★★★ | ★★★★ | ★★★★★ | ★★★★★ |
| Architecture design | ☆ | ★ | ★★★ | ★★★★★ | ★★★★★ |
| Test coverage | ☆ | ★ | ★★★ | ★★★★ | ★★★★★ |
| API stability | ☆ | ☆ | ★★ | ★★★★★ | ★★★★★ |
| Backward compatibility | ☆ | ☆ | ★ | ★★★★★ | ★★★★★ |
| Documentation | ☆ | ★ | ★★ | ★★★★ | ★★★★★ |
| Security | ☆ | ★ | ★★ | ★★★ | ★★★★★ |

---

## Metric Thresholds

### Code Metrics

| Metric | L1 | L2 | L3 | L4 | L5 |
|--------|-----|-----|-----|-----|-----|
| Function length | N/A | ≤80 | ≤50 | ≤30 | ≤20 |
| Parameter count | N/A | ≤7 | ≤5 | ≤3 | ≤2 |
| Nesting depth | N/A | ≤5 | ≤4 | ≤3 | ≤2 |
| PR size (lines) | N/A | ≤800 | ≤500 | ≤300 | ≤200 |
| Test coverage | N/A | 30% | 60% | 80% | 95% |
| DRY tolerance (max repeats) | N/A | 4 | 3 | 2 | 1 |

### Quality Gates

| Gate | L1 | L2 | L3 | L4 | L5 |
|------|----|----|----|----|-----|
| Linter pass | Optional | Required | Required | Required | Required |
| Type check | Optional | Optional | Required | Required | Required |
| Unit tests | None | Some | Core paths | Comprehensive | Complete |
| Integration tests | None | None | Optional | Required | Required |
| Security scan | None | None | Optional | Required | Required + audit |
| Code review | None | Self | 1 person | 2+ people | Team + security |

---

## Statistics

| Item | Value |
|------|-------|
| Total options | 3 + 4 + 2 = 9 |
| Valid combinations | 20 |
| Average questions | 2.3 |
| Output levels | L1-L5 (5 levels) |

---

## Decision Flowchart

```
                    START
                      │
                      ▼
        ┌─────────────────────────┐
        │ Q1: Who uses this code? │
        └─────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
        D1           D2           D3
       Solo       Internal     External
         │            │            │
         ▼            ▼            ▼
        ┌─────────────────────────┐
        │ Q2: What standard?      │
        └─────────────────────────┘
                      │
      ┌───────┬───────┼───────┬───────┐
      ▼       ▼       ▼       ▼       │
     R1      R2      R3      R4       │
    Ship   Normal  Careful  Strict    │
      │       │       │       │       │
      │       │       ▼       ▼       │
      │       │   ┌───────────────┐   │
      │       │   │ Q3: Critical? │◄──┘
      │       │   │ (D2/D3 only)  │
      │       │   └───────────────┘
      │       │         │
      │       │    ┌────┴────┐
      │       │    ▼         ▼
      │       │   C1        C2
      │       │  Normal   Critical
      │       │    │         │
      ▼       ▼    ▼         ▼
        ┌─────────────────────────┐
        │    LOOKUP TABLE         │
        │    → L1, L2, L3, L4, L5 │
        └─────────────────────────┘
```

---

## Fix Effort & Benefit

For each Critical and Important issue, assess two dimensions to help teams prioritize fix order. These dimensions are supplementary information — they never change the severity of an issue.

### Effort (how hard to fix)

| Rating | Description | Examples |
|--------|-------------|----------|
| **Low** | A few lines changed, < 30 min | Swap string concat for parameterized query, add input validation, rename variable |
| **Medium** | Moderate refactor, 30 min - 4 h | Extract parameter object, split function, add error handling layer |
| **High** | Architectural change or wide-reaching modification, > 4 h | Redesign module boundaries, change data flow, replace framework component |

### Benefit (value gained after fixing)

Benefit combines **trigger frequency** (how often users hit the issue) and **impact scope** (how bad it is when triggered).

| Rating | Trigger Frequency | Impact Scope | Examples |
|--------|-------------------|--------------|----------|
| **High** | Hot path / every request | Data loss, security breach, full outage | SQL injection on login endpoint, null pointer in request handler |
| **Medium** | Common but not every request, OR edge case + severe | Feature malfunction, partial user impact | Missing validation on settings page, race condition under load |
| **Low** | Edge case / specific conditions | UI glitch, degraded experience | Parameter count smell in internal helper, naming issue in rarely-called function |
