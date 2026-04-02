# Quick Start

This guide will get you up and running with ramlpy in just a few minutes.

## Basic Usage

### Parsing a RAML File

The simplest way to use ramlpy is to parse a RAML file:

```python
from ramlpy import parse

api = parse("api.raml")
print("API Title:", api.title)
print("API Version:", api.version)
print("Base URI:", api.base_uri)
```

### Parsing RAML from a String

You can also parse RAML content directly from a string:

```python
from ramlpy import parse_string

raml_content = """
#%RAML 1.0
title: My API
version: v1
baseUri: https://api.example.com/{version}

/users:
  get:
    description: Get a list of users
    queryParameters:
      limit:
        type: integer
        default: 20
        minimum: 1
        maximum: 100
      offset:
        type: integer
        default: 0
"""

api = parse_string(raml_content)
```

## Accessing Resources and Methods

Once you have parsed the API, you can access its resources and methods:

```python
# Get a resource by path
users_resource = api.resource("/users")

# Get a method from the resource
get_method = users_resource.method("get")

# Access method details
print("Method:", get_method.method)
print("Description:", get_method.description)
print("Query parameters:", list(get_method.query_parameters.keys()))
```

## Validating Requests

The most powerful feature of ramlpy is request validation:

```python
# Validate an incoming request
result = api.validate_request(
    path="/users",
    method="GET",
    path_params={},
    query_params={"limit": "50", "offset": "10"},
    headers={"Accept": "application/json"},
    body=None,
    content_type=None,
)

if result.ok:
    # Request is valid - use the coerced data
    print("Validated query params:", result.data["query_params"])
    # Output: {'limit': 50, 'offset': 10}
else:
    # Request is invalid - show errors
    for error in result.errors:
        print(f"Error: {error['message']}")
```

## Type Coercion

ramlpy automatically coerces string values to the correct Python types:

| RAML Type | Python Type | Example |
|-----------|-------------|---------|
| `string` | `str` | `"hello"` → `"hello"` |
| `integer` | `int` | `"123"` → `123` |
| `number` | `float` | `"3.14"` → `3.14` |
| `boolean` | `bool` | `"true"` → `True` |

## Error Handling

When validation fails, ramlpy provides structured error information:

```python
result = api.validate_request(
    path="/users",
    method="GET",
    query_params={"limit": "not_a_number"},
)

for error in result.errors:
    print("Code:", error["code"])        # "invalid_type"
    print("Message:", error["message"])  # "Parameter 'limit' is not a valid integer"
    print("Pointer:", error["pointer"])  # "query.limit"
    print("Expected:", error["expected"])  # "integer"
    print("Actual:", error["actual"])    # "not_a_number"
```

## Next Steps

Now that you have the basics, you might want to explore:

- [Tutorial: Building a Validated API](tutorial.md) - A complete walkthrough
- [How-to Guides](../how-to/index.md) - Solve specific problems
- [Examples](../examples/index.md) - See real-world usage
