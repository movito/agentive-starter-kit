"""
Test Template for TDD Workflow
==============================

Copy this file when creating new test suites.

Usage:
    1. Copy to tests/test_<feature>.py
    2. Replace placeholder tests with real tests
    3. Run: pytest tests/test_<feature>.py -v

TDD Workflow:
    1. RED: Write failing tests first
    2. GREEN: Implement minimum code to pass
    3. REFACTOR: Improve while keeping tests green

"""

import pytest


class TestFeatureName:
    """Tests for [Feature Name].

    Replace this docstring with a description of what you're testing.
    """

    def test_placeholder_passes(self):
        """Placeholder test - replace with real test.

        Follow AAA pattern:
        - Arrange: Set up test data
        - Act: Call the function/method
        - Assert: Verify the result
        """
        # Arrange
        expected = True

        # Act
        result = True

        # Assert
        assert result == expected

    def test_placeholder_example_with_fixture(self, tmp_path):
        """Example test using pytest fixture.

        Common fixtures:
        - tmp_path: Temporary directory (pathlib.Path)
        - capsys: Capture stdout/stderr
        - monkeypatch: Mock attributes/environment
        """
        # Arrange
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello", encoding="utf-8")

        # Act
        content = test_file.read_text(encoding="utf-8")

        # Assert
        assert content == "hello"

    @pytest.mark.skip(reason="Not implemented yet - TDD RED phase")
    def test_future_feature(self):
        """Test for feature not yet implemented.

        Use @pytest.mark.skip for tests you're planning but haven't
        implemented yet. Remove skip when ready to implement.
        """
        pass


class TestEdgeCases:
    """Edge case tests for [Feature Name].

    Always test:
    - Empty inputs
    - Invalid inputs
    - Boundary conditions
    - Error handling
    """

    def test_handles_empty_input(self):
        """Test behavior with empty input."""
        # Arrange
        empty_input = ""

        # Act & Assert
        assert len(empty_input) == 0

    def test_handles_none_input(self):
        """Test behavior with None input."""
        # Arrange
        none_input = None

        # Act & Assert
        assert none_input is None


# Fixtures can be defined at module level
@pytest.fixture
def sample_data():
    """Provide sample test data.

    Fixtures are reusable across tests.
    """
    return {"name": "test", "value": 42, "items": ["a", "b", "c"]}


class TestWithFixture:
    """Tests using the sample_data fixture."""

    def test_uses_fixture(self, sample_data):
        """Example using custom fixture."""
        assert sample_data["name"] == "test"
        assert sample_data["value"] == 42
        assert len(sample_data["items"]) == 3
