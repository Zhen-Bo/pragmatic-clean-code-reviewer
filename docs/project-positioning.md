# Project Positioning Guide

Detailed guide for the 3+4+2 questionnaire system.

## Quick Lookup Table

| Who (Q1) | Standard (Q2) | Critical (Q3) | Level | Example |
|----------|---------------|---------------|-------|---------|
| Solo | Ship | - | L1 | Experiment script |
| Solo | Normal | - | L1 | Personal utility |
| Solo | Careful | - | L2 | Long-term personal project |
| Solo | Strict | - | L3 | Perfectionist project |
| Internal | Ship | - | L1 | Team prototype |
| Internal | Normal | - | L2 | Team daily development |
| Internal | Careful | Normal | L2 | Internal helper tool |
| Internal | Careful | Critical | L3 | **Internal SDK** |
| Internal | Strict | Normal | L3 | Internal tool (high std) |
| Internal | Strict | Critical | L4 | **Internal core infra** |
| External | Ship | - | L2 | Product MVP |
| External | Normal | - | L3 | General product feature |
| External | Careful | Normal | L3 | Small OSS tool |
| External | Careful | Critical | L4 | **Product core feature** |
| External | Strict | Normal | L4 | OSS tool (high std) |
| External | Strict | Critical | L5 | **Finance/Medical/Core OSS** |

## Strictness Matrix

| Check | L1 | L2 | L3 | L4 | L5 |
|-------|----|----|----|----|-----|
| Functional Correctness | ★★★ | ★★★★ | ★★★★★ | ★★★★★ | ★★★★★ |
| Error Handling | ★ | ★★ | ★★★ | ★★★★ | ★★★★★ |
| Naming & Readability | ★ | ★★★ | ★★★★ | ★★★★★ | ★★★★★ |
| Architecture | ☆ | ★ | ★★★ | ★★★★★ | ★★★★★ |
| Testing | ☆ | ★ | ★★★ | ★★★★ | ★★★★★ |

## Level Descriptions

### L1 🧪 Lab
- **Key Question:** Does it run?
- **Use Case:** Experiments, throwaway scripts
- **Focus:** Just make it work

### L2 🛠️ Tool
- **Key Question:** Will I understand this next month?
- **Use Case:** Personal tools, internal utilities
- **Focus:** Basic readability and error handling

### L3 🤝 Team
- **Key Question:** Can a teammate take this over?
- **Use Case:** Team projects, shared codebases
- **Focus:** Clean code, documentation, tests

### L4 🚀 Infra
- **Key Question:** Will others suffer if this breaks?
- **Use Case:** Internal SDKs, shared infrastructure
- **Focus:** Robustness, API design, comprehensive tests

### L5 🏛️ Critical
- **Key Question:** Can this pass a security/compliance audit?
- **Use Case:** Financial systems, medical software, core OSS
- **Focus:** Maximum rigor, security, compliance
