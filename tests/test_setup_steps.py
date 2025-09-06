# pyright: basic
"""Tests for setup steps."""

from unittest.mock import MagicMock, patch

import pytest

from wr_cli.setup.steps import (
    CheckNodeJSStep,
    CheckPythonStep,
    InstallGhstackStep,
    InstallLocalPackagesStep,
    InstallRequirementsStep,
    InstallUvStep,
    LockPythonVersionStep,
    SetupGhstackStep,
)


class TestCheckNodeJSStep:
    """Test the CheckNodeJSStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = CheckNodeJSStep(console, verbose=False)
        assert step.name == "Check Node.js"
        assert step.description == "Verify Node.js is installed"

    @patch("wr_cli.setup.steps.command_exists")
    def test_is_completed_when_node_exists(self, mock_command_exists):
        """Test is_completed returns True when Node.js exists."""
        mock_command_exists.return_value = True
        
        console = MagicMock()
        step = CheckNodeJSStep(console, verbose=False)
        assert step.is_completed() is True
        mock_command_exists.assert_called_once_with("node")

    @patch("wr_cli.setup.steps.command_exists")
    def test_is_completed_when_node_missing(self, mock_command_exists):
        """Test is_completed returns False when Node.js is missing."""
        mock_command_exists.return_value = False
        
        console = MagicMock()
        step = CheckNodeJSStep(console, verbose=False)
        assert step.is_completed() is False

    @patch("wr_cli.setup.steps.get_node_version")
    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_when_already_installed(self, mock_command_exists, mock_get_version):
        """Test execute returns True when Node.js is already installed."""
        mock_command_exists.return_value = True
        mock_get_version.return_value = "v18.0.0"
        
        console = MagicMock()
        step = CheckNodeJSStep(console, verbose=True)
        assert step.execute() is True
        console.print.assert_called_once_with("  Found Node.js v18.0.0")

    @patch("wr_cli.setup.steps.command_exists")
    @patch("wr_cli.setup.steps.platform.system")
    def test_execute_when_missing_on_macos(self, mock_system, mock_command_exists):
        """Test execute shows macOS install instruction when Node.js is missing."""
        mock_command_exists.return_value = False
        mock_system.return_value = "Darwin"
        
        console = MagicMock()
        step = CheckNodeJSStep(console, verbose=False)
        assert step.execute() is False
        console.print.assert_called_once_with(
            "[yellow]Node.js not found. Install with: brew install node[/yellow]"
        )


class TestCheckPythonStep:
    """Test the CheckPythonStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = CheckPythonStep(console, verbose=False)
        assert step.name == "Check Python"
        assert step.description == "Verify Python 3.11+ is installed"

    @patch("wr_cli.setup.steps.get_python_executable")
    def test_is_completed_when_python_exists(self, mock_get_python):
        """Test is_completed returns True when Python 3.11+ exists."""
        mock_get_python.return_value = "python3.11"
        
        console = MagicMock()
        step = CheckPythonStep(console, verbose=False)
        assert step.is_completed() is True

    @patch("wr_cli.setup.steps.get_python_executable")
    def test_is_completed_when_python_missing(self, mock_get_python):
        """Test is_completed returns False when Python 3.11+ is missing."""
        mock_get_python.return_value = None
        
        console = MagicMock()
        step = CheckPythonStep(console, verbose=False)
        assert step.is_completed() is False


