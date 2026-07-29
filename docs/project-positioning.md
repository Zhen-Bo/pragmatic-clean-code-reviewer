# Project Positioning Guide

Human-oriented guide to the 3+4+2 questionnaire and L1–L5 levels.

**Canonical sources** (do not duplicate tables here):

- Question options, D/R/C → level mapping, level definitions, metric thresholds,
  Effort/Benefit calibration:
  [references/positioning.md](../references/positioning.md)
- Persisting answers as a project profile:
  [review-profile.md](review-profile.md) and
  [references/review-profile.md](../references/review-profile.md)

## What Positioning Does

Positioning chooses **how strict** the review is: which numeric thresholds apply,
which checklist points are gated by level, and how aggressive Important-count
verdict gates are. It never shrinks mandatory breadth — every active checklist
point is still scanned.

Precedence (session → profile → questionnaire → disclosed L3 fallback) is defined
in [references/review-profile.md](../references/review-profile.md). Profile
settings may change thresholds and emphasis only.

## How to Choose Quickly

1. **Who uses the code?** Solo / internal team / external or OSS.
2. **What standard do you want?** Ship / normal / careful / strict.
3. **How critical if broken?** Asked only when the audience is internal or
   external *and* the standard is careful or strict.

If you skip calibration, the skill uses **L3 Team** and discloses that fallback
in the report header. Guesses are never written to a profile file.

## Level Intent (narrative)

### L1 🧪 Lab

- **Key Question:** Does it run?
- **Use Case:** Experiments, throwaway scripts
- **Focus:** Just make it work

### L2 🛠️ Tool

- **Key Question:** Will I understand this next month?
- **Use Case:** Personal tools, internal utilities
- **Focus:** Basic readability and error handling

### L3 🤝 Team

- **Key Question:** Can a teammate take this over?
- **Use Case:** Team projects, shared codebases
- **Focus:** Clean code, documentation, tests

### L4 🚀 Infra

- **Key Question:** Will others suffer if this breaks?
- **Use Case:** Internal SDKs, shared infrastructure
- **Focus:** Failure handling, API design, tests across core and edge paths

### L5 🏛️ Critical

- **Key Question:** Can this pass a security/compliance audit?
- **Use Case:** Financial systems, medical software, core OSS
- **Focus:** Maximum rigor, security, compliance

## Related

- Feature overview: [features.md](features.md)
- Metrics measurement rules: [metrics.md](metrics.md)
- Full AI contract: [SKILL.md](../SKILL.md)
