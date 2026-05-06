"""Capture v1.0 baseline timings for calculate_aspects_batch().

Reference point for ASP-08 ≤5% regression HARD GATE (Phase 9). Supports
``--aspect-set {classical,traditional,extended}``; default ``extended`` matches
v1.0 behavior of iterating all 14 aspects.

This script is the single source of truth for the v1.0 timing baseline used by
Wave 3 to verify the regression budget. It is owned by Plan 09-01 and MUST NOT
be modified by Plan 09-05 — Wave 3 only consumes it.

Usage
-----
Capture v1.0 baseline (default --aspect-set extended)::

    python tests/benchmark_aspects_batch.py \\
        --capture .planning/phases/09-configurable-aspects/baseline-v1.0.json

Compare against captured baseline (Wave 3, uses recorded aspect_set automatically)::

    python tests/benchmark_aspects_batch.py \\
        --compare .planning/phases/09-configurable-aspects/baseline-v1.0.json

Phase 9 fast-path benchmark with classical preset (Wave 3, post-09-04a)::

    python tests/benchmark_aspects_batch.py \\
        --capture /tmp/phase9-classical.json --aspect-set classical
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import numpy as np

from ketu.aspects.calculator import calculate_aspects_batch
from ketu.calculations import utc_to_julian


BENCH_DATES_BATCH_SIZES: list[int] = [30, 90, 365]
ANCHOR: datetime = datetime(2025, 1, 1, tzinfo=timezone.utc)
ASPECT_SET_CHOICES: list[str] = ["classical", "traditional", "extended"]
DEFAULT_ASPECT_SET: str = "extended"
WARMUP_ITERATIONS: int = 5
DEFAULT_ITERATIONS: int = 50


def build_jd_array(n_dates: int) -> np.ndarray:
    """Build a daily Julian Date array of ``n_dates`` entries anchored at ``ANCHOR``.

    Parameters
    ----------
    n_dates : int
        Number of consecutive daily dates to build.

    Returns
    -------
    numpy.ndarray
        1-D float64 array of Julian Dates.
    """
    return np.array(
        [utc_to_julian(ANCHOR + timedelta(days=i)) for i in range(n_dates)],
        dtype=np.float64,
    )


def _git_sha() -> str:
    """Return the current git HEAD SHA (40 hex chars), or ``"unknown"`` on failure."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        if len(sha) == 40 and all(c in "0123456789abcdef" for c in sha):
            return sha
        return "unknown"
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return "unknown"


def _call_with_aspect_set(jd_array: np.ndarray, aspect_set: str) -> Any:
    """Invoke calculate_aspects_batch with graceful fallback for v1.0 HEAD.

    On a Phase-9-aware HEAD, calls
    ``calculate_aspects_batch(jd_array, aspects=aspect_set)``.
    On v1.0 HEAD (Plan 09-04a not yet landed), falls back to
    ``calculate_aspects_batch(jd_array)`` — but ONLY if ``aspect_set`` is
    ``"extended"`` (the v1.0 default). Other values raise.

    Parameters
    ----------
    jd_array : numpy.ndarray
        Array of Julian Dates.
    aspect_set : str
        Aspect set name.

    Returns
    -------
    Any
        Whatever ``calculate_aspects_batch`` returns (list of structured arrays).

    Raises
    ------
    RuntimeError
        If the v1.0 fallback was triggered and ``aspect_set != "extended"``.
    """
    try:
        return calculate_aspects_batch(jd_array, aspects=aspect_set)  # type: ignore[call-arg]
    except TypeError as exc:
        msg = str(exc)
        # Narrowly scope the fallback to the missing 'aspects' kwarg only.
        if "aspects" not in msg or "unexpected keyword argument" not in msg:
            raise
        if aspect_set != "extended":
            raise RuntimeError(
                f"v1.0 HEAD only supports --aspect-set extended; got {aspect_set}. "
                "Plan 09-04a (the calculator refactor that wires the 'aspects' kwarg) "
                "has not landed yet. Re-run with --aspect-set extended for the "
                "apples-to-apples v1.0 baseline, or wait until Wave 3."
            )
        return calculate_aspects_batch(jd_array)


