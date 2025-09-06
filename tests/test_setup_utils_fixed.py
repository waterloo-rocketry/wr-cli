"""Fixed tests for setup utilities based on actual implementation."""

import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

from wr_cli.setup.utils import (
    command_exists,
    get_node_version,
    get_python_executable,
    get_system_info,
    run_command,
    run_command_interactive,
    ensure_directory,
)


def test_command_exists():
    """Test command_exists function."""
    # Test with a command that should exist on most systems
    assert command_exists("echo") == True

    # Test with a command that definitely doesn't exist
    assert command_exists("nonexistent_command_12345") == False


def test_run_command():
    """Test run_command function."""
    success, stdout, stderr = run_command(["echo", "hello"])
    assert success == True
    assert stdout == "hello"
    assert stderr == ""

    # Test command that doesn't exist
    success, stdout, stderr = run_command(["nonexistent_command_12345"])
    assert success == False


def test_get_system_info():
    """Test get_system_info function."""
    info = get_system_info()
    assert isinstance(info, dict)
    assert "platform" in info
    assert "architecture" in info
    assert "python_version" in info


@patch("subprocess.run")
def test_run_command_success_with_output(mock_run):
    """Test run_command with successful execution and output."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "test output"
    mock_result.stderr = ""
    mock_run.return_value = mock_result
    
    success, stdout, stderr = run_command(["test", "command"])
    
    assert success is True
    assert stdout == "test output"
    assert stderr == ""
    mock_run.assert_called_once_with(
        ["test", "command"],
        capture_output=True,
        text=True,
        check=True,
        cwd=None
    )


@patch("subprocess.run")
def test_run_command_failure_with_error(mock_run):
    """Test run_command with failed execution and error output."""
    # Simulate CalledProcessError
    error = subprocess.CalledProcessError(1, ["test", "command"])
    error.stdout = "partial output"
    error.stderr = "error message"
    mock_run.side_effect = error
    
    success, stdout, stderr = run_command(["test", "command"])
    
    assert success is False
    assert stdout == "partial output"
    assert stderr == "error message"


@patch("subprocess.run")
def test_run_command_file_not_found(mock_run):
    """Test run_command when command file is not found."""
    mock_run.side_effect = FileNotFoundError()
    
    success, stdout, stderr = run_command(["nonexistent", "command"])
    
    assert success is False
    assert stdout == ""
    assert stderr == "Command not found: nonexistent"


@patch("subprocess.run")
def test_run_command_interactive_mode(mock_run):
    """Test run_command in interactive mode."""
    with patch("subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        success, stdout, stderr = run_command(["test", "command"], interactive=True)
        
        assert success is True
        assert stdout == ""  # Interactive mode doesn't capture output
        assert stderr == ""
        
        mock_popen.assert_called_once_with(
            ["test", "command"],
            cwd=None,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )


@patch("subprocess.run")
def test_run_command_interactive_success(mock_run):
    """Test run_command_interactive with successful execution."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    success, stdout, stderr = run_command_interactive(["test", "command"])
    
    assert success is True
    assert stdout == ""  # run_command_interactive doesn't return output
    assert stderr == ""
    mock_run.assert_called_once_with(
        "test command",
        shell=True,
        cwd=None,
        text=True
    )


@patch("subprocess.run")
def test_run_command_interactive_failure(mock_run):
    """Test run_command_interactive with failed execution."""
    mock_result = MagicMock()
    mock_result.returncode = 1
    mock_run.return_value = mock_result
    
    success, stdout, stderr = run_command_interactive(["test", "command"])
    
    assert success is False
    assert stdout == ""
    assert stderr == ""


@patch("subprocess.run")
def test_run_command_interactive_exception(mock_run):
    """Test run_command_interactive when subprocess raises exception."""
    mock_run.side_effect = RuntimeError("Command failed")
    
    success, stdout, stderr = run_command_interactive(["test", "command"])
    
    assert success is False
    assert stdout == ""
    assert "Error running command: Command failed" in stderr


