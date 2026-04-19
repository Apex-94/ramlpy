# ramlpy Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Public API Reference](#public-api-reference)
6. [Validation](#validation)
7. [CLI Usage](#cli-usage)
8. [RAML 0.8 vs 1.0 Support](#raml-08-vs-10-support)
9. [Include Resolution](#include-resolution)
10. [Python Version Compatibility](#python-version-compatibility)
11. [Testing](#testing)
12. [Known Limitations](#known-limitations)

---

## Overview

`ramlpy` is a framework-agnostic Python library for parsing and validating RAML 0.8 and 1.0 files.

It provides:

- **Dual version support**: Parse both RAML 0.8 and 1.0 files
- **Normalized internal model**: Both versions compile into a shared object model
- **Route-scoped validation**: Create reusable validators for path, query, header, and body inputs
- **Type coercion**: Automatically coerce validated values into Python types
- **Structured errors**: Consistent validation errors across frameworks
- **Python 3.6+ support**: Works with Python 3.6 through 3.14+

### Why ramlpy?

`ramlpy` is designed for teams that want RAML parsing and validation without being tied to a specific web framework. You can parse the RAML file once, build validators for each route, and plug them into Flask, FastAPI, Django, aiohttp, a custom gateway, or direct request-handling code.

---

## Installation

### From Source

```bash
git clone <repository-url>
cd ramlpy
pip install -e .
```

### Development Dependencies

```bash
pip install ramlpy[dev]
```

### Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `ruamel.yaml>=0.17.0` | YAML 1.2 parsing with custom tags | Yes |
| `python-dateutil>=2.8.0` | ISO datetime parsing | Yes |
| `jsonschema>=3.0.0` | JSON Schema body validation | Yes |
| `typing_extensions>=3.7` | Type hints for Python < 3.10 | Yes (< 3.10) |

---

## Quick Start

### Parsing a RAML File

```python
from ramlpy import parse

api = parse("api.raml")
print(api.title)
print(api.version)
print(api.base_uri)
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
"""

api = parse_string(raml_text)
```

### Building a Route Validator

```python
validator = api.validator_for("/users/{userId}", "get")
```

### Validating Parsed Request Data

```python
result = validator.validate(
    path_params={"userId": "42"},
    query_params={"limit": "50"},
    headers={"X-Request-ID": "req-123"},
    body=None,
    content_type=None,
)

if result.ok:
    print(result.data)
    # {
    #     "path_params": {"userId": 42},
    #     "query_params": {"limit": 50},
    #     "headers": {"X-Request-ID": "req-123"},
    #     "body": None,
    # }
else:
    for error in result.errors:
        print(f"{error['pointer']}: {error['message']}")
```

### Strict Validation

```python
validated = validator.validate_or_raise(
    path_params={"userId": "42"},
    query_params={"limit": "50"},
)

user_id = validated["path_params"]["userId"]
limit = validated["query_params"]["limit"]
```

---

## Architecture

### Data Flow

```
RAML File
    |
    v
Loader -> Parser -> Normalized ApiSpec -> RouteValidator -> Validated Data / Errors
```

### Main Layers

1. **Loader**
   Resolves `!include` references and YAML input.
2. **Parser**
   Parses RAML 0.8 and 1.0 into version-specific AST structures.
3. **Normalizer**
   Produces a shared normalized model (`ApiSpec`, `ResourceSpec`, `MethodSpec`, `TypeSpec`).
4. **Validator**
   Coerces scalar inputs, validates enums and required fields, and validates request bodies with JSON Schema.

---

## Public API Reference

### Parsing

```python
from ramlpy import parse, parse_string

api = parse("api.raml")
api = parse_string(raml_text, base_path=".")
```

### Route Lookup

```python
resource = api.resource("/users")
resource, method, extracted = api.match_route("/users/42", "get")
```

### Route Validator Creation

```python
validator = api.validator_for("/users/{userId}", "get")
```

### Route Validator Methods

```python
result = validator.validate(
    path_params=None,
    query_params=None,
    headers=None,
    body=None,
    content_type=None,
)

validated = validator.validate_or_raise(...)
body = validator.validate_body_or_raise(payload, content_type="application/json")
```

### Result Object

`validator.validate(...)` returns a `ValidationResult`:

```python
ValidationResult(
    ok=True,
    data={
        "path_params": {},
        "query_params": {},
        "headers": {},
        "body": None,
    },
    errors=[],
)
```

If `ok` is `False`, `errors` contains structured dictionaries with fields like `code`, `message`, `pointer`, `expected`, and `actual`.

---

## Validation

### What Gets Validated

- Path parameters
- Query parameters
- Headers
- Request body

### Type Coercion

Common coercions:

- `integer` -> `int`
- `number` -> `float`
- `boolean` -> `bool`
- `datetime` -> parsed datetime-compatible value handling

### Body Validation

Request bodies are validated using JSON Schema generated from RAML 1.0 types or directly from RAML 0.8 schema definitions.

---

## CLI Usage

```bash
ramlpy-ng validate api.raml
ramlpy-ng info api.raml
```

---

## RAML 0.8 vs 1.0 Support

### RAML 0.8

- `schemas`
- `resourceTypes`
- `traits`
- request body schema validation

### RAML 1.0

- `types`
- inline object definitions
- unions and arrays
- annotations

Both versions normalize into the same runtime model.

---

## Include Resolution

`ramlpy` resolves `!include` recursively relative to the including file. This works for modular RAML projects with shared schemas, libraries, and fragments.

---

## Python Version Compatibility

- Python 3.6
- Python 3.7
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13
- Python 3.14

---

## Testing

Run the test suite with:

```bash
pytest -q
```

---

## Known Limitations

- Response validation is not the primary focus of the current API.
- Some advanced RAML features may be normalized but not fully enforced at validation time.
- Framework adapters are intentionally not bundled; integration is left to application code.
