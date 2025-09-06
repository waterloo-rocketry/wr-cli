# WR CLI

A command-line interface for bootstrapping Waterloo Rocketry development environments.

## Installation

```bash
pip install -e .
```

## Usage

### Setup Development Environment

```bash
wr setup
```

This will:

- Ensure Node.js and Python are installed
- Install `uv` package manager
- Install and configure `ghstack`
- Lock Python version to 3.11
- Install dependencies from `requirements.txt`
- Install omnibus and parsley libraries

### Run Custom Commands

```bash
wr run <command-name>
```

Commands are defined in `wr.yml`:

```yaml
commands:
  test: "pytest tests/"
  lint: "black . && isort ."
  build: "python -m build"
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
isort .
```
