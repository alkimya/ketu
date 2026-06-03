# Phase 30: Chiron Range 1900–2100 - Research

**Researched:** 2026-06-03
**Domain:** Chebyshev ephemeris extension — data regeneration + accuracy spike + regression re-pinning
**Confidence:** HIGH (all findings from direct source inspection)

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Stratégie de repli du spike (si gate < 0.01° échoue sur les ailes 1900–1950)**
- Levier #1 = monter `degree` 10→12 (premier essai si gate casse sur les ailes près du périhélie).
- Paramètres UNIFORMES sur toute la plage 1900–2100 — un seul `degree`, un seul `seg_len`. PAS de paramètres adaptatifs par région (rejetés : complexifient générateur + évaluateur, risquent le fix `actual_len`).
- Borne basse 1900 ferme ; remonter à ~1905 = tout dernier recours documenté, seulement après accord utilisateur explicite (Stop + demander).
- Pas de contrainte stricte sur la taille du `.npz` — précision prime. ~2-3× la taille actuelle acceptable.

**Bornes & comportement hors-plage**
- Bornes calendaires : `jd_start = JD(1900-01-01 UTC)`, `jd_end = JD(2100-01-01 UTC)`.
- Comportement hors-plage actuel CONSERVÉ — Phase 30 = données, pas sémantique d'erreur. Le planner doit d'abord INSPECTER et RAPPORTER le comportement actuel de `chiron.py` hors-plage (erreur ? clamp ? NaN ?) ; on le préserve tel quel.
- Tests aux bornes ET juste dehors : points pinnés à 1900.0 et 2100.0 (dedans, valides, < 0.01°) + un point juste avant 1900 et juste après 2100 (vérifie comportement hors-plage inchangé).
- Périhélie ~1895–96 (sous la borne) : le spike doit valider densément le bord 1900–1905 sous gradient — échantillonnage dense de 1900–1910, pas de moyenne qui masque un pic local. Worst-case prioritaire.

**Stratégie de re-pinning des tests**
- Source de vérité = Swiss Ephemeris (pyswisseph build/test-only). Longitudes générées par pyswisseph puis pinnées en dur.
- Garder les refs existants 1950–2050 + AJOUTER les ailes (non-régression du centre).
- Densité minimale (CHIR-11) : au moins 1 ref pré-1950 (ex. 1920) + 1 ref post-2050 (ex. 2080). Au moins un point dans la zone à fort gradient 1900–1910 si le risque s'y matérialise.
- Gate < 0.01° UNIFORME partout.

**Traçabilité du spike**
- Consigner dans le decision log STATE/PROJECT (style `[Phase 23-01]`, `[Phase 24-04]`) : max|Δλ| mesuré, params finaux (`seg`/`degree`), décision (degree 10 ou 12).
- Spike ÉPHÉMÈRE — rien committé sous `tools/`/`ketu/`/`tests/`/`pyproject` (précédent Phase 23 « spike-only »). On mesure, on consigne le verdict, on jette le script de mesure.
- Check pré-vol build EXPLICITE en première étape du spike : `pyswisseph` importe + `seas_18.se1` trouvable (couvre 1800–2400) ; échouer tôt avec message clair sinon.
- Échec total → STOP + demander : si même `degree=12` (tout levier raisonnable à params uniformes) ne tient pas < 0.01° à 1900.0, le workflow s'arrête et demande à l'utilisateur avant de remonter la borne (~1905 = modif de requirement).

### Claude's Discretion
- Valeur exacte de `seg_len` si réduction nécessaire (mais uniforme, jamais adaptatif).
- Choix exact des dates de référence pré-1950/post-2050.
- Détails d'implémentation du script de spike éphémère.
- Mécanique de génération des longitudes-oracle Swiss Ephemeris pour le pinning.

### Deferred Ideas (OUT OF SCOPE)
- Documentation de la plage Chiron 1900–2100 (Phase 31, DOC-16).
- Extension au-delà de 1900–2100. Modif sémantique d'erreur hors-plage (ValueError explicite).
</user_constraints>

---

## Summary

