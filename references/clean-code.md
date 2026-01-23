# Clean Code Reference

Complete rule reference from *Clean Code* by Robert C. Martin.

> **Note:** CC-64 to CC-77 (Formatting chapter) are intentionally omitted. Formatting should be handled by automated tools (linters/formatters), not human reviewers.

## Table of Contents

- [Chapter 1: Clean Code](#chapter-1-clean-code)
- [Chapter 2: Meaningful Names](#chapter-2-meaningful-names)
- [Chapter 3: Functions](#chapter-3-functions)
- [Chapter 4: Comments](#chapter-4-comments)
- [Chapter 6: Objects and Data Structures](#chapter-6-objects-and-data-structures)
- [Chapter 7: Error Handling](#chapter-7-error-handling)
- [Chapter 8: Boundaries](#chapter-8-boundaries)
- [Chapter 9: Unit Tests](#chapter-9-unit-tests)
- [Chapter 10: Classes](#chapter-10-classes)
- [Chapter 11: Systems](#chapter-11-systems)
- [Chapter 12: Emergence](#chapter-12-emergence)
- [Chapter 13: Concurrency](#chapter-13-concurrency)
- [Appendix: Smells and Heuristics](#appendix-smells-and-heuristics)

---

## Chapter 1: Clean Code

| Rule | Name | Review Point |
|------|------|--------------|
| CC-1 | Clean Code Is Focused | Each unit does one thing? |
| CC-2 | Readable by Others | Easy to understand? Others can take over? |
| CC-3 | Written by Someone Who Cares | Shows attention to detail and professionalism? |

---

## Chapter 2: Meaningful Names

| Rule | Name | Review Point |
|------|------|--------------|
| CC-4 | Use Intention-Revealing Names | Names clearly express intent? |
| CC-5 | Avoid Disinformation | Naming might mislead? Matches actual behavior? |
| CC-6 | Make Meaningful Distinctions | Similar names meaningfully different? Using a1, a2? |
| CC-7 | Use Pronounceable Names | Names usable in conversation? |
| CC-8 | Use Searchable Names | Important vars/consts searchable? |
| CC-9 | Avoid Encodings | Using outdated conventions like Hungarian? |
| CC-10 | Avoid Mental Mapping | Reader needs to remember what var represents? |
| CC-11 | Class Names Should Be Nouns | Class names are noun phrases? |
| CC-12 | Method Names Should Be Verbs | Method names are verb phrases? |
| CC-13 | Don't Be Cute | Names clear and direct? Avoiding insider terms? |
| CC-14 | Pick One Word per Concept | Same concept uses same word consistently? |
| CC-15 | Don't Pun | Same word has multiple meanings? |
| CC-16 | Use Solution Domain Names | Technical concepts use correct terms? |
| CC-17 | Use Problem Domain Names | Business concepts use business terms? |
| CC-18 | Add Meaningful Context | Names have enough context? Need prefix/suffix? |
| CC-19 | Don't Add Gratuitous Context | Unnecessary prefix or redundant context? |

---

## Chapter 3: Functions

| Rule | Name | Review Point |
|------|------|--------------|
| CC-20 | Small! | Function small enough? Can decompose further? |
| CC-21 | Do One Thing | Function does only one thing? Can extract others? |
| CC-22 | One Level of Abstraction per Function | Mixing high and low level operations? |
| CC-23 | Reading Code from Top to Bottom: The Stepdown Rule | Code arranged high to low abstraction? |
| CC-24 | Switch Statements | Switch replaceable with polymorphism? Properly encapsulated? |
| CC-25 | Use Descriptive Names | Function name clearly describes behavior? |
| CC-26 | Function Arguments | Param count reasonable? Can reduce? |
| CC-27 | Dyadic Functions | Two-argument functions justified? Order intuitive? |
| CC-28 | Flag Arguments | Boolean params switching behavior? Split into multiple functions? |
| CC-29 | Argument Objects | Multiple params should be combined into object? |
| CC-30 | Argument Lists | Variable arguments used appropriately? |
| CC-31 | Have No Side Effects | Hidden side effects? Doing things not implied by name? |
| CC-32 | Output Arguments | Using params as output? Can return result instead? |
| CC-33 | Command Query Separation | Function both acts and returns state? |
| CC-34 | Prefer Exceptions to Returning Error Codes | Proper exception use? Error codes causing complex nesting? |
| CC-35 | Extract Try/Catch Blocks | Error handling separated from normal logic? |
| CC-36 | Error Handling Is One Thing | Error handling function focused on errors only? |
| CC-37 | Don't Repeat Yourself | Duplicate code extractable? |
| CC-38 | Structured Programming | Single entry/exit per function? (relaxed for small functions) |

---

## Chapter 4: Comments

| Rule | Name | Review Point |
|------|------|--------------|
| CC-39 | Comments Do Not Make Up for Bad Code | Comment eliminable by improving code? |
| CC-40 | Explain Yourself in Code | Replace comment with better naming/structure? |
| CC-41 | Legal Comments | Copyright/license headers present if required? |
| CC-42 | Informative Comments | Comment provides useful info not in code? |
| CC-43 | Explanation of Intent | Complex rules or non-intuitive decisions explained? |
| CC-44 | Clarification | Obscure code clarified with comment? |
| CC-45 | Warning of Consequences | Dangerous ops or important limits warned? |
| CC-46 | TODO Comments | TODOs tracked? Expired TODOs? |
| CC-47 | Amplification | Important point emphasized appropriately? |
| CC-48 | Bad Comments: Mumbling | Comment clear and meaningful? Vague comments? |
| CC-49 | Bad Comments: Redundant | Comment harder to read than code? Restating code? |
| CC-50 | Bad Comments: Misleading | Comment matches code behavior? |
| CC-51 | Bad Comments: Mandated | Meaningless forced comments? |
| CC-52 | Bad Comments: Journal | Change log that should be in VCS? |
| CC-53 | Bad Comments: Noise | Meaningless filler comments? |
| CC-54 | Bad Comments: Use Function/Variable Instead | Comment replaceable by well-named function/variable? |
| CC-55 | Bad Comments: Position Markers | Unnecessary dividers or region markers? |
| CC-56 | Bad Comments: Closing Brace Comments | Closing brace comments? Function too long? |
| CC-57 | Bad Comments: Attributions | Attribution that should be in VCS? |
| CC-58 | Bad Comments: Commented-Out Code | Commented-out code present? |
| CC-59 | Bad Comments: HTML Comments | HTML in comments? |
| CC-60 | Bad Comments: Nonlocal Information | Comment describes distant code? |
| CC-61 | Bad Comments: Too Much Information | Comment has too much unrelated info? |
| CC-62 | Bad Comments: Inobvious Connection | Reader can understand what comment means? |
| CC-63 | Bad Comments: Function Headers | Header comment replaceable by better function name? |

---

## Chapter 5: Formatting

> **CC-64 to CC-77 intentionally omitted.** 
> 
> Formatting should be handled by Linter/Formatter tools (Prettier, ESLint, Black, gofmt, etc.), not human reviewers. Focus on logic and design instead.

---

## Chapter 6: Objects and Data Structures

| Rule | Name | Review Point |
|------|------|--------------|
| CC-78 | Data Abstraction | Class hides implementation? Exposes abstract interface? |
| CC-79 | Data/Object Anti-Symmetry | Correct choice of object vs data structure? |
| CC-80 | The Law of Demeter | Following Law of Demeter? Too many chained calls? |
| CC-81 | Train Wrecks | Long method call chains? Should split? |
| CC-82 | Hybrids | Class exposing both data and behavior? Unclear design? |
| CC-83 | Hiding Structure | Object exposing too much internals? Following Tell Don't Ask? |
| CC-84 | Data Transfer Objects | DTO staying pure? No business logic? |
| CC-85 | Active Record | Active Record not mixed with business logic? |

---

## Chapter 7: Error Handling

| Rule | Name | Review Point |
|------|------|--------------|
| CC-86 | Use Exceptions Rather Than Return Codes | Proper exception use? Error handling separated from main logic? |
| CC-87 | Write Your Try-Catch-Finally Statement First | Error handling structure established early? |
| CC-88 | Use Unchecked Exceptions | (Java-specific) Checked exceptions creating dependency chains? |
| CC-89 | Provide Context with Exceptions | Exception has enough context to understand problem? |
| CC-90 | Define Exception Classes in Terms of a Caller's Needs | Exception hierarchy meaningful? Caller can effectively catch? |
| CC-91 | Define the Normal Flow | Special cases handled elegantly? Using Null Object or Special Case pattern? |
| CC-92 | Don't Return Null | Avoiding null returns? Using Optional or empty collection? |
| CC-93 | Don't Pass Null | Avoiding null as parameter? |

---

## Chapter 8: Boundaries

| Rule | Name | Review Point |
|------|------|--------------|
| CC-94 | Using Third-Party Code | Third-party code properly encapsulated? Dependencies isolated? |
| CC-95 | Exploring and Learning Boundaries | Learning tests for third-party APIs? |
| CC-96 | Learning Tests Are Better Than Free | API behavior documented through tests? |
| CC-97 | Using Code That Does Not Yet Exist | Using interfaces to isolate unfinished/external modules? |
| CC-98 | Clean Boundaries | System boundaries clearly defined? Boundary change cost controllable? |

---

## Chapter 9: Unit Tests

| Rule | Name | Review Point |
|------|------|--------------|
| CC-99 | The Three Laws of TDD | Test written before production code? |
| CC-100 | Keeping Tests Clean | Test code clean, readable, maintainable? |
| CC-101 | Tests Enable the -ilities | Test coverage supports refactoring and change? |
| CC-102 | Clean Tests | Tests clearly express intent? Easy to understand? |
| CC-103 | Domain-Specific Testing Language | Tests use readable, domain-specific helpers? |
| CC-104 | One Assert per Test | Each test focused on one concept? Too many asserts? |
| CC-105 | Single Concept per Test | Test focused on single concept? |
| CC-106 | F.I.R.S.T. | Tests Fast, Independent, Repeatable, Self-Validating, Timely? |

---

## Chapter 10: Classes

| Rule | Name | Review Point |
|------|------|--------------|
| CC-107 | Class Organization | Class structure follows standard organization? |
| CC-108 | Encapsulation | Class properly encapsulated? Minimal public interface? |
| CC-109 | Classes Should Be Small! | Class small enough? Focused on single responsibility? |
| CC-110 | The Single Responsibility Principle | Class has only one responsibility? Multiple reasons to change? |
| CC-111 | Cohesion | Class cohesion high? Methods use most class variables? |
| CC-112 | Maintaining Cohesion Results in Many Small Classes | Low cohesion class should be split? |
| CC-113 | Organizing for Change | Class easy to extend without modifying existing code? |
| CC-114 | Isolating from Change | Dependencies point to abstractions not concretes? |

---

## Chapter 11: Systems

| Rule | Name | Review Point |
|------|------|--------------|
| CC-115 | Separate Constructing a System from Using It | Construction logic separated from business logic? |
| CC-116 | Separation of Main | Main module only handles wiring? |
| CC-117 | Factories | Factory pattern used appropriately for construction? |
| CC-118 | Dependency Injection | Using DI? Dependencies provided externally? |
| CC-119 | Scaling Up | Architecture allows gradual scaling? Over-designed? |
| CC-120 | Cross-Cutting Concerns | Cross-cutting concerns (logging, security, transactions) properly handled? |
| CC-121 | Test Drive the System Architecture | Architecture starts simple? Over-design signs? |
| CC-122 | Optimize Decision Making | Decisions deferred until last responsible moment? |
| CC-123 | Use Standards Wisely | Standards used when they add value? |
| CC-124 | Systems Need Domain-Specific Languages | DSLs considered for complex domains? |

---

## Chapter 12: Emergence

| Rule | Name | Review Point |
|------|------|--------------|
| CC-125 | Getting Clean via Emergent Design | Following the four rules of simple design? |
| CC-126 | Simple Design Rule 1: Runs All the Tests | All tests pass? System verifiable? |
| CC-127 | Simple Design Rule 2: Contains No Duplication | Code, logic, knowledge duplication? |
| CC-128 | Simple Design Rule 3: Expresses Intent | Code clearly expresses intent? Reader can understand? |
| CC-129 | Simple Design Rule 4: Minimal Classes and Methods | Unnecessary classes or methods? Over-designed? |
| CC-130 | Minimal Classes and Methods | Pragmatic minimalism applied? |

---

## Chapter 13: Concurrency

| Rule | Name | Review Point |
|------|------|--------------|
| CC-131 | Why Concurrency? | Concurrency really needed? Just adding complexity? |
| CC-132 | Myths and Misconceptions | Correct understanding of concurrency challenges? |
| CC-133 | Concurrency Defense Principles | Following SRP, limiting scope, using copies, thread independence? |
| CC-134 | Know Your Library | Correctly using language's concurrency tools? Using thread-safe collections? |
| CC-135 | Know Your Execution Models | Appropriate concurrency model? Understanding its characteristics? |
| CC-136 | Beware Dependencies Between Synchronized Methods | Dependencies between sync methods? Deadlock possible? |
| CC-137 | Keep Synchronized Sections Small | Synchronized sections minimized? Unnecessary long sync blocks? |
| CC-138 | Writing Correct Shut-Down Code Is Hard | Shutdown logic correct? All threads and resources handled? |
| CC-139 | Testing Threaded Code | Multithreaded code has proper tests? Stress tested? |

---

## Appendix: Smells and Heuristics

### Comments (C)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-140 | C1: Inappropriate Information | Comment has info that shouldn't be in code? |
| CC-141 | C2: Obsolete Comment | Outdated comment inconsistent with code? |
| CC-142 | C3: Redundant Comment | Comment just repeats what code expresses? |
| CC-143 | C4: Poorly Written Comment | Comment clear, concise, correct? |
| CC-144 | C5: Commented-Out Code | Commented-out code present? |

### Environment (E)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-145 | E1: Build Requires More Than One Step | Build automated and simple? |
| CC-146 | E2: Tests Require More Than One Step | Tests can run in one step? |

### Functions (F)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-147 | F1: Too Many Arguments | Function has more than 3 params? Can reduce? |
| CC-148 | F2: Output Arguments | Using params as output? |
| CC-149 | F3: Flag Arguments | Boolean params controlling function behavior? |
| CC-150 | F4: Dead Function | Unused functions? |

### General (G)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-151 | G1: Multiple Languages in One Source File | Source file mixes languages? Separable? |
| CC-152 | G2: Obvious Behavior Is Unimplemented | Behavior matches expectations? Surprises or omissions? |
| CC-153 | G3: Incorrect Behavior at the Boundaries | Boundary conditions correctly handled? Test covered? |
| CC-154 | G4: Overridden Safeties | Disabled warnings or tests? |
| CC-155 | G5: Duplication | Duplicate code, logic, knowledge? |
| CC-156 | G6: Code at Wrong Level of Abstraction | Code at correct abstraction level? |
| CC-157 | G7: Base Classes Depending on Their Derivatives | Base class independent of derived? |
| CC-158 | G8: Too Much Information | Public interface minimized? Exposing too much? |
| CC-159 | G9: Dead Code | Code that never executes? |
| CC-160 | G10: Vertical Separation | Definition and use close together? |
| CC-161 | G11: Inconsistency | Code style and patterns consistent? |
| CC-162 | G12: Clutter | Unused variables, functions, comments, imports? |
| CC-163 | G13: Artificial Coupling | Unrelated things coupled together? |
| CC-164 | G14: Feature Envy | Method overuses other class's data? |
| CC-165 | G15: Selector Arguments | Params used to select internal behavior? |
| CC-166 | G16: Obscured Intent | Code intent clear? Needs explanation to understand? |
| CC-167 | G17: Misplaced Responsibility | Functionality in correct location? |
| CC-168 | G18: Inappropriate Static | Static method appropriate? Should be instance method? |
| CC-169 | G19: Use Explanatory Variables | Complex expressions broken into meaningful variables? |
| CC-170 | G20: Function Names Should Say What They Do | Function name accurately describes behavior? |
| CC-171 | G21: Understand the Algorithm | Algorithm clear and correct? Author truly understands? |
| CC-172 | G22: Make Logical Dependencies Physical | Dependencies explicitly expressed? |
| CC-173 | G23: Prefer Polymorphism to If/Else or Switch/Case | Replace conditional logic with polymorphism? |
| CC-174 | G24: Follow Standard Conventions | Code follows team coding standards? |
| CC-175 | G25: Replace Magic Numbers with Named Constants | Unnamed magic numbers? |
| CC-176 | G26: Be Precise | Code precisely handles various situations? Vague assumptions? |
| CC-177 | G27: Structure Over Convention | Design decisions enforced by structure? |
| CC-178 | G28: Encapsulate Conditionals | Complex conditionals extracted into meaningfully named functions? |
| CC-179 | G29: Avoid Negative Conditionals | Negative conditionals rewritable as positive? |
| CC-180 | G30: Functions Should Do One Thing | Functions doing more than one thing? Should decompose? |
| CC-181 | G31: Hidden Temporal Couplings | Temporal dependencies explicit? |
| CC-182 | G32: Don't Be Arbitrary | Code structure has reason? Avoiding arbitrary decisions? |
| CC-183 | G33: Encapsulate Boundary Conditions | Boundary conditions centrally handled? |
| CC-184 | G34: Functions Should Descend Only One Level of Abstraction | Function operates at single abstraction level? |
| CC-185 | G35: Keep Configurable Data at High Levels | Config data at high level and accessible? |
| CC-186 | G36: Avoid Transitive Navigation | Following Law of Demeter? Avoiding deep navigation? |

### Names (N)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-187 | N1: Choose Descriptive Names | Names descriptive and accurate? |
| CC-188 | N2: Choose Names at the Appropriate Level of Abstraction | Names reflect abstraction level? Leaking implementation? |
| CC-189 | N3: Use Standard Nomenclature Where Possible | Using standard terms and pattern names? |
| CC-190 | N4: Unambiguous Names | Names possibly misunderstood? Clear enough? |
| CC-191 | N5: Use Long Names for Long Scopes | Long-scope variables have descriptive names? |
| CC-192 | N6: Avoid Encodings | Avoiding Hungarian notation and encodings? |
| CC-193 | N7: Names Should Describe Side-Effects | Functions with side-effects indicate in name? |

### Tests (T)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-194 | T1: Insufficient Tests | Tests cover all possible failures? |
| CC-195 | T2: Use a Coverage Tool! | Using coverage tool? Coverage meets standard? |
| CC-196 | T3: Don't Skip Trivial Tests | Missing simple test cases? |
| CC-197 | T4: An Ignored Test Is a Question About an Ambiguity | Ignored tests have clear explanation? Plan to resolve? |
| CC-198 | T5: Test Boundary Conditions | Boundary conditions have test coverage? |
| CC-199 | T6: Exhaustively Test Near Bugs | Bug fix includes comprehensive tests? |
| CC-200 | T7: Patterns of Failure Are Revealing | Test failures analyzed for root cause? |
| CC-201 | T8: Test Coverage Patterns Can Be Revealing | Coverage reports used to improve tests? |
| CC-202 | T9: Tests Should Be Fast | Tests fast enough for frequent running? |

---

## Quick Reference by Topic

| Topic | Rules |
|-------|-------|
| **Naming** | CC-4~19, CC-187~193 |
| **Functions** | CC-20~38, CC-147~150, CC-180 |
| **Comments** | CC-39~63, CC-140~144 |
| **Classes** | CC-107~114 |
| **Error Handling** | CC-86~93 |
| **Testing** | CC-99~106, CC-194~202 |
| **Concurrency** | CC-131~139 |
| **Code Smells** | CC-151~186 |
