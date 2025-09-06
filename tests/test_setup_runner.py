# pyright: basic
"""Tests for setup runner."""

from unittest.mock import MagicMock

import pytest
from rich.console import Console

from wr_cli.setup.runner import SetupRunner


class TestSetupRunner:
    """Test the SetupRunner class."""

    def test_init_default_parameters(self):
        """Test initialization with default parameters."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console)
        
        assert runner.console is console
        assert runner.verbose is False
        assert runner.force is False
        assert runner.project_name == "unknown"

    def test_init_custom_parameters(self):
        """Test initialization with custom parameters."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, verbose=True, force=True, project_name="test-project")
        
        assert runner.console is console
        assert runner.verbose is True
        assert runner.force is True
        assert runner.project_name == "test-project"

    def test_get_default_steps(self):
        """Test that default project gets default steps."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="unknown")
        
        # Should have 4 default steps
        assert len(runner.steps) == 4
        step_names = [step.name for step in runner.steps]
        expected_steps = [
            "Check Node.js",
            "Check Python",
            "Install uv",
            "Lock Python version"
        ]
        assert step_names == expected_steps

    def test_get_wr_cli_steps(self):
        """Test that wr-cli project gets wr-cli specific steps."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="wr-cli")
        
        # Should have 6 wr-cli steps
        assert len(runner.steps) == 6
        step_names = [step.name for step in runner.steps]
        expected_steps = [
            "Check Node.js",
            "Check Python",
            "Install uv",
            "Install ghstack",
            "Setup ghstack",
            "Lock Python version"
        ]
        assert step_names == expected_steps

    def test_get_omnibus_steps(self):
        """Test that omnibus project gets omnibus specific steps."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="omnibus")
        
        # Should have 6 omnibus steps
        assert len(runner.steps) == 6
        step_names = [step.name for step in runner.steps]
        expected_steps = [
            "Check Node.js",
            "Check Python",
            "Install uv",
            "Lock Python version",
            "Sync dependencies",  # This is the actual name
            "Install local packages"
        ]
        assert step_names == expected_steps

    def test_run_setup_all_steps_succeed(self):
        """Test run_setup when all steps succeed."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="unknown")
        
        # Mock all steps to succeed
        for step in runner.steps:
            step.run = MagicMock(return_value=True)
        
        result = runner.run_setup()
        
        assert result is True
        
        # Verify all steps were called with force=False (default)
        for step in runner.steps:
            step.run.assert_called_once_with(force=False)
        
        # Verify console output
        console.print.assert_any_call("[blue]Running 4 setup steps...[/blue]\n")
        console.print.assert_any_call("\n[green]All setup steps completed successfully![/green]")

    def test_run_setup_with_force(self):
        """Test run_setup passes force flag to steps."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="unknown", force=True)
        
        # Mock all steps to succeed
        for step in runner.steps:
            step.run = MagicMock(return_value=True)
        
        result = runner.run_setup()
        
        assert result is True
        
        # Verify all steps were called with force=True
        for step in runner.steps:
            step.run.assert_called_once_with(force=True)

    def test_run_setup_one_step_fails(self):
        """Test run_setup when one step fails."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="unknown")
        
        # Mock first step to fail, others succeed
        runner.steps[0].run = MagicMock(return_value=False)
        for step in runner.steps[1:]:
            step.run = MagicMock(return_value=True)
        
        result = runner.run_setup()
        
        assert result is False
        
        # Verify all steps were still called
        for step in runner.steps:
            step.run.assert_called_once_with(force=False)
        
        # Verify failure message includes failed step name
        console.print.assert_any_call(f"\n[red]Failed steps: {runner.steps[0].name}[/red]")

    def test_run_setup_multiple_steps_fail(self):
        """Test run_setup when multiple steps fail."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="unknown")
        
        # Mock first and third steps to fail
        runner.steps[0].run = MagicMock(return_value=False)
        runner.steps[1].run = MagicMock(return_value=True)
        runner.steps[2].run = MagicMock(return_value=False)
        runner.steps[3].run = MagicMock(return_value=True)
        
        result = runner.run_setup()
        
        assert result is False
        
        # Verify failure message includes both failed step names
        failed_names = f"{runner.steps[0].name}, {runner.steps[2].name}"
        console.print.assert_any_call(f"\n[red]Failed steps: {failed_names}[/red]")

    def test_run_setup_step_counter_display(self):
        """Test that step counter is displayed correctly."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="unknown")
        
        # Mock all steps to succeed
        for step in runner.steps:
            step.run = MagicMock(return_value=True)
        
        runner.run_setup()
        
        # Check that step counters were printed
        expected_counters = ["[dim](1/4)[/dim]", "[dim](2/4)[/dim]", "[dim](3/4)[/dim]", "[dim](4/4)[/dim]"]
        for counter in expected_counters:
            console.print.assert_any_call(counter, end=" ")

    def test_verbose_flag_passed_to_steps(self):
        """Test that verbose flag is passed to all steps."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, verbose=True, project_name="unknown")
        
        # Verify all steps have verbose=True
        for step in runner.steps:
            assert step.verbose is True

    def test_console_passed_to_steps(self):
        """Test that console is passed to all steps."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="unknown")
        
        # Verify all steps have the same console
        for step in runner.steps:
            assert step.console is console

    def test_project_name_unknown_uses_default_steps(self):
        """Test that unknown project name uses default steps."""
        console = MagicMock(spec=Console)
        runner = SetupRunner(console, project_name="some-random-project")
        
        # Should fall back to default steps
        assert len(runner.steps) == 4
        step_names = [step.name for step in runner.steps]
        expected_steps = [
            "Check Node.js",
            "Check Python",
            "Install uv",
            "Lock Python version"
        ]
        assert step_names == expected_steps
