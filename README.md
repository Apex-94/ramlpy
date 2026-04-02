# ramlpy-ng

A modern Python library for parsing and validating RAML 0.8 and 1.0 files.

## Features

- **Dual version support**: Parse both RAML 0.8 and 1.0 files
- **Normalized internal model**: Both versions compile into a shared object model
- **Request validation**: Validate path, query, header, and body inputs
- **Type coercion**: Automatically coerce validated values into Python types
- **Flask integration**: Easy-to-use decorators for request validation
- **Developer-friendly errors**: Structured validation error reports
- **Python 3.6+ support**: Works with Python 3.6 through 3.14+

## Installation

```bash
pip install ramlpy-ng
```

### With Flask Integration

```bash
pip install ramlpy-ng[flask]
```

### Development Dependencies

```bash
pip install ramlpy-ng[dev]
```

## Quick Start

### Parsing a RAML File

```python
from ramlpy import parse

api = parse("api.raml")
print(api.title)       # "My API"
print(api.version)     # "v1"
print(api.base_uri)    # "https://api.example.com/{version}"
```

### Parsing from String

```python
from ramlpy import parse_string

raml_text = """
#%RAML 1.0
title: My API
version: v1

/users:
  get:
    queryParameters:
      limit:
        type: integer
        default: 10
        minimum: 1
        maximum: 100
"""

api = parse_string(raml_text)
```

### Validating a Request

```python
result = api.validate_request(
    path="/users",
    method="GET",
    path_params={},
    query_params={"limit": "50"},
    headers={"Accept": "application/json"},
    body=None,
    content_type=None,
)

if result.ok:
    print(result.data)
else:
    for error in result.errors:
        print(f"{error['pointer']}: {error['message']}")
```

## CLI

```bash
ramlpy-ng validate api.raml
ramlpy-ng info api.raml
```

## Documentation

See the [full documentation](docs/README.md) for detailed guides and API reference.

## License

MIT
