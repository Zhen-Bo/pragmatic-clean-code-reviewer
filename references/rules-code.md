# Code family rules

Atomic smell rules for the `code` family. Config keys are the `key` values below. Numeric thresholds live in [presets.md](presets.md), not here — detectors define *what* is counted, never the cut-off.

Classic Fowler/Beck smells form the backbone; Clean Code ch17 heuristics feed semantic judgment only.

**Status:** `stable` may enter presets. `experimental` is off in every profile (including auto) until a config file turns the rule on explicitly.

**Evidence ranks:** mechanical = tool or attached script output; semantic = LLM judgment. Never invent a mechanical number when the tool is missing — skip or mark estimate per [measurement.md](measurement.md).

## Index

| key | status | detectors |
| --- | --- | --- |
| `code.long-function` | stable | mechanical |
| `code.large-file` | stable | mechanical |
| `code.deep-nesting` | stable | mechanical |
| `code.long-parameter-list` | stable | mechanical |
| `code.duplicate-code` | stable | mechanical |
| `code.duplicated-knowledge` | stable | semantic |
| `code.misleading-naming` | stable | semantic |
| `code.god-class` | stable | semantic |
| `code.feature-envy` | stable | semantic |
| `code.data-clumps` | stable | semantic |
| `code.primitive-obsession` | stable | semantic |
| `code.shotgun-surgery` | stable | semantic |
| `code.divergent-change` | stable | semantic |
| `code.message-chains` | stable | semantic |
| `code.middle-man` | stable | semantic |
| `code.speculative-generality` | stable | semantic |
| `code.dead-code` | stable | semantic |
| `code.repeated-switches` | stable | semantic |
| `code.global-data` | stable | semantic |
| `code.magic-values` | stable | semantic |
| `code.missed-reuse` | experimental | semantic |
| `code.contract-drift` | experimental | semantic |
| `code.patch-accumulation` | experimental | semantic |

## Rules

### code.long-function

- **key:** `code.long-function`
- **family:** code
- **status:** stable
- **symptom:** One function body does so much work that a reader cannot hold the whole path in mind. Common signs: many branches, mixed high- and low-level steps, or a name that needs "and" to stay honest.
- **detectors:**
  - **mechanical** — count the function’s non-blank, non-comment lines: physical lines from the declaration through the body, skipping blanks, comment-only lines, and documentation-only lines (full counting contract in [measurement.md](measurement.md)). The attached measure scripts provide the number; `lizard` may only corroborate it. Without a script path, estimate with that counting rule and mark the evidence weaker.
  - **semantic** — statement-packing does not shrink the smell: when several statements share a line (`a; b`, folded one-liners), judge length as if each statement held its own line and mark the finding estimate.
- **exceptions:** Generated code under a declared generated path; thin wrappers that only delegate; framework entrypoints whose length is forced by a single unavoidable protocol (state the protocol).
- **refactoring:** Extract Function — pull a named chunk out so the parent reads as one level of abstraction.
- **source_refs:** CC-20, CC-21, CC-22, CC-180, CC-184
- **principle_refs:** SRP, KISS
- **related:** `code.deep-nesting` (often co-occurs; report both when both breach), `code.god-class` (many long methods may feed a cohesion finding)

### code.large-file

- **key:** `code.large-file`
- **family:** code
- **status:** stable
- **symptom:** A single source file is so large that navigation, review, and ownership cost rise even before class design is judged.
- **detectors:**
  - **mechanical** — count physical lines of the source file (`wc -l` or equivalent). Include blanks and comments; exclude only files outside the scan scope.
- **exceptions:** Generated files; pure data tables or snapshot fixtures that are intentionally monolithic; vendored third-party copies.
- **refactoring:** Move to Another File / Split Module — separate by responsibility or feature boundary, not arbitrary line cuts.
- **source_refs:** CC-107, CC-110
- **principle_refs:** SRP, SoC
- **related:** `code.god-class` (size metric primary is this rule; multi-responsibility primary is `code.god-class` — do not collapse one into the other)

### code.deep-nesting

- **key:** `code.deep-nesting`
- **family:** code
- **status:** stable
- **symptom:** Control structure piles up so far that the happy path is hard to see. Readers track many open branches at once.
- **detectors:**
  - **mechanical** — maximum nesting depth inside a function: function body starts at depth 0; each nested control level (`if`/`else`, loops, `try`/`catch`, `switch`/`match`, `with`, and language equivalents) adds 1. Nested function and class bodies are not walked; they are measured as their own units. Report the peak depth and the innermost location.
