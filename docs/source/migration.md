# Migration Guide

This guide helps you upgrade Ketu across major and minor versions. For the full list of changes, see the [Changelog](changelog.md).

---

## Upgrading from v1.2 to v1.3

### Breaking Change: CHART_DTYPE body axis expanded from 13 to 14 bodies (D-08)

In v1.3, Chiron is added as body_id=13 (the 14th body). This change expands several array dimensions:

**Before (v1.2):**
- `chart["body_lons"]` — shape `(13,)`
- `chart["body_lats"]` — shape `(13,)`
- `chart["body_speeds"]` — shape `(13,)`
- `chart["aspect_matrix"]` — shape `(13, 13)`
- `chart["aspect_orbs"]` — shape `(13, 13)`
- `SYNASTRY_BODY_COUNT = 15` (13 bodies + ASC + MC)

**After (v1.3):**
- `chart["body_lons"]` — shape `(14,)` — index 13 = Chiron
- `chart["body_lats"]` — shape `(14,)`
- `chart["body_speeds"]` — shape `(14,)`
- `chart["aspect_matrix"]` — shape `(14, 14)`
- `chart["aspect_orbs"]` — shape `(14, 14)`
- `SYNASTRY_BODY_COUNT = 16` (14 bodies + ASC + MC)

**Migration actions:**

1. **Code that iterates `range(13)` over body arrays**: update to `range(14)` or use `len(chart["body_lons"])`.
2. **Cached `CHART_DTYPE` arrays from v1.2**: these are incompatible. Recompute them with v1.3.
3. **Downstream consumers checking body count**: update any hardcoded `13` or `SYNASTRY_BODY_COUNT == 15` assertions.
4. **Index 12 (previously last body = Lilith)**: remains unchanged — Chiron is index 13.

```python
# Before (v1.2) — iterating over bodies
for i in range(13):
    lon = chart["body_lons"][i]

# After (v1.3) — use len() or the constant 14
for i in range(len(chart["body_lons"])):   # 14 bodies
    lon = chart["body_lons"][i]
    # i == 13 is Chiron (new)
```

### New: Chiron access

No new import needed — use existing calculation functions with `body_id=13`:

```python
from ketu.calculations import long, lat

chiron_lon = long(jd, 13)   # Chiron longitude
chiron_lat = lat(jd, 13)    # Chiron latitude
```

Valid date range: 1900–2100 (expanded in v1.4). Out-of-range input is silently clamped to the nearest segment boundary — no `ValueError` is raised.

---

## Upgrading from v1.1 to v1.2

### New Subpackages

v1.2 adds five new subpackages. No existing API was removed or renamed.

**`ketu.charts`** — full natal chart:

```python
from ketu.charts import compute_chart, is_day_chart, CHART_DTYPE

chart = compute_chart(jd, lat=48.8566, lon=2.3522, system="placidus")
# chart["body_lons"][0] — Sun longitude
# chart["asc"]          — Ascendant
```

**`ketu.synastry`** — inter-chart aspects:

```python
from ketu.synastry import calculate_synastry, SYNASTRY_DTYPE

syn = calculate_synastry(chart_a, chart_b)
```

**`ketu.composite`** — midpoint composite:

```python
from ketu.composite import calculate_composite, circular_midpoint

comp = calculate_composite(chart_a, chart_b)
```

**`ketu.returns`** — solar and lunar returns:

```python
from ketu.returns import solar_return, lunar_return

sr = solar_return(natal_jd, natal_lat, natal_lon, target_year=2026)
lr = lunar_return(natal_jd, natal_lat, natal_lon, target_jd=search_jd)
```

**`ketu.parts`** — Arabic Parts:

```python
from ketu.parts import calculate_part, calculate_all_parts

fortune = calculate_part("fortune", chart)
```

### Additional House Systems

Three new systems added to `ketu.houses`:

- `"whole_sign"` — each house = one full zodiac sign
- `"equal"` — 30° equal divisions from ASC
- `"regiomontanus"` — celestial equator division

```python
from ketu.houses import calculate_houses

h = calculate_houses(jd, lat, lon, system="whole_sign")
```

---

## Upgrading from v1.0 to v1.1

### New: Configurable Aspect Sets

`calculate_aspects` now accepts an optional `aspects` parameter. Without it, behavior is unchanged (EXTENDED = all 14 aspects).

```python
from ketu.aspects import calculate_aspects, CLASSICAL, TRADITIONAL, EXTENDED

# v1.0 behavior (unchanged default)
all_aspects = calculate_aspects(jd)

# New v1.1: filter to classical only
classical = calculate_aspects(jd, aspects=CLASSICAL)
```