Phase 30 is a data extension phase: the generator script already has all the machinery needed, and only needs its hardcoded range constants updated. The generator (`tools/gen_chiron_coeffs.py`) currently hardcodes `1950`/`2050` in `setup_oracle()` via `swe.julday(1950, 1, 1, 0.0)` / `swe.julday(2050, 1, 1, 0.0)` (lines 110–111), and nowhere else in the file — there is no second hardcoded constant. The `_DEGREE` and `_SEG_LEN` constants are at lines 55–56 and are trivially changeable for the spike. The ephemeris path defaults to a hardcoded local path (`_DEFAULT_EPHE_PATH`, line 76) but is also readable from `SE_EPHE_PATH` env var; `seas_18.se1` is confirmed accessible at that path and covers 1800–2400 (Chiron at 1900 and 2100 returns `retflag=260`, Moshier fallback, acceptable).

The runtime evaluator `ketu/ephemeris/chiron.py` has a **clamp-based** out-of-range behavior (not an error, not NaN): JDs before `jd_start` clamp `si=0`, JDs after `jd_end` clamp `si=n_segs-1`, then `t` is also clipped to `[-1, 1]`. This behavior is exercised by existing tests (`test_clamp_below_range`, `test_clamp_above_range`) that reference the data relative to `seg_starts[0]` and `seg_starts[-1]`, so they survive the `.npz` regeneration without code change — but the docstring texts mentioning "1950"/"2050" will need updating.

The regression test file (`tests/ephemeris/test_chiron_regression.py`) has 7 pinned reference points spanning 1950–2050. The extension adds new entries before 1950 and after 2050 using the same pattern: hardcoded `(jd, lon_degrees)` tuples in `_CHIRON_REFS`, generated by `tools/gen_chiron_coeffs.py --dump-refs` (after updating that function for the new dates). The existing 7 entries remain; new entries are appended.

**Primary recommendation:** The spike and regeneration are a single-plan phase. Run the spike script (ephemeral, never committed) to measure accuracy at degree=10 for 1900–2100, decide on degree, then edit `gen_chiron_coeffs.py` for the new range (2 line changes in `setup_oracle`), run it to regenerate `.npz`, update the regression test, and update docstrings/comments mentioning 1142/1950/2050.

---

## Architecture Patterns

### Findings: `tools/gen_chiron_coeffs.py` (22 KB, 660 lines)

**Constants — exact locations:**

| Constant | Line | Value | Notes |
|----------|------|-------|-------|
| `_SEG_LEN` | 55 | `32.0` (float) | "LOCKED, do not modify" comment |
| `_DEGREE` | 56 | `10` (int) | "LOCKED, do not modify" comment |
| `_N_FIT` | 57 | `_DEGREE + 8` | computed, changes with degree |
| `jd0` (start) | 110 | `swe.julday(1950, 1, 1, 0.0)` | inside `setup_oracle()` |
| `jd1` (end) | 111 | `swe.julday(2050, 1, 1, 0.0)` | inside `setup_oracle()` |
| `_REF_JDS` | 61–69 | 7 JDs for `--dump-refs` | includes 1950 and 2050 endpoints |
| `_DEFAULT_EPHE_PATH` | 76 | `/home/loc/workspace/rahu/kerykeion/kerykeion/sweph` | fallback if `SE_EPHE_PATH` unset |
| `_DEFAULT_OUTPUT` | 71–74 | `ketu/data/chiron_coeffs.npz` | relative to `__file__` |

**Ephemeris path resolution (line 601):**
```python
ephe_path = os.environ.get("SE_EPHE_PATH", _DEFAULT_EPHE_PATH)
```
The `_DEFAULT_EPHE_PATH` (line 76) points to the kerykeion sweph directory, which is confirmed accessible and contains `seas_18.se1`. No need to set `SE_EPHE_PATH` on this machine unless the path changes.

**CLI args:** The generator supports `--output` and `--dump-refs`, but has NO CLI arg for `--jd-start`, `--jd-end`, or `--degree`. To run the spike with different parameters, a small wrapper script (ephemeral, never committed) must be created, or the constants must be temporarily edited. Since the spike is ephemeral, editing the module constants in-memory via a wrapper is the cleanest approach:

