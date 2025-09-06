# pyright: basic
"""Tests for configuration module."""

import tempfile
from pathlib import Path

import pytest

from wr_cli.config import load_config


def test_load_config_with_valid_file():
    """Test loading a valid config file."""
    config_content = """
project_name: "test-project"
commands:
  test: "echo test"
  build: "echo build"
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write(config_content)
        config_path = Path(f.name)
    
    try:
        config = load_config(config_path)
        assert config["project_name"] == "test-project"
        assert config["commands"]["test"] == "echo test"
        assert config["commands"]["build"] == "echo build"
    finally:
        config_path.unlink()


def test_load_config_with_nonexistent_file():
    """Test loading a config file that doesn't exist."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("nonexistent.yml"))


def test_load_config_with_invalid_yaml():
    """Test loading an invalid YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        f.write("invalid: yaml: content: [")
        config_path = Path(f.name)
    
    try:
        with pytest.raises(Exception):  # YAML parsing error
            load_config(config_path)
    finally:
        config_path.unlink()


def test_load_config_from_file():
    """Test loading config from a specific file path."""
    # Create a temporary wr.yml file
    config_content = """
project_name: "file-project"
commands:
  test: "file test command"
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config_file = temp_path / "custom.yml"
        config_file.write_text(config_content)
        
        config = load_config(config_file)
        assert config["project_name"] == "file-project"
        assert config["commands"]["test"] == "file test command"
