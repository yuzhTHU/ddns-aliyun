import logging
import importlib
from .ipv4 import IPV4
from pathlib import Path

__all__ = ['IPV4']
_logger = logging.getLogger(__name__)

for py_file in Path(__file__).parent.glob("*.py"):
    if py_file.name != "__init__.py":
        try:
            importlib.import_module(f".{py_file.stem}", package=__name__)
        except Exception as e:
            _logger.warning(f"Failed to import {py_file.name}: {e}")
