# How to validate request bodies

This guide shows how to validate request bodies with route-scoped validators.

## JSON Body Validation

RAML 1.0 lets you describe request bodies with named types:

```raml
#%RAML 1.0
title: User API
version: v1

types:
  UserCreateRequest:
    type: object
    properties:
      name:
        type: string
        minLength: 1
        maxLength: 100
      email:
        type: string
        pattern: "^[^@]+@[^@]+\\.[^@]+$"
      age?:
        type: integer
        minimum: 0
        maximum: 150
      role?:
        type: string
        enum: [admin, user, guest]

/users:
  post:
    body:
      application/json:
        type: UserCreateRequest
```

Validation:

```python
validator = api.validator_for("/users", "post")

result = validator.validate(
    body={
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
    },
    content_type="application/json",
)

if result.ok:
    validated_body = result.data["body"]
```

## Strict Body Validation

```python
validator = api.validator_for("/users", "post")
payload = validator.validate_body_or_raise(
    {
        "name": "Alice",
        "email": "alice@example.com",
    },
    content_type="application/json",
)
```

## RAML 0.8 Schema Validation

In RAML 0.8, request bodies can point to JSON Schema definitions:

```raml
#%RAML 0.8
title: User API
version: v1

schemas:
  - UserCreate: |
      {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "type": "object",
        "required": ["name", "email"],
        "properties": {
          "name": {"type": "string"},
          "email": {"type": "string"},
          "age": {"type": "integer", "minimum": 0}
        }
      }

/users:
  post:
    body:
      application/json:
        schema: UserCreate
```

The same `validator.validate(...)` and `validator.validate_body_or_raise(...)` APIs work for both RAML 0.8 and RAML 1.0.

## Handling Invalid Bodies

```python
result = validator.validate(
    body={"name": 123},
    content_type="application/json",
)

if not result.ok:
    for error in result.errors:
        print(f"{error['pointer']}: {error['message']}")
```
