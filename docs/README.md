# ramlpy Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [Public API Reference](#public-api-reference)
6. [Model Classes](#model-classes)
7. [Validation](#validation)
8. [Flask Integration](#flask-integration)
9. [CLI Usage](#cli-usage)
10. [RAML 0.8 vs 1.0 Support](#raml-08-vs-10-support)
11. [Include Resolution](#include-resolution)
12. [Python Version Compatibility](#python-version-compatibility)
13. [Testing](#testing)
14. [Known Limitations](#known-limitations)
15. [Troubleshooting](#troubleshooting)

---

## Overview

`ramlpy` is a modern Python library for parsing and validating RAML 0.8 and 1.0 files. It is designed for Flask-based REST API integrations and provides:

- **Dual version support**: Parse both RAML 0.8 and 1.0 files
- **Normalized internal model**: Both versions compile into a shared object model
- **Request validation**: Validate path, query, header, and body inputs
- **Type coercion**: Automatically coerce validated values into Python types
- **Flask integration**: Easy-to-use decorators for request validation
- **Developer-friendly errors**: Structured validation error reports
- **Python 3.6+ support**: Works with Python 3.6 through 3.14+

### Why ramlpy?

Existing RAML parsers like `ramlfications` have limitations:
- RAML 0.8-only support
- Python 3.10+ only
- No Flask integration
- Limited validation error reporting

`ramlpy` addresses these with a clean architecture:
1. YAML loader with include resolution
2. Version-aware parser
3. Version-specific AST to normalized model compiler
4. Validator engine with type coercion
5. Flask integration layer

---

## Installation

### From Source

```bash
git clone <repository-url>
cd ramlpy
pip install -e .
```

### With Flask Integration

```bash
pip install ramlpy[flask]
```

### Development Dependencies

```bash
pip install ramlpy[dev]
```

### Dependencies

| Package | Purpose | Required |
|---------|---------|----------|
| `ruamel.yaml>=0.17.0` | YAML 1.2 parsing with custom tags | Yes |
| `python-dateutil>=2.8.0` | ISO datetime parsing (Python 3.6 compat) | Yes |
| `jsonschema>=3.0.0` | JSON Schema body validation | Yes |
| `typing_extensions>=3.7` | Type hints for Python < 3.10 | Yes (< 3.10) |
| `Flask>=1.0` | Flask integration | Optional |

---

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

### Accessing Routes

```python
# Get a resource by path
users_resource = api.resource("/users")

# Get a method from the resource
get_method = users_resource.method("get")

# Access query parameters
for name, param in get_method.query_parameters.items():
    print(f"{name}: {param.type_ref} (required={param.required})")
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
    # {
    #     "path_params": {},
    #     "query_params": {"limit": 50},
    #     "headers": {"Accept": "application/json"},
    #     "body": None,
    # }
else:
    for error in result.errors:
        print(f"{error['pointer']}: {error['message']}")
```

---

## Architecture

### Data Flow

```
RAML File
    |
    v
+-----------------------------------------+
|           Loader Layer                  |
|  +-----------------------------------+  |
|  | 1. Version Detection              |  |
|  |    - Read first line              |  |
|  |    - Match #%RAML 0.8 or 1.0      |  |
|  +-----------------------------------+  |
|  +-----------------------------------+  |
|  | 2. Include Resolution             |  |
|  |    - Resolve !include directives  |  |
|  |    - Each file gets own loader    |  |
|  |    - JSON files as raw text       |  |
|  +-----------------------------------+  |
|  +-----------------------------------+  |
|  | 3. YAML Loading                   |  |
|  |    - ruamel.yaml safe loader      |  |
|  +-----------------------------------+  |
+-----------------------------------------+
    |
    v
+-----------------------------------------+
|           Parser Layer                  |
|  +-----------------------------------+  |
|  | RAML 0.8 Parser                   |  |
|  | - Resources, methods, schemas      |  |
|  | - resourceTypes, traits            |  |
|  +-----------------------------------+  |
|  +-----------------------------------+  |
|  | RAML 1.0 Parser                   |  |
|  | - Resources, methods, types        |  |
|  | - uses, annotations                |  |
|  +-----------------------------------+  |
|                                         |
|  Output: Version-specific AST           |
+-----------------------------------------+
    |
    v
+-----------------------------------------+
|         Compiler Layer                  |
|  +-----------------------------------+  |
|  | 0.8 Normalizer                    |  |
|  | - schemas -> TypeSpec              |  |
|  | - parameters -> ParameterSpec      |  |
|  +-----------------------------------+  |
|  +-----------------------------------+  |
|  | 1.0 Normalizer                    |  |
|  | - types -> TypeSpec                |  |
|  | - parameters -> ParameterSpec      |  |
|  +-----------------------------------+  |
|                                         |
|  Output: Normalized ApiSpec             |
+-----------------------------------------+
    |
    v
+-----------------------------------------+
|         Validator Layer                 |
|  +-----------------------------------+  |
|  | Scalar Coercion                   |  |
|  | - string, integer, number         |  |
|  | - boolean, datetime               |  |
|  +-----------------------------------+  |
|  +-----------------------------------+  |
|  | Request Validation                |  |
|  | - Required checks                 |  |
|  | - Type validation                 |  |
|  | - Enum validation                 |  |
|  | - Range validation                |  |
|  +-----------------------------------+  |
+-----------------------------------------+
```

### Package Structure

```
ramlpy/
+-- __init__.py           # Public API exports
+-- _compat.py            # Python version compatibility
+-- api.py                # parse(), parse_string()
+-- exceptions.py         # Exception classes
|
+-- loader/
|   +-- __init__.py
|   +-- version.py        # RAML version detection
|   +-- source.py         # Source file representation
|   +-- yaml_loader.py    # YAML loading
|   +-- include_resolver.py  # !include resolution
|
+-- parser/
|   +-- __init__.py
|   +-- ast_nodes.py      # AST node classes
|   +-- base.py           # Base parser class
|   +-- parser08.py       # RAML 0.8 parser
|   +-- parser10.py       # RAML 1.0 parser
|   +-- fragments10.py    # RAML 1.0 fragments
|
+-- compiler/
|   +-- __init__.py
|   +-- normalize08.py    # 0.8 -> model compiler
|   +-- normalize10.py    # 1.0 -> model compiler
|
+-- model/
|   +-- __init__.py
|   +-- api.py            # ApiSpec
|   +-- resource.py       # ResourceSpec
|   +-- method.py         # MethodSpec
|   +-- parameters.py     # ParameterSpec
|   +-- bodies.py         # BodySpec
|   +-- types.py          # TypeSpec, TypeRef
|   +-- security.py       # SecuritySchemeSpec
|
+-- validator/
|   +-- __init__.py
|   +-- errors.py         # ValidationIssue, ValidationResult
|   +-- scalars.py        # Scalar type coercion
|   +-- coercion.py       # Advanced coercion
|   +-- object_types.py   # Object validation
|   +-- jsonschema_support.py  # JSON Schema validation
|   +-- engine.py         # Main validation engine
|
+-- integrations/
|   +-- __init__.py
|   +-- flask.py          # Flask integration
|
+-- cli/
    +-- __init__.py
    +-- main.py           # CLI entry point
```

---

## Public API Reference

### `parse(path)`

Parse a RAML file and return an `ApiSpec`.

**Parameters:**
- `path` (str): Path to the RAML file

**Returns:**
- `ApiSpec`: Normalized API specification

**Raises:**
- `RamlVersionError`: If RAML version is unsupported or missing
- `RamlParseError`: If file cannot be parsed
- `IncludeResolutionError`: If an `!include` directive cannot be resolved

**Example:**
```python
from ramlpy import parse

api = parse("api.raml")
```

### `parse_string(text, base_path=None)`

Parse RAML text and return an `ApiSpec`.

**Parameters:**
- `text` (str): RAML content as string
- `base_path` (str, optional): Base path for resolving relative includes

**Returns:**
- `ApiSpec`: Normalized API specification

**Raises:**
- `RamlVersionError`: If RAML version is unsupported or missing
- `RamlParseError`: If text cannot be parsed

**Example:**
```python
from ramlpy import parse_string

api = parse_string("#%RAML 1.0\ntitle: Test\nversion: v1")
```

---

## Model Classes

### ApiSpec

Top-level normalized RAML API specification.

**Attributes:**
- `title` (str): API title
- `version` (str): API version
- `base_uri` (str): Base URI template
- `media_type` (str): Default media type
- `resources` (list): List of `ResourceSpec`
- `types` (dict): Type registry (name -> `TypeSpec`)
- `traits` (dict): Trait definitions
- `resource_types` (dict): Resource type definitions
- `security_schemes` (dict): Security scheme definitions
- `metadata` (dict): Additional metadata

**Methods:**

#### `resource(path)`

Get a resource by its full path.

```python
resource = api.resource("/users/{id}")
```

#### `validate_request(path, method, ...)`

Validate an incoming request.

```python
result = api.validate_request(
    path="/users",
    method="get",
    query_params={"limit": "10"},
)
```

### ResourceSpec

A RAML resource with its methods and nested resources.

**Attributes:**
- `full_path` (str): Full resource path (e.g., `/users/{id}`)
- `relative_path` (str): Relative path segment
- `uri_parameters` (dict): URI parameter definitions (name -> `ParameterSpec`)
- `methods` (dict): HTTP method definitions (method -> `MethodSpec`)
- `nested_resources` (list): Nested `ResourceSpec` objects
- `applied_traits` (list): Applied trait names
- `applied_resource_type` (str): Applied resource type name

**Methods:**

#### `method(name)`

Get a method by name (case-insensitive).

```python
get_method = resource.method("get")
```

### MethodSpec

A RAML HTTP method on a resource.

**Attributes:**
- `method` (str): HTTP method (lowercase)
- `headers` (dict): Header definitions (name -> `ParameterSpec`)
- `query_parameters` (dict): Query parameter definitions
- `bodies` (dict): Body definitions (media_type -> `BodySpec`)
- `responses` (dict): Response definitions
- `secured_by` (list): Security scheme names
- `description` (str): Method description

### ParameterSpec

A parameter (path, query, header, form, or body property).

**Attributes:**
- `name` (str): Parameter name
- `location` (str): Parameter location (`path`, `query`, `header`, `form`, `body-property`)
- `required` (bool): Whether parameter is required
- `type_ref` (str): Type reference (e.g., `string`, `integer`)
- `enum` (list): Allowed values
- `default`: Default value
- `repeat` (bool): Whether parameter can repeat
- `pattern` (str): Regex pattern for validation
- `minimum`: Minimum value (numeric types)
- `maximum`: Maximum value (numeric types)
- `min_length`: Minimum length (string types)
- `max_length`: Maximum length (string types)
- `raw_source` (dict): Original RAML definition

### BodySpec

A request or response body specification.

**Attributes:**
- `media_type` (str): Media type (e.g., `application/json`)
- `type_ref` (str): Type reference
- `example`: Example value
- `examples` (dict): Named examples
- `schema_ref`: Schema reference

### TypeSpec

A type definition.

**Attributes:**
- `name` (str): Type name
- `base_type` (str): Base type (e.g., `object`, `string`)
- `facets` (dict): Type facets
- `properties` (dict): Object properties (name -> `ParameterSpec`)
- `items`: Array item type
- `enum` (list): Enum values
- `schema_source`: Original schema source
- `inline_definition` (dict): Full inline definition

### TypeRef

A reference to a type by name.

**Attributes:**
- `name` (str): Type name
- `namespace` (str): Namespace (for `uses` imports)

---

## Validation

### Validation Result

The `validate_request()` method returns a `ValidationResult`:

```python
ValidationResult(
    ok=True,
    data={
        "path_params": {"id": 123},
        "query_params": {"limit": 10},
        "headers": {"Accept": "application/json"},
        "body": None,
    },
    errors=[]
)
```

### Validation Errors

When validation fails, errors contain:

```python
{
    "code": "invalid_type",
    "message": "Parameter 'limit' is not a valid integer",
    "pointer": "query.limit",
    "expected": "integer",
    "actual": "abc"
}
```

**Error Codes:**
- `missing_required`: Required parameter is missing
- `invalid_type`: Value cannot be coerced to expected type
- `invalid_enum`: Value not in allowed enum values
- `route_not_found`: No matching route in RAML spec

### Type Coercion

The validator automatically coerces string values to Python types:

| RAML Type | Python Type | Examples |
|-----------|-------------|----------|
| `string` | `str` | `"hello"` -> `"hello"` |
| `integer` | `int` | `"123"` -> `123` |
| `number` | `float` | `"3.14"` -> `3.14` |
| `boolean` | `bool` | `"true"` -> `True`, `"0"` -> `False` |
| `datetime` | `datetime` | `"2024-01-01T00:00:00"` -> `datetime` |
| `date` | `date` | `"2024-01-01"` -> `date` |
| `time` | `time` | `"12:00:00"` -> `time` |

---

## Flask Integration

### Decorator Approach

```python
from flask import Flask, request
from ramlpy import parse
from ramlpy.integrations.flask import validate_with_raml

app = Flask(__name__)
api = parse("api.raml")

@app.route("/users/<id>")
@validate_with_raml(api, path="/users/{id}", method="get")
def get_user(id):
    validated = request.raml.validated
    user_id = validated["path_params"]["id"]
    return {"id": user_id}
```

### Extension Approach

```python
from ramlpy.integrations.flask import RamlApi

raml = RamlApi(app, api_spec=api)

@app.route("/users/<id>")
@raml.validate(path="/users/{id}", method="get")
def get_user(id):
    validated = request.raml.validated
    return {"id": validated["path_params"]["id"]}
```

### Error Response

When validation fails, Flask returns a 400 response:

```json
{
    "errors": [
        {
            "code": "invalid_type",
            "message": "Parameter 'id' is not a valid integer",
            "pointer": "path.id",
            "expected": "integer",
            "actual": "abc"
        }
    ]
}
```

---

## CLI Usage

### Parse a RAML File

```bash
ramlpy-ng parse api.raml
```

Output:
```
Title: My API
Version: v1
Base URI: https://api.example.com/{version}
Resources:
  /users
    - GET
    - POST
  /users/{id}
    - GET
```

### Parse as JSON

```bash
ramlpy-ng parse api.raml --json
```

Output:
```json
{
    "title": "My API",
    "version": "v1",
    "base_uri": "https://api.example.com/{version}",
    "resources": ["/users", "/users/{id}"]
}
```

### Validate a RAML File

```bash
ramlpy-ng validate api.raml
```

Output:
```
RAML file is valid.
Title: My API
Version: v1
Resources: 2
```

---

## RAML 0.8 vs 1.0 Support

### RAML 0.8 Features

| Feature | Support |
|---------|---------|
| Root document | Yes |
| Resources and methods | Yes |
| baseUri, protocols, mediaType | Yes |
| uriParameters | Yes |
| queryParameters | Yes |
| headers | Yes |
| body | Yes |
| schemas | Yes |
| resourceTypes | Yes |
| traits | Yes |
| securitySchemes | Yes |
| `!include` | Yes |

### RAML 1.0 Features

| Feature | Support |
|---------|---------|
| types | Yes |
| Typed fragments | Yes |
| Libraries and `uses` | Yes |
| Annotations | Partial |
| Overlays/extensions | No |
| Examples / named examples | Yes |
| 1.0 trait and resource type applications | Partial |
| Compatibility for deprecated `schemas`/`schema` | Yes |

---

## Include Resolution

### How It Works

The include resolver uses a **two-step approach** to avoid context leaking between nested includes:

**Step 1: Load raw YAML with placeholders**
- Each file is loaded with its own YAML loader
- `!include` directives are replaced with `IncludeRef` placeholders
- The loader does NOT recursively parse included files during this step

**Step 2: Resolve the tree**
- After the entire YAML document is loaded, walk the object tree
- For each `IncludeRef`, resolve it relative to the file that contained it
- Recursively load and resolve nested includes with their own base directories

This pattern ensures:
- `api.raml` is loaded once with all `!include` becoming `IncludeRef`
- Only after the whole `api.raml` object is loaded do you resolve includes
- Each include is resolved relative to the correct file's directory
- No chance of nested includes temporarily changing the meaning of sibling includes

### Implementation

```python
class IncludeRef(object):
    """Placeholder for an unresolved !include directive."""
    def __init__(self, value):
        self.value = value

class IncludeResolver(object):
    def load(self, path):
        # Step 1: Load raw YAML with IncludeRef placeholders
        raw = self._load_raw_yaml_file(path)
        # Step 2: Walk tree and resolve all IncludeRef
        return self._resolve_tree(raw, os.path.dirname(path))
    
    def _resolve_tree(self, value, base_dir):
        if isinstance(value, IncludeRef):
            return self._resolve_include(value, base_dir)
        if isinstance(value, dict):
            return {k: self._resolve_tree(v, base_dir) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_tree(item, base_dir) for item in value]
        return value
```

### Supported Include Types

| Extension | Behavior |
|-----------|----------|
| `.raml`, `.yaml`, `.yml` | Parsed recursively as YAML |
| `.json`, `.xsd`, `.xml`, `.txt` | Included as raw text |
| Other | Included as raw text |

### Example

```raml
#%RAML 0.8
title: My API
schemas:
  - User: !include schemas/user.schema.json
  - Error: !include schemas/error.schema.json
```

The JSON schema files are included as raw strings, which can then be used with JSON Schema validation.

---

## Python Version Compatibility

### Supported Versions

- Python 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14

### Compatibility Layer

The `ramlpy._compat` module provides:

- **Datetime parsing**: Uses `dateutil.parser.isoparse` for Python 3.6, `datetime.fromisoformat` for 3.7+
- **Type hints**: Uses `typing_extensions` for `Literal`, `Protocol`, `TypedDict` on Python < 3.10
- **Dataclasses**: Fallback for Python 3.6

### Version Detection

```python
from ramlpy._compat import PYTHON_36, PYTHON_310_PLUS

if PYTHON_310_PLUS:
    # Use match/case syntax
    pass
else:
    # Use if/elif chains
    pass
```

---

## Testing

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

### Test Structure

```
tests/
+-- fixtures/
|   +-- raml_examples/
|       +-- simple-08/
|       +-- simple-08-with-types/
|       +-- simple-10-inline/
|       +-- simple-10-with-types/
|       +-- complex-10-with-types/
|       +-- modular-10-library/
+-- test_loader/
|   +-- test_version.py
+-- test_parser/
|   +-- test_integration.py
|   +-- test_raml_examples.py
+-- test_validator/
    +-- test_engine.py
    +-- test_scalars.py
```

### Test Coverage

- **77 tests passing** (all tests pass, no skipped tests)
- Covers all raml_examples fixtures including complex-08-with-types

---

## Known Limitations

### RAML 1.0 Overlays/Extensions

RAML 1.0 overlays and extensions are not yet supported. This is planned for a future release.

### Resource Type Parameterization

RAML 0.8 resource type parameterization (e.g., `<<resourcePathName>>`) is not fully implemented. The parser loads the resource types but does not expand the parameters.

### RAML 1.0 Library `uses` with Nested Type References

When using `uses` to import libraries, type references like `types.Customer` are loaded but the namespace resolution may not work for deeply nested library imports.

---

## Troubleshooting

### "Missing or invalid RAML header"

**Cause**: The RAML file does not start with `#%RAML 0.8` or `#%RAML 1.0`.

**Solution**: Ensure your RAML file starts with the correct header:
```raml
#%RAML 1.0
title: My API
```

### "Cannot resolve include: ..."

**Cause**: An `!include` directive references a file that does not exist.

**Solution**: Check the include path is correct relative to the file containing it:
```raml
# api.raml
schemas:
  - User: !include schemas/user.schema.json  # Relative to api.raml's directory
```

### "Parameter 'X' is not a valid integer"

**Cause**: The request contains a value that cannot be coerced to the expected type.

**Solution**: Ensure the request contains valid values:
```python
# Wrong: limit is a string
query_params={"limit": "abc"}

# Correct: limit is a numeric string
query_params={"limit": "10"}
```

### Flask Integration Not Working

**Cause**: Flask is not installed.

**Solution**: Install with Flask support:
```bash
pip install ramlpy[flask]
```

---

## License

MIT License. See LICENSE file for details.