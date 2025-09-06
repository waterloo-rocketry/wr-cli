# pyright: basic
"""Tests for the WR CLI."""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from wr_cli.main import cli


def test_cli_help():
    """Test that the CLI shows help message."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "WR CLI" in result.output


def test_setup_command_exists():
    """Test that the setup command exists."""
    runner = CliRunner()
    result = runner.invoke(cli, ["setup", "--help"])
    assert result.exit_code == 0
    assert "Set up the development environment" in result.output


def test_run_command_exists():
    """Test that the run command exists."""
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--help"])
    assert result.exit_code == 0
    assert "Run a command defined in wr.yml" in result.output


def test_setup_command_config_not_found():
    """Test setup command when config file is not found."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "nonexistent.yml"
        result = runner.invoke(cli, ["setup", "--config", str(config_path)])
        assert result.exit_code == 1
        assert "Config file" in result.output and "not found" in result.output


def test_setup_command_invalid_config():
    """Test setup command with invalid YAML config."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["setup", "--config", config_path])
        assert result.exit_code == 1
        assert "Error loading config" in result.output
    finally:
        Path(config_path).unlink()


@patch("wr_cli.main.SetupRunner")
def test_setup_command_success(mock_setup_runner):
    """Test successful setup command execution."""
    # Mock the setup runner
    mock_runner_instance = MagicMock()
    mock_runner_instance.run_setup.return_value = True
    mock_setup_runner.return_value = mock_runner_instance
    
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("""
project_name: test-project
commands:
  test: echo "hello"
""")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["setup", "--config", config_path, "--verbose", "--force"])
        assert result.exit_code == 0
        assert "Setup completed successfully" in result.output
        
        # Verify SetupRunner was called with correct parameters
        mock_setup_runner.assert_called_once()
        call_args = mock_setup_runner.call_args
        assert call_args.kwargs["verbose"] is True
        assert call_args.kwargs["force"] is True
        assert call_args.kwargs["project_name"] == "test-project"
        
        mock_runner_instance.run_setup.assert_called_once()
    finally:
        Path(config_path).unlink()


@patch("wr_cli.main.SetupRunner")
def test_setup_command_failure(mock_setup_runner):
    """Test setup command when setup fails."""
    # Mock the setup runner to return failure
    mock_runner_instance = MagicMock()
    mock_runner_instance.run_setup.return_value = False
    mock_setup_runner.return_value = mock_runner_instance
    
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("""
project_name: test-project
commands:
  test: echo "hello"
""")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["setup", "--config", config_path])
        assert result.exit_code == 1
        assert "Setup failed" in result.output
    finally:
        Path(config_path).unlink()


@patch("wr_cli.main.SetupRunner")
def test_setup_command_keyboard_interrupt(mock_setup_runner):
    """Test setup command interrupted by user."""
    # Mock the setup runner to raise KeyboardInterrupt
    mock_runner_instance = MagicMock()
    mock_runner_instance.run_setup.side_effect = KeyboardInterrupt()
    mock_setup_runner.return_value = mock_runner_instance
    
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("""
project_name: test-project
commands:
  test: echo "hello"
""")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["setup", "--config", config_path])
        assert result.exit_code == 1
        assert "Setup interrupted by user" in result.output
    finally:
        Path(config_path).unlink()


@patch("wr_cli.main.SetupRunner")
def test_setup_command_unexpected_error(mock_setup_runner):
    """Test setup command with unexpected error."""
    # Mock the setup runner to raise an unexpected exception
    mock_runner_instance = MagicMock()
    mock_runner_instance.run_setup.side_effect = RuntimeError("Unexpected error")
    mock_setup_runner.return_value = mock_runner_instance
    
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("""
project_name: test-project
commands:
  test: echo "hello"
""")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["setup", "--config", config_path])
        assert result.exit_code == 1
        assert "Unexpected error: Unexpected error" in result.output
    finally:
        Path(config_path).unlink()


def test_setup_command_default_project_name():
    """Test setup command uses default project name when not specified."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("""
commands:
  test: echo "hello"
""")
        config_path = f.name
    
    try:
        with patch("wr_cli.main.SetupRunner") as mock_setup_runner:
            mock_runner_instance = MagicMock()
            mock_runner_instance.run_setup.return_value = True
            mock_setup_runner.return_value = mock_runner_instance
            
            result = runner.invoke(cli, ["setup", "--config", config_path])
            assert result.exit_code == 0
            
            # Verify default project name was used
            call_args = mock_setup_runner.call_args
            assert call_args.kwargs["project_name"] == "unknown-project"
    finally:
        Path(config_path).unlink()


@patch("wr_cli.main.run_command")
def test_run_command_success(mock_run_command):
    """Test successful run command execution."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("""
commands:
  test: echo "hello"
""")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["run", "test", "--config", config_path])
        assert result.exit_code == 0
        
        # Verify run_command was called with correct parameters
        mock_run_command.assert_called_once()
        call_args = mock_run_command.call_args
        assert call_args.args[0] == "test"  # command_name
        assert "commands" in call_args.args[1]  # config dict
        assert call_args.args[1]["commands"]["test"] == "echo \"hello\""
    finally:
        Path(config_path).unlink()


def test_run_command_config_not_found():
    """Test run command when config file is not found."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        config_path = Path(temp_dir) / "nonexistent.yml"
        result = runner.invoke(cli, ["run", "test", "--config", str(config_path)])
        assert result.exit_code == 1
        assert "Config file" in result.output and "not found" in result.output


def test_run_command_invalid_config():
    """Test run command with invalid YAML config."""
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["run", "test", "--config", config_path])
        assert result.exit_code == 1
        assert "Error running command" in result.output  # This is the actual error message format
    finally:
        Path(config_path).unlink()


def test_run_command_default_config():
    """Test run command uses default wr.yml when no config specified."""
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory and test default config behavior
        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(temp_dir)
            result = runner.invoke(cli, ["run", "test"])
            assert result.exit_code == 1
            assert "Config file" in result.output and "not found" in result.output
        finally:
            os.chdir(original_cwd)


@patch("wr_cli.main.run_command")
def test_run_command_execution_error(mock_run_command):
    """Test run command when execution raises an error."""
    # Mock run_command to raise an exception
    mock_run_command.side_effect = ValueError("Command not found")
    
    runner = CliRunner()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("""
commands:
  test: echo "hello"
""")
        config_path = f.name
    
    try:
        result = runner.invoke(cli, ["run", "test", "--config", config_path])
        assert result.exit_code == 1
        assert "Error running command: Command not found" in result.output
    finally:
        Path(config_path).unlink()