- **exceptions:** Nested structure required by a declarative schema or generated state machine; depth driven only by early-guard `if` chains that exit immediately (prefer still flattening when cheap).
- **refactoring:** Replace Nested Conditional with Guard Clauses; Extract Function.
- **source_refs:** CC-22, CC-34, CC-178, CC-184
- **principle_refs:** KISS
- **related:** `code.long-function`

### code.long-parameter-list

- **key:** `code.long-parameter-list`
- **family:** code
- **status:** stable
- **symptom:** A callable asks the caller to supply so many separate arguments that call sites become error-prone and hard to extend.
- **detectors:**
  - **mechanical** — count every declared value parameter once: positional, keyword-only, defaulted / optional, and each variadic rest pack. Exclude the method receiver (`self`/`cls`/`this`) and pure type parameters/generics. A destructured parameter counts as one.
- **exceptions:** Positional APIs fixed by an external standard (C ABI, protocol buffers positional mapping); test helpers that mirror a wide fixture intentionally.
- **refactoring:** Introduce Parameter Object; Preserve Whole Object.
- **source_refs:** CC-26, CC-29, CC-147
- **principle_refs:** KISS
- **related:** `code.data-clumps` (same values traveling together across many signatures → prefer clump finding when the group repeats)

### code.duplicate-code

- **key:** `code.duplicate-code`
- **family:** code
- **status:** stable
- **symptom:** Near-identical token sequences appear in more than one place. Edits risk updating one copy and missing the others.
- **detectors:**
  - **mechanical** — when `jscpd` (or an equivalent token clone detector recorded in the environment block) is present, use its clone groups as candidates: same or near-same token spans above the tool's configured minimum. Record tool name, version, and clone locations. If no clone tool is available, **skip this rule** — do not invent clone percentages with the LLM.
- **exceptions:** Generated pairs that must stay byte-aligned; intentional dual implementations behind a clear compatibility boundary; tests that repeat structure for readability when each case stays tiny.
- **refactoring:** Extract Function; Pull Up Method; Introduce shared module with a domain name (not `Utils`).
- **source_refs:** CC-37, CC-155
- **principle_refs:** DRY
- **related:** `code.duplicated-knowledge` (see dedup below), `code.shotgun-surgery`
- **supersedes:** When the same span is both a token clone and same-knowledge, **primary = `code.duplicate-code`**; suppress `code.duplicated-knowledge` for that span so one symptom is not double-counted.

### code.duplicated-knowledge

- **key:** `code.duplicated-knowledge`
- **family:** code
- **status:** stable
- **symptom:** Two or more places encode the **same business rule or decision** even when the text differs. Changing the rule requires coordinated edits. This is about shared meaning, not similar shape (accidental look-alike code that must diverge stays separate).
- **detectors:**
  - **semantic** — judge change-coupling: same concept, and an edit to one instance would be wrong if the others did not follow. No fixed numeric quota; do not promise a clone percentage.
- **exceptions:** Parallel implementations required by platform boundaries (e.g. client vs server validation) with an explicit single source of truth elsewhere; generated projections of one schema.
- **refactoring:** Extract Function / Module; Replace Dup with single policy object.
- **source_refs:** CC-37, CC-155, PP-15, CA-25
- **principle_refs:** DRY
- **related:** `code.duplicate-code` (token clones), `code.missed-reuse`, `code.shotgun-surgery`
- **dedup:** If `code.duplicate-code` already covers the span, do not also report this rule there. Report this rule only when same-knowledge holds **without** a mechanical clone hit.

### code.misleading-naming

- **key:** `code.misleading-naming`
- **family:** code
- **status:** stable
- **symptom:** A name suggests the wrong behavior, type, or scope — so a safe reader draws a false conclusion. Includes names that hide side effects, interchangeable names for different concepts, and encoded noise that obscures intent.
- **detectors:**
  - **semantic** — compare the name to observed behavior and data flow at use sites. Flag only when the mismatch would change a maintainer's decision.
- **exceptions:** Established domain jargon documented in a project glossary; generated identifiers constrained by an external schema.
- **refactoring:** Rename Method / Rename Variable; Split Phase when one name covers two jobs.
- **source_refs:** CC-4, CC-5, CC-14, CC-25, CC-170, CC-187, CC-193, PP-74
- **principle_refs:** POLA
- **related:** `code.magic-values` (unnamed literals often pair with weak names)

