# Principles Spectrum

When principles seem to conflict, they're usually a spectrum. This guide explains when to apply which end.

## Table of Contents

- [DRY vs WET/AHA Spectrum](#dry-vs-wetaha-spectrum)
- [YAGNI vs Future-Proofing Spectrum](#yagni-vs-future-proofing-spectrum)
- [Abstraction Timing](#abstraction-timing)
- [Level-Based Guidelines](#level-based-guidelines)

---

## DRY vs WET/AHA Spectrum

### The Spectrum

```
Over-DRY ←──────────────────────────────────→ Over-WET
(Wrong abstraction)                    (Maintenance nightmare)
     │                                         │
     │       ┌─────────────────────┐           │
     │       │   SWEET SPOT        │           │
     │       │   Rule of Three     │           │
     │       └─────────────────────┘           │
     │                 ↑                       │
     ▼                 │                       ▼
Tight coupling    Right timing          Change one, miss others
Hard to modify    Clear pattern         Bug duplication
```

### Key Insight: DRY is About Knowledge, Not Code

**DRY does NOT mean:** "Never have similar-looking code"

**DRY means:** "Every piece of *knowledge* should have a single source of truth"

### Example: Same Code, Different Knowledge

```python
# These look the same but represent DIFFERENT business rules!
# DO NOT merge them.

def calculate_order_tax(order):
    return order.total * 0.08  # Order tax rate

def calculate_shipping_tax(shipping):
    return shipping.cost * 0.08  # Shipping tax rate (happens to be same)
```

If order tax changes to 0.10 but shipping tax stays 0.08, they should change independently. **This is accidental duplication, not true duplication.**

### Example: Different Code, Same Knowledge

```python
# These look different but represent THE SAME knowledge!
# SHOULD be unified.

# In orders.py
TAX_RATE = 0.08
def calculate_order_tax(order):
    return order.total * TAX_RATE

# In invoices.py  
def calculate_invoice_tax(invoice):
    return invoice.amount * 0.08  # Same tax rate, hardcoded!
```

If the tax rate changes, you'd need to change both. **This is true duplication.**

---

## Decision Framework

### Before Abstracting, Ask:

```
┌─────────────────────────────────────────────────────┐
│ Is this the SAME KNOWLEDGE or just SIMILAR CODE?   │
└─────────────────────────────────────────────────────┘
                        │
           ┌────────────┴────────────┐
           ▼                         ▼
    SAME KNOWLEDGE              SIMILAR CODE
    (True duplication)          (Accidental duplication)
           │                         │
           ▼                         ▼
    ┌─────────────────┐       ┌─────────────────┐
    │ If one changes, │       │ They might      │
    │ must the other  │       │ change          │
    │ ALWAYS change?  │       │ independently   │
    └─────────────────┘       └─────────────────┘
           │                         │
           ▼                         ▼
        UNIFY                   KEEP SEPARATE
```

### Rule of Three

| Occurrences | Action | Rationale |
|-------------|--------|-----------|
| 1st time | Just write it | You don't know the pattern yet |
| 2nd time | Note it, maybe copy | Pattern emerging, but not clear |
| 3rd time | **Consider abstracting** | Pattern is now clear |

**Why wait for three?**
- 1st time: You might be wrong about what's common
- 2nd time: You see similarity but not the full picture
- 3rd time: You can see what varies and what's constant

---

## YAGNI vs Future-Proofing Spectrum

### The Spectrum

```
Extreme YAGNI ←──────────────────────────────→ Over-Engineering
(Constant rewrites)                         (Wasted effort)
     │                                           │
     │         ┌─────────────────────┐           │
     │         │   SWEET SPOT        │           │
     │         │   Extensible but    │           │
     │         │   not extended      │           │
     │         └─────────────────────┘           │
     │                   ↑                       │
     ▼                   │                       ▼
No flexibility     Just enough hooks      Features nobody uses
Rewrite often      Simple extension       Complex unused code
```

### When to Prepare for the Future

| Signal | YAGNI (Don't build) | Future-proof (Build hooks) |
|--------|---------------------|---------------------------|
| Requirement certainty | "Maybe someday..." | "Next sprint we need..." |
| Change cost | Easy to add later | Expensive to retrofit |
| Pattern frequency | First time seeing this | Third time this pattern |
| Project level | L1-L2 | L4-L5 |

### Example

**YAGNI (Don't build):**
```python
# Just need to send emails now
def send_email(to, subject, body):
    smtp.send(to, subject, body)
```

**Future-proof (When L4-L5 and pattern is clear):**
```python
# Multiple notification channels are planned for next month
class NotificationService:
    def __init__(self, channel: NotificationChannel):
        self.channel = channel
    
    def notify(self, recipient, message):
        self.channel.send(recipient, message)
```

---

## Abstraction Timing

### The Abstraction Checklist

Before creating an abstraction, all should be YES:

- [ ] Does this represent a **single business concept**?
- [ ] If one instance changes, must **all instances change**?
- [ ] Can you name the abstraction **clearly** (without "Utils", "Helper", "Common")?
- [ ] Will the abstraction **reduce** overall complexity?

If any is NO, **keep it duplicated** for now.

### Bad Abstraction Signs

| Sign | Problem | Action |
|------|---------|--------|
| Name contains "Utils", "Helper", "Common" | No clear concept | Split by actual purpose |
| Many boolean parameters | Different behaviors forced together | Split into separate functions |
| Constant conditional checks inside | Wrong abstraction level | Rethink the boundary |
| Changes require modifying the abstraction | Abstraction is wrong | Let it diverge |

---

## Level-Based Guidelines

Different strictness levels have different tolerance for duplication:

### DRY Tolerance by Level

| Level | Tolerance | Rationale |
|-------|-----------|-----------|
| **L1** | High (4+ repeats OK) | Code is throwaway, don't waste time abstracting |
| **L2** | Medium-high (4 repeats) | Personal maintenance, abstract when it hurts |
| **L3** | Medium (3 repeats) | Team handoff, abstractions help understanding |
| **L4** | Low (2 repeats) | Wide usage, consistency is critical |
| **L5** | Very low (1 repeat) | Any duplication is a bug waiting to happen |

### YAGNI Tolerance by Level

| Level | YAGNI Strictness | Future-proofing |
|-------|------------------|-----------------|
| **L1** | Maximum YAGNI | None |
| **L2** | Strong YAGNI | Minimal hooks |
| **L3** | Moderate YAGNI | Consider extension points |
| **L4** | Balanced | Plan for known extensions |
| **L5** | Consider stability | Design for change |

### Practical Examples

**L1-L2 (High YAGNI, High DRY tolerance):**
```python
# Just copy-paste, it's fine
def process_user_order(order):
    tax = order.total * 0.08
    return order.total + tax

def process_admin_order(order):
    tax = order.total * 0.08  # Same calculation, but who cares at L1
    return order.total + tax
```

**L4-L5 (Low YAGNI, Low DRY tolerance):**
```python
# Abstract immediately, this is critical code
TAX_RATE = Decimal("0.08")  # Single source of truth

def calculate_tax(amount: Decimal) -> Decimal:
    return amount * TAX_RATE

def process_order(order: Order) -> Decimal:
    return order.total + calculate_tax(order.total)
```

---

## Quick Decision Guide

| Situation | Question | Answer |
|-----------|----------|--------|
| 2nd duplicate | Should I abstract? | **Usually no.** Wait for third. |
| 3rd duplicate | Should I abstract? | **Ask the checklist.** All YES → abstract. |
| Looks similar | Same knowledge? | **Check if they change together.** |
| Adding feature | Build for future? | **Check project level.** L1-L2 = no, L4-L5 = maybe. |
| Naming "Utils" | Good abstraction? | **No.** Find the real concept or keep separate. |

---

## Related Rules

| Rule | Description |
|------|-------------|
| PP-15 | DRY—Don't Repeat Yourself |
| PP-43 | Avoid Fortune-Telling (YAGNI) |
| CA-25 | True duplication vs accidental similarity |
| CC-37 | Don't Repeat Yourself |
| CC-128 | No Duplication |
| CC-130 | Minimal Classes and Methods |
