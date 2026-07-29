# Metrics Inventory

Explanatory inventory of review constants. Operating procedure and authoritative
thresholds live in [SKILL.md](../SKILL.md). This document explains *why* each
constant exists; it is not a second source of truth. If a value here and SKILL.md
disagree, SKILL.md wins.

## Table of Contents

- [Inventory](#inventory)
- [Counting conventions](#counting-conventions)
- [Removed metrics](#removed-metrics)

## Inventory

| Constant | Value | Status | Rationale |
|----------|-------|--------|-----------|
| Function length (L2/L3/L4/L5) | 80 / 50 / 30 / 20 logic lines | Retained (recalibrated, unchanged) | Conversation-starter ceilings by strictness. Count logic lines only (exclude docstrings, comments, blanks). A clear longer function may beat a forced split; exemptions for pure data builders, large match/switch maps, and single-responsibility code that cannot be meaningfully decomposed. |
| Function length ×1.5 multiplier | ceil(base × 1.5); non-stacking; test functions only | New | Applies once for framework-recognized test functions only — the only cohort with an objective membership signal. Does not stack. Parameters, nesting, and other metrics are unaffected. Error-ceremony handling is a subtraction, not a multiplier (see counting conventions). |
| Parameter count (L2/L3/L4/L5) | 7 / 5 / 4 / 3 | Changed (L4 3→4, L5 2→3) | Clean Code CC-147 treats three as a natural ceiling. A legitimate three-argument operation such as `transfer(from, to, amount)` must not be a finding at the strictest levels. L4 and L5 were raised so that three required args stay legal. Count required parameters only when defaults exist. |
| Nesting depth (L2/L3/L4/L5) | 5 / 4 / 3 / 2 | Retained | Depth still scales with strictness. Counting convention updated (see below): body starts at 0; top-level conditional is 1; consecutive guard clauses at depth 1 are excluded so early-return style is not punished. Nesting breaches are Important, not Minor. |
| PR / scope size (L2/L3/L4/L5) | 800 / 500 / 300 / 200 lines | Retained | Soft scope signal for reviewability. At most one `[PROJECT:SCOPE]` finding per review. Severity: Minor at L1–L2, Important at L3–L5. Never tagged `[fundamental]`. |
| DRY total occurrences (L1–L5) | Never / 5 / 3 / 2 / 2 | Changed (L3 4→3, L4 3→2) | Total occurrences including the original. L3 aligns with Rule of Three. L4 matches L5 at 2 for high-consistency codebases. Test code: +1 occurrence before reporting. Never report the first occurrence as duplication. Accidental similarity (different knowledge) is not DRY. |
| Verdict: Critical count | ≥3 → Major rework; 1–2 → Needs fixes | Retained | Critical findings always drive the verdict; volume distinguishes rework from targeted fixes. |
| Verdict: `[fundamental]` tag | Important architecture finding; ≥1 → Major rework | Retained | Marks structural defects that block safe evolution without requiring Critical severity. |
| Verdict: Important threshold | Absolute bases 4 (L1–L2) / 3 (L3) / 2 (L4–L5); each Important finding has `verdict_weight = min(affected_files, 3)`; gate compares sum of weights | Changed | Cap of 3 aligns with the distributed-evidence ≤3-locations limit, so weight never exceeds provable sites. Absolute gates restore monotonicity: total scope size never affects a gate. Worked cases: (1) L4, two single-file findings → weight 2 ≥ 2 → Needs fixes; (2) adding an unaffected 5th file changes nothing; (3) one root cause across 20 files → weight 3, blocks L3–L5, never alone at L1–L2. |
| Finding grouping | Same root cause in ≥2 files → one finding ID; breadth via verdict weight | Changed (from >3) | Grouping compresses the report to one ID; breadth is carried by `verdict_weight = min(affected_files, 3)`, never by counting duplicate findings. |
| Minor cap | 10 reported; omitted counts disclosed | New | Bounds report noise. If more Minor items exist, stop at 10 and state how many were omitted. |
| Batching trigger | >8 files or >1,500 est. LOC | Changed (LOC bound added) | Large scopes must be batched so coverage stays complete and evidence stays local. |
| Batch size | ≤5 files and ≤600 est. LOC; any >600-LOC file is its own batch | Changed | Dual bound prevents oversized batches by file count or size. Context exhaustion yields ⛔ Review incomplete at the batch boundary. |
| Evidence: single site | ≤3 lines quoted | Changed | Verbatim evidence for Critical/Important; short enough to stay auditable. |
| Evidence: distributed | ≤3 locations / ≤6 lines total | Changed | Replaces single-quote-only when the defect spans sites. |
| Evidence: negative | Search scope + absent artifact | Changed | For missing tests, missing validation, etc.: state where you looked and what was absent. |
| Waiver / override expiry | ≤180 days | Retained | Time-boxed relief; Critical findings are never waivable (see SKILL.md). |
| Active waiver tripwire | >10 active | Retained | Signals profile hygiene problems. |
| Suppression tripwire | >30% of candidates suppressed, minimum 10 candidates | New (minimum) | Relative suppression rate only fires when the sample is large enough to mean something. |
| Override bounds | Raise-only, ≤2× default, never beyond L2; L5 DRY not overridable | Retained | Raise-only overrides loosen metric enforcement within bounds (higher thresholds are easier to pass). Never beyond L2; L5 DRY not overridable. |
| Profile staleness | Age >180d, skill_major mismatch, or dominant_language mismatch | Retained | STALE profiles remain usable: report header shows `(stale)` and one non-blocking confirmation. Staleness is not rejection. |
| Level ↔ positioning conflict | Stricter of declared and derived (never L3 fallback); exclusions kept; waivers/overrides revalidated against effective level | Changed | A typo must fail toward strictness, not leniency. Effective level is the stricter candidate; exclusions stay; each waiver and override is revalidated against that level. |
| Effort / Benefit unknown or split | Medium | Retained (intentional) | When evidence does not support High or Low, resolve to Medium rather than inventing precision. |

## Counting conventions

1. **Logic lines only** for function length: exclude docstrings, comments, blank
   lines. Also exclude mechanical error-propagation/cleanup lines (itemized),
   capped at 50% of raw; report as `raw / excluded / counted`. Per-line auditable;
   extends the existing logic-lines exclusion list; removes Go/C false-positive
   family at L4–L5 without a multiplier.
2. **Nesting:** body depth = 0; each nested block increases depth; top-level
   conditional = 1; consecutive guard clauses that remain at depth 1 are excluded
   from the peak count.
3. **Parameters:** count required parameters when defaults are present.
4. **DRY:** count total occurrences of the same knowledge, including the original.
   Test code gets +1 before reporting. Never report a lone first occurrence.
5. **Function length ×1.5:** apply once for framework-recognized test functions
   only; round up; do not stack; function length only. Not for production
   error-ceremony code.

## Removed metrics

| Metric | Status | Rationale |
|--------|--------|-----------|
| Estimated test coverage percentages | Removed | Never estimate a coverage percentage. Report changed behavior that lacks a meaningful test (name file and function). Cite a number only when a real coverage report exists in the repository. |

Smell routing and symptom lookup: [references/quick-lookup.md](../references/quick-lookup.md).
DRY spectrum and Rule of Three context: [references/principles-spectrum.md](../references/principles-spectrum.md).
Level positioning context: [references/positioning.md](../references/positioning.md).
