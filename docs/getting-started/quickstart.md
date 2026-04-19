# Quick Start

This guide gets you from a RAML file to validated handler inputs with the new framework-agnostic validator API.

## Parse a RAML File

```python
from ramlpy import parse

api = parse("api.raml")
print("API Title:", api.title)
print("API Version:", api.version)
print("Base URI:", api.base_uri)
```

## Parse RAML from a String

```python
from ramlpy import parse_string

raml_content = """
#%RAML 1.0
title: My API
version: v1
baseUri: https://api.example.com/{version}

/users:
  get:
    queryParameters:
      limit:
        type: integer
        default: 20
      offset:
        type: integer
        default: 0
"""

api = parse_string(raml_content)
```

## Access Resources and Methods

```python
users_resource = api.resource("/users")
get_method = users_resource.method("get")

print("Method:", get_method.method)
print("Query parameters:", list(get_method.query_parameters.keys()))
```

## Build a Route Validator

```python
validator = api.validator_for("/users", "get")
```

## Validate Parsed Request Values

```python
result = validator.validate(
    query_params={"limit": "50", "offset": "10"},
    headers={"Accept": "application/json"},
)

if result.ok:
    print("Validated query params:", result.data["query_params"])
    # {'limit': 50, 'offset': 10}
else:
    for error in result.errors:
        print(f"Error: {error['message']}")
```

## Strict Error Handling

```python
validated = validator.validate_or_raise(
    query_params={"limit": "50", "offset": "10"},
)

limit = validated["query_params"]["limit"]
offset = validated["query_params"]["offset"]
```

## Type Coercion

ramlpy automatically coerces common scalar values:

| RAML Type | Python Type | Example |
|-----------|-------------|---------|
| `string` | `str` | `"hello"` -> `"hello"` |
| `integer` | `int` | `"123"` -> `123` |
| `number` | `float` | `"3.14"` -> `3.14` |
| `boolean` | `bool` | `"true"` -> `True` |

## Structured Errors

```python
result = validator.validate(query_params={"limit": "not_a_number"})

for error in result.errors:
    print("Code:", error["code"])
    print("Message:", error["message"])
    print("Pointer:", error["pointer"])
    print("Expected:", error["expected"])
    print("Actual:", error["actual"])
```

## Next Steps

- [Tutorial: Building a Validated API](tutorial.md)
- [How-to Guides](../how-to/index.md)
- [Examples](../examples/index.md)
