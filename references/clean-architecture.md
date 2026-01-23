# Clean Architecture Reference

Complete rule reference from *Clean Architecture* by Robert C. Martin.

## Table of Contents

- [Part 1: Introduction](#part-1-introduction)
- [Part 2: Programming Paradigms](#part-2-programming-paradigms)
- [Part 3: Design Principles (SOLID)](#part-3-design-principles-solid)
- [Part 4: Component Principles](#part-4-component-principles)
- [Part 5: Architecture](#part-5-architecture)
- [Part 6: Details](#part-6-details)
- [Appendix](#appendix)

---

## Part 1: Introduction

| Rule | Name | Review Point |
|------|------|--------------|
| CA-1 | Design and Architecture Are the Same Thing | Architecture and design decisions consistent? |
| CA-2 | The Goal: Minimize Human Resources | Architecture reduces maintenance cost? Easy to understand and modify? |
| CA-3 | Behavior vs Structure | Over-focusing on features while ignoring structure? Code easy to change? |
| CA-4 | The Greater Value | Is the system's structure (ability to change) being preserved? |

---

## Part 2: Programming Paradigms

| Rule | Name | Review Point |
|------|------|--------------|
| CA-5 | Structured Programming | Control flow clear? Avoiding complex jumps? |
| CA-6 | Object-Oriented Programming | Polymorphism correctly used? Dependency direction correct? |
| CA-7 | Functional Programming | Appropriate use of immutability? Minimizing side effects? |

---

## Part 3: Design Principles (SOLID)

| Rule | Name | Review Point |
|------|------|--------------|
| CA-8 | SRP: Single Responsibility Principle | Module responsible to only one actor? Multiple reasons to change? |
| CA-9 | OCP: Open-Closed Principle | Adding features requires modifying existing code? Can extend instead? |
| CA-10 | LSP: Liskov Substitution Principle | Subclass can fully substitute parent? Correct inheritance relationship? |
| CA-11 | ISP: Interface Segregation Principle | Interface too large? Client forced to implement unneeded methods? |
| CA-12 | DIP: Dependency Inversion Principle | Dependency direction correct? Depending on abstractions not concretes? |

### SOLID Quick Reference

| Principle | One-liner | Violation Sign |
|-----------|-----------|----------------|
| **SRP** | One reason to change | Class serves multiple stakeholders |
| **OCP** | Open for extension, closed for modification | Adding feature requires editing existing code |
| **LSP** | Subtypes substitutable for base types | Type checks or special cases for subtypes |
| **ISP** | No unused dependencies | Client imports methods it never calls |
| **DIP** | Depend on abstractions | Business logic imports infrastructure |

---

## Part 4: Component Principles

### Component Cohesion

| Rule | Name | Review Point |
|------|------|--------------|
| CA-13 | Components | Component division reasonable? Considering deployment units? |
| CA-14 | REP: Reuse/Release Equivalence Principle | Reusable components independently releasable? Version control reasonable? |
| CA-15 | CCP: Common Closure Principle | Frequently co-changing classes in same component? |
| CA-16 | CRP: Common Reuse Principle | Component has unrelated functionality? Users forced to bring unneeded dependencies? |
| CA-17 | The Tension Diagram for Component Cohesion | Component design considers project stage? Balancing cohesion principles? |

### Component Coupling

| Rule | Name | Review Point |
|------|------|--------------|
| CA-18 | ADP: Acyclic Dependencies Principle | Circular dependencies between components? |
| CA-19 | SDP: Stable Dependencies Principle | Depending on less stable components? |
| CA-20 | SAP: Stable Abstractions Principle | Stable components abstract enough? Concrete implementations in unstable components? |

### Component Principles Summary

| Principle | Focus | Question |
|-----------|-------|----------|
| **REP** | Reuse | Can this component be released independently? |
| **CCP** | Maintenance | Do things that change together live together? |
| **CRP** | Minimalism | Does using this component force unnecessary dependencies? |
| **ADP** | Dependencies | Are there circular dependencies? |
| **SDP** | Stability | Do we depend on things more stable than us? |
| **SAP** | Abstraction | Are stable components abstract? Are abstract components stable? |

---

## Part 5: Architecture

| Rule | Name | Review Point |
|------|------|--------------|
| CA-21 | What Is Architecture? | Architecture allows deferring decisions? Locking in tech choices too early? |
| CA-22 | Independence | System maintains independence in use cases, operations, development, deployment? |
| CA-23 | Decoupling Layers | Layers separated by reason for change? Layer coupling minimized? |
| CA-24 | Decoupling Use Cases | Use cases independent? One use case change affects others? |
| CA-25 | Duplication | True duplication or accidental similarity? Would merging increase improper coupling? |
| CA-26 | Boundaries: Drawing Lines | Boundaries correctly divided? Boundary locations reasonable? |
| CA-27 | Boundary Anatomy | Boundary implementation appropriate for project scale and needs? |
| CA-28 | Policy and Level | Policies organized by level? High-level policies independent of low-level details? |
| CA-29 | Business Rules | Business rules separated from technical details? Core logic independent? |
| CA-30 | Screaming Architecture | Project structure clearly expresses business use cases? Only seeing framework? |
| CA-31 | The Clean Architecture | Dependencies only point inward? Outer depends on inner? |
| CA-32 | Presenters and Humble Objects | Hard-to-test parts isolated? Using Humble Object pattern? |
| CA-33 | Partial Boundaries | Boundary cost reasonable? Can use more lightweight approach? |
| CA-34 | Layers and Boundaries | Boundaries in appropriate locations? Over-design or under-design? |
| CA-35 | The Main Component | Main component only handles initialization? Correctly transfers control to high level? |

### The Clean Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Frameworks & Drivers                      │
│  (Web, UI, DB, Devices, External Interfaces)                │
├─────────────────────────────────────────────────────────────┤
│                    Interface Adapters                        │
│  (Controllers, Gateways, Presenters)                        │
├─────────────────────────────────────────────────────────────┤
│                   Application Business Rules                 │
│  (Use Cases)                                                │
├─────────────────────────────────────────────────────────────┤
│                  Enterprise Business Rules                   │
│  (Entities)                                                 │
└─────────────────────────────────────────────────────────────┘

Dependencies point INWARD only.
Inner layers know nothing about outer layers.
```

### The Dependency Rule

> Source code dependencies must point only inward, toward higher-level policies.

**Violations:**
- Entity importing a Controller
- Use Case importing a Database class
- Business rule depending on UI framework

**Correct:**
- Controller imports Use Case interface
- Database implements Repository interface defined by Use Case
- UI calls Application Service

---

## Part 6: Details

| Rule | Name | Review Point |
|------|------|--------------|
| CA-36 | The Database Is a Detail | Business logic depends on specific database? Easy to swap databases? |
| CA-37 | The Web Is a Detail | Business logic depends on specific UI framework? Easy to swap UI? |
| CA-38 | Frameworks Are Details | Over-depending on framework? Business logic can exist without framework? |
| CA-39 | Case Study: Video Sales | Architecture follows clean architecture principles? Components correctly identified and organized? |
| CA-40 | The Missing Chapter | Package structure reflects architecture? |

### Details Checklist

| Question | Good Sign | Bad Sign |
|----------|-----------|----------|
| Can I change the database? | Repository interface with multiple implementations | SQL queries in business logic |
| Can I change the UI? | Presenter pattern, framework-agnostic views | Business logic in controllers |
| Can I change the framework? | Thin framework layer, business logic portable | Framework annotations everywhere |
| Can I test without infrastructure? | Pure unit tests with mocks | Tests require database/network |

---

## Appendix

| Rule | Name | Review Point |
|------|------|--------------|
| CA-41 | Architecture Archaeology | Understanding existing architecture before changing? |
| CA-42 | The Boy Scout Rule for Architecture | Change improves or maintains architecture quality? |
| CA-43 | Cost of Change | Changes getting harder? Architecture supports continuous evolution? |
| CA-44 | Keep Options Open | Locking in tech decisions too early? Maintaining enough flexibility? |
| CA-45 | Dependency Management | Dependency direction correct? Improper dependencies? |
| CA-46 | Humble Object Pattern | Using humble objects to isolate hard-to-test code? |
| CA-47 | Plugin Architecture | Details as plugins? Core independent of details? |
| CA-48 | The Test Boundary | Tests correctly depend on tested code? Test structure reflects system structure? |

---

## Quick Reference by Topic

| Topic | Rules |
|-------|-------|
| **SOLID** | CA-8, CA-9, CA-10, CA-11, CA-12 |
| **Components** | CA-13~20 |
| **Boundaries** | CA-26, CA-27, CA-33, CA-34 |
| **Clean Architecture** | CA-31, CA-32, CA-35 |
| **Independence** | CA-21, CA-22, CA-23, CA-24 |
| **Details as Plugins** | CA-36, CA-37, CA-38, CA-47 |
| **Testing** | CA-46, CA-48 |

---

## Architecture Decision Checklist

Before making architectural decisions, consider:

- [ ] **Does this make the system easier to change?** (CA-2, CA-3)
- [ ] **Are dependencies pointing in the right direction?** (CA-12, CA-31)
- [ ] **Can I defer this decision?** (CA-21, CA-44)
- [ ] **Is this true duplication or accidental similarity?** (CA-25)
- [ ] **Does the structure scream the business purpose?** (CA-30)
- [ ] **Can I test this without infrastructure?** (CA-46, CA-48)
- [ ] **Is the framework a detail, not a foundation?** (CA-38, CA-47)
