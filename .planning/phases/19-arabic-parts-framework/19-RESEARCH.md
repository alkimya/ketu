# Phase 19: Arabic Parts Framework — Research

**Researched:** 2026-05-28
**Domain:** Pure-NumPy astrological computation — extensible registry pattern, sect-aware formula dispatch, CLI introspection flag
**Confidence:** HIGH (all findings sourced from direct codebase reading; no external library needed)

---

## Summary

Phase 19 is a structural clone of Phase 15 (additional-house-systems). The registry pattern (`@register` decorator + `SYSTEMS` dict + `get_system` dispatch) is reproduced verbatim in `ketu/parts/`. The sect-aware dispatch (Fortune/Spirit) piggybacks on the existing `is_day_chart(jd, lat, lon)` function, called with the chart's own `jd`/`lat`/`lon` fields. No new dependencies are required.

The five key research questions are resolved with HIGH confidence from the codebase. Chart field access is fully pinned (body indices 0=Sun, 1=Moon, 3=Venus; `chart["asc"]`; Descendant = `(chart["asc"] + 180) % 360`). The formula callable signature should be `(asc_lon: float, sun_lon: float, moon_lon: float, venus_lon: float) -> float` — not an abstract `body_lons` dict — to keep each formula self-documenting and argument-explicit. Normalization is bare `% 360.0` inline (the codebase has no shared utility; all modules inline it). The `--list-parts` CLI flag mirrors `--list-house-systems` exactly: a top-level `action="store_true"` argparse flag, a first-wins short-circuit in `main()`, and a `cmd_list_parts()` function in `ketu/cli/introspection.py`.

**Primary recommendation:** Copy `ketu/houses/` structure to `ketu/parts/`; replace `HouseSystemFn` with a `PartSpec` dataclass; wire `calculate_part` and `calculate_all_parts` against `is_day_chart`; mirror `--list-house-systems` in the CLI. Three plans suffice: (1) `ketu/parts/` skeleton + registry, (2) 3 part implementations + public API, (3) CLI flag + tests + coverage gate.

---

## Key Research Findings (5 Questions Answered)

### Q1 — How does a chart expose ASC, Sun, Moon, Venus, and Descendant?

Source: `ketu/charts/core.py:85` (CHART_DTYPE) + `ketu/charts/core.py:79-81` (body axis comment).

**CHART_DTYPE fields:**
- `chart["asc"]` — scalar `f8`, Ascendant in degrees `[0, 360)`. Direct field.
- `chart["body_lons"]` — `f8` array of shape `(13,)`. Body axis is FROZEN (D-08):
  - Index 0 = Sun
  - Index 1 = Moon
  - Index 3 = Venus
- Descendant is derived: `(chart["asc"] + 180.0) % 360.0` — NOT a stored field. The `composite/api.py` line 250 confirms: `composite_desc = (composite_asc + 180.0) % 360.0`.

**Concrete accessor pattern for `calculate_part`:**
```python
asc_lon   = float(chart["asc"])
sun_lon   = float(chart["body_lons"][0])
moon_lon  = float(chart["body_lons"][1])
venus_lon = float(chart["body_lons"][3])
desc_lon  = (asc_lon + 180.0) % 360.0
```

**Formula callable shape:** Each `PartSpec` formula should receive exactly the 4 values it needs. The cleanest design (see Q3) is a fixed signature `(asc, sun, moon, venus) -> float` — formulas that don't use all args simply ignore the extras. This avoids the abstract `body_lons` dict/array that the spec text mentions; the planner should use the concrete 4-argument signature instead.

**`calculate_part` scalar contract:** `chart` is a scalar (0-d) CHART_DTYPE record. The function operates one chart at a time (same as `calculate_composite`). No vectorisation over multiple charts required by the PARTS-03/04 spec.

---

### Q2 — How does `is_day_chart` behave? Does `calculate_part` need to vectorise?

Source: `ketu/charts/api.py:360-505`.

**Signature:** `is_day_chart(jd, lat, lon) -> np.ndarray of bool`

- Takes `(jd, lat, lon)` separately — NOT a chart object.
- Returns `np.ndarray` of dtype `bool`, shape = `broadcast_shapes(jd, lat, lon)`.
- Scalar inputs return a 0-d `np.ndarray` (not a bare `bool`); use `bool(result)` to unwrap.
- Vectorised over the inputs, but `calculate_part` needs only the scalar case.

