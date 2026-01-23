# Language-Specific Rule Adjustments

Clean Code and related books are primarily written with Java/OOP in mind. This guide explains how to adjust rules for different programming paradigms.

## Table of Contents

- [Paradigm Classification](#paradigm-classification)
- [Pure OOP Languages](#pure-oop-languages)
- [Multi-Paradigm Languages](#multi-paradigm-languages)
- [Functional-First Languages](#functional-first-languages)
- [Systems Languages](#systems-languages)
- [Procedural Languages](#procedural-languages)
- [Handling Unknown Languages](#handling-unknown-languages)

---

## Paradigm Classification

Before reviewing, identify the language and its primary paradigm:

| Paradigm | Languages | Clean Code Applicability |
|----------|-----------|-------------------------|
| **Pure OOP** | Java, C# | ✅ Fully applicable |
| **Multi-paradigm** | TypeScript, Python, Kotlin, Scala | ⚠️ Adjust for FP patterns |
| **Functional-first** | Haskell, Elixir, Clojure, F#, Elm | ⚠️ Many OOP rules don't apply |
| **Systems/Ownership** | Rust, Zig | ⚠️ Different patterns |
| **Procedural** | C, Go | ⚠️ No classes, different idioms |

---

## Pure OOP Languages

### Java / C#

All Clean Code rules apply as written. These are the target languages of the book.

| Rule | Applicability | Notes |
|------|---------------|-------|
| CC-11: Class Names = Nouns | ✅ Full | Follow exactly |
| CC-12: Method Names = Verbs | ✅ Full | Follow exactly |
| CC-24: Avoid Switch | ✅ Full | Use polymorphism instead |
| CC-88: Unchecked Exceptions | ✅ Full | Java-specific, prefer unchecked |
| CC-92: Don't Return Null | ✅ Full | Use Optional<T> |

---

## Multi-Paradigm Languages

### TypeScript / JavaScript

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-11/12: Class = Noun, Method = Verb | ⚠️ Flexible | Functions are first-class; not everything needs a class |
| CC-24: Avoid Switch | ⚠️ Adjust | Discriminated unions + exhaustive switch is idiomatic |
| CC-92: Don't Return Null | ⚠️ Adjust | Use `undefined`, `null`, or proper types with strict null checks |
| CC-34: Prefer Exceptions | ⚠️ Adjust | Result types and error callbacks are valid patterns |

**TypeScript-specific idioms:**
```typescript
// Discriminated union with exhaustive switch - OK
type Result = { type: 'success'; data: T } | { type: 'error'; message: string };

switch (result.type) {
  case 'success': return handle(result.data);
  case 'error': return showError(result.message);
  // TypeScript ensures exhaustiveness
}
```

### Python

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-9: Avoid Encodings | ⚠️ Adjust | `_private` prefix is Pythonic convention |
| CC-20: Function Length | ⚠️ Adjust | Python is expressive; slightly longer is acceptable |
| CC-26: Limit Parameters | ⚠️ Flexible | `**kwargs` and named arguments provide flexibility |
| PP-51: Avoid Inheritance | ⚠️ Adjust | Mixins and ABCs are idiomatic |

**Python-specific idioms:**
```python
# Private by convention - OK
class MyClass:
    def __init__(self):
        self._internal_state = {}  # Single underscore = private
        self.__mangled = {}        # Double underscore = name mangling

# Dataclasses for DTOs - OK
@dataclass
class User:
    name: str
    email: str
```

### Kotlin

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-92/93: Null Handling | ✅ Enhanced | Use nullable types `?` and safe calls `?.` |
| CC-24: Avoid Switch | ⚠️ Adjust | `when` expression is powerful and idiomatic |
| CC-26: Limit Parameters | ⚠️ Flexible | Named arguments + default values help |
| CC-84: DTOs | ⚠️ Adjust | `data class` is idiomatic |

**Kotlin-specific idioms:**
```kotlin
// Null-safe - preferred pattern
val length = user?.name?.length ?: 0

// When expression - idiomatic
when (result) {
    is Success -> handleSuccess(result.data)
    is Error -> handleError(result.message)
}

// Data class - idiomatic DTO
data class User(val name: String, val email: String)
```

### Scala

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-24: Avoid Switch | ❌ Inapplicable | Pattern matching is fundamental |
| CC-92: Don't Return Null | ✅ Strict | Use `Option[T]`, never null |
| CC-34: Prefer Exceptions | ⚠️ Adjust | `Either[E, A]` and `Try[T]` are idiomatic |
| PP-51: Avoid Inheritance | ⚠️ Adjust | Traits and case classes are idiomatic |

---

## Functional-First Languages

### Haskell / Elm / PureScript

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-11/12: Class Naming | ❌ Inapplicable | No classes; type constructors and functions |
| CC-24: Avoid Switch | ❌ Inapplicable | Pattern matching is the core paradigm |
| CC-92/93: Null Handling | ❌ Inapplicable | `Maybe`/`Option` built into the type system |
| CC-34: Prefer Exceptions | ❌ Inapplicable | `Either`/`Result` types; no exceptions |
| CC-31: No Side Effects | ✅ Core | Enforced by the type system |

**Focus instead on:**
- Type signatures clarity
- Function composition
- Avoiding partial functions
- Proper use of monads

### Elixir / Erlang

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| PP-38: Crash Early | ✅ Core | "Let it crash" is the philosophy |
| CC-24: Avoid Switch | ❌ Inapplicable | Pattern matching everywhere |
| PP-59: Use Actors | ✅ Core | OTP/GenServer is the standard |
| CC-92: Don't Return Null | ⚠️ Different | Use tagged tuples: `{:ok, value}` / `{:error, reason}` |

**Elixir-specific idioms:**
```elixir
# Pattern matching - idiomatic
case result do
  {:ok, value} -> handle_success(value)
  {:error, reason} -> handle_error(reason)
end

# Let it crash - supervisor handles recovery
def handle_call(:risky_operation, _from, state) do
  # Just let it crash if something's wrong
  result = dangerous_operation!()
  {:reply, result, state}
end
```

### Clojure

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-11/12: Class Naming | ❌ Inapplicable | Data and functions, not classes |
| CC-20: Small Functions | ✅ Core | Composable functions are key |
| CA-7: Immutability | ✅ Core | Default is immutable |
| CC-24: Avoid Switch | ⚠️ Adjust | `cond`, `case`, multimethods are idiomatic |

---

## Systems Languages

### Rust

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-92/93: Null Handling | ✅ Enforced | No null exists; use `Option<T>` and `Result<T,E>` |
| CC-24: Avoid Switch | ❌ Inapplicable | `match` is idiomatic and powerful |
| PP-51: Avoid Inheritance | ✅ Enforced | No inheritance; use traits + composition |
| CC-34: Prefer Exceptions | ❌ Inapplicable | No exceptions; use `Result<T,E>` |
| CC-40: Resource Cleanup | ✅ Enforced | RAII via ownership/Drop trait |

**Rust-specific idioms:**
```rust
// Result handling - idiomatic
fn read_file(path: &str) -> Result<String, io::Error> {
    let content = fs::read_to_string(path)?;  // ? operator
    Ok(content)
}

// Match expression - idiomatic
match result {
    Ok(value) => println!("Success: {}", value),
    Err(e) => eprintln!("Error: {}", e),
}

// Traits for polymorphism - idiomatic
trait Drawable {
    fn draw(&self);
}
```

### Zig

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-34: Prefer Exceptions | ❌ Inapplicable | Error unions: `!T` |
| CC-92: Don't Return Null | ⚠️ Adjust | Optional types: `?T` |
| PP-40: Resource Cleanup | ✅ Core | `defer` for cleanup |

---

## Procedural Languages

### Go

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-34: Prefer Exceptions | ❌ Inapplicable | Explicit error returns `(value, err)` |
| CC-11: Class Names | ❌ Inapplicable | No classes; use struct + methods |
| PP-51: Avoid Inheritance | ✅ Enforced | No inheritance; use interfaces + embedding |
| CC-92: Don't Return Null | ⚠️ Different | `nil` is idiomatic for zero values |
| CC-20: Small Functions | ✅ Apply | Go prefers small, focused functions |

**Go-specific idioms:**
```go
// Error handling - idiomatic
result, err := doSomething()
if err != nil {
    return fmt.Errorf("failed to do something: %w", err)
}

// Interface for polymorphism - idiomatic
type Reader interface {
    Read(p []byte) (n int, err error)
}

// Embedding for composition - idiomatic
type Server struct {
    *http.Server
    config Config
}
```

### C

| Rule | Adjustment | Rationale |
|------|------------|-----------|
| CC-11/12: Class Naming | ❌ Inapplicable | No classes; structs and functions |
| CC-34: Prefer Exceptions | ❌ Inapplicable | Return codes and errno |
| PP-40: Resource Cleanup | ✅ Critical | Manual memory management |
| CC-20: Small Functions | ✅ Apply | Especially important for safety |

---

## Handling Unknown Languages

If you encounter an unfamiliar language, ask:

### Key Questions

1. **Paradigm:** Is it OOP, functional, or multi-paradigm?
2. **Null handling:** Does it have null/nil or Option types?
3. **Error handling:** Exceptions, Result types, or error codes?
4. **Inheritance:** Does it have class inheritance or composition-based?
5. **Mutability:** Default mutable or immutable?

### Fallback Strategy

```
IF OOP-based:
    → Apply Clean Code rules with minor adjustments

IF Functional-based:
    → Focus on: function purity, composition, type safety
    → De-emphasize: class design, inheritance rules

IF Systems-based:
    → Focus on: resource management, safety, explicitness
    → De-emphasize: exception handling, null rules

IF Procedural:
    → Focus on: function design, data structures, clarity
    → De-emphasize: OOP-specific rules
```

---

## Quick Reference Table

| Rule Category | OOP | Multi-Paradigm | Functional | Systems | Procedural |
|---------------|-----|----------------|------------|---------|------------|
| Class naming | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Avoid switch | ✅ | ⚠️ | ❌ | ❌ | ⚠️ |
| No null returns | ✅ | ⚠️ | ✅ Built-in | ✅ Built-in | ⚠️ |
| Prefer exceptions | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| Avoid inheritance | ⚠️ | ⚠️ | ✅ | ✅ | ✅ |
| Small functions | ✅ | ✅ | ✅ | ✅ | ✅ |
| No side effects | ⚠️ | ⚠️ | ✅ | ⚠️ | ⚠️ |
| Resource cleanup | ⚠️ | ⚠️ | ⚠️ | ✅ Critical | ✅ Critical |

**Legend:**
- ✅ Fully apply
- ⚠️ Apply with adjustments
- ❌ Not applicable / different pattern
