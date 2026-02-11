# External Integrations

**Analysis Date:** 2026-02-12

## Overview

Ketu is a **self-contained library with minimal external integrations**. It performs pure numerical computation without network calls or external APIs.

## APIs & External Services

**None**

Ketu does not depend on:
- Ephemeris web APIs (e.g., JPL Horizons, Astropy)
- Astrology data services
- Real-time feeds
- Third-party calculation services

All astronomical calculations are implemented in pure Python/NumPy using orbital elements and perturbation theory.

## Data Storage

**No persistent external storage used.**

**Local Cache (Optional):**
- Type: NumPy binary format (.npy files)
- Location: User's system cache directory (configurable in `EphemerisCache`)
- Contents: Pre-computed daily planetary positions (all 13 bodies)
- Module: `ketu/cache/ephemeris_cache.py`
- Persistence: Survives application restarts
- Clearing: Manual deletion of cache directory

**No database connections:**
- Ketu operates purely in-memory or with local file caching
- No SQL, PostgreSQL, or TimescaleDB integration

## Authentication & Identity

**None**

Ketu does not authenticate with external services or require API keys.

## Monitoring & Observability

**Error Tracking:**
- None

**Logs:**
- Standard Python logging (via `logging` module if needed by calling code)
- No external log aggregation

## CI/CD & Deployment

**Hosting & Distribution:**
- **PyPI** - Python Package Index (read-only)
  - Package: `ketu` (https://pypi.org/project/ketu/)
  - Publication: Via GitHub Actions workflow (manual trigger)
  - Automatic testing before publish

**Documentation Hosting:**
- **ReadTheDocs** - Sphinx HTML documentation
  - Primary: English (`docs/en/`)
  - Secondary: French (`docs/fr/`)
  - Auto-rebuild: On git push to main branch (when enabled)

**Code Repository:**
- **GitHub** (alkimya/ketu)
  - Read-only for Ketu library
  - GitHub Actions for CI/CD (test + publish workflows)

## Environment Configuration

**Required Environment Variables:**
- None

**Optional Environment Variables:**
- `XDG_CACHE_HOME` - Custom cache directory (used by `EphemerisCache`)
- If not set, uses system default (e.g., `~/.cache/` on Linux)

**Secrets Location:**
- None needed for library operation
- PyPI tokens stored in GitHub Actions secrets (for publishing)
  - `PYPI_API_TOKEN` - Production PyPI upload
  - `TEST_PYPI_API_TOKEN` - TestPyPI pre-release upload
  - `CODECOV_TOKEN` - Code coverage reporting (optional)

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Data Flow

### Input Sources

**User-provided data:**
1. **Timestamps** - UTC datetime objects or Julian dates
2. **Body names** - Astronomical bodies: Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, Rahu (Mean North Node), Ketu (Mean South Node), Lilith (Black Moon)

**Embedded data:**
- Orbital elements (J2000.0 epoch) hardcoded in `ketu/ephemeris/orbital.py`
- Aspect definitions hardcoded in `ketu/complex.py`
- Harmonic series hardcoded in `ketu/resonance.py`

### Output Destinations

**Programmatic output:**
- In-memory NumPy arrays (positions, velocities, aspects)
- Python data structures (dataclasses for `AspectWindow`, `TransitAspect`, etc.)
- Structured arrays for ML-ready feature generation

**File exports (optional):**
1. **SVG charts** - Zodiacal visualization via matplotlib (if installed)
   - Written to user-specified location
   - Module: `ketu/export.py` → `draw_zodiacal_chart()`

2. **iCalendar files** (.ics) - Aspect/lunation calendars
   - Written to user-specified location
   - Module: `ketu/export.py`
   - Functions: `export_lunations_to_ical()`, `export_aspects_to_ical()`, `export_transits_to_ical()`

3. **NumPy cache files** (.npy) - Ephemeris cache
   - Location: System cache directory (typically `~/.cache/ketu/`)
   - Module: `ketu/cache/ephemeris_cache.py`
   - Naming: `ephemeris_{year}_{month:02d}.npy`

## Integration Patterns in Solaris Ecosystem

**Within Solaris (when imported as dependency):**

Ketu is consumed by **Kala** (ML analysis module):
- Import: `from ketu import ...` in `kala/` code
- Data flow: Ketu provides cycle features → Kala generates ML signals
- No bidirectional communication

Ketu is independent of:
- **Soma** (data pipeline) - No coupling
- **Surya** (agent framework) - No coupling
- **Solaris** database - No direct database connection
  - (Note: Solaris framework may load cache-compatible data, but Ketu doesn't read from DB)

**Shared concepts:**
- Cycle phases (0-360 degrees)
- Body identifiers (Sun, Moon, planets)
- Timestamp formats (UTC aware datetime or Julian dates)

## Library-Only Characteristics

**No network I/O:**
- All calculations are deterministic (same inputs → same outputs)
- Fully reproducible results
- Can run offline completely

**No side effects:**
- No global state modifications
- No files written without user request
- Cache is optional and can be disabled

**Thread-safe aspects:**
- NumPy computations are thread-safe
- Cache implementation uses locking (`threading.Lock` in `EphemerisCache`)
- Aspect calculations are pure functions

---

*Integration audit: 2026-02-12*
