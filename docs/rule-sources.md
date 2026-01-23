# Rule Sources

This skill is based on 350+ rules from three foundational software engineering books.

## 📗 The Pragmatic Programmer (PP-1 to PP-100)

**Authors:** David Thomas & Andrew Hunt

> *"Care about your craft. Think about your work."*

### Key Principles

| Principle | Rule | Description |
|-----------|------|-------------|
| **DRY** | PP-15 | Don't Repeat Yourself |
| **YAGNI** | PP-43 | You Aren't Gonna Need It |
| **ETC** | PP-14 | Easy To Change |
| Design by Contract | PP-37 | Clear preconditions and postconditions |
| Tracer Bullets | PP-20 | End-to-end working path first |
| Broken Windows | PP-5 | Don't tolerate bad code |

---

## 📘 Clean Code (CC-1 to CC-202)

**Author:** Robert C. Martin

> *"Clean code reads like well-written prose."*

### Key Principles

| Principle | Rule | Description |
|-----------|------|-------------|
| **KISS** | CC-130 | Keep It Simple, Stupid |
| Small Functions | CC-20, CC-21 | Functions should be small and do one thing |
| Meaningful Names | CC-4 | Use intention-revealing names |
| No Side Effects | CC-31 | Functions shouldn't have hidden effects |
| Error Handling | CC-86 | Use exceptions, not return codes |

---

## 📙 Clean Architecture (CA-1 to CA-48)

**Author:** Robert C. Martin

> *"The goal of software architecture is to minimize human resources."*

### SOLID Principles

| Principle | Rule | Description |
|-----------|------|-------------|
| **S**ingle Responsibility | CA-8 | One reason to change |
| **O**pen-Closed | CA-9 | Open for extension, closed for modification |
| **L**iskov Substitution | CA-10 | Subtypes must be substitutable |
| **I**nterface Segregation | CA-11 | No unused dependencies |
| **D**ependency Inversion | CA-12 | Depend on abstractions |

### Architecture Principles

| Principle | Rule | Description |
|-----------|------|-------------|
| Dependency Rule | CA-31 | Dependencies point inward only |
| Screaming Architecture | CA-30 | Structure reveals intent |
| Plugin Architecture | CA-47 | Details as plugins |

### Component Principles

| Category | Principles |
|----------|------------|
| **Cohesion** | REP (CA-14), CCP (CA-15), CRP (CA-16) |
| **Coupling** | ADP (CA-18), SDP (CA-19), SAP (CA-20) |

---

## Rule Prefix Reference

| Prefix | Source | Total Rules |
|--------|--------|-------------|
| **PP-##** | The Pragmatic Programmer | 100 |
| **CC-##** | Clean Code | 202 |
| **CA-##** | Clean Architecture | 48 |
