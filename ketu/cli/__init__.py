"""Ketu command-line interface.

Public entry point: :func:`main`. Used by both ``python -m ketu`` (via
``ketu/__main__.py``, repointed in Plan 11-05) and the ``ketu`` console
script (via ``[project.scripts]`` in pyproject.toml, repointed in Plan
11-05).
"""
from __future__ import annotations

from .parser import main

__all__ = ["main"]
