"""Post-publish smoke test for ketu==1.8.0 (D-08).

Run with a FRESH venv that has ketu==1.8.0 installed FROM PyPI:

    python -m venv /tmp/ketu18smoke
    /tmp/ketu18smoke/bin/pip install --no-cache-dir ketu==1.8.0
    /tmp/ketu18smoke/bin/python smoke_v18.py

Prints SMOKE_OK on success; exits non-zero otherwise.
"""

import math
import sys

import numpy as np

# ---------------------------------------------------------------------------
# (a) body_decl_speed present in CHART_DTYPE
# ---------------------------------------------------------------------------
from ketu.charts import CHART_DTYPE  # type: ignore[import]

dtype_names = np.dtype(CHART_DTYPE).names
if "body_decl_speed" not in dtype_names:
    print(f"FAIL (a): body_decl_speed not in CHART_DTYPE fields: {dtype_names}")
    sys.exit(1)
print("(a) body_decl_speed in CHART_DTYPE.names — OK")

# ---------------------------------------------------------------------------
# (b) a test chart's body_decl_speed is finite and not all-zero
# ---------------------------------------------------------------------------
from ketu.charts import compute_chart  # type: ignore[import]
from ketu.calculations import utc_to_julian  # type: ignore[import]
from datetime import datetime, timezone

jd = utc_to_julian(datetime(2026, 6, 17, 12, 0, tzinfo=timezone.utc))
chart = compute_chart(jd, lat=48.85, lon=2.35)

speeds = chart["body_decl_speed"]
assert speeds.shape == (14,), f"Expected shape (14,), got {speeds.shape}"

if not all(math.isfinite(float(v)) for v in speeds):
    print(f"FAIL (b): body_decl_speed contains non-finite values: {speeds}")
    sys.exit(1)

if all(float(v) == 0.0 for v in speeds):
    print("FAIL (b): body_decl_speed is all-zero (not populated)")
    sys.exit(1)
print(f"(b) body_decl_speed populated — shape {speeds.shape}, finite, not all-zero — OK")

# ---------------------------------------------------------------------------
# (c) DECL_STANDSTILL_EPS importable from ketu.calculations
# ---------------------------------------------------------------------------
from ketu.calculations import DECL_STANDSTILL_EPS  # type: ignore[import]

if not (isinstance(DECL_STANDSTILL_EPS, float) and DECL_STANDSTILL_EPS > 0):
    print(f"FAIL (c): DECL_STANDSTILL_EPS has unexpected value: {DECL_STANDSTILL_EPS!r}")
    sys.exit(1)
print(f"(c) DECL_STANDSTILL_EPS = {DECL_STANDSTILL_EPS} — OK")

# ---------------------------------------------------------------------------
# (d) import swisseph raises ImportError (pyswisseph stayed test-only)
# ---------------------------------------------------------------------------
try:
    import swisseph  # noqa: F401
    print("FAIL (d): import swisseph succeeded — pyswisseph must NOT be a runtime dep")
    sys.exit(1)
except ImportError:
    print("(d) import swisseph raises ImportError — runtime stays pure NumPy — OK")

# ---------------------------------------------------------------------------
print()
print("SMOKE_OK")