```python
# Ephemeral spike script (never committed):
import gen_chiron_coeffs as g
g._SEG_LEN = 32.0  # or lower if needed
g._DEGREE = 10     # or 12
g._N_FIT = g._DEGREE + 8

import swisseph as swe
jd0 = swe.julday(1900, 1, 1, 0.0)
jd1 = swe.julday(2100, 1, 1, 0.0)
# run g.generate_all_coefficients(jd0, jd1)
# run g.validate_coefficients(...)
```

**`.npz` write function (`write_npz`, lines 502–547):** Writes exactly 8 named arrays: `lon_coeffs`, `lat_coeffs`, `dist_coeffs`, `seg_starts`, `seg_len` (scalar float64), `degree` (scalar int32), `jd_start` (scalar float64), `jd_end` (scalar float64). Uses `np.savez_compressed`. The `jd0`/`jd1` are passed in as the range endpoints — if `setup_oracle` is updated to return 1900/2100 JDs, the write is correct automatically.

**`actual_len` at generation time:** Yes — `fit_segment()` (lines 249–284) computes `actual_len = jd_e - jd_s` where `jd_e = min(jd_s + _SEG_LEN, jd1)`. The last segment uses the clipped end, so the generator already handles it correctly. The Phase 24-04 fix lives in the evaluator (`chiron.py:113`) and will remain valid with the new `.npz` since the evaluator reads `jd_end` from the file.

**Validation built-in:** `validate_coefficients()` (lines 352–455) runs a full pur-NumPy vs oracle comparison after generation, with 200 points per segment. The main loop already reports the worst segment. This is the built-in gate that prevents writing the `.npz` if `max|Δλ| >= 0.01°`.

---

### Findings: `ketu/ephemeris/chiron.py` (8.3 KB, 250 lines)

**Array names loaded from `.npz` (line 52):** `npz.files` — reads all keys: `lon_coeffs`, `lat_coeffs`, `dist_coeffs`, `seg_starts`, `seg_len`, `degree`, `jd_start`, `jd_end`. Code uses `data["seg_starts"]`, `data["seg_len"]`, `data["jd_end"]`, `data["lon_coeffs"]`, `data["lat_coeffs"]`, `data["dist_coeffs"]`. The key `jd_start` is stored in `.npz` but **not read by the evaluator** — the evaluator derives segment selection from `seg_starts[0]` (the first element of `seg_starts`). This is fine.

**`_eval_chiron_qty` — exact `actual_len` fix (line 113):**
```python
actual_len = min(seg_starts[si] + seg_len, jd_end) - seg_starts[si]
```
This is the Phase 24-04 fix. It reads `jd_end` from the parameter (which comes from `data["jd_end"]`), so when the `.npz` is regenerated with `jd_end=2488069.5` (2100-01-01), the evaluator automatically uses the correct `jd_end` for the new last segment. No code change required in `chiron.py` for the `.npz` extension.

**Out-of-range behavior (CONFIRMED, lines 110–111):**
```python
si = int((jd - seg_starts[0]) / seg_len)
si = max(0, min(si, len(seg_starts) - 1))
```
Then `t` is also clipped to `[-1, 1]` (line 114). Behavior: **silent clamp** — JDs below range return the first segment's extrapolation (clamped to `t=-1` at most), JDs above range return the last segment's extrapolation (clamped to `t=+1` at most). No exception, no NaN, no warning. This behavior is preserved automatically after `.npz` regeneration since it depends on `seg_starts[0]` and `len(seg_starts)-1`, which update with the new data.

**Zero `pyswisseph` import:** Confirmed (line-by-line inspection). The module imports only `functools`, `importlib.resources`, `numpy`, and `.coordinates`. No `swisseph`, `pyswisseph`, or `swe` anywhere.

**Docstring references to 1950/2050:** Lines 36, 75, 85 contain stale range references in docstrings that will need updating after `.npz` regeneration. These are cosmetic/documentation changes, but since numpydoc gates are BLOCKING, doctests in those docstrings must pass. Inspection confirms no runnable doctest in those docstring sections — they are description-only. The actual doctests (`>>> data["lon_coeffs"].shape`, `>>> 0.0 <= val % 360.0 < 360.0`, etc.) do not hardcode `(1142, 11)` so they survive.

---

### Findings: `tests/ephemeris/test_chiron_regression.py` (92 lines)

