# Contributing to WR CLI

## Development Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd wr-cli-prototype
   ```

2. **Set up development environment**

   ```bash
   # Install the CLI in development mode
   pip install -e ".[dev]"

   # Or use the CLI itself to set up
   wr setup
   ```

3. **Verify installation**
   ```bash
   wr --help
   wr run test
   ```

## Code Standards

This project follows strict code quality standards:

- **Python 3.11+** - Minimum supported version
- **Type hints** - All functions must have type annotations
- **Black formatting** - Consistent code style
- **isort imports** - Organized import statements
- **MyPy type checking** - Static type verification
- **Pytest tests** - Comprehensive test coverage

### Formatting and Linting

```bash
# Format code
wr run format

# Check formatting and types
wr run lint

# Run tests
wr run test
```

## Adding New Features

### Adding a New Setup Step

1. **Create the step class** in `wr_cli/setup/steps.py`:

   ```python
   class MyNewStep(SetupStep):
       @property
       def name(self) -> str:
           return "My New Step"

       @property
       def description(self) -> str:
           return "Description of what this step does"

       def is_completed(self) -> bool:
           # Return True if step is already done
           return False

       def execute(self) -> bool:
           # Implement the actual setup logic
           return True
   ```

2. **Add to the runner** in `wr_cli/setup/runner.py`:

   ```python
   self.steps: List[SetupStep] = [
       # ... existing steps ...
       MyNewStep(console, verbose),
   ]
   ```

3. **Write tests** in `tests/test_setup_steps.py`:
   ```python
   def test_my_new_step():
       console = Console()
       step = MyNewStep(console, verbose=False)
       assert step.name == "My New Step"
       # Add more specific tests
   ```

### Adding a New CLI Command

1. **Add command to `wr_cli/main.py`**:

   ```python
   @cli.command()
   @click.option("--option", help="Description")
   def my_command(option: str) -> None:
       """My new command description."""
       # Implementation here
   ```

2. **Write tests** in `tests/test_main.py`:
   ```python
   def test_my_command():
       runner = CliRunner()
       result = runner.invoke(cli, ["my-command", "--help"])
       assert result.exit_code == 0
   ```

## Testing

### Running Tests

```bash
# Run all tests
wr run test

# Run specific test file
pytest tests/test_main.py -v

# Run with coverage
pytest tests/ --cov=wr_cli --cov-report=html
```

### Writing Tests

- **Use pytest** for all tests
- **Mock external dependencies** (network calls, file system operations)
- **Test both success and failure cases**
- **Include integration tests** for CLI commands

### Test Structure

```
tests/
├── test_main.py              # CLI command tests
├── test_config.py            # Configuration loading tests
├── test_commands.py          # Custom command execution tests
├── test_setup_runner.py      # Setup orchestration tests
├── test_setup_steps.py       # Individual setup step tests
└── test_setup_utils.py       # Utility function tests
```

## Documentation

- **Update README.md** for user-facing changes
- **Update ARCHITECTURE.md** for structural changes
- **Add docstrings** to all new functions and classes
- **Update this file** for new contribution guidelines

## Pull Request Process

1. **Create a feature branch**

   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**

   - Follow the coding standards
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**

   ```bash
   wr run test
   wr run lint
   ```

4. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add my new feature"
   ```

5. **Submit a pull request**
   - Clear description of changes
   - Link to any related issues
   - Include screenshots if applicable

## Commit Message Format

Use conventional commits format:

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting)
- `refactor:` - Code refactoring
- `test:` - Adding or fixing tests
- `chore:` - Maintenance tasks

Examples:

```
feat: add Docker installation step
fix: handle missing requirements.txt gracefully
docs: update setup instructions
test: add tests for ghstack configuration
```

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features and fixes
3. **Create release tag**
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```
4. **Build and publish** (if configured)
   ```bash
   wr run build
   ```

## Getting Help

- **Issues** - Report bugs and request features
- **Discussions** - Ask questions and share ideas
- **Documentation** - Check README.md and ARCHITECTURE.md
- **Tests** - Look at existing tests for examples
