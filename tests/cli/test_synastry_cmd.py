"""End-to-end tests for ``ketu synastry ...`` subcommand.

Mirrors the test shape of :mod:`tests.cli.test_houses_cmd`: in-process
invocation via the ``invoke_main`` fixture (CLI conftest) with
``capsys`` for stdout/stderr capture. Polar-latitude tests use
``--polar-fallback porphyry`` for the porphyry path; the default
``raise`` path is verified by asserting a propagating exception.
"""
from __future__ import annotations

import argparse
import json

import numpy as np
import pytest


# Cheap synthetic dates / locations: J2000.0 + Paris (default tests),
# extra equator/NYC chart-B for cross-pair coverage.
J2000 = "2000-01-01T12:00:00Z"
PARIS = (48.85, 2.35)
NYC = (40.71, -74.01)
EQUATOR = (0.0, 0.0)


# -------------------------------------------------------------------- #
# A. Parser argument requirements                                       #
# -------------------------------------------------------------------- #


class TestSynastryParserRequirements:
    """Argparse argument validation for the synastry subparser."""

    def test_synastry_subparser_exists(self, invoke_main, capsys):
        """``ketu synastry --help`` returns exit 0 and lists key args."""
        with pytest.raises(SystemExit) as exc:
            invoke_main(["synastry", "--help"])
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "synastry" in out
        assert "--date-a" in out
        assert "--date-b" in out

    def test_synastry_requires_date_a(self, invoke_main, capsys):
        """Missing --date-a triggers argparse error (exit 2, stderr cites flag)."""
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "synastry",
                "--lat-a", "48.85", "--lon-a", "2.35",
                "--date-b", J2000, "--lat-b", "40.71", "--lon-b", "-74.01",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "--date-a" in err

    def test_synastry_requires_date_b(self, invoke_main, capsys):
        """Missing --date-b triggers argparse error (exit 2, stderr cites flag)."""
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "synastry",
                "--date-a", J2000, "--lat-a", "48.85", "--lon-a", "2.35",
                "--lat-b", "40.71", "--lon-b", "-74.01",
            ])
        assert exc.value.code == 2
        err = capsys.readouterr().err
        assert "--date-b" in err

    def test_synastry_requires_lat_lon_pair_a(self, invoke_main, capsys):
        """Missing --lat-a or --lon-a triggers argparse error."""
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "synastry",
                "--date-a", J2000, "--lon-a", "2.35",
                "--date-b", J2000, "--lat-b", "40.71", "--lon-b", "-74.01",
            ])
        assert exc.value.code == 2

    def test_synastry_requires_lat_lon_pair_b(self, invoke_main, capsys):
        """Missing --lat-b or --lon-b triggers argparse error."""
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "synastry",
                "--date-a", J2000, "--lat-a", "48.85", "--lon-a", "2.35",
                "--date-b", J2000, "--lon-b", "-74.01",
            ])
        assert exc.value.code == 2


# -------------------------------------------------------------------- #
# B. Mode selector                                                      #
# -------------------------------------------------------------------- #


class TestSynastryModeSelector:
    """``--mode`` argument behaviour."""

    def test_synastry_mode_filtered_default(self, invoke_main, capsys):
        """Without --mode, output mentions 'filtered mode' in the table title."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "filtered mode" in out

    def test_synastry_mode_dense_explicit(self, invoke_main, capsys):
        """--mode dense produces 225 rows in JSON; STDERR cites the mode."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            "--mode", "dense", "--json",
        ])
        assert rc == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert len(data) == 225
        assert "Synastry mode: dense" in captured.err

    def test_synastry_mode_invalid_rejected(self, invoke_main, capsys):
        """--mode matrix is rejected by argparse choices=."""
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "synastry",
                "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
                "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
                "--mode", "matrix",
            ])
        assert exc.value.code == 2


# -------------------------------------------------------------------- #
# C. JSON output                                                        #
# -------------------------------------------------------------------- #


class TestSynastryJsonOutput:
    """``--json`` opt-in surface."""

    def test_synastry_json_output_parses(self, invoke_main, capsys):
        """--json output is valid JSON list-of-dicts."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            "--json",
        ])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert isinstance(data, list)
        assert all(isinstance(row, dict) for row in data)

    def test_synastry_json_keys_match_dtype_plus_names(self, invoke_main, capsys):
        """Each dict has the 8 SYNASTRY_DTYPE fields + body_a_name/body_b_name/aspect_name."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            "--json",
        ])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert len(data) > 0  # filtered mode has some aspected pairs
        expected_keys = {
            "body_a", "body_b", "lon_a", "lon_b",
            "aspect_type", "orb", "applying", "orb_limit",
            "body_a_name", "body_b_name", "aspect_name",
        }
        for row in data:
            assert set(row.keys()) == expected_keys

    def test_synastry_json_dense_count_225(self, invoke_main, capsys):
        """--mode dense --json returns exactly 225 dicts."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(EQUATOR[0]), "--lon-a", str(EQUATOR[1]),
            "--date-b", J2000, "--lat-b", str(EQUATOR[0]), "--lon-b", str(EQUATOR[1]),
            "--mode", "dense", "--json",
        ])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 225

    def test_synastry_json_filtered_no_negative_aspect_type(self, invoke_main, capsys):
        """Filtered JSON: all aspect_type >= 0 (no sentinel rows leak through)."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            "--json",
        ])
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert all(row["aspect_type"] >= 0 for row in data)
        # aspect_name is never None in filtered mode either.
        assert all(row["aspect_name"] is not None for row in data)


