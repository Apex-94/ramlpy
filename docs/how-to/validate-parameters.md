# How to validate request parameters

This guide shows how to validate path, query, and header values using route-scoped validators.

## Build the Validator Once

```python
validator = api.validator_for("/users/{userId}", "get")
```

## Path Parameters

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
result = validator.validate(path_params={"userId": "123"})

if result.ok:
    user_id = result.data["path_params"]["userId"]  # 123
```

## Query Parameters

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
validator = api.validator_for("/users", "get")
result = validator.validate(
    query_params={"limit": "50", "offset": "10", "role": "admin"},
)

if result.ok:
    limit = result.data["query_params"]["limit"]
    offset = result.data["query_params"]["offset"]
    role = result.data["query_params"]["role"]
```

## Header Parameters

```raml
/users:
  get:
    headers:
      X-Request-ID:
        type: string
        required: true
      X-API-Version:
        type: string
        default: "v1"
```

Validation:

```python
validator = api.validator_for("/users", "get")
result = validator.validate(
    headers={"X-Request-ID": "abc-123", "X-API-Version": "v1"},
)
```

Header matching is case-insensitive, so lowercase framework header maps also work.

## Strict Mode

```python
validated = validator.validate_or_raise(
    path_params={"userId": "123"},
    query_params={"limit": "25"},
    headers={"X-Request-ID": "req-1"},
)
```

## Handling Errors

```python
result = validator.validate(query_params={"limit": "abc"})

for error in result.errors:
    print(error["code"])
    print(error["message"])
    print(error["pointer"])
    print(error["expected"])
    print(error["actual"])
```
