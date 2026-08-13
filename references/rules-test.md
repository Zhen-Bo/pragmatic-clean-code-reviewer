# Test family rules

Registry of test smells for `smell-check`. Load when auditing automated tests.

Each rule is one config key. Detector text defines *what* to measure and *how*; numeric cutoffs live only in the central preset table ([presets.md](presets.md)). Experimental rules stay off in every profile (including `auto`) until the config file turns them on one by one.

## Index

| key | status | detectors |
| --- | --- | --- |
| `test.assertion-free-test` | stable | mechanical + semantic |
| `test.assertion-roulette` | stable | mechanical + semantic |
| `test.eager-test` | stable | semantic |
| `test.conditional-test-logic` | stable | mechanical + semantic |
| `test.mystery-guest` | stable | semantic |
| `test.general-fixture` | stable | estimate + semantic |
| `test.ignored-test` | stable | mechanical + semantic |
| `test.sleepy-test` | stable | mechanical |
| `test.order-dependent-tests` | stable | semantic |
| `test.sensitive-equality` | stable | semantic |
| `test.obscure-test` | stable | semantic |
| `test.non-deterministic` | stable | semantic |
| `test.over-mocking` | experimental | semantic |

## Rules

### `test.assertion-free-test`

- **key:** `test.assertion-free-test`
- **family:** test
- **status:** stable
- **symptom:** A test runs setup and calls production code, but never checks a result. The suite stays green even if the behavior under the name breaks. (Also called empty test when the body has no checks at all.)
- **detectors:**
  - **mechanical:** In each test function or method body, count assertion sites: framework assert/expect calls, `pytest.raises` / equivalent exception matchers, and mock-verification calls (`assert_called*`, `toHaveBeenCalled*`, and peers). Count one site per call expression. Report candidates with zero sites.
  - **semantic:** Confirm the body is not a deliberate “must not throw” smoke with that intent in the name or a one-line comment; confirm it is not a shared helper misclassified as a test.
- **exceptions:** Generators or parametrize wrappers that only yield cases; abstract base test methods meant for subclasses; tests whose only job is “construction does not raise” when the name states that and no stronger check is feasible.
- **refactoring:** Introduce Assertion
- **source_refs:** CC-102, CC-106, alias Empty Test
- **principle_refs:** F.I.R.S.T. Self-validating
- **related:** `test.over-mocking` (mock-only checks still count as assertion sites here; prefer over-mocking when the gap is “only doubles were checked”)

### `test.assertion-roulette`

- **key:** `test.assertion-roulette`
- **family:** test
- **status:** stable
- **symptom:** One test piles many checks with no messages or structure. When it fails, the reader cannot tell which expectation broke or why that expectation matters.
- **detectors:**
  - **mechanical:** Per test function, count assertion sites (same definition as `test.assertion-free-test`). The preset table supplies the comparison value.
  - **semantic:** Judge whether a failure would still point at the broken expectation — explicit messages, matcher descriptions, or one readable story (table-driven cases, fluent multi-field object checks) — or a bag of unrelated expectations.
- **exceptions:** Single structured equality on one object or snapshot; framework-native multi-field matchers that fail with field-level detail; generated property cases that re-use one named assertion helper.
- **refactoring:** Extract Method (split named checks) or Split Test
- **source_refs:** CC-104, CC-105
- **related:** `test.eager-test` (when many asserts map to several behaviors, eager-test is primary)

### `test.eager-test`

- **key:** `test.eager-test`
- **family:** test
- **status:** stable
- **symptom:** One test exercises several independent behaviors or scenarios. A single failure mixes causes; the name cannot describe what actually broke.
- **detectors:**
  - **semantic:** Read arrange / act / assert blocks. Flag when the body covers more than one distinct outcome, rule, or user-visible path that could stand alone as its own test name. Multiple asserts on one outcome of one act are not this smell.
- **exceptions:** One scenario that must prove several linked post-conditions of a single transaction; end-to-end path tests that intentionally walk a pipeline and name that path.
- **refactoring:** Split Test
- **source_refs:** CC-104, CC-105
- **related:** `test.assertion-roulette` (eager-test primary when the root issue is multiple concepts)

### `test.conditional-test-logic`

- **key:** `test.conditional-test-logic`
- **family:** test
- **status:** stable
- **symptom:** The test branches with `if` / `else` or loops that may skip checks. Some paths never assert, so a broken case can exit green.
- **detectors:**
  - **mechanical:** In test bodies, count conditional and loop nodes that can gate assertion sites: `if`/`elif`/`else`, `switch`/`match`, `for`/`while`, and conditional expressions. Count each such node once per test.
  - **semantic:** Distinguish data-driven loops that always assert once per case from branches that can skip the check entirely.