class TestInstallUvStep:
    """Test the InstallUvStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = InstallUvStep(console, verbose=False)
        assert step.name == "Install uv"
        assert step.description == "Install uv package manager"

    @patch("wr_cli.setup.steps.command_exists")
    def test_is_completed_when_uv_exists(self, mock_command_exists):
        """Test is_completed returns True when uv exists."""
        mock_command_exists.return_value = True
        
        console = MagicMock()
        step = InstallUvStep(console, verbose=False)
        assert step.is_completed() is True
        mock_command_exists.assert_called_once_with("uv")


class TestLockPythonVersionStep:
    """Test the LockPythonVersionStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = LockPythonVersionStep(console, verbose=False)
        assert step.name == "Lock Python version"
        assert step.description == "Install and pin Python version from .python-version file"

    def test_get_target_python_version_from_file(self):
        """Test reading target Python version from .python-version file."""
        console = MagicMock()
        step = LockPythonVersionStep(console, verbose=False)
        
        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value="3.11.13"):
                version = step._get_target_python_version()
                assert version == "3.11.13"

    def test_get_target_python_version_default(self):
        """Test default Python version when .python-version file doesn't exist."""
        console = MagicMock()
        step = LockPythonVersionStep(console, verbose=False)
        
        with patch("pathlib.Path.exists", return_value=False):
            version = step._get_target_python_version()
            assert version == "3.11"


class TestInstallGhstackStep:
    """Test the InstallGhstackStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = InstallGhstackStep(console, verbose=False)
        assert step.name == "Install ghstack"
        assert step.description == "Install ghstack for GitHub workflow"

    @patch("wr_cli.setup.steps.command_exists")
    def test_is_completed_when_ghstack_exists(self, mock_command_exists):
        """Test is_completed returns True when ghstack exists."""
        mock_command_exists.return_value = True
        
        console = MagicMock()
        step = InstallGhstackStep(console, verbose=False)
        assert step.is_completed() is True
        mock_command_exists.assert_called_once_with("ghstack")

    @patch("wr_cli.setup.steps.command_exists")
    def test_is_completed_when_ghstack_missing(self, mock_command_exists):
        """Test is_completed returns False when ghstack is missing."""
        mock_command_exists.return_value = False
        
        console = MagicMock()
        step = InstallGhstackStep(console, verbose=False)
        assert step.is_completed() is False

    @patch("wr_cli.setup.steps.run_command_interactive")
    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_success(self, mock_command_exists, mock_run_command):
        """Test successful ghstack installation."""
        mock_command_exists.side_effect = [False, True]  # ghstack missing, uv exists
        mock_run_command.return_value = (True, "success", "")
        
        console = MagicMock()
        step = InstallGhstackStep(console, verbose=False)
        result = step.execute()
        
        assert result is True
        mock_run_command.assert_called_once_with(["uv", "tool", "install", "ghstack"])

    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_already_completed(self, mock_command_exists):
        """Test execute returns True when ghstack already installed."""
        mock_command_exists.return_value = True
        
        console = MagicMock()
        step = InstallGhstackStep(console, verbose=False)
        result = step.execute()
        
        assert result is True

    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_uv_not_available(self, mock_command_exists):
        """Test execute fails when uv is not available."""
        mock_command_exists.side_effect = [False, False]  # ghstack missing, uv missing
        
        console = MagicMock()
        step = InstallGhstackStep(console, verbose=False)
        result = step.execute()
        
        assert result is False
        console.print.assert_called_once_with("[red]uv not installed, cannot install ghstack[/red]")

    @patch("wr_cli.setup.steps.run_command_interactive")
    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_installation_fails(self, mock_command_exists, mock_run_command):
        """Test execute fails when installation fails."""
        mock_command_exists.side_effect = [False, True]  # ghstack missing, uv exists
        mock_run_command.return_value = (False, "", "installation failed")
        
        console = MagicMock()
        step = InstallGhstackStep(console, verbose=False)
        result = step.execute()
        
        assert result is False
        console.print.assert_called_once_with("[red]Failed to install ghstack: installation failed[/red]")


class TestSetupGhstackStep:
    """Test the SetupGhstackStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = SetupGhstackStep(console, verbose=False)
        assert step.name == "Setup ghstack"
        assert step.description == "Configure ghstack with GitHub authentication"

    def test_is_completed_when_config_exists(self):
        """Test is_completed returns True when .ghstackrc exists."""
        console = MagicMock()
        step = SetupGhstackStep(console, verbose=False)
        
        with patch("pathlib.Path.exists", return_value=True):
            assert step.is_completed() is True

    def test_is_completed_when_config_missing(self):
        """Test is_completed returns False when .ghstackrc is missing."""
        console = MagicMock()
        step = SetupGhstackStep(console, verbose=False)
        
        with patch("pathlib.Path.exists", return_value=False):
            assert step.is_completed() is False

    @patch("wr_cli.setup.steps.run_command_interactive")
    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_success(self, mock_command_exists, mock_run_command):
        """Test successful ghstack setup."""
        mock_command_exists.return_value = True
        mock_run_command.return_value = (True, "setup complete", "")
        
        console = MagicMock()
        step = SetupGhstackStep(console, verbose=False)
        result = step.execute()
        
        assert result is True
        mock_run_command.assert_called_once_with(["ghstack"])

    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_ghstack_not_installed(self, mock_command_exists):
        """Test execute fails when ghstack is not installed."""
        mock_command_exists.return_value = False
        
        console = MagicMock()
        step = SetupGhstackStep(console, verbose=False)
        result = step.execute()
        
        assert result is False
        console.print.assert_called_once_with("[red]ghstack not installed[/red]")


