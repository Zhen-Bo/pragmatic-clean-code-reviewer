# Measurement protocol

Authoritative definitions for mechanical metrics in smell-check. Registry rules name *what* to count; this file names *how* to count, which layer produces the number, and how absence degrades. **Never invent a mechanical number when the tool or script that should produce it is missing.** Threshold cut-offs live in [presets.md](presets.md), not here.

Static analysis only: **do not** build, compile, or execute subject code (including its tests).

## Candidate table (all layers)

Scripts and shell recipes emit the same TSV shape, one row per measurement:

| column | meaning |
| --- | --- |
| `rule` | rule key or metric key (`code.long-function`, `test.assertion-sites`, …) |
| `location` | `path:line` (1-based line of the symbol or match) |
| `symbol` | function/method qualname, test label, or `-` for file-level rows |
| `value` | non-negative integer (or duration ms when noted) |

- **Encoding:** UTF-8, `\t` separators, `\n` line endings, no header row.
- **Sort (fixed):** `rule` ascending, then `location`, then `symbol`, then `value`. Same input → same bytes.
- **Paths:** forward slashes; prefer paths relative to the scan root when known.
- Optional filters on attached scripts: `--threshold-lines N`, `--threshold-nesting N`, `--threshold-params N` keep only rows with `value > N` for the matching rule. No filter → full dump.

Metric keys emitted by attached scripts:

| metric key | feeds rule(s) |
| --- | --- |
| `code.long-function` | `code.long-function` |
| `code.deep-nesting` | `code.deep-nesting` |
| `code.long-parameter-list` | `code.long-parameter-list` |
| `test.assertion-sites` | `test.assertion-free-test`, `test.assertion-roulette` |
| `test.gate-nodes` | `test.conditional-test-logic` |

File-level and grep-level rows use the rule key directly (`code.large-file`, `test.ignored-test`, `test.sleepy-test`, `code.duplicate-code`).

## Three layers

Use the first layer in this table that can produce a real measurement for that language and metric. Record the layer and tool identity in the report **environment** block.

| layer | when | evidence label |
| --- | --- | --- |
| 1. shell | file lines, skip markers, hard-wait greps; `jscpd` when the environment has it, otherwise `code.duplicate-code` skips | mechanical |
| 2. attached scripts | Python via `scripts/measure_python.py`; TS/JS via `scripts/measure_ts.mjs` when subject has `typescript` | mechanical |
| 3. LLM estimate | no script/tool path applies | estimate (weak) — never labeled mechanical |

Commands below are **POSIX reference implementations**. Other environments may use equivalents that implement the same definition; write the command actually used into environment.

### Probe every run

Before measuring, probe presence and version (include absences):

```sh
command -v python3 && python3 --version
command -v node && node --version
command -v lizard && lizard --version
command -v jscpd && jscpd --version
# subject-repo typescript (from scan root):
node -e "const r=require('module').createRequire(process.cwd()+'/package.json'); console.log(r('typescript/package.json').version)"
```

- Missing tool → degrade or skip that metric; state the reason in environment.
- **Never** propose installation in the report body. Optional install/remove commands live only in the “Optional tools” section of this file (and user docs that quote it).

## Metric definitions

### `code.long-function` — non-blank, non-comment lines

- **Count:** physical lines belonging to the function, from its declaration line (decorators excluded) through the end of its body. Skip blank lines, comment-only lines, and documentation-only lines (docstrings, doc comments). A statement spanning several physical lines counts each of those lines. Several statements packed onto one line still count as one line; the semantic detector in [rules-code.md](rules-code.md) judges packed code.
- **Nested functions:** a nested statement-bodied function, and any function bound to a name where it is declared (including arrow and function-expression initializers), is its own unit — its declaration line counts as one line of the outer function and its body is excluded. An anonymous single-expression function (lambda, expression-bodied callback) counts inline in the enclosing function.
- **Layer:** Python → `measure_python.py`; TS/JS with subject `typescript` → `measure_ts.mjs`; else estimate. `lizard` may only corroborate the script numbers (record its version when cited); it never replaces them, because its counting differs in detail.

