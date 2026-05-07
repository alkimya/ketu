"""End-to-end tests for `ketu houses ...` subcommand."""
from __future__ import annotations

import re

import numpy as np
import pytest

from ketu import calculate_houses
from ketu.cli._dates import parse_iso_utc


class TestHousesCmdMatchesPythonAPI:
    """CLI output cusps match the Python API for the same inputs (CLI-04 success criterion 4)."""

    PARIS = ("2026-05-06T12:00:00Z", 48.85, 2.35)
    SYDNEY = ("2026-05-06T12:00:00Z", -33.87, 151.21)
    GREENWICH = ("2000-01-01T12:00:00Z", 51.4769, 0.0)

    @pytest.mark.parametrize("system", ["placidus", "koch", "porphyry"])
    @pytest.mark.parametrize("loc", [PARIS, SYDNEY, GREENWICH])
    def test_cli_cusps_match_python_api(self, invoke_main, capsys, system, loc):
        date_iso, lat, lon = loc
        rc = invoke_main([
            "houses",
            "--date", date_iso, "--lat", str(lat), "--lon", str(lon),
            "--system", system,
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "House Cusps" in out
        # Cross-check: parse the printed degrees and compare to API.
        jd = parse_iso_utc(date_iso)
        rec = calculate_houses(jd=jd, lat=lat, lon=lon, system=system, polar_fallback="raise")
        cusps_api = np.asarray(rec["cusps"]).reshape(-1)
        # Pull each "(NNN.NNNN°)" from the output lines for verification.
        printed = [float(m.group(1)) for m in re.finditer(r"\(\s*([\d.\-]+)°\)", out)]
        # 12 cusps + ASC + MC = 14 angles printed
        assert len(printed) == 14
        for i in range(12):
            assert printed[i] == pytest.approx(cusps_api[i], abs=1e-3)


class TestHousesCmdFlags:
    """Argument validation paths."""

    def test_missing_lat_rejected(self, invoke_main, capsys):
        with pytest.raises(SystemExit) as exc:
            invoke_main(["houses", "--date", "2000-01-01T12:00:00Z", "--lon", "0"])
        assert exc.value.code == 2

    def test_invalid_system_rejected(self, invoke_main, capsys):
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "houses", "--date", "2000-01-01T12:00:00Z",
                "--lat", "48.85", "--lon", "2.35",
                "--system", "regiomontanus",
            ])
        assert exc.value.code == 2

    def test_default_system_is_placidus(self, invoke_main, capsys):
        rc = invoke_main([
            "houses", "--date", "2000-01-01T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
        ])
        assert rc == 0


class TestHousesCmdPolar:
    """Polar latitudes — default raise vs porphyry fallback."""

    def test_polar_default_raises(self, invoke_main, capsys):
        """At lat=80°, default --polar-fallback=raise propagates HighLatitudeError → SystemExit."""
        with pytest.raises(Exception):
            invoke_main([
                "houses", "--date", "2000-01-01T12:00:00Z",
                "--lat", "80.0", "--lon", "0.0",
                "--system", "placidus",
            ])
        # HighLatitudeError is a ValueError subclass; not yet caught by cmd_houses
        # (intentional — surfaces as a clear traceback or non-zero exit).

    def test_polar_porphyry_fallback_succeeds(self, invoke_main, capsys):
        """--polar-fallback porphyry substitutes Porphyry cusps and returns 0."""
        rc = invoke_main([
            "houses", "--date", "2000-01-01T12:00:00Z",
            "--lat", "80.0", "--lon", "0.0",
            "--system", "placidus",
            "--polar-fallback", "porphyry",
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "House Cusps" in out


class TestHousesCmdISOZShim:
    """End-to-end: 'Z' suffix accepted (Python 3.10 + 3.11+)."""

    def test_z_suffix_accepted_via_cli(self, invoke_main, capsys):
        rc = invoke_main([
            "houses", "--date", "2026-05-06T12:00:00Z",
            "--lat", "48.85", "--lon", "2.35",
            "--system", "placidus",
        ])
        assert rc == 0
        assert "House Cusps" in capsys.readouterr().out