**Pin structure (lines 41–49):**
```python
_CHIRON_REFS: list[tuple[float, float]] = [
    (2433282.5, 255.777223),  # 1950-01-01  retflag=260
    (2440587.5,   2.520351),  # 1970-01-01  retflag=260
    ...
    (2469807.5, 246.587706),  # 2050-01-01  retflag=260
]
TOLERANCE_DEG: float = 0.01
```

**Test mechanism (lines 55–91):** `@pytest.mark.parametrize("jd, expected_lon", _CHIRON_REFS)` — each tuple becomes one parametrized test case. Adding new tuples to `_CHIRON_REFS` automatically adds new test cases. Pattern for new wing refs:
```python
(2422324.5, XXX.XXXXXX),  # 1920-01-01  retflag=260
(2480764.5, XXX.XXXXXX),  # 2080-01-01  retflag=260
```
The assertion uses wrap-aware delta: `delta = abs(actual_lon - expected_lon); if delta > 180.0: delta = 360.0 - delta`.

**Test unit clamp tests (lines 222–281):** `test_clamp_below_range` and `test_clamp_above_range` use `seg_starts[0] - 1000.0` and `seg_starts[-1] + seg_len + 1000.0` respectively — relative offsets from the data, not hardcoded JDs. These tests are **not broken** by `.npz` regeneration.

**Shape assertion that WILL BREAK:** `test_load_chiron_data_shapes` (lines 38–61) in `tests/ephemeris/test_chiron_unit.py` asserts:
```python
assert data["lon_coeffs"].shape == (1142, 11)
assert data["lat_coeffs"].shape == (1142, 11)
assert data["dist_coeffs"].shape == (1142, 11)
assert data["seg_starts"].shape == (1142,)
```
After regeneration with 2283 segments, these assertions will fail. They must be updated to `(2283, 11)` / `(2283,)`. This is the only test that hardcodes segment count.

**Comment `test_chiron_unit.py:108`:** "In natural 1950-2050 data, Chiron moves at most ~0.019°/day" — a cosmetic docstring line that should be updated to reference the new range. No runnable assertion.

**`test_cycles_calculator.py:96`:** `assert np.all(result['julian_day'] < 2470000)  # Before 2050` — unrelated to Chiron range, not broken.

---

### Findings: `.npz` Contents (current)

| Key | Shape | Dtype | Value |
|-----|-------|-------|-------|
| `lon_coeffs` | (1142, 11) | float64 | Chebyshev coefficients for ecliptic longitude |
| `lat_coeffs` | (1142, 11) | float64 | Chebyshev coefficients for latitude |
| `dist_coeffs` | (1142, 11) | float64 | Chebyshev coefficients for distance (AU) |
| `seg_starts` | (1142,) | float64 | JD start of each segment |
| `seg_len` | scalar () | float64 | 32.0 |
| `degree` | scalar () | int32 | 10 |
| `jd_start` | scalar () | float64 | 2433282.5 (= 1950-01-01 UTC) |
| `jd_end` | scalar () | float64 | 2469807.5 (= 2050-01-01 UTC) |

File size: 289.7 KB (296,611 bytes).

**New range computed values:**

| Parameter | New Value | Source |
|-----------|-----------|--------|
| `jd_start` | 2415020.5 | `swe.julday(1900, 1, 1, 0.0)` |
| `jd_end` | 2488069.5 | `swe.julday(2100, 1, 1, 0.0)` |
| total_days | 73049.0 | 200 years exactly |
| `n_segs` | 2283 | `ceil(73049.0 / 32.0)` |
| last segment `actual_len` | 25.0 days | `73049 % 32 = 25` |
| estimated file size | ~580 KB compressed | 2.00× current |

Old last segment `actual_len` = 13.0 days (`36525 % 32 = 13`). New = 25.0 days.

---

### Spike Feasibility

**Oracle confirmed working at 1900 and 2100:**
- `swe.calc_ut(JD_1900, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED)` → `retflag=260`, lon=258.8960°
- `swe.calc_ut(JD_2100, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED)` → `retflag=260`, lon=241.8599°
- `retflag=260` = Moshier+SPEED — same fallback as current 1950–2050 (acceptable, delta vs SWIEPH ≤ 0.000067°)
- `seas_18.se1` covers years 1800–2400 (confirmed: year 1800 fails with `seas_12.se1 not found`, year 1850 works)

