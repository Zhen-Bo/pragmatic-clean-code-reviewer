# Code Review Reference Manual

Complete rule reference from The Pragmatic Programmer (PP), Clean Code (CC), and Clean Architecture (CA).

**Usage:** Consult this when the 11-point checklist triggers uncertainty or for dispute resolution.

---

## The Pragmatic Programmer (PP-1 to PP-100)

### Chapter 1: A Pragmatic Philosophy

| Rule | Name | Review Point |
|------|------|--------------|
| PP-1 | Care About Your Craft | Does code show quality pursuit? |
| PP-2 | Think! About Your Work | Evidence of thought vs copy-paste? |
| PP-4 | Provide Options, Don't Make Excuses | Clear solution in PR description? |
| PP-5 | Don't Live with Broken Windows | Adding code near existing mess without fixing? |
| PP-7 | Remember the Big Picture | Changes align with architecture direction? |

### Chapter 2: A Pragmatic Approach

| Rule | Name | Review Point |
|------|------|--------------|
| PP-14 | Good Design Is Easier to Change (ETC) | Is design easy to modify? Unnecessary coupling? |
| PP-15 | DRY—Don't Repeat Yourself | Duplicate code, logic, or knowledge? |
| PP-16 | Make It Easy to Reuse | Shared logic discoverable and usable? |
| PP-17 | Eliminate Effects Between Unrelated Things | Modules improperly coupled? |
| PP-18 | There Are No Final Decisions | Design allows future changes? |
| PP-19 | Forgo Following Fads | Tech choice based on needs vs hype? |
| PP-20 | Use Tracer Bullets | New feature has end-to-end working path? |
| PP-21 | Prototype to Learn | Prototype code in production? |
| PP-22 | Program Close to Problem Domain | Names reflect business domain? |

### Chapter 3: The Basic Tools

| Rule | Name | Review Point |
|------|------|--------------|
| PP-25 | Keep Knowledge in Plain Text | Config uses readable text format? |
| PP-28 | Always Use Version Control | Proper VCS use? Atomic commits? |
| PP-31 | Failing Test Before Fixing Code | Bug fix includes reproduction test? |
| PP-32 | Read the Damn Error Message | Error handling preserves meaningful messages? |
| PP-34 | Don't Assume It—Prove It | Key assumptions have test validation? |

### Chapter 4: Pragmatic Paranoia

| Rule | Name | Review Point |
|------|------|--------------|
| PP-36 | You Can't Write Perfect Software | Appropriate defensive mechanisms? |
| PP-37 | Design with Contracts | Preconditions/postconditions clear? |
| PP-38 | Crash Early | Fail immediately on impossible states? |
| PP-39 | Use Assertions for the Impossible | "Impossible" cases have assertions? |
| PP-40 | Finish What You Start | Resources properly released? Leak risks? |
| PP-41 | Act Locally | Scope minimized? |
| PP-42 | Take Small Steps—Always | Change small and focused? |
| PP-43 | Avoid Fortune-Telling | Over-engineering for hypothetical future? |

### Chapter 5: Bend, or Break

| Rule | Name | Review Point |
|------|------|--------------|
| PP-44 | Decoupled Code Is Easier to Change | Module coupling reasonable? |
| PP-45 | Tell, Don't Ask | Code violating encapsulation? |
| PP-46 | Don't Chain Method Calls | Violating Law of Demeter? |
| PP-47 | Avoid Global Data | Using global state? Necessary? |
| PP-48 | If Global, Wrap It in an API | Required global state has proper access control? |
| PP-49 | Programs Are About Data | Data flow clear and traceable? |
| PP-50 | Don't Hoard State; Pass It Around | State management reasonable? |
| PP-51 | Don't Pay Inheritance Tax | Inheritance appropriate? Better alternatives? |
| PP-52 | Prefer Interfaces for Polymorphism | Polymorphism via interfaces not inheritance? |
| PP-53 | Delegate to Services: Has-A > Is-A | Using composition over inheritance? |
| PP-55 | Parameterize with External Config | Configurable items externalized? Hardcoding reasonable? |

### Chapter 6: Concurrency

| Rule | Name | Review Point |
|------|------|--------------|
| PP-56 | Analyze Workflow for Concurrency | Concurrent design reasonable? |
| PP-57 | Shared State Is Incorrect State | Unnecessary shared state? Proper sync? |
| PP-58 | Random Failures = Concurrency Issues | Potential race conditions? |
| PP-59 | Use Actors for Stateless Concurrency | Appropriate concurrency model? |

