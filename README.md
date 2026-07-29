<h1 align="center">Pragmatic Clean Code Reviewer</h1>

<p align="center">
  <strong>An Agent Skill for pragmatic code and architecture review</strong><br>
  Works with any harness that supports the Agent Skills format: Claude Code, Codex, OpenCode, and compatible runners.
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/Zhen-Bo/pragmatic-clean-code-reviewer?style=flat-square" alt="License">
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#features">Features</a> •
  <a href="#known-limitations">Known Limitations</a> •
  <a href="docs/project-positioning.md">Project Positioning</a> •
  <a href="docs/review-profile.md">Review Profile</a> •
  <a href="docs/rule-sources.md">Rule Sources</a>
</p>

---

## Overview

This skill (v2.0.0, from frontmatter `metadata.version`) is a calibrated review
contract: it checks changed code for contract and safety risks, architecture,
maintainability, testing, and operational concerns. Severity follows project
positioning. Coverage accounting is mandatory.

It is grounded in three software engineering books (350+ rules loaded
**progressively** when a finding needs citation detail — not all scanned
individually every run):

| Book | Author | Rules |
|------|--------|-------|
| **The Pragmatic Programmer** | David Thomas & Andrew Hunt | 100 Tips |
| **Clean Code** | Robert C. Martin | 202 Rules |
| **Clean Architecture** | Robert C. Martin | 48 Principles |

Every review always scans the **19-point closed checklist** (groups A–E). Rule
corpus files are opened only when needed for paradigm adjustments, citations, or
edge cases.

> **Philosophy:** Let machines handle formatting; humans focus on logic and design.

> **Not a substitute** for fuzzing, formal verification, a dedicated security
> audit, or framework-specific static analysis. Output is a review, not a proof.

---

## Installation

### Quick Install

Clone into your harness skills directory:

```bash
git clone https://github.com/Zhen-Bo/pragmatic-clean-code-reviewer.git <skills-directory>/pragmatic-clean-code-reviewer
```

| Harness | Skills directory |
|---------|------------------|
| **Claude Code** | `~/.claude/skills/` |
| **Codex** | `~/.codex/skills/` |
| **OpenCode** | `~/.config/opencode/skills/` |
| **Other Agent Skills runner** | your harness's skills directory |

### From GitHub Release

