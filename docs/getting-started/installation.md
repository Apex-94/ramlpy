# Installation

## Requirements

- Python 3.6 or later (up to 3.14)
- pip package manager

## Installing ramlpy

### Basic Installation

To install ramlpy with its core dependencies:

```bash
pip install ramlpy
```

This installs:
- `ruamel.yaml>=0.17.0` - YAML parsing
- `python-dateutil>=2.8.0` - Datetime parsing
- `jsonschema>=3.0.0` - JSON Schema validation
- `typing_extensions>=3.7` - Type hints (Python < 3.10 only)

### With Flask Integration

If you plan to use ramlpy with Flask:

```bash
pip install ramlpy[flask]
```

This additionally installs:
- `Flask>=1.0` - Flask web framework

### For Development

If you want to contribute to ramlpy or run its tests:

```bash
pip install ramlpy[dev]
```

This additionally installs:
- `pytest>=6.0` - Testing framework
- `pytest-cov>=2.0` - Coverage reporting
- `pytest-flask>=1.0` - Flask testing utilities
- `flake8>=3.0` - Code linting

## Installing from Source

To install from the source repository:

```bash
git clone https://github.com/your-org/ramlpy.git
cd ramlpy
pip install -e .
```

The `-e` flag installs the package in "editable" mode, so changes to the source code are immediately reflected.

## Verifying Installation

To verify that ramlpy is installed correctly:

```python
>>> import ramlpy
>>> ramlpy.__version__
'0.1.0'
```

## Troubleshooting

### "No module named 'ramlpy'"

Make sure you're using the correct Python environment:

```bash
python -m pip install ramlpy
```

### "ImportError: cannot import name 'parse'"

Make sure you're importing from the correct module:

```python
from ramlpy import parse  # Correct
from ramlpy.parser import parse  # Incorrect
```

### Dependency Conflicts

If you have conflicts with existing packages, try installing in a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install ramlpy
```
