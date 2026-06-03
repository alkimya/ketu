# Requirements: Ketu — Milestone v1.4 Dynamic Harmonics & Chiron Range

**Defined:** 2026-06-02
**Core Value:** Cycle calculations must be correct, tested, and performant. If the math is wrong, nothing downstream matters.

## v1.4 Requirements

Requirements for the v1.4 minor release. Each maps to exactly one roadmap phase (numbering continues from v1.3, which ended at Phase 27 + inserted 26.1 → v1.4 starts at Phase 28).

**Scope framing:** additive minor. The frozen sha256-fingerprinted `core.aspects` table and its named presets (CLASSICAL/TRADITIONAL/EXTENDED) stay byte-identical. The dynamic-harmonic capability is a PARALLEL path. The only behaviour change is the Chiron orb (0°→4°), documented in CHANGELOG. Runtime stays pure NumPy; `pyswisseph` remains test/build-only.

### Dynamic Harmonics

- [x] **ASP-04**: A user can generate the aspects of ANY integer harmonic `h` via a new public generator (e.g. `generate_harmonic_aspects(h)`), returning angle + coefficient specs — not limited to the preset set `{1,2,3,5,6,9,10}`
- [x] **ASP-05**: The generator uses the unified 360° convention — angles `fold_to_0_180(k·360/h)` for `k=1..h//2`, coefficient `k/h` — deduplicating mirror pairs and never emitting 0°/360°; unnamed high harmonics emit a blank symbol
- [x] **ASP-06**: A user can pass dynamically-generated aspects to `calculate_aspects` and have them detected with correct per-pair orbs `((orb1+orb2)/2 × dynamic_coef)` — dynamic aspects are first-class through the full detection chain (`calculate_aspects`, vectorized, batch)
- [x] **ASP-07**: Dynamic aspects flow correctly through cycles and synastry (orb derived from `core.bodies['orb']` × dynamic coefficient); no code path assumes the 14-row table for a dynamic aspect
- [x] **ASP-08**: The frozen `core.aspects` table and the named-preset sha256 fingerprints are unchanged (regression-pinned); `_VALID_HARMONICS` does NOT gate the dynamic path
- [x] **ASP-09**: `find_aspect_timing` and `find_aspects_between_dates` (hardcoded table-index lookups) are guarded so dynamic angles do not raise `IndexError`; off-table aspects resolve via a synthetic name, not a crash

### Chiron Orb

- [ ] **CHIR-06**: Chiron's natal orb is 4° (parity with Pluto) — single source `core.bodies['orb']` — propagating automatically to `get_orb`, synastry `_BODY_ORBS_16`, cycles, and the CLI
- [ ] **CHIR-07**: The byte-stable CLI fixture (`tests/cli/fixtures/v1_1_reference_output.txt`) is regenerated for the new Chiron aspects at 4° and manually audited as correct (not blindly accepted)
- [ ] **CHIR-08**: Synastry test docstrings/asserts that grouped Chiron with the zero-orb points (Rahu/Ketu/Lilith) are corrected; a new explicit test pins Chiron orb = 4°

### Chiron Range

- [ ] **CHIR-09**: The Chiron Chebyshev accuracy on the widened 1900–2100 range is empirically validated (spike) — max |Δλ| vs Swiss Ephemeris over the extended wings (incl. the ~1895–1896 perihelion region near the lower bound) is measured BEFORE committing the `.npz`; the Chebyshev degree is raised (e.g. 10→12) if the locked seg=32/deg=10 params fail the < 0.01° gate
- [ ] **CHIR-10**: `ketu/data/chiron_coeffs.npz` is regenerated over 1900–2100 via the offline `tools/gen_chiron_coeffs.py` (build-only pyswisseph); the embedded `jd_start`/`jd_end` reflect the new range and the partial first/last segments use `actual_len` (Phase 24 last-segment fix preserved)
- [ ] **CHIR-11**: Regression references are re-pinned to span 1900–2100 (new reference longitudes), and the accuracy regression test holds at < 0.01°; runtime eval stays pure NumPy

### Documentation

