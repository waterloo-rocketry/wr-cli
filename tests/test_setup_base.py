# pyright: basic
"""Tests for setup base classes."""

from unittest.mock import MagicMock

import pytest
from rich.console import Console

from wr_cli.setup import SetupStep


class MockSetupStep(SetupStep):
    """Mock setup step for testing."""

    def __init__(self, console: Console, verbose: bool = False, name: str = "Mock Step", description: str = "Mock description", should_succeed: bool = True):
        super().__init__(console, verbose)
        self._name = name
        self._description = description
        self._should_succeed = should_succeed
        self.execute_called = False
        self.is_completed_result = False

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def is_completed(self) -> bool:
        return self.is_completed_result

    def execute(self) -> bool:
        self.execute_called = True
        if not self._should_succeed:
            raise RuntimeError("Mock execution failed")
        return self._should_succeed


class TestSetupStep:
    """Test the SetupStep base class."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console)
        
        assert step.console is console
        assert step.verbose is False

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, verbose=True)
        
        assert step.console is console
        assert step.verbose is True

    def test_properties(self):
        """Test step properties."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, name="Test Step", description="Test description")
        
        assert step.name == "Test Step"
        assert step.description == "Test description"

    def test_run_successful_execution(self):
        """Test run method with successful execution."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, should_succeed=True)
        
        result = step.run()
        
        assert result is True
        assert step.execute_called is True
        
        # Verify console output
        expected_calls = [
            (("[blue]→ Mock Step[/blue] - Mock description",), {}),
            (("[green]✓ Mock Step[/green] completed",), {})
        ]
        assert console.print.call_count == 2
        for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
            actual_call = console.print.call_args_list[i]
            assert actual_call.args == expected_args

    def test_run_failed_execution(self):
        """Test run method with failed execution."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, should_succeed=False)
        
        result = step.run()
        
        assert result is False
        assert step.execute_called is True
        
        # Verify console output
        expected_calls = [
            (("[blue]→ Mock Step[/blue] - Mock description",), {}),
            (("[red]✗ Mock Step[/red] failed",), {})
        ]
        assert console.print.call_count == 2

    def test_run_already_completed_no_force(self):
        """Test run method when step is already completed and force=False."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, should_succeed=True)
        step.is_completed_result = True
        
        result = step.run(force=False)
        
        assert result is True
        assert step.execute_called is False
        
        # Should show already completed message
        console.print.assert_called_once_with("[green]✓ Mock Step[/green] (already completed)")

    def test_run_already_completed_with_force(self):
        """Test run method when step is already completed but force=True."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, should_succeed=True)
        step.is_completed_result = True
        
        result = step.run(force=True)
        
        assert result is True
        assert step.execute_called is True
        
        # Should execute normally, not show already completed message
        expected_calls = [
            (("[blue]→ Mock Step[/blue] - Mock description",), {}),
            (("[green]✓ Mock Step[/green] completed",), {})
        ]
        assert console.print.call_count == 2

    def test_run_with_exception_no_verbose(self):
        """Test run method when execute raises exception without verbose mode."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, verbose=False, should_succeed=False)
        
        result = step.run()
        
        assert result is False
        
        # Should show error message but not traceback
        expected_calls = [
            (("[blue]→ Mock Step[/blue] - Mock description",), {}),
            (("[red]✗ Mock Step[/red] failed: Mock execution failed",), {})
        ]
        assert console.print.call_count == 2
        for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
            actual_call = console.print.call_args_list[i]
            assert actual_call.args == expected_args

    def test_run_with_exception_verbose(self):
        """Test run method when execute raises exception with verbose mode."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console, verbose=True, should_succeed=False)
        
        result = step.run()
        
        assert result is False
        
        # Should show error message and traceback
        assert console.print.call_count == 3  # step start, error message, traceback
        console.print.assert_any_call("[blue]→ Mock Step[/blue] - Mock description")
        console.print.assert_any_call("[red]✗ Mock Step[/red] failed: Mock execution failed")
        
        # Last call should be traceback (starts with [red] and contains traceback info)
        last_call = console.print.call_args_list[-1]
        traceback_text = last_call.args[0]
        assert traceback_text.startswith("[red]")
        assert "RuntimeError" in traceback_text

    def test_is_completed_default_implementation(self):
        """Test that default is_completed implementation returns False."""
        console = MagicMock(spec=Console)
        step = MockSetupStep(console)
        
        # Using the base implementation
        assert step.is_completed() == step.is_completed_result  # False by default
