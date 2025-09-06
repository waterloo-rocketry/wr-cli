# pyright: basic
"""Tests for command execution functionality."""

import subprocess
import sys
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from wr_cli.commands import run_command


class TestRunCommand:
    """Test the run_command function."""

    def test_run_command_success(self):
        """Test successful command execution."""
        config = {
            "commands": {
                "test": "echo 'Hello World'"
            }
        }
        console = MagicMock(spec=Console)
        
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "Hello World\n"
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            run_command("test", config, console)
            
            # Verify subprocess.run was called correctly
            mock_run.assert_called_once_with(
                "echo 'Hello World'",
                shell=True,
                check=True,
                text=True,
                capture_output=True,
            )
            
            # Verify console output
            expected_calls = [
                (("[blue]Running:[/blue] echo 'Hello World'",), {}),
                (("Hello World\n",), {}),
                (("[green]✓ Command 'test' completed successfully[/green]",), {})
            ]
            assert console.print.call_count == 3
            for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
                actual_call = console.print.call_args_list[i]
                assert actual_call.args == expected_args
                assert actual_call.kwargs == expected_kwargs

    def test_run_command_success_no_stdout(self):
        """Test successful command execution with no stdout."""
        config = {
            "commands": {
                "silent": "exit 0"
            }
        }
        console = MagicMock(spec=Console)
        
        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            run_command("silent", config, console)
            
            # Verify console output (should not print empty stdout)
            expected_calls = [
                (("[blue]Running:[/blue] exit 0",), {}),
                (("[green]✓ Command 'silent' completed successfully[/green]",), {})
            ]
            assert console.print.call_count == 2
            for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
                actual_call = console.print.call_args_list[i]
                assert actual_call.args == expected_args

    def test_run_command_not_found(self):
        """Test error when command is not found in config."""
        config = {
            "commands": {
                "test": "echo 'Hello World'",
                "build": "make build"
            }
        }
        console = MagicMock(spec=Console)
        
        with pytest.raises(ValueError, match="Command 'missing' not found. Available commands: test, build"):
            run_command("missing", config, console)

    def test_run_command_no_commands_section(self):
        """Test error when config has no commands section."""
        config = {}
        console = MagicMock(spec=Console)
        
        with pytest.raises(ValueError, match="Command 'test' not found. Available commands:"):
            run_command("test", config, console)

    def test_run_command_empty_commands_section(self):
        """Test error when commands section is empty."""
        config = {"commands": {}}
        console = MagicMock(spec=Console)
        
        with pytest.raises(ValueError, match="Command 'test' not found. Available commands:"):
            run_command("test", config, console)

    @patch("sys.exit")
    def test_run_command_failure_with_stdout_stderr(self, mock_exit):
        """Test command failure with both stdout and stderr."""
        config = {
            "commands": {
                "fail": "ls /nonexistent"
            }
        }
        console = MagicMock(spec=Console)
        
        with patch("subprocess.run") as mock_run:
            error = subprocess.CalledProcessError(2, "ls /nonexistent")
            error.stdout = "some output\n"
            error.stderr = "ls: /nonexistent: No such file or directory\n"
            mock_run.side_effect = error
            
            run_command("fail", config, console)
            
            # Verify console output for failure
            expected_calls = [
                (("[blue]Running:[/blue] ls /nonexistent",), {}),
                (("[red]✗ Command 'fail' failed with exit code 2[/red]",), {}),
                (("[yellow]stdout:[/yellow]",), {}),
                (("some output\n",), {}),
                (("[red]stderr:[/red]",), {}),
                (("ls: /nonexistent: No such file or directory\n",), {})
            ]
            assert console.print.call_count == 6
            for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
                actual_call = console.print.call_args_list[i]
                assert actual_call.args == expected_args
            
            # Verify sys.exit was called with correct code
            mock_exit.assert_called_once_with(2)

    @patch("sys.exit")
    def test_run_command_failure_no_output(self, mock_exit):
        """Test command failure with no stdout or stderr."""
        config = {
            "commands": {
                "fail": "exit 1"
            }
        }
        console = MagicMock(spec=Console)
        
        with patch("subprocess.run") as mock_run:
            error = subprocess.CalledProcessError(1, "exit 1")
            error.stdout = ""
            error.stderr = ""
            mock_run.side_effect = error
            
            run_command("fail", config, console)
            
            # Verify console output for failure (should only show failure message)
            expected_calls = [
                (("[blue]Running:[/blue] exit 1",), {}),
                (("[red]✗ Command 'fail' failed with exit code 1[/red]",), {})
            ]
            assert console.print.call_count == 2
            for i, (expected_args, expected_kwargs) in enumerate(expected_calls):
                actual_call = console.print.call_args_list[i]
                assert actual_call.args == expected_args
            
            mock_exit.assert_called_once_with(1)

    @patch("sys.exit")
    def test_run_command_failure_only_stderr(self, mock_exit):
        """Test command failure with only stderr output."""
        config = {
            "commands": {
                "fail": "echo 'error' >&2 && exit 1"
            }
        }
        console = MagicMock(spec=Console)
        
        with patch("subprocess.run") as mock_run:
            error = subprocess.CalledProcessError(1, "echo 'error' >&2 && exit 1")
            error.stdout = ""
            error.stderr = "error\n"
            mock_run.side_effect = error
            
            run_command("fail", config, console)
            
            # Verify console output shows only stderr
            expected_calls = [
                (("[blue]Running:[/blue] echo 'error' >&2 && exit 1",), {}),
                (("[red]✗ Command 'fail' failed with exit code 1[/red]",), {}),
                (("[red]stderr:[/red]",), {}),
                (("error\n",), {})
            ]
            assert console.print.call_count == 4
            
            mock_exit.assert_called_once_with(1)
