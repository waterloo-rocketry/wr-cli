# WR CLI Project Overview

## Architecture

The WR CLI is built with a modular architecture that allows for easy extension and maintenance:

### Core Components

1. **Main CLI (`wr_cli/main.py`)** - Entry point using Click framework
2. **Configuration (`wr_cli/config.py`)** - YAML configuration loading
3. **Commands (`wr_cli/commands.py`)** - Custom command execution
4. **Setup System (`wr_cli/setup/`)** - Modular setup steps

### Setup System Architecture

The setup system is designed with extensibility in mind:

- **Base Class (`wr_cli/setup/__init__.py`)** - Abstract `SetupStep` class
- **Utilities (`wr_cli/setup/utils.py`)** - Common helper functions
- **Steps (`wr_cli/setup/steps.py`)** - Individual setup step implementations
- **Runner (`wr_cli/setup/runner.py`)** - Orchestrates all setup steps

### Setup Steps

The current setup steps are executed in this order:

1. **CheckNodeJSStep** - Verifies Node.js installation
2. **CheckPythonStep** - Verifies Python 3.11+ installation
3. **InstallUvStep** - Installs the `uv` package manager
4. **InstallGhstackStep** - Installs `ghstack` for GitHub workflow
5. **SetupGhstackStep** - Configures `ghstack` authentication
6. **LockPythonVersionStep** - Creates `.python-version` file
7. **InstallRequirementsStep** - Installs from `requirements.txt`
8. **InstallLocalPackagesStep** - Installs `omnibus` and `parsley` packages

## Adding New Setup Steps

To add a new setup step:

1. Create a new class inheriting from `SetupStep` in `wr_cli/setup/steps.py`
2. Implement the required abstract methods:
   - `name` - Display name for the step
   - `description` - What the step does
   - `execute()` - The actual setup logic
3. Optionally override `is_completed()` for smart skipping
4. Add the step to the `steps` list in `SetupRunner.__init__()`

### Example New Step

```python
class InstallDockerStep(SetupStep):
    \"\"\"Install Docker if not present.\"\"\"

    @property
    def name(self) -> str:
        return "Install Docker"

    @property
    def description(self) -> str:
        return "Install Docker for containerization"

    def is_completed(self) -> bool:
        return command_exists("docker")

    def execute(self) -> bool:
        if self.is_completed():
            return True

        # Platform-specific Docker installation logic
        system = platform.system().lower()
        if system == "darwin":
            self.console.print("[yellow]Please install Docker Desktop from https://docker.com[/yellow]")
        elif system == "linux":
            # Install via package manager
            success, _, stderr = run_command(["sudo", "apt-get", "install", "-y", "docker.io"])
            if not success:
                self.console.print(f"[red]Failed to install Docker: {stderr}[/red]")
                return False

        return command_exists("docker")
```

## Customization for Other Projects

The CLI is designed to be easily adaptable for other projects:

### 1. Fork and Modify

1. Fork this repository
2. Update `pyproject.toml` with new project details
3. Modify the setup steps in `wr_cli/setup/steps.py`
4. Update `wr.yml` with project-specific commands

### 2. Configuration-Driven Approach

For future versions, consider making steps configurable via YAML:

```yaml
# wr-config.yml
setup_steps:
  - name: check_nodejs
    enabled: true
  - name: check_python
    enabled: true
    version: "3.11"
  - name: install_custom_tool
    enabled: true
    url: "https://example.com/tool.sh"

commands:
  test: "pytest tests/"
  build: "python -m build"
```

## Testing

The project includes comprehensive tests:

- **Unit Tests** - Test individual components
- **Integration Tests** - Test the full CLI workflow
- **Setup Tests** - Verify setup steps work correctly

Run tests with:

```bash
wr run test
# or
pytest tests/ -v
```

## Development Workflow

1. **Make changes** to the code
2. **Format code** with `wr run format`
3. **Run tests** with `wr run test`
4. **Build package** with `wr run build`
5. **Test CLI** with `wr setup --verbose`

## Error Handling

The CLI includes comprehensive error handling:

- **Graceful failures** - Steps fail individually without stopping entire setup
- **Verbose mode** - Detailed error information with stack traces
- **User-friendly messages** - Clear instructions for manual fixes
- **Force mode** - Re-run steps even if previously completed

## Future Enhancements

Potential improvements:

1. **Configuration validation** - Validate `wr.yml` structure
2. **Step dependencies** - Allow steps to depend on others
3. **Parallel execution** - Run independent steps in parallel
4. **Plugin system** - Load setup steps from external packages
5. **Progress indicators** - Better visual feedback for long operations
6. **Rollback capability** - Undo setup steps if needed
7. **Cross-platform support** - Better Windows and Linux support
