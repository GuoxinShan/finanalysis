# Quick Reference: Calculation Precision

## The Golden Rule

**Calculate from raw RM'000 values → Then round for display**

Never use rounded values as inputs to new calculations.

---

## Common Scenarios

### 1. Percentage Calculations

✅ **CORRECT**:
```
NCI% = 97,078 / 215,492 = 0.4506 → 45.1%
```

❌ **WRONG**:
```
NCI% = 97.1 / 215.5 = 0.4503 → 45.0%  (error: 0.1pp)
```

---

### 2. Derived Values (Subtraction)

✅ **CORRECT**:
```
NCI = 215,492 - 114,818 = 97,078 → 97.1m
```

❌ **WRONG**:
```
NCI = 215.5 - 114.8 = 100.7m  (error: 3.6m)
```

---

### 3. Growth Rates

✅ **CORRECT**:
```
Growth = (3,252,347 - 2,057,234) / 2,057,234 = 0.5810 → 58.1%
```

❌ **WRONG**:
```
Growth = (3,252.3 - 2,057.2) / 2,057.2 = 0.5809 → 58.1%

Note: Growth rates are MORE resilient (0.01% error),
but still calculate from raw for consistency.
```

---

### 4. Margin Calculations

✅ **CORRECT**:
```
Margin = 525,134 / 3,252,347 = 0.1615 → 16.15%
```

❌ **WRONG**:
```
Margin = 525.1 / 3,252.3 = 0.1615 → 16.15%

Note: Margins are resilient when both rounded consistently,
but still calculate from raw for consistency.
```

---

## When to Use Raw vs. Rounded

| Operation | Use Raw RM'000? | Why |
|-----------|----------------|-----|
| Percentage | ✅ Yes | Error compounds |
| Subtraction | ✅ Yes | Error compounds badly |
| Growth rate | ✅ Yes | Consistency |
| Margin | ✅ Yes | Consistency |
| Display in text | ❌ No | Round for readability |
| Display in table | ❌ No | Round for readability |

---

## Verification Test

If you're unsure, calculate both ways and compare:

```python
# Method 1: From raw
raw_result = raw_numerator / raw_denominator

# Method 2: From rounded
rounded_result = rounded_numerator / rounded_denominator

# Check
if abs(raw_result - rounded_result) > 0.001:  # 0.1%
    print("⚠️ Warning: Rounding error detected!")
    print(f"Use raw method: {raw_result}")
```

---

## In Worker Prompts

When writing worker instructions, include:

```markdown
**Precision Standard**: All calculations must use raw RM'000 values from
fs_index.json. Round ONLY the final display value. Never derive metrics
from rounded table values.

Example:
- ✅ NCI% = 97,078 / 215,492 = 45.1%
- ❌ NCI% = 97.1 / 215.5 = 45.0% (wrong)
```

---

## Data Bundle Format

Ensure data bundles provide raw values:

```json
{
  "metrics": {
    "pat": {
      "raw": 215492,
      "display": "215.5m",
      "unit": "RM'000"
    },
    "nci": {
      "raw": 97078,
      "display": "97.1m",
      "calculated_from": "fs_index.line_items['nci']"
    }
  }
}
```

This way workers have both:
- Raw values for calculations
- Display values for text/tables

---

## Checklist for Workers

Before outputting derived metrics:

- [ ] Did I calculate from raw RM'000 values?
- [ ] Did I round only the final display value?
- [ ] Does my percentage match when calculated both ways?
- [ ] Is my derived value within 0.1% of the source data?

---

**Remember**: Precision isn't about showing more decimals—it's about avoiding error cascades from premature rounding.
