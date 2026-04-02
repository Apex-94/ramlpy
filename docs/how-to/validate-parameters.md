# How to validate request parameters

This guide shows you how to validate different types of request parameters using ramlpy.

## Path Parameters

Path parameters are defined in the URI template and are always required:

```raml
/users/{userId}:
  uriParameters:
    userId:
      type: integer
      minimum: 1
  get:
    responses:
      200:
        body:
          application/json:
            type: User
```

Validation:

```python
result = api.validate_request(
    path="/users/{userId}",
    method="get",
    path_params={"userId": "123"},
)

if result.ok:
    user_id = result.data["path_params"]["userId"]  # 123 (int)
```

## Query Parameters

Query parameters are optional by default, but can be marked as required:

```raml
/users:
  get:
    queryParameters:
      limit:
        type: integer
        required: true
        minimum: 1
        maximum: 100
      offset:
        type: integer
        default: 0
      role:
        type: string
        enum: [admin, user, guest]
```

Validation:

```python
result = api.validate_request(
    path="/users",
    method="get",
    query_params={"limit": "50", "offset": "10", "role": "admin"},
)

if result.ok:
    limit = result.data["query_params"]["limit"]  # 50 (int)
    offset = result.data["query_params"]["offset"]  # 10 (int)
    role = result.data["query_params"]["role"]  # "admin" (str)
```

## Header Parameters

Header parameters work the same way:

```raml
/users:
  get:
    headers:
      X-Request-ID:
        type: string
        required: true
        pattern: "^[a-f0-9-]+$"
      X-API-Version:
        type: string
        default: "v1"
```

Validation:

```python
result = api.validate_request(
    path="/users",
    method="get",
    headers={"X-Request-ID": "abc-123", "X-API-Version": "v1"},
)
```

## Shorthand Syntax (RAML 1.0)

RAML 1.0 supports shorthand parameter definitions:

```raml
/users:
  get:
    queryParameters:
      limit?: integer
      offset?: integer
      status?: string
```

The `?` suffix indicates the parameter is optional.

## Common Validation Patterns

### Required vs Optional

```raml
queryParameters:
  required_param:
    type: string
    required: true
  optional_param:
    type: string
    required: false
  shorthand_optional?:
    type: string
```

### Enum Validation

```raml
queryParameters:
  status:
    type: string
    enum: [pending, active, completed]
```

### Range Validation

```raml
queryParameters:
  page:
    type: integer
    minimum: 1
    maximum: 1000
  per_page:
    type: integer
    minimum: 1
    maximum: 100
    default: 20
```

### Pattern Validation

```raml
queryParameters:
  email:
    type: string
    pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
```

## Handling Validation Errors

When validation fails, errors include detailed information:

```python
result = api.validate_request(
    path="/users",
    method="get",
    query_params={"limit": "abc"},
)

for error in result.errors:
    print(f"Code: {error['code']}")        # "invalid_type"
    print(f"Message: {error['message']}")  # "Parameter 'limit' is not a valid integer"
    print(f"Pointer: {error['pointer']}")  # "query.limit"
    print(f"Expected: {error['expected']}")  # "integer"
    print(f"Actual: {error['actual']}")    # "abc"
```
