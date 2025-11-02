# Example Component Specification

**Component Name:** example_component
**Target Stage:** staging
**Version:** 1.0.0
**Date:** 2025-10-20

---

## Overview

This is an example component specification demonstrating the format expected by the integrated workflow system. This component provides a simple calculator service with basic arithmetic operations.

---

## Requirements

### Functional Requirements

1. **Addition Operation**
   - Accept two numbers as input
   - Return their sum
   - Support integers and floats

2. **Subtraction Operation**
   - Accept two numbers as input
   - Return their difference
   - Support integers and floats

3. **Multiplication Operation**
   - Accept two numbers as input
   - Return their product
   - Support integers and floats

4. **Division Operation**
   - Accept two numbers as input
   - Return their quotient
   - Handle division by zero gracefully
   - Support integers and floats

### Non-Functional Requirements

1. **Performance**
   - All operations complete in <10ms
   - Support concurrent operations

2. **Reliability**
   - Handle invalid inputs gracefully
   - Return appropriate error messages

3. **Maintainability**
   - Well-documented code
   - Comprehensive test coverage (≥70%)
   - Type hints for all functions

---

## API Design

### Calculator Class

```python
class Calculator:
    """Simple calculator with basic arithmetic operations."""

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        pass

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        pass

    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        pass

    def divide(self, a: float, b: float) -> float:
        """Divide a by b. Raises ValueError if b is zero."""
        pass
```

---

## Implementation Notes

### Error Handling

- Division by zero should raise `ValueError` with message "Cannot divide by zero"
- Invalid input types should raise `TypeError` with descriptive message

### Testing Requirements

- Unit tests for all operations
- Edge case tests (zero, negative numbers, very large numbers)
- Error handling tests
- Coverage target: ≥70%

---

## Dependencies

- Python 3.12+
- No external dependencies required

---

## Acceptance Criteria

1. ✅ All four operations implemented
2. ✅ All tests passing
3. ✅ Test coverage ≥70%
4. ✅ Type hints for all functions
5. ✅ Docstrings for all public methods
6. ✅ Error handling for edge cases
7. ✅ Linting passes (ruff)
8. ✅ Type checking passes (pyright)

---

## Maturity Stage Targets

### Development
- Basic functionality implemented
- Initial tests written
- Coverage ≥50%

### Staging
- All functionality complete
- Comprehensive tests
- Coverage ≥70%
- Documentation complete
- All quality gates passing

### Production
- Integration tests added
- Coverage ≥80%
- Performance validated
- 7-day staging stability

---

## Example Usage

```python
from example_component import Calculator

calc = Calculator()

# Basic operations
result = calc.add(5, 3)  # 8
result = calc.subtract(10, 4)  # 6
result = calc.multiply(3, 7)  # 21
result = calc.divide(15, 3)  # 5.0

# Error handling
try:
    result = calc.divide(10, 0)
except ValueError as e:
    print(f"Error: {e}")  # "Cannot divide by zero"
```

---

## Related Components

- None (standalone component)

---

## Notes

This is a minimal example component designed to demonstrate the workflow system. Real components would have more complex requirements and dependencies.
