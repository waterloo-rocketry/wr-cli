"""Setup steps for development environment."""

import getpass
import platform
from pathlib import Path
from typing import Any, List, Optional

from ..setup import SetupStep
from .utils import (
    command_exists,
    get_node_version,
    get_python_executable,
    run_command,
    run_command_interactive,
)


class CheckNodeJSStep(SetupStep):
    """Ensure Node.js is installed."""

    @property
    def name(self) -> str:
        return "Check Node.js"

    @property
    def description(self) -> str:
        return "Verify Node.js is installed"

    def is_completed(self) -> bool:
        return command_exists("node")

    def execute(self) -> bool:
        if self.is_completed():
            version = get_node_version()
            if self.verbose:
                self.console.print(f"  Found Node.js {version}")
            return True

        system = platform.system().lower()
        if system == "darwin":
            self.console.print(
                "[yellow]Node.js not found. Install with: brew install node[/yellow]"
            )
        elif system == "linux":
            self.console.print(
                "[yellow]Node.js not found. Install with: sudo apt-get install nodejs npm[/yellow]"
            )
        elif system == "windows":
            self.console.print(
                "[yellow]Node.js not found. Download from https://nodejs.org/[/yellow]"
            )
        else:
            self.console.print(
                "[yellow]Node.js not found. Please install Node.js from https://nodejs.org/[/yellow]"
            )
        return False


class CheckPythonStep(SetupStep):
    """Ensure Python 3.11+ is installed."""

    @property
    def name(self) -> str:
        return "Check Python"

    @property
    def description(self) -> str:
        return "Verify Python 3.11+ is installed"

    def is_completed(self) -> bool:
        return get_python_executable() is not None

    def execute(self) -> bool:
        python_cmd = get_python_executable()
        if python_cmd:
            success, version_output, _ = run_command([python_cmd, "--version"])
            if success and self.verbose:
                self.console.print(f"  Found {version_output}")
            return True

        system = platform.system().lower()
        if system == "darwin":
            self.console.print(
                "[yellow]Python 3.11+ not found. Install with: brew install python@3.11[/yellow]"
            )
        elif system == "linux":
            self.console.print(
                "[yellow]Python 3.11+ not found. Install with: sudo apt-get install python3.11[/yellow]"
            )
        elif system == "windows":
            self.console.print(
                "[yellow]Python 3.11+ not found. Download from https://python.org/[/yellow]"
            )
        else:
            self.console.print(
                "[yellow]Python 3.11+ not found. Please install Python 3.11+[/yellow]"
            )
        return False


class InstallUvStep(SetupStep):
    """Install the uv package manager."""

    @property
    def name(self) -> str:
        return "Install uv"

    @property
    def description(self) -> str:
        return "Install uv package manager"

    def is_completed(self) -> bool:
        return command_exists("uv")

    def execute(self) -> bool:
        if self.is_completed():
            return True

        system = platform.system().lower()

        try:
            if system == "windows":
                # Use interactive execution for PowerShell script
                success, _, stderr = run_command_interactive([
                    "powershell",
                    "-c",
                    "irm https://astral.sh/uv/install.ps1 | iex",
                ])
            else:
                # Use interactive execution for shell script
                success, _, stderr = run_command_interactive([
                    "sh", "-c",
                    "curl -LsSf https://astral.sh/uv/install.sh | sh"
                ])

            if not success:
                self.console.print(f"[red]Failed to install uv[/red]")
                if stderr and self.verbose:
                    self.console.print(f"  Error: {stderr}")
                return False

            return command_exists("uv")

        except Exception as e:
            self.console.print(f"[red]Failed to install uv: {e}[/red]")
            return False


class InstallGhstackStep(SetupStep):
    """Install ghstack using uv tool."""

    @property
    def name(self) -> str:
        return "Install ghstack"

    @property
    def description(self) -> str:
        return "Install ghstack for GitHub workflow"

    def is_completed(self) -> bool:
        return command_exists("ghstack")

    def execute(self) -> bool:
        if self.is_completed():
            return True

        if not command_exists("uv"):
            self.console.print("[red]uv not installed, cannot install ghstack[/red]")
            return False

        success, _, stderr = run_command_interactive(["uv", "tool", "install", "ghstack"])
        if success:
            return True

        self.console.print(f"[red]Failed to install ghstack: {stderr}[/red]")
        return False


class SetupGhstackStep(SetupStep):
    """Set up ghstack configuration with GitHub token."""

    @property
    def name(self) -> str:
        return "Setup ghstack"

    @property
    def description(self) -> str:
        return "Configure ghstack with GitHub authentication"

    def is_completed(self) -> bool:
        ghstack_config = Path.home() / ".ghstackrc"
        return ghstack_config.exists()

    def execute(self) -> bool:
        if not command_exists("ghstack"):
            self.console.print("[red]ghstack not installed[/red]")
            return False

        ghstack_config = Path.home() / ".ghstackrc"
        _ = run_command_interactive(["ghstack"])

        if ghstack_config.exists():
            return True
        self.console.print(
            "[yellow]GitHub Personal Access Token required for ghstack[/yellow]"
        )
        self.console.print(
            "[yellow]Please create a token at: https://github.com/settings/tokens[/yellow]"
        )
        self.console.print("[yellow]Required permissions: repo (full control)[/yellow]")

        token = getpass.getpass("Enter your GitHub Personal Access Token: ").strip()
        if not token:
            self.console.print("[red]No token provided, skipping ghstack setup[/red]")
            return False

        username = input("Enter your GitHub username: ").strip()
        if not username:
            self.console.print(
                "[red]No username provided, skipping ghstack setup[/red]"
            )
            return False

        config_content = f"""[ghstack]
github_url = github.com
github_oauth = {token}
github_username = {username}
"""

        try:
            ghstack_config.write_text(config_content)
            ghstack_config.chmod(0o600)  # Secure permissions
            if self.verbose:
                self.console.print(f"  Created {ghstack_config}")
            return True
        except Exception as e:
            self.console.print(f"[red]Failed to create .ghstackrc: {e}[/red]")
            return False


