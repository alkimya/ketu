# Technology Stack

**Analysis Date:** 2026-05-29

## Languages

**Primary:**
- Python 3.10–3.13 - Core library and runtime (via `requires-python = ">=3.10"` in `pyproject.toml`)

**Secondary:**
- None (pure Python; no C/Cython extensions in Ketu itself — pyswisseph is test-only)

## Runtime

**Environment:**
- Python 3.10, 3.11, 3.12, 3.13 (matrix tested in `.github/workflows/tests.yml`)

**Package Manager:**
- pip (standard)
- Lockfile: `requirements.txt` (minimal; contains only `numpy>=1.20.0`)

## Frameworks

**Core:**
- **NumPy** ≥1.20.0 - ONLY runtime dependency; structured arrays for ML interop, vectorized astronomical calculations

**Testing:**
- **pytest** - Test runner (installed via CI in `tests.yml` line 29)
- **pytest-cov** - Coverage reporting (installed via CI line 29)
- **coverage.py** - Code coverage (configured in `pyproject.toml` lines 87–102; fail-under=70 global, modular gates at 95%)

**Build/Dev:**
- **setuptools** ≥61.0 - Package build backend (in `pyproject.toml` line 2 `[build-system]`)
- **wheel** - Wheel distribution format (in `pyproject.toml` line 2 `[build-system]`)
- **build** - Build frontend (installed in `publish.yml` line 17)
- **interrogate** ≥1.7.0 - Docstring coverage audit (≥95% gate; blocking in `tests.yml` line 49, `pyproject.toml` lines 104–118)
- **numpydoc** ≥1.10.0 - NumPy docstring style validator (blocking in `tests.yml` lines 51–59, `pyproject.toml` lines 120–135)
- **mypy** - Static type checker (installed in `tests.yml` line 38 for Python 3.11 run; `pyproject.toml` lines 137–162 config)
- **twine** - PyPI validation (installed in `publish.yml` line 22)

## Key Dependencies

**Critical:**
- **numpy** ≥1.20.0 - Sole runtime dependency; used throughout for structured arrays (`CHART_DTYPE`, `SYNASTRY_DTYPE`, `CYCLE_DTYPE`, `HOUSES_DTYPE`, `PARTS_DTYPE`), vectorized calculations in `ketu.ephemeris`, `ketu.aspects`, `ketu.calculations`

**Infrastructure (test-only, optional):**
- **pyswisseph** ≥2.10.0 - Ephemeris oracle for validation tests only (in `pyproject.toml` line 43 `[project.optional-dependencies] test`). AGPL-licensed; isolated behind `pytest.importorskip("swisseph")` gates in `tests/houses/conftest.py`, `tests/charts/conftest.py`, `tests/returns/conftest.py`, `tests/test_lilith_cross_check.py` to prevent runtime contamination. Never imported into Ketu proper (`ketu/` package); zero AGPL exposure in shipped library.

## Configuration

**Environment:**
- No `.env` files required or consumed; Ketu is stateless
- CLI accepts user input interactively (date, time, timezone) via stdin
- Ephemeris cache directory: `~/.ketu/ephemeris_cache` (hardcoded default in `ketu/cache/ephemeris_cache.py` line 76; user-customizable via `EphemerisCache(cache_dir=...)` parameter)

**Build:**
- `pyproject.toml` - Project metadata, dependencies, tool configs (setuptools, pytest, coverage, interrogate, numpydoc, mypy)
- `Makefile` - Development convenience targets:
  - `make test` - Full pytest suite with coverage
  - `make test-fast` - No coverage instrumentation
  - `make houses-coverage` - HOU-09 ≥95% gate for `ketu.houses` (two-step pattern to avoid NumPy reload bug; lines 21–39)
  - `make charts-coverage` - CHART-05 ≥95% gate for `ketu.charts` (lines 41–52)
  - `make synastry-coverage` - SYN-05 ≥95% gate for `ketu.synastry` (lines 54–66)
  - `make composite-coverage` - COMP-05 ≥95% gate for `ketu.composite` (lines 68–80)
  - `make returns-coverage` - RET-06 ≥95% gate for `ketu.returns` (lines 82–94)
  - `make parts-coverage` - PARTS ≥95% gate for `ketu.parts` (lines 96–107)
  - `make doc-gates` - Runs interrogate + numpydoc lint locally (lines 109–119)
  - `make mypy` - Type-check with strict mode (lines 121–123)
  - `make clean` - Remove artifacts (lines 125–129)

## Platform Requirements

**Development:**
- Python 3.10+ with venv (repository uses `venv/` not `.venv/` per `CLAUDE.md`)
- Unix-like shell (bash/zsh) for Makefile recipes and CI scripts
- Git for version control

**Production:**
- Python 3.10–3.13
- NumPy ≥1.20.0
- ~230 KB/year for optional ephemeris cache (stored locally in `~/.ketu/ephemeris_cache/`; `.npy` format)
- No network access required (fully offline-capable)
- No external services (pure NumPy calculations)

## CI/CD Configuration

**Tests Workflow (`.github/workflows/tests.yml`):**
- Trigger: `push` to `main` or `develop`; `pull_request` to `main`; manual `workflow_dispatch`
- Runs on: `ubuntu-latest`
- Matrix: Python 3.10, 3.11, 3.12, 3.13
- Actions versions (Node.js 24, hardened Phase 20):
  - `actions/checkout@v5`
  - `actions/setup-python@v6`
  - `codecov/codecov-action@v5`
- Steps:
  - Install deps: pip, `[dev]` extra optional, pytest, pytest-cov
  - Run tests: pytest with coverage (all versions)
  - Type check: mypy --strict (Python 3.11 only)
  - Coverage threshold: ≥70% (Python 3.13 only)
  - Doc coverage: interrogate ≥95% (Python 3.13 only)
  - Doc style: numpydoc lint (Python 3.13 only, blocking)
  - Upload coverage: Codecov (Python 3.13 only)

**Publish Workflow (`.github/workflows/publish.yml`):**
- Trigger: Git tags matching `v*.*.*` (semantic versioning)
- Runs on: `ubuntu-latest`
- Jobs:
  1. **Build** (`build` job, Python 3.11):
     - Checkout, setup Python
     - Install: pip, build
     - Build: `python -m build --sdist --wheel`
     - Validate: twine check (safety gate)
     - Upload artifact: `python-package-distributions`
  2. **Publish to PyPI** (`publish-to-pypi` job):
     - Depends on: `build` job
     - Auth: OIDC trusted publishing (no API tokens in repo; GitHub environment `pypi` with OIDC provider)
     - Permissions: `id-token: write`
     - Download artifact, publish: `pypa/gh-action-pypi-publish@release/v1`

## Version

Current: **1.2.0** (shipped to PyPI 2026-05-28 via OIDC trusted publishing)

---

*Stack analysis: 2026-05-29*