@patch("subprocess.run")
def test_run_command_interactive_no_show_command(mock_run):
    """Test run_command_interactive with show_command=False."""
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_run.return_value = mock_result
    
    success, stdout, stderr = run_command_interactive(["test", "command"], show_command=False)
    
    assert success is True
    # Command should still be executed even without showing it
    mock_run.assert_called_once()


@patch("wr_cli.setup.utils.command_exists")
@patch("wr_cli.setup.utils.run_command")
def test_get_node_version_success(mock_run_command, mock_command_exists):
    """Test get_node_version when node is available."""
    mock_command_exists.return_value = True
    mock_run_command.return_value = (True, "v18.17.0", "")
    
    version = get_node_version()
    assert version == "v18.17.0"
    mock_run_command.assert_called_once_with(["node", "--version"])


@patch("wr_cli.setup.utils.command_exists")
def test_get_node_version_not_installed(mock_command_exists):
    """Test get_node_version when node is not installed."""
    mock_command_exists.return_value = False
    
    version = get_node_version()
    assert version is None
    mock_command_exists.assert_called_once_with("node")


@patch("wr_cli.setup.utils.command_exists")
@patch("wr_cli.setup.utils.run_command")
def test_get_node_version_failure(mock_run_command, mock_command_exists):
    """Test get_node_version when node command fails."""
    mock_command_exists.return_value = True
    mock_run_command.return_value = (False, "", "command not found")
    
    version = get_node_version()
    assert version is None


@patch("wr_cli.setup.utils.command_exists")
@patch("wr_cli.setup.utils.run_command")
def test_get_python_executable_success(mock_run_command, mock_command_exists):
    """Test get_python_executable when Python 3.11+ is available."""
    mock_command_exists.side_effect = lambda cmd: cmd == "python3.11"
    mock_run_command.return_value = (True, "Python 3.11.5", "")
    
    executable = get_python_executable()
    assert executable == "python3.11"


@patch("wr_cli.setup.utils.command_exists")
@patch("wr_cli.setup.utils.run_command")
def test_get_python_executable_fallback_to_python3(mock_run_command, mock_command_exists):
    """Test get_python_executable falls back to python3 when specific version not found."""
    # python3.11 doesn't exist, python3 does and has correct version
    mock_command_exists.side_effect = lambda cmd: cmd == "python3"
    mock_run_command.return_value = (True, "Python 3.11.5", "")
    
    executable = get_python_executable()
    assert executable == "python3"


@patch("wr_cli.setup.utils.command_exists")
def test_get_python_executable_no_suitable_version(mock_command_exists):
    """Test get_python_executable when no suitable Python version is found."""
    mock_command_exists.return_value = False
    
    executable = get_python_executable()
    assert executable is None


def test_get_system_info_actual_values():
    """Test get_system_info returns actual system values."""
    info = get_system_info()
    
    # Verify the structure and that values match actual system info
    assert isinstance(info["platform"], str)
    assert isinstance(info["architecture"], str)
    assert isinstance(info["python_version"], str)
    
    # Verify values match what we expect from system calls
    assert info["platform"] == platform.system()
    assert info["architecture"] == platform.machine()
    assert info["python_version"] == platform.python_version()


@patch("shutil.which")  
def test_command_exists_with_which(mock_which):
    """Test command_exists using shutil.which."""
    mock_which.return_value = "/usr/bin/test-command"
    
    result = command_exists("test-command")
    
    assert result is True
    mock_which.assert_called_once_with("test-command")


@patch("shutil.which")
def test_command_exists_not_found(mock_which):
    """Test command_exists when command is not found."""
    mock_which.return_value = None
    
    result = command_exists("nonexistent-command")
    
    assert result is False
    mock_which.assert_called_once_with("nonexistent-command")


def test_ensure_directory(tmp_path):
    """Test ensure_directory creates directories."""
    test_dir = tmp_path / "test" / "nested" / "dir"
    
    ensure_directory(test_dir)
    
    assert test_dir.exists()
    assert test_dir.is_dir()


def test_ensure_directory_already_exists(tmp_path):
    """Test ensure_directory with existing directory."""
    test_dir = tmp_path / "existing"
    test_dir.mkdir()
    
    # Should not raise an error
    ensure_directory(test_dir)
    
    assert test_dir.exists()
    assert test_dir.is_dir()
