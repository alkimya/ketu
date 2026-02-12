# Phase 1: API Surface Cleanup - Research

**Researched:** 2026-02-12
**Domain:** Python package API design, dependency management, library refactoring
**Confidence:** HIGH

## Summary

This phase requires cleaning ketu's public API by removing export modules (charts, icalendar), restructuring the package surface to use explicit submodule imports, and documenting the migration path. The technical domain is well-established in Python packaging with clear best practices from the Scientific Python ecosystem.

**Primary recommendation:** Follow the submodule import pattern (users access `ketu.cycles.generate_cycle_series` rather than flat top-level imports), remove optional dependencies entirely (no extras_require), and provide staged migration guidance modeled after pandas 3.0's approach.

The numpy-only dependency strategy is validated by the Scientific Python SPEC 0 (Minimum Supported Dependencies) and aligns with modern library design patterns. The swisseph removal is already complete on develop branch, requiring only verification.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Removal strategy:**
- Hard delete chart and icalendar modules — no stub modules, no deprecation warnings
- Standard Python ImportError if someone tries to import removed modules
- Full cleanup: delete related test files, fixtures, and config entries — no trace of removed modules
- Remove `fr/` directory (French translations) as part of this phase

**Public API shape:**
- Submodule access pattern: `from ketu.cycles import generate_cycle_series`, not flat top-level imports
- Users import from specific submodules (core, cycles, aspects), not from `ketu` directly
- `ketu.__init__.py` does NOT re-export submodule functions

**Dependency boundaries:**
- numpy is the ONLY hard dependency for v1.0
- swisseph already removed on develop branch — confirm and finalize removal
- svgwrite removed entirely (charts are gone)
- icalendar removed entirely
- matplotlib removed entirely
- No extras_require groups — just numpy, dev deps handled separately

**Migration guidance:**
- UPGRADING.md audience: internal use now, public-quality for PyPI release
- Keep library-generic — no Kala-specific references
- Tone: concise but professional for external developers

### Claude's Discretion

- What goes in `ketu.__all__` at top level (version, constants, or minimal)
- Whether submodules define their own `__all__`
- Whether to flatten or keep `ketu/cycles/` package structure
- UPGRADING.md depth and whether to write it in this phase or defer to Phase 6
- UPGRADING.md format (before/after snippets vs concise list)

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope
</user_constraints>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| setuptools | >=61.0 | Build backend | Default Python build system, stable API |
| wheel | latest | Binary distribution | Required for modern package distribution |
| numpy | >=1.20.0 | Array computations | Foundation of scientific Python, only dependency needed |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | latest (dev) | Testing framework | Development only, not production dependency |
| type checkers | optional (dev) | Static analysis | For IDE support, not distributed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| setuptools | poetry/hatch | User chose setuptools (existing), migration out of scope |
| numpy arrays | Python lists | Loss of 10-100x performance for astronomical calculations |
| Explicit packages list | auto-discovery | User has explicit list already, safer for refactoring |

**Installation (post-cleanup):**
```bash
pip install ketu  # Only numpy as dependency
```

**Current dependencies being removed:**
```bash
# These will NO LONGER be available or suggested
matplotlib>=3.5.0    # chart module dependency
icalendar>=5.0.0     # icalendar export dependency
svgwrite             # Not in current pyproject.toml, verify not used
```

## Architecture Patterns

### Recommended Project Structure (Post-Cleanup)
```
ketu/
├── __init__.py              # Minimal exports (__version__ only)
├── core.py                  # Core astronomical data (bodies, aspects, signs)
├── calculations.py          # Position/velocity calculations
├── display.py               # Print functions, CLI entry point
├── lunar_calendar.py        # Lunar cycle utilities
├── complex.py               # Complex number representations
├── resonance.py             # Resonance field calculations
├── aspects/                 # Aspect calculations package
│   ├── __init__.py          # Re-exports from submodules
│   ├── core.py              # Low-level aspect logic
│   ├── calculator.py        # High-level aspect finding
│   ├── windows.py           # Aspect window detection
│   ├── timelines.py         # ML-ready timeline generation
│   └── transits.py          # Transit calculations
├── cycles/                  # Cycle calculations package
│   ├── __init__.py          # Re-exports from calculator
│   └── calculator.py        # Cycle series generation
├── ephemeris/               # Astronomical calculation internals
│   ├── __init__.py
│   ├── time.py
│   ├── planets.py
│   ├── orbital.py
│   └── coordinates.py
└── cache/                   # Ephemeris caching
    ├── __init__.py
    └── ephemeris_cache.py
```