1. Go to [Releases](https://github.com/Zhen-Bo/pragmatic-clean-code-reviewer/releases)
2. Download the latest `.skill` or `.zip` file
3. Extract to your skills directory (see table above)

---

## Usage

### Invoke the Skill

Invoke by name in harnesses with slash invocation, or use natural language.

```
/pragmatic-clean-code-reviewer
```

Examples:

- *"Review this PR for merge readiness"*
- *"Architecture review of this module"*
- *"Is this ready to merge at team standard?"*
- *"Refactor review — focus on maintainability"*

### Optional Review Profile

Persist calibration in the **target** project so reviews skip the questionnaire:

1. Canonical: `docs/code-review-profile.md`
2. Fallback: `.code-review-profile.md` (canonical wins if both exist)

Authoritative schema: [references/review-profile.md](references/review-profile.md).
Human-oriented overview: [docs/review-profile.md](docs/review-profile.md).

---

## Features

| Feature | Description |
|---------|-------------|
| **3+4+2 Positioning** | Questionnaire (or profile) → L1–L5 strictness |
| **Five Strictness Levels** | L1 (Lab) through L5 (Critical) |
| **19-Point Checklist** | Always-scanned closed taxonomy (A–E); 350+ rules loaded on demand |
| **Coverage Accounting** | Scope Manifest, Coverage Ledger, Whole-Scope Checks, Coverage Reconciliation (mandatory) |
| **Effort & Benefit** | Critical/Important only; nested reason bullets |
| **Deterministic Verdicts** | Level-aware gates; fourth verdict `⛔ Review incomplete` when coverage is partial |
| **Rule Citations** | Findings cite PP/CC/CA when detailed; Critical/Important evidence is one of: site quote (≤3 lines), distributed (≤3 locations, ≤6 lines total), or negative (search scope + absent artifact) |
| **Language-Aware** | Paradigm adjustments via progressive reference load |
| **Review Profile** | Per-project calibration, thresholds, scoped waivers |

**[Detailed features →](docs/features.md)**

---

## Quick Reference

### Strictness Levels

| Level | Name | Key Question |
|-------|------|--------------|
| **L1** | Lab | Does it run? |
| **L2** | Tool | Understandable next month? |
| **L3** | Team | Can teammates take over? |
| **L4** | Infra | Others suffer if broken? |
| **L5** | Critical | Can it pass audit? |

**[Full positioning guide →](docs/project-positioning.md)**

### Required Report Blocks

1. Header (level, positioning, source, profile path)
2. Scope Manifest
3. Coverage Ledger
4. Whole-Scope Checks
5. 🔴 Critical Issues *(omit if empty)*
6. 🟡 Important Issues *(omit if empty)*
7. 🔵 Minor Issues *(omit if empty)* — compact one-liners; **capped at 10**; **verdict-neutral**
8. Waiver Disclosure
9. Coverage Reconciliation
10. Verdict

Incomplete coverage never claims merge readiness:

```
⛔ Review incomplete — X/Y files reviewed · X/Y domain cells accounted
```

Full worked examples: [references/report-example.md](references/report-example.md)

### Rule Prefixes

| Prefix | Source |
|--------|--------|
| **PP-##** | The Pragmatic Programmer |
| **CC-##** | Clean Code |
| **CA-##** | Clean Architecture |

**[Full rule sources →](docs/rule-sources.md)**

---

## Documentation

| Document | Description |
|----------|-------------|
| [Features](docs/features.md) | Feature explanations |
| [Project Positioning](docs/project-positioning.md) | 3+4+2 system and L1–L5 mapping |
| [Review Profile](docs/review-profile.md) | Per-project calibration, waivers, lifecycle |
| [Metrics & Code Smells](docs/metrics.md) | Measurement rules and exemptions |
| [Rule Sources](docs/rule-sources.md) | Book summaries and key principles |

---

## File Structure

```
pragmatic-clean-code-reviewer/
├── SKILL.md                # Main skill contract (for AI) — v2.0.0
├── README.md               # This file
├── CHANGELOG.md            # Release history
├── docs/                   # Documentation (for humans)
│   ├── features.md
│   ├── project-positioning.md
│   ├── review-profile.md
│   ├── metrics.md
│   └── rule-sources.md
└── references/             # Rule references and examples (for AI)
    ├── report-example.md
    ├── review-profile.md
    ├── clean-code.md
    ├── clean-architecture.md
    ├── pragmatic-programmer.md
    └── ...
```

---

## Contributing

Contributions are welcome:

- Report issues
- Suggest improvements
- Submit pull requests

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Known Limitations

This skill is prompt-only. It has no runtime, so the following limits are structural, not oversights.

**Coverage accounting is self-reported.** The Scope Manifest, Coverage Ledger, and reconciliation arithmetic make an incomplete review visible, but a model can still fabricate them. Real line counts, verbatim evidence quotes, per-file emission, and bidirectional reconciliation raise the cost of faking a review above the cost of performing one. That is a deterrent, not a proof.

**The review profile is self-certification.** `docs/code-review-profile.md` is written by the team being reviewed. Non-waivable Critical findings, mandatory disclosure, and the waiver tripwires make abuse visible and attributable. They cannot make it impossible.

**Finding quality is model quality.** The contract bounds what must be checked and what evidence a finding must carry. It cannot make a model notice a defect it does not understand.

Closing any of these requires an enforcement layer outside the skill: a tool that reads the real file list and rejects a report whose ledger does not reconcile, or an organizational approval path for waivers. Partial mitigations inside the prompt would add contract surface without closing the gap, so they are deliberately not attempted. These will be revisited only when a complete answer exists, not patched incrementally.

---

## Credits

Based on principles from:

- *"The Pragmatic Programmer"* by David Thomas and Andrew Hunt
- *"Clean Code"* by Robert C. Martin
- *"Clean Architecture"* by Robert C. Martin