- [ ] **DOC-14**: `concepts.md` is recentred on the 180°-division default (harmonics 1/2/3/6); the aspect tables show CLASSICAL (5) and TRADITIONAL (7) only, with default vs opt-in marked; EXTENDED (H5/H9/H10) is removed from the tables but documented as available in code
- [ ] **DOC-15**: `migration.md` (the "EXTENDED = all 14 aspects unchanged" claim) and `relational_charts.md` (the `aspects` default `"classical"` claim) are corrected to the v1.3+ TRADITIONAL default; no remaining doc states the wrong default
- [ ] **DOC-16**: The dynamic-harmonics generator (with the accepted ~2× smaller full-circle orb note), Chiron 1900–2100 range, and Chiron orb 4° are documented in the API/concepts pages; no reference to Kala appears in any Ketu doc
- [ ] **DOC-17**: The French gettext catalogs for every touched page are re-extracted, re-translated (no English fallback for changed strings), and recompiled (`.mo`); en + fr docs build at the established 1-warning baseline; no doc/code drift (no example references a removed table)

### Release

- [ ] **REL-12**: Version is bumped to 1.4.0 (`pyproject.toml` + `ketu/__init__.py`); CHANGELOG `[1.4.0]` documents Added (dynamic harmonics, Chiron 1900–2100) + Changed (Chiron orb 4°, docs); fr CHANGELOG synced
- [ ] **REL-13**: `ketu==1.4.0` is published to PyPI via OIDC with a GitHub release (sdist + wheel); **both** `origin/main` and the tag are pushed (RTD follows main, PyPI follows tag); fresh-venv smoke confirms the dynamic generator, Chiron at 4° orb, the 1900–2100 range, and no `pyswisseph` at runtime

## Future Requirements

Deferred beyond v1.4. Tracked but not in this roadmap.

### Dynamic Harmonics (CLI / ergonomics)

- **ASP-F1**: CLI surface for arbitrary harmonics (`--harmonics h7`) — requires changing `parse_harmonics_spec`'s return type and has byte-stability implications for the CLI fixture; deferred to a follow-up
- **ASP-F2**: Formalize the synthetic naming scheme for off-table aspects (e.g. `H7k1`) as a documented API contract rather than an implementation detail

### Aspect engine cleanup

- **ASP-F3**: `find_aspect_timing` orb-derivation design debt (orb passed directly vs table-derived) — documented in v1.4, refactored later

## Out of Scope

Explicitly excluded for v1.4. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Reconciling the half-circle (table) and full-circle (dynamic) orb conventions | User accepted the ~2× smaller dynamic full-circle orbs; the two conventions coexist as independent paths — no unification |
| Replacing or extending the frozen 14-row `core.aspects` table | Fingerprint contract must hold; the dynamic path is parallel, never grows the table |
| `pyswisseph` as a runtime dependency | NumPy-only runtime + AGPL isolation non-negotiable; build-only for `.npz` regeneration |
| scipy / sympy / symbolic math for harmonics | Harmonic generation is plain NumPy arithmetic on angles; no new runtime dep |
| Any body beyond Chiron (centaurs, asteroids, fixed stars) | No new bodies in v1.4; bodies axis stays 14 → no Kala positional break |
| CLI `--harmonics h7` arbitrary-harmonic flag | Deferred (ASP-F1) — return-type + byte-stability work; Python API is the v1.4 surface |
| Chiron range beyond 1900–2100 | 1900–2100 covers all relevant birth/event dates + near-future projection; wider range adds segments/size for no demand |
| Davison composite, remaining Hermetic Lots, progressions/directions | Still deferred from v1.2/v1.3; orthogonal to harmonics + Chiron range |

## Traceability

Which phases cover which requirements. Filled during roadmap creation (2026-06-02).

| Requirement | Phase    | Status  |
|-------------|----------|---------|
| ASP-04      | Phase 28 | Complete |
| ASP-05      | Phase 28 | Complete |
| ASP-06      | Phase 28 | Complete |
| ASP-07      | Phase 28 | Complete |
| ASP-08      | Phase 28 | Complete |
| ASP-09      | Phase 28 | Complete |
| CHIR-06     | Phase 29 | Pending |
| CHIR-07     | Phase 29 | Pending |
| CHIR-08     | Phase 29 | Pending |
| CHIR-09     | Phase 30 | Pending |
| CHIR-10     | Phase 30 | Pending |
| CHIR-11     | Phase 30 | Pending |
| DOC-14      | Phase 31 | Pending |
| DOC-15      | Phase 31 | Pending |
| DOC-16      | Phase 31 | Pending |
| DOC-17      | Phase 31 | Pending |
| REL-12      | Phase 32 | Pending |
| REL-13      | Phase 32 | Pending |

**Coverage:**
- v1.4 requirements: 18 total
- Mapped to phases: 18/18 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-02*
*Last updated: 2026-06-02 — traceability filled (roadmap created)*