**`swe.CHIRON` constant:** Confirmed `swe.CHIRON = 15` (not 13 — body_id=13 is Ketu's internal index, distinct from swisseph's constant).

**Exact Oracle call for spike + pinning:**
```python
import swisseph as swe
flags = swe.FLG_SWIEPH | swe.FLG_SPEED  # = 258
xx, retflag, errmsg = swe.calc_ut(float(jd), swe.CHIRON, flags)
lon = xx[0] % 360.0
```

**Ephemeral spike script design:** The generator has no `--degree` or `--jd-start`/`--jd-end` CLI args. The spike script must be a separate ephemeral `.py` (never committed) that:
1. Sets `ephe_path` and calls `swe.set_ephe_path()` (pre-flight check)
2. Verifies Chiron query at J2000.0 succeeds and reports `retflag`
3. Calls `generate_all_coefficients(jd_1900, jd_2100)` with patched `_DEGREE`/`_SEG_LEN`
4. Calls `validate_coefficients()` with DENSE sampling of 1900–1910 region (increase `n_val_per_seg` or add a dedicated dense pass on segments 0–10)
5. Reports `max|Δλ|`, worst JD, and whether gate passes
6. If gate fails: retry with `_DEGREE=12`
7. Reports verdict for decision log entry

**Dense 1900–1910 sampling concern:** The built-in `validate_coefficients` distributes 200 points per segment uniformly. For the near-perihelion edge (1900–1910 = segments 0–10), this is already dense enough (200 pts over 32 days = 1 pt every 0.16 days). The spike should explicitly report per-segment max errors for segments 0–10 to surface any gradient spike vs. the overall worst-case. The existing validator already tracks per-segment max and the `worst_jd`.

---

## Common Pitfalls

### Pitfall 1: Generator hardcodes range in `setup_oracle()` — must change TWO lines
**What goes wrong:** Only updating `_DEGREE`/`_SEG_LEN` without updating `setup_oracle()` lines 110–111 leaves the generator still computing 1142 segments for 1950–2050.
**How to avoid:** Lines 110–111 are the ONLY place jd0/jd1 are computed. Change both to `swe.julday(1900, 1, 1, 0.0)` and `swe.julday(2100, 1, 1, 0.0)`.

### Pitfall 2: `_REF_JDS` and `--dump-refs` not updated for new wing dates
**What goes wrong:** Running `--dump-refs` after updating `setup_oracle` will correctly compute new JDs, but `_REF_JDS` (line 61–69) still lists only the old 7 dates (1950–2050). New wing dates (e.g., 1920-01-01, 2080-01-01) must be added to `_REF_JDS` so `--dump-refs` generates the extended pinning list.
**How to avoid:** Add `swe.julday(1900, 1, 1, 0.0)`, `swe.julday(1920, 1, 1, 0.0)`, `swe.julday(2080, 1, 1, 0.0)` to `_REF_JDS`. The existing 7 are kept verbatim.

### Pitfall 3: `test_load_chiron_data_shapes` will BREAK immediately after `.npz` regeneration
**What goes wrong:** Hard assertion `shape == (1142, 11)` in `tests/ephemeris/test_chiron_unit.py:55–58` fails with new 2283-segment `.npz`.
**How to avoid:** Update assertions to `(2283, 11)` / `(2283,)` in the same commit that regenerates the `.npz`. These must change atomically.

### Pitfall 4: `lru_cache` on `_load_chiron_data` masks stale `.npz` during testing
**What goes wrong:** If the cache is populated before the new `.npz` is in place, tests see old shapes. This only affects in-process sequential runs — `pytest` starts fresh, so this is not an issue. Note it for spike scripts that import `chiron.py` directly.
**How to avoid:** In spike scripts, call `_load_chiron_data.cache_clear()` after replacing the `.npz` file if needed.

### Pitfall 5: Docstrings mentioning "1950" or "2050" stale after regeneration
**What goes wrong:** numpydoc gate checks docstrings; stale range descriptions don't fail the gate (no assert), but mislead maintainers.
**Files to update:** `tools/gen_chiron_coeffs.py` (module docstring lines 10–17, `_DEGREE`/`_SEG_LEN` LOCKED comments, `setup_oracle` docstring), `ketu/ephemeris/chiron.py` (docstring lines 36, 75, 85, 106), `tests/ephemeris/test_chiron_regression.py` (module docstring line 13, test docstring line 78), `tests/ephemeris/test_chiron_unit.py` (lines 43–57, 108, 223–234, 256–268).

