# Test-Driven Development Basics: Reusable Pattern

**Layer:** Foundation
**Topic:** 1.3 Test-Driven Development Basics
**Type:** Template + Checklist

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

## When to Use This Pattern

Use these TDD patterns when:
- Implementing new functions or methods with clear requirements
- Fixing bugs where you can reproduce the failure
- Refactoring code that needs to maintain existing behavior
- Building features where correctness is critical
- Working on code that will be maintained long-term

## The Pattern

### AAA Test Template

```python
def test_[function_name]_[scenario]_[expected_result]():
    """Test that [function] [does what] when [given what input]."""
    # ARRANGE - Set up test data and preconditions
    [input_data] = [create test input]
    [expected_output] = [define expected result]

    # ACT - Execute the function under test
    [actual_output] = [function_under_test]([input_data])

    # ASSERT - Verify the actual output matches expectations
    assert [actual_output] == [expected_output]
```

**JavaScript/Jest version:**
```javascript
test('[function] [scenario] [expected result]', () => {
  // ARRANGE - Set up test data and preconditions
  const inputData = [create test input];
  const expectedOutput = [define expected result];

  // ACT - Execute the function under test
  const actualOutput = [functionUnderTest](inputData);

  // ASSERT - Verify the actual output matches expectations
  expect(actualOutput).toEqual(expectedOutput);
});
```

### Test Naming Convention

**Format:** `test_[function]_[scenario]_[expected_result]`

**Examples:**
- `test_parse_duration_valid_minutes_returns_int`
- `test_parse_duration_invalid_format_raises_error`
- `test_calculate_timecode_zero_frames_returns_midnight`
- `test_user_login_correct_password_creates_session`

**Guidelines:**
- Use underscores to separate parts (Python) or camelCase (JavaScript)
- Function name first - groups related tests when sorted alphabetically
- Scenario describes the input or condition being tested
- Expected result states what should happen (not what shouldn't)

### RED-GREEN-REFACTOR Checklist

**RED - Write a Failing Test:**
- [ ] Write test for ONE specific behavior
- [ ] Run test - verify it FAILS with clear error message
- [ ] Failure reason is correct (not syntax error or import failure)
- [ ] Test name describes what's being tested

**GREEN - Make It Pass:**
- [ ] Write MINIMUM code to make test pass
- [ ] Avoid over-engineering - solve exactly this case
- [ ] Run test - verify it now PASSES
- [ ] Run ALL tests - verify no regressions

**REFACTOR - Improve the Code:**
- [ ] Remove duplication between test cases
- [ ] Clarify variable names and structure
- [ ] Extract reusable functions if pattern emerges
- [ ] Run ALL tests after each refactor - verify still passing
- [ ] Commit the working code

**Repeat:** Write next test (RED), make it pass (GREEN), refactor if needed, commit.

## Usage Example

**Scenario:** Implementing a `calculate_discount(price, percent)` function.

**RED - Write failing test:**
```python
def test_calculate_discount_20_percent_reduces_price_by_fifth():
    """Test that 20% discount on $100 returns $80."""
    # ARRANGE
    original_price = 100
    discount_percent = 20
    expected_price = 80

    # ACT
    discounted_price = calculate_discount(original_price, discount_percent)

    # ASSERT
    assert discounted_price == expected_price
```

Run test → **FAILS** (function doesn't exist yet). ✓ This is correct.

**GREEN - Make it pass:**
```python
def calculate_discount(price, percent):
    """Apply percent discount to price."""
    return price - (price * percent / 100)
```

Run test → **PASSES**. ✓ Minimum implementation complete.

**REFACTOR - Improve:**
Code is already clean. Commit and move to next test.

**RED - Next test (edge case):**
```python
def test_calculate_discount_zero_percent_returns_original_price():
    """Test that 0% discount returns unchanged price."""
    # ARRANGE
    original_price = 50
    discount_percent = 0
    expected_price = 50

    # ACT
    discounted_price = calculate_discount(original_price, discount_percent)

    # ASSERT
    assert discounted_price == expected_price
```

Run test → **PASSES** (implementation already handles this). ✓ Good!

**RED - Error case:**
```python
def test_calculate_discount_invalid_percent_raises_error():
    """Test that discount >100% raises ValueError."""
    # ARRANGE
    original_price = 100
    discount_percent = 150  # Invalid

    # ACT & ASSERT
    with pytest.raises(ValueError):
        calculate_discount(original_price, discount_percent)
```

Run test → **FAILS** (no validation yet). ✓ This is correct.

**GREEN - Add validation:**
```python
def calculate_discount(price, percent):
    """Apply percent discount to price."""
    if percent < 0 or percent > 100:
        raise ValueError("Discount percent must be between 0 and 100")
    return price - (price * percent / 100)
```

Run test → **PASSES**. All tests pass. Commit.

## Customization Tips

**For different test types:**
- **Unit tests:** Use AAA pattern strictly - one function, clear inputs/outputs
- **Integration tests:** ARRANGE may include database setup, ACT calls multiple functions
- **End-to-end tests:** ARRANGE sets up entire system state, ACT simulates user actions

**For different languages:**
- **Python:** Use pytest, descriptive test names with underscores
- **JavaScript:** Use Jest/Vitest, camelCase test names
- **Go:** Use table-driven tests with AAA structure in each case
- **Rust:** Use `#[test]` attribute with descriptive names

**Adjust TDD rigor based on:**
- **Critical code:** Strict TDD with high coverage (>90%)
- **Exploratory work:** Lighter testing, add tests once approach is proven
- **UI layout:** Visual review often better than brittle snapshot tests
- **Throwaway prototypes:** Skip TDD entirely, evaluate value first

---

## Key Terms

This document uses these terms from **agentive development** (a methodology treating AI assistants as specialized collaborators, not mere code generators):

- **Agent** - AI collaborator with a specific role and tool access
- **Task** - Discrete unit of work with clear acceptance criteria
- **Quality gate** - Objective pass/fail criteria before proceeding
- **TDD (Test-Driven Development)** - Practice of writing tests before implementation
- **Template** - Reusable document structure with placeholders

See the [full glossary](../../../../.agent-context/agentive-development-glossary.md) for complete terminology reference.

---

**See also:**
- [Concept: Test-Driven Development Basics](./concept.md)
- [Example: Test-Driven Development Basics](./example.md)
- [1.2 Discrete Task Decomposition](../02-discrete-task-decomposition/concept.md)
