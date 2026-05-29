# Contributing to Ketu

We are happy to welcome your contributions!

## How to Contribute

### 1. Fork the Project

```bash
# Fork on GitHub and then clone
git clone https://github.com/alkimya/ketu.git
cd ketu
```

### 2. Set Up a Development Environment

```bash
# Create a virtual environment
python -m venv venv

# Install in development mode with all dev extras
pip install -e ".[dev]"
```

The `[dev]` extra installs pytest, pytest-cov, mypy, sphinx, myst-parser, interrogate, and other development tools.

### 3. Create a Branch

```bash
git checkout -b feature/my-new-feature
```

### 4. Develop and Test

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage check (must reach 100%)
pytest tests/ --cov=ketu --cov-fail-under=100

# Type checking (strict mode)
mypy ketu/

# Run doctests
pytest --doctest-modules ketu/ --no-cov

# Docstring coverage gate
interrogate ketu/ --fail-under 95

# Numpydoc lint
python -m numpydoc --validate ketu/
```

### 5. Commit with a Clear Message

```bash
git add src/module.py
git commit -m "feat: add house calculation"
```

Commit message prefixes:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation
- `style:` Formatting or code style
- `refactor:` Refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

### 6. Push and Open a Pull Request

```bash
git push origin feature/my-new-feature
```

Then open a PR on GitHub.

## Development Guidelines

### Code Style

- Follow PEP 8 for Python code
- NumPy-style docstrings (required for numpydoc gate)
- Type hints everywhere (mypy strict)
- Maximum 88 characters per line (Black default)

### Tests

- **Coverage target: 100%** (enforced via `fail_under=100` in CI)
- No `# pragma: no cover` annotations — unreachable branches are handled via `exclude_lines` in `pyproject.toml`
- Use pytest for unit tests
- Add doctests (`>>>`) for all public functions

### Documentation

- Document every new public function with NumPy-style docstrings
- Include `Examples` section with `>>>` prompts in docstrings (collected by `make doctest`)
- Update the Sphinx docs in `docs/source/` when adding features
- Use `from ketu.submodule import function` style — not `import ketu; ketu.function()`

### pyswisseph Policy

`pyswisseph` is **test/validation only** — it is never imported at runtime. Runtime code must be pure NumPy. This maintains AGPL isolation. If a new calculation requires Swiss Ephemeris data, generate offline coefficients (as was done for Chiron in v1.3) and embed them as `.npz` files.

## Project Architecture

```text
ketu/
├── __init__.py          # Public re-exports (bodies, aspects, signs, HOUSES_DTYPE…)
├── core.py              # Data structures: bodies (14), aspects, signs
├── calculations.py      # High-level API: long, lat, body_sign, is_retrograde…
├── display.py           # CLI display: print_positions, print_aspects, main
├── aspects/             # Configurable aspect sets (CLASSICAL/TRADITIONAL/EXTENDED)
├── houses/              # Six house systems + HOUSES_DTYPE + HighLatitudeError
├── charts/              # Full natal chart: compute_chart, is_day_chart, CHART_DTYPE
├── synastry/            # Inter-chart aspects: calculate_synastry, SYNASTRY_DTYPE
├── composite/           # Midpoint composite: calculate_composite, circular_midpoint
├── returns/             # Solar/lunar returns: solar_return, lunar_return
├── parts/               # Arabic Parts: PARTS, calculate_part, calculate_all_parts
├── data/                # Embedded coefficient data (chiron_coeffs.npz)
└── ephemeris/           # Pure NumPy astronomical engine
    ├── time.py          # Time conversions
    ├── orbital.py       # Orbital mechanics (re-export hub)
    ├── _elements.py     # ORBITAL_ELEMENTS + Lilith constants
    ├── _perturbations.py # Perturbation strategies
    ├── coordinates.py   # Coordinate transformations
    ├── planets.py       # Planetary position dispatch (BODY_STRATEGIES)
    └── chiron.py        # Chiron Chebyshev evaluator (v1.3)
tests/
├── conftest.py          # Shared session-scoped fixtures
├── test_ketu.py         # Top-level API tests
└── [subpackage tests]
```

## Quality Gates (CI)

All of the following must pass before merging:

| Gate | Command | Target |
|------|---------|--------|
| Tests | `pytest tests/` | All pass |
| Coverage | `pytest --cov=ketu --cov-fail-under=100` | 100% |
| Type check | `mypy ketu/` | 0 errors (strict) |
| Docstring coverage | `interrogate ketu/ --fail-under 95` | ≥95% |
| Numpydoc lint | `python -m numpydoc --validate ketu/` | 0 violations |
| Doctests | `pytest --doctest-modules ketu/ --no-cov` | All pass |

## Review Process

- Tests: the full suite must pass
- Coverage: must stay at 100% (no decrease allowed)
- Documentation: keep it current and clear
- Style: respect the agreed conventions
- Performance: avoid regressions

## Resources

### Technical Documentation

- [Swiss Ephemeris](https://www.astro.com/swisseph/) (validation only — not a runtime dependency)
- [NumPy documentation](https://numpy.org/doc/stable/)

### Issues

- [GitHub Discussions](https://github.com/alkimya/ketu/discussions)
- [Issues](https://github.com/alkimya/ketu/issues)
- Email: [loc.cosnier@pm.me](mailto:loc.cosnier@pm.me)

### Documentation ReadTheDocs

- [Project documentation (Read the Docs)](https://ketu.readthedocs.io/)

## License

By contributing, you agree that your work will be released under the MIT License.
