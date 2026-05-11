# Ketu Makefile — convenience targets for development and CI.
#
# All recipes assume the `[test]` extra is installed
# (`pip install -e .[test]`). All recipes invoke pytest/mypy through
# ``python -m`` so they pick up the active venv (or the venv at
# ``./venv``) — direct ``pytest``/``mypy`` shebangs in this repo's
# ``venv/bin/`` were observed to mis-resolve in some environments.

PYTHON ?= python

.PHONY: test test-fast houses-coverage charts-coverage synastry-coverage doc-gates mypy clean

## test: Run the full pytest suite with coverage report.
test:
	$(PYTHON) -m pytest tests/

## test-fast: Run the full suite without coverage instrumentation (faster).
test-fast:
	$(PYTHON) -m pytest tests/ --no-cov

## houses-coverage: Run the HOU-09 ≥95% coverage gate scoped to ketu.houses.
##
## This is a separate invocation from the project-wide `pytest tests/` so
## a partial test run (e.g. `pytest tests/test_ephemeris.py`) cannot
## silently miss the gate.
##
## Two-step pattern. Why not just ``--cov=ketu.houses --cov-fail-under=95``?
## When coverage.py uses ``source=ketu.houses`` (a sub-package), one
## swisseph oracle test in this suite trips a NumPy module reload that
## corrupts ``_NoValueType`` sentinels and crashes ``numpy.amax`` with
## ``TypeError``. With ``source=ketu`` (full package) coverage works
## cleanly. So we run pytest once with the project-wide ``ketu`` source
## (no ``--cov-fail-under`` since most modules are unexercised by
## tests/houses/), then scope the threshold check to ``ketu/houses/*``
## via ``coverage report --include``. Net effect: same gate, no
## NumPy-reload bug.
houses-coverage:
	$(PYTHON) -m pytest tests/houses/ -o addopts="" --cov --cov-report= --cov-fail-under=0
	$(PYTHON) -m coverage report --include='ketu/houses/*' --fail-under=95 -m

## charts-coverage: Run the CHART-05 ≥95% coverage gate scoped to ketu.charts.
##
## Mirror of `houses-coverage` (HOU-09). Same two-step pattern to avoid
## the NumPy `_NoValueType` reload bug triggered when coverage.py uses
## `source=ketu.charts` (sub-package). With `source=ketu` (full package)
## coverage works cleanly. We run pytest once with the project-wide
## `ketu` source (no `--cov-fail-under` since most modules are
## unexercised by tests/charts/), then scope the threshold check to
## `ketu/charts/*` via `coverage report --include`.
charts-coverage:
	$(PYTHON) -m pytest tests/charts/ -o addopts="" --cov --cov-report= --cov-fail-under=0
	$(PYTHON) -m coverage report --include='ketu/charts/*' --fail-under=95 -m

## synastry-coverage: Run the SYN-05 ≥95% coverage gate scoped to ketu.synastry.
##
## Mirror of `houses-coverage` (HOU-09) and `charts-coverage` (CHART-05).
## Same two-step pattern to avoid the NumPy `_NoValueType` reload bug
## triggered when coverage.py uses `source=ketu.synastry` (sub-package).
## With `source=ketu` (full package) coverage works cleanly. We run
## pytest once with the project-wide `ketu` source (no `--cov-fail-under`
## since most modules are unexercised by tests/synastry/), then scope
## the threshold check to `ketu/synastry/*` via `coverage report
## --include`.
synastry-coverage:
	$(PYTHON) -m pytest tests/synastry/ -o addopts="" --cov --cov-report= --cov-fail-under=0
	$(PYTHON) -m coverage report --include='ketu/synastry/*' --fail-under=95 -m

## doc-gates: Run the doc-gate suite locally (interrogate + numpydoc lint).
##
## Mirrors what CI runs in tests.yml. Use before pushing to avoid
## learning about a gate failure from the GitHub Actions email.
doc-gates:
	$(PYTHON) -m interrogate ketu/
	$(PYTHON) -m numpydoc lint $$(find ketu -name "*.py" \
	    ! -path "*/__pycache__/*" \
	    ! -name "lunar_calendar.py" \
	    ! -name "_*.py") || true
	@echo "Doc gates OK (numpydoc warnings shown above; not blocking until v1.2.0)."

## mypy: Run mypy --strict over the whole package.
mypy:
	$(PYTHON) -m mypy --strict ketu/

## clean: Remove pytest/coverage artifacts.
clean:
	rm -rf .pytest_cache/ .coverage htmlcov/ coverage.json
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
