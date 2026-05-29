# Phase 21: Quality - Context

**Gathered:** 2026-05-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Lift project quality to 100% on three internal axes — total test coverage (QAL-10),
a guarded division in the orbital engine (QAL-11), and deepened public-API docstrings
(QAL-12) — establishing a clean baseline **before** the ephemeris refactor (Phase 22)
and Chiron (Phase 24). No new astronomical capability ships in this phase; it is
quality hardening on the `ketu==1.2.0` baseline.

</domain>

<decisions>
## Implementation Decisions

### Div/0 guard (QAL-11)
- **Strategy: floor `r`, not clamp.** Apply `np.maximum(r, 1e-10)` before the
  `arcsin(z / r)` division at `orbital.py:755` so the heliocentric latitude stays
  finite and continuous at the degenerate `r→0` case (body at the Sun's center —
  never reached in practice, but must not warn or produce `NaN`).
- **Epsilon = `1e-10`.** The value cited in the ROADMAP. Far below any real
  heliocentric distance (min ~0.3 AU for Mercury), so zero impact on normal
  calculations; it only engages in the degenerate case.
- **Scope: all equivalent sites.** Audit `orbital.py` (and the rest of `ketu/ephemeris/`)
  for any division by `r` or same-shape `arcsin` and guard them consistently — don't
  leave unprotected twins of the line cited by QAL-11.
- **Regression test asserts the full contract.** Force `r→0` and assert: (1) no
  `RuntimeWarning` (via `warnings.catch_warnings` + `filterwarnings("error")`),
  (2) no `NaN` in the resulting latitude, AND (3) latitude stays within `[-90, 90]`.

### Docstring depth (QAL-12)
- **Scope: exported public API.** Everything in `ketu/__init__.py` `__all__` plus the
  subpackage `api.py` surfaces — the interface consumers (Kala, PyPI users) actually
  touch. Clear, verifiable boundary.
- **Language: English.** Consistent with the existing numpydoc docstrings, the
  `numpydoc validate` gate, and the international PyPI audience. FR translation of the
  *docs* happens via gettext in Phase 25 — not in the docstrings.
- **Examples are real, CI-collected doctests.** `>>>` format with actual outputs,
  collected by `pytest --doctest-modules` so they can never rot.
- **Determinism: fixed dates + rounded output.** Hard-code JD/dates in examples and
  round outputs (`round(x, 2)`) or use `ELLIPSIS` on decimals so doctests are
  reproducible across platforms (no float-jitter failures).
- **Notes cover accuracy vs Swiss + edge cases.** State expected precision (e.g.
  `< 0.01°` vs Swiss Ephemeris over a supported date range) where known/measurable,
  the supported date range, and limit behavior (poles, `r→0`, event-less days).

### Coverage strategy (QAL-10)
- **Targeted tests, zero pragmas.** The project currently has ZERO `no cover` pragmas
  — coverage is earned by real tests. Preserve that policy: every missing line
  (including the new `r→0` guard) is covered by a test that genuinely exercises the
  path. The 100% is real, not cosmetic. (No `# pragma: no cover` introduced.)
- **Uncovered conversion helpers tested with known values + round-trip.** For the
  `_ecliptic.py` outlier (`ra_to_lambda`, `lambda_to_ra`, the RA↔λ lines 43-47 + 69-73):
  assert against known astronomical values (e.g. equinoxes where RA = λ) AND a
  round-trip `ra→λ→ra ≈ identity`. Covers the line and validates correctness.

### Quality gate scope (QAL-10)
- **Project gate: `fail_under` 70 → 100, existing omits kept.** Set `fail_under = 100`
  on the non-omitted source. `ketu/__main__.py` (entry point) and `ketu/lunar_calendar.py`
  (legacy, already outside `interrogate`) stay in `[tool.coverage.run] omit` and remain
  documented. The 100% applies to the testable core.
- **Project 100% in CI; keep the per-subpackage 95% Makefile gates as-is.** The global
  `fail_under = 100` is enforced in CI. The seven per-subpackage Makefile gates (95%,
  via `make *-coverage`) stay as local safety nets — the project 100% dominates them
  de facto. No Makefile rewrites.

### Claude's Discretion
- Exact set of additional regression tests needed to close remaining (non-`_ecliptic`)
  coverage gaps — discover the gaps by running `pytest --cov` and close each with a
  real test.
- Precise wording/structure of each docstring's Examples and Notes (within the
  decisions above).
- How `--doctest-modules` is wired into the pytest config / CI without breaking
  partial test runs (the existing config deliberately avoids `--cov-fail-under` in
  `addopts` to allow partial runs — respect that constraint).

</decisions>

<specifics>
## Specific Ideas

- The project's "zero `no cover` pragma" discipline is a deliberate quality stance —
  keep 100% honest. The new div/0 guard is the canonical example: it adds a defensive
  line, and that line must be exercised by the QAL-11 regression test, not excluded.
- STATE.md flagged a line-number reconciliation (`orbital.py:755` vs the pending todo's
  `:733`) for the div/0 site — confirmed during this discussion: the live
  `arcsin(z / r)` is at **line 755**. Resolve the stale todo reference accordingly.
- Doctests double as the most durable form of QAL-12: an example that's CI-collected
  can't drift from the code.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (The per-body strategy refactor that the
guard audit might tempt toward is Phase 22; documenting Chiron accuracy is Phase 25.)

</deferred>

---

*Phase: 21-quality*
*Context gathered: 2026-05-29*