### Chapter 7: While You Are Coding

| Rule | Name | Review Point |
|------|------|--------------|
| PP-62 | Don't Program by Coincidence | Code based on correct assumptions? Undefined behavior? |
| PP-63 | Estimate Algorithm Order | Appropriate algorithm complexity? Performance issues? |
| PP-64 | Test Your Estimates | Performance assumptions validated? |
| PP-65 | Refactor Early, Refactor Often | Code needing refactor? Refactoring part of change? |
| PP-67 | Test Is First User of Code | Code testable? Hard-to-test = design problem |
| PP-68 | Build End-to-End | Feature has end-to-end working path? |
| PP-69 | Design to Test | Design considers testability? |
| PP-70 | Test Your Software | Test coverage sufficient? |
| PP-71 | Use Property-Based Tests | Key algorithms have property tests? |
| PP-72 | Keep It Simple, Minimize Attack Surface | Unnecessary complexity? Minimal public interface? |
| PP-73 | Apply Security Patches Quickly | Dependencies have known vulnerabilities? |
| PP-74 | Name Well; Rename When Needed | Naming clear, consistent, meaningful? |

### Chapter 8: Before the Project

| Rule | Name | Review Point |
|------|------|--------------|
| PP-79 | Policy Is Metadata | Business rules configurable? |
| PP-80 | Use a Project Glossary | Terminology consistent? |

### Chapter 9: Pragmatic Projects

| Rule | Name | Review Point |
|------|------|--------------|
| PP-87 | Do What Works, Not Fashionable | Tech choices based on actual effectiveness? |
| PP-89 | Use VCS for Builds/Tests/Releases | CI/CD properly configured? |
| PP-90 | Test Early, Often, Automatically | Automated tests in CI? |
| PP-91 | Coding Ain't Done 'Til Tests Run | All tests passing? |
| PP-94 | Find Bugs Once | Bug fix includes regression prevention test? |
| PP-95 | Don't Use Manual Procedures | Build and deploy automated? |

---

## Clean Code (CC-1 to CC-202)

### Chapter 1: Clean Code

| Rule | Name | Review Point |
|------|------|--------------|
| CC-1 | Clean Code Is Focused | Each unit does one thing? |
| CC-2 | Readable by Others | Easy to understand? Others can take over? |
| CC-3 | Written by Someone Who Cares | Shows attention to detail and professionalism? |

### Chapter 2: Meaningful Names

| Rule | Name | Review Point |
|------|------|--------------|
| CC-4 | Use Intention-Revealing Names | Names clearly express intent? |
| CC-5 | Avoid Disinformation | Naming might mislead? Matches actual behavior? |
| CC-6 | Make Meaningful Distinctions | Similar names meaningfully different? Using a1, a2? |
| CC-7 | Use Pronounceable Names | Names usable in conversation? |
| CC-8 | Use Searchable Names | Important vars/consts searchable? |
| CC-9 | Avoid Encodings | Using outdated conventions like Hungarian? |
| CC-10 | Avoid Mental Mapping | Reader needs to remember what var represents? |
| CC-11 | Class Names = Nouns | Class names are noun phrases? |
| CC-12 | Method Names = Verbs | Method names are verb phrases? |
| CC-13 | Don't Be Cute | Names clear and direct? Avoiding insider terms? |
| CC-14 | One Word per Concept | Same concept uses same word consistently? |
| CC-15 | Don't Pun | Same word has multiple meanings? |
| CC-16 | Use Solution Domain Names | Technical concepts use correct terms? |
| CC-17 | Use Problem Domain Names | Business concepts use business terms? |
| CC-18 | Add Meaningful Context | Names have enough context? Need prefix/suffix? |
| CC-19 | Don't Add Gratuitous Context | Unnecessary prefix or redundant context? |

### Chapter 3: Functions

