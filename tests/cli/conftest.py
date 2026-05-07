"""Shared fixtures for tests/cli/.

The CLI is exercised by injecting argv into ``ketu.cli.main(argv)`` and
capturing stdout/stderr via pytest's ``capsys`` fixture. Subprocess-based
testing lives in test_legacy_byte_identical.py only (Plan 11-06) — every
other test should use in-process invocation for speed.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable, Sequence

import pytest

# Make sure tests can locate the v1.0 fixture file (used in Plan 11-06).
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def invoke_main() -> Callable[[Sequence[str]], int]:
    """Return a callable that runs ``ketu.cli.main(argv)`` and returns the rc.

    Imported lazily inside the fixture so a missing import (e.g. during
    Plan 11-01 scaffolding) surfaces as a test failure, not a collection
    error.
    """

    def _invoke(argv: Sequence[str]) -> int:
        from ketu.cli import main

        return main(list(argv))

    return _invoke
