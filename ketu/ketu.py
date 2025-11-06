"""Backward compatibility module.

This module provides backward compatibility for imports like 'from ketu import ketu'.
All functionality is now organized in core, calculations, and display modules.
"""

# Re-export everything from the new modular structure
from .core import *
from .calculations import *
from .display import *

__all__ = [
    # Re-export all symbols
]