### Pitfall 6: `degree=12` changes `_N_FIT = _DEGREE + 8` → 20
**What goes wrong:** If degree is raised to 12, `_N_FIT` automatically becomes 20 (12+8) since it's computed. The generator is correct. But the decision log entry must record `degree=12` so a future reader knows the spike changed it.
**How to avoid:** Document in decision log entry: params used (seg_len, degree_final, max|Δλ| measured).

---

## Code Examples

### The Two Lines to Change in `gen_chiron_coeffs.py` (setup_oracle)

Current (lines 110–111):
```python
jd0 = swe.julday(1950, 1, 1, 0.0)
jd1 = swe.julday(2050, 1, 1, 0.0)
```

After update:
```python
jd0 = swe.julday(1900, 1, 1, 0.0)
jd1 = swe.julday(2100, 1, 1, 0.0)
```

### `test_chiron_unit.py` Shape Assertions to Update

Current (lines 55–58):
```python
assert data["lon_coeffs"].shape == (1142, 11)
assert data["lat_coeffs"].shape == (1142, 11)
assert data["dist_coeffs"].shape == (1142, 11)
assert data["seg_starts"].shape == (1142,)
```

After update (degree=10) or (degree=12 → still 11 coeffs? No — degree=12 → 13 coeffs):
```python
# degree=10 unchanged: (n_segs, 11)
assert data["lon_coeffs"].shape == (2283, 11)
assert data["lat_coeffs"].shape == (2283, 11)
assert data["dist_coeffs"].shape == (2283, 11)
assert data["seg_starts"].shape == (2283,)
```

**IMPORTANT:** If degree is raised to 12, the coefficient dimension changes: `degree+1 = 13`. The shape assertions would need `(2283, 13)`. The `int(data["degree"]) == 10` assertion (line 61) must also change to `== 12`.

### Oracle Call for Pinning New Reference Longitudes

```python
import swisseph as swe
swe.set_ephe_path("/home/loc/workspace/rahu/kerykeion/kerykeion/sweph")
flags = swe.FLG_SWIEPH | swe.FLG_SPEED  # 258

new_ref_jds = [
    (swe.julday(1900, 1, 1, 0.0), "1900-01-01"),
    (swe.julday(1920, 1, 1, 0.0), "1920-01-01"),
    (swe.julday(2080, 1, 1, 0.0), "2080-01-01"),
]
for jd, label in new_ref_jds:
    xx, retflag, _ = swe.calc_ut(jd, swe.CHIRON, flags)
    lon = xx[0] % 360.0
    print(f"    ({jd}, {lon:.6f}),  # {label}  retflag={retflag}")
```

This is cleanly done via `tools/gen_chiron_coeffs.py --dump-refs` after updating `_REF_JDS` (add new dates) and `setup_oracle` (new range).

### Ephemeral Spike Skeleton

