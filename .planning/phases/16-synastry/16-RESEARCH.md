# Phase 16: Synastry — Research

**Researched:** 2026-05-10
**Domain:** Cross-chart aspect computation (NumPy structured-array pipeline) over `CHART_DTYPE` pairs, with tightened orb convention + dual output mode + CLI surface.
**Confidence:** HIGH (composition only — every primitive exists in v1.1/v1.2; novelty is the dtype, the orb convention, and the cross-product N×M loop).

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Phase boundary**

- Compute aspects between two natal charts via `calculate_synastry(chart_a, chart_b, aspects="classical", orbs="synastry", mode="filtered")`.
- Returns a `SYNASTRY_DTYPE` NumPy structured array.
- Supports two output modes: dense N×N matrix / filtered orbed list.
- Uses synastry-tightened orbs distinct from natal orbs.
- Exposes a `ketu synastry` CLI sub-command.
- Depends on Phase 14 (`CHART_DTYPE`).
- Out of scope: composite (P17), solar return (P18), Arabic Parts cross-chart (P19), Davison (v1.3+), transits-to-natal, batch synastry.

**SYNASTRY_DTYPE schema (locked)**

- Floor: 5 mandatory fields from ROADMAP success criterion #1: `body_a, body_b, aspect_type, orb, applying`.
- **Self-pairs INCLUDED** in dense mode — Sun_A↔Sun_B, Moon_A↔Moon_B are canonical synastry aspects.
- Matrix is fully populated, no diagonal skip.

**Dense vs filtered API (locked)**

- Mode selector: `mode="dense" | "filtered"` (explicit string parameter, extensible to future modes).
- Default: `mode="filtered"` — practical default for astrological use.
- Both modes share the same `SYNASTRY_DTYPE`.
- Batch over arrays of charts: NOT in scope (single-pair only).

**Orbs synastry source (locked)**

- Foundation formula: re-use Ketu's house orb formula `orb_pair = (bodies["orb"][b1] + bodies["orb"][b2]) / 2 * aspects["coef"][asp]` from `ketu/aspects/calculator.py:32`. AUTHORITATIVE.
- Body-orb values `(12, 12, 8, 10, 8, 10, 10, 6, 6, 4, 0, 0, 0)` and `aspects["coef"]` are AUTHORITATIVE.
- Synastry orbs MUST derive from this formula, not redefine ab initio.

**CLI exposition (locked)**

- Sub-command IN SCOPE: `ketu synastry` is a full sub-command.
- Default output format: aligned ASCII table, `--json` opt-in.
- Flags exposed: `--mode dense|filtered`, `--system <house_system>`, `--list-orbs`.

### Claude's Discretion

- Exact `SYNASTRY_DTYPE` field set beyond the 5 mandatory.
- Body scope (planets only / +ASC/MC / full CHART_DTYPE bodies).
- `applying` field computation strategy (velocity-based vs always-False MVP).
- Output schema identity in dense mode (NaN-fill vs masked).
- Row ordering in filtered mode.
- Synastry orb tightening formula (factor / per-aspect / per-body).
- Storage location for synastry orbs (ORBS registry vs dedicated module).
- User override surface for orbs.
- Whether `orbs="classical"` is accepted in synastry.
- CLI input args design (suffixed / file / positional).
- `--list-orbs` exact print format.

### Deferred Ideas (OUT OF SCOPE)

- Batch synastry (N×M chart pairs in one call).
- Composite chart — Phase 17.
- Solar return synastry — Phase 18.
- Davison composite — v1.3.
- Transit-to-natal aspects (different concern).
- Synastry interpretation engine (text rendering of meanings).
</user_constraints>

---

## Summary

Phase 16 is **composition over invention** — much like Phase 14. Every astronomical primitive exists in v1.1/v1.2: `CHART_DTYPE` provides per-chart `body_lons`/`body_speeds`/`asc`/`mc` (Phase 14), `bodies["orb"]` provides per-body orb widths (`ketu/core.py:65`), `aspects["coef"]` provides per-aspect coefficients (`ketu/core.py:86`), `resolve_aspect_set` provides the configurable aspect mask (Phase 9). The novelty is **threefold**:

1. A new `SYNASTRY_DTYPE` for the cross-product result rows (the 5 mandatory fields plus a small set of auto-sufficiency fields).
2. A new `orbs="synastry"` convention — recommended as a **multiplicative factor of 0.5** applied to the existing natal formula, citing Astrodienst (astro.com)'s documented half-natal-orb practice.
3. A new `ketu/synastry/` subpackage mirroring `ketu/houses/` and `ketu/charts/` (`core.py` + `api.py` + `__init__.py`), plus a `ketu synastry` CLI sub-command mirroring `ketu houses`.

A registry-style indirection is **not justified** for orb conventions in v1.2 (only one preset is shipped — `"synastry"`). A small `_PRESETS_BY_NAME` dict + `resolve_orb_set(spec)` resolver mirroring `ketu/aspects/presets.py` is the right shape. This keeps the door open for a second preset (e.g. `"natal"` for caller comparison views) without committing to the over-engineered registry pattern.

The `applying` field should be **velocity-based using the natal speeds stored in `CHART_DTYPE.body_speeds`** — both charts are static (their natal speeds were "frozen" at birth), so applying/separating is a pure deterministic function of `(speed_a, speed_b, lon_a, lon_b, aspect_angle)`. Computing it adds zero astronomical state and ~10 lines of NumPy; an "always-False MVP" would force callers to write the logic themselves and would make the field semantically misleading.

**Primary recommendation:**

Build `ketu/synastry/{core.py,api.py,orbs.py,__init__.py}` mirroring `ketu/charts/`. `SYNASTRY_DTYPE` = 8 fields (pure record-style, NOT chart-axis-style). Default body scope = full 13-body axis from `CHART_DTYPE` + ASC + MC (15 bodies; ASC/MC contact is canonical in synastry). Orb convention = `(natal_orb_a + natal_orb_b)/2 * coef * 0.5` with the 0.5 factor citing astro.com. `applying` field = velocity-based natal convention. Filtered mode rows ordered by `(body_a_index, body_b_index)` canonical order (predictable for ML/tests, NOT orb-ascending). `ketu synastry` CLI uses suffixed `--date-a/--lat-a/--lon-a` + `--date-b/--lat-b/--lon-b` args (no chart files in MVP — file inputs deferred).

---

## Standard Stack

