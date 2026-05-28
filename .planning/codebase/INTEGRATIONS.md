# External Integrations

**Analysis Date:** 2026-05-29

## Overview

**Ketu is a standalone library with zero runtime external service dependencies.** All calculations are pure NumPy (deterministic, fully offline). Ketu produces structured NumPy arrays for downstream ML consumption and feeds the Solaris trading ecosystem (Kala, Surya) but contains no bidirectional integrations, network calls, or authentication itself.

## APIs & External Services

**None in production.** Ketu is purely computational:
- No HTTP/REST APIs consumed
- No webhooks received or sent
- No rate-limited external oracles
- No API keys required or configured

Rationale: Ketu is a *library*, not a service. Consumers (Kala, Surya, user scripts) call Ketu's Python API to get arrays.

## Data Storage

**Databases:**
- None. Ketu stores no data in traditional databases (PostgreSQL, MongoDB, etc.)

**File Storage:**
- **Local filesystem only** - Ephemeris cache (optional, for performance):
  - Location: `~/.ketu/ephemeris_cache/` (configurable via `EphemerisCache(cache_dir=...)` in `ketu/cache/ephemeris_cache.py` line 66)
  - Format: NumPy binary (`.npy` files), one per month per body set
  - Size: ~230 KB/year for 13 bodies, ~19 KB/month
  - Lifecycle: Persistent across runs; created on-demand; user-managed (no automatic pruning)
  - Example file: `~/.ketu/ephemeris_cache/2026-05-ephemeris.npy`

**Caching:**
- In-memory cache: Python dicts in `EphemerisCache._memory_cache` (session-only, not persisted between interpreter runs unless explicitly saved)
- LRU memoization: `functools.lru_cache` for expensive calculations (e.g., `ketu.aspects.calculator.get_orb()` at line ~100)

## Authentication & Identity

**Auth Provider:**
- None required. Ketu is a pure computational library; no identity/auth model.

## Monitoring & Observability

**Error Tracking:**
- None (no error reporting service integrated)

**Logs:**
- **Approach:** Standard Python `logging` module (not integrated in core; CLI uses `print()` for output in `ketu/cli/formatters.py`)
- CLI writes to stdout (user-readable tables, JSON optional)
- Errors raised as Python exceptions (caller responsibility to handle/log)

## CI/CD & Deployment

**Hosting:**
- **PyPI** (Python Package Index) - Primary distribution channel
- **GitHub** (github.com/alkimya/ketu) - Source control and CI platform
- **Read the Docs** (ketu.readthedocs.io) - Auto-built documentation (referenced in `pyproject.toml` line 52)

**CI Pipeline:**
- **GitHub Actions** (free tier):
  - `.github/workflows/tests.yml` - Test suite on push/PR, all Python 3.10–3.13
  - `.github/workflows/publish.yml` - Build & publish on git tags
  - No external CI services (CircleCI, Travis, etc.)

**Trusted Publishing:**
- **OIDC (OpenID Connect)** via GitHub to PyPI (Phase 20, hardened)
- No PyPI API tokens stored in repo (`publish.yml` uses `pypa/gh-action-pypi-publish@release/v1` with `permissions.id-token: write`)
- Eliminates credential rotation burden; leverages GitHub-issued ephemeral JWTs

## Environment Configuration

**Required env vars:**
- None. Ketu runs with zero mandatory environment variables.

**Optional env vars:**
- None documented or used in code.

**Secrets location:**
- No secrets in codebase. PyPI publishing uses OIDC trusted publishing (no API keys).

## Webhooks & Callbacks

**Incoming:**
- None. Ketu does not expose or consume webhooks.

**Outgoing:**
- None. Ketu does not make outbound API calls or fire webhooks.

## Test-Only Oracle: pyswisseph

**Purpose:** Validation and cross-checking of Ketu's pure-NumPy calculations against the industry-standard Swiss Ephemeris C library.

