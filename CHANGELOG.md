# Changelog

All notable changes to the WR CLI project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-05

### Added

- Initial release of WR CLI
- Modular setup system with 8 setup steps:
  - Node.js installation check
  - Python 3.11+ installation check
  - UV package manager installation
  - ghstack installation and configuration
  - Python version locking to 3.11
  - Requirements.txt dependency installation
  - Local package installation (omnibus, parsley)
- Custom command execution from wr.yml configuration
- Rich terminal output with colors and formatting
- Comprehensive error handling and verbose mode
- Force mode to re-run completed setup steps
- Full test suite with pytest
- Development tooling (black, isort, mypy)
- Documentation and contribution guidelines

### Features

- **Setup Command**: `wr setup [--force] [--verbose]`
- **Run Command**: `wr run <command-name> [--config path/to/wr.yml]`
- **Help System**: Built-in help for all commands
- **Configuration**: YAML-based command configuration
- **Extensible Architecture**: Easy to add new setup steps

### Technical Details

- Python 3.11+ required
- Built with Click framework for CLI
- Rich library for beautiful terminal output
- PyYAML for configuration parsing
- Comprehensive type hints throughout
- Modular design for easy extension

### Development

- Pre-commit hooks for code quality
- Automated testing with pytest
- Code formatting with black and isort
- Type checking with mypy
- Development mode installation support
- Example configurations and tests
