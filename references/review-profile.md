# Review Profile Specification

Authoritative schema and rules for the per-project review profile. A profile
persists calibration so a review can skip the questionnaire, and it records
deliberate project decisions: excluded paths, numeric threshold overrides, and
scoped waivers.

A profile changes calibration only. It never reduces mandatory breadth,
completeness accounting, or evidence requirements.

## Table of Contents

- [Location and Discovery](#location-and-discovery)
- [Schema](#schema)
- [Field Reference](#field-reference)
- [Worked Example](#worked-example)
- [Validity](#validity)
- [Waivers](#waivers)
- [Threshold Overrides](#threshold-overrides)
- [Precedence](#precedence)
- [Consent and Persistence](#consent-and-persistence)

---

## Location and Discovery

| Role | Path |
|------|------|
| **Canonical** | `docs/code-review-profile.md` |
| **Fallback** | `.code-review-profile.md` (project root) |

Discovery order is canonical first, then fallback. If both files exist, use the
canonical `docs/` file and disclose the duplicate in the report header. The
canonical file wins; the fallback is ignored, not merged.

Profiles live in the target project under review.

---

## Schema

YAML frontmatter plus a short markdown body.

```yaml
---
schema: 1
skill: pragmatic-clean-code-reviewer
skill_major: 2
level: L3
positioning: { D: D2, R: R3, C: C2 }
dominant_language: python
last_confirmed: 2026-07-29
exclude:
  - "generated/**"
threshold_overrides:
  - id: T1
    metric: function_length
    value: 80
    paths: ["src/legacy/**"]
    rationale: "Legacy adapter functions are decomposed in a separate migration"
    approver: "a.mercer"
    created: 2026-07-29
    expires: 2026-12-01
waivers:
  - id: W1
    point: C2
    paths: ["src/legacy/exporters/**"]
    rationale: "Duplication retained until the exporter migration lands"
    approver: "a.mercer"
    created: 2026-07-29
    expires: 2026-12-01
---
```

The markdown body carries two optional sections:

```markdown
# Review Profile

## Rationale

Why this level and positioning fit the project.

## Accepted Debt

Human context only. Accepted-debt prose never suppresses a finding; only a
valid waiver entry does that.
```

---

## Field Reference

| Field | Required | Role |
|-------|----------|------|
| `schema` | yes | Profile document schema version. Current value: `1` |
| `skill` | yes | Must be `pragmatic-clean-code-reviewer` |
| `skill_major` | yes | Skill major version the profile was written for. Current value: `2` |
| `level` | yes | `L1`–`L5`. Must match the level derived from `positioning` |
| `positioning` | yes | Canonical D/R/C codes from [positioning.md](positioning.md) |
| `dominant_language` | yes | Primary language of the reviewed code at last confirmation. Selects the profile's language adjustments and is checked against the reviewed scope |
| `last_confirmed` | yes | ISO date of the last human confirmation |
| `exclude` | no | Path globs dropped from default scope. A file the user names explicitly is still reviewed; the exclusion is disclosed instead |
| `threshold_overrides` | no | Raise specific numeric thresholds for matching paths |
| `waivers` | no | Suppress reporting of specific findings for matching paths |

`positioning.C` is present only for the combinations that ask Q3, meaning
(D2 or D3) with (R3 or R4). Omit it otherwise.

---

## Worked Example

The example in [Schema](#schema) is the canonical worked profile:

- `positioning: D2 / R3 / C2` maps to **L3** in the lookup table, and `level`
  states `L3`. The profile is valid.
- Override `T1` raises `function_length` for `src/legacy/**` from the L3 default
  of 50 to 80. That is within 2× the level default (100) and no more permissive
  than the L2 value (80), so it is legal.
- Waiver `W1` names one checklist point, a bounded path glob, a rationale, an
  approver, a creation date, and an expiry 125 days later. L3 permits a
  self-approved waiver; this one names a person anyway.

---

## Validity

### Conflicted: level disagrees with positioning

If `level` does not equal the level derived from `positioning` through the
lookup table in [positioning.md](positioning.md), the profile is **conflicted**.
A conflicted profile is still used. It is never rejected wholesale, and this
case never falls back to the questionnaire or to L3.

1. The **effective level is the stricter of the two candidates**: the higher one
   on the L1→L5 scale. A profile stating `L2` whose positioning derives L4 is
   reviewed at L4.
2. The report header names both candidates and carries the marker
   `profile conflict: stricter level selected`, with the profile path.
3. The review raises exactly one **Important** governance finding, headed
   `[PROJECT:SCOPE]` with `Point: A1`, naming the stated level and the derived
   level.
4. `exclude` globs stay active. Scope exclusion does not depend on the level.
5. Every waiver and threshold override is **revalidated against the effective
   level**: approver not `self` at L4–L5, expiry, bounded scope, and the numeric
   caps measured against the effective level's defaults. The rules are the ones
   in [Waivers](#waivers) and [Threshold Overrides](#threshold-overrides); only
   the level they are measured against changes. Each entry that fails is
   suspended on its own, with the consequence its own rule already defines;
   entries that still pass stay active.

The skill never rewrites a profile to resolve the conflict. Correcting the
stored file needs the same explicit consent as any other profile write, so the
header disclosure and the governance finding repeat on every review until the
stored profile is fixed.

### Stale: usable but labeled

A profile is **stale** when any of the following holds:

- `last_confirmed` is more than 180 days old.
- `skill_major` does not match this skill's major version.
- `dominant_language` does not match the dominant language of the reviewed
  scope.

A stale profile still applies. The report header labels the source `(stale)`
with the reason, and the review asks one non-blocking confirmation question.
Staleness never blocks or delays the review.

---

## Waivers

A waiver suppresses **reporting**, never **checking**. The Coverage Ledger cell
for the point still records the outcome, in the form `C2:Waived:F3/W1`, naming
the finding and the waiver that suppressed it.

Waived findings appear in the Waiver Disclosure section and in Coverage
Reconciliation counts. They do not count toward verdict severity totals.

### Required fields

Every waiver must carry: `id`, exactly one checklist `point`, bounded `paths`
glob(s), `rationale`, `approver`, `created`, and `expires`.

### Rules

| Rule | Effect |
|------|--------|
| Expiry | `expires` is at most 180 days after `created`. An expired waiver is inactive and its finding is reported normally |
| Approver at L4–L5 | Must not be `self`. A self-approved waiver at these levels is invalid: it is inactive, the finding is reported, and an **Important** governance finding is raised |
| Blanket scope | `**`, an unbounded path, or a category-wide/whole-domain waiver is invalid: the finding is reported and an **Important** governance finding is raised |
| Critical findings | Never waivable. A waiver targeting one is ignored, the finding is reported, and a **Critical** governance finding is raised |
| Volume tripwire | More than 10 active waivers raises an **Important** waiver-abuse finding, unconditionally |
| Suppression tripwire | More than 30% of candidate findings suppressed raises an **Important** waiver-abuse finding, evaluated only when there are at least 10 candidate findings |

An invalid waiver never silently degrades into a valid one. The underlying
finding is always reported.

---

## Threshold Overrides

An override changes a numeric threshold for matching paths. It never changes
severity definitions, verdict gates, domain breadth, evidence requirements, or
completeness accounting.

### Overridable metrics

Only these five, using these exact ids:

`function_length` · `parameter_count` · `nesting_depth` · `dry_occurrences` ·
`pr_scope_size`

Any other `metric` value is invalid and the override is ignored.

### Bounds

| Rule | Effect |
|------|--------|
| Raise only | An override may only loosen a threshold. A profile cannot tighten one |
| 2× cap | The value is at most twice the level default for that metric |
| L2 floor | The value is never more permissive than the L2 value for that metric |
| L5 duplication | `dry_occurrences` is not overridable at L5 |
| Governance | Same required fields as waivers: `id`, `rationale`, `approver`, `created`, `expires` (≤180 days), plus `metric`, `value`, and bounded `paths` |
| Expiry | An expired override is inactive: the level default applies and the attempted use is disclosed, like an expired waiver |
| Approver at L4–L5 | Must not be `self`. A missing or `self` approver at these levels leaves the override inactive, the level default applies, and an **Important** governance finding is raised |
| Disclosure | Every applied override is listed in the report, like waivers |

An override that breaks a bound is ignored, the level default applies, and the
report discloses the rejection.

A session instruction may tighten a threshold below the level default. That is
a session-level decision and does not modify the profile.

---

## Precedence

```
explicit session instruction
  > valid profile
  > questionnaire answers
  > disclosed L3 fallback
```

A conflicted profile still occupies the profile position in this chain: it
calibrates at its effective level under [Validity](#validity) instead of
dropping through to the questionnaire.

Precedence affects calibration, thresholds, and emphasis only. It never affects
mandatory breadth, completeness accounting, evidence requirements, or Critical
findings.

---

## Consent and Persistence

1. **Discover** before asking the questionnaire.
2. **Use** a valid profile: skip the questionnaire, and print the level, the
   positioning source, and the profile path in the report header.
3. **Offer to save** once, after a questionnaire. Write the file only after
   explicit user consent.
4. **Never write** into this skill's own repository. Profiles belong to the
   target project.
5. **Never persist** a disclosed L3 fallback. A fallback is a guess, not a
   calibration.
6. **Update** dates, waivers, and overrides when the project's risk posture
   changes.

---

## Related

- Questionnaire, lookup table, level definitions, thresholds:
  [positioning.md](positioning.md)
- User-facing summary: [docs/review-profile.md](../docs/review-profile.md)
- Report examples including waived findings:
  [report-example.md](report-example.md)