```python
# /tmp/chiron_spike_30.py — NEVER COMMIT
import sys
sys.path.insert(0, "/home/loc/workspace/ketu/tools")
sys.path.insert(0, "/home/loc/workspace/ketu")
import gen_chiron_coeffs as g
import swisseph as swe

# Override constants for spike
g._DEGREE = 10  # or 12 if retry
g._N_FIT = g._DEGREE + 8
SEG_LEN = 32.0

EPHE_PATH = "/home/loc/workspace/rahu/kerykeion/kerykeion/sweph"
swe.set_ephe_path(EPHE_PATH)

# Pre-flight check
jd_test = 2451545.0
xx, retflag, _ = swe.calc_ut(jd_test, swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED)
print(f"Pre-flight: retflag={retflag}, CHIRON={swe.CHIRON}, lon={xx[0]:.4f}°")

jd0 = swe.julday(1900, 1, 1, 0.0)
jd1 = swe.julday(2100, 1, 1, 0.0)
print(f"Range: {jd0} to {jd1}  ({(jd1-jd0):.0f} days)")

# Generate
lon_c, lat_c, dist_c, seg_s = g.generate_all_coefficients(jd0, jd1)

# Validate — dense report on 1900-1910 edge (segments 0-10)
print("\n=== DENSE SEGMENT REPORT (1900-1910) ===")
import numpy as np
import numpy.polynomial.chebyshev as npc
import math
n_segs = len(seg_s)
for si in range(min(11, n_segs)):
    jd_s = seg_s[si]
    jd_e = min(jd_s + SEG_LEN, jd1)
    actual_len = jd_e - jd_s
    t_val = np.linspace(-1.0, 1.0, 500)
    jd_val = jd_s + (t_val + 1.0) / 2.0 * actual_len
    lon_pred = npc.chebval(t_val, lon_c[si]) % 360.0
    lon_true = np.array([swe.calc_ut(float(jd), swe.CHIRON, swe.FLG_SWIEPH | swe.FLG_SPEED)[0][0] % 360.0 for jd in jd_val])
    lon_errs = np.abs(lon_pred - lon_true)
    lon_errs = np.minimum(lon_errs, 360.0 - lon_errs)
    print(f"  seg {si:3d} JD={jd_s:.1f}: max|Δλ|={np.max(lon_errs):.6f}°")

# Full validation
max_lon_err, max_lat_err, max_dist_err, worst_jd = g.validate_coefficients(
    lon_c, lat_c, dist_c, seg_s, jd0, jd1
)
print(f"\nFINAL: max|Δλ|={max_lon_err:.6f}°  (gate: < 0.01°)")
print(f"  worst JD: {worst_jd:.2f}")
gate = "PASS" if max_lon_err < 0.01 else "FAIL"
print(f"  GATE: {gate}")
```

---

## Decision Log Target

After the spike, one entry must be added to two files:

**`PROJECT.md` Key Decisions table** (line ~168): Add a row:
```
| [Phase 30-01]: Chiron range 1900–2100 spike verdict | max|Δλ|=X.XXXXXX° measured; degree=Y (seg=32d); gate PASS/FAIL | — Phase 30 |
```

**`STATE.md` Accumulated Context / Decisions section** (around line 85): Add:
```
- [Phase 30-01]: Chiron range 1900-2100 spike: max|Δλ|=X.XXXXXX°, params seg=32d/degree=Y, gate PASS < 0.01°; new .npz = 2283 segs, jd_start=2415020.5, jd_end=2488069.5.
```

---

## Open Questions

1. **Will degree=10 pass for 1900–2100?**
   - What we know: Phase 23 measured `max|Δλ|=0.000861°` for 1950–2050 at degree=10. The perihelion (~1895–1896) is below the 1900 lower bound, so 1900 is near but not at the sharpest curvature. The 1895–96 perihelion was Chiron's closest approach to the Sun — this means Chiron's orbital velocity and curvature were maximum in that period. The 1900–1905 region is in the aftermath of perihelion: orbit still highly curved.
   - What's unclear: Whether the degree=10 polynomial residuals at segments near 1900 (post-perihelion high-curvature region) exceed 0.01°.
   - Recommendation: The spike script (with dense 500-pt validation on segs 0–10) answers this definitively. If degree=10 fails any segment in 1900–1910, increment to degree=12 and re-run. No guessing required.

2. **Does the existing `--dump-refs` output need manual editing or is there a clean CLI flow?**
   - What we know: `--dump-refs` only outputs the 7 hardcoded `_REF_JDS` dates. After updating `_REF_JDS` to include 1900, 1920, 2080 dates, running `--dump-refs` will print the complete pinning list for both old and new refs.
   - Recommendation: Update `_REF_JDS` (add 3 new dates) before running `--dump-refs` to get the full list in one shot.

3. **Degree=12: what changes downstream?**
   - If degree goes to 12: `degree+1=13` → coefficient shape `(2283, 13)`. The evaluator reads `coeffs[si]` with no hardcoded dimension — `chebval(t, coeffs[si])` works for any length. The only downstream change is `test_load_chiron_data_shapes` assertions for shape `(2283, 13)` and `int(data["degree"]) == 12`.
   - No change to `_eval_chiron_qty` logic — it is dimension-agnostic.

---

## Sources

