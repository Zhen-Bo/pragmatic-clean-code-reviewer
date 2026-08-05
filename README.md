<h1 align="center">Pragmatic Code Review</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Pragmatic%20Programmer-Applied-orange?style=for-the-badge&logo=bookstack" alt="Pragmatic Programmer — Applied">
  <img src="https://img.shields.io/badge/Clean%20Code-Applied-brightgreen?style=for-the-badge&logo=checkmarx" alt="Clean Code — Applied">
  <img src="https://img.shields.io/badge/Clean%20Architecture-Applied-blue?style=for-the-badge&logo=blueprint" alt="Clean Architecture — Applied">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Beyond%20the%20Books-Current%20Primary%20Sources-9cf?style=flat-square" alt="Beyond the Books — Current Primary Sources">
  <img src="https://img.shields.io/badge/License-MIT-blueviolet?style=flat-square" alt="License — MIT">
</p>

<p align="center">
  <strong>An Agent Skill for code and architecture review — for Claude Code, Codex, OpenCode, and compatible Agent Skills runners.</strong>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#eight-rule-packs">Rule Packs</a> •
  <a href="#review-flow">Review Flow</a> •
  <a href="#findings">Findings</a> •
  <a href="#known-limitations">Limitations</a> •
  <a href="#license">License</a>
</p>

---

## Before you use this skill

> [!WARNING]
> **Token cost.** This skill consumes significantly more tokens than a normal review skill. It loads all eight Rule Packs, reads every in-scope file completely, and keeps an Auditable Review Trace through the conversation. Plan for that cost.

> [!CAUTION]
> **Large scopes and context limits.** A large Review Scope may hit auto-compaction and lose review state. Split the scope into smaller reviews, or use subagents so the main agent can integrate results without overflowing context.

---

## What it promises

**Complete Review** means all known required review work is accounted for in one Auditable Review Trace, and Final Recheck found no unfinished work. The final report is emitted only after that.

The final report claims only what the Auditable Review Trace evidences: confirmed findings, completed work, and remaining uncertainty. It is not a defect-free guarantee, a certification, or a complete security audit, and it contains no merge recommendation — the merge decision stays with you.

| | |
|---|---|
| 🔍 **Complete Review** | All required review work accounted for in one Auditable Review Trace, with a Final Recheck before the report |
| 📦 **Eight Rule Packs** | Design, testing, security, contracts, reliability, dependencies, docs, and research — loaded once per review |
| 🎚️ **Quality Levels L1–L5** | You pick the strictness in the request; L3 applies by default |
| 🧭 **Scope-first** | Your target is resolved into a complete file list, shown with its basis before review starts |
| 📋 **Severity-ordered reports** | Critical → Important → Minor, every finding with evidence and consequence |
| 🤝 **Scales with subagents** | Parallel workers for large independent file groups; the main agent owns the single trace |

---

## Installation

Clone into your harness skills directory:

```bash
git clone https://github.com/Zhen-Bo/pragmatic-code-review.git <skills-directory>/pragmatic-code-review
```

| Harness | Skills directory |
|---------|------------------|
| **Claude Code** | `~/.claude/skills/` |
| **Codex** | `~/.codex/skills/` |
| **OpenCode** | `~/.config/opencode/skills/` |
| **Other Agent Skills runner** | your harness's skills directory |

