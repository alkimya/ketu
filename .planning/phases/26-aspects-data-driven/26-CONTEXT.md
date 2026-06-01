# Phase 26: Aspects Data-Driven + Dynamic Harmonics - Context

**Gathered:** 2026-06-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the aspect engine **data-driven**: aspects live in one declarative table
(`Aspect(name, angle, harmonic, coefficient, symbol)`) over which the
detection/orb logic iterates — no per-aspect hardcoding scattered across modules.
Add a **harmonic-selection API** (`aspects_for_harmonics([1, 2, 3, 6])`) alongside
the existing `CLASSICAL`/`TRADITIONAL`/`EXTENDED` presets. **Change the default
aspect set** to the seven half-circle harmonics (H1/2/3/6); the full-circle minors
(H5/H9/H10) become opt-in. Document the breaking public-surface change
(CHANGELOG + UPGRADING + concepts.md/api.md + fr gettext).

This is the **final aspect contract** for v1.3.0 — it lands before the release
(Phase 27) so there is no breaking 1.4 follow-up. It is a **breaking change** to
the public aspect surface (default set, presets, table shape).

Discussion clarified HOW to implement within this boundary. New capabilities
(e.g. CLI wiring of the harmonic API) are deferred, not in scope.

</domain>

<decisions>
## Implementation Decisions

### Aspect table shape
- **Extend the existing structured array** in `ketu/core.py` (`core.aspects`) —
  do NOT switch to NamedTuple/dataclass. Stay NumPy-first (CLAUDE.md), keep the
  vectorized iteration paradigm the engine already uses. The table grows two new
  dtype fields; it does not change kind.
- **Exactly the 5 roadmap fields**: `name`, `angle`, `harmonic`, `coefficient`,
  `symbol`. `coefficient` == the current `coef` field (orb weight). **No absolute
  orb field** — effective orb stays derived (body orb × coefficient), preserving
  current orb semantics.
- New fields to add to the dtype: `harmonic` (`i4`) and `symbol` (a Unicode-capable
  string field, e.g. `U2`/`U4` — sized at planning to hold the glyphs below).
- **Table stays in `ketu/core.py`** — it is the canonical historical source
  imported everywhere (`presets.py` does `from ketu.core import aspects`).
  Enrich in place; zero import-chain rewiring. The iteration/detection logic may
  live in `ketu/aspects/`.

### Aspect symbols
- Use **standard astrological Unicode glyphs** (e.g. ☌ conjunction, ⚹ sextile,
  □ square, △ trine, ☍ opposition, plus the minor-aspect glyphs).
- At planning: confirm the canonical glyph per aspect and check what
  `display.py` / `ketu/cli/formatters.py` already render, so the table's `symbol`
  column stays consistent with existing output. Size the `symbol` dtype field to
  fit the chosen glyphs.

### Harmonic-selection API
- **`aspects_for_harmonics([...])` returns a boolean mask** — the same length-N
  `np.bool_` mask shape that `resolve_aspect_set` and the presets produce. This is
  a drop-in into the existing pipeline (`aspects=`, the CLI, `resolve_aspect_set`),
  introducing **no new type to propagate** through hot loops.
- **Presets are redefined ON TOP of the harmonic table** — single source of truth.
  The default and presets become named compositions derived from the `harmonic`
  field (e.g. default = `aspects_for_harmonics([1, 2, 3, 6])`), not independently
  hardcoded masks. `EXTENDED` keeps all aspects.
- **Strict validation**: only harmonics actually present in the table
  (1, 2, 3, 5, 6, 9, 10) are valid. `aspects_for_harmonics([7])` raises
  `ValueError` (matches the strict error contract of `resolve_aspect_set`, which
  already raises on unknown preset/name/index).
- Public surface: `aspects_for_harmonics` is a **sister function** to
  `resolve_aspect_set`, exported from `ketu/aspects/presets.py` (or the package
  `__init__`), added to `__all__`.

### Default aspect set & coefficients
- **New default = the 7 half-circle aspects** (H1/2/3/6) — Conjunction (0°, H1),
  Semi-sextile (30°), Sextile (60°), Square (90°), Trine (120°), Quincunx (150°),
  Opposition (180°). These are exactly the existing `TRADITIONAL` preset's 7 rows.
- **This is a TWO-part default shift to call out in UPGRADING**: the *current*
  `resolve_aspect_set` default is `CLASSICAL` (5 aspects), not 7. So 1.3.0 both
  (a) adds Semi-sextile + Quincunx to the implicit default and (b) keeps the
  H5/H9/H10 minors out of the default. A caller with no `aspects=` now gets 7
  aspects instead of 5.