**Usage pattern inside `calculate_part`:**
```python
# chart is a scalar CHART_DTYPE (0-d structured array)
is_day = bool(is_day_chart(float(chart["jd"]), float(chart["lat"]), float(chart["lon"])))
```

The docstring at line 437–441 states: "Phase 19 (Arabic Parts) calls this helper directly with `(jd, lat, lon)`." — this is the already-planned integration point.

**D-12 rationale (important):** `is_day_chart` is intentionally NOT stored in CHART_DTYPE to avoid double-source-of-truth. `calculate_part` must call it fresh from the chart's `jd`/`lat`/`lon` fields.

**Vectorisation:** `calculate_part` should be scalar (one chart at a time). `calculate_all_parts` iterates the registry and calls `calculate_part` for each part. No NumPy batch vectorisation needed for Phase 19.

---

### Q3 — Registry design for Fortune/Spirit (sect-aware) vs Marriage (fixed)?

Source: `ketu/houses/registry.py` (pattern to clone).

**Recommendation: `PartSpec` dataclass with `night_formula` defaulting to `day_formula`.**

```python
from dataclasses import dataclass, field
from typing import Callable

# Concrete formula signature — all 4 values always passed; unused ones ignored.
PartFormula = Callable[[float, float, float, float], float]
# Arguments: (asc_lon, sun_lon, moon_lon, venus_lon) -> longitude [0, 360)

@dataclass(frozen=True)
class PartSpec:
    name: str
    day_formula: PartFormula
    night_formula: PartFormula  # = day_formula for sect-FIXED parts (Marriage)
    description: str = ""       # for --list-parts output
```

Marriage registration:
```python
_marriage_formula = lambda asc, sun, moon, venus: (asc + (asc + 180.0) - venus) % 360.0
register("marriage", day_formula=_marriage_formula, night_formula=_marriage_formula,
         description="ASC + DESC - Venus (fixed, no sect inversion)")
```

Fortune registration:
```python
register("fortune",
    day_formula=lambda asc, sun, moon, venus: (asc + moon - sun) % 360.0,
    night_formula=lambda asc, sun, moon, venus: (asc + sun - moon) % 360.0,
    description="day: ASC+Moon-Sun / night: ASC+Sun-Moon")
```

**Why `night_formula=day_formula` instead of a `sect_aware: bool` flag:**
- A v1.3 Lot that happens to be FIXED (like Marriage) registers with one callable passed for both.
- A v1.3 Lot that is sect-aware registers two distinct callables.
- `calculate_part` dispatch is always `spec.day_formula if is_day else spec.night_formula` — no `if sect_aware` branching needed anywhere. Additive without API change.
- A `sect_aware: bool` flag would force a conditional branch into the dispatch and could be misread as "applies only to the classical sect-aware formula set" — the identity-callable approach is self-documenting.

**`PARTS` registry:**
```python
PARTS: dict[str, PartSpec] = {}

def register(name: str, *, day_formula: PartFormula, night_formula: PartFormula,
             description: str = "") -> None:
    PARTS[name.lower()] = PartSpec(name=name.lower(), day_formula=day_formula,
                                   night_formula=night_formula, description=description)

def get_part(name: str) -> PartSpec:
    key = name.lower()
    if key not in PARTS:
        available = sorted(PARTS.keys())
        raise ValueError(f"unknown part {name!r}; available: {available}")
    return PARTS[key]
```

Note: Unlike houses where `register` is a decorator (because the fn IS the system), for parts there is no single function to decorate — the spec carries two callables. Use a plain `register(name, ...)` call instead of `@register(name)`.

---

### Q4 — Is there an existing [0, 360) normalization helper?

Source: grep across `ketu/` for `% 360` patterns.

**No shared utility exists.** Every module that needs normalization inlines `% 360.0`:
- `ketu/composite/core.py:82`: `mid = (a + short / 2.0) % 360.0`
- `ketu/composite/api.py:250`: `composite_desc = (composite_asc + 180.0) % 360.0`
- `ketu/houses/regiomontanus.py:105-140`: multiple inline `% 360.0`
- `ketu/charts/api.py:504`: `delta = (asc - sun_lon) % 360.0`

**Convention:** Inline `% 360.0` everywhere. Do not create a shared helper for Phase 19 — it would be an over-engineering departure from the established pattern.

Part formulas should return `(formula_result) % 360.0`. This is sufficient because Python/NumPy `%` on floats always returns `[0, 360)` for any real input.

---

### Q5 — How is `--list-house-systems` output formatted?

Source: `ketu/cli/introspection.py:56-65`, `ketu/cli/parser.py:60-64`, `ketu/cli/parser.py:290-295`.