| Rule | Name | Review Point |
|------|------|--------------|
| CC-20 | Small! | Function small enough? Can decompose further? |
| CC-21 | Do One Thing | Function does only one thing? Can extract others? |
| CC-22 | One Abstraction Level per Function | Mixing high and low level operations? |
| CC-23 | Stepdown Rule | Code arranged high to low abstraction? |
| CC-24 | Switch Statements | Switch replaceable with polymorphism? Properly encapsulated? |
| CC-25 | Use Descriptive Names | Function name clearly describes behavior? |
| CC-26 | Function Arguments | Param count reasonable? Can reduce? |
| CC-28 | Flag Arguments | Boolean params switching behavior? Split into multiple functions? |
| CC-29 | Argument Objects | Multiple params should be combined into object? |
| CC-31 | Have No Side Effects | Hidden side effects? Doing things not implied by name? |
| CC-32 | Output Arguments | Using params as output? Can return result instead? |
| CC-33 | Command Query Separation | Function both acts and returns state? |
| CC-34 | Prefer Exceptions over Error Codes | Proper exception use? Error codes causing complex nesting? |
| CC-35 | Extract Try/Catch Blocks | Error handling separated from normal logic? |
| CC-36 | Error Handling Is One Thing | Error handling function focused on errors only? |
| CC-37 | Don't Repeat Yourself (DRY) | Duplicate code extractable? |

### Chapter 4: Comments

| Rule | Name | Review Point |
|------|------|--------------|
| CC-39 | Comments Don't Make Up for Bad Code | Comment eliminable by improving code? |
| CC-40 | Explain Yourself in Code | Replace comment with better naming/structure? |
| CC-43 | Good: Explanation of Intent | Complex rules or non-intuitive decisions explained? |
| CC-45 | Good: Warning of Consequences | Dangerous ops or important limits warned? |
| CC-46 | Good: TODO Comments | TODOs tracked? Expired TODOs? |
| CC-48 | Bad: Mumbling | Comment clear and meaningful? Vague comments? |
| CC-49 | Bad: Redundant | Comment harder to read than code? Restating code? |
| CC-50 | Bad: Misleading | Comment matches code behavior? |
| CC-51 | Bad: Mandated | Meaningless forced comments? |
| CC-52 | Bad: Journal | Change log that should be in VCS? |
| CC-53 | Bad: Noise | Meaningless filler comments? |
| CC-54 | Bad: Use Function/Variable Instead | Comment replaceable by well-named function/variable? |
| CC-55 | Bad: Position Markers | Unnecessary dividers or region markers? |
| CC-56 | Bad: Closing Brace Comments | Closing brace comments? Function too long? |
| CC-57 | Bad: Attributions | Attribution that should be in VCS? |
| CC-58 | Bad: Commented-Out Code | Commented-out code present? |
| CC-60 | Bad: Nonlocal Information | Comment describes distant code? |
| CC-61 | Bad: Too Much Information | Comment has too much unrelated info? |
| CC-62 | Bad: Inobvious Connection | Reader can understand what comment means? |
| CC-63 | Bad: Function Headers | Header comment replaceable by better function name? |

### Chapter 6: Objects and Data Structures

| Rule | Name | Review Point |
|------|------|--------------|
| CC-78 | Data Abstraction | Class hides implementation? Exposes abstract interface? |
| CC-79 | Data/Object Anti-Symmetry | Correct choice of object vs data structure? |
| CC-80 | Law of Demeter | Following Law of Demeter? Too many chained calls? |
| CC-81 | Train Wrecks | Long method call chains? Should split? |
| CC-82 | Hybrids | Class exposing both data and behavior? Unclear design? |
| CC-83 | Hiding Structure | Object exposing too much internals? Following Tell Don't Ask? |
| CC-84 | Data Transfer Objects | DTO staying pure? No business logic? |

### Chapter 7: Error Handling

| Rule | Name | Review Point |
|------|------|--------------|
| CC-86 | Use Exceptions over Return Codes | Proper exception use? Error handling separated from main logic? |
| CC-89 | Provide Context with Exceptions | Exception has enough context to understand problem? |
| CC-90 | Define Exceptions by Caller's Needs | Exception hierarchy meaningful? Caller can effectively catch? |
| CC-91 | Define the Normal Flow | Special cases handled elegantly? Using Null Object or Special Case pattern? |
| CC-92 | Don't Return Null | Avoiding null returns? Using Optional or empty collection? |
| CC-93 | Don't Pass Null | Avoiding null as parameter? |

### Chapter 8: Boundaries

| Rule | Name | Review Point |
|------|------|--------------|
| CC-94 | Using Third-Party Code | Third-party code properly encapsulated? Dependencies isolated? |
| CC-97 | Using Code That Doesn't Exist Yet | Using interfaces to isolate unfinished/external modules? |
| CC-98 | Clean Boundaries | System boundaries clearly defined? Boundary change cost controllable? |

### Chapter 9: Unit Tests