- **Coefficients kept bit-for-bit identical** for all retained aspects — only the
  *structure* (data-driven), the *default set*, and the *new harmonic/symbol
  columns* change. Effective orbs for retained aspects do not move. No numeric
  recalibration.
- **Opt-in path for the minors (H5/H9/H10)**: `EXTENDED` stays all-14 (unchanged),
  and `aspects_for_harmonics([5, 9, 10])` / `([1, 2, 3, 5, 6, 9, 10])` composes
  them à la carte. **No new preset** — two natural existing paths cover the need.

### Migration & public breaking change
- **Hard break, documented** — no deprecation alias, no transition period for the
  default change. Consistent with the Phase 24 precedent (13→14 bodies broke the
  freeze with no alias). UPGRADING shows how to restore old behavior:
  `aspects='classical'` for the old 5, `aspects='extended'` for all 14.
- **Kala**: generic UPGRADING note; Kala adapts post-release (same posture as the
  13→14 and angular_separation breaks — explicitly NOT a release blocker per
  project memory). If Kala passes `aspects=` explicitly it is unaffected; if it
  relies on the implicit default it now sees 7 instead of 5.
- **CHANGELOG + UPGRADING**: a dedicated "Aspect engine changes (1.3.0)" UPGRADING
  section with **before/after** of the default set (5→7), the recipe to restore
  the old default (`aspects='classical'`), the new `aspects_for_harmonics` API,
  and the minors-now-opt-in note — with concrete code examples. CHANGELOG gets a
  BREAKING entry under `[1.3.0]`.
- **concepts.md (Harmonic Theory)** gets a **full pedagogical explanation**: what a
  harmonic is, why half-circle (1/2/3/6) is the default, why full-circle minors
  (5/9/10) are opt-in, and how to compose a set via `aspects_for_harmonics`.
  Calibrate against existing concepts.md content at planning to avoid duplication.
- **api.md** updated for the new function + table fields; **fr gettext catalogs
  regenerated** through the existing pipeline (`docs/locale/`, gettext) — fr
  msgstr may stay English-fallback (consistent with Phase 25 / the pending
  pre-1.3.0-release fr-translation memory note).

### Claude's Discretion
- **CLI naming-collision resolution** (delegated): The CLI `--harmonics` flag
  already exists but means "aspect *set* spec" (preset name / canonical indices)
  and **explicitly rejects bare integers as ambiguous** ("harmonic? index?").
  The new API introduces real harmonic numbers. **Decision: API-only this phase;
  do NOT wire a harmonic-number CLI surface.** ASP-02 specifies an API, not a CLI;
  touching `--harmonics`'s contract would open a second (CLI) break the roadmap
  doesn't require. CLI wiring is captured as a deferred idea.
- Exact `symbol` dtype width, the precise glyph per aspect, and where the
  iteration/detection loop physically lives within `ketu/aspects/`.
- Whether `TRADITIONAL` is literally reused as the default constant or the default
  is a freshly-named harmonic-derived constant (both yield the same 7 rows).

</decisions>

<specifics>
## Specific Ideas

- **Harmonic-mapping validation needed in research/planning**: each angle must be
  assigned its correct harmonic so the "7 half-circle" set falls out cleanly. The
  delicate one is 60° (sextile): theoretically H6 (360/6), while 120° trine = H3
  and 90° square = H2. The mapping H1={0°,180°}, H2={90°}, H3={120°}, H6={30°,
  60°,150°} yields the intended 7. Confirm the H3/H6 attribution against standard
  harmonic theory at planning before freezing the `harmonic` column — this is a
  theory point to verify in research, not an open product choice.
- The whole change is **structure + default + new columns only** — retained
  aspects' angles and coefficients are byte-stable. The data-driven refactor must
  not perturb any existing numeric output for aspects that survive in a given set.
- 100% coverage gate and the full suite must stay green at the end (v1.3 invariant).

</specifics>

<deferred>
## Deferred Ideas

- **CLI wiring of the harmonic API** — exposing `aspects_for_harmonics` through a
  CLI surface (e.g. an `h1,h2,...`-prefixed form on `--harmonics`, or a new flag)
  to disambiguate from the existing set-spec semantics. Out of scope for Phase 26
  (API-only); candidate for a future CLI-focused phase if user demand appears.
- **Per-aspect absolute orb field** — adding an absolute orb column (fixed orb per
  aspect, independent of body) rather than the current body-orb × coefficient
  derivation. Would change orb semantics; deliberately NOT in this phase.
- **Numeric recalibration of coefficients to a clean `1/harmonic` formula** —
  considered and rejected for 1.3.0 (would add a numeric break on top of the
  structural one). Could be revisited later if a principled formula is wanted.

</deferred>

---

*Phase: 26-aspects-data-driven*
*Context gathered: 2026-06-01*
