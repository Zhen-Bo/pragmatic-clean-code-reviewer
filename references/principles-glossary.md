# Principles Glossary

Quick reference for commonly used software engineering principles and their rule mappings.

## Table of Contents

- [Core Principles](#core-principles)
- [SOLID Principles](#solid-principles)
- [Design Principles](#design-principles)
- [Testing Principles](#testing-principles)
- [Architecture Principles](#architecture-principles)

---

## Core Principles

| Acronym | Full Name | One-liner | Related Rules |
|---------|-----------|-----------|---------------|
| **YAGNI** | You Aren't Gonna Need It | Don't build what you don't need yet | PP-43 |
| **KISS** | Keep It Simple, Stupid | Simplest solution that works | CC-130, PP-72 |
| **DRY** | Don't Repeat Yourself | Knowledge should have single source | PP-15, CC-37, CC-128, CC-155 |
| **WET** | Write Everything Twice | Acceptable duplication before abstraction | See [principles-spectrum.md](principles-spectrum.md) |
| **AHA** | Avoid Hasty Abstractions | Don't abstract too early | See [principles-spectrum.md](principles-spectrum.md) |

### YAGNI - You Aren't Gonna Need It

> "Don't implement something until you need it, and don't try to predict the future."

**Review Points:**
- Is this feature actually needed now?
- Are we building for hypothetical future requirements?
- Does this add unnecessary complexity?

**Anti-patterns:**
- Implementing unused factory patterns "for flexibility"
- Adding configuration options nobody asked for
- Building generic frameworks instead of solving the problem

**Related:** PP-43 (Avoid Fortune-Telling)

---

### KISS - Keep It Simple, Stupid

> "The simplest solution that works is usually the best one."

**Review Points:**
- Is this the simplest approach that solves the problem?
- Can someone understand this in 5 minutes?
- Are we over-engineering?

**Anti-patterns:**
- Using design patterns where a simple function suffices
- Abstracting code that's only used once
- Creating deep inheritance hierarchies

**Related:** CC-130 (Minimal Classes and Methods), PP-72 (Keep It Simple)

---

### DRY - Don't Repeat Yourself

> "Every piece of knowledge must have a single, unambiguous, authoritative representation."

**Review Points:**
- Is this the same *knowledge* or just similar *code*?
- If one changes, must the other change too?
- Is the abstraction clear and well-named?

**Important:** DRY is about *knowledge*, not *code text*. Two pieces of code that look the same but represent different business rules should NOT be merged.

**Related:** PP-15, CC-37, CC-128, CC-155

---

## SOLID Principles

| Letter | Principle | One-liner | Rule |
|--------|-----------|-----------|------|
| **S** | Single Responsibility | One reason to change | CA-8, CC-110 |
| **O** | Open/Closed | Open for extension, closed for modification | CA-9, CC-113 |
| **L** | Liskov Substitution | Subtypes must be substitutable | CA-10 |
| **I** | Interface Segregation | No client should depend on unused methods | CA-11 |
| **D** | Dependency Inversion | Depend on abstractions, not concretions | CA-12, CC-114 |

### SRP - Single Responsibility Principle

> "A class should have only one reason to change."

**Review Points:**
- Does this class/module have multiple responsibilities?
- Would different stakeholders request changes to different parts?
- Can you describe what it does without using "and"?

**Related:** CA-8, CC-110

---

### OCP - Open/Closed Principle

> "Software entities should be open for extension but closed for modification."

**Review Points:**
- Can new behavior be added without modifying existing code?
- Are we using inheritance/composition appropriately?
- Does adding a feature require touching many files?

**Related:** CA-9, CC-113

---

### LSP - Liskov Substitution Principle

> "Objects of a superclass should be replaceable with objects of a subclass without breaking the program."

**Review Points:**
- Can the subclass be used everywhere the parent is expected?
- Does the subclass violate any parent's contract?
- Are we using inheritance for code reuse vs true polymorphism?

**Related:** CA-10

---

### ISP - Interface Segregation Principle

> "No client should be forced to depend on methods it doesn't use."

**Review Points:**
- Is this interface too large?
- Do implementers need to provide empty/dummy methods?
- Should this be split into smaller interfaces?

**Related:** CA-11

---

### DIP - Dependency Inversion Principle

> "High-level modules should not depend on low-level modules. Both should depend on abstractions."

**Review Points:**
- Does business logic depend on infrastructure details?
- Are dependencies injected or hardcoded?
- Can we swap implementations easily?

**Related:** CA-12, CC-114

---

## Design Principles

| Acronym | Full Name | One-liner | Rules |
|---------|-----------|-----------|-------|
| **LoD** | Law of Demeter | Don't talk to strangers | PP-46, CC-80, CC-186 |
| **TDA** | Tell, Don't Ask | Tell objects what to do, don't query them | PP-45, CC-83 |
| **CQS** | Command Query Separation | Methods either change state OR return data, not both | CC-33 |
| **SoC** | Separation of Concerns | Different concerns in different places | CA-23, CC-110 |
| **POLA** | Principle of Least Astonishment | Behavior should match expectations | CC-152 |
| **CoC** | Convention over Configuration | Sensible defaults reduce boilerplate | — |

### LoD - Law of Demeter

> "Only talk to your immediate friends. Don't talk to strangers."

**Review Points:**
- Are there long method chains? (`a.getB().getC().doThing()`)
- Does this code know too much about other objects' internals?
- Should we add a delegating method?

**Related:** PP-46, CC-80, CC-81, CC-186

---

### TDA - Tell, Don't Ask

> "Tell objects what to do, don't ask for their data and operate on it."

**Review Points:**
- Are we getting data just to make a decision?
- Could the object make the decision itself?
- Is logic in the wrong place?

**Related:** PP-45, CC-83

---

### CQS - Command Query Separation

> "A method should either change state OR return information, never both."

**Review Points:**
- Does this method have side effects AND return a value?
- Is the return value informational or for control flow?
- Exception: Pop() from a stack is acceptable.

**Related:** CC-33

---

### POLA - Principle of Least Astonishment

> "Behavior should match what users/developers expect."

**Review Points:**
- Does the function do what its name suggests?
- Are there hidden side effects?
- Would a new developer be surprised?

**Related:** CC-152 (Obvious Behavior Unimplemented)

---

## Testing Principles

| Acronym | Full Name | One-liner | Rules |
|---------|-----------|-----------|-------|
| **F.I.R.S.T.** | Fast, Independent, Repeatable, Self-Validating, Timely | Test quality criteria | CC-106 |
| **AAA** | Arrange, Act, Assert | Test structure pattern | — |
| **TDD** | Test-Driven Development | Write test first, then code | CC-99, PP-31 |

### F.I.R.S.T.

| Letter | Meaning | Check |
|--------|---------|-------|
| **F** | Fast | Tests run in seconds, not minutes |
| **I** | Independent | Tests don't depend on each other |
| **R** | Repeatable | Same result every time, any environment |
| **S** | Self-Validating | Pass/fail without human interpretation |
| **T** | Timely | Written at the right time (ideally before code) |

**Related:** CC-106

---

## Component Principles

Component-level design principles from Clean Architecture. These apply when designing packages, modules, or microservices.

### Component Cohesion (What goes together?)

| Acronym | Full Name | One-liner | Rule |
|---------|-----------|-----------|------|
| **REP** | Reuse/Release Equivalence Principle | Reusable components must be releasable | CA-14 |
| **CCP** | Common Closure Principle | Classes that change together belong together (SRP for components) | CA-15 |
| **CRP** | Common Reuse Principle | Don't force users to depend on things they don't need (ISP for components) | CA-16 |

### REP - Reuse/Release Equivalence Principle

> "The granule of reuse is the granule of release."

**Review Points:**
- Can this component be versioned and released independently?
- Are all classes in the component releasable together?
- Would upgrading this component bring unrelated changes?

**Related:** CA-14

---

### CCP - Common Closure Principle

> "Gather into components those classes that change for the same reasons and at the same times."

**Review Points:**
- Do classes in this component change together?
- When a requirement changes, does it affect multiple components?
- Is this the component-level SRP?

**Related:** CA-15

---

### CRP - Common Reuse Principle

> "Don't force users of a component to depend on things they don't need."

**Review Points:**
- Does using this component bring unnecessary dependencies?
- Are there classes in this component that users never need?
- Should this component be split?

**Related:** CA-16

---

### Component Coupling (How do components relate?)

| Acronym | Full Name | One-liner | Rule |
|---------|-----------|-----------|------|
| **ADP** | Acyclic Dependencies Principle | No cycles in the component dependency graph | CA-18 |
| **SDP** | Stable Dependencies Principle | Depend in the direction of stability | CA-19 |
| **SAP** | Stable Abstractions Principle | Stable components should be abstract | CA-20 |

### ADP - Acyclic Dependencies Principle

> "Allow no cycles in the component dependency graph."

**Review Points:**
- Are there circular dependencies between components/packages?
- Can you build components in a clear order?
- Would changing component A require rebuilding component B and vice versa?

**Breaking Cycles:**
1. **Dependency Inversion** - Add an interface to break the cycle
2. **Extract New Component** - Move shared code to a new component

**Related:** CA-18

---

### SDP - Stable Dependencies Principle

> "Depend in the direction of stability."

**Review Points:**
- Does this component depend on less stable components?
- Are volatile components being depended upon by many others?
- Stable components should be depended upon, not depend on unstable ones

**Stability Metric:**
```
I = Fan-out / (Fan-in + Fan-out)
I = 0: Maximally stable (many dependents, no dependencies)
I = 1: Maximally unstable (no dependents, many dependencies)
```

**Related:** CA-19

---

### SAP - Stable Abstractions Principle

> "A component should be as abstract as it is stable."

**Review Points:**
- Are stable components mostly interfaces/abstract classes?
- Are concrete implementations in unstable components?
- Is there a balance between abstractness and stability?

**The Main Sequence:**
- Components should be near the line from (Abstract=1, Instability=0) to (Abstract=0, Instability=1)
- **Zone of Pain:** Concrete and stable (hard to change)
- **Zone of Uselessness:** Abstract and unstable (never used)

**Related:** CA-20

---

## Architecture Principles

| Principle | One-liner | Rules |
|-----------|-----------|-------|
| **Dependency Rule** | Dependencies point inward toward core | CA-31 |
| **Screaming Architecture** | Architecture should scream its purpose | CA-30 |
| **Plugin Architecture** | Details as plugins to core | CA-48 |
| **Humble Object** | Isolate hard-to-test code | CA-32, CA-47 |

### Dependency Rule

> "Source code dependencies must point only inward, toward higher-level policies."

**Layers (outer to inner):**
1. Frameworks & Drivers (DB, UI, Web)
2. Interface Adapters (Controllers, Gateways)
3. Application Business Rules (Use Cases)
4. Enterprise Business Rules (Entities)

**Related:** CA-31

---

## Quick Lookup Table

| When you see... | Consider... | Principle |
|-----------------|-------------|-----------|
| Feature nobody asked for | Remove it | YAGNI |
| Overly complex solution | Simplify | KISS |
| Copy-pasted code | Extract (if same knowledge) | DRY |
| Premature abstraction | Wait for Rule of Three | AHA/WET |
| Class doing too much | Split it | SRP |
| Long method chains | Add delegate methods | LoD |
| Getting data to decide | Move logic to data owner | TDA |
| Method with side effects + return | Split it | CQS |
| Surprising behavior | Rename or redesign | POLA |
| Business logic in controller | Move to use case | Dependency Rule |
| Circular package dependencies | Break with interface | ADP |
| Stable component is concrete | Add abstractions | SAP |
| Depending on volatile component | Invert dependency | SDP |
| Component has unrelated classes | Split component | CRP |
| Related classes in different packages | Move together | CCP |
| Can't release component independently | Restructure | REP |