**TO DELETE:**
```
ketu/export/                 # Entire directory
├── __init__.py
├── chart.py                 # matplotlib dependency
├── icalendar.py             # icalendar dependency
└── constants.py             # Chart-related constants

fr/                          # French translations (already gone)
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

### Pattern 1: Submodule Import Pattern (Scientific Python Standard)
**What:** Users import from specific submodules, not package root
**When to use:** All imports in v1.0+
**Example:**
```python
# v1.0 (CORRECT)
from ketu.cycles import generate_cycle_series, DEFAULT_PAIRS
from ketu.aspects import calculate_aspects, AspectWindow

# v0.4.0 (DEPRECATED - will break)
from ketu import generate_cycle_series  # ImportError in v1.0
```

**Source:** [Scientific Python SPEC 1 - Lazy Loading](https://scientific-python.org/specs/spec-0001/)

### Pattern 2: Minimal `__init__.py` at Package Root
**What:** Package `__init__.py` exposes only metadata, not functions
**When to use:** Top-level `ketu/__init__.py`
**Example:**
```python
# ketu/__init__.py - MINIMAL APPROACH (recommended)
"""Ketu - Astronomical calculations for cycle analysis."""

__version__ = "1.0.0"
__author__ = "Loc Cosnier"
__license__ = "MIT"

__all__ = ["__version__", "__author__", "__license__"]
```

**Rationale:** Ben Hoyt's ["Designing Pythonic library APIs"](https://benhoyt.com/writings/python-api-design/) recommends flat namespace, but Scientific Python SPEC 1 shows explicit submodule imports avoid import-time overhead and improve discoverability. For ketu's use case (Kala imports specific functions), submodule pattern is superior.

### Pattern 3: Submodule `__all__` for Explicit Exports
**What:** Each submodule defines `__all__` listing public API
**When to use:** `ketu/cycles/__init__.py`, `ketu/aspects/__init__.py`
**Example:**
```python
# ketu/cycles/__init__.py
from ketu.cycles.calculator import (
    generate_cycle_series,
    generate_multi_cycle_series,
    CycleState,
    CYCLE_DTYPE,
    DEFAULT_PAIRS,
)