def bench_one(
    jd_array: np.ndarray,
    aspect_set: str,
    iterations: int = DEFAULT_ITERATIONS,
) -> dict[str, Any]:
    """Benchmark ``calculate_aspects_batch`` for a single batch size.

    Performs ``WARMUP_ITERATIONS`` warmup calls (results discarded) followed by
    ``iterations`` measured calls timed via :func:`time.perf_counter`.

    Parameters
    ----------
    jd_array : numpy.ndarray
        Pre-built array of Julian Dates (timed call does NOT include array build).
    aspect_set : str
        One of ``"classical"``, ``"traditional"``, ``"extended"``.
    iterations : int, optional
        Number of measured iterations (default 50).

    Returns
    -------
    dict
        Dictionary with keys ``n_dates``, ``iterations``, ``aspect_set``,
        ``mean``, ``median``, ``std``, ``min``, ``max`` — timings in seconds.
    """
    # Warmup
    for _ in range(WARMUP_ITERATIONS):
        _call_with_aspect_set(jd_array, aspect_set)

    # Measure
    timings: list[float] = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _call_with_aspect_set(jd_array, aspect_set)
        t1 = time.perf_counter()
        timings.append(t1 - t0)

    return {
        "n_dates": int(jd_array.shape[0]),
        "iterations": int(iterations),
        "aspect_set": aspect_set,
        "mean": float(statistics.mean(timings)),
        "median": float(statistics.median(timings)),
        "std": float(statistics.stdev(timings)) if len(timings) > 1 else 0.0,
        "min": float(min(timings)),
        "max": float(max(timings)),
    }


def run_all_sizes(aspect_set: str, iterations: int = DEFAULT_ITERATIONS) -> dict[str, dict[str, Any]]:
    """Run :func:`bench_one` for every batch size in ``BENCH_DATES_BATCH_SIZES``.

    Parameters
    ----------
    aspect_set : str
        Aspect set to exercise.
    iterations : int, optional
        Per-size iteration count.

    Returns
    -------
    dict
        Mapping ``str(n_dates) -> result dict``.
    """
    results: dict[str, dict[str, Any]] = {}
    for n in BENCH_DATES_BATCH_SIZES:
        jd_array = build_jd_array(n)
        results[str(n)] = bench_one(jd_array, aspect_set, iterations=iterations)
    return results


def _format_seconds(seconds: float) -> str:
    """Format a duration in seconds with a sensible unit."""
    if seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"
    if seconds < 1.0:
        return f"{seconds * 1e3:.2f} ms"
    return f"{seconds:.3f} s"


def _print_results(results: dict[str, dict[str, Any]], aspect_set: str) -> None:
    """Print human-readable benchmark results to stdout."""
    print(f"calculate_aspects_batch benchmark — aspect_set={aspect_set}")
    print(f"Python {sys.version.split()[0]}, NumPy {np.__version__}")
    print("-" * 70)
    for n in BENCH_DATES_BATCH_SIZES:
        r = results[str(n)]
        print(f"  batch_size={n:>4}  iter={r['iterations']:>3}")
        print(
            f"    mean={_format_seconds(r['mean'])} ± {_format_seconds(r['std'])}  "
            f"median={_format_seconds(r['median'])}  "
            f"min={_format_seconds(r['min'])}  max={_format_seconds(r['max'])}"
        )


def _capture(path: str, aspect_set: str, iterations: int) -> None:
    """Run benchmarks and write a JSON capture file at ``path``."""
    results = run_all_sizes(aspect_set, iterations=iterations)
    payload: dict[str, Any] = {
        "version": "v1.0-baseline",
        "git_sha": _git_sha(),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "aspect_set": aspect_set,
        "bench": results,
    }
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
        f.write("\n")
    _print_results(results, aspect_set)
    print()
    print(f"Captured baseline -> {path}")
    print(f"  version    = {payload['version']}")
    print(f"  git_sha    = {payload['git_sha']}")
    print(f"  aspect_set = {payload['aspect_set']}")


