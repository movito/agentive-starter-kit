# Testing Guide

## Overview

This project follows Test-Driven Development (TDD) practices. All code should be developed using the Red-Green-Refactor cycle.

## Running Tests

### All Tests
```bash
pytest tests/ -v
```

### Fast Tests Only (Skip Slow Tests)
```bash
pytest tests/ -v -m "not slow"
```

### With Coverage Report
```bash
pytest tests/ -v --cov --cov-report=term-missing
```

### Single Test File
```bash
pytest tests/test_template.py -v
```

### Single Test Function
```bash
pytest tests/test_template.py::TestBasicExamples::test_simple_assertion -v
```

## Writing Tests

### TDD Workflow (Red-Green-Refactor)

1. **RED**: Write a failing test first
   ```python
   def test_add_numbers():
       """Should add two numbers correctly."""
       result = add(2, 3)
       assert result == 5
   ```

2. **GREEN**: Write minimum code to pass
   ```python
   def add(a, b):
       return 5  # Stub - just enough to pass
   ```

3. **REFACTOR**: Improve implementation
   ```python
   def add(a, b):
       return a + b  # Proper implementation
   ```

### Test Structure (AAA Pattern)

```python
def test_example():
    """Test description following AAA pattern."""
    # Arrange: Set up test data
    input_data = {"key": "value"}

    # Act: Call the function under test
    result = function_to_test(input_data)

    # Assert: Verify the result
    assert result["status"] == "success"
```

### Using Test Template

Reference `tests/test_template.py` for examples of:
- Class-based test organization
- Fixtures (built-in and custom)
- Edge case testing
- Pytest markers

### Marking Slow Tests

Tests that take >1 second should be marked as slow:

```python
import pytest

@pytest.mark.slow
def test_process_large_file():
    """Process a large file (takes ~5 seconds)."""
    result = process_file("large.txt")
    assert result.success
```

Skip slow tests during development:
```bash
pytest tests/ -v -m "not slow"
```

## Test Organization

```
tests/
├── test_template.py           # Template and examples
├── test_smoke.py              # Smoke tests (verify structure)
├── conftest.py                # Shared fixtures
└── [feature]/                 # Feature-specific tests
    ├── test_api.py
    ├── test_models.py
    └── ...
```

## CI/CD

### GitHub Actions

Tests run automatically on:
- Push to `main` branch
- Pull requests to `main`

View results in the Actions tab of your GitHub repository.

### Pre-commit Hooks

Before each commit, pre-commit runs:
- Code formatting (black, isort)
- Linting (ruff)
- Fast tests (`pytest -m "not slow"`)

**Skip pre-commit** (for WIP commits):
```bash
SKIP_TESTS=1 git commit -m "WIP: In progress work"
```

**Skip specific hook**:
```bash
SKIP=pytest-check git commit -m "WIP"
```

## Coverage Targets

### Recommended Targets
- **Overall**: >70% coverage
- **Critical paths**: >90% coverage
- **New code**: >80% coverage

### View Coverage Report
```bash
pytest tests/ --cov --cov-report=html
open htmlcov/index.html  # Opens in browser
```

## Troubleshooting

### "ModuleNotFoundError" when running tests
```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Reinstall in development mode
pip install -e ".[dev]"
```

### Pre-commit hooks failing
```bash
# Run pre-commit manually to see errors
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### Tests passing locally but failing in CI
- Check Python version (CI may run different version)
- Check for missing dependencies in `pyproject.toml`
- Look at CI logs for environment differences

## Best Practices

1. **Test First**: Write tests before implementation (TDD)
2. **One Assertion**: Each test should verify one behavior
3. **Independent Tests**: Tests should not depend on each other
4. **Clear Names**: Test names should describe what they verify
5. **Fast Tests**: Keep unit tests under 100ms when possible
6. **Mock External Calls**: Don't hit real APIs or file systems in unit tests
7. **Use Fixtures**: Reuse test setup via pytest fixtures

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)
- [TDD Guide](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