- **exceptions:** Parametrize / table loops that run the same assert for every row; environment guards that skip the whole test through the framework’s skip API (see `test.ignored-test`); language-required try/finally for cleanup that does not guard the assert.
- **refactoring:** Split Test or Guard Assertion moved to framework skip
- **source_refs:** CC-106
- **related:** `test.assertion-free-test` (path with zero asserts → assertion-free primary for that path)

### `test.mystery-guest`

- **key:** `test.mystery-guest`
- **family:** test
- **status:** stable
- **symptom:** The test depends on a file, database row, server, clock, or other outsider that the body never sets up or names. Readers cannot see the full input; failures look random.
- **detectors:**
  - **semantic:** Trace values used in acts and asserts back to setup in the same test, fixture, or explicit factory. Flag hidden reliance on repo paths, global env, live services, or shared DB state not created in the visible arrange phase.
- **exceptions:** Contract or integration suites whose fixture module documents and owns the external resource; hermetic testcontainers or ephemeral sandboxes created in setup and torn down in the same module.
- **refactoring:** In-line Setup or Fresh Fixture
- **source_refs:** PP-67, PP-69
- **principle_refs:** F.I.R.S.T. Independent, Repeatable
- **related:** `test.general-fixture`, `test.non-deterministic`

### `test.general-fixture`

- **key:** `test.general-fixture`
- **family:** test
- **status:** stable
- **symptom:** Shared setup builds a large world, but each test uses only a thin slice. Setup cost and coupling rise; changing one field breaks unrelated tests.
- **detectors:**
  - **estimate** (no attached script measures fixture-name liveness): For a shared fixture (module/class `setup` / `beforeEach` / fixture function), list names it defines. Per consumer test, count how many of those names the body reads. Candidates are fixtures where most consumers touch only a small fraction of defined names.
  - **semantic:** Confirm the unused bulk is real data construction, not harmless shared constants or one-liners.
- **exceptions:** Minimal shared graph required by the domain (e.g. one user + one org) when every test needs the whole graph; immutable constants and pure factories with no heavy I/O.
- **refactoring:** Fresh Fixture or Implicit Setup narrowed to Parameterized Creation Method
- **source_refs:** CC-100, CC-106
- **related:** `test.mystery-guest`, `test.order-dependent-tests`

### `test.ignored-test`

- **key:** `test.ignored-test`
- **family:** test
- **status:** stable
- **symptom:** A test is skipped, disabled, or marked expected-fail with no clear open question and no plan to restore it. The suite pretends coverage that is not enforced.
- **detectors:**
  - **mechanical:** Find skip/disable markers (`@unittest.skip`, `@pytest.mark.skip`, `it.skip`, `xtest`, `test.skip`, `Ignore`, `Disabled`, `pending`, and peers) and count each marked test once.
  - **semantic:** Read the skip reason. Flag markers with empty, placeholder, or stale reasons and no linked issue or expiry.
- **exceptions:** Skip tied to an open issue id or explicit temporary reason with owner; platform/feature gates that skip only when a capability is absent and say so.
- **refactoring:** Fix and re-enable, or delete the test and record the gap elsewhere
- **source_refs:** CC-197, CC-154
- **principle_refs:** F.I.R.S.T. Timely

### `test.sleepy-test`

- **key:** `test.sleepy-test`
- **family:** test
- **status:** stable
- **symptom:** The test waits with a fixed sleep or long timeout instead of a condition. Runs are slow and still flake when the machine is busy.
- **detectors:**
  - **mechanical:** In test bodies and test-only helpers, count hard-wait calls (`sleep`, `time.sleep`, `Thread.sleep`, `setTimeout` used only to delay, `asyncio.sleep` without a predicate, and peers). Count each call site once; record the duration argument when present. Every hard-wait call site is a mechanical candidate; there is no numeric gate.
  - **semantic:** n/a for primary detection; use semantic only to drop intentional pacing demos outside CI unit suites if path excludes already missed them.
- **exceptions:** Chaos or load harnesses that model real wall-clock delays; tests of the sleep API itself.
- **refactoring:** Replace wait with deterministic clock, fake scheduler, or condition-based wait
- **source_refs:** CC-202, CC-106
- **principle_refs:** F.I.R.S.T. Fast, Repeatable
- **related:** `test.non-deterministic` (sleepy-test is primary when the only issue is fixed sleep)

### `test.order-dependent-tests`

- **key:** `test.order-dependent-tests`
- **family:** test
- **status:** stable
- **symptom:** A test passes only when another test ran first, or when module-level mutable state still holds a prior value. Reordering or running alone turns green to red.
- **detectors:**
  - **semantic:** Look for shared mutable module/class state written by one test and read by another; reliance on insertion order of global registries; missing teardown after mutations. Prefer evidence from code structure over running the suite (skill must not execute subject tests).
