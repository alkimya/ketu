# Contributing to Ketu

Thanks for taking the time to contribute — every improvement helps!

> Une version française de ce guide est disponible dans `fr/CONTRIBUTING.md`.

## Quick start

### Set up your development environment

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"
```

### Run the tests

Before opening a pull request, make sure the suite is green:

```bash
pytest tests/ -v --cov=ketu
```

You can target a specific test file if needed:

```bash
pytest tests/test_ketu.py -v
```

## Development guidelines

- Follow **PEP 8** for Python style (Black’s defaults are a good baseline).
- Add **type hints** whenever they improve readability.
- Document every public function with a concise **docstring** (Google style).
- Include unit tests for new features or bug fixes.

### Example docstring

```python
def calculate_aspect(jdate, body1, body2):
    """Return the aspect between two celestial bodies.

    Args:
        jdate (float): Julian day number.
        body1 (int): ID of the first body.
        body2 (int): ID of the second body.

    Returns:
        tuple[int, int, int, float] | None: (body1, body2, aspect_index, orb)
        or None if no aspect is detected.
    """
```

## Contribution workflow

1. **Fork** the repository.
2. **Create** a feature branch: `git checkout -b feature/my-feature`.
3. **Commit** with meaningful messages: `git commit -m "feat: add pure numpy ephemeris"`.
4. **Push** your branch: `git push origin feature/my-feature`.
5. **Open** a pull request on GitHub describing your changes.

### Commit messages

Use clear prefixes to convey the intent of a change:

- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation update
- `test`: tests only
- `refactor`: code changes that neither fix nor add a feature
- `chore`: maintenance, tooling, non-production code

## Report a bug

Open an issue on GitHub with:

- A clear description of the problem
- Steps to reproduce the bug
- Expected vs. observed behavior
- Your version of Python and Ketu
- A minimal code example if possible

## Suggest a feature

Before working on a major feature:

1. Open an issue to discuss it
2. Wait for feedback from the community
3. Once approved, start development

## Documentation

If you add or modify features:

1. Update the documentation in `/docs/source/`
2. Add usage examples
3. Update the [CHANGELOG.md](../CHANGELOG.md)

To generate documentation locally:

```bash
cd docs
make livehtml  # Launch a live reload documentation server
```

## Checklist before PR

- [ ] Tests pass (`pytest tests/`)
- [ ] Code coverage is maintained or improved
- [ ] Code follows PEP 8
- [ ] Docstrings are up to date
- [ ] The [CHANGELOG.md](../CHANGELOG.md) is up to date
- [ ] Documentation is updated if necessary

## Thank you

Every contribution, big or small, is appreciated. Whether it's:

- Correcting a typo in the documentation
- Adding tests
- Improving performance
- Suggesting new features

## Resources

- [Project documentation (Read the Docs)](https://ketu.readthedocs.io/)
- [Issue tracker](https://github.com/alkimya/ketu/issues)
- [Discussions](https://github.com/alkimya/ketu/discussions)
- Contact: [loc.cosnier@pm.me](mailto:loc.cosnier@pm.me)

## License

By contributing you agree that your code will be released under the MIT License.