def _compare(
    path: str,
    cli_aspect_set: str | None,
    iterations: int,
    threshold_pct: float = 5.0,
) -> int:
    """Compare current performance against a captured baseline.

    Reads ``baseline["aspect_set"]`` and uses it as the source of truth. If a
    CLI ``--aspect-set`` value was provided AND it disagrees with the baseline,
    exits non-zero with a clear ``aspect_set mismatch`` error to prevent silent
    apples-to-oranges drift.

    Parameters
    ----------
    path : str
        Path to baseline JSON file.
    cli_aspect_set : str or None
        Value of ``--aspect-set`` from the CLI, or ``None`` if user did not pass it.
    iterations : int
        Per-size iteration count for the comparison run.
    threshold_pct : float, optional
        Regression threshold in percent. Default 5.0 (ASP-08 hard gate).

    Returns
    -------
    int
        ``0`` if all batch sizes are within ``+threshold_pct`` of baseline,
        non-zero otherwise (regression detected, or aspect_set mismatch).
    """
    with open(path, "r", encoding="utf-8") as f:
        baseline: dict[str, Any] = json.load(f)

    baseline_aspect_set: str = baseline["aspect_set"]
    if cli_aspect_set is not None and cli_aspect_set != baseline_aspect_set:
        print(
            f"ERROR: aspect_set mismatch: baseline={baseline_aspect_set}, "
            f"requested={cli_aspect_set} — apples-to-apples comparison requires "
            f"the same aspect_set. Either omit --aspect-set (will use "
            f"{baseline_aspect_set}) or pass --aspect-set {baseline_aspect_set}.",
            file=sys.stderr,
        )
        return 2

    aspect_set = baseline_aspect_set
    print(f"Comparing against {path} (aspect_set={aspect_set})")
    current = run_all_sizes(aspect_set, iterations=iterations)

    print("-" * 70)
    max_regression = -float("inf")
    for n in BENCH_DATES_BATCH_SIZES:
        key = str(n)
        baseline_mean = float(baseline["bench"][key]["mean"])
        current_mean = float(current[key]["mean"])
        delta_pct = (current_mean - baseline_mean) / baseline_mean * 100.0
        sign = "+" if delta_pct >= 0 else ""
        print(
            f"  batch_size={n:>4}  baseline={_format_seconds(baseline_mean)}  "
            f"current={_format_seconds(current_mean)}  delta={sign}{delta_pct:.2f}%"
        )
        max_regression = max(max_regression, delta_pct)

    print("-" * 70)
    if max_regression > threshold_pct:
        print(
            f"REGRESSION: max delta {max_regression:+.2f}% exceeds "
            f"+{threshold_pct:.2f}% gate (ASP-08 HARD GATE)",
            file=sys.stderr,
        )
        return 1
    print(f"OK: max delta {max_regression:+.2f}% within +{threshold_pct:.2f}% gate")
    return 0


def main() -> int:
    """CLI entry point. Returns process exit code."""
    parser = argparse.ArgumentParser(
        description="Benchmark calculate_aspects_batch — Phase 9 ASP-08 reference.",
    )
    parser.add_argument(
        "--capture",
        metavar="PATH",
        help="Run benchmark and write JSON capture to PATH.",
    )
    parser.add_argument(
        "--compare",
        metavar="PATH",
        help="Run benchmark and compare against captured baseline at PATH.",
    )
    parser.add_argument(
        "--aspect-set",
        choices=ASPECT_SET_CHOICES,
        default=None,
        help=(
            f"Aspect preset to exercise (default {DEFAULT_ASPECT_SET}). "
            "In --compare mode, must match baseline['aspect_set'] if provided."
        ),
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help=f"Measured iterations per batch size (default {DEFAULT_ITERATIONS}).",
    )
    args = parser.parse_args()

    if args.capture and args.compare:
        parser.error("--capture and --compare are mutually exclusive")

    cli_aspect_set: str | None = args.aspect_set
    effective_aspect_set: str = cli_aspect_set if cli_aspect_set is not None else DEFAULT_ASPECT_SET

    try:
        if args.compare:
            return _compare(args.compare, cli_aspect_set, args.iterations)
        if args.capture:
            _capture(args.capture, effective_aspect_set, args.iterations)
            return 0
        # Default: print to stdout
        results = run_all_sizes(effective_aspect_set, iterations=args.iterations)
        _print_results(results, effective_aspect_set)
        return 0
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
