# Requirements: Ketu — v1.5 Lunar Declination & Harmonics Debt

**Defined:** 2026-06-03
**Core Value:** Cycle calculations must be correct, tested, and performant.
**Framing:** Additive minor (`ketu==1.5.0`). No breaking changes intended. `is_ascending` (ecliptic latitude β) and `core.aspects` (14-row frozen table + sha256 preset fingerprints) stay UNCHANGED. The biodynamic framing is **aspect-centric** (angular mechanics + the Moon's own δ trajectory), NOT zodiacal/sidereal (Thun constellation calendar) — see `.planning/research/DECLINATION.md`.

## v1 Requirements

Requirements for the v1.5 release. Each maps to a roadmap phase (numbering continues at **33**).

### Declination (DECL)

Equatorial declination δ as a first-class, vectorizable quantity, plus the Moon's biodynamic montant/descendant trajectory and out-of-bounds detection. Computation reuses the verified `coordinates.py` chain (Meeus eq. 13.4; `ecliptic_to_equatorial` → `rectangular_to_spherical` numerically equivalent to the direct formula to machine precision).

- [ ] **DECL-01**: User can compute a body's equatorial declination δ via `declination(jdate, body)` (scalar) — degrees, north +, south −, bounded [−90, +90]
- [ ] **DECL-02**: `declination` is vectorizable over a `jdate` array (no Python loop in the hot path), consistent with ketu's NumPy-first contract
- [ ] **DECL-03**: An equivalence regression test pins `declination` against the existing `ecliptic_to_equatorial` → `rectangular_to_spherical` chain (asserts machine-precision agreement, locking the reuse)
- [ ] **DECL-04**: User can compute the rate of change of declination via `declination_velocity(jdate, body)` (degrees/day), using ketu's existing forward finite-difference idiom (step mirrors `lat_velocity`); no longitude-style wraparound correction (δ is unbounded-free in [−90, +90])
- [ ] **DECL-05**: User can test the Moon's biodynamic montant/descendant trajectory via `is_ascending_declination(jdate, body)` (bool, True when dδ/dt > 0 = montante) — distinct from and parallel to the existing β-based `is_ascending`, which stays UNCHANGED
- [ ] **DECL-06**: User can test out-of-bounds via `is_out_of_bounds(jdate, body)` (bool, True when |δ| > ε), using the **instantaneous** obliquity ε(jd) (`true_obliquity`) as the threshold — physically correct, free, consistent with the engine
- [ ] **DECL-07**: `body_decl` field added to `CHART_DTYPE` (14 bodies, f8, additive, mirrors `body_lats`) — declination present in every computed chart; returns / synastry / composite inherit it without recomputation
- [ ] **DECL-08**: A `CHART_DTYPE` layout ratchet test guards the additive `body_decl` field change (analogue of the prior 13→14 body-count ratchet); downstream positional-contract impact (Kala) documented
- [ ] **DECL-09**: Declination feature documented (en + fr) — `declination` / `declination_velocity` / `is_ascending_declination` / `is_out_of_bounds` API + the aspect-centric montant/descendant framing (draconic month ~27.21 d, OOB nodal cycle), with the explicit β-vs-δ distinction

### Harmonics Debt (HARM)

Pay down the three dynamic-harmonics debts left open by v1.4 (`generate_harmonic_aspects`, `dynamic_specs=`). One grouped phase, implementation order F2 → F3 → F1 (CLI surface depends on the naming contract being stable). The frozen `core.aspects` table + V1/V13 sha256 fingerprints stay byte-identical throughout.

- [ ] **HARM-01** (ASP-F2): The synthetic off-table aspect naming scheme `H{h}-{k}` (k = 1..h//2, e.g. `H7-1`, `H7-2`, `H7-3`) is a documented public API contract — format, ordering, and bytes-vs-str encoding guaranteed; always `H{h}-{k}` for uniformity (no traditional-name substitution by the generator)
- [ ] **HARM-02** (ASP-F2): A pinning test asserts `generate_harmonic_aspects(h)['name']` exactly for representative harmonics, including boundaries (h=2 opposition-only; even h folding the last row to exactly 180°; h up to 64) — locking the contract across versions
- [ ] **HARM-03** (ASP-F2): Documentation distinguishes the two channels: the GENERATOR always emits `H{h}-{k}`, while the DETECTION layer prefers the canonical table name on angle collision (e.g. 120° → Trine, not `H3-1`)
- [ ] **HARM-04** (ASP-F3): `find_aspect_timing` can derive the dynamic orb itself via a new `dyn_coef: Optional[float] = None` parameter (computes `(bodies['orb'][b1] + bodies['orb'][b2]) / 2 * dyn_coef`), instead of the caller passing the orb raw
- [ ] **HARM-05** (ASP-F3): The static path (`orb=None` → table lookup via `get_orb`) and the existing explicit `orb=<float>` escape hatch both stay backward-compatible and byte-identical; precedence when both `orb` and `dyn_coef` are given is defined and tested
- [ ] **HARM-06** (ASP-F1): User can request an arbitrary harmonic on the CLI via `--harmonics h7` (h-prefixed, case-insensitive; disambiguated from the rejected bare integer and from preset/index syntax) → produces the harmonic's `h//2` aspects via `dynamic_specs=`
- [ ] **HARM-07** (ASP-F1): `parse_harmonics_spec` returns a typed shape (mask + dynamic_specs, e.g. a `NamedTuple`) clean under mypy `--strict`, signalling the dynamic channel to the command layer; grammar is **Tight** — `h7` alone or the existing comma index list; preset+harmonic mixing (`traditional,h7`) and multi-harmonic (`h7,h11`) are explicitly deferred
- [ ] **HARM-08** (ASP-F1): The existing v1.1 CLI byte-stability fixture stays UNCHANGED (verified, not re-pinned); a NEW byte-stability fixture for a `--harmonics h7` invocation is freshly generated and manually audited; the resolved-config stderr header labels the arbitrary-harmonic selection clearly
- [ ] **HARM-09** (ASP-F1): The `--harmonics h7` CLI surface is documented (en + fr) — syntax, semantics, the Tight-grammar boundary (what is deferred)

### Release (REL)

- [ ] **REL-01**: All quality gates green — 100% coverage (`fail_under=100`, zero pragma), mypy `--strict` clean, numpydoc + interrogate gates pass, full test suite passes
- [ ] **REL-02**: Version bumped to 1.5.0 (`pyproject.toml` + `ketu/__init__.py`); dated `[1.5.0]` CHANGELOG (Added: declination δ + montant/descendant + OOB + `body_decl`; arbitrary-harmonic CLID `h7`; Changed: none breaking) + `fr/CHANGELOG.md` synced; UPGRADING v1.4→v1.5 + README "What's New"
- [ ] **REL-03**: `ketu==1.5.0` shipped to PyPI via OIDC trusted publishing; tag `v1.5.0` + `origin/main` BOTH pushed (RTD follows main, PyPI follows tag); GitHub release with sdist + wheel; post-publish fresh-venv smoke FROM PyPI asserts the v1.5 surface (declination, montant/descendant, OOB, `--harmonics h7`, no `pyswisseph` at runtime)

## Future Requirements

Deferred to a future milestone. Tracked but not in the v1.5 roadmap.

### Declination Aspects (DECLA)

- **DECLA-01**: Parallels (same δ) as a declination aspect type — real Western-astrology technique (parallel ≈ conjunction); coherent with the aspect-centric biodynamic framing but touches the aspect engine
- **DECLA-02**: Contra-parallels (opposite-hemisphere equal δ) as a declination aspect type (contra-parallel ≈ opposition)
- **DECLA-03**: Declination-aspect orbs + detection-chain integration (new aspect type alongside the longitude aspects)

### Harmonics CLI (HARMF)

- **HARMF-01**: Rich CLI grammar — multi-harmonic (`h7,h11`) and preset+harmonic mixing (`traditional,h7`)

## Out of Scope

Explicitly excluded for v1.5. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Declination aspects (parallels / contra-parallels) | Real technique, but touches the aspect engine (new type, orbs, detection integration); NOT needed by the montant/descendant core (Moon's δ trajectory alone). Tracked as DECLA-01..03 |
| Changing `is_ascending` (β) to δ semantics | Would be BREAKING; β and δ are distinct notions and both are valid. `is_ascending` stays UNCHANGED; δ trajectory is a new parallel function (`is_ascending_declination`) |
| Rich `--harmonics` grammar (`h7,h11`, `traditional,h7`) | Tight grammar (`h7` alone + index list) is the v1.5 surface; mixing/multi adds grammar + byte-stability cost for little immediate need. Tracked as HARMF-01 |
| Fixed 23°26′ OOB threshold | Instantaneous ε(jd) is physically correct and free; the fixed threshold is slightly wrong at range edges |
| Declination for non-chart consumers beyond CHART_DTYPE (e.g. a `body_decl` in CYCLE_DTYPE) | CYCLE_DTYPE is Moon-Moon angular-separation oriented; declination belongs to chart/position surface. Scalar `declination()` covers ad-hoc needs |
| `pyswisseph` / scipy as runtime dependency | Pure-NumPy contract non-negotiable; pyswisseph stays test/build-only |
| Timezone handling | UTC remains required; caller's responsibility |

## Traceability

Which phases cover which requirements. Populated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DECL-01 | TBD | Pending |
| DECL-02 | TBD | Pending |
| DECL-03 | TBD | Pending |
| DECL-04 | TBD | Pending |
| DECL-05 | TBD | Pending |
| DECL-06 | TBD | Pending |
| DECL-07 | TBD | Pending |
| DECL-08 | TBD | Pending |
| DECL-09 | TBD | Pending |
| HARM-01 | TBD | Pending |
| HARM-02 | TBD | Pending |
| HARM-03 | TBD | Pending |
| HARM-04 | TBD | Pending |
| HARM-05 | TBD | Pending |
| HARM-06 | TBD | Pending |
| HARM-07 | TBD | Pending |
| HARM-08 | TBD | Pending |
| HARM-09 | TBD | Pending |
| REL-01 | TBD | Pending |
| REL-02 | TBD | Pending |
| REL-03 | TBD | Pending |

**Coverage:**
- v1.5 requirements: 21 total (9 DECL + 9 HARM + 3 REL)
- Mapped to phases: 0 (roadmap pending)
- Unmapped: 21 ⚠️ (filled by roadmap)

---
*Requirements defined: 2026-06-03*
*Last updated: 2026-06-03 after initial definition*
