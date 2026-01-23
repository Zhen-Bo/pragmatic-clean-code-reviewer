# The Pragmatic Programmer Reference

Complete rule reference from *The Pragmatic Programmer* (20th Anniversary Edition) by David Thomas and Andrew Hunt.

## Table of Contents

- [Chapter 1: A Pragmatic Philosophy](#chapter-1-a-pragmatic-philosophy)
- [Chapter 2: A Pragmatic Approach](#chapter-2-a-pragmatic-approach)
- [Chapter 3: The Basic Tools](#chapter-3-the-basic-tools)
- [Chapter 4: Pragmatic Paranoia](#chapter-4-pragmatic-paranoia)
- [Chapter 5: Bend, or Break](#chapter-5-bend-or-break)
- [Chapter 6: Concurrency](#chapter-6-concurrency)
- [Chapter 7: While You Are Coding](#chapter-7-while-you-are-coding)
- [Chapter 8: Before the Project](#chapter-8-before-the-project)
- [Chapter 9: Pragmatic Projects](#chapter-9-pragmatic-projects)

---

## Chapter 1: A Pragmatic Philosophy

| Rule | Name | Review Point |
|------|------|--------------|
| PP-1 | Care About Your Craft | Does code show quality pursuit? |
| PP-2 | Think! About Your Work | Evidence of thought vs copy-paste? |
| PP-3 | You Have Agency | Taking ownership of decisions? Not blaming tools/process? |
| PP-4 | Provide Options, Don't Make Excuses | Clear solution in PR description? |
| PP-5 | Don't Live with Broken Windows | Adding code near existing mess without fixing? |
| PP-6 | Be a Catalyst for Change | Does this change encourage better practices? |
| PP-7 | Remember the Big Picture | Changes align with architecture direction? |
| PP-8 | Make Quality a Requirements Issue | Is quality being traded off appropriately? |
| PP-9 | Invest Regularly in Your Knowledge Portfolio | *(Personal skill, not code review)* |
| PP-10 | Critically Analyze What You Read and Hear | *(Personal skill, not code review)* |
| PP-11 | English is Just Another Programming Language | Is documentation clear and precise? |
| PP-12 | It's Both What You Say and the Way You Say It | Are commit messages and comments well-written? |
| PP-13 | Build Documentation In, Don't Bolt It On | Is documentation integrated or afterthought? |

---

## Chapter 2: A Pragmatic Approach

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
| PP-23 | Estimate to Avoid Surprises | Are estimates realistic and documented? |
| PP-24 | Iterate the Schedule with the Code | Is schedule updated as understanding improves? |

---

## Chapter 3: The Basic Tools

| Rule | Name | Review Point |
|------|------|--------------|
| PP-25 | Keep Knowledge in Plain Text | Config uses readable text format? |
| PP-26 | Use the Power of Command Shells | *(Personal skill, not code review)* |
| PP-27 | Achieve Editor Fluency | *(Personal skill, not code review)* |
| PP-28 | Always Use Version Control | Proper VCS use? Atomic commits? |
| PP-29 | Fix the Problem, Not the Blame | Bug fix focuses on root cause? Not finger-pointing? |
| PP-30 | Don't Panic | Debugging approach is systematic, not random? |
| PP-31 | Failing Test Before Fixing Code | Bug fix includes reproduction test? |
| PP-32 | Read the Damn Error Message | Error handling preserves meaningful messages? |
| PP-33 | "select" Isn't Broken | Blaming libraries/frameworks without evidence? |
| PP-34 | Don't Assume It—Prove It | Key assumptions have test validation? |
| PP-35 | Learn a Text Manipulation Language | *(Personal skill, not code review)* |

---

## Chapter 4: Pragmatic Paranoia

| Rule | Name | Review Point |
|------|------|--------------|
| PP-36 | You Can't Write Perfect Software | Appropriate defensive mechanisms? |
| PP-37 | Design with Contracts | Preconditions/postconditions clear? |
| PP-38 | Crash Early | Fail immediately on impossible states? |
| PP-39 | Use Assertions for the Impossible | "Impossible" cases have assertions? |
| PP-40 | Finish What You Start | Resources properly released? Leak risks? |
| PP-41 | Act Locally | Scope minimized? |
| PP-42 | Take Small Steps—Always | Change small and focused? |
| PP-43 | Avoid Fortune-Telling | Over-engineering for hypothetical future? (YAGNI) |

---

## Chapter 5: Bend, or Break

| Rule | Name | Review Point |
|------|------|--------------|
| PP-44 | Decoupled Code Is Easier to Change | Module coupling reasonable? |
| PP-45 | Tell, Don't Ask | Code violating encapsulation? |
| PP-46 | Don't Chain Method Calls | Violating Law of Demeter? |
| PP-47 | Avoid Global Data | Using global state? Necessary? |
| PP-48 | If Global, Wrap It in an API | Required global state has proper access control? |
| PP-49 | Programming Is About Code, But Programs Are About Data | Data flow clear and traceable? |
| PP-50 | Don't Hoard State; Pass It Around | State management reasonable? |
| PP-51 | Don't Pay Inheritance Tax | Inheritance appropriate? Better alternatives? |
| PP-52 | Prefer Interfaces to Express Polymorphism | Polymorphism via interfaces not inheritance? |
| PP-53 | Delegate to Services: Has-A Trumps Is-A | Using composition over inheritance? |
| PP-54 | Use Mixins to Share Functionality | Mixins/traits used appropriately? |
| PP-55 | Parameterize Your App Using External Configuration | Configurable items externalized? Hardcoding reasonable? |

---

## Chapter 6: Concurrency

| Rule | Name | Review Point |
|------|------|--------------|
| PP-56 | Analyze Workflow to Improve Concurrency | Concurrent design reasonable? |
| PP-57 | Shared State Is Incorrect State | Unnecessary shared state? Proper sync? |
| PP-58 | Random Failures Are Often Concurrency Issues | Potential race conditions? |
| PP-59 | Use Actors For Concurrency Without Shared State | Appropriate concurrency model? |
| PP-60 | Use Blackboards to Coordinate Workflow | Complex coordination handled properly? |

---

## Chapter 7: While You Are Coding

| Rule | Name | Review Point |
|------|------|--------------|
| PP-61 | Listen to Your Inner Lizard | Does something feel wrong? Trust it. |
| PP-62 | Don't Program by Coincidence | Code based on correct assumptions? Undefined behavior? |
| PP-63 | Estimate the Order of Your Algorithms | Appropriate algorithm complexity? Performance issues? |
| PP-64 | Test Your Estimates | Performance assumptions validated? |
| PP-65 | Refactor Early, Refactor Often | Code needing refactor? Refactoring part of change? |
| PP-66 | Testing Is Not About Finding Bugs | Tests document behavior and enable refactoring |
| PP-67 | A Test Is the First User of Your Code | Code testable? Hard-to-test = design problem |
| PP-68 | Build End-to-End, Not Top-Down or Bottom-Up | Feature has end-to-end working path? |
| PP-69 | Design to Test | Design considers testability? |
| PP-70 | Test Your Software, or Your Users Will | Test coverage sufficient? |
| PP-71 | Use Property-Based Tests to Validate Your Assumptions | Key algorithms have property tests? |
| PP-72 | Keep It Simple and Minimize Attack Surfaces | Unnecessary complexity? Minimal public interface? |
| PP-73 | Apply Security Patches Quickly | Dependencies have known vulnerabilities? |
| PP-74 | Name Well; Rename When Needed | Naming clear, consistent, meaningful? |

---

## Chapter 8: Before the Project

| Rule | Name | Review Point |
|------|------|--------------|
| PP-75 | No One Knows Exactly What They Want | Requirements clarified and validated? |
| PP-76 | Programmers Help People Understand What They Want | Active requirement discovery? |
| PP-77 | Requirements Are Learned in a Feedback Loop | Iterative requirement refinement? |
| PP-78 | Work with a User to Think Like a User | User perspective considered? |
| PP-79 | Policy Is Metadata | Business rules configurable? |
| PP-80 | Use a Project Glossary | Terminology consistent? |

---

## Chapter 9: Pragmatic Projects

| Rule | Name | Review Point |
|------|------|--------------|
| PP-81 | Don't Go into the Code Alone | Pair programming or review in place? |
| PP-82 | Agile Is Not a Noun; Agile Is How You Do Things | Process enables adaptation? |
| PP-83 | Maintain Small, Stable Teams | Team structure supports ownership? |
| PP-84 | Schedule It to Make It Happen | Improvement tasks scheduled? |
| PP-85 | Organize Fully Functional Teams | Team has all needed skills? |
| PP-86 | Do What Works, Not What's Fashionable | Tech choices based on effectiveness? |
| PP-87 | Deliver When Users Need It | Delivery aligns with user needs? |
| PP-88 | Use Version Control to Drive Builds, Tests, and Releases | CI/CD properly configured? |
| PP-89 | Test Early, Test Often, Test Automatically | Automated tests in CI? |
| PP-90 | Coding Ain't Done 'Til All the Tests Run | All tests passing? |
| PP-91 | Use Saboteurs to Test Your Testing | Mutation testing considered? |
| PP-92 | Test State Coverage, Not Code Coverage | Tests cover important states? |
| PP-93 | Find Bugs Once | Bug fix includes regression prevention test? |
| PP-94 | Don't Use Manual Procedures | Build and deploy automated? |
| PP-95 | Delight Users, Don't Just Deliver Code | User experience considered? |
| PP-96 | Sign Your Work | Code shows pride in craftsmanship? |
| PP-97 | First, Do No Harm | Changes don't break existing functionality? |
| PP-98 | Don't Enable Scoundrels | Not building harmful features? |
| PP-99 | It's Your Life | *(Personal philosophy, not code review)* |
| PP-100 | Share | Knowledge being shared with team? |

---

## Quick Reference by Topic

| Topic | Rules |
|-------|-------|
| **Code Quality** | PP-1, PP-2, PP-5, PP-65, PP-74 |
| **Design** | PP-14, PP-17, PP-44, PP-51, PP-52, PP-53 |
| **DRY/Reuse** | PP-15, PP-16 |
| **Testing** | PP-31, PP-34, PP-66, PP-67, PP-69, PP-70, PP-71, PP-89, PP-90 |
| **Error Handling** | PP-36, PP-37, PP-38, PP-39, PP-40 |
| **Concurrency** | PP-56, PP-57, PP-58, PP-59, PP-60 |
| **Security** | PP-72, PP-73 |
| **Architecture** | PP-7, PP-18, PP-43, PP-55 |
| **Team/Process** | PP-81, PP-82, PP-83, PP-84, PP-94 |