| Rule | Name | Review Point |
|------|------|--------------|
| CC-100 | Keeping Tests Clean | Test code clean, readable, maintainable? |
| CC-101 | Tests Enable -ilities | Test coverage supports refactoring and change? |
| CC-102 | Clean Tests | Tests clearly express intent? Easy to understand? |
| CC-104 | One Assert per Test | Each test focused on one concept? Too many asserts? |
| CC-105 | Single Concept per Test | Test focused on single concept? |
| CC-106 | F.I.R.S.T. | Tests Fast, Independent, Repeatable, Self-Validating, Timely? |

### Chapter 10: Classes

| Rule | Name | Review Point |
|------|------|--------------|
| CC-107 | Class Organization | Class structure follows standard organization? |
| CC-108 | Encapsulation | Class properly encapsulated? Minimal public interface? |
| CC-109 | Classes Should Be Small! | Class small enough? Focused on single responsibility? |
| CC-110 | Single Responsibility Principle | Class has only one responsibility? Multiple reasons to change? |
| CC-111 | Cohesion | Class cohesion high? Methods use most class variables? |
| CC-112 | Many Small Classes | Low cohesion class should be split? |
| CC-113 | Organizing for Change (OCP) | Class easy to extend without modifying existing code? |
| CC-114 | Isolating from Change | Dependencies point to abstractions not concretes? |

### Chapter 11: Systems

| Rule | Name | Review Point |
|------|------|--------------|
| CC-115 | Separate Construction from Using | Construction logic separated from business logic? |
| CC-118 | Dependency Injection | Using DI? Dependencies provided externally? |
| CC-119 | Scaling Up | Architecture allows gradual scaling? Over-designed? |
| CC-120 | Cross-Cutting Concerns | Cross-cutting concerns (logging, security, transactions) properly handled? |
| CC-121 | Test Drive Architecture | Architecture starts simple? Over-design signs? |

### Chapter 12: Emergence

| Rule | Name | Review Point |
|------|------|--------------|
| CC-126 | Runs All Tests | All tests pass? System verifiable? |
| CC-128 | No Duplication | Code, logic, knowledge duplication? |
| CC-129 | Expressive | Code clearly expresses intent? Reader can understand? |
| CC-130 | Minimal Classes and Methods | Unnecessary classes or methods? Over-designed? |

### Chapter 13: Concurrency

| Rule | Name | Review Point |
|------|------|--------------|
| CC-131 | Why Concurrency? | Concurrency really needed? Just adding complexity? |
| CC-133 | Concurrency Defense Principles | Following SRP, limiting scope, using copies, thread independence? |
| CC-134 | Know Your Library | Correctly using language's concurrency tools? Using thread-safe collections? |
| CC-135 | Know Your Execution Models | Appropriate concurrency model? Understanding its characteristics? |
| CC-136 | Beware Synchronized Method Dependencies | Dependencies between sync methods? Deadlock possible? |
| CC-137 | Keep Synchronized Sections Small | Synchronized sections minimized? Unnecessary long sync blocks? |
| CC-138 | Correct Shutdown Is Hard | Shutdown logic correct? All threads and resources handled? |
| CC-139 | Testing Threaded Code | Multithreaded code has proper tests? Stress tested? |

### Appendix: Smells and Heuristics

#### Comments (CC-140 to CC-144)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-140 | C1: Inappropriate Information | Comment has info that shouldn't be in code? |
| CC-141 | C2: Obsolete Comment | Outdated comment inconsistent with code? |
| CC-142 | C3: Redundant Comment | Comment just repeats what code expresses? |
| CC-143 | C4: Poorly Written Comment | Comment clear, concise, correct? |
| CC-144 | C5: Commented-Out Code | Commented-out code present? |

#### Environment (CC-145 to CC-146)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-145 | E1: Build Requires Multiple Steps | Build automated and simple? |
| CC-146 | E2: Tests Require Multiple Steps | Tests can run in one step? |

#### Functions (CC-147 to CC-150)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-147 | F1: Too Many Arguments | Function has more than 3 params? Can reduce? |
| CC-148 | F2: Output Arguments | Using params as output? |
| CC-149 | F3: Flag Arguments | Boolean params controlling function behavior? |
| CC-150 | F4: Dead Function | Unused functions? |