### Core (already in v1.2)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| numpy | 2.x (existing) | Structured-array dtype, broadcasting, vectorised ops | Project-wide constraint (PROJECT.md "pure-NumPy contract"). |
| `ketu.charts.CHART_DTYPE` | v1.2 (Phase 14) | Pre-computed natal chart input | Locked Phase 14 contract; CHART_DTYPE.body_axis is FROZEN per D-08. |
| `ketu.core.bodies` | v1.0 | Per-body orb widths and IDs (`bodies["orb"]`, `bodies["name"]`) | Single source of truth for orb foundation values (Abu Ma'shar / Al-Biruni convention). |
| `ketu.core.aspects` | v1.0 (14-row) | Per-aspect angles and coefficients (`aspects["angle"]`, `aspects["coef"]`) | Single source of truth for the orb formula coefficient table (canonical 14-row registry). |
| `ketu.aspects.presets.resolve_aspect_set` | v1.1 (Phase 9) | Resolve `aspects=` spec to length-14 bool mask | Reused identically — synastry honors `aspects="classical"` exactly like natal aspects. |

### Supporting (already in v1.2)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `ketu.calculations.distance` | v1.0 | Angular separation modulo 360 | Reused for cross-chart pair distance (already vectorised). |
| `ketu.cli.parser` | v1.1 (Phase 11) | argparse subcommand + introspection skeleton | Add `synastry` subparser + `--list-orbs` top-level flag (mirror `--list-house-systems`). |
| `ketu.cli._dates.parse_iso_utc` | v1.1 (Phase 11) | ISO-8601 → JD conversion with Z-suffix shim | Reused for both `--date-a` and `--date-b` parsing. |
| `ketu.cli.formatters.emit_resolved_config` | v1.1 (Phase 11) | Resolved-config STDERR header | Extended to include `orbs=` label + chart-pair description. |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Multiplicative factor 0.5 | Per-aspect synastry coefficient table parallel to `aspects["coef"]` | Per-aspect table allows nuance (e.g. trines kept wider than squares in synastry — Liz Greene-style 6° on sextiles, 5° on squares). But it breaks the single-source-of-truth principle and forces a second hardcoded table. The astro.com convention is uniformly half-natal — simplest, cited, defensible. **Reject.** Future: a `"liz_greene"` orb preset can add the table-based variant later via the `_PRESETS_BY_NAME` map. |
| Per-body synastry orb override (e.g. ASC=4°, MC=4° instead of derived) | Hardcoded body-orb table for synastry | Adds a third hardcoded table; deviates from the locked "derive from natal formula" decision. **Reject.** ASC/MC have `bodies["orb"]=0` in v1.0 (not in `bodies` registry — they are houses fields). The synastry orb for ASC/MC must use a sensible default — recommend `ASC_MC_ORB_DEG = 8` (single named constant, derived once at module-load), then halved by the synastry factor → 4°. This matches the typical 3-5° range cited in astro.com. |
| Full ORBS registry (decorator + dict) mirroring `houses/registry.py` | Frozen dict of presets mirroring `aspects/presets.py` | Registry adds extension surface for v1.3+ user-registered orb sets but introduces a dict mutability concern (already addressed for SYSTEMS via the loaded-at-import discipline) and a `register_orbs()` decorator. v1.2 ships ONE preset (`"synastry"`). YAGNI. **Reject for v1.2** — but mirror the `_PRESETS_BY_NAME` + `resolve_orb_set(spec)` shape so a v1.3 lift to full registry is cosmetic. |
| Always-False `applying` MVP | Velocity-based natal-speed convention | MVP defers cost but makes the field semantically misleading and forces callers to recompute downstream. The math is 5 lines of NumPy (sign of `(speed_a - speed_b) * (aspect_angle - distance)`). **Reject MVP.** Document the convention loudly. |

**Installation:** No new dependencies. Pure-NumPy.

---

## Architecture Patterns

### Recommended Project Structure

```
ketu/
└── synastry/
    ├── __init__.py        # public surface: calculate_synastry, SYNASTRY_DTYPE, ORB_PRESETS
    ├── core.py            # SYNASTRY_DTYPE definition + module docstring "Why structured array"
    ├── orbs.py            # synastry orb formula + _PRESETS_BY_NAME + resolve_orb_set()
    └── api.py             # calculate_synastry() — composition layer

ketu/cli/
├── parser.py              # add `synastry` subparser + --list-orbs top-level flag
├── synastry_cmd.py        # NEW: cmd_synastry dispatcher (mirror houses_cmd.py)
└── introspection.py       # add cmd_list_orbs (mirror cmd_list_house_systems)

tests/
└── synastry/
    ├── __init__.py
    ├── conftest.py        # oracle fixtures (3+ celebrity couples, JSON-backed)
    ├── fixtures/
    │   └── reference_synastry.json   # AA-rated couples + Astro.com-validated aspects
    ├── test_dtype.py      # SYNASTRY_DTYPE shape + field-name invariants
    ├── test_orbs.py       # orb formula + factor + resolve_orb_set
    ├── test_calculate_synastry.py     # filtered + dense + self-pairs + edge cases
    ├── test_oracle.py     # 3 hand-validated celebrity-couple synastry oracles
    └── test_applying.py   # applying/separating semantics
tests/cli/
├── test_synastry_cmd.py   # CLI table output + --json + --list-orbs
```

**Why this layout (mirrors `ketu/charts/` per Phase 14 RESEARCH.md):**

- `core.py` holds the dtype + module docstring explaining "Why structured array" — same pattern as `charts/core.py`, `houses/core.py`, `cycles/calculator.py:37`.
- `api.py` holds the public composition function — same pattern as `charts/api.py`, `houses/api.py`.
- `orbs.py` is justified because the orb logic has > 30 lines (formula + presets + resolver + cite-block) AND has its own preset registry pattern. It's the synastry-side analogue of `aspects/presets.py`.
- `__init__.py` re-exports the 3-4 public names — same pattern as `charts/__init__.py`.
- A separate `tests/synastry/` directory mirrors `tests/charts/` and `tests/houses/`.

### Pattern 1: SYNASTRY_DTYPE — record-style (NOT axis-style)

**What:** `SYNASTRY_DTYPE` is **record-style** (1-D array of N rows, one per cross-pair) — NOT axis-style (2-D matrix indexed by `[body_a, body_b]`). This is a deliberate departure from `CHART_DTYPE.aspect_matrix` which is axis-style ((13, 13) subarray).

**When to use:** Synastry's natural unit is "an aspect record between two specific bodies", and the dense vs filtered modes both produce record sequences (dense produces N_a × N_b records with `aspect_type=-1` sentinels for non-aspected pairs; filtered produces only the K rows where an aspect was detected). A record-style dtype unifies both modes under one contract — caller code is `for row in result: ...` or `result[result["aspect_type"] >= 0]` regardless of mode.

**Why not axis-style** (per D-05 / D-17 in Phase 14): the axis-style `aspect_matrix` made sense for `CHART_DTYPE` because charts naturally vectorise over `(jd, lat, lon)` and the 13-body axis is FROZEN. Synastry has TWO body axes that can differ in size if/when ASC/MC are included as virtual bodies (15-body axis), and the natural broadcast unit is the chart pair (singleton in v1.2, vectorised over pairs in v1.3+). Record-style aligns naturally with both.

**Example:**

```python
# Source: Phase 14 CHART_DTYPE (charts/core.py:85) — opposite pattern
# Source: ketu/cycles/calculator.py:37 — same record-style pattern
SYNASTRY_DTYPE = np.dtype([
    ("body_a",      "i1"),       # chart-A body index, [0..14]
    ("body_b",      "i1"),       # chart-B body index, [0..14]
    ("lon_a",       "f8"),       # chart-A body longitude (degrees)
    ("lon_b",       "f8"),       # chart-B body longitude (degrees)
    ("aspect_type", "i1"),       # canonical aspect index [0..13] OR -1 = "no aspect"
    ("orb",         "f4"),       # signed orb (aspect_angle - distance), NaN if aspect_type==-1
    ("applying",    "?"),        # True = applying (orb shrinking), False = separating or N/A
    ("orb_limit",   "f4"),       # max orb tolerance for this pair+aspect (post-factor); NaN if no aspect
])
```

### Pattern 2: Orb formula derivation

**What:** `orb_synastry(b1, b2, asp) = (orb[b1] + orb[b2]) / 2 * coef[asp] * SYNASTRY_FACTOR`

**SYNASTRY_FACTOR = 0.5** (cited from Astrodienst's documented practice).

**Cross-check:** with the values from `ketu/core.py:65`:

| Pair | Aspect | Natal orb | Synastry orb (×0.5) | astro.com / Liz Greene reference |
|------|--------|-----------|---------------------|-----------------------------------|
| Sun↔Moon | Conjunction (coef=1) | (12+12)/2*1 = **12°** | **6°** | ~5-6° (matches) |
| Sun↔Mars | Square (coef=0.5) | (12+8)/2*0.5 = **5°** | **2.5°** | ~3° (close — within tolerance) |
| Venus↔Saturn | Trine (coef=2/3) | (10+10)/2*0.667 = **6.67°** | **3.33°** | ~3-4° (matches) |
| Sun↔Sun (self-pair) | Conjunction | (12+12)/2*1 = **12°** | **6°** | Headline synastry — matches |
| Moon↔Moon (self-pair) | Conjunction | (12+12)/2*1 = **12°** | **6°** | Headline synastry — matches |

The 0.5 factor produces values comfortably inside the ROADMAP's "3-5° on majors" target band. SUN-SUN at 6° conjunction is wider than 5° but accurate to astro.com practice (luminaries widened uniformly). Document this explicitly in the orb-set docstring.

**ASC/MC orb convention:** since `bodies["orb"]` does not include ASC/MC (they are houses fields, not bodies), introduce a single named constant `ASC_MC_NATAL_ORB_DEG = 8.0` in `synastry/orbs.py`. Apply the formula with this value substituted when one or both partners are ASC/MC. Synastry ASC↔planet conjunction → `(12+8)/2 * 1 * 0.5 = 5°` (matches astrological practice).

### Pattern 3: Cross-product enumeration (NOT triu_indices)

**What:** Natal aspects use `np.triu_indices(13, k=1)` → 78 unique unordered pairs from a single chart, **excluding self-pairs**. Synastry uses the **full Cartesian product** `np.indices((N_a, N_b))` → N_a × N_b ordered pairs, **INCLUDING self-pairs** (Sun_A↔Sun_B etc.).

**Example:**

```python
# Source: ketu/aspects/calculator.py:187 — natal pattern (UPPER TRIANGLE ONLY)
i_indices, j_indices = np.triu_indices(n_bodies, k=1)
# 78 pairs from 13 bodies, no self-pairs

# NEW for synastry — FULL CROSS-PRODUCT
n_a, n_b = body_count_a, body_count_b   # 15 each (13 + ASC + MC)
i_idx, j_idx = np.indices((n_a, n_b))
i_flat = i_idx.ravel()                  # shape (n_a * n_b,) = (225,)
j_flat = j_idx.ravel()                  # shape (n_a * n_b,) = (225,)
# Self-pairs are at positions where i_flat[k] == j_flat[k]
# (Sun_A↔Sun_B at k=0, Moon_A↔Moon_B at k=16, etc.)
```

**Pitfall:** `combinations(13, 2) = 78`; `np.indices((15, 15)).reshape(2, -1).T.shape = (225, 2)`. Synastry produces ~3× more pairs than natal because (a) it's full cartesian and (b) ASC/MC are added.

### Pattern 4: applying/separating from natal speeds

**What:** Both charts are static; their natal speeds are stored in `CHART_DTYPE.body_speeds[i]`. The "relative motion" of pair `(body_a, body_b)` is `speed_a - speed_b` (degrees/day). The aspect is **applying** if the absolute distance to the exact aspect angle is shrinking under the relative motion.

**Why velocity-based, NOT always-False:**

1. The applying convention IS deterministic for a static pair — both speeds are fixed at birth.
2. The literature explicitly affirms this: "The natal planets are fixed for life, so the cross-aspects remain the same" (astrologyweekly.com forum, multiple practitioner sources).
3. Computing it adds 5 lines of NumPy and zero astronomical state.
4. Always-False misleads: callers will assume `applying=False` means "separating", not "MVP shortcut".

**Algorithm:**

```python
# Signed angular distance from exact aspect, in [-180, 180]
# (using the existing convention: orb = aspect_angle - distance)
delta = aspect_angle - distance     # already computed for orb field
relative_speed = speed_a - speed_b  # natal motion delta, deg/day
# Applying: |delta| is shrinking. d|delta|/dt = sign(delta) * d(delta)/dt.
# d(delta)/dt = -d(distance)/dt = -relative_speed (if a is faster, distance grows or shrinks linearly).
# Applying iff sign(delta) * (-relative_speed) < 0  iff sign(delta) * relative_speed > 0
applying = (np.sign(delta) * relative_speed) > 0
# Edge case: delta == 0 (exact aspect) → applying = False (already exact, neither applying nor separating)
# Retrograde bodies: speed_x is negative; the formula handles this naturally.
```

**Document loudly in docstring:** "applying/separating is computed from the **natal** speeds (`CHART_DTYPE.body_speeds`), not from current motion. This matches the standard synastry interpretation of cross-aspects between two static birth charts."

### Pattern 5: Filtered mode row ordering — canonical body-pair order

**What:** Filtered mode rows are ordered by `(body_a, body_b)` canonical body index ascending — NOT by `|orb|` ascending.

**Why:**

- **Predictable for ML/tests** — Kala (the downstream consumer) and the test oracle both want stable ordering. `(body_a, body_b)` canonical is deterministic; orb-ascending is fragile to ephemeris precision noise.
- Aligns with the existing project precedent: `calculate_aspects_vectorized` returns rows ordered by `(body1, body2)` upper-triangle canonical (`triu_indices` order), per the `i_asp` loop in `calculator.py:210-240`.
- Caller can always sort by orb post-hoc with one line: `result[np.argsort(np.abs(result["orb"]))]`.

**Counter-evidence:** astro.com renders synastry tables sorted by tightest orb. But that's a presentation choice, not a data-contract choice. Ketu is a calc engine, not a renderer — return canonical, let the renderer sort. The CLI dispatcher (`synastry_cmd.py`) can sort for display while the API stays canonical.

### Pattern 6: Dense-mode schema — NaN-fill, NOT masked array

**What:** Dense mode returns an `(N_a × N_b,)` 1-D array of `SYNASTRY_DTYPE` rows, with `aspect_type = -1` and `orb = NaN` for non-aspected pairs. Filtered mode returns a (K,) 1-D array with only the K rows where an aspect was detected.

**Why NaN-fill, not masked array:**

- `np.ma.MaskedArray` interop is patchy with structured dtypes (see e.g. NumPy `>=2.0` deprecation warnings on masked structured arrays).
- Phase 14 `CHART_DTYPE.aspect_matrix` already uses the `(-1, NaN)` sentinel pattern — synastry inherits the project's existing convention. Single-source-of-truth.
- Caller filtering is trivial: `dense[dense["aspect_type"] >= 0]` → equivalent to filtered mode.

### Anti-Patterns to Avoid

- **Using `triu_indices` for cross-product enumeration.** Natal pattern excludes self-pairs and de-duplicates unordered pairs. Synastry needs the FULL Cartesian product (self-pairs included, ordering matters: Sun_A↔Mars_B is distinct from Mars_A↔Sun_B). Use `np.indices` instead.
- **Hand-rolling a parallel orb table.** The CONTEXT.md decision is explicit: synastry orbs derive from the existing formula. Hand-rolling Robert Hand's or Liz Greene's specific tables breaks the single-source-of-truth.
- **Storing `is_day_chart` or other scalar in SYNASTRY_DTYPE.** Phase 14 D-12 explicitly rejected this for `CHART_DTYPE`. Synastry inherits the same rule — sect-related logic stays in `is_day_chart()`, not in synastry rows.
- **Recomputing positions inside `calculate_synastry`.** The whole point of `CHART_DTYPE` is that positions are pre-computed (Phase 14). Synastry consumes pre-resolved charts, never re-fetches ephemeris.
- **Synastry-vectorised batch over chart arrays in v1.2.** Out of scope per CONTEXT.md. The internal pair loop IS vectorised (NumPy ops over the 225-pair flat array), but the public surface accepts ONE `chart_a` + ONE `chart_b`. v1.3 can lift this — Phase 14 D-16 (the explicit S-loop trade-off) gives precedent.
- **CLI argument duplication of `houses` dispatcher patterns.** The locked decision says "CLI parity with `ketu houses`" — reuse `parse_iso_utc`, `emit_resolved_config`, `_format_cusp` style. Don't reinvent argparse types.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Aspect angle computation | Manual `((lon_b - lon_a) + 360) % 360` then test against each aspect angle | Adapt the existing `calculate_aspects_vectorized` orb-checking loop (calculator.py:210-240) over the cross-product index pair | The 6-aspect classical / 14-aspect extended scan logic + sign convention is already debugged and Kala-contract-stable. Recreating it leaks subtle sign bugs (`aspect_angle - distance` is already a non-obvious sign convention per Phase 14 D-05). |
| Aspect-set spec resolution | Custom string parser for `aspects=` | `ketu.aspects.presets.resolve_aspect_set` | Phase 9 deliverable — accepts `None|str|Sequence|np.ndarray`, returns a length-14 mask. Synastry passes its `aspects=` argument straight through. |
| ISO 8601 → JD conversion in CLI | Manual `datetime.fromisoformat` + JD math | `ketu.cli._dates.parse_iso_utc` | Phase 11 deliverable — already handles the Python 3.10 `Z`-suffix shim. Reuse for both `--date-a` and `--date-b`. |
| Chart computation in CLI | Manual ephemeris calls + ASC/MC math | `ketu.charts.compute_chart` | Phase 14 deliverable — single call returns `CHART_DTYPE` with all 13 bodies + ASC/MC. CLI flow: `compute_chart(jd_a, lat_a, lon_a)` × 2 → `calculate_synastry(chart_a, chart_b)`. |
| Tabular ASCII output formatting | `printf`-style format strings | Reuse `ketu.calculations.dd_to_dms` + the `_format_cusp` pattern from `houses_cmd.py:23` | Single source of truth for the `º DD°MM'SS"` format (Phase 11 BLOCKER 1 fix). The `--json` mode uses `json.dumps` over a list-of-dicts conversion of the structured array. |
| Resolved-config STDERR header | Manual STDERR print | `ketu.cli.formatters.emit_resolved_config` | Phase 11 deliverable — extend signature if needed (add an `orbs=` kwarg), don't duplicate. |
| Body-orb registry | Hardcoded dict | `ketu.core.bodies["orb"]` | Single source of truth (Abu Ma'shar / Al-Biruni convention, project-wide). |
| Aspect coefficient table | Hardcoded dict | `ketu.core.aspects["coef"]` | Single source of truth (canonical 14-row registry, Phase 9-frozen ordering). |

**Key insight:** Phase 16 is composition over invention. The astronomical primitives are all in place — the contribution is the new dtype, the orb convention, the cross-product enumeration, and the CLI surface. Resist the temptation to "improve" existing tables; the orb-formula reuse is locked by CONTEXT.md.

---

## Common Pitfalls

### Pitfall 1: `np.indices((n_a, n_b))` produces ORDERED pairs

**What goes wrong:** Naive thinking from natal aspects: "I have 13 bodies, I get C(13,2)=78 unordered pairs". For synastry, the (Sun_A, Mars_B) row is a DIFFERENT astrological aspect from (Mars_A, Sun_B) — the chart-of-origin matters. Both rows must appear in the result.

**Why it happens:** Programmers default to `combinations(bodies, 2)` or `triu_indices(k=1)` because that's the natal pattern. For cross-charts, this loses half the data.

**How to avoid:** Use `np.indices((n_a, n_b))` (or `np.meshgrid` with `indexing="ij"`). Sanity test: for 13 bodies on each side, the cross-product has 13×13 = 169 pairs (not 78).

**Warning signs:** Test count mismatch — if your test fixture expected ~80 records and you got 78, you're using the natal pattern.

### Pitfall 2: Self-pair orb when `bodies["orb"]` repeats

**What goes wrong:** Self-pair Sun_A↔Sun_B uses `(orb[Sun] + orb[Sun]) / 2 = orb[Sun]` — fine. But for Rahu/Ketu (`bodies["orb"][10] = 0`, `[11] = 0`), the self-pair orb is `(0+0)/2*coef*0.5 = 0`. Any aspect detection requires `|distance - aspect_angle| ≤ orb`, so a zero orb means **only EXACT-degree matches detect**. Practically, Rahu_A↔Rahu_B will never aspect except at distance 0.0000... .

**Why it happens:** v1.0 inherited zero-orb for Nodes (Rahu, Ketu) and Lilith from the body table — these are points, not bodies, and the convention is to require very tight orbs.

**How to avoid:** This is **correct astrological behavior** — document it. Add a test that Rahu_A↔Rahu_B with non-exact distance does NOT register an aspect. Optionally: synastry consumers who want Rahu/Ketu to aspect can pass a per-body override at the orb-set level (defer to v1.3 unless test feedback demands it).

**Warning signs:** "Why doesn't Lilith aspect Lilith?" support questions. Pre-empt with a docstring NOTE.

### Pitfall 3: ASC/MC NaN propagation at polar latitudes

**What goes wrong:** For polar charts (|lat| > ~66.5°), `compute_chart(polar_fallback="raise")` raises `HighLatitudeError`. With `polar_fallback="porphyry"`, the chart is computed but Porphyry cusps are substituted. The Phase 14 contract: ASC/MC themselves are computed via `compute_ascmc` which is closed-form via `arctan2` and **mathematically defined at every latitude** — so ASC/MC values are valid even at the pole.

**Why it happens:** A naive synastry impl might propagate NaN from polar cusps into ASC/MC contact aspects. But `chart["asc"]` is NEVER NaN (per Phase 14 D-15). Cusps may be NaN at extreme latitudes only if a registered system does not support them (e.g. Regiomontanus at lat 80°+).

**How to avoid:** Synastry uses ONLY `chart["asc"]` and `chart["mc"]` for the ASC/MC contact extension — NOT `chart["cusps"]`. ASC/MC are guaranteed defined by Phase 14 contract. Add a polar-couple oracle test (e.g. Reykjavik birth × Quito birth) to pin this contract.

**Warning signs:** `nan` appearing in synastry output for high-latitude inputs.

### Pitfall 4: Velocity sign convention for retrograde bodies

**What goes wrong:** `CHART_DTYPE.body_speeds[i]` is negative when retrograde (per Phase 14 docstring). The `applying = sign(delta) * relative_speed > 0` formula handles this naturally — but only if the relative_speed is computed as a SIGNED `speed_a - speed_b` (NOT `abs(speed_a) - abs(speed_b)`).

**Why it happens:** Engineers reach for `np.abs` to "normalize" speeds, breaking the applying/separating sign.

**How to avoid:** Keep the signed convention. Add a unit test: Mercury_A retrograde + Venus_B prograde → applying flag matches the natal-speed signed-delta calculation. Cite the test against a hand-computed example.

**Warning signs:** "All retrograde aspects show as separating" in test output.

### Pitfall 5: dense vs filtered count drift

**What goes wrong:** Caller mixes modes — runs `mode="dense"` then `mode="filtered"`, expects the filtered count to equal `(dense["aspect_type"] >= 0).sum()`. Drift can occur if the dense and filtered code paths share state (e.g. the orb cache).

**Why it happens:** Premature optimization — caching pair-orb computations across mode calls.

**How to avoid:** **Idempotency invariant**: `calculate_synastry(a, b, mode="dense")[result["aspect_type"] >= 0]` must equal `calculate_synastry(a, b, mode="filtered")` modulo row ordering AND have the same `(body_a, body_b, aspect_type, orb)` content. Pin this with a property test (random chart pair → both modes produce equivalent filtered subsets).

**Warning signs:** Property test failures.

### Pitfall 6: `bodies["orb"]` dtype is float32, applying multiplications can lose precision

**What goes wrong:** `bodies["orb"]` is `f4` (`ketu/core.py:81`). Multiplying by `coef` (`f4`) and then by `SYNASTRY_FACTOR` (Python float = `f8`) produces an `f8` upcast. Inconsistent dtype handling can break the `orb_limit` field type contract (`f4` per recommended schema).

**Why it happens:** NumPy auto-upcasts in mixed-precision arithmetic.

**How to avoid:** Explicit cast at the formula site: `np.asarray((orb_a + orb_b) / 2 * coef * SYNASTRY_FACTOR, dtype=np.float32)`. Add a dtype assertion in the test suite.

**Warning signs:** dtype mismatch in `assert_array_equal` or `dtype.itemsize` discrepancies.

### Pitfall 7: System case-sensitivity at the CLI boundary

**What goes wrong:** `--system Whole_Sign` should normalize to `whole_sign` per `ketu/houses/registry.py:73` (case-insensitive registration). But if `synastry_cmd.py` argparse uses `choices=sorted(_HOUSE_SYSTEMS.keys())`, it requires LOWERCASE input.

**Why it happens:** argparse's `choices=` is strict. The houses CLI dispatcher (Phase 11 `houses_cmd.py:43`) handles this by listing only lowercase keys, which works because `get_system` lowercases on lookup.

**How to avoid:** Mirror the `houses_cmd.py` convention — `choices=sorted(_HOUSE_SYSTEMS.keys())`, lowercase input expected. Document in `--help`.

**Warning signs:** argparse "invalid choice 'Placidus'" error from users typing capitalized names.

### Pitfall 8: --list-orbs collision with --list-house-systems / --list-aspect-sets

**What goes wrong:** Phase 11 introduced top-level `--list-aspect-sets` and `--list-house-systems` flags. CONTEXT.md asks for `--list-orbs` (mirroring the same pattern). If multiple `--list-*` flags are passed simultaneously, current dispatcher (`parser.py:174-181`) processes them in order with early returns — only the FIRST one wins.

**Why it happens:** argparse stores all flags as `args.list_*` booleans; the dispatcher's `if args.list_X: cmd_list_X(); return 0` ladder doesn't combine.

**How to avoid:** Mirror the existing pattern exactly — add `args.list_orbs` to the same ladder. Document the early-return behavior. (Or: refactor to handle multiple flags — out of scope unless test feedback demands it.)

**Warning signs:** User passes `--list-orbs --list-aspect-sets`, sees only one of the two.

---

## Code Examples

Verified patterns from existing Ketu sources.

### Example 1: SYNASTRY_DTYPE definition

```python
# Source pattern: ketu/cycles/calculator.py:37 (CYCLE_DTYPE precedent — record-style structured array)
# Source pattern: ketu/charts/core.py:85 (CHART_DTYPE — alternative axis-style; rejected here)

import numpy as np

#: Number of bodies in the synastry body axis: 13 canonical (per CHART_DTYPE) +
#: ASC + MC. Frozen at 15 for v1.2; v1.3 may add Vertex if Phase 17/18 demand it.
SYNASTRY_BODY_COUNT: int = 15

#: Structured dtype for ONE synastry aspect record.
#:
#: Fields (8 total, ordered as identity → values → metadata):
#:     - ``body_a`` (i1): chart-A body index, [0..14] (0..12 = ketu.core.bodies, 13 = ASC, 14 = MC).
#:     - ``body_b`` (i1): chart-B body index, [0..14].
#:     - ``lon_a`` (f8): chart-A body longitude (degrees [0, 360)).
#:     - ``lon_b`` (f8): chart-B body longitude (degrees [0, 360)).
#:     - ``aspect_type`` (i1): canonical aspect index [0..13] per ketu.core.aspects, OR
#:           -1 for "no aspect" (dense mode only).
#:     - ``orb`` (f4): signed orb in degrees, ``aspect_angle - distance``;
#:           NaN if ``aspect_type == -1``. Inherits Phase 14 sign convention.
#:     - ``applying`` (?): True when the aspect is applying under natal-speed convention,
#:           False when separating. Always False when aspect_type == -1.
#:     - ``orb_limit`` (f4): tolerance threshold used (post-factor synastry orb);
#:           NaN if aspect_type == -1.
SYNASTRY_DTYPE: np.dtype = np.dtype([
    ("body_a",      "i1"),
    ("body_b",      "i1"),
    ("lon_a",       "f8"),
    ("lon_b",       "f8"),
    ("aspect_type", "i1"),
    ("orb",         "f4"),
    ("applying",    "?"),
    ("orb_limit",   "f4"),
])
```

### Example 2: Orb formula + preset resolver

```python
# Source pattern: ketu/aspects/presets.py:91-156 (resolve_aspect_set + _PRESET_BY_NAME)
# Source formula: ketu/aspects/calculator.py:32 (get_orb)

from __future__ import annotations
from typing import Union
import numpy as np

from ketu.core import bodies as _BODIES, aspects as _ASPECTS

#: Multiplicative factor applied to the natal orb formula for synastry.
#: Cited from Astrodienst (astro.com) FAQ "Partner horoscopes": "for drawing
#: aspects in a synastry chart, half the orb of the natal chart is used."
SYNASTRY_FACTOR: float = 0.5

#: Natal orb width assigned to ASC and MC for synastry. Not present in
#: ketu.core.bodies (which lists only the 13 ephemeris bodies). Set to 8°
#: matching the convention for Mercury / Mars / Uranus / Neptune (mid-tier).
ASC_MC_NATAL_ORB_DEG: float = 8.0

# Extended body-orb table for synastry (15 entries: 13 canonical + ASC + MC).
_BODY_ORBS_15: np.ndarray = np.concatenate([
    _BODIES["orb"].astype(np.float32),         # 13 canonical
    np.array([ASC_MC_NATAL_ORB_DEG] * 2, dtype=np.float32),  # ASC, MC
])  # shape (15,)

OrbSetSpec = Union[None, str]


def synastry_orb_limit(b1: int, b2: int, asp: int, factor: float = SYNASTRY_FACTOR) -> float:
    """Compute the synastry orb tolerance for a body pair + aspect.

    Reuses the natal formula ``(orb_a + orb_b) / 2 * coef`` and tightens by ``factor``.

    Parameters
    ----------
    b1, b2 : int
        Body indices in the 15-body synastry axis.
    asp : int
        Canonical aspect index [0..13].
    factor : float, default SYNASTRY_FACTOR (= 0.5)
        Multiplicative tightening factor.

    Returns
    -------
    float
        Orb tolerance in degrees (always positive; distance from exact aspect angle).
    """
    return float(
        (_BODY_ORBS_15[b1] + _BODY_ORBS_15[b2]) / 2.0
        * float(_ASPECTS["coef"][asp])
        * factor
    )


_PRESETS_BY_NAME: dict[str, float] = {
    "synastry": SYNASTRY_FACTOR,   # 0.5
    "classical": 1.0,              # full natal orb (caller comparison view)
}


def resolve_orb_set(spec: OrbSetSpec) -> float:
    """Resolve the ``orbs=`` parameter to a multiplicative factor.

    Parameters
    ----------
    spec : None or str
        - ``None`` or ``"synastry"`` -> SYNASTRY_FACTOR (0.5)
        - ``"classical"`` -> 1.0 (use natal orbs unchanged; for expert views).

    Returns
    -------
    float
        Multiplicative factor applied to the natal formula.

    Raises
    ------
    ValueError
        If ``spec`` is an unknown preset name.
    """
    if spec is None:
        return _PRESETS_BY_NAME["synastry"]
    if isinstance(spec, str):
        key = spec.lower()
        if key in _PRESETS_BY_NAME:
            return _PRESETS_BY_NAME[key]
        valid = ", ".join(sorted(_PRESETS_BY_NAME))
        raise ValueError(f"unknown orb preset {spec!r}. Valid: {valid}")
    raise ValueError(f"unsupported orbs= type: {type(spec).__name__}")
```

### Example 3: calculate_synastry — composition core

```python
# Source pattern: ketu/charts/api.py (compute_chart)
# Source pattern: ketu/aspects/calculator.py:135-249 (calculate_aspects_vectorized)

from __future__ import annotations
from typing import Literal
import numpy as np

from ketu.aspects.presets import resolve_aspect_set, AspectSetSpec
from ketu.calculations import distance
from ketu.core import aspects as _ASPECTS

from .core import SYNASTRY_DTYPE, SYNASTRY_BODY_COUNT
from .orbs import _BODY_ORBS_15, resolve_orb_set, OrbSetSpec


def _extend_body_data(chart: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Extend a CHART_DTYPE record's 13-body axis to a 15-body synastry axis (incl. ASC, MC).

    Returns
    -------
    lons : np.ndarray, shape (15,)
        Longitudes of 13 canonical bodies + ASC + MC.
    speeds : np.ndarray, shape (15,)
        Natal speeds of 13 canonical bodies + 0.0 + 0.0 for ASC/MC (ASC/MC have
        no per-day speed in the static natal-chart sense; for the applying
        calculation, this means ASC/MC contacts are always classified as
        non-applying — which is consistent with the static-chart convention).
    """
    lons = np.concatenate([
        np.asarray(chart["body_lons"], dtype=np.float64),
        np.asarray([float(chart["asc"]), float(chart["mc"])], dtype=np.float64),
    ])
    speeds = np.concatenate([
        np.asarray(chart["body_speeds"], dtype=np.float64),
        np.zeros(2, dtype=np.float64),
    ])
    return lons, speeds


def calculate_synastry(
    chart_a: np.ndarray,
    chart_b: np.ndarray,
    aspects: AspectSetSpec = "classical",
    orbs: OrbSetSpec = "synastry",
    mode: Literal["dense", "filtered"] = "filtered",
) -> np.ndarray:
    """Compute aspects between two natal charts.

    Returns a structured array of SYNASTRY_DTYPE rows. In ``mode="filtered"``,
    only aspected pairs appear. In ``mode="dense"``, all 15x15 = 225 pairs
    appear, with ``aspect_type=-1`` and ``orb=NaN`` for non-aspected pairs.

    Self-pairs are INCLUDED (Sun_A↔Sun_B, Moon_A↔Moon_B, etc.).

    The applying field is computed from natal speeds (CHART_DTYPE.body_speeds)
    per the static-chart convention; both partner charts are fixed and the
    relative motion is `speed_a - speed_b`.

    Parameters
    ----------
    chart_a, chart_b : np.ndarray
        CHART_DTYPE scalar records (Phase 14).
    aspects : AspectSetSpec, default "classical"
        Aspect-set spec, passed through resolve_aspect_set. Default classical
        (5 majors), aligned with package-wide default.
    orbs : OrbSetSpec, default "synastry"
        Orb tightening preset. ``"synastry"`` (default) applies factor 0.5 to
        the natal formula. ``"classical"`` uses natal orbs unchanged (expert view).
    mode : {"dense", "filtered"}, default "filtered"
        Output shape. Filtered = only aspected rows; dense = all 225 rows.

    Returns
    -------
    np.ndarray
        Structured array of SYNASTRY_DTYPE rows.

    Notes
    -----
    UTC ONLY. Both charts must have been computed with UTC Julian Dates.
    Time-zone conversion is the caller's responsibility.
    """
    mask = resolve_aspect_set(aspects)                   # length-14 bool
    factor = resolve_orb_set(orbs)                       # float scalar
    selected_indices = np.where(mask)[0]                 # canonical aspect indices

    lons_a, speeds_a = _extend_body_data(chart_a)        # (15,)
    lons_b, speeds_b = _extend_body_data(chart_b)        # (15,)

    # Cross-product enumeration — FULL Cartesian (NOT triu_indices).
    n = SYNASTRY_BODY_COUNT
    i_idx, j_idx = np.indices((n, n))
    i_flat = i_idx.ravel()                               # shape (225,)
    j_flat = j_idx.ravel()                               # shape (225,)

    pos_a = lons_a[i_flat]
    pos_b = lons_b[j_flat]
    speed_a = speeds_a[i_flat]
    speed_b = speeds_b[j_flat]
    dist = distance(pos_a, pos_b)                        # shape (225,) — uses existing helper

    # Initialize all-pairs result (dense baseline).
    out = np.empty(n * n, dtype=SYNASTRY_DTYPE)
    out["body_a"] = i_flat.astype(np.int8)
    out["body_b"] = j_flat.astype(np.int8)
    out["lon_a"] = pos_a
    out["lon_b"] = pos_b
    out["aspect_type"] = -1
    out["orb"] = np.nan
    out["applying"] = False
    out["orb_limit"] = np.nan

    # First-aspect-wins matching (mirrors calculator.py:204 matched_pairs convention).
    matched = np.zeros(n * n, dtype=bool)

    for i_asp in selected_indices:
        i_asp_int = int(i_asp)
        ang = float(_ASPECTS["angle"][i_asp_int])
        coef = float(_ASPECTS["coef"][i_asp_int])

        # Per-pair orb limit (vectorised), with synastry factor.
        orbs_pair = (_BODY_ORBS_15[i_flat] + _BODY_ORBS_15[j_flat]) / 2.0 * coef * factor

        if i_asp_int == 0:
            in_orb = (dist <= orbs_pair) & (~matched)
            delta = -dist                                # distance from exact (=0)
        else:
            in_orb = (np.abs(dist - ang) <= orbs_pair) & (~matched)
            delta = ang - dist                           # signed orb (Phase 14 convention)

        if not np.any(in_orb):
            continue

        # Applying: sign(delta) * relative_speed > 0.
        rel_speed = speed_a - speed_b
        applying = (np.sign(delta) * rel_speed) > 0

        out["aspect_type"][in_orb] = i_asp_int
        out["orb"][in_orb] = delta[in_orb].astype(np.float32)
        out["applying"][in_orb] = applying[in_orb]
        out["orb_limit"][in_orb] = orbs_pair[in_orb].astype(np.float32)
        matched |= in_orb

    if mode == "dense":
        return out
    if mode == "filtered":
        return out[out["aspect_type"] >= 0]
    raise ValueError(f"unknown mode {mode!r}; expected 'dense' or 'filtered'")
```

### Example 4: CLI dispatcher (mirrors houses_cmd.py)

```python
# Source pattern: ketu/cli/houses_cmd.py
# Source pattern: ketu/cli/aspects_cmd.py

from __future__ import annotations
import argparse
import json

import numpy as np

from ketu.charts import compute_chart
from ketu.synastry import calculate_synastry, SYNASTRY_DTYPE
from ketu.calculations import dd_to_dms
from ketu.core import bodies, aspects as _ASPECTS, signs

from ._dates import parse_iso_utc
from .formatters import emit_resolved_config


def cmd_synastry(args: argparse.Namespace) -> int:
    """Compute synastry between two charts and print as table or JSON."""
    emit_resolved_config(mask=None, preset_name=None, house_system=args.system)

    jd_a = parse_iso_utc(args.date_a)
    jd_b = parse_iso_utc(args.date_b)
    chart_a = compute_chart(jd_a, args.lat_a, args.lon_a, system=args.system,
                            polar_fallback=args.polar_fallback)
    chart_b = compute_chart(jd_b, args.lat_b, args.lon_b, system=args.system,
                            polar_fallback=args.polar_fallback)
    result = calculate_synastry(chart_a, chart_b, mode=args.mode)

    if args.json:
        out = [{k: float(r[k]) if isinstance(r[k], (np.floating, np.integer))
                else bool(r[k]) if isinstance(r[k], np.bool_) else r[k]
                for k in result.dtype.names} for r in result]
        print(json.dumps(out, indent=2))
        return 0

    # Aligned ASCII table (mirror houses_cmd.py:_format_cusp style).
    print()
    print(f"------- Synastry ({args.mode}, {len(result)} rows) -------")
    print(f"{'Body A':<10} {'Body B':<10} {'Aspect':<14} {'Orb':>8} {'Applying':>10}")
    for row in result:
        if row["aspect_type"] < 0:
            continue
        name_a = _body_label(int(row["body_a"]))
        name_b = _body_label(int(row["body_b"]))
        asp_name = _ASPECTS["name"][int(row["aspect_type"])].decode()
        print(f"{name_a:<10} {name_b:<10} {asp_name:<14} "
              f"{float(row['orb']):>+8.3f} {str(bool(row['applying'])):>10}")
    return 0


def _body_label(idx: int) -> str:
    """Map a 15-body synastry axis index to a human-readable label."""
    if 0 <= idx <= 12:
        return bodies["name"][idx].decode()
    if idx == 13:
        return "ASC"
    if idx == 14:
        return "MC"
    raise ValueError(f"invalid body index {idx}")
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Per-body hardcoded orb tables (e.g. Robert Hand "Synastry & Composite Charts") | Derived multiplicative factor on top of natal formula | astro.com (Liz Greene) ca. 2010s | Single source of truth; orb formula stays project-wide; synastry just adjusts the factor. |
| Synastry as an N×N flat 2-D matrix output | Record-style structured array per cross-pair | Modern ML pipelines (Kala-style consumers) | Records compose better with `pandas`/Arrow/Parquet; matrices remain available via dense mode + reshape. |
| `applying` undefined for synastry (cross-static charts) | Velocity-based using natal speeds (the only deterministic option) | Practitioner consensus | Aligns with "natal cross-aspects are fixed" while still labeling the dynamic tendency. |
| Composite chart = synastry replacement | Composite is a separate phase (Phase 17, future) | Modern relational astrology (Hand, Tyl) | Composite and synastry serve different purposes — synastry is "how do you affect each other?", composite is "what is the relationship itself?". |

**Deprecated/outdated:**

- Manually summing wing-orbs (e.g. "Sun gives 8°, Moon gives 8°, total = 16°"): use the average-then-coefficient formula consistently.
- Synastry orbs sourced from a printed reference table only: cite the formula derivation explicitly so the orb is reproducible.

---

## Open Questions

1. **Should `chart["cusps"]` participate in synastry?**
   - What we know: ASC and MC contacts are canonical synastry. House cusps 2-12 contacts are NOT canonical (cusps are house boundaries, not bodies).
   - What's unclear: Some practitioners aspect Vertex (cusp 8 in some conventions, but stored separately as `chart["vertex"]`) to natal planets in synastry.
   - Recommendation: **DO NOT** include cusps 1-12 or Vertex in v1.2 synastry. ASC + MC only (15-body axis). Add Vertex in v1.3 if Phase 17 (composite) demands it. Document loudly in the docstring that `chart["cusps"]` is not consulted.

2. **Does the user-override surface for `orbs=` accept dicts (e.g. `orbs={"factor": 0.4}`)?**
   - What we know: CONTEXT.md says "user override → Claude's Discretion".
   - What's unclear: How aggressive an override surface to expose in v1.2.
   - Recommendation: **MVP: name-only string preset** (`orbs="synastry"` or `orbs="classical"`). DO NOT accept dict / callable / Sequence in v1.2. Defer the rich override to v1.3 when (a) we have Composite (Phase 17) precedent and (b) test feedback identifies real callers needing it. The single-source-of-truth `_PRESETS_BY_NAME` map can be extended in-place.

3. **Should `aspects="classical"` be the default for synastry, or `aspects="extended"`?**
   - What we know: Natal default (Phase 9) is `"classical"` (5 majors). CLASSICAL covers conjunction/sextile/square/trine/opposition.
   - What's unclear: Synastry traditionally weighs minor aspects (semi-sextile, quincunx, sesquare) more heavily because compatibility nuance lives in those.
   - Recommendation: **Default to `"classical"`** — match the package-wide convention (less surprise for callers using `compute_chart` defaults). Document that practitioners often pass `"traditional"` (CLASSICAL + semi-sextile + quincunx) for relational work. Test fixtures use `"classical"` to keep the oracle simple.

4. **Oracle test source: Astro.com vs Solar Fire vs hand calculation?**
   - What we know: 3 oracle pairs needed (ROADMAP success criterion #4); Solar Fire is a paid commercial product; Astro.com has anti-bot protection on FAQ pages but published synastry charts are accessible through the chart-display URL.
   - What's unclear: Which source is authoritative when they disagree (they will disagree at the 0.1° level due to differing ephemeris; that's acceptable — orb tolerance hides it).
   - Recommendation: **Primary oracle = Astro.com** (free, widely cited, AA-rated couples available via AstroDataBank). **Cross-check oracle = Solar Fire screenshots** if the test fixture builder has access (not blocking — Astro.com alone is sufficient if the fixture is committed to the repo with a comment citing the chart URL). Tolerance: max orb delta ≤ 0.1° on majors.

5. **CLI input args design: suffixed (`--lat-a/--lat-b`) vs file (`--chart-a alice.json`) vs positional?**
   - What we know: CONTEXT.md gives discretion. Existing CLI uses suffixed-style for single chart (`--lat`, `--lon`).
   - What's unclear: File-based input (`--chart-a alice.yaml`) is more ergonomic but introduces a chart serialization format Ketu doesn't have yet.
   - Recommendation: **MVP: suffixed `--date-a/--lat-a/--lon-a` + `--date-b/--lat-b/--lon-b`** (mirror existing patterns). DO NOT introduce a chart-file format in v1.2 — that's a Phase 17/18 deliverable (cross-cutting concern across composite, return). Suffixed args with shell heredocs / `xargs` is the v1.2 escape hatch.

---

## Test Strategy Outline

### Unit tests (`tests/synastry/`)

- `test_dtype.py` — SYNASTRY_DTYPE shape, field names, dtype invariants. Pin SYNASTRY_BODY_COUNT == 15.
- `test_orbs.py` — orb formula values for 4-5 canonical pairs (Sun-Sun, Moon-Moon, Venus-Mars, ASC-Sun, Rahu-Rahu zero-orb edge case). `resolve_orb_set` accepts `"synastry"`, `"classical"`, None; rejects unknown strings with helpful message.
- `test_calculate_synastry.py` — Filter mode with 0/1/many aspects, dense mode shape == (225,), self-pairs present in dense, cross-product NOT triu, applying/separating signs correct, retrograde-body applying flag, polar-fallback ASC contact at high latitude, dtype roundtrip.
- `test_applying.py` — Hand-validated applying flag against known synastry pair (e.g. fast Moon approaching slow Saturn in chart B → applying=True from natal motion).
- `test_modes_idempotent.py` — Property: `dense[mask >= 0]` == `filtered` modulo ordering for random chart pairs.

### Oracle tests (`tests/synastry/test_oracle.py`)

- 3 hand-validated couples with Rodden-rated AA/A birth data:
  1. **Marie Curie × Pierre Curie** (Marie AA-rated per Astro-Databank; Pierre's birth time imprecise — fall back to documented but lower rating; document the rating).
  2. **Princess Diana × Prince Charles** (both well-documented, AA/A rated).
  3. **John Lennon × Yoko Ono** (Lennon = AA; Ono = AA per Rodden; well-cited synastry pair in literature).

  Each fixture stored as `tests/synastry/fixtures/oracle_{slug}.json` with structure:

  ```json
  {
    "name": "lennon_ono",
    "rodden_a": "AA", "rodden_b": "AA",
    "chart_a": {"jd": ..., "lat": ..., "lon": ...},
    "chart_b": {"jd": ..., "lat": ..., "lon": ...},
    "expected_aspects": [
      {"body_a": "Sun", "body_b": "Moon", "aspect": "Conjunction", "orb_max": 5.0},
      ...
    ],
    "source_citation": "Astro-Databank URL ..."
  }
  ```

  Test asserts: each expected aspect appears in `calculate_synastry(...)` filtered output with `|orb| <= orb_max`. Max orb delta per couple is asserted ≤ 0.1° on majors (cite Phase 14 oracle precedent: tests/houses/fixtures/reference_charts.json tolerance).

### Property-based tests (optional, hypothesis)

- Random chart pair → `len(dense) == 225` always.
- Random chart pair → `len(filtered) <= 225` always.
- Random chart pair, fixed seed → `calculate_synastry(a, b)` == `calculate_synastry(a, b)` (idempotency / no hidden state).
- For ANY chart `a`: `calculate_synastry(a, a, mode="dense")` produces the diagonal (Sun_A↔Sun_A) at orb=0 conjunction (sanity: a chart synastry'd with itself shows all self-pairs at exact orb).

### CLI tests (`tests/cli/test_synastry_cmd.py`)

- argparse: `--mode dense|filtered`, both `--date-a/--date-b` required, `--system` from registry, `--polar-fallback` from {raise, porphyry}, `--json` toggle, `--list-orbs` short-circuits.
- Aligned table output byte-stable on a fixed couple fixture (JSON-fixture-driven; mirror `tests/cli/test_v1_1_reference_byte_stable.py`).
- `--json` output shape: list-of-dicts, each dict has all SYNASTRY_DTYPE field names, dtype-converted to JSON-friendly Python types.
- `--list-orbs` prints the `_PRESETS_BY_NAME` table with one preset per line + the formula derivation block.

### Coverage target

≥95% on `ketu/synastry/` (per ROADMAP / Phase 13 doc-gates contract). Reachable: the module is < 300 LoC; the two non-trivial branches are dense-vs-filtered and applying-sign which are both unit-testable. The hardest cell to cover will be the `aspect_type=-1` early-skip in dense iteration — covered by the property test "random chart pair has < 225 aspected pairs".

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Orb factor 0.5 produces fewer aspects than astro.com on test couples | MEDIUM | LOW | Tolerance band: assert `|orb_synastry - orb_astro_com| <= 0.5°`. If consistently off, add a `"liz_greene"` preset with per-aspect coefficients (deferred to v1.3). |
| `bodies["orb"]==0` for Rahu/Ketu/Lilith makes self-pairs invisible | HIGH (will surprise users) | LOW (documented behavior) | Loud docstring NOTE + dedicated unit test pinning the behavior. v1.3 escape hatch: per-body override map. |
| Polar latitudes break ASC-MC contacts | LOW (Phase 14 D-15 solved this) | MEDIUM | Dedicated polar-couple oracle test (Reykjavik × Quito or similar). Pin that ASC/MC are never NaN. |
| Cross-product enumeration with full body axes performance-fail at high N | LOW (15×15=225 pairs is trivial) | LOW | Performance budget: synastry call < 5ms for one couple (CHART_DTYPE pre-computed). Add benchmark in `tests/synastry/benchmark_synastry.py`. |
| `applying` field semantically misleading at edge cases (delta=0, ASC/MC speed=0) | MEDIUM | LOW | Loud docstring: "applying=False when delta=0 OR speeds_a == speeds_b OR either body is ASC/MC". Pin all three edges in unit tests. |
| CLI `--list-orbs` collides with `--list-aspect-sets` semantically (both list "aspect-related stuff") | LOW | LOW | Clear help text differentiating the two. Document collision behavior (early-return ladder). |
| Astro.com FAQ anti-bot prevents auto-validation in tests | HIGH (already observed) | LOW | Don't auto-fetch in tests. Capture expected aspects manually once at fixture-build time, store in JSON, cite the source URL. Tests use ONLY local JSON. |
| Future `aspects=` mask config drift with synastry orbs (cache key issue from Phase 9 RESEARCH §Pitfall 4) | LOW (no cache today) | MEDIUM | Forward-looking: if Phase 17 adds caching, cache key MUST include `(aspect_mask.tobytes(), orb_factor)`. Document in `synastry/__init__.py` docstring. |
| Vectorisation across chart-pairs creep into v1.2 scope | MEDIUM | HIGH (scope blow-up) | Hard "scalar pair only" boundary in `calculate_synastry` signature. v1.3 issue tracking the lift. |
| SYNASTRY_DTYPE schema churn before v1.2 freeze | MEDIUM | HIGH (consumer break) | Lock the 8-field schema in `core.py` early; never reorder fields between waves. Document in `core.py` module docstring "Why 8 fields, not 5 or 12". |

---

## Sources

### Primary (HIGH confidence)

- **`ketu/aspects/calculator.py:32`** — `get_orb` formula (project source code; AUTHORITATIVE per CONTEXT.md).
- **`ketu/core.py:65`** — `bodies` structured array with orb widths (project source code; AUTHORITATIVE).
- **`ketu/core.py:86`** — `aspects` structured array with coefficients (project source code; AUTHORITATIVE).
- **`ketu/charts/core.py:85`** — `CHART_DTYPE` definition (project source code; Phase 14 frozen contract).
- **`ketu/charts/api.py:193`** — `compute_chart` signature and behavior (project source code; Phase 14).
- **`ketu/aspects/presets.py:91-156`** — `resolve_aspect_set` resolver pattern (project source code; Phase 9).
- **`ketu/houses/registry.py:44`** — `register` decorator pattern (project source code; reference for orb-set resolver shape).
- **`ketu/cli/houses_cmd.py:43`** — `cmd_houses` dispatcher pattern (project source code; reference for `cmd_synastry`).
- **`ketu/cli/parser.py`** — argparse subparser pattern with `--list-*` introspection (project source code; reference for `--list-orbs`).
- **`ketu/cli/_dates.py:21`** — `parse_iso_utc` ISO-8601 parser (project source code; reused for `--date-a/--date-b`).
- **`ketu/cycles/calculator.py:37`** — `CYCLE_DTYPE` record-style precedent (project source code; reference shape for `SYNASTRY_DTYPE`).

### Secondary (MEDIUM confidence — cross-verified)

- **Astrodienst (astro.com) Partner Horoscopes FAQ** — "for drawing aspects in a synastry chart, half the orb of the natal chart is used" (cited via WebSearch; primary URL `https://www.astro.com/faq/fq_fh_partner_e.htm` returns anti-bot challenge but quote is widely echoed by independent sources).
- **The Astrology Place (theastrologyplacemembership.com)** — "much smaller orbs are used in forecasting and synastry" + Liz Greene 10° natal / 6° sextile convention.
- **Truth in Aspect Astrology / Facebook** — practitioner orb table for synastry (5-10° on conjunctions luminaries / 8° squares).
- **AstrologyWeekly forum** — confirms "natal planets are fixed for life, so the cross-aspects remain the same" (validates the natal-speed `applying` convention).
- **Lois Rodden's Rodden Rating system** — AA = birth certificate (highest reliability); used to filter oracle test couples.
- **Astro-Databank entries** — Marie Curie (AA per Baptism Certificate at noon), Yoko Ono (AA per Rodden), John Lennon (A, lower rating, contested), Princess Diana (AA per published time 19:45 BST), Brad Pitt (A).

### Tertiary (LOW confidence — flagged for validation at fixture-build time)

- **John Lennon birth time** — A-rated only; some sources flag it as "many astrologers' guess" for the rising sign. **Recommendation:** still usable as oracle if test asserts only Sun/Moon/Mars positions (not ASC/MC). Document the rating in the fixture.
- **Solar Fire default synastry orbs** — example "Conjunctions/Oppositions/Squares 5°, Trines/Sextiles 3°" cited in Solunars forum but not from Solar Fire's official docs. **Recommendation:** use Astro.com as the primary cross-check; treat Solar Fire as a secondary if available.
- **Specific Liz Greene orb table** — 10° natal, 6° sextile, halved for synastry → 5°/3° matches the band but the exact source (book / chapter) was not located in this research pass.

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — 100% reuse of v1.2 primitives (CHART_DTYPE, resolve_aspect_set, bodies, aspects, distance).
- Architecture (subpackage layout, dtype shape, cross-product loop): HIGH — direct mirror of `ketu/charts/` and `ketu/houses/` precedents.
- Orb convention (factor 0.5): MEDIUM-HIGH — astro.com cited; Liz Greene-style per-aspect table is a v1.3 evolution path.
- Applying field semantics: MEDIUM-HIGH — practitioner consensus + 5 lines of NumPy; document loudly in docstring.
- ASC/MC orb default (8°): MEDIUM — uses mid-tier convention (Mercury/Mars range); could also defensibly be 5° or 6°. Pin in unit test against fixture.
- Oracle couples: MEDIUM — Astro-Databank rating system is well-documented; auto-fetch is impossible (anti-bot); manual fixture entry is the path.
- CLI design: HIGH — suffixed args mirror existing patterns exactly.
- Common pitfalls: HIGH — drawn from Phase 9 / 11 / 14 RESEARCH.md predecessors and direct codebase inspection.

**Research date:** 2026-05-10
**Valid until:** 2026-08-10 (30 days for ephemeris-stable domain; the project's astronomical primitives are slow-moving). Re-research if astro.com publishes a new synastry-orbs reference or if Phase 17 (composite) lands first and changes the orb-preset surface.
