"""CLI tests for ``--list-parts`` introspection flag (PARTS-08).

Mirrors the ``TestListHouseSystems`` pattern in
``tests/cli/test_introspection.py`` — invokes ``main(["--list-parts"])``
via the same ``invoke_main`` fixture used by all other CLI tests, and also
tests ``cmd_list_parts()`` directly.

Tests run OFFLINE — no network access.
"""
from __future__ import annotations

import pytest


@pytest.fixture
def invoke_main():
    """Return a callable that runs ``ketu.cli.main(argv)`` and returns the rc."""
    def _invoke(argv):
        from ketu.cli import main
        return main(list(argv))
    return _invoke


class TestListPartsViaCLI:
    """``--list-parts`` flag: 3 names + 'fixed' note + exit 0."""

    def test_exit_code_is_zero(self, invoke_main) -> None:
        """``ketu --list-parts`` exits 0 (no subcommand required)."""
        rc = invoke_main(["--list-parts"])
        assert rc == 0

    def test_fortune_in_output(self, invoke_main, capsys) -> None:
        """'fortune' appears in --list-parts stdout."""
        invoke_main(["--list-parts"])
        out = capsys.readouterr().out
        assert "fortune" in out

    def test_spirit_in_output(self, invoke_main, capsys) -> None:
        """'spirit' appears in --list-parts stdout."""
        invoke_main(["--list-parts"])
        out = capsys.readouterr().out
        assert "spirit" in out

    def test_marriage_in_output(self, invoke_main, capsys) -> None:
        """'marriage' appears in --list-parts stdout."""
        invoke_main(["--list-parts"])
        out = capsys.readouterr().out
        assert "marriage" in out

    def test_fixed_note_in_output(self, invoke_main, capsys) -> None:
        """Marriage fixed-formula note contains the word 'fixed' (success criterion #4)."""
        invoke_main(["--list-parts"])
        out = capsys.readouterr().out
        assert "fixed" in out

    def test_all_three_names_present(self, invoke_main, capsys) -> None:
        """All 3 built-in part names appear in a single --list-parts call."""
        invoke_main(["--list-parts"])
        out = capsys.readouterr().out
        for name in ("fortune", "spirit", "marriage"):
            assert name in out, f"part {name!r} missing from --list-parts output"


class TestListPartsDirectCall:
    """Direct ``cmd_list_parts()`` call captures the same output."""

    def test_cmd_list_parts_produces_output(self, capsys) -> None:
        """cmd_list_parts() writes non-empty content to stdout."""
        from ketu.cli.introspection import cmd_list_parts
        cmd_list_parts()
        out = capsys.readouterr().out
        assert out.strip() != ""

    def test_cmd_list_parts_lists_all_names(self, capsys) -> None:
        """cmd_list_parts() stdout contains all 3 part names."""
        from ketu.cli.introspection import cmd_list_parts
        cmd_list_parts()
        out = capsys.readouterr().out
        for name in ("fortune", "spirit", "marriage"):
            assert name in out, f"part {name!r} missing from cmd_list_parts() output"

    def test_cmd_list_parts_fixed_note(self, capsys) -> None:
        """cmd_list_parts() trailing Marriage note contains 'fixed'."""
        from ketu.cli.introspection import cmd_list_parts
        cmd_list_parts()
        out = capsys.readouterr().out
        assert "fixed" in out