#### General (CC-151 to CC-186)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-151 | G1: Multiple Languages in One File | Source file mixes languages? Separable? |
| CC-152 | G2: Obvious Behavior Unimplemented | Behavior matches expectations? Surprises or omissions? |
| CC-153 | G3: Incorrect Boundary Behavior | Boundary conditions correctly handled? Test covered? |
| CC-154 | G4: Overridden Safeties | Disabled warnings or tests? |
| CC-155 | G5: Duplication | Duplicate code, logic, knowledge? |
| CC-156 | G6: Wrong Abstraction Level | Code at correct abstraction level? |
| CC-157 | G7: Base Classes Depend on Derivatives | Base class independent of derived? |
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
| CC-173 | G23: Prefer Polymorphism over If/Else/Switch | Replace conditional logic with polymorphism? |
| CC-174 | G24: Follow Standard Conventions | Code follows team coding standards? |
| CC-175 | G25: Replace Magic Numbers | Unnamed magic numbers? |
| CC-176 | G26: Be Precise | Code precisely handles various situations? Vague assumptions? |
| CC-177 | G27: Structure over Convention | Design decisions enforced by structure? |
| CC-178 | G28: Encapsulate Conditionals | Complex conditionals extracted into meaningfully named functions? |
| CC-179 | G29: Avoid Negative Conditionals | Negative conditionals rewritable as positive? |
| CC-180 | G30: Functions Should Do One Thing | Functions doing more than one thing? Should decompose? |
| CC-181 | G31: Hidden Temporal Couplings | Temporal dependencies explicit? |
| CC-182 | G32: Don't Be Arbitrary | Code structure has reason? Avoiding arbitrary decisions? |
| CC-183 | G33: Encapsulate Boundary Conditions | Boundary conditions centrally handled? |
| CC-184 | G34: One Abstraction Level per Function | Function operates at single abstraction level? |
| CC-185 | G35: Keep Configurable Data at High Levels | Config data at high level and accessible? |
| CC-186 | G36: Avoid Transitive Navigation | Following Law of Demeter? Avoiding deep navigation? |

#### Names (CC-187 to CC-193)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-187 | N1: Choose Descriptive Names | Names descriptive and accurate? |
| CC-188 | N2: Names at Appropriate Abstraction Level | Names reflect abstraction level? Leaking implementation? |
| CC-189 | N3: Use Standard Nomenclature | Using standard terms and pattern names? |
| CC-190 | N4: Unambiguous Names | Names possibly misunderstood? Clear enough? |
| CC-191 | N5: Long Names for Long Scopes | Long-scope variables have descriptive names? |
| CC-192 | N6: Avoid Encodings | Avoiding Hungarian notation and encodings? |
| CC-193 | N7: Names Should Describe Side-Effects | Functions with side-effects indicate in name? |

#### Tests (CC-194 to CC-202)

| Rule | Name | Review Point |
|------|------|--------------|
| CC-194 | T1: Insufficient Tests | Tests cover all possible failures? |
| CC-195 | T2: Use Coverage Tool | Using coverage tool? Coverage meets standard? |
| CC-196 | T3: Don't Skip Trivial Tests | Missing simple test cases? |
| CC-197 | T4: Ignored Test = Question About Ambiguity | Ignored tests have clear explanation? Plan to resolve? |
| CC-198 | T5: Test Boundary Conditions | Boundary conditions have test coverage? |
| CC-199 | T6: Exhaustively Test Near Bugs | Bug fix includes comprehensive tests? |
| CC-200 | T7: Failure Patterns Are Revealing | Test failures analyzed for root cause? |
| CC-201 | T8: Coverage Patterns Are Revealing | Coverage reports used to improve tests? |
| CC-202 | T9: Tests Should Be Fast | Tests fast enough for frequent running? |

---

## Clean Architecture (CA-1 to CA-48)

### Part 1: Introduction

| Rule | Name | Review Point |
|------|------|--------------|
| CA-1 | Design and Architecture Are Same | Architecture and design decisions consistent? |
| CA-2 | Goal: Minimize Human Resources | Architecture reduces maintenance cost? Easy to understand and modify? |
| CA-3 | Behavior vs Structure | Over-focusing on features while ignoring structure? Code easy to change? |

### Part 2: Programming Paradigms

| Rule | Name | Review Point |
|------|------|--------------|
| CA-5 | Structured Programming | Control flow clear? Avoiding complex jumps? |
| CA-6 | Object-Oriented Programming | Polymorphism correctly used? Dependency direction correct? |
| CA-7 | Functional Programming | Appropriate use of immutability? Minimizing side effects? |

### Part 3: Design Principles (SOLID)

