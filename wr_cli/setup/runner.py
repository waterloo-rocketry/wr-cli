"""Setup runner that orchestrates all setup steps."""

from typing import List

from rich.console import Console

from ..setup import SetupStep
from .steps import (
    CheckNodeJSStep,
    CheckPythonStep,
    InstallGhstackStep,
    InstallLocalPackagesStep,
    InstallRequirementsStep,
    InstallUvStep,
    LockPythonVersionStep,
    SetupGhstackStep,
)


class SetupRunner:
    """Orchestrates the execution of setup steps."""

    def __init__(
        self,
        console: Console,
        verbose: bool = False,
        force: bool = False,
        project_name: str = "unknown",
    ) -> None:
        """Initialize the setup runner.

        Args:
            console: Rich console for output
            verbose: Enable verbose output
            force: Force re-run of steps even if completed
            project_name: Name of the project being set up
        """
        self.console = console
        self.verbose = verbose
        self.force = force
        self.project_name = project_name

        # Define setup steps based on project
        if project_name == "omnibus":
            self.steps: List[SetupStep] = self._get_omnibus_steps()
        elif project_name == "wr-cli":
            self.steps: List[SetupStep] = self._get_wr_cli_steps()
        else:
            # Default setup steps for generic projects
            self.steps: List[SetupStep] = self._get_default_steps()

    def _get_default_steps(self) -> List[SetupStep]:
        """Get default setup steps for generic projects."""
        return [
            CheckNodeJSStep(self.console, self.verbose),
            CheckPythonStep(self.console, self.verbose),
            InstallUvStep(self.console, self.verbose),
            LockPythonVersionStep(self.console, self.verbose),
        ]

    def _get_wr_cli_steps(self) -> List[SetupStep]:
        """Get setup steps for the WR CLI project."""
        return [
            CheckNodeJSStep(self.console, self.verbose),
            CheckPythonStep(self.console, self.verbose),
            InstallUvStep(self.console, self.verbose),
            InstallGhstackStep(self.console, self.verbose),
            SetupGhstackStep(self.console, self.verbose),
            LockPythonVersionStep(self.console, self.verbose),
        ]

    def _get_omnibus_steps(self) -> List[SetupStep]:
        """Get setup steps for the Omnibus project."""
        return [
            CheckNodeJSStep(self.console, self.verbose),
            CheckPythonStep(self.console, self.verbose),
            InstallUvStep(self.console, self.verbose),
            LockPythonVersionStep(self.console, self.verbose),
            InstallRequirementsStep(self.console, self.verbose),
            InstallLocalPackagesStep(self.console, self.verbose),
        ]

    def run_setup(self) -> bool:
        """Run all setup steps.

        Returns:
            True if all steps completed successfully, False otherwise
        """
        self.console.print(f"[blue]Running {len(self.steps)} setup steps...[/blue]\n")

        failed_steps: list[str] = []

        for i, step in enumerate(self.steps, 1):
            self.console.print(f"[dim]({i}/{len(self.steps)})[/dim]", end=" ")

            success = step.run(force=self.force)
            if not success:
                failed_steps.append(step.name)

        if failed_steps:
            self.console.print(f"\n[red]Failed steps: {', '.join(failed_steps)}[/red]")
            return False

        self.console.print("\n[green]All setup steps completed successfully![/green]")
        return True