**Integration Pattern:**
- **Dependency:** `pyswisseph` ≥2.10.0 in `pyproject.toml` line 43 (`[project.optional-dependencies] test`)
- **License:** AGPL-3.0 (pyswisseph) — incompatible with Ketu's MIT license at runtime
- **Isolation Strategy:** Test-only via `pytest.importorskip("swisseph")` gates in:
  - `tests/houses/conftest.py` (lines 32–50) - oracle helper for house cusp validation
  - `tests/charts/conftest.py` (lines 32–50) - oracle helper for chart validation
  - `tests/returns/conftest.py` - oracle for return chart validation
  - `tests/test_lilith_cross_check.py` - black moon (Lilith) formula validation
  - `tests/houses/test_lst_obliquity_precision.py` - obliquity and LST cross-checks
  - `ketu.houses` and `ketu.charts` modules: pure NumPy, zero swisseph imports (verified by test at `tests/houses/test_integration.py` and `tests/charts/test_compute_chart.py`)
- **Workflow:**
  1. Module-level `pytest.importorskip("swisseph")` skips entire test module if swisseph absent
  2. Then `import swisseph as swe` (mypy overrides at `pyproject.toml` lines 144–146 ignore missing stubs)
  3. Oracle functions call `swe.calc_ut()`, `swe.houses_ex()`, etc.
  4. Returns compared against Ketu's NumPy calculations
- **Critical Constraint:** NumPy must be imported BEFORE swisseph (see `tests/houses/conftest.py` lines 34–43) to prevent `_NoValueType` sentinel mismatch when coverage.py reloads modules mid-flight
- **Result:** Ketu shipped product is MIT-clean, AGPL-uncontaminated; test suite can leverage pyswisseph for validation without licensing conflict

## Downstream Consumers (Solaris Ecosystem)

**Not integrations into Ketu, but Ketu is a dependency for:**

**Kala (sibling project):**
- Consumes: `ketu` library via pip dependency
- Adapter: KetuDataAdapter (in separate Kala codebase, not in Ketu repo)
- Data flow: Ketu outputs numpy arrays (`CHART_DTYPE`, `CYCLE_DTYPE`, etc.) → Kala ingests for ML training
- Dependency version: v1.1+ (v1.0 migration required; see `UPGRADING.md` ASP-04 section)
- Key change in v1.1: `aspects=CLASSICAL` default; Kala explicitly opts into `aspects=EXTENDED` to match v1.0 behavior (1284 tests verify no regression)

**Surya (trading agent):**
- Consumes: `ketu` library for ephemeris/cycle calculations
- Integration: Python API calls (no separate adapter documented)

**No return integrations:** Ketu does not import or depend on Kala, Surya, or other Solaris components. Ketu is **upstream-only** in the dependency graph.

## Package Distribution

**PyPI Publishing (OIDC Trusted):**
- Registry: https://pypi.org/project/ketu/
- Current version: 1.2.0 (published 2026-05-28)
- Build artifact types: sdist (`.tar.gz`), wheel (`.whl`)
- Trigger: Git tag push matching `v*.*.*` → GitHub Action → OIDC JWT → PyPI
- Validation gate: twine check (prevents malformed metadata; `publish.yml` line 22)

## Documentation Hosting

**Read the Docs:**
- URL: https://ketu.readthedocs.io
- Build trigger: webhook on GitHub push (auto-docs via RTD integration)
- Source: `docs/` directory (Sphinx + numpydoc)
- No authentication required; public read access

## Summary: No External Runtime Dependencies

| Category | Status | Notes |
|----------|--------|-------|
| HTTP APIs | None | Pure NumPy calculations |
| Databases | None | Optional local cache only |
| Auth/OAuth | None | Not a service |
| Webhooks | None | Stateless library |
| Monitoring | None | Caller responsibility |
| Secrets | None | OIDC trusted publishing |
| External Oracles | pyswisseph (test-only) | AGPL isolated, zero runtime contamination |

---

*Integration audit: 2026-05-29*
