"""CLI-03 self-stable forward-contract regression test.

Pins the stdout of ``python -m ketu --harmonics all aspects --date
2000-01-01T12:00:00Z`` to the v1.1 reference fixture committed at
``tests/cli/fixtures/v1_1_reference_output.txt``. Any drift in the
``--harmonics all`` legacy escape-hatch output (added space, dropped
block, format change, encoding flip, etc.) fails this test in CI.

History / pivot rationale
-------------------------
This plan (11-06) was originally specified as a **v1.0 byte-identical
regression test** — pin the output of the v1.0.0 git tag and assert
HEAD reproduces it byte-for-byte. That contract is mathematically
infeasible on this branch:

* Phase 8 ("Lilith calibration") shifted Lilith's longitude
  computation. The J2000.0 UTC fixture row for Lilith in v1.0 read
  ``Gemini 23º21'31"``; the same invocation on v1.1 emits
  ``Sagittarius 23º27'41"``. The astronomy underneath the CLI was
  deliberately changed.
* Phase 9 ("configurable aspects") moved the default aspect set
  semantics; ``--harmonics all`` now resolves through
  ``ketu.aspects_config.resolve_set("extended")`` rather than v1.0's
  hard-coded enumeration. Same end-set, but the resolution path and
  the resolved-config header (``# Aspect set: ...`` on stderr) are
  new surfaces.

Both changes are intentional. The user accepted "Option A": re-pin the
fixture to the **current v1.1 output** and reinterpret CLI-03 as a
**self-stable forward contract** — it catches future format drift but
intentionally drops the "byte-identical to v1.0" guarantee that was
already lost in reality.

What this test still guarantees
-------------------------------
1. The ``--harmonics all`` stdout format is frozen as of this commit.
   Any future PR that touches ``ketu.display.print_positions``,
   ``ketu.display.print_aspects``, ``ketu.cli.aspects_cmd``, or the
   trailing "Aspect Timing Example" block surfaces here as a clear
   byte-diff failure.
2. The resolved-config header (``# Aspect set: ...``) lands on
   ``stderr``, never on ``stdout`` — guards against the
   "header leak to stdout" pitfall that would silently corrupt every
   downstream consumer parsing ``--harmonics all`` output.
3. The degree-symbol convention is locked to U+00BA ``º`` (MASCULINE
   ORDINAL INDICATOR), inherited from v1.0's ``display.py``. A
   future "fix" that converts it to U+00B0 ``°`` (DEGREE SIGN) would
   change every aspect/position line and surface here.

This is a **subprocess** test (not in-process via ``invoke_main``) for
two reasons:

* It mirrors what users actually run — the surface is the bytes the
  OS sees, including any encoding or line-ending quirks.
* It exercises the ``ketu/__main__.py`` entry point repointed in
  Plan 11-05; an in-process test would skip that path.
"""
from __future__ import annotations

import difflib
import subprocess
import sys
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures" / "v1_1_reference_output.txt"

REFERENCE_DATE = "2000-01-01T12:00:00Z"
REFERENCE_ARGV = [
    sys.executable,
    "-m",
    "ketu",
    "--harmonics",
    "all",
    "aspects",
    "--date",
    REFERENCE_DATE,
]


