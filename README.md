<p align="center">
  <a href="https://github.com/Zhen-Bo/smell-check">
    <img src="assets/smell-check-banner.svg" alt="smell-check: code and test smell audits" width="100%">
  </a>
</p>

<p align="center">
  <a href="SKILL.md">Read the skill docs »</a>
  ·
  <a href="#install">Install</a>
  ·
  <a href="#what-a-report-looks-like">Example report</a>
  ·
  <a href="docs/README.zh-TW.md">繁體中文</a>
</p>

<p align="center">
  <strong>A codebase health check with receipts.</strong><br>
  <code>smell-check</code> is an Agent Skill for AI coding agents.<br>
  It audits the paths you choose for code smells and test smells, and every finding carries its evidence.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://github.com/Zhen-Bo/smell-check/releases"><img src="https://img.shields.io/github/v/release/Zhen-Bo/smell-check?include_prereleases&sort=semver" alt="Release"></a>
  <a href="https://skills.sh/Zhen-Bo/smell-check"><img src="https://skills.sh/b/Zhen-Bo/smell-check" alt="skills.sh installs"></a>
</p>

---

The smells it hunts are the maintainability warnings catalogued in *Refactoring*, *Clean Code*, and the test-smell literature.
It is a health check for a codebase, **not a PR review bot**: no merge advice, no code edits, no test runs.

- **Measured, not vibed.** Structure metrics come from scripts and tools (`wc`, AST counters, `jscpd`) wherever those can run; anything unmeasured is marked `estimate`, never dressed up as fact.
- **Evidence rank on every finding.** `mechanical` (a script counted it), `semantic` (the agent judged it, and the basis is written down), or `estimate` (weak, and says so).
- **Diagnosis, not prescription.** A finding states what is wrong, where, and what it costs maintainers. Fix strategy stays with whoever owns the fix.
- **Static only.** It never edits your code, never executes your code or tests, and never reads gitignored paths.

## What a report looks like

Reports land in `.smell-check/<UTC-timestamp>/`, written in your conversation language. Open `index.html` for the offline report.

```text
.smell-check/20260828-103000Z/
├── index.html             # summary and source-area index
├── summary.md             # canonical manifest and Markdown overview
└── findings/              # Markdown reports of at most 100 findings each
```

Every active finding shows its rule key, source location, verbatim snippet, evidence rank, evidence, and consequence. Dismissed hits keep the exception or judgment that removed them, so you can audit the auditor.

## Why smell-check

Reading *Refactoring* or *Clean Code* changes how you see code.
The effect lasts about a week.
Nobody holds hundreds of pages of judgment in working memory while shipping, and nobody re-reads the book mid-task.

Meanwhile coding agents write more and more of the code, and the people prompting them hold less and less of it in their own heads.
The reading still has to happen; humans just stopped being the ones who can afford to do it.

The books already wrote down how to read a codebase.
`smell-check` turns that into a procedure an agent can execute: measurement instead of memory, evidence instead of impressions, every judgment recorded per finding.
It complements linters, type checkers, and tests; it does not replace them.

## Install

```bash
npx skills add Zhen-Bo/smell-check
```

<details>
<summary>Optional measurement tools</summary>

The skill works with plain `git` + `wc` + Python 3.
Extra tools unlock extra measurements; when absent, the report says so instead of guessing:

| Tool | Unlocks |
| --- | --- |
| `jscpd` (`npm i -g jscpd`) | `code.duplicate-code` clone detection |
| `lizard` (`pip install lizard`) | corroboration of `code.long-function` measurements |
| `node` | TS/JS metrics via the attached script (uses the repo's own `typescript` install) |

</details>

## Run your first audit

The skill asks you to name the scope before scanning, discloses which size profile it picked and why, runs the mechanical and semantic passes, and writes the report bundle.

Ask your agent:

```text
Use the smell-check skill to audit this whole repository.
```

> [!WARNING]
> Whole-repo audits of large codebases consume a lot of tokens, and a long run can outgrow the agent's context window, where early judgments may be lost to compression.
> The skill warns you and asks for confirmation before scanning a large scope, and nothing is silently truncated; if you stop mid-run it writes a `partial` report plus the list of finished paths.

## Size profiles

Thresholds scale with how many people must keep the code readable.
Explicit `profile` in config always wins; otherwise **auto** picks one from the source-code line count of the scope.
Only source code counts, so generated output, vendored bundles, fixtures, lockfiles, markup, and prose are excluded:

| Profile | Fits | e.g. `code.long-function` limit |
| --- | --- | ---: |
| `personal` | personal projects, where running is enough | 100 |
| `small` | in-team tools, roughly 5–20 maintainers | 60 |
| `medium` | products maintained by tens to hundreds | 40 |
| `large` | enterprise codebases, thousands of maintainers | 30 |
| `ultimate` | the strictest workable reading of the books and the test-smell literature; auto never picks it | 20 |

| Source lines in scope | Auto picks |
| ---: | --- |
| 0 – 2,999 | `personal` |
| 3,000 – 14,999 | `small` |
| 15,000 – 74,999 | `medium` |
| ≥ 75,000 | `large` |

## What it checks

**20 stable code rules**

- long functions
- large files
- deep nesting
- long parameter lists
- duplicate code
- duplicated knowledge
- misleading naming
- god classes
- feature envy
- data clumps
- primitive obsession
- shotgun surgery
- divergent change
- message chains
- middle men
- speculative generality
- dead code
- repeated switches
- global data
- magic values

**12 stable test rules**

- assertion-free tests
- assertion roulette
- eager tests
- conditional test logic
- mystery guests
- general fixtures
- ignored tests
- sleepy tests
- order-dependent tests
- sensitive equality
- obscure tests
- non-determinism

Four experimental rules stay off until you enable them one by one in config.
Every rule ships with its exceptions: table-driven test loops, composition roots, wire-boundary DTOs, and similar justified patterns get dismissed with the reason written down, not reported as noise.

## Report anatomy

1. **Index**: repository state, profile, aggregate counts, rule summary, synthesis, source areas, and environment
2. **Finding reports**: active and dismissed findings split into Markdown files by status and source area, capped at 100 per file
3. **Canonical Markdown**: [summary.md](references/report-bundle.md#summary-manifest) holds the run manifest and shard inventory; the model authors one fresh HTML overview from [DESIGN.md](DESIGN.md)
4. **Markdown output**: the summary and every detailed finding report stay readable without an HTML renderer

## Configuration

Optional `.smell-check.toml` at the scan root.
Choices only, no rule text:

```toml
profile = "medium"                 # pin strictness; omit to let auto decide
report_ignore = "git-info-exclude" # or "gitignore" / "none"

exclude = ["vendor/**", "dist/**"]

[rules]
"code.magic-values" = false   # silence a stable rule
"test.over-mocking" = true    # enable an experimental rule

[thresholds]
"code.long-function" = 80     # overrides beat the profile, no questions asked
```

## Package layout

```text
smell-check/
├── SKILL.md              # the audit procedure
├── references/           # rule registries, presets, measurement, configuration, report contract
├── scripts/
│   ├── measure_python.py # Python AST metrics
│   ├── measure_ts.mjs    # TS/JS metrics
│   └── validate_report.py # validates the report bundle
├── assets/
└── DESIGN.md             # design contract for the AI-authored HTML index
```

## FAQ

**Does it change my code?**
No.
Static analysis only; your code and tests are never executed.
It writes the report bundle, and on the first run it asks where to ignore `.smell-check/` (default: `.git/info/exclude`) before touching anything else.

**Does it replace my linter or type checker?**
No.
Keep them; they enforce what can be decided mechanically on every commit.
`smell-check` reads for design-level maintainability warnings, and labels each finding as a measured fact or a judgment call.

**What happens if scanned code contains prompt-injection text?**
Subject content is treated as data, never as instructions.
Instruction-like text inside the scanned code does not change the procedure.

**Which model should run it?**
Whatever your runner uses.
The mechanical baseline is script-measured and model-independent; the semantic pass is only as good as the model you bring.

## License

[MIT](LICENSE)
