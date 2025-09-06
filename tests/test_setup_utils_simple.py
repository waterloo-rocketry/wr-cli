# pyright: basic
"""Tests for setup utilities - simplified version."""

from wr_cli.setup.utils import command_exists, get_system_info, run_command


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
