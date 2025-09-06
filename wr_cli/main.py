"""Main CLI entry point for the WR CLI."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel

from .commands import run_command
from .config import load_config
from .setup.runner import SetupRunner

console = Console()


@click.group()
@click.version_option()
def cli() -> None:
    """WR CLI - Bootstrap Waterloo Rocketry development environments."""
    pass


@cli.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force re-run setup steps even if already completed",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--config", "-c", help="Path to wr.yml config file", default="wr.yml")
def setup(force: bool, verbose: bool, config: str) -> None:
    """Set up the development environment."""
    config_path = Path(config)

    if not config_path.exists():
        console.print(f"[red]Error: Config file '{config_path}' not found.[/red]")
        sys.exit(1)

    try:
        config_data = load_config(config_path)
        project_name = config_data.get("project_name", "unknown-project")
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)

    console.print(
        Panel.fit(
            f"[bold blue]WR CLI Setup[/bold blue]\n"
            f"Setting up {project_name} development environment...",
            border_style="blue",
        )
    )

    runner = SetupRunner(
        console=console, verbose=verbose, force=force, project_name=project_name
    )

    try:
        success = runner.run_setup()
        if success:
            console.print(
                Panel.fit(
                    "[bold green]✓ Setup completed successfully![/bold green]",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel.fit(
                    "[bold red]✗ Setup failed![/bold red]\n"
                    "Check the output above for details.",
                    border_style="red",
                )
            )
            sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Setup interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("command_name")
@click.option("--config", "-c", help="Path to wr.yml config file")
def run(command_name: str, config: Optional[str]) -> None:
    """Run a command defined in wr.yml."""
    config_path = Path(config) if config else Path("wr.yml")

    if not config_path.exists():
        console.print(f"[red]Error: Config file '{config_path}' not found.[/red]")
        sys.exit(1)

    try:
        config_data = load_config(config_path)
        run_command(command_name, config_data, console)
    except Exception as e:
        console.print(f"[red]Error running command: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    cli()
