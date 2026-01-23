<p align="center">
  <img src="https://img.shields.io/badge/Clean%20Code-Enforced-brightgreen?style=for-the-badge&logo=checkmarx" alt="Clean Code">
  <img src="https://img.shields.io/badge/Clean%20Architecture-Verified-blue?style=for-the-badge&logo=blueprint" alt="Clean Architecture">
  <img src="https://img.shields.io/badge/Pragmatic%20Programmer-Applied-orange?style=for-the-badge&logo=bookstack" alt="Pragmatic Programmer">
</p>

<h1 align="center">Pragmatic Clean Code Reviewer</h1>

<p align="center">
  <strong>A Claude Code skill for conducting rigorous code reviews based on software engineering classics</strong>
</p>

<p align="center">
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#features">Features</a> •
  <a href="docs/project-positioning.md">Project Positioning</a> •
  <a href="docs/rule-sources.md">Rule Sources</a>
</p>

---

## Overview

This skill transforms Claude Code into a **strict code review expert** that evaluates your code against 350+ rules from three foundational software engineering books:

| Book | Author | Rules |
|------|--------|-------|
| 📗 **The Pragmatic Programmer** | David Thomas & Andrew Hunt | 100 Tips |
| 📘 **Clean Code** | Robert C. Martin | 202 Rules |
| 📙 **Clean Architecture** | Robert C. Martin | 48 Principles |

> **Philosophy:** Let machines handle formatting; humans focus on logic and design.

---

## Installation

### Quick Install

| Tool | Command |
|------|---------|
| **Claude Code** | `git clone https://github.com/Zhen-Bo/pragmatic-clean-code-reviewer.git ~/.claude/skills/pragmatic-clean-code-reviewer` |
| **OpenCode** | `git clone https://github.com/Zhen-Bo/pragmatic-clean-code-reviewer.git ~/.config/opencode/skills/pragmatic-clean-code-reviewer` |
| **Codex** | `git clone https://github.com/Zhen-Bo/pragmatic-clean-code-reviewer.git ~/.codex/skills/pragmatic-clean-code-reviewer` |

### From GitHub Release

1. Go to [Releases](https://github.com/Zhen-Bo/pragmatic-clean-code-reviewer/releases)
2. Download the latest `.skill` or `.zip` file
3. Extract to your skills directory (see table above)

---

## Usage

### Invoke the Skill

```
/pragmatic-clean-code-reviewer
```

### Or Use Natural Language

- *"Review my code for code smells"*
- *"Check if this PR is ready to merge"*
- *"Audit the architecture of this module"*

---

## Features

| Feature | Description |
|---------|-------------|
| 🎯 **3+4+2 Positioning System** | Questionnaire determines L1-L5 strictness |
| 🏷️ **Five Strictness Levels** | From L1 (Lab) to L5 (Critical) |
| ✅ **15-Point Checklist** | Systematic code evaluation |
| 📋 **Standardized Reports** | Clear, consistent output format |
| 🔖 **Rule Citations** | Every issue references PP/CC/CA rules |
| 🌐 **Language-Aware** | Adjusts rules for different paradigms |

👉 **[See detailed features →](docs/features.md)**

---

## Quick Reference

### Strictness Levels

| Level | Name | Key Question |
|-------|------|--------------|
| **L1** | 🧪 Lab | Does it run? |
| **L2** | 🛠️ Tool | Understandable next month? |
| **L3** | 🤝 Team | Can teammates take over? |
| **L4** | 🚀 Infra | Others suffer if broken? |
| **L5** | 🏛️ Critical | Can it pass audit? |

👉 **[Full positioning guide →](docs/project-positioning.md)**

### Rule Prefixes

| Prefix | Source |
|--------|--------|
| **PP-##** | The Pragmatic Programmer |
| **CC-##** | Clean Code |
| **CA-##** | Clean Architecture |

👉 **[Full rule sources →](docs/rule-sources.md)**

---

## Documentation

| Document | Description |
|----------|-------------|
| [Features](docs/features.md) | Detailed feature explanations |
| [Project Positioning](docs/project-positioning.md) | 3+4+2 system & L1-L5 mapping |
| [Metrics & Code Smells](docs/metrics.md) | Thresholds and exemptions |
| [Rule Sources](docs/rule-sources.md) | Book summaries and key principles |

---

## File Structure

```
pragmatic-clean-code-reviewer/
├── SKILL.md                # Main skill (for AI)
├── README.md               # This file
├── CHANGELOG.md            # Release history
├── docs/                   # Detailed documentation (for humans)
│   ├── features.md
│   ├── project-positioning.md
│   ├── metrics.md
│   └── rule-sources.md
└── references/             # Rule references (for AI)
    ├── clean-code.md
    ├── clean-architecture.md
    ├── pragmatic-programmer.md
    └── ...
```

---

## Contributing

Contributions are welcome! Please feel free to:

- 🐛 Report issues
- 💡 Suggest improvements
- 🔧 Submit pull requests

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Credits

Based on principles from:
- 📗 *"The Pragmatic Programmer"* by David Thomas and Andrew Hunt
- 📘 *"Clean Code"* by Robert C. Martin
- 📙 *"Clean Architecture"* by Robert C. Martin

---

<p align="center">
  <sub>Built with principles from software engineering classics</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Made%20for-Claude%20Code-blueviolet?style=flat-square" alt="Made for Claude Code">
  <img src="https://img.shields.io/github/license/Zhen-Bo/pragmatic-clean-code-reviewer?style=flat-square" alt="License">
</p>