- **exceptions:** Explicit suite-level scenarios documented as ordered integration scripts outside unit folders; transactional fixtures that reset between tests.
- **refactoring:** Fresh Fixture; isolate shared state
- **source_refs:** CC-106
- **principle_refs:** F.I.R.S.T. Independent
- **related:** `test.general-fixture`, `test.non-deterministic`

### `test.sensitive-equality`

- **key:** `test.sensitive-equality`
- **family:** test
- **status:** stable
- **symptom:** The test compares full string forms of objects (`toString`, `repr`, locale-formatted numbers, full HTML dumps) instead of the fields that matter. Harmless formatting changes break the suite.
- **detectors:**
  - **semantic:** Flag equality asserts whose expected side is a brittle rendered string of a structured value, or whose actual side is `str(obj)` / `repr(obj)` / formatted dump when field-level checks would do.
- **exceptions:** Pure string APIs under test (serializers, CLI output, golden files owned as the contract); snapshot tests stored and reviewed as artifacts.
- **refactoring:** Compare meaningful fields or use a dedicated equality helper
- **source_refs:** CC-102
- **related:** `test.obscure-test`

### `test.obscure-test`

- **key:** `test.obscure-test`
- **family:** test
- **status:** stable
- **symptom:** Readers cannot tell what behavior is protected. Names do not state the scenario; setup is a wall of noise; asserts bury the point.
- **detectors:**
  - **semantic:** Judge whether a competent reader can answer “what breaks if this test fails?” from the name and body in one short pass. Flag opaque names (`test1`, `works`, `edge`), copy-pasted noise, and missing arrange/act/assert shape when the domain needs it.
- **exceptions:** Generated names from a clear parametrize id list; characterization tests labeled as such while legacy behavior is captured.
- **refactoring:** Rename Test; Extract Method for domain helpers
- **source_refs:** CC-100, CC-102, CC-103
- **related:** `code.misleading-naming` (production names → code family; test names and test readability → this rule)
- **principle_refs:** F.I.R.S.T. Self-validating

### `test.non-deterministic`

- **key:** `test.non-deterministic`
- **family:** test
- **status:** stable
- **symptom:** The same test can pass or fail without code changes—time, timezone, locale, network, random seeds, or leftover process state leak into the result. (Often called flaky when CI shows intermittent red.)
- **detectors:**
  - **semantic:** Trace sources of nondeterminism: live clock, unseeded random, real network/DNS, unordered set iteration used in asserts, residual files/ports. Do not run the suite; reason from static use of those sources without fakes.
- **exceptions:** Explicit property or fuzz tests with fixed seeds recorded in the test; integration suites that accept environmental limits and isolate them behind markers.
- **refactoring:** Introduce Test Stub / Fake Clock; seed and pin environment
- **source_refs:** CC-106, CC-139
- **principle_refs:** F.I.R.S.T. Repeatable
- **related:** `test.sleepy-test` (primary when fixed sleep is the sole cause), `test.order-dependent-tests` (primary when shared mutable state is the sole cause), `test.mystery-guest`

### `test.over-mocking`

- **key:** `test.over-mocking`
- **family:** test
- **status:** experimental
- **default:** off in every profile including `auto`; enable only via explicit per-rule config
- **symptom:** Tests replace almost every collaborator with test doubles and assert only that mocks were called. Real outputs, parsing, and error paths stay unproven. Green tests can hide a broken implementation of the unit’s own logic.
- **detectors:**
  - **semantic:** For each test module (file) or, when clearer, each service/SUT the module targets, estimate the share of tests whose asserts land only on mock call history (`assert_called_with`, `toHaveBeenCalledWith`, and peers) with no check of return values, thrown domain errors, or parsed structures. **Reporting unit:** one finding per test module or per SUT—not one finding per test method. List every contributing test location under that single finding as evidence.
  - **mechanical:** none (no reliable cross-language mock metric without execution)
- **exceptions:** Pure delegation adapters whose only job is to forward to a port; boundary tests that intentionally lock an HTTP path or message shape; hexagonal ports where the double *is* the contract under test.
- **refactoring:** Replace Test Double with Real Object for pure logic; keep doubles at true I/O edges
- **applicability:** Highest noise risk; treat as a coverage-shape signal, not an automatic “delete these tests” list
- **source_refs:** PP-67, PP-92, CA-48
- **principle_refs:** F.I.R.S.T. Self-validating
- **related:** `test.assertion-free-test` (zero asserts → assertion-free; mock-only asserts → this rule)