### code.god-class

- **key:** `code.god-class`
- **family:** code
- **status:** stable
- **symptom:** One type or module owns many unrelated reasons to change — a "do-everything" hub. Callers reach into it for unrelated jobs; cohesion is low.
- **detectors:**
  - **semantic** — cluster methods and fields by actor or change reason. Multiple independent responsibilities in one type, or a module that every feature must edit, is the signal. Line count alone is not enough (see `code.large-file`).
- **exceptions:** Framework root types required by the platform; façade deliberately thin over subsystems (then check `code.middle-man` instead if it only forwards).
- **refactoring:** Extract Class; Move Method; Split Module by reason to change.
- **source_refs:** CC-107, CC-110, CC-180, CA-8
- **principle_refs:** SRP, SoC
- **related:** `code.large-file`, `code.long-function`, `code.divergent-change`

### code.feature-envy

- **key:** `code.feature-envy`
- **family:** code
- **status:** stable
- **symptom:** A function spends more time reaching into another type's data than working with its own. The logic "wishes it lived" on the other type.
- **detectors:**
  - **semantic** — count and weigh foreign field/getter usage vs own state in the function body. Envy is about data ownership, not mere collaboration through a narrow interface.
- **exceptions:** Pure formatters/serializers that project foreign data; orchestration layers that intentionally coordinate several types without owning their data.
- **refactoring:** Move Method; Extract Method then Move; Keep a thin adapter on the boundary.
- **source_refs:** CC-164, CC-83
- **principle_refs:** Tell Don't Ask, LoD
- **related:** `code.message-chains`, `code.data-clumps`

### code.data-clumps

- **key:** `code.data-clumps`
- **family:** code
- **status:** stable
- **symptom:** The same small group of values always travels together across parameters, fields, or return tuples — a concept without a name.
- **detectors:**
  - **semantic** — find recurring groups (three or more values, or two values with an invariant between them) that appear together in multiple signatures or types and mean one thing.
- **exceptions:** Positional pairs fixed by math or protocol (coordinates with a standard type already in use); temporary unpacking at a single boundary.
- **refactoring:** Introduce Parameter Object; Extract Class for the clump.
- **source_refs:** CC-29, CC-147
- **principle_refs:** DRY
- **related:** `code.long-parameter-list`, `code.primitive-obsession`

### code.primitive-obsession

- **key:** `code.primitive-obsession`
- **family:** code
- **status:** stable
- **symptom:** Domain ideas are carried as bare strings, numbers, or bools so rules (validation, units, allowed values) scatter and repeat.
- **detectors:**
  - **semantic** — look for primitives that carry domain meaning (ids, money, emails, statuses, units) with repeated validation or formatting at many call sites.
- **exceptions:** True primitives at a serialization edge; performance-critical inner loops with a documented typed boundary outside.
- **refactoring:** Replace Primitive with Object / Value Object; Introduce Parameter Object.
- **source_refs:** CC-175, CC-78
- **principle_refs:** DRY
- **related:** `code.data-clumps`, `code.magic-values`

### code.shotgun-surgery

- **key:** `code.shotgun-surgery`
- **family:** code
- **status:** stable
- **symptom:** One conceptual change forces many tiny edits across scattered files. Miss one site and behavior drifts.
- **detectors:**
  - **semantic** — infer from structure and recent change patterns: the same decision or constant knowledge appears in many modules that must stay aligned. Prefer evidence from repeated parallel edits when git history is in scope; structure alone can still support the finding when coupling is obvious.
- **exceptions:** Deliberate cross-cutting release switches documented as such; multi-package API renames already scripted.
- **refactoring:** Move Method / Move Field to gather the decision; Introduce common module; Inline Class when a split is the cause.
- **source_refs:** PP-14, PP-15, CA-8
- **principle_refs:** DRY, SRP
- **related:** `code.duplicated-knowledge`, `code.divergent-change`, `code.contract-drift`

### code.divergent-change

- **key:** `code.divergent-change`
- **family:** code
- **status:** stable
- **symptom:** One module changes for many unrelated reasons — different features keep reopening the same file for different jobs.
- **detectors:**
  - **semantic** — map change reasons inside the type/module. Two or more independent axes of change (e.g. persistence + UI + billing rules) in one place indicate the smell.