### Primary (HIGH confidence)
- Direct read of `/home/loc/workspace/ketu/tools/gen_chiron_coeffs.py` (660 lines, full)
- Direct read of `/home/loc/workspace/ketu/ketu/ephemeris/chiron.py` (250 lines, full)
- Direct read of `/home/loc/workspace/ketu/tests/ephemeris/test_chiron_regression.py` (92 lines, full)
- Direct read of `/home/loc/workspace/ketu/tests/ephemeris/test_chiron_unit.py` (300+ lines, key sections)
- Live `numpy.load` of `ketu/data/chiron_coeffs.npz` — shapes/dtypes verified
- Live `swisseph` queries at JD_1900, JD_2100, JD_1910 — oracle works, retflag=260 confirmed
- Direct inspection of `swe.CHIRON = 15`, `swe.FLG_SWIEPH | swe.FLG_SPEED = 258`

### Secondary (HIGH confidence)
- `grep -rn` scan of all `tests/` and `ketu/` for hardcoded `1950`/`2050`/`1142`/`2433282`/`2469807` patterns — found `test_chiron_unit.py:55–58` as the only code assertion that will break

---

## Metadata

**Confidence breakdown:**
- Generator interface: HIGH — read fully, verified CLI args, constant locations, path resolution
- Runtime evaluator behavior: HIGH — out-of-range clamp confirmed from code + existing tests
- Oracle feasibility: HIGH — live queries confirmed working at 1900 and 2100
- Spike approach: HIGH — generator machinery is reusable as-is with ephemeral wrapper
- Tests that will break: HIGH — `test_chiron_unit.py:55-58` shape assertions identified with line numbers
- Degree=12 impact: HIGH — evaluator is dimension-agnostic (chebval), only test assertions change

**Research date:** 2026-06-03
**Valid until:** Stable — no external dependencies, all findings from local source code

---

## RESEARCH COMPLETE

**Phase:** 30 - Chiron Range 1900–2100
**Confidence:** HIGH

### Key Findings

1. **Generator changes are minimal:** Two lines in `setup_oracle()` (lines 110–111 of `tools/gen_chiron_coeffs.py`) + new dates in `_REF_JDS` (lines 61–69). No CLI args for range/degree exist — spike needs an ephemeral wrapper that overrides `_DEGREE`/`_N_FIT`.

2. **Confirmed working oracle:** `swe.calc_ut(JD_1900, swe.CHIRON, ...)` → `retflag=260`, accessible via default `_DEFAULT_EPHE_PATH`. No `SE_EPHE_PATH` env var needed on this machine.

3. **One test will break:** `tests/ephemeris/test_chiron_unit.py:55–58` hardcodes `(1142, 11)` shapes. Must update to `(2283, 11)` (degree=10) or `(2283, 13)` (degree=12). This is the only code assertion that breaks.

4. **Out-of-range behavior is silent clamp** (not error, not NaN) — `max(0, min(si, n_segs-1))` + `t` clipped to `[-1,1]`. Preserved automatically after `.npz` regeneration since it reads `seg_starts[0]` and `len(seg_starts)-1` from the loaded data.

5. **`actual_len` fix survives automatically:** `_eval_chiron_qty:113` reads `jd_end` from `data["jd_end"]` which will be `2488069.5` after regeneration. New last segment `actual_len = 25.0` days (`73049 % 32`). No code change to `chiron.py` needed.

### File Created
`.planning/phases/30-chiron-range-1900-2100/30-RESEARCH.md`

### Confidence Assessment
| Area | Level | Reason |
|------|-------|--------|
| Generator interface | HIGH | Full source read, CLI tested |
| Oracle feasibility at 1900/2100 | HIGH | Live queries confirmed |
| Tests that break | HIGH | Grep scan + line-number pinpointing |
| Spike approach | HIGH | Built-in validate_coefficients() reusable |
| Degree=12 impact if needed | HIGH | Evaluator is dimension-agnostic |

### Open Questions
- Will degree=10 pass for 1900–2100 (especially 1900–1910 post-perihelion region)? — Answered definitively only by running the spike. The perihelion (~1895–96) is just below the 1900 lower bound; 1900–1905 is in the aftermath of maximum orbital curvature.

### Ready for Planning
Research complete. Planner can now create PLAN.md files.