__all__ = [
    "generate_cycle_series",
    "generate_multi_cycle_series",
    "CycleState",
    "CYCLE_DTYPE",
    "DEFAULT_PAIRS",
]
```

**Source:** [Real Python - Python's __all__](https://realpython.com/python-all-attribute/)

### Pattern 4: Explicit Package Declaration in pyproject.toml
**What:** List packages explicitly rather than auto-discovery
**When to use:** During major refactoring (this phase)
**Example:**
```toml
[tool.setuptools]
packages = [
    "ketu",
    "ketu.ephemeris",
    "ketu.aspects",
    "ketu.cycles",
    "ketu.cache",
]
# NOTE: ketu.export is REMOVED from this list
```

**Why:** User already has explicit list. During refactoring, explicit > auto-discovery to prevent accidental inclusion of deleted modules.

**Source:** [Setuptools - Package Discovery](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html)

### Anti-Patterns to Avoid

- **Stub modules for removed code:** Don't create `ketu/export/__init__.py` with deprecation warnings — clean break with ImportError
- **Empty extras_require:** Don't keep `[project.optional-dependencies]` table with empty lists — remove entirely
- **Conditional imports in __init__.py:** Current pattern of `try: from ketu.export import ...` creates API uncertainty — delete completely
- **Top-level re-exports:** Don't import submodule functions into `ketu/__init__.py` — forces users onto submodule pattern immediately

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Removing unused imports | Manual search | `autoflake --remove-all-unused-imports` | Catches all cases, handles multi-line imports |
| Type stub generation | Manual .pyi files | Rely on inline type hints | ketu already has type hints, .pyi only needed for lazy loading |
| Deprecation warnings | Custom warning infrastructure | Standard ImportError | Clean break is clearer than deprecation for v1.0 |
| pyproject.toml validation | Manual checking | `pip install -e .` in clean venv | Catches missing dependencies, import errors |

**Key insight:** For major version bumps, **clean breaks are clearer than deprecation chains**. Users upgrade intentionally and expect to read migration docs. Half-measures (stub modules, warnings) create confusion without preventing breakage.

## Common Pitfalls

### Pitfall 1: Forgetting to Update Test Imports
**What goes wrong:** Tests still import from old paths, pytest passes because modules exist, then build fails after deletion
**Why it happens:** Tests import `from ketu import X` which works in v0.4.0
**How to avoid:**
1. Grep all test files for import patterns: `grep -r "from ketu import" tests/`
2. Update tests to use submodule imports BEFORE deleting export modules
3. Run full test suite after import updates, before deletions
**Warning signs:** Imports in test files don't match documented patterns

### Pitfall 2: Leaving References in pyproject.toml
**What goes wrong:** Build succeeds but package metadata references removed features
**Why it happens:** Multiple places reference optional dependencies:
- `[project.optional-dependencies]`
- `[project.scripts]` (CLI entry points)
- `[tool.setuptools]` packages list
**How to avoid:**
1. Create checklist of all pyproject.toml sections
2. Search for removed module names: `chart`, `icalendar`, `export`
3. Verify `[project.scripts]` doesn't reference removed display functions
**Warning signs:** Build warnings about missing modules in entry points

### Pitfall 3: Incomplete Test File Cleanup
**What goes wrong:** Orphaned test files remain, coverage reports mislead
**Why it happens:** Tests may be named generically (`test_ketu.py`) or in unexpected locations
**How to avoid:**
1. Search test files for removed functionality: `grep -r "export\|chart\|ical" tests/`
2. Check fixtures: `grep -r "@pytest.fixture" tests/ | grep -i "chart\|export"`
3. Verify no conftest.py has export-related fixtures
**Warning signs:** Test file imports matplotlib or icalendar

### Pitfall 4: Assuming Empty extras_require is Safe
**What goes wrong:** Downstream packages using `pip install ketu[chart]` get cryptic errors
**Why it happens:** pip install succeeds with warning, but users expect feature
**How to avoid:**
- Remove entire `[project.optional-dependencies]` section
- Document in UPGRADING.md that `[chart]` and `[icalendar]` extras are gone
- Do NOT keep empty placeholders
**Warning signs:** `[project.optional-dependencies]` table exists but empty
**Justification:** User specified "no extras_require groups" — removal safer than empty groups

### Pitfall 5: Breaking Existing Kala Integration
**What goes wrong:** Kala code imports from old paths, breaks on ketu upgrade
**Why it happens:** Kala may use top-level imports or export functions
**How to avoid:**
1. Search Kala codebase for ketu imports before starting
2. Create compatibility shim in Kala if needed (Kala's responsibility, not ketu's)
3. Document breaking changes clearly in UPGRADING.md
**Warning signs:** No verification of Kala's current import patterns
**Note:** Research suggests checking `/home/loc/workspace/solaris/kala/` for `from ketu import` patterns, but that's integration validation (Phase 7), not API design

## Code Examples

Verified patterns from official sources and current ketu structure:

### Minimal Package Root (Recommended for ketu.__init__.py)
```python
# Source: Scientific Python SPEC 1, Ben Hoyt API design patterns
"""Ketu - Astronomical cycle calculations.

Submodules:
- ketu.cycles: Planetary cycle time series generation
- ketu.aspects: Aspect calculations and windows
- ketu.core: Astronomical constants and data structures
- ketu.calculations: Position and velocity calculations
"""