- **exceptions:** Composition roots and wiring modules whose job is to host many reasons by design (still flag if business rules leak in).
- **refactoring:** Extract Class; Split Module along change axes.
- **source_refs:** CC-110, CA-8
- **principle_refs:** SRP
- **related:** `code.god-class` (often the same hub; primary for "many responsibilities now" is `code.god-class`; primary for "many change axes over time" is this rule — pick one primary per hub, mention the other in related evidence), `code.shotgun-surgery`

### code.message-chains

- **key:** `code.message-chains`
- **family:** code
- **status:** stable
- **symptom:** Call sites walk a long path of intermediate objects (`a.b().c().d()` style — a "train wreck"). Callers know too much about the graph and break when the middle shape changes.
- **detectors:**
  - **semantic** — flag chains that expose intermediate structure across a boundary the caller should not own. Short fluent builders inside one type are not chains.
- **exceptions:** Fluent DSLs designed as one expression; test builders local to tests.
- **refactoring:** Hide Delegate; Extract Method on the owner; Introduce façade method.
- **source_refs:** CC-80, CC-81, CC-186, PP-46
- **principle_refs:** LoD
- **related:** `code.feature-envy`, `code.middle-man`

### code.middle-man

- **key:** `code.middle-man`
- **family:** code
- **status:** stable
- **symptom:** A type mostly forwards calls to another type and adds little policy of its own — an extra hop without behavior.
- **detectors:**
  - **semantic** — most public methods are pure delegates; little or no extra logic, validation, or composition.
- **exceptions:** Required boundaries (security proxy, remote stub, binary compatibility shim) that exist for a non-logic reason stated in code or docs.
- **refactoring:** Remove Middle Man; Inline Class; keep a thin interface only when the boundary is real.
- **source_refs:** CC-158, PP-53
- **principle_refs:** YAGNI, KISS
- **related:** `code.message-chains`, `code.speculative-generality`

### code.speculative-generality

- **key:** `code.speculative-generality`
- **family:** code
- **status:** stable
- **symptom:** Abstractions, parameters, or extension points exist for imagined futures and are unused — or only one implementation ever appears with no second need.
- **detectors:**
  - **semantic** — unused type parameters, empty interface hierarchies, strategy hooks with a single hard-coded path, or config flags that never change behavior.
- **exceptions:** Stability contracts required by a published public API; plugin points already loaded by external in-repo plugins.
- **refactoring:** Collapse Hierarchy; Inline Class; Remove Parameter; Dead Code Elimination.
- **source_refs:** CC-129, CC-130, PP-43
- **principle_refs:** YAGNI, KISS
- **related:** `code.dead-code`, `code.middle-man`

### code.dead-code

- **key:** `code.dead-code`
- **family:** code
- **status:** stable
- **symptom:** Code that can never run, or is never referenced, still ships — including commented-out blocks left as false history.
- **detectors:**
  - **semantic** — unreachable branches, always-false guards, unreferenced private helpers, and large commented-out regions. Optional static unused-symbol tools may support evidence when present; without them, do not claim machine-proof unused exports across dynamic languages.
- **exceptions:** Entry points reached by reflection/DI registration with clear markers; feature-flagged paths that are off but scheduled and tested.
- **refactoring:** Delete dead code (VCS keeps history); Remove Parameter; Empty Method removal.
- **source_refs:** CC-58, CC-144, CC-150, CC-159, CC-162
- **principle_refs:** YAGNI, KISS
- **related:** `code.speculative-generality`

### code.repeated-switches

- **key:** `code.repeated-switches`
- **family:** code
- **status:** stable
- **symptom:** The same discrimination on a type or status is copied across many `switch`/`match`/`if-else` chains. Adding a variant means hunting every chain.
- **detectors:**
  - **semantic** — find repeated branching on the same enum/status/type tag in multiple places that must stay aligned.
- **exceptions:** A single exhaustive switch at a system boundary; switches over third-party enums you do not control where polymorphism is unavailable.
- **refactoring:** Replace Conditional with Polymorphism; Introduce Strategy; centralize the decision once.
- **source_refs:** CC-24, CC-173
- **principle_refs:** OCP, DRY
- **related:** `code.shotgun-surgery`, `code.duplicated-knowledge`

### code.global-data