| Rule | Name | Review Point |
|------|------|--------------|
| CA-8 | SRP: Single Responsibility | Module responsible to only one actor? Multiple reasons to change? |
| CA-9 | OCP: Open-Closed | Adding features requires modifying existing code? Can extend instead? |
| CA-10 | LSP: Liskov Substitution | Subclass can fully substitute parent? Correct inheritance relationship? |
| CA-11 | ISP: Interface Segregation | Interface too large? Client forced to implement unneeded methods? |
| CA-12 | DIP: Dependency Inversion | Dependency direction correct? Depending on abstractions not concretes? |

### Part 4: Component Principles

| Rule | Name | Review Point |
|------|------|--------------|
| CA-13 | Components | Component division reasonable? Considering deployment units? |
| CA-14 | REP: Reuse/Release Equivalence | Reusable components independently releasable? Version control reasonable? |
| CA-15 | CCP: Common Closure | Frequently co-changing classes in same component? |
| CA-16 | CRP: Common Reuse | Component has unrelated functionality? Users forced to bring unneeded dependencies? |
| CA-17 | Component Cohesion Tension | Component design considers project stage? Balancing cohesion principles? |
| CA-18 | ADP: Acyclic Dependencies | Circular dependencies between components? |
| CA-19 | SDP: Stable Dependencies | Depending on less stable components? |
| CA-20 | SAP: Stable Abstractions | Stable components abstract enough? Concrete implementations in unstable components? |

### Part 5: Architecture

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
| CA-31 | Clean Architecture | Dependencies only point inward? Outer depends on inner? |
| CA-32 | Presenters and Humble Objects | Hard-to-test parts isolated? Using Humble Object pattern? |
| CA-33 | Partial Boundaries | Boundary cost reasonable? Can use more lightweight approach? |
| CA-34 | Layers and Boundaries | Boundaries in appropriate locations? Over-design or under-design? |
| CA-35 | The Main Component | Main component only handles initialization? Correctly transfers control to high level? |

### Part 6: Details

| Rule | Name | Review Point |
|------|------|--------------|
| CA-36 | Services: Great and Small | Service split really needed? Over-microserviced? |
| CA-37 | The Test Boundary | Tests correctly depend on tested code? Test structure reflects system structure? |
| CA-38 | Clean Embedded Architecture | Hardware/platform code isolated? Business logic independently testable? |
| CA-39 | Database Is a Detail | Business logic depends on specific database? Easy to swap databases? |
| CA-40 | Web Is a Detail | Business logic depends on specific UI framework? Easy to swap UI? |
| CA-41 | Frameworks Are Details | Over-depending on framework? Business logic can exist without framework? |
| CA-42 | Case Study | Architecture follows clean architecture principles? Components correctly identified and organized? |

### Appendix

| Rule | Name | Review Point |
|------|------|--------------|
| CA-43 | Boy Scout Rule for Architecture | Change improves or maintains architecture quality? |
| CA-44 | Cost of Change | Changes getting harder? Architecture supports continuous evolution? |
| CA-45 | Keep Options Open | Locking in tech decisions too early? Maintaining enough flexibility? |
| CA-46 | Dependency Management | Dependency direction correct? Improper dependencies? |
| CA-47 | Humble Object Pattern | Using humble objects to isolate hard-to-test code? |
| CA-48 | Plugin Architecture | Details as plugins? Core independent of details? |

---

## Quick Lookup by Symptom

| Symptom | Related Rules |
|---------|---------------|
| Function too long | CC-20, CC-21, CC-180 |
| Too many parameters | CC-26, CC-29, CC-147 |
| Duplicate code | PP-15, CC-37, CC-128, CC-155 |
| Hard to test | PP-67, PP-69, CC-114, CA-47 |
| Tight coupling | PP-17, PP-44, CC-114, CA-12 |
| God class | CC-109, CC-110, CA-8 |
| Feature envy | CC-164 |
| Primitive obsession | CC-29 |
| Switch statements | CC-24, CC-173 |
| Null issues | CC-92, CC-93 |
| Magic numbers | CC-175 |
| Dead code | CC-150, CC-159 |
| Comments smell | CC-39, CC-58, CC-141, CC-144 |
| Naming issues | CC-4~19, CC-187~193, PP-74 |
| Error handling | CC-86~93, PP-36~39 |
| Test issues | CC-99~106, CC-194~202, PP-91 |
| Concurrency | CC-131~139, PP-56~59 |
| Architecture | CA-21~48 |
