# Design and Maintainability

**Purpose:** Structure, naming, cohesion, coupling, duplication of knowledge, and change cost of the code under review.

Packs organize attention and never limit reportable problems. Report any concrete design or maintainability problem with code evidence and consequence, whether or not a named rule covers it.

Quality Level (L1–L5) decides whether a maintainability concern becomes a Confirmed Violation. It never changes Finding Severity. Threshold breaches start closer inspection; they are not findings by themselves.

## Contents

- [Structure and size](#structure-and-size)
- [Naming and intent](#naming-and-intent)
- [Duplication of knowledge](#duplication-of-knowledge)
- [Cohesion and coupling](#cohesion-and-coupling)
- [Abstraction and simplicity](#abstraction-and-simplicity)
- [Comments as design signals](#comments-as-design-signals)
- [Symptom index](#symptom-index)

## Structure and size

Inspect functions, classes, and modules for focus and change cost:

- One job per function; one reason to change per class or module (SRP).
- Mixed abstraction levels in one function; deep nesting; long parameter lists.
- God classes, feature envy, data clumps, primitive obsession.
- Class and module size are judged by cohesion and responsibility, not by a line score.

Optional rule references: CC-20–38, CC-107–114, CC-147–150, CC-180, CA-8.

## Naming and intent

Names must match behavior. Misleading, encoded, or interchangeable names are design defects when they raise the cost of safe change.

- Intention-revealing names; one word per concept; no gratuitous context.
- Method names that hide side effects; Manager/Handler/Processor when a precise domain name exists.
- Code that needs a comment to explain *what* it does — prefer clearer structure or names first.

Optional rule references: CC-4–19, CC-187–193, PP-74.

## Duplication of knowledge

DRY is about knowledge, not similar-looking text. Two blocks that look alike but encode different business rules should stay separate (accidental similarity). Two blocks that must always change together are the same knowledge and should share one source.

Before abstracting, all of these should hold:

1. Same business concept, not only similar shape.
2. If one instance changes, the others must change with it.
3. The abstraction has a clear name (not Utils, Helper, Common).
4. The abstraction reduces overall complexity.

Rule of Three is a design heuristic: the third clear occurrence often reveals the real pattern. Quality Level thresholds calibrate how hard you look for confirmed same-knowledge occurrences; they do not auto-create findings.

Optional rule references: PP-15, CC-37, CC-128, CC-155, CA-25.

## Cohesion and coupling

- Related change reasons live together; unrelated ones do not (CCP / CRP at package level).
- Dependency direction toward stable abstractions (DIP, Dependency Rule).
- Law of Demeter / train wrecks; Tell, Don't Ask; Command Query Separation.
- Circular package or component dependencies; business logic depending on frameworks or storage details.

Optional rule references: CA-8–12, CA-13–20, CA-31, PP-44–46, CC-80–83.

## Abstraction and simplicity

- YAGNI: do not build for hypothetical futures; do not force unused extension points.
- KISS: simplest complete solution for the current requirement.
- Wrong abstraction signs: Utils/Helper names, many boolean flags, constant conditionals inside a shared helper, changes that always edit the abstraction.
- Prefer composition and interfaces where inheritance is only for reuse.
- Magic numbers and strings without named constants when the value carries domain meaning.

Optional rule references: PP-43, PP-72, CC-130, CC-175, CA-9.

## Comments as design signals

Comments are in scope. Prefer code that needs no *what* comment. Keep *why*, external constraints, and safety warnings.

Report: obsolete comments, comments that contradict code, commented-out code, and comments that restate the next line.

Optional rule references: CC-39–63, CC-140–144.

## Symptom index

| Symptom | Look for |
| --- | --- |
| Function too long / deep nesting | Extract, early return, single abstraction level |
| Too many parameters | Parameter object; optional vs required args |
| Duplicate knowledge | Shared source only when change-coupled |
| God class / low cohesion | Split by actor or reason to change |
| Long call chains | Delegate; hide structure |
| Speculative generality | Remove unused abstraction |
| Dead code | Delete; history lives in VCS |
| Surprising behavior | Rename, split command/query, fix side effects |