- **key:** `code.global-data`
- **family:** code
- **status:** stable
- **symptom:** Mutable process-wide state (globals, singletons with writable fields, hidden module state) lets distant code interfere. Order of writes becomes part of the contract.
- **detectors:**
  - **semantic** — writable module-level state shared across features; singletons that accumulate mutable fields; ambient context that tests must reset globally.
- **exceptions:** Process-true constants; framework-owned application context constructed once at bootstrap and treated as read-only after init; logging sinks.
- **refactoring:** Parameterize Method; Replace Global with explicit context object; wrap required globals behind a narrow API.
- **source_refs:** PP-47, PP-48, PP-50, PP-57
- **principle_refs:** DIP
- **related:** `code.shotgun-surgery`

### code.magic-values

- **key:** `code.magic-values`
- **family:** code
- **status:** stable
- **symptom:** Bare literals carry domain meaning (timeouts, limits, statuses, multipliers) so readers cannot tell why the number exists and edits miss siblings.
- **detectors:**
  - **semantic** — literals that encode policy, not obvious identity values (`0`, `1`, `-1`, empty string) used in a clear local way. Repeated identical policy literals strengthen the case.
- **exceptions:** Mathematical identities; test data that is intentionally concrete; literals required by a wire protocol shown next to a named constant map.
- **refactoring:** Replace Magic Number with Named Constant; Introduce Value Object when rules attach to the value.
- **source_refs:** CC-175
- **principle_refs:** DRY, KISS
- **related:** `code.primitive-obsession`, `code.duplicated-knowledge`

### code.missed-reuse

- **key:** `code.missed-reuse`
- **family:** code
- **status:** experimental
- **symptom:** The repo already contains a suitable helper, type, or module, yet a new copy of the behavior was added nearby. Common after multi-file agent edits that never searched for an existing seam.
- **detectors:**
  - **semantic** — match new logic to existing in-repo utilities with the same responsibility and compatible interface. Require a concrete existing symbol path as evidence; do not flag mere stylistic similarity.
- **exceptions:** Deliberate isolation for dependency direction; experimental forks marked temporary; performance-specialized copies with measured justification.
- **refactoring:** Reuse existing module; Extract and redirect callers; Delete the new copy.
- **applicability:** Most valuable on multi-file changes in medium+ repos with shared libraries.
- **source_refs:** PP-15, PP-16
- **principle_refs:** DRY
- **related:** `code.duplicated-knowledge`, `code.duplicate-code`
- **notes:** Default **off** in all profiles. Enable only via config.

### code.contract-drift

- **key:** `code.contract-drift`
- **family:** code
- **status:** experimental
- **symptom:** Two sides of a contract (producer/consumer, schema/handler, client/server DTO, route/handler params) no longer agree — field names, nullability, units, or error shapes diverged across files.
- **detectors:**
  - **semantic** — compare paired definitions and use sites across files for incompatible assumptions. Cite both sides. Not a substitute for typed codegen when the project already has a single schema source.
- **exceptions:** Versioned dual-read/dual-write windows that are explicit and time-bounded; intentionally separate public vs internal models with adapters.
- **refactoring:** Align to one source of truth; Introduce Adapter; shared schema or type package.
- **applicability:** Cross-file and cross-package boundaries; JSON/API edges without codegen.
- **source_refs:** PP-37, CC-89
- **principle_refs:** DIP
- **related:** `code.shotgun-surgery`, `code.duplicated-knowledge`, `test.assertion-free-test` (weak tests often hide drift)
- **notes:** Default **off** in all profiles. Enable only via config.

### code.patch-accumulation

- **key:** `code.patch-accumulation`
- **family:** code
- **status:** experimental
- **symptom:** A unit grows by stacked special cases — extra flags, end-of-function patches, "one more if" for each incident — instead of a redesign around the real rule. Often left by successive narrow fixes.
- **detectors:**
  - **semantic** — long functions or modules dominated by incident-shaped branches (`if special_customer`, `if legacy_path`) that share little structure, with comments or names pointing at past firefights.
- **exceptions:** Regulated rule tables that are inherently case lists; state machines encoded as explicit transitions.
- **refactoring:** Replace Conditional with Polymorphism; Extract Rule table; Recompose with a clearer model.
- **applicability:** Hot files with many recent small edits.
- **source_refs:** CC-21, CC-165, PP-65
- **principle_refs:** KISS, SRP
- **related:** `code.long-function`, `code.divergent-change`, `code.repeated-switches`
- **notes:** Default **off** in all profiles. Enable only via config.