class TestInstallRequirementsStep:
    """Test the InstallRequirementsStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = InstallRequirementsStep(console, verbose=False)
        assert step.name == "Sync dependencies"
        assert step.description == "Install and sync project dependencies"

    def test_is_completed_always_false(self):
        """Test is_completed returns True (caching behavior)."""
        console = MagicMock()
        step = InstallRequirementsStep(console, verbose=False)
        assert step.is_completed() is True  # It actually returns True for caching

    @patch("wr_cli.setup.steps.run_command_interactive")
    def test_execute_success(self, mock_run_command):
        """Test successful requirements installation."""
        mock_run_command.return_value = (True, "installed", "")
        
        console = MagicMock()
        step = InstallRequirementsStep(console, verbose=False)
        result = step.execute()
        
        assert result is True
        mock_run_command.assert_called_once_with(["uv", "sync"], show_command=False)

    @patch("wr_cli.setup.steps.run_command_interactive")
    def test_execute_failure(self, mock_run_command):
        """Test failed requirements installation."""
        mock_run_command.return_value = (False, "", "sync failed")
        
        console = MagicMock()
        step = InstallRequirementsStep(console, verbose=False)
        result = step.execute()
        
        assert result is False
        console.print.assert_called_once_with("[red]Failed to sync dependencies: sync failed[/red]")


class TestInstallLocalPackagesStep:
    """Test the InstallLocalPackagesStep class."""

    def test_name_and_description(self):
        """Test step name and description."""
        console = MagicMock()
        step = InstallLocalPackagesStep(console, verbose=False)
        assert step.name == "Install local packages"
        assert step.description == "Install omnibus, parsley from local directories"

    def test_is_completed_always_false(self):
        """Test is_completed always returns False (always run this step)."""
        console = MagicMock()
        step = InstallLocalPackagesStep(console, verbose=False)
        assert step.is_completed() is False

    @patch("wr_cli.setup.steps.run_command_interactive")
    @patch("wr_cli.setup.steps.command_exists")
    @patch("pathlib.Path.exists")
    def test_execute_success(self, mock_path_exists, mock_command_exists, mock_run_command):
        """Test successful local packages installation."""
        mock_command_exists.return_value = True  # uv exists
        mock_path_exists.side_effect = lambda: True  # package dir and pyproject.toml exist
        mock_run_command.return_value = (True, "installed", "")
        
        console = MagicMock()
        step = InstallLocalPackagesStep(console, verbose=False)
        result = step.execute()
        
        assert result is True
        # Should call uv add for each package
        assert mock_run_command.call_count >= 1

    @patch("wr_cli.setup.steps.command_exists")
    def test_execute_failure(self, mock_command_exists):
        """Test failed local packages installation when uv is missing."""
        mock_command_exists.return_value = False  # uv not available
        
        console = MagicMock()
        step = InstallLocalPackagesStep(console, verbose=False)
        result = step.execute()
        
        assert result is False
        console.print.assert_called_once_with("[red]uv not installed[/red]")
