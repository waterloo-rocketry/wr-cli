# pyright: basic
"""Tests for __main__ module."""

import sys
from unittest.mock import patch


def test_main_module():
    """Test that __main__ module can be imported and executed."""
    # Remove the module if it was previously imported
    if 'wr_cli.__main__' in sys.modules:
        del sys.modules['wr_cli.__main__']
        
    with patch("wr_cli.main.cli") as mock_cli:
        # Import the __main__ module to trigger execution
        import wr_cli.__main__
        
        # The cli() is only called if __name__ == "__main__", but since we're importing
        # it as a module, __name__ will be "wr_cli.__main__", so cli() won't be called
        mock_cli.assert_not_called()
