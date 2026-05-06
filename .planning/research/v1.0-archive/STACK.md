# Technology Stack

**Project:** Ketu 1.0 Consolidation
**Researched:** 2026-02-12
**Context:** Brownfield - stack already established, this documents what exists and any needed updates

## Recommended Stack (Existing)

### Core Dependencies

| Technology | Current | Recommended | Purpose | Why |
|------------|---------|-------------|---------|-----|
| Python | 3.11+ | 3.11+ | Runtime | Already established, 3.11+ for performance and typing improvements |
| NumPy | 1.x | 2.x if available | Structured arrays, vectorization | Core of numerical API, consider NumPy 2.0 migration for performance |
| swisseph | Latest | Latest | Swiss Ephemeris calculations | No alternatives, industry standard for astronomical calculations |

### Development Dependencies

| Technology | Current | Recommended | Purpose | Why |
|------------|---------|-------------|---------|-----|
| pytest | Latest | Latest | Test framework | Standard for Python scientific packages |
| pytest-cov | Latest | Latest | Coverage reporting | Track 70% coverage target |
| mypy | Latest | Latest | Static type checking | Enforce type hints in CI |
| ruff | N/A | Add | Linting + formatting | Replace flake8/black with single fast tool |
| hypothesis | N/A | Add (optional) | Property-based testing | For numerical invariant testing (post-1.0) |

### Documentation Dependencies

| Technology | Current | Recommended | Purpose | Why |
|------------|---------|-------------|---------|-----|
| Sphinx | Unknown | Latest | Doc generation | Standard for Python projects |
| numpydoc | Unknown | Latest | NumPy docstring format | Parse NumPy-style docstrings |
| sphinx-rtd-theme | Unknown | Latest | ReadTheDocs theme | Clean, searchable docs |

### Build & Packaging

| Technology | Current | Recommended | Purpose | Why |
|------------|---------|-------------|---------|-----|
| setuptools | Unknown | setuptools or hatch | Package building | Already on PyPI, maintain compatibility |
| pyproject.toml | Unknown | Required | PEP 621 metadata | Modern Python packaging standard |
| build | Unknown | Latest | Build backend | PEP 517 compliant building |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| Ephemeris | swisseph | JPL Horizons | Horizons is web API, need offline calculations |
| Ephemeris | swisseph | pyephem | pyephem less accurate, less maintained |
| Ephemeris | swisseph | astropy.coordinates | Overkill dependency, slower for time series |
| Arrays | NumPy | pandas | NumPy is lighter, pandas is consumer not producer |
| Testing | pytest | unittest | pytest more features, better error messages |
| Linting | ruff | flake8 + black | ruff is 10-100x faster, single tool |
| Typing | mypy | pyright | mypy more mature for scientific Python |
| Docs | Sphinx | MkDocs | Sphinx standard for scientific Python, better API docs |

## Installation

### Production
```bash
pip install ketu
```

### Development
```bash
git clone https://github.com/user/ketu.git
cd ketu
python -m venv venv
source venv/bin/activate
pip install -e ".[dev,docs]"
```

### With optional dependencies (if any added)
```bash
pip install ketu[benchmark]  # Performance testing
pip install ketu[validation]  # External validation tools
```

## Dependency Philosophy

**Minimize production dependencies** - Only swisseph and NumPy are required. Every additional dependency:
- Increases installation complexity
- Adds security surface
- Creates version compatibility issues
- Slows import time

**Examples of dependencies to avoid:**
- pandas (users can convert structured arrays themselves)
- matplotlib (visualization is user responsibility)
- requests (no web APIs in calculation library)
- pydantic (validation can be done with stdlib + NumPy)

**When to add a dependency:**
- Required for core calculation functionality
- No reasonable pure-Python alternative
- Widely adopted in scientific Python ecosystem
- Stable API and active maintenance

## Python Version Support

**Recommended policy:** Follow NEP 29 (NumPy Enhancement Proposal 29)
- Support last 42 months of Python releases
- Drop Python version 2 years after next version release
- Clear communication in changelog when dropping support

**For 1.0 release (2026):**
- Minimum: Python 3.11 (released Oct 2022, ~3.5 years old)
- Maximum: Python 3.13+ (test in CI)
- Drop 3.10 support (if not already) before 1.0

**Testing matrix:**
```yaml
# In CI
python-version: ["3.11", "3.12", "3.13"]
os: [ubuntu-latest, macos-latest, windows-latest]
```

## NumPy Compatibility

**Critical decision:** NumPy 1.x vs 2.x

NumPy 2.0 was released in 2024 with breaking changes. For 1.0:

**Option A: NumPy 1.x only (Conservative)**
```toml
[project]
dependencies = ["numpy>=1.20,<2.0"]
```
- Pro: No migration work, stable
- Con: Missing NumPy 2.0 performance improvements

**Option B: NumPy 1.x + 2.x (Flexible)**
```toml
[project]
dependencies = ["numpy>=1.20"]
```
- Pro: Users choose their NumPy version
- Con: Must test both 1.x and 2.x in CI, handle compatibility

**Option C: NumPy 2.x only (Forward-looking)**
```toml
[project]
dependencies = ["numpy>=2.0"]
```
- Pro: Best performance, simpler testing
- Con: Forces users to upgrade, may break downstream packages

**Recommendation for 1.0: Option B (Flexible)** - Support both NumPy 1.x and 2.x with compatibility layer if needed. Test both in CI matrix.

## Type Checking Configuration

For `mypy.ini` or `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true  # All public functions must be typed
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_equality = true

[[tool.mypy.overrides]]
module = "swisseph.*"
ignore_missing_imports = true  # swisseph has no type stubs
```

## Linting Configuration

For `ruff.toml` or `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "NPY", # NumPy-specific rules
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["D"]  # No docstrings required in tests
```

## Testing Configuration

For `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
addopts = [
    "--cov=ketu",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--strict-markers",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "numerical: marks tests requiring external validation data",
]
```

## CI/CD Stack

| Tool | Purpose | Why |
|------|---------|-----|
| GitHub Actions | CI/CD | Free for public repos, good Python support |
| pytest | Test execution | Industry standard |
| codecov or coveralls | Coverage reporting | Track 70% target over time |
| PyPI trusted publishing | Package releases | Secure, no API tokens needed |

## Sources

**Confidence: HIGH**

Stack decisions based on:
- Existing Ketu codebase (swisseph + NumPy already established)
- Python packaging standards (PEP 621, PEP 517)
- NEP 29 (NumPy Enhancement Proposal 29 for version support)
- Scientific Python Ecosystem Coordination (SPEC) guidelines
- Observation of mature scientific Python projects (scipy, scikit-learn patterns)

**No changes recommended to production dependencies** - swisseph + NumPy is the right minimal stack.

**Changes recommended for development:**
1. Add mypy for type checking enforcement
2. Add ruff for modern linting/formatting
3. Consider hypothesis for property-based testing (post-1.0)
4. Formalize Python version support policy (NEP 29)
5. Decide NumPy 1.x vs 2.x compatibility strategy