__version__ = "1.0.0"
__author__ = "Loc Cosnier"
__license__ = "MIT"

# Optionally expose core data structures for convenience
from ketu.core import bodies, aspects, signs

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "bodies",
    "aspects",
    "signs",
]
```

**Rationale for exposing core data structures:** `bodies`, `aspects`, `signs` are constants, not functions. Importing them has zero overhead and they're used by nearly all ketu code. This is the ONE exception to "no top-level re-exports."

### Submodule __all__ Pattern (for cycles, aspects)
```python
# Source: Real Python __all__ guide, current ketu/cycles/__init__.py
"""Planetary cycle calculations for time series analysis."""

from ketu.cycles.calculator import (
    generate_cycle_series,
    generate_multi_cycle_series,
    CycleState,
    CYCLE_DTYPE,
    MAJOR_ASPECTS,
    DEFAULT_PAIRS,
)

__all__ = [
    "generate_cycle_series",
    "generate_multi_cycle_series",
    "CycleState",
    "CYCLE_DTYPE",
    "MAJOR_ASPECTS",
    "DEFAULT_PAIRS",
]
```

### Clean pyproject.toml Dependencies
```toml
# Source: Setuptools documentation, Scientific Python SPEC 0
[project]
name = "ketu"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.20.0",
]

# NO [project.optional-dependencies] section
# NO matplotlib, icalendar, svgwrite references

[tool.setuptools]
packages = [
    "ketu",
    "ketu.ephemeris",
    "ketu.aspects",
    "ketu.cycles",
    "ketu.cache",
]
# ketu.export is REMOVED
```

### UPGRADING.md Structure (pandas 3.0 pattern)
```markdown
# Source: pandas 3.0.0 migration guide
# Upgrading from Ketu 0.4.0 to 1.0.0

## Overview

Ketu 1.0.0 removes optional export modules to focus on core astronomical calculations. This is a **breaking change** requiring code updates.

**Upgrade path:** Review this guide, update imports, then upgrade.

## Removed Features

### Chart Visualization (ketu.export.chart)
**Removed:** `draw_zodiacal_chart()`, matplotlib dependency

**Migration:**
- If you need chart visualization, copy `ketu/export/chart.py` from v0.4.0 into your project
- Or use dedicated astrology chart libraries

```python
# v0.4.0 (REMOVED)
from ketu.export import draw_zodiacal_chart
draw_zodiacal_chart(jd)

# v1.0.0 - No replacement
# Copy chart.py to your project if needed
```

### iCalendar Export (ketu.export.icalendar)
**Removed:** `export_lunations_to_ical()`, `export_transits_to_ical()`, icalendar dependency

**Migration:** Use ketu's aspect/transit data with icalendar library directly

### Optional Dependencies
**Removed:** `pip install ketu[chart]`, `pip install ketu[all]`

**Migration:** `pip install ketu` now only installs numpy

## Import Changes

All ketu functions now use **submodule imports**:

```python
# v0.4.0 (DEPRECATED)
from ketu import generate_cycle_series
from ketu import calculate_aspects

# v1.0.0 (REQUIRED)
from ketu.cycles import generate_cycle_series
from ketu.aspects import calculate_aspects
```

**What still works at top level:**
- `from ketu import bodies, aspects, signs` (constants)
- `from ketu import __version__`

## Installation

```bash
# Remove old version
pip uninstall ketu

# Install v1.0
pip install ketu==1.0.0

# No optional extras needed
```

## Quick Migration Checklist

- [ ] Search codebase for `from ketu import`
- [ ] Update to `from ketu.cycles import` or `from ketu.aspects import`
- [ ] Remove `ketu[chart]` from requirements.txt if present
- [ ] Test imports in clean virtual environment
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Flat namespace imports | Submodule imports | Python 3.7+ (PEP 562) | Faster import times, clearer API boundaries |
| Optional features via extras | Split packages or user-side integration | Scientific Python SPEC 1 (2023) | Smaller dependency trees, less version conflicts |
| setup.py configuration | pyproject.toml | PEP 621 (2020), standard since 2023 | Single source of truth for metadata |
| Deprecation warnings for major version | Clean breaks with migration docs | pandas 3.0 (2026), numpy 2.0 (2024) | Clearer migration path, less code maintenance |