### `code.deep-nesting` — max nesting depth

- Function body starts at depth **0**. Each nested control structure (`if`/`else`, loops, `try`/`catch`, `switch`/`match`, `with`) enters depth+1. Report peak depth and location of the function.
- Nested function/class bodies are **not** walked as deeper control of the outer function.
- **Layer:** same scripts as long-function; else estimate.

### `code.long-parameter-list` — declared value parameters

- Count every declared value parameter once: positional, keyword-only, defaulted / optional, and each variadic pack (`*args`, `**kwargs`, `...rest`).
- **Exclude:** the receiver (`self`/`cls`/`this`) and pure type parameters.
- A destructured parameter counts as one parameter.
- **Layer:** attached scripts; else estimate.

### `code.large-file` — physical lines

- Count physical lines of the source file (blanks and comments included).
- **Layer 1 reference:**

```sh
# emit: code.large-file  path:1  -  LINECOUNT
wc -l <path>
```

### `code.duplicate-code` — token clones

- Mechanical **only** when `jscpd` is present. Otherwise **skip** the rule (see [rules-code.md](rules-code.md)); do not LLM-fake clone percentages.
- Fixed jscpd flags for reproducible candidates (override only if environment records the change):

```sh
jscpd --min-lines 5 --min-tokens 50 --reporters json --silent <scope>
```

- Map each clone group to rows: `code.duplicate-code`, first file `path:line`, symbol `-`, value = duplicated line count (or token count if lines unavailable). Sort as usual. Record jscpd version.

### `test.assertion-sites`

- Per test function/method (name starts with `test`, or `it`/`test` callback in JS frameworks): count assertion sites — language `assert` statements, framework assert/expect calls, `pytest.raises` (and peers), mock verification calls (`assert_called*`, `toHaveBeenCalled*`, and peers). **One site per call expression** (for `expect(x).toBe(y)`, count the matcher call once). Assertion sites inside functions declared within the test body still count toward that test.
- Feeds `test.assertion-free-test` (value 0) and `test.assertion-roulette` (high value; message density is semantic).
- **Layer:** `measure_python.py` / `measure_ts.mjs` for those languages; else estimate.

### `test.gate-nodes`

- Per test body: count conditional and loop nodes that can gate or skip asserts: `if`/`elif`/`else`, loops, `switch`/`match`, and conditional expressions (`x if c else y`, `c ? a : b`). Nested statement-bodied function bodies excluded.
- Feeds `test.conditional-test-logic`.
- **Layer:** same scripts; else estimate.

### `test.ignored-test` — skip markers (shell)

Fixed patterns (extend only by editing this list; keep sorted output):

| family | pattern (extended regex) |
| --- | --- |
| Python | `@unittest\.skip` / `@unittest\.skipIf` / `@unittest\.skipUnless` / `@pytest\.mark\.skip` / `@pytest\.mark\.skipif` |
| JS/TS | `\bit\.skip\b` / `\bdescribe\.skip\b` / `\btest\.skip\b` / `\bxit\b` / `\bxtest\b` / `\bxdescribe\b` |
| Java etc. | `@Ignore\b` / `@Disabled\b` / `@EnabledIf` |
| General | `\bpending\b` (RSpec-style) |

```sh
# reference: list matches as test.ignored-test  path:line  -  1
rg -n --no-heading -e '@unittest\.skip' -e '@pytest\.mark\.skip' -e '\bit\.skip\b' -e '\bdescribe\.skip\b' -e '\btest\.skip\b' -e '\bxit\b' -e '\bxtest\b' -e '\bxdescribe\b' -e '@Ignore\b' -e '@Disabled\b' -e '@EnabledIf' -e '\bpending\b' <scope>
```

Semantic pass still judges empty/stale reasons.

### `test.sleepy-test` — hard waits (shell)

| pattern |
| --- |
| `\btime\.sleep\s*\(` |
| `\basyncio\.sleep\s*\(` |
| `\bThread\.sleep\s*\(` |
| `\bsetTimeout\s*\(` |
| `\bsetInterval\s*\(` |
| `\bsleep\s*\(` (shell/ruby-ish; confirm test path) |
| `\bwaitForTimeout\s*\(` |
| `\bpage\.waitForTimeout\s*\(` |