### New: House Systems

`ketu.houses` is a new subpackage — no existing code is broken.

```python
from ketu.houses import calculate_houses, house_of, SYSTEMS

h = calculate_houses(jd, lat=48.8566, lon=2.3522, system="placidus")
print(f"ASC: {h['asc']:.2f}°")

# Determine which house a planet is in
from ketu.calculations import long
sun_house = house_of(long(jd, 0), h["cusps"])
```

### Import Path Corrections (if upgrading from pre-1.0)

If you were using the old `import ketu; ketu.long(...)` style (which was never officially supported as a public API), switch to the correct submodule imports:

```python
# Old (never worked correctly — ketu.long is not in ketu.__all__)
import ketu
lon = ketu.long(jd, 0)

# Correct (v1.0+)
from ketu.calculations import long
lon = long(jd, 0)
```

---

## Upgrading from v0.4.0 to v1.0.0

### Removed: Export Modules

Ketu 1.0 is a pure calculation library. Visualization and calendar export features have been removed:

- **Removed modules**: `ketu.export.chart`, `ketu.export.icalendar`
- **Removed functions**: `draw_zodiacal_chart()`, `export_lunations_to_ical()`, `export_aspects_to_ical()`, `export_transits_to_ical()`

**Migration**: Implement visualization in your application layer using Ketu's calculation results.

### Removed: Pandas Dependency

- `generate_aspect_timeline()` now returns NumPy structured array (was DataFrame)
- `AspectTimeline.to_pandas()` removed
- **Migration**: Use `import pandas as pd; df = pd.DataFrame(timeline)` for manual conversion

### Renamed: Velocity Functions (Breaking)

- `vlong()` → `long_velocity()`
- `vlat()` → `lat_velocity()`
- `vdist_au()` → `dist_velocity_au()`

**Migration**: Use find-and-replace in your codebase:

```bash
sed -i 's/ketu\.vlong(/ketu.long_velocity(/g' *.py
sed -i 's/ketu\.vlat(/ketu.lat_velocity(/g' *.py
sed -i 's/ketu\.vdist_au(/ketu.dist_velocity_au(/g' *.py
```

### Changed: Public API Surface

- `ketu.__init__.py` exports only metadata + core constants
- Functions accessed via submodule imports: `from ketu.calculations import long`
- `ketu.__all__` explicitly lists public API

**Migration**: Most users won't notice this change. If you were importing from internal modules, switch to public API imports.

## Correctness Fixes (v0.4.0 → v1.0.0)

**IMPORTANT: These fixes change calculation results. Recompute cached 0.4.0 results.**

1. **Cache operator precedence bug**: `use_cache=False` was ignored due to missing parentheses
2. **Aspect vectorization non-determinism**: `calculate_aspects_vectorized()` now returns consistent results
3. **Moon velocity wrapping**: Correct velocity at 360°/0° boundary (was showing ±360° spikes)

## Migration Steps (v0.4.0 → v1.0.0)

### Step 1: Update Package

```bash
pip install --upgrade ketu
```

### Step 2: Update Your Code

**Replace velocity function calls:**

```python
# Before (v0.4.0)
v = ketu.vlong(jday, body_id)

# After (v1.0.0)
from ketu.calculations import long_velocity
v = long_velocity(jday, body_id)
```

**Replace pandas conversions:**

```python
# Before (v0.4.0)
timeline = ketu.generate_aspect_timeline(...)
df = timeline.to_pandas()

# After (v1.0.0)
import pandas as pd
timeline = ketu.generate_aspect_timeline(...)
df = pd.DataFrame(timeline)
```

**Remove chart/icalendar calls:**

```python
# Before (v0.4.0) - REMOVED
ketu.draw_zodiacal_chart(jday, output_file="chart.svg")
ketu.export_lunations_to_ical(start, end, "lunations.ics")

# After (v1.0.0) - No replacement
# Implement visualization in your application layer using ketu calculation results
```

### Step 3: Test Your Code

Run your test suite to catch any remaining issues.

### Step 4: Recompute Cached Results

If you cached calculation results from 0.4.0, recompute them for correctness.

## Rollback

Versions 0.3.0 and 0.4.0 were not published to PyPI, so `pip install ketu==0.4.0` will not work. If you need the previous behavior, install from source:

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu
git checkout v0.2.1  # Last published pre-NumPy version
pip install .
```

Note: v1.0.0 is the first NumPy-based release on PyPI. The previous PyPI version is v0.2.1 (pyswisseph-based).

## Getting Help

If you encounter issues:

1. Review the [Changelog](changelog.md) for complete list of changes
2. Open an [issue](https://github.com/alkimya/ketu/issues)
