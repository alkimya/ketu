"""--harmonics SPEC argparse type validator.

Accepts a string spec and returns a length-14 ``np.bool_`` mask suitable
for filtering ``ketu.core.aspects``. The mask is produced by
:func:`ketu.aspects.presets.resolve_aspect_set` (Phase 9 deliverable);
this module is a thin tokenizer that picks the right input shape
(preset name vs. comma-separated indices) before delegating.

Spec semantics (from REQUIREMENTS.md CLI-02 + research Pattern 2):

- ``"classical"`` / ``"traditional"`` / ``"extended"`` / ``"all"``
  (case-insensitive) → named preset. ``"all"`` aliases ``"extended"``
  (preserves the v1.0 14-aspect output via CLI-03 byte-identical).
- ``"0,4,7,9,13"`` → comma-separated canonical aspect indices into
  ``ketu.core.aspects`` (length-14 registry, append-only).
- ``"12"`` → REJECTED (Pitfall 5; REQUIREMENTS.md line 101). Bare
  integers are ambiguous (single? harmonic? subset?). Use a named
  preset or comma-separated list.
- ``""`` empty → REJECTED.
- Anything else → REJECTED with a hint listing valid preset names.

argparse convention: this function is wired as ``type=parse_harmonics_spec``
on the ``--harmonics`` argument. argparse catches ArgumentTypeError /
TypeError / ValueError and renders ``error: argument --harmonics: <msg>``
with ``SystemExit(2)``.
"""
from __future__ import annotations

import argparse
from typing import FrozenSet

import numpy as np
import numpy.typing as npt

from ketu.aspects.presets import resolve_aspect_set

_PRESET_NAMES: FrozenSet[str] = frozenset(
    {"classical", "traditional", "extended", "all"}
)


def parse_harmonics_spec(value: str) -> npt.NDArray[np.bool_]:
    """Parse a ``--harmonics SPEC`` string into a length-14 boolean mask.

    Parameters
    ----------
    value : str
        Spec string. See module docstring for accepted forms.

    Returns
    -------
    np.ndarray of np.bool_, shape (14,)
        Boolean mask indexable into ``ketu.core.aspects``.

    Raises
    ------
    argparse.ArgumentTypeError
        On any invalid spec. argparse converts this to a clean
        ``error: argument --harmonics: <message>`` and exits with code 2.
    """
    if value is None or value == "":
        raise argparse.ArgumentTypeError(
            "--harmonics requires a value (named preset or comma-separated list)"
        )

    s = value.strip().lower()
    if not s:
        raise argparse.ArgumentTypeError(
            "--harmonics requires a non-blank value"
        )

    # Preset names — including 'all' alias for 'extended'.
    if s in _PRESET_NAMES:
        if s == "all":
            s = "extended"
        try:
            return resolve_aspect_set(s)
        except ValueError as e:  # defensive — resolve_aspect_set should accept all preset names
            raise argparse.ArgumentTypeError(str(e))

    # Comma-present → list of indices.
    if "," in s:
        try:
            indices = [int(x.strip()) for x in s.split(",") if x.strip()]
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"invalid harmonics list {value!r}: expected comma-separated "
                f"integers in [0, 14) (e.g. '0,4,7,9,13')"
            )
        if not indices:
            raise argparse.ArgumentTypeError(
                f"empty harmonics list {value!r}"
            )
        try:
            return resolve_aspect_set(indices)
        except (ValueError, TypeError) as e:
            raise argparse.ArgumentTypeError(
                f"invalid harmonics list {value!r}: {e}"
            )

    # No comma — try bare integer detection (must REJECT per spec).
    try:
        int(s)
    except ValueError:
        pass  # not an integer — fall through to "unrecognized" branch
    else:
        valid = sorted(_PRESET_NAMES)
        raise argparse.ArgumentTypeError(
            f"bare integer {value!r} is ambiguous (single index? harmonic "
            f"number? subset?); use a named preset ({', '.join(valid)}) or "
            f"a comma-separated list (e.g. '{value},...')"
        )

    valid = sorted(_PRESET_NAMES)
    raise argparse.ArgumentTypeError(
        f"unrecognized harmonics spec {value!r}: expected one of "
        f"{valid} or comma-separated indices in [0, 14)"
    )