**CLI wiring (3-location change):**

1. **`ketu/cli/parser.py`** — `build_parser()`: add `--list-parts` as `action="store_true"` alongside the existing `--list-house-systems` flag. Import `cmd_list_parts` from `introspection`. Add `if args.list_parts: cmd_list_parts(); return 0` to the first-wins ladder (AFTER `--list-orbs`, which is already last).

2. **`ketu/cli/introspection.py`** — add `cmd_list_parts()` function. Output format mirrors `cmd_list_house_systems` exactly:

```python
def cmd_list_house_systems() -> None:
    print("Available house systems (use with --system NAME on `ketu houses`):")
    print()
    for name in sorted(_HOUSE_SYSTEMS.keys()):
        desc = _SYSTEM_DESCRIPTIONS.get(name, "(no description available)")
        print(f"  {name:10} : {desc}")
    print()
    print("At polar latitudes, use --polar-fallback porphyry ...")
```

Mirror for parts:
```python
_PART_DESCRIPTIONS = {
    "fortune":  "day: ASC+Moon-Sun / night: ASC+Sun-Moon (sect-aware)",
    "spirit":   "day: ASC+Sun-Moon / night: ASC+Moon-Sun (sect-aware, mirror of Fortune)",
    "marriage": "ASC+DESC-Venus = ASC+(ASC+180)-Venus (fixed — no sect inversion)",
}

def cmd_list_parts() -> None:
    print("Available Arabic Parts (use with calculate_part() / calculate_all_parts()):")
    print()
    for name in sorted(_PARTS.keys()):
        desc = _PART_DESCRIPTIONS.get(name, "(no description available)")
        print(f"  {name:10} : {desc}")
    print()
    print("Marriage note: fixed formula — day and night formulas are identical.")
```

3. **`tests/cli/test_introspection.py`** — add `TestListParts` class mirroring `TestListHouseSystems` (3 parts, output contains each name, exits 0).

**First-wins order (pinned by existing test `test_list_flags_collision_first_wins`):** The order is `list_aspect_sets → list_house_systems → list_orbs → list_parts` (add `list_parts` last to avoid disturbing the existing collision test).

---

## Architecture Patterns

### Recommended File Layout

```
ketu/parts/
├── __init__.py          # public re-export: PARTS, get_part, register, calculate_part, calculate_all_parts
├── registry.py          # PARTS dict, PartSpec dataclass, PartFormula type alias, register(), get_part()
└── api.py               # calculate_part(part_name, chart), calculate_all_parts(chart, parts=None)

tests/parts/
├── __init__.py
├── test_parts_registry.py       # registry round-trip, ValueError on unknown, extensibility
├── test_parts_oracle.py         # pinned oracle values (day+night for Fortune+Spirit, once for Marriage)
├── test_parts_coverage_gate.py  # sentinel for parts_coverage_gate marker
└── test_parts_cli.py            # --list-parts output (3 parts present, Marriage note in output)
```

### Pattern: `ketu/parts/registry.py`

Exact analogue of `ketu/houses/registry.py` with `PartSpec` replacing `HouseSystemFn`.

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

PartFormula = Callable[[float, float, float, float], float]
# (asc_lon, sun_lon, moon_lon, venus_lon) -> longitude in [0, 360)

@dataclass(frozen=True)
class PartSpec:
    name: str
    day_formula: PartFormula
    night_formula: PartFormula
    description: str = ""

PARTS: dict[str, PartSpec] = {}

def register(name: str, *, day_formula: PartFormula, night_formula: PartFormula,
             description: str = "") -> None:
    PARTS[name.lower()] = PartSpec(name=name.lower(), day_formula=day_formula,
                                   night_formula=night_formula, description=description)

def get_part(name: str) -> PartSpec:
    key = name.lower()
    if key not in PARTS:
        raise ValueError(f"unknown part {name!r}; available: {sorted(PARTS.keys())}")
    return PARTS[key]
```

### Pattern: `ketu/parts/api.py`

```python
from __future__ import annotations
import numpy as np
from ketu.charts.api import is_day_chart
from .registry import PARTS, get_part

def calculate_part(part_name: str, chart: np.ndarray) -> float:
    spec = get_part(part_name)
    is_day = bool(is_day_chart(float(chart["jd"]), float(chart["lat"]), float(chart["lon"])))
    formula = spec.day_formula if is_day else spec.night_formula
    asc   = float(chart["asc"])
    sun   = float(chart["body_lons"][0])
    moon  = float(chart["body_lons"][1])
    venus = float(chart["body_lons"][3])
    return float(formula(asc, sun, moon, venus))

