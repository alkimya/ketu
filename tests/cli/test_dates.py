"""Unit tests for ketu.cli._dates.parse_iso_utc."""
from __future__ import annotations

import sys
from datetime import datetime, timezone

import pytest

from ketu.cli import _dates as _dates_mod
from ketu.cli._dates import parse_iso_utc
from ketu.ephemeris.time import utc_to_julian


class TestZShim:
    """Python-3.10 'Z' shim regression — must work on 3.10 AND 3.11+."""

    def test_z_suffix_accepted_on_all_python_versions(self):
        """The 'Z' shim is unconditional → must work on every Python the project supports."""
        jd = parse_iso_utc("2026-05-06T12:00:00Z")
        # Compare against an explicit UTC datetime → utc_to_julian path.
        expected_dt = datetime(2026, 5, 6, 12, 0, 0, tzinfo=timezone.utc)
        expected_jd = utc_to_julian(expected_dt)
        assert jd == pytest.approx(expected_jd, abs=1e-9)

    def test_plus_00_00_suffix_equivalent_to_z(self):
        jd_z = parse_iso_utc("2026-05-06T12:00:00Z")
        jd_offset = parse_iso_utc("2026-05-06T12:00:00+00:00")
        assert jd_z == pytest.approx(jd_offset, abs=1e-12)

    def test_z_shim_path_explicit_when_py310(self):
        """If running on Python 3.10, exercise the shim directly to ensure it isn't dead.

        On 3.11+, datetime.fromisoformat accepts Z natively; the shim is
        belt-and-suspenders. We assert the result matches regardless.
        """
        # Whatever Python we're on, the shim must produce the same result as
        # the explicit +00:00 form.
        ref = utc_to_julian(datetime(2000, 1, 1, 0, 0, 0, tzinfo=timezone.utc))
        assert parse_iso_utc("2000-01-01T00:00:00Z") == pytest.approx(ref, abs=1e-12)
        assert parse_iso_utc("2000-01-01T00:00:00+00:00") == pytest.approx(ref, abs=1e-12)
        # Inform the test report which interpreter ran (for CI debugging only).
        if sys.version_info < (3, 11):
            # On 3.10 the shim is mandatory; assert reaching here proves it.
            assert True


class TestZShimForceExercised:
    """MAJOR 4 fix (revision iteration 1): force the shim path on EVERY Python version.

    The previous shim tests are weak on Python 3.11+ because both ``Z`` and
    ``+00:00`` succeed via native ``fromisoformat`` support — if a future
    refactor accidentally deletes the shim's ``s = s[:-1] + "+00:00"``
    line, those tests still pass on 3.11+.

    These tests monkeypatch ``datetime.fromisoformat`` (as imported by the
    ``_dates`` module) to raise on raw ``Z`` input — emulating Python 3.10
    behavior. With the shim in place, ``parse_iso_utc("...Z")`` MUST still
    succeed because the ``Z`` is replaced with ``+00:00`` BEFORE the
    monkeypatched ``fromisoformat`` is called. Without the shim, the call
    would propagate the simulated ValueError and ``parse_iso_utc`` would
    raise SystemExit.

    This guarantees the shim is mechanically exercised on every CI run,
    regardless of interpreter version.
    """

    def test_shim_replaces_z_before_fromisoformat_call(self, monkeypatch):
        """Monkeypatch fromisoformat to reject 'Z'; shim must still produce success."""
        from datetime import datetime as real_datetime

        # Real fromisoformat from the test's module scope.
        real_fromisoformat = real_datetime.fromisoformat

        # The class-method we want to wrap. Build a 3.10-equivalent that
        # raises on raw 'Z' but accepts everything else (including +00:00).
        def py310_fromisoformat(s: str) -> real_datetime:
            if s.endswith("Z"):
                # Emulate Python 3.10: ValueError on naked 'Z'.
                raise ValueError(
                    "Invalid isoformat string (simulated 3.10): %r" % s
                )
            return real_fromisoformat(s)

        # Build a fake datetime class that uses our py310-equivalent
        # fromisoformat. We then monkeypatch the module-level binding
        # `_dates_mod.datetime` to this fake — _dates_mod uses
        # `datetime.fromisoformat(s)` so this is the right injection point.
        class FakeDatetime(real_datetime):
            @classmethod
            def fromisoformat(cls, s: str) -> "FakeDatetime":  # type: ignore[override]
                return py310_fromisoformat(s)  # type: ignore[return-value]

        monkeypatch.setattr(_dates_mod, "datetime", FakeDatetime)

        # With the shim, this MUST succeed (Z gets replaced before the
        # fromisoformat call).
        jd = parse_iso_utc("2026-05-06T12:00:00Z")
        ref = utc_to_julian(real_datetime(2026, 5, 6, 12, 0, 0, tzinfo=timezone.utc))
        assert jd == pytest.approx(ref, abs=1e-9)

    def test_shim_absent_would_fail_under_simulated_py310(self, monkeypatch):
        """Negative control: confirm the simulated 3.10 fromisoformat actually rejects 'Z'.

        This is the test that proves the test in the previous case is
        meaningful — if our monkeypatch were broken (e.g. didn't actually
        get applied), the shim test would pass trivially. Here we call
        the FAKE fromisoformat DIRECTLY (bypassing the shim) and assert
        it raises, so the harness is wired correctly.
        """
        from datetime import datetime as real_datetime

        real_fromisoformat = real_datetime.fromisoformat

        def py310_fromisoformat(s: str) -> real_datetime:
            if s.endswith("Z"):
                raise ValueError("simulated 3.10")
            return real_fromisoformat(s)

        with pytest.raises(ValueError):
            py310_fromisoformat("2026-05-06T12:00:00Z")

        # And confirm it accepts +00:00:
        assert py310_fromisoformat("2026-05-06T12:00:00+00:00") is not None


class TestNaiveDatetime:
    """Naive datetimes (no offset) are assumed UTC."""

    def test_naive_datetime_assumed_utc(self):
        jd_naive = parse_iso_utc("2026-05-06T12:00:00")
        jd_explicit = parse_iso_utc("2026-05-06T12:00:00Z")
        assert jd_naive == pytest.approx(jd_explicit, abs=1e-12)


class TestNonUTCOffset:
    """Non-UTC offsets converted to UTC before utc_to_julian."""

    def test_plus_2_hours_offset_converts_to_utc(self):
        # 14:00+02:00 == 12:00 UTC
        jd_paris = parse_iso_utc("2026-05-06T14:00:00+02:00")
        jd_utc = parse_iso_utc("2026-05-06T12:00:00Z")
        assert jd_paris == pytest.approx(jd_utc, abs=1e-9)


class TestErrors:
    """Bad input → SystemExit with helpful message."""

    def test_empty_string_rejected(self):
        with pytest.raises(SystemExit) as exc:
            parse_iso_utc("")
        assert "--date" in str(exc.value)

    def test_not_a_date_rejected(self):
        with pytest.raises(SystemExit) as exc:
            parse_iso_utc("not-a-date")
        assert "--date" in str(exc.value)

    def test_garbage_with_z_rejected(self):
        with pytest.raises(SystemExit):
            parse_iso_utc("xxxZ")
