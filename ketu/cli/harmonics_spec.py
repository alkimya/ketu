"""
--harmonics SPEC argparse type validator.

Accepts a string spec and returns a :class:`HarmonicsSelection` NamedTuple
``(mask, dynamic_specs)`` suitable for driving :func:`ketu.aspects.calculate_aspects`.
The mask (length-14 ``np.bool_``) is produced by
:func:`ketu.aspects.presets.resolve_aspect_set` (Phase 9 deliverable);
``dynamic_specs`` carries the structured array from
:func:`ketu.aspects.harmonics.generate_harmonic_aspects` for ``h<N>`` tokens, or
``None`` for preset / index-list forms.

This module is a thin tokenizer that picks the right input shape
(preset name vs. comma-separated indices vs. harmonic token) before delegating.

Spec semantics (from REQUIREMENTS.md CLI-02 + research Pattern 2):

- ``"classical"`` / ``"traditional"`` / ``"extended"`` / ``"all"``
  (case-insensitive) → named preset. ``"all"`` aliases ``"extended"``
  (preserves the v1.0 14-aspect output via CLI-03 byte-identical).
  Returns ``HarmonicsSelection(mask=<preset mask>, dynamic_specs=None)``.
- ``"0,4,7,9,13"`` → comma-separated canonical aspect indices into
  ``ketu.core.aspects`` (length-14 registry, append-only).
  Returns ``HarmonicsSelection(mask=<computed mask>, dynamic_specs=None)``.
- ``"h7"`` / ``"H7"`` (case-insensitive) → harmonic token ``h<N>`` for any
  integer ``N`` in ``[2, 64]``. Returns
  ``HarmonicsSelection(mask=np.zeros(14, bool), dynamic_specs=<array>)``.
  Range validation is delegated to :func:`generate_harmonic_aspects`; a
  ``ValueError`` from it is wrapped as :exc:`argparse.ArgumentTypeError`.
  The grammar is **Tight**: ``h7,h11`` and ``traditional,h7`` are **not**
  accepted (deferred to HARMF-01). ``h7,h11`` is parsed by the comma branch
  where ``int("h7")`` raises, yielding an ``ArgumentTypeError``.
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
import re
from typing import FrozenSet, NamedTuple, Optional

import numpy as np
import numpy.typing as npt

from ketu.aspects.harmonics import DynamicAspectSpec, generate_harmonic_aspects
from ketu.aspects.presets import resolve_aspect_set

_PRESET_NAMES: FrozenSet[str] = frozenset(
    {"classical", "traditional", "extended", "all"}
)

#: Compiled regex for the ``h<N>`` harmonic token (case-insensitive via prior
#: ``.lower()``). Applied AFTER the preset and comma branches, BEFORE the
#: bare-int rejection trap.
_H_TOKEN_RE = re.compile(r"^h(\d+)$")


class HarmonicsSelection(NamedTuple):
    """
    Resolved harmonics selection returned by :func:`parse_harmonics_spec`.

    Attributes
    ----------
    mask : np.ndarray of np.bool_, shape (14,)
        Length-14 boolean mask indexable into ``ketu.core.aspects``.  Always
        present.  For ``h<N>`` tokens the mask is all-False (only dynamic specs
        are used); for preset / index-list inputs it carries the resolved
        selection and ``dynamic_specs`` is ``None``.
    dynamic_specs : DynamicAspectSpec
        Structured array from :func:`~ketu.aspects.harmonics.generate_harmonic_aspects`
        for ``h<N>`` inputs.  ``None`` for preset and comma-separated-index inputs.
    """

    mask: npt.NDArray[np.bool_]
    dynamic_specs: Optional[DynamicAspectSpec]


def parse_harmonics_spec(value: str) -> HarmonicsSelection:
    """
    Parse a ``--harmonics SPEC`` string into a :class:`HarmonicsSelection`.

    Parameters
    ----------
    value : str
        Spec string. See module docstring for accepted forms.

    Returns
    -------
    HarmonicsSelection
        NamedTuple ``(mask, dynamic_specs)`` where ``mask`` is a length-14
        ``np.bool_`` array and ``dynamic_specs`` is either ``None`` (for
        preset / index-list inputs) or a structured array of dynamic aspect
        specs (for ``h<N>`` tokens).

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
            return HarmonicsSelection(
                mask=resolve_aspect_set(s), dynamic_specs=None
            )
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
            return HarmonicsSelection(
                mask=resolve_aspect_set(indices), dynamic_specs=None
            )
        except (ValueError, TypeError) as e:
            raise argparse.ArgumentTypeError(
                f"invalid harmonics list {value!r}: {e}"
            )

    # Harmonic token h<N> — AFTER preset+comma, BEFORE bare-int trap.
    m = _H_TOKEN_RE.match(s)
    if m:
        try:
            specs = generate_harmonic_aspects(int(m.group(1)))
        except ValueError as e:
            raise argparse.ArgumentTypeError(str(e))
        return HarmonicsSelection(
            mask=np.zeros(14, dtype=np.bool_), dynamic_specs=specs
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