def calculate_all_parts(chart: np.ndarray, parts: list[str] | None = None) -> dict[str, float]:
    names = parts if parts is not None else sorted(PARTS.keys())
    return {name: calculate_part(name, chart) for name in names}
```

### Pattern: `ketu/parts/__init__.py`

```python
from .api import calculate_all_parts, calculate_part
from .registry import PARTS, PartSpec, get_part, register

# Trigger registration of built-in parts:
from . import _parts_builtin  # noqa: F401

__all__ = ["PARTS", "PartSpec", "calculate_all_parts", "calculate_part", "get_part", "register"]
```

And a `ketu/parts/_parts_builtin.py` (or inline in `__init__.py`) that calls `register(...)` for the 3 parts.

Alternatively, put the 3 registration calls directly in `__init__.py` after the imports — Phase 15's analogues are separate modules (`placidus.py`, `koch.py`, etc.) but for 3 simple lambdas a single `_parts_builtin.py` or inline block is cleaner.

### Pattern: Oracle Tests

Mirror `tests/composite/test_oracle.py` (self-consistency primary gate). For parts, "self-consistency" means: hand-compute the expected value once, pin it as a float constant, assert `abs(result - expected) < 1e-9`.

Oracle test skeleton:
```python
# J2000 noon Paris: jd=2451545.0, lat=48.8566, lon=2.3522
# is_day_chart(...) == True (confirmed by existing tests)
# body_lons[0] = Sun lon (read from compute_chart output)
# body_lons[1] = Moon lon (read from compute_chart output)
# body_lons[3] = Venus lon (read from compute_chart output)
# chart["asc"] = ASC lon (read from compute_chart output)
# Compute expected manually: (asc + moon - sun) % 360.0 for Fortune day

# J2000 midnight Paris: jd=2451544.5, lat=48.8566, lon=2.3522
# is_day_chart(...) == False → night formula applies
```

Pin 5 oracle values:
1. Fortune — day chart (Paris J2000 noon)
2. Fortune — night chart (Paris J2000 midnight)
3. Spirit — day chart (Paris J2000 noon)
4. Spirit — night chart (Paris J2000 midnight)
5. Marriage — any chart (same value day and night; verify with both)

### Anti-Patterns to Avoid

- **If/elif ladder in dispatch.** Never `if part_name == "fortune": ... elif part_name == "spirit": ...` — the entire point is registry dispatch.
- **Storing sect in CHART_DTYPE.** D-12 explicitly forbids this. Always call `is_day_chart` fresh.
- **Calling `compute_chart` inside `calculate_part`.** The chart is passed in; do not re-compute.
- **Using `is_day_chart` with a chart object.** The signature is `(jd, lat, lon)` — extract fields explicitly.
- **Creating a mod-360 utility function.** Inline `% 360.0` per the codebase convention.

---

## Common Pitfalls

### Pitfall 1: `--list-parts` collision test breaks
**What goes wrong:** Adding `list_parts` to `main()` before `list_orbs` in the first-wins ladder changes the output of `test_list_flags_collision_first_wins`.
**How to avoid:** Add `if args.list_parts: ...` AFTER `if args.list_orbs: ...` (i.e., last in the ladder). The existing test pins `--list-orbs --list-house-systems` collision and is not affected by appending a new entry at the end.

### Pitfall 2: `__init__.py` omits trigger import
**What goes wrong:** `from ketu.parts import PARTS` returns an empty dict if the registration module is never imported.
**How to avoid:** Mirror the `houses/__init__.py` pattern — add a `from . import _parts_builtin  # noqa: F401` line (or inline the calls) that runs `register(...)` at import time.

### Pitfall 3: `calculate_all_parts(chart, parts=["Fortune"])` — wrong case
**What goes wrong:** Registry keys are lowercase; user-facing names passed to `parts=[...]` may be mixed-case.
**How to avoid:** `calculate_part` calls `get_part(name)` which does `name.lower()` — already case-insensitive per the houses registry pattern. Mirror the same pattern here.

### Pitfall 4: Marriage formula simplification
**Formula:** `ASC + Descendant - Venus` = `ASC + (ASC + 180) - Venus` = `(2*ASC + 180 - Venus) % 360`.
Both forms are equivalent. The lambda should use the simplified form to avoid computing a throwaway Descendant variable:
```python
lambda asc, sun, moon, venus: (2.0 * asc + 180.0 - venus) % 360.0
```

