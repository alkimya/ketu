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

## Installation in a Virtual Environment (Recommended)

### With venv

```bash
# Create the environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install Ketu
pip install ketu
```

## Installation Verification

### Command Line

```bash
# Check that the command is available
ketu --help

# Launch the interactive interface
ketu
```

### In Python

```python
import ketu
print(ketu.__version__)
# Output: 0.2.0
```

## Dependencies

Ketu uses the following libraries:

Library         |   Version |   Description
----------------|-----------|--------------
numpy           |   ≥1.20.0 |   Numerical computations and arrays
pyswisseph      |   ≥2.10.0 |   Planetary ephemerides

## Uninstallation

```bash
pip uninstall ketu
```

## Next Steps

Once installed, see the [Quick Start Guide](quickstart.md) to begin using Ketu.
