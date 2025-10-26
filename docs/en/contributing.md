# Contributing to Ketu

We are happy to welcome your contributions! 🌟

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

# Install in development mode
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/my-new-feature
```

### 4. Develop and Test

```bash
# Run the test suite
pytest tests/

# Lint the codebase
flake8 ketu/

# Format the code
black ketu/
```

### 5. Commit with a Clear Message

```bash
git add .
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
- Google-style docstrings
- Type hints where they help readability
- Maximum 88 characters per line (Black default)

### Tests

- Minimum coverage target: 80%
- Use pytest for unit tests
- Mock Swiss Ephemeris calls when needed

### Documentation

- Document every new public function
- Include examples in docstrings
- Update the Sphinx docs when relevant

## Areas to Contribute

### 🎯 Current Priorities

1. **Pure NumPy migration**: Replace pyswisseph
2. **Exact aspect timing**: Find the precise moments aspects are exact

## Project Architecture

```
ketu/
├── ketu/
│   ├── __init__.py      # Public exports
│   ├── ketu.py          # Main module
├── tests/
│   ├── test_ketu.py
│   ├── test_ephemeris.py
│   └── fixtures/
├── docs/
│   └── source/
└── examples/
```

## Review Process

- ✅ Tests: the full suite must pass
- 📈 Coverage: do not decrease coverage
- 📝 Documentation: keep it current and clear
- 🎨 Style: respect the agreed conventions
- ⚙️ Performance: avoid regressions

## Resources

### Technical Documentation

- [Swiss Ephemeris](https://www.astro.com/swisseph/)

### Issues

- [GitHub Discussions](https://github.com/alkimya/ketu/discussions)
- [Issues](https://github.com/alkimya/ketu/issues)
- Email: [loc.cosnier@pm.me](mailto:loc.cosnier@pm.me)

### Documentation ReadTheDocs

- [Project documentation (Read the Docs)](https://ketu.readthedocs.io/)

## License

By contributing, you agree that your work will be released under the MIT License.