### Pitfall 5: `calculate_all_parts` with `parts=None` ordering
**What goes wrong:** `parts=None` should return ALL registry parts; if the caller expects a deterministic order, document it.
**How to avoid:** Use `sorted(PARTS.keys())` as the default iteration order (alphabetical: fortune, marriage, spirit). Mirrors `sorted(_HOUSE_SYSTEMS.keys())` in `cmd_list_house_systems`.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead |
|---------|-------------|-------------|
| Sect determination | Custom day/night logic | `ketu.charts.api.is_day_chart(jd, lat, lon)` |
| Registry + dispatch | Custom dict + if/elif | `PARTS` dict + `get_part()` (clone from `houses/registry.py`) |
| Mod-360 normalization | Utility function | Inline `% 360.0` (per codebase convention) |
| Chart field access | Index magic | Named fields: `chart["asc"]`, `chart["body_lons"][0]`, etc. |

---

## Standard Stack

No new dependencies. Pure Python + NumPy, same as every other ketu subpackage.

| Component | Version | Source |
|-----------|---------|--------|
| numpy | already in venv | structured array access, `% 360.0` |
| dataclasses | stdlib | `PartSpec` frozen dataclass |
| typing | stdlib | `Callable`, type aliases |

---

## Code Examples

### Resolving a Part

```python
# Source: codebase pattern (charts/api.py + houses/registry.py)
from ketu.charts import compute_chart
from ketu.parts import calculate_part, calculate_all_parts

chart = compute_chart(2451545.0, 48.8566, 2.3522)  # Paris J2000 noon

fortune_lon = calculate_part("fortune", chart)   # float in [0, 360)
all_parts   = calculate_all_parts(chart)          # {"fortune": ..., "marriage": ..., "spirit": ...}
filtered    = calculate_all_parts(chart, parts=["fortune", "spirit"])
```

### Oracle Fixture Pattern (from composite/test_oracle.py)

```python
# Hand-derive once, pin as float constant, regress forever
chart = compute_chart(2451545.0, 48.8566, 2.3522)
asc   = float(chart["asc"])
sun   = float(chart["body_lons"][0])
moon  = float(chart["body_lons"][1])
venus = float(chart["body_lons"][3])
# is_day = True for Paris J2000 noon (existing test confirms this)
expected_fortune_day = (asc + moon - sun) % 360.0
# Run calculate_part("fortune", chart) and assert abs(result - expected_fortune_day) < 1e-9
```

---

## Open Questions

None. All 5 key questions are resolved with HIGH confidence from codebase reading.

---

## Sources

### Primary (HIGH confidence — direct codebase reads)

- `/home/loc/workspace/ketu/ketu/charts/core.py:85-100` — CHART_DTYPE definition; body axis order (0=Sun, 1=Moon, 3=Venus) confirmed at lines 79-81
- `/home/loc/workspace/ketu/ketu/charts/api.py:360-505` — `is_day_chart` signature, D-12/D-13/D-14/D-15 design rationale, Phase 19 callsite already documented at line 441
- `/home/loc/workspace/ketu/ketu/houses/registry.py` — registry pattern to clone
- `/home/loc/workspace/ketu/ketu/houses/__init__.py` — `__init__.py` trigger-import pattern
- `/home/loc/workspace/ketu/ketu/cli/introspection.py:56-65` — `cmd_list_house_systems` output format
- `/home/loc/workspace/ketu/ketu/cli/parser.py:60-64, 290-295` — argparse wiring + first-wins ladder
- `/home/loc/workspace/ketu/ketu/composite/api.py:250` — Descendant derivation `(asc + 180.0) % 360.0`
- `/home/loc/workspace/ketu/tests/composite/test_oracle.py` — oracle test idiom (hand-derived pinned values)
- `/home/loc/workspace/ketu/tests/returns/test_returns_coverage_gate.py` — coverage gate sentinel pattern

---

## Metadata

**Confidence breakdown:**
- Registry pattern: HIGH — direct read of houses/registry.py; exact clone
- Chart field access: HIGH — direct read of CHART_DTYPE + body axis comment
- `is_day_chart` integration: HIGH — docstring already names Phase 19 as the consumer
- CLI wiring: HIGH — direct read of parser.py + introspection.py; exact mirror
- Normalization: HIGH — grep of entire ketu/ confirms no shared utility; inline `% 360.0` everywhere

**Research date:** 2026-05-28
**Valid until:** Stable (pure internal codebase research; no external libraries)
