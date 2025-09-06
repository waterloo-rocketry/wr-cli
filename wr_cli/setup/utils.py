"""Utilities for setup steps."""

import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def run_command(
    command: List[str],
    capture_output: bool = True,
    check: bool = True,
    cwd: Optional[Path] = None,
    interactive: bool = False,
) -> Tuple[bool, str, str]:
    """Run a command and return the result.

    Args:
        command: Command to run as a list of strings
        capture_output: Whether to capture stdout/stderr (ignored if interactive=True)
        check: Whether to raise on non-zero exit code
        cwd: Working directory for the command
        interactive: Whether to run in interactive mode (streams output, allows input)

    Returns:
        Tuple of (success, stdout, stderr)
    """
    try:
        if interactive:
            # Interactive mode: stream output and allow input
            process = subprocess.Popen(
                command,
                cwd=cwd,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            
            # Wait for process to complete
            return_code = process.wait()
            
            if check and return_code != 0:
                raise subprocess.CalledProcessError(return_code, command)
                
            return return_code == 0, "", ""
        else:
            # Non-interactive mode: capture output
            result = subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                check=check,
                cwd=cwd,
            )
            return True, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        return (
            False,
            e.stdout.strip() if e.stdout else "",
            e.stderr.strip() if e.stderr else "",
        )
    except FileNotFoundError:
        return False, "", f"Command not found: {command[0]}"


def run_command_interactive(
    command: List[str],
    cwd: Optional[Path] = None,
    show_command: bool = True,
) -> Tuple[bool, str, str]:
    """Run a command interactively, streaming output and allowing input.
    
    Args:
        command: Command to run as a list of strings
        cwd: Working directory for the command
        show_command: Whether to show the command being executed
        
    Returns:
        Tuple of (success, stdout, stderr)
    """
    cmd_str = " ".join(command)
    
    if show_command:
        print(f"$ {cmd_str}")
    
    try:
        # Use shell=True for simplicity and full interactivity
        result = subprocess.run(
            cmd_str,
            shell=True,
            cwd=cwd,
            text=True,
        )
        
        return result.returncode == 0, "", ""
        
    except Exception as e:
        return False, "", f"Error running command: {e}"


def command_exists(command: str) -> bool:
    """Check if a command exists on the system.

    Args:
        command: Command name to check

    Returns:
        True if command exists, False otherwise
    """
    return shutil.which(command) is not None


def get_python_executable() -> Optional[str]:
    """Get the path to the Python executable.

    Returns:
        Path to Python executable, or None if not found
    """
    # Try different Python command variations
    for cmd in ["python3.11", "python3", "python"]:
        if command_exists(cmd):
            # Verify it's actually Python 3.11+
            success, stdout, _ = run_command([cmd, "--version"])
            if success and "Python 3.1" in stdout:
                return cmd
    return None


def get_node_version() -> Optional[str]:
    """Get the installed Node.js version.

    Returns:
        Node.js version string, or None if not installed
    """
    if not command_exists("node"):
        return None

    success, stdout, _ = run_command(["node", "--version"])
    return stdout if success else None


def get_system_info() -> Dict[str, str]:
    """Get system information.

    Returns:
        Dictionary with system information
    """
    return {
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
    }


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure exists
    """
    path.mkdir(parents=True, exist_ok=True)
