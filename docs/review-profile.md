# Review Profile

A review profile stores your project's calibration so the reviewer can skip the
positioning questionnaire and print where its settings came from. It also
records path exclusions, raised numeric thresholds, and scoped waivers.

The profile lives in **your project**, not in this skill's repository:

- Canonical path: `docs/code-review-profile.md`
- Fallback path: `.code-review-profile.md`

If both exist, the canonical file is used and the duplicate is disclosed in the
report header.

## Minimal example

```yaml
---
schema: 1
skill: pragmatic-clean-code-reviewer
skill_major: 2
level: L3
positioning: { D: D2, R: R3, C: C2 }
dominant_language: python
last_confirmed: 2026-07-29
---
```

`level` must match the level the `positioning` codes map to. If it does not, the
whole profile is rejected and the review says so.

The reviewer offers to create this file after a questionnaire and writes it only
with your consent.

## Related

- Authoritative schema, waiver rules, and threshold-override bounds:
  [references/review-profile.md](../references/review-profile.md)
- Questionnaire and level lookup:
  [references/positioning.md](../references/positioning.md)