Or download a release package from [Releases](https://github.com/Zhen-Bo/pragmatic-code-review/releases) and extract it there.

Formerly `pragmatic-clean-code-reviewer` — old links and clone URLs redirect here.

---

## Usage

### Invoke

By name (slash invocation where supported) or natural language:

```
/pragmatic-code-review
```

Examples:

- *"Review `src/auth` at L4"*
- *"Code review of this PR — Quality Level L3"*
- *"Architecture review of the payments module"*
- *"Refactor review — focus on maintainability"*

### Review Scope

You name the target. The skill resolves it with repository tools into a complete file list before review, and shows the scope basis and file count at start.

| Situation | Behavior |
|-----------|----------|
| Scope given | Review that target only |
| Scope absent | Ask once for Review Scope and wait (only user interaction) |
| Target does not exist | Empty scope; completed review reporting that fact |

Every in-scope path is read directly and fully. Paths ignored by `.gitignore` are never read — they may hold secrets.

### Quality Level

Pick L1–L5 directly in the request. If you pick nothing, **L3** applies and is stated before review. Only your stated level applies for the whole review.

A level relaxes only what the trigger table and the rule packs explicitly state for it — for example, testing findings are reported only at L3 and above. Correctness, security, authorization, data integrity, contracts, and repository policy stay full obligations at every level.

Inspection triggers: a measured value strictly greater than the trigger at the applied level is a Confirmed Violation; equal to the trigger is not a breach:

| Inspection trigger | L1 | L2 | L3 | L4 | L5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Function effective logic lines | none | 80 | 50 | 30 | 20 |
| Required parameters | none | 7 | 5 | 4 | 3 |
| Maximum nesting depth | none | 5 | 4 | 3 | 2 |
| Confirmed occurrences of the same duplicated knowledge | none | 3 | 2 | 1 | 1 |
| Source-file lines | none | 800 | 500 | 300 | 200 |

`none` means no numeric trigger; concrete structural problems remain reportable at every level.

<details>
<summary><strong>Counting rules (summary)</strong></summary>

- **Logic lines** — one per statement or clause header; docstrings don't count
- **Required parameters** — caller-mandatory only
- **Nesting** — function body starts at depth 0; each control level adds 1
- **Duplicated knowledge** — reviewer-judged same knowledge; count strictly above the level trigger is a finding
- **File lines** — physical lines

Full rules live in [SKILL.md](SKILL.md).

</details>

---

## Eight Rule Packs

All eight load once at review start and stay available for the whole review. Every problem with evidence and a consequence is reportable, whether or not a pack names it.

1. **Design and Maintainability**
2. **Testing**
3. **Security and Privacy**
4. **Contracts and Compatibility**
5. **Reliability and Operations**
6. **Dependencies and Build**
7. **Documentation**
8. **Research Reproducibility**

Detailed guidance lives under `references/`. Rule IDs are optional pointers into that guidance.

Guidance draws on *The Pragmatic Programmer*, *Clean Code*, *Clean Architecture*, current primary sources, and established principles.

---

## Review flow

1. Fix Quality Level (default L3).
2. Enumerate Review Scope; show basis and file count.
3. Load all eight Rule Packs.
4. Read each in-scope file completely; record work in the Auditable Review Trace.
5. Run whole-scope checks (cross-file effects, contracts, and similar).
6. **Final Recheck** — reconcile scope against the trace; a gap continues the review.
7. Report findings only after Complete Review (or a labeled partial review if you stop early).

The Auditable Review Trace lives in the conversation only. The trace records only work actually performed — the goal is complete work, never a complete-looking trace.

For large scopes, workers scale to scope: the main agent alone for small file sets, one subagent for a medium batch, parallel subagents only for independent file groups. Each subagent loads this skill and uses the same Quality Level. The main agent owns the single trace.

---

## Findings

A **Confirmed Violation** needs concrete code evidence and a credible consequence; rule IDs are optional.

**Finding Severity** follows the most severe supported consequence:

| Severity | Examples of supported consequence |
|----------|-----------------------------------|
| **Critical** | Authorization bypass, sensitive-data disclosure, authoritative-data loss or corruption, unavailable core service, physical harm, substantial financial loss |
| **Important** | Incorrect external behavior, reduced reliability, required workaround, serious performance degradation, concrete maintainability or testing burden |
| **Minor** | Limited local inconvenience or a small maintainability or testing burden |

Report format — one heading per severity class, ordered Critical → Important → Minor, then by code location:

```markdown
### Critical

- `path/to/file:line` Problem summary
  - Evidence: relevant code and supporting reasoning
  - Consequence: supported consequence
```

Citations go inside Evidence only when the finding depends on an external source. Suspected problems that repository evidence cannot settle are reported with open uncertainty for you to rule out. Documentation-versus-code contradictions and misleading code comments are findings.

---

## File structure

```
pragmatic-code-review/
├── SKILL.md          # Review contract (for the agent)
├── README.md         # This file
├── CHANGELOG.md
├── LICENSE
├── scripts/
│   └── validate_skill.py
└── references/       # Rule Pack guidance and Rule Corpus
```

---

## Known limitations

This skill is prompt-only. It has no external verifier.

- **The Auditable Review Trace is self-reported.** Final Recheck reconciles scope against the trace inside the same conversation. That raises the cost of faking completion; it is not a proof of comprehension.
- **Finding quality is model quality.** The contract bounds what must be checked and what evidence a finding must carry. It cannot make a model notice a defect it does not understand.
- **Context boundaries end the trace.** There is no resumable review across compaction or new sessions. If auto-compaction triggers mid-review, review state is silently lost and the final report may be incomplete or misstate what was actually reviewed. Split large scopes or use subagents (see the notice at the top).

---

## License

MIT License — see [LICENSE](LICENSE).

## Credits

Principles drawn from:

- 📗 *The Pragmatic Programmer* by David Thomas and Andrew Hunt
- 📘 *Clean Code* by Robert C. Martin
- 📙 *Clean Architecture* by Robert C. Martin

---

<p align="center">
  <sub>Built on principles from software engineering classics. The merge decision stays with you.</sub>
</p>
