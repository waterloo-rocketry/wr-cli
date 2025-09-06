"""Base classes for setup steps."""

from abc import ABC, abstractmethod
from rich.console import Console


class SetupStep(ABC):
    """Base class for all setup steps."""

    def __init__(self, console: Console, verbose: bool = False) -> None:
        """Initialize the setup step.

        Args:
            console: Rich console for output
            verbose: Enable verbose output
        """
        self.console = console
        self.verbose = verbose

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the setup step."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this step does."""
        pass

    def is_completed(self) -> bool:
        """Check if this setup step is already completed.

        Returns:
            True if the step is already completed, False otherwise
        """
        return False

    @abstractmethod
    def execute(self) -> bool:
        """Execute the setup step.

        Returns:
            True if successful, False otherwise
        """
        pass

    def run(self, force: bool = False) -> bool:
        """Run the setup step with status checking.

        Args:
            force: Force re-run even if already completed

        Returns:
            True if successful, False otherwise
        """
        if not force and self.is_completed():
            self.console.print(f"[green]✓ {self.name}[/green] (already completed)")
            return True

        self.console.print(f"[blue]→ {self.name}[/blue] - {self.description}")

        try:
            success = self.execute()
            if success:
                self.console.print(f"[green]✓ {self.name}[/green] completed")
            else:
                self.console.print(f"[red]✗ {self.name}[/red] failed")
            return success
        except Exception as e:
            self.console.print(f"[red]✗ {self.name}[/red] failed: {e}")
            if self.verbose:
                import traceback

                self.console.print(f"[red]{traceback.format_exc()}[/red]")
            return False
