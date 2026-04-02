# How to validate request bodies

This guide shows you how to validate request bodies using ramlpy.

## JSON Body Validation

RAML 1.0 allows you to define the expected body structure using types:

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
        default: user

/users:
  post:
    body:
      application/json:
        type: UserCreateRequest
    responses:
      201:
        body:
          application/json:
            type: User
```

Validation:

```python
result = api.validate_request(
    path="/users",
    method="post",
    body={
        "name": "Alice",
        "email": "alice@example.com",
        "age": 30,
    },
    content_type="application/json",
)

if result.ok:
    validated_body = result.data["body"]
    # Use the validated body
```

## RAML 0.8 Schema Validation

In RAML 0.8, you use JSON Schema directly:

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

## Required vs Optional Properties

In RAML 1.0, use `?` suffix for optional properties:

```raml
types:
  UserCreateRequest:
    type: object
    properties:
      name: string       # Required
      email: string      # Required
      age?: integer      # Optional
      role?: string      # Optional
```

## Nested Objects

You can define nested object structures:

```raml
types:
  Address:
    type: object
    properties:
      street: string
      city: string
      country: string
      zipCode: string

  UserCreateRequest:
    type: object
    properties:
      name: string
      email: string
      address: Address
```

## Arrays

Define array types for lists of items:

```raml
types:
  Tag:
    type: string
    minLength: 1

  UserCreateRequest:
    type: object
    properties:
      name: string
      tags: Tag[]
```

## Handling Validation Errors

When the body doesn't match the expected structure:

```python
result = api.validate_request(
    path="/users",
    method="post",
    body={"name": 123},  # name should be string
    content_type="application/json",
)

if not result.ok:
    for error in result.errors:
        print(f"{error['pointer']}: {error['message']}")
```