class LockPythonVersionStep(SetupStep):
    """Lock Python version using uv based on .python-version file."""

    @property
    def name(self) -> str:
        return "Lock Python version"

    @property
    def description(self) -> str:
        return "Install and pin Python version from .python-version file"

    def _get_target_python_version(self) -> str:
        """Get the target Python version from .python-version file."""
        python_version_file = Path(".python-version")
        if python_version_file.exists():
            return python_version_file.read_text().strip()
        return "3.11"  # Default fallback

    def _get_current_python_version(self) -> str:
        """Get the currently active Python version via uv."""
        success, stdout, _ = run_command(["uv", "python", "--version"])
        if success and stdout:
            # Extract version from output like "Python 3.11.13"
            parts = stdout.strip().split()
            if len(parts) >= 2 and parts[1]:
                return parts[1]
        return ""

    def is_completed(self) -> bool:
        target_version = self._get_target_python_version()
        current_version = self._get_current_python_version()
        
        if not current_version:
            return False
            
        # Check if current version matches target (allows patch version differences)
        if "." in target_version:
            # If target specifies exact version (e.g., "3.11.13"), match exactly
            return current_version == target_version
        else:
            # If target specifies minor version (e.g., "3.11"), match minor version
            return current_version.startswith(f"{target_version}.")

    def execute(self) -> bool:
        if not command_exists("uv"):
            self.console.print("[red]uv not installed[/red]")
            return False

        target_version = self._get_target_python_version()
        
        # Install the target Python version via uv if not available
        success, _, stderr = run_command_interactive(["uv", "python", "install", target_version], show_command=False)
        if not success and "already installed" not in stderr.lower():
            self.console.print(f"[red]Failed to install Python {target_version}: {stderr}[/red]")
            return False

        # Pin the project to use the target version
        success, _, stderr = run_command_interactive(["uv", "python", "pin", target_version], show_command=False)
        if success:
            if self.verbose:
                self.console.print(f"  Pinned Python version to {target_version}")
            return True

        self.console.print(f"[red]Failed to pin Python version: {stderr}[/red]")
        return False


class InstallRequirementsStep(SetupStep):
    """Install dependencies from requirements.txt using uv sync."""

    @property
    def name(self) -> str:
        return "Sync dependencies"

    @property
    def description(self) -> str:
        return "Install and sync project dependencies"

    def is_completed(self) -> bool:
        uv_lock = Path("uv.lock")
        pyproject = Path("pyproject.toml")

        if not uv_lock.exists() or not pyproject.exists():
            return False

        return uv_lock.stat().st_mtime >= pyproject.stat().st_mtime

    def execute(self) -> bool:
        if not command_exists("uv"):
            self.console.print("[red]uv not installed[/red]")
            return False

        success, _, stderr = run_command_interactive(["uv", "sync"], show_command=False)
        if success:
            return True

        self.console.print(f"[red]Failed to sync dependencies: {stderr}[/red]")
        return False


class InstallLocalPackagesStep(SetupStep):
    """Install omnibus and parsley libraries from local directories."""

    def __init__(
        self, console: Any, verbose: bool, packages: Optional[List[str]] = None
    ) -> None:
        super().__init__(console, verbose)
        self.packages = packages or ["omnibus", "parsley"]

    @property
    def name(self) -> str:
        return "Install local packages"

    @property
    def description(self) -> str:
        return f"Install {', '.join(self.packages)} from local directories"

    def is_completed(self) -> bool:
        return False

    def execute(self) -> bool:
        if not command_exists("uv"):
            self.console.print("[red]uv not installed[/red]")
            return False

        success_count = 0
        for package in self.packages:
            package_dir = Path(package).resolve()  # Use absolute path
            if not package_dir.exists():
                if self.verbose:
                    self.console.print(f"  {package}/ directory not found, skipping")
                continue

            # Check if it has a pyproject.toml to confirm it's a valid Python package
            if not (package_dir / "pyproject.toml").exists():
                if self.verbose:
                    self.console.print(f"  {package}/ has no pyproject.toml, skipping")
                continue

            success, _, stderr = run_command_interactive([
                "uv", "add", "--editable", f"./{package}"
            ], show_command=False)

            if success:
                success_count += 1
                if self.verbose:
                    self.console.print(f"  Added {package} as editable dependency")
            else:
                self.console.print(f"[red]Failed to add {package}: {stderr}[/red]")
                if self.verbose and stderr:
                    self.console.print(f"  Error details: {stderr}")

        return success_count > 0 or all(not Path(pkg).exists() for pkg in self.packages)
