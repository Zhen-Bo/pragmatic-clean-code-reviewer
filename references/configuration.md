# Configuration

Repo choices for `smell-check` live in one file: **`.smell-check.toml`** at the repository root (or the root of the scan target when that is a nested project).

The file stores **choices only**: which profile, which rules on/off, which numbers to override, which paths to skip, where to ignore the report directory. It must **not** copy rule text, detector definitions, or exception lists — those live in the registries and drift if duplicated.

Threshold meaning and enable-set defaults come from [presets.md](presets.md). Counting rules come from the registries and [measurement.md](measurement.md).

## Schema (minimal)

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `profile` | string | no | One of `personal`, `small`, `medium`, `large`, `ultimate`. Omit to run **auto** (git repos only). |
| `rules` | table: rule key → bool | no | Per-rule on (`true`) / off (`false`). Only way to turn **experimental** rules on. |
| `thresholds` | table: rule key → integer | no | Override the numeric gate for a rule that has a five-value row in [presets.md](presets.md). |
| `exclude` | array of strings | no | Path globs skipped for measurement and judgment (matched against paths relative to the repo / scan root). |
| `report_ignore` | string | no | Where the `.smell-check/` report directory gets ignored: `"git-info-exclude"`, `"gitignore"`, or `"none"`. When set, use it without asking; when absent, the report step asks once (skill body, report file section). |

Unknown keys are ignored with a one-line note in the report environment block (do not fail the run). Rule keys that are not in a registry are ignored the same way.

Valid `profile` values are only the five named presets. The word `auto` is **not** written into the file; auto is what happens when `profile` is absent.

## Example

```toml
# .smell-check.toml — choices only; rule definitions stay in references/
# root keys must come before the first table, or TOML nests them into it

profile = "medium"
report_ignore = "git-info-exclude"

exclude = [
  "vendor/**",
  "**/generated/**",
  "dist/**",
  "**/*.pb.go",
]

[rules]
# stable rules default on; set false to silence one
"code.magic-values" = false
# experimental rules default off; set true to enable
"test.over-mocking" = true

[thresholds]
# overrides beat the profile table
"code.long-function" = 80
```

## Resolver

Build the effective settings in this order. Later steps win.

1. **Load preset** from [presets.md](presets.md) for the effective profile (enable set + five-value thresholds).
2. **Apply `rules`** from the config file: each listed key forces on or off.
3. **Apply `thresholds`** from the config file: each listed key replaces that rule’s number for this run.
4. **Apply `exclude`**: drop matching paths before measure and judge.

### Override priority

User overrides always beat the preset. **Do not question them. Do not warn that they are “too high” or “too low.”**

Example: Config has `profile = "ultimate"` and `[thresholds] "code.long-function" = 80`.  
Preset ultimate for that rule is **20**. Effective threshold is **80**. The preset 20 does not apply.

### Profile selection

| Situation | Effective profile |
| --- | --- |
| `profile` set to a valid name | That name. Auto does not run. |
| `profile` omitted, directory is a git work tree | **auto** precheck (below) picks one of personal / small / medium / large. |
| `profile` omitted, not a git directory | **Stop.** Ask the user to set `profile` explicitly. Do not guess. |
| `profile` set to an unknown string | **Stop.** Ask for a valid name. Do not fall through to auto. |

An explicit `profile` always wins over auto, even when auto would pick a different size.

## Auto precheck

Run only when `profile` is omitted and the target is inside a git work tree.

### Metric (single, deterministic)

**Total source-code lines of the resolved scan file list** — take the git-tracked files inside the user-chosen scope after `exclude` filtering, keep only the files a maintainer edits as code (implementation and test code in any programming language), and count their lines. Data and records stay in the scan list for file-level rules but never enter this count: fixtures, lockfiles, generated output, vendored bundles, markup, and prose.

- Do not count untracked or ignored files.
- Reference POSIX shape — list tracked files in scope, drop `exclude` matches and non-code files from that list, then count (record the real commands and the kept file types in the report environment block):

```bash
git ls-files -z -- <scope-paths> | xargs -0 wc -l   # filter the list to code files first
```

Use the total line figure from `wc -l` (the final “total” line when multiple files; the single count when one file). Equivalent commands on other platforms are fine if they implement the same definition.

If the resolved list is empty or keeps no code files, treat the metric as **0** and continue with the table (personal).

### Line-count → profile map

| Total source lines in scope | Effective profile |
| ---: | --- |
| 0 – 2,999 | `personal` |
| 3,000 – 14,999 | `small` |
| 15,000 – 74,999 | `medium` |
| ≥ 75,000 | `large` |

**`ultimate` is never chosen by auto.** It is a strict profile the user must set on purpose.

### What auto must write into the report

Always state:

1. **effective profile** (the name chosen),
2. **metric value** (total source lines),
3. **decision basis** (which row of the table applied),
4. **source = auto** (so readers see it was not a file pin),
5. a short **suggestion** to pin the profile in `.smell-check.toml`.

Example: No config file (or file without `profile`). Auto runs, report shows e.g. effective profile `small`, lines `7480`, basis `3000–14999 → small`, and suggests writing `profile = "small"`.

## Out of scope here

- How metrics are counted inside functions (registries + [measurement.md](measurement.md)).
- Report file layout (skill body).
- Installing tools or changing subject code.