**Deprecated/outdated:**
- **setup.py with setuptools.setup()**: Replaced by pyproject.toml (PEP 621). Still works but not recommended for new projects.
- **`from package import *` patterns**: Discouraged in modern Python. Explicit imports preferred.
- **Empty extras_require placeholders**: Previously recommended to avoid breaking downstream, but modern consensus is clean removal for major versions.
- **Stub modules with deprecation warnings**: pandas 3.0 and numpy 2.0 set precedent for clean breaks at major versions.

## Open Questions

1. **Should ketu expose core data structures at top level?**
   - What we know: `bodies`, `aspects`, `signs` are constants (dicts), not functions
   - What's unclear: User preference for `from ketu import bodies` vs `from ketu.core import bodies`
   - Recommendation: Keep constants at top level (zero import cost, high convenience). Update `__all__` in `ketu/__init__.py` to include them.

2. **Should UPGRADING.md include code snippets from ketu/export modules?**
   - What we know: Users may need chart functionality, no direct replacement
   - What's unclear: How much code to provide in migration guide vs "here's the old file path"
   - Recommendation: Provide file path to v0.4.0 modules, explain they can copy. Don't include full code in UPGRADING.md (too long, maintenance burden).

3. **Should cycles/ remain a package or flatten to single module?**
   - What we know: Currently `ketu/cycles/__init__.py` + `ketu/cycles/calculator.py` (only one implementation file)
   - What's unclear: Future expansion plans (more cycle calculators?)
   - Recommendation: Keep package structure. Single-module packages are common in Python (e.g., `typing`, `dataclasses`). Easier to add modules later than restructure package → module.

## Sources

### Primary (HIGH confidence)
- [Scientific Python SPEC 0 - Minimum Supported Dependencies](https://scientific-python.org/specs/spec-0000/) - Dependency policy, verified 2026-02-12
- [Scientific Python SPEC 1 - Lazy Loading](https://scientific-python.org/specs/spec-0001/) - Submodule import patterns, verified 2026-02-12
- [Real Python - Python's __all__](https://realpython.com/python-all-attribute/) - __all__ usage patterns, verified 2026-02-12
- [pandas 3.0.0 What's New](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html) - Migration guide structure, verified 2026-02-12
- [Setuptools - Package Discovery](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html) - Explicit vs auto package discovery, verified 2026-02-12

### Secondary (MEDIUM confidence)
- [Ben Hoyt - Designing Pythonic library APIs](https://benhoyt.com/writings/python-api-design/) - API design principles, date unknown but widely cited
- [Python Packaging Guide - Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) - Official packaging docs, verified 2026-02-12
- [pytest - Good Integration Practices](https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html) - Test organization, verified 2026-02-12

### Tertiary (LOW confidence)
- [Discussions on setuptools package discovery](https://github.com/pypa/setuptools/discussions/3346) - Community discussions, may not reflect current best practices

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - numpy is established standard, setuptools widely documented
- Architecture: HIGH - Scientific Python SPECs are authoritative, pandas 3.0 provides recent precedent
- Pitfalls: MEDIUM-HIGH - Based on common refactoring issues, verified with multiple sources
- UPGRADING.md patterns: HIGH - pandas 3.0 provides 2026 real-world example

**Research date:** 2026-02-12
**Valid until:** 2026-04-12 (60 days - packaging best practices stable, but verify dependency versions before Phase 6 release)

**Key assumptions:**
- User has independent ketu venv (verified in CLAUDE.md)
- Kala integration handled separately (Phase 7)
- swisseph already removed (verified in README.md, needs code confirmation)
- No external users besides Kala project (internal library, public-quality for future)
