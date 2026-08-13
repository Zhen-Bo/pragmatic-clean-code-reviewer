# Presets

Named size profiles for `smell-check`. One central table owns **enable sets** and **numeric thresholds**. How to count, exceptions, and evidence ranks stay in the rule registries and [measurement.md](measurement.md) — this file does not restate them.

## Profiles

| profile | fits |
| --- | --- |
| `personal` | personal projects — running is enough |
| `small` | in-team tools, roughly 5–20 maintainers |
| `medium` | products maintained by tens to hundreds of people |
| `large` | enterprise codebases, thousands of maintainers or more |
| `ultimate` | the strictest workable reading of the source books and the test-smell literature |

Profiles express desired strictness, not a measured fact about the team — a personal project may pin `medium` on purpose for future maintainability. `auto` is not a row here. It only picks one of these five (see [configuration.md](configuration.md)).

## Threshold semantics

- Report only when the measured value is **strictly greater** than the profile threshold.
- Example: `code.long-function` at **medium** uses threshold **40**. A function with **40** counted lines is not reported. **41** is reported.
- Measurement meaning never changes by profile — only the number compared against does.

## Numeric thresholds

Counting definitions live in [measurement.md](measurement.md).

| rule key | metric | personal | small | medium | large | ultimate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `code.long-function` | non-blank, non-comment lines per function | 100 | 60 | 40 | 30 | 20 |
| `code.large-file` | physical lines per source file | 1000 | 600 | 500 | 300 | 200 |
| `code.deep-nesting` | peak nesting depth inside a function | 6 | 4 | 3 | 2 | 1 |
| `code.long-parameter-list` | declared value parameters per callable | 10 | 6 | 4 | 3 | 2 |
| `test.assertion-roulette` | assertion sites per test | 10 | 6 | 4 | 3 | 1 |
| `test.conditional-test-logic` | conditional and loop nodes per test | 5 | 3 | 2 | 1 | 0 |

## No numeric gate

| rule key | reason |
| --- | --- |
| `code.duplicate-code` | Uses the clone-tool minimums fixed in [measurement.md](measurement.md). The threshold does not scale by profile. |
| `test.sleepy-test` | Every hard-wait call site is a mechanical candidate; the semantic pass applies the registry exceptions. |
| `test.general-fixture` | The signal is a **low** consumer-use fraction, not “strictly greater than N”. Estimate plus semantic judgment. |

Other stable rules are on/off only. Experimental rules never enter an enable set by default.

## Enable sets

Every **stable** rule is **on** in all five profiles. Every **experimental** rule is **off** in all five profiles (including any path that resolved via `auto`). Turn experimental rules on only with an explicit per-rule config entry.

### On in every profile (stable)

**code (20):**  
`code.long-function`, `code.large-file`, `code.deep-nesting`, `code.long-parameter-list`, `code.duplicate-code`, `code.duplicated-knowledge`, `code.misleading-naming`, `code.god-class`, `code.feature-envy`, `code.data-clumps`, `code.primitive-obsession`, `code.shotgun-surgery`, `code.divergent-change`, `code.message-chains`, `code.middle-man`, `code.speculative-generality`, `code.dead-code`, `code.repeated-switches`, `code.global-data`, `code.magic-values`

**test (12):**  
`test.assertion-free-test`, `test.assertion-roulette`, `test.eager-test`, `test.conditional-test-logic`, `test.mystery-guest`, `test.general-fixture`, `test.ignored-test`, `test.sleepy-test`, `test.order-dependent-tests`, `test.sensitive-equality`, `test.obscure-test`, `test.non-deterministic`

### Off in every profile (experimental)

`code.missed-reuse`, `code.contract-drift`, `code.patch-accumulation`, `test.over-mocking`