```sh
rg -n --no-heading -e 'time\.sleep\s*\(' -e 'asyncio\.sleep\s*\(' -e 'Thread\.sleep\s*\(' -e 'setTimeout\s*\(' -e 'setInterval\s*\(' -e 'waitForTimeout\s*\(' -e '\bsleep\s*\(' <scope>
```

Emit `test.sleepy-test  path:line  -  1` (or duration ms in `value` when the first arg is a literal number). Every hit is a mechanical candidate; there is no numeric gate (see [presets.md](presets.md)).

### Test-family mechanical map (honest)

| rule | shell | measure_python.py | measure_ts.mjs | other languages |
| --- | --- | --- | --- | --- |
| `test.assertion-free-test` / `test.assertion-roulette` | — | assertion-sites | assertion-sites | LLM estimate |
| `test.conditional-test-logic` | — | gate-nodes | gate-nodes | LLM estimate |
| `test.ignored-test` | skip-marker grep | — | — | same grep patterns |
| `test.sleepy-test` | hard-wait grep | — | — | same grep patterns |
| `test.general-fixture` | — | — | — | **LLM estimate only** (fixture-name liveness needs semantic use-graph; not in attached scripts) |
| remaining test rules | — | — | — | semantic / estimate per registry |

## Attached scripts

### Python — [measure_python.py](../scripts/measure_python.py)

- Stdlib only (`ast`).
- Usage:

```sh
python3 scripts/measure_python.py [--threshold-lines N] [--threshold-nesting N] [--threshold-params N] <files.py...>
python3 scripts/measure_python.py --self-check
```

### TypeScript / JavaScript — [measure_ts.mjs](../scripts/measure_ts.mjs)

- Zero package dependencies of its own. Resolves `typescript` from the **subject repo** (`createRequire` on subject `package.json` / `node_modules/typescript`).
- If `node` or `typescript` is missing: exit non-zero with a clear stderr message; audit degrades TS/JS function metrics to estimate and records the reason. Do not install packages into the subject repo.
- Usage:

```sh
node scripts/measure_ts.mjs [--root SUBJECT_ROOT] [--threshold-lines N] [--threshold-nesting N] [--threshold-params N] <files...>
node scripts/measure_ts.mjs --self-check
```

## Optional tools (detect-only)

Do not auto-install. If the operator already has them, use and record versions.

### lizard (function metrics)

```sh
# install (operator machine)
pipx install lizard
# remove
pipx uninstall lizard
```

When present, use only to corroborate script output for long-function; the registry metric always comes from the attached scripts. Record lizard’s version when cited.

### jscpd (duplicate-code)

```sh
# install
npm install -g jscpd
# remove
npm uninstall -g jscpd
```

Defaults locked above. No jscpd → skip `code.duplicate-code` mechanical candidates.

## Environment block (report appendix)

Fixed field set for every report. Use this template:

```markdown
## Environment

- time_utc: <ISO-8601>
- skill_version: <tag or commit>
- execution_model: <host agent name>
- partial: <false | true; if true, list unfinished paths>
- tools:
  - python3: <version | absent>
  - node: <version | absent>
  - typescript_subject: <version | absent>
  - lizard: <version | absent>
  - jscpd: <version | absent>
- commands_run:
  - <exact command line 1>
  - <exact command line 2>
- degradations:
  - <metric or rule>: <reason>   # e.g. code.duplicate-code: jscpd absent → skipped
```

Rules:

- Every mechanical number in findings must trace to a listed command or script invocation.
- Absences are first-class: write `absent`, not silence.
- `partial: true` when the run stopped early; list what was finished.

## Layer 3 — LLM estimate

When only layer 3 applies:

- Follow the same counting definitions above as closely as the language allows.
- Label evidence **estimate** (weak), never mechanical.
- Prefer skip over a fake precision for clone detection (`code.duplicate-code`).
