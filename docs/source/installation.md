# Installation

## Prerequisites

Ketu requires:

- Python 3.10 or higher
- pip (Python package manager)

## Stable Installation from PyPI

The simplest way to install Ketu:

```bash
pip install ketu
```

## Installation from Source

### Clone the Repository

```bash
git clone https://github.com/alkimya/ketu.git
cd ketu
```

### Development Mode Installation

```bash
pip install -e .
```

This method allows you to modify the source code and see changes immediately.

### Development Installation with Extras

For contributors, install the `[dev]` extra to get all testing and documentation tools:

```bash
pip install -e ".[dev]"
```

This installs pytest, coverage, mypy, sphinx, and other development dependencies.

## Installation in a Virtual Environment (Recommended)

### With venv

```bash
# Create the environment
python -m venv venv

# Install Ketu
pip install ketu
```

## Installation Verification

### Command Line

```bash
# Launch the interactive interface
ketu
```

### In Python

```python
import ketu
print(ketu.__version__)
# Output: 1.3.0
```

## Dependencies

Ketu uses the following libraries:

Library         |   Version |   Description
----------------|-----------|--------------
numpy           |   ≥1.20.0 |   Numerical computations and arrays

Ketu is a pure NumPy library at runtime. `pyswisseph` is used only for generating Chiron ephemeris coefficients (a build-time tool, not a runtime dependency).

## Uninstallation

```bash
pip uninstall ketu
```

## Next Steps

Once installed, see the [Quick Start Guide](quickstart.md) to begin using Ketu.
