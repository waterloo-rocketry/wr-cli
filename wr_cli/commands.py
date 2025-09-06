"""Command execution functionality for WR CLI."""

import subprocess
import sys
from typing import Any, Dict

from rich.console import Console


def run_command(command_name: str, config: Dict[str, Any], console: Console) -> None:
    """Run a command defined in the configuration.

    Args:
        command_name: Name of the command to run
        config: Configuration dictionary loaded from wr.yml
        console: Rich console for output

    Raises:
        ValueError: If the command is not found in the configuration
        subprocess.CalledProcessError: If the command execution fails
    """
    commands = config.get("commands", {})

    if command_name not in commands:
        available_commands = ", ".join(commands.keys())
        raise ValueError(
            f"Command '{command_name}' not found. "
            f"Available commands: {available_commands}"
        )

    command = commands[command_name]
    console.print(f"[blue]Running:[/blue] {command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
        )

        if result.stdout:
            console.print(result.stdout)

        console.print(
            f"[green]✓ Command '{command_name}' completed successfully[/green]"
        )

    except subprocess.CalledProcessError as e:
        console.print(
            f"[red]✗ Command '{command_name}' failed with exit code {e.returncode}[/red]"
        )
        if e.stdout:
            console.print("[yellow]stdout:[/yellow]")
            console.print(e.stdout)
        if e.stderr:
            console.print("[red]stderr:[/red]")
            console.print(e.stderr)
        sys.exit(e.returncode)