class TestV1_1ReferenceByteStable:
    """CLI-03: --harmonics all stdout is byte-identical to the v1.1 fixture.

    Self-stable forward contract — pin format drift after Phase 11
    consolidation, NOT v1.0 backward compatibility (see module docstring
    for the Option A pivot history).
    """

    def test_fixture_exists_and_nonempty(self) -> None:
        """Sanity: the fixture file is committed and has content."""
        assert FIXTURE.exists(), f"Fixture missing: {FIXTURE}"
        assert FIXTURE.stat().st_size > 1500, (
            f"Fixture suspiciously small: {FIXTURE.stat().st_size} bytes "
            f"(expected >1500; v1.1 reference is ~2125 bytes)"
        )

    def test_harmonics_all_byte_identical_to_v1_1_reference(self) -> None:
        """Run ``python -m ketu --harmonics all aspects --date 2000-01-01T12:00:00Z``
        and assert stdout matches the pinned v1.1 fixture byte-for-byte.
        """
        expected = FIXTURE.read_bytes()

        result = subprocess.run(
            REFERENCE_ARGV,
            capture_output=True,
            check=False,  # inspect non-zero exits ourselves for better messages
            timeout=60,
        )

        if result.returncode != 0:
            pytest.fail(
                f"`python -m ketu --harmonics all aspects --date {REFERENCE_DATE}` "
                f"exited with code {result.returncode}.\n"
                f"stderr: {result.stderr.decode(errors='replace')!r}"
            )

        if result.stdout != expected:
            actual = result.stdout
            actual_text = actual.decode(errors="replace")
            expected_text = expected.decode(errors="replace")
            diff = "\n".join(
                difflib.unified_diff(
                    expected_text.splitlines(),
                    actual_text.splitlines(),
                    fromfile="v1_1_reference_output.txt (expected)",
                    tofile="current --harmonics all stdout (actual)",
                    lineterm="",
                )
            )
            pytest.fail(
                "CLI-03 self-stable forward contract: --harmonics all stdout "
                "drifted from the v1.1 reference fixture.\n\n"
                "Common causes of drift:\n"
                "  - emit_resolved_config leaked '# ' lines to stdout "
                "(should be file=sys.stderr)\n"
                "  - 'Aspect Timing Example' trailing block missing or "
                "reformatted (must match Plan 11-04 cmd_aspects exactly)\n"
                "  - Aspect-printing format string drifted (column widths, "
                "separators, spacing)\n"
                "  - Position-printing changed in display.print_positions\n"
                "  - Degree-symbol flipped: U+00BA `º` (MASCULINE ORDINAL, "
                "the v1.x convention) vs U+00B0 `°` (DEGREE SIGN)\n"
                "  - Number formatting drifted (e.g. width of arc-minutes "
                "field, trailing zero handling)\n\n"
                "If the drift is INTENTIONAL (e.g. a deliberate format "
                "redesign in a major-version bump), regenerate the fixture:\n"
                f"  python -m ketu --harmonics all aspects --date {REFERENCE_DATE} "
                f"> {FIXTURE}\n"
                "and document the bump in the release notes.\n\n"
                f"Unified diff:\n{diff}"
            )

    def test_stderr_is_structurally_clean(self) -> None:
        """Stderr should contain only the resolved-config header (or be empty).

        Specifically: every non-empty stderr line must start with ``# ``.
        This guards against ``print()`` calls accidentally hitting stderr
        (e.g. a future ``print(..., file=sys.stderr)`` that emits user-
        visible content) and against warnings or tracebacks leaking into
        what should be a "diagnostics-header-only" channel.
        """
        result = subprocess.run(
            REFERENCE_ARGV,
            capture_output=True,
            check=False,
            timeout=60,
        )
        assert result.returncode == 0, (
            f"CLI exited non-zero (rc={result.returncode}); "
            f"stderr={result.stderr!r}"
        )
        stderr_text = result.stderr.decode()
        for line in stderr_text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            assert stripped.startswith("#"), (
                f"Non-comment line leaked to stderr: {line!r}\n"
                f"Full stderr:\n{stderr_text}"
            )

    def test_stderr_contains_aspect_set_header(self) -> None:
        """CLI-06 belt-and-suspenders: the resolved-config header is present
        on stderr (confirms ``emit_resolved_config`` ran with file=sys.stderr).
        """
        result = subprocess.run(
            REFERENCE_ARGV,
            capture_output=True,
            check=False,
            timeout=60,
        )
        assert result.returncode == 0
        stderr = result.stderr.decode()
        assert "# Aspect set:" in stderr, (
            f"CLI-06 header expected on stderr; got stderr={stderr[:500]!r}"
        )

    def test_degree_symbol_is_masculine_ordinal(self) -> None:
        """The pinned fixture uses U+00BA ``º`` (MASCULINE ORDINAL INDICATOR),
        not U+00B0 ``°`` (DEGREE SIGN). This is the v1.x display convention
        carried over from v1.0's ``display.py``. Locking it here means a
        future PR that "modernizes" to U+00B0 surfaces as a clear failure
        instead of silent breakage of every downstream parser.
        """
        data = FIXTURE.read_bytes()
        # UTF-8 encoding of U+00BA is 0xc2 0xba; U+00B0 is 0xc2 0xb0.
        assert data.count(b"\xc2\xba") > 20, (
            "Fixture lost its U+00BA `º` masculine-ordinal degree symbols"
        )
        assert data.count(b"\xc2\xb0") == 0, (
            "Fixture contains U+00B0 `°` degree-sign characters; "
            "the v1.x convention is U+00BA `º` MASCULINE ORDINAL INDICATOR"
        )