# -------------------------------------------------------------------- #
# D. House system selector                                              #
# -------------------------------------------------------------------- #


class TestSynastrySystemSelector:
    """``--system`` argument behaviour."""

    def test_synastry_system_placidus_default(self, invoke_main, capsys):
        """Without --system, stderr cites placidus."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
        ])
        assert rc == 0
        err = capsys.readouterr().err
        assert "House system: placidus" in err

    def test_synastry_system_whole_sign(self, invoke_main, capsys):
        """--system whole_sign succeeds; stderr cites whole_sign."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            "--system", "whole_sign",
        ])
        assert rc == 0
        err = capsys.readouterr().err
        assert "House system: whole_sign" in err

    def test_synastry_system_invalid_rejected(self, invoke_main, capsys):
        """--system nonexistent_xyz triggers argparse error."""
        with pytest.raises(SystemExit) as exc:
            invoke_main([
                "synastry",
                "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
                "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
                "--system", "nonexistent_xyz",
            ])
        assert exc.value.code == 2


# -------------------------------------------------------------------- #
# E. Polar fallback                                                     #
# -------------------------------------------------------------------- #


class TestSynastryPolarFallback:
    """``--polar-fallback`` argument pass-through to compute_chart."""

    def test_synastry_polar_fallback_default_raise(self, invoke_main):
        """At lat=80° with default raise, an exception propagates (no zero rc)."""
        with pytest.raises(Exception):
            invoke_main([
                "synastry",
                "--date-a", J2000, "--lat-a", "80.0", "--lon-a", "0.0",
                "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            ])

    def test_synastry_polar_fallback_porphyry_succeeds(self, invoke_main, capsys):
        """--polar-fallback porphyry substitutes Porphyry cusps and returns 0."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", "80.0", "--lon-a", "0.0",
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            "--polar-fallback", "porphyry",
        ])
        assert rc == 0
        out = capsys.readouterr().out
        assert "Synastry" in out


# -------------------------------------------------------------------- #
# F. ASCII table format                                                 #
# -------------------------------------------------------------------- #


class TestSynastryAsciiTable:
    """Default ASCII table layout."""

    def test_synastry_table_header_columns(self, invoke_main, capsys):
        """Table contains Body A / Body B / Aspect / Orb / Limit / Apply columns."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
        ])
        assert rc == 0
        out = capsys.readouterr().out
        for header in ("Body A", "Body B", "Aspect", "Orb", "Limit", "Apply"):
            assert header in out, f"column header {header!r} missing"

    def test_synastry_table_no_aspects_message(self, capsys):
        """Empty-result branch prints the 'no aspects' message.

        Mocked via a direct cmd_synastry call with patched
        calculate_synastry — the natural input space has no easy
        no-aspects corner case in default settings.
        """
        from ketu.cli.synastry_cmd import cmd_synastry
        from ketu.synastry import SYNASTRY_DTYPE
        from unittest.mock import patch

        args = argparse.Namespace(
            date_a=J2000, lat_a=PARIS[0], lon_a=PARIS[1],
            date_b=J2000, lat_b=NYC[0], lon_b=NYC[1],
            mode="filtered", system="placidus", polar_fallback="raise",
            json=False,
        )
        empty = np.empty(0, dtype=SYNASTRY_DTYPE)
        with patch("ketu.cli.synastry_cmd.calculate_synastry", return_value=empty):
            rc = cmd_synastry(args)
        assert rc == 0
        out = capsys.readouterr().out
        assert "(no aspects within synastry orbs)" in out


# -------------------------------------------------------------------- #
# G. STDERR diagnostics                                                 #
# -------------------------------------------------------------------- #


class TestSynastryStderrDiagnostics:
    """Resolved-config header on STDERR (CLI-06)."""

    def test_synastry_stderr_includes_resolved_config(self, invoke_main, capsys):
        """STDERR carries the synastry-mode and orbs preset citation."""
        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
        ])
        assert rc == 0
        err = capsys.readouterr().err
        assert "# Synastry mode: filtered" in err
        assert "# Orbs: synastry" in err


# -------------------------------------------------------------------- #
# H. JSON ↔ Python API consistency                                      #
# -------------------------------------------------------------------- #


class TestSynastryJsonMatchesPythonAPI:
    """The JSON dump mirrors a direct calculate_synastry call."""

    def test_json_rows_match_python_api(self, invoke_main, capsys):
        """JSON aspect_type values match a direct calculate_synastry call."""
        from ketu.charts import compute_chart
        from ketu.cli._dates import parse_iso_utc
        from ketu.synastry import calculate_synastry

        rc = invoke_main([
            "synastry",
            "--date-a", J2000, "--lat-a", str(PARIS[0]), "--lon-a", str(PARIS[1]),
            "--date-b", J2000, "--lat-b", str(NYC[0]), "--lon-b", str(NYC[1]),
            "--json",
        ])
        assert rc == 0
        cli_data = json.loads(capsys.readouterr().out)

        jd = parse_iso_utc(J2000)
        chart_a = compute_chart(jd, PARIS[0], PARIS[1])
        chart_b = compute_chart(jd, NYC[0], NYC[1])
        api_result = calculate_synastry(chart_a, chart_b)
        assert len(cli_data) == len(api_result)
        cli_keys = [(r["body_a"], r["body_b"], r["aspect_type"]) for r in cli_data]
        api_keys = [
            (int(r["body_a"]), int(r["body_b"]), int(r["aspect_type"]))
            for r in api_result
        ]
        assert cli_keys == api_keys
