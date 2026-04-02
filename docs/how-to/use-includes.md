# How to use RAML includes

This guide shows you how to organize large RAML APIs using `!include` directives.

## Why Use Includes?

As your API grows, a single RAML file can become unwieldy. Includes help you:

- Split your API into manageable files
- Reuse types and schemas across resources
- Maintain separate files for different concerns
- Enable team collaboration on different API parts

## Basic Include Syntax

```raml
#%RAML 1.0
title: My API
version: v1

types:
  User: !include types/user.raml
  Error: !include types/error.raml

/users:
  get:
    responses:
      200:
        body:
          application/json:
            type: User[]
```

## Including Types

Create a separate file for each type:

**types/user.raml:**
```raml
type: object
properties:
  id: integer
  name: string
  email: string
```

**types/error.raml:**
```raml
type: object
properties:
  code: string
  message: string
```

## Including JSON Schemas (RAML 0.8)

For RAML 0.8, JSON schemas are included as raw text:

**schemas/user.schema.json:**
```json
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "object",
  "required": ["id", "name", "email"],
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"},
    "email": {"type": "string"}
  }
}
```

**api.raml:**
```raml
#%RAML 0.8
title: My API
version: v1

schemas:
  - User: !include schemas/user.schema.json
```

## Including Resource Types and Traits

**resourceTypes/collection.raml:**
```raml
get:
  responses:
    200:
      body:
        application/json:
          type: <<itemType>>[]
post:
  body:
    application/json:
      type: <<createType>>
  responses:
    201:
      body:
        application/json:
          type: <<itemType>>
```

**api.raml:**
```raml
#%RAML 1.0
title: My API
version: v1

resourceTypes:
  collection: !include resourceTypes/collection.raml

/users:
  type:
    collection:
      itemType: User
      createType: UserCreate
```

## Nested Includes

Includes can be nested arbitrarily deep:

**types/address.raml:**
```raml
type: object
properties:
  street: string
  city: string
  country: !include types/country.raml
```

## How Include Resolution Works

ramlpy uses a two-step include resolution pattern:

1. **First pass**: Load YAML with `!include` replaced by `IncludeRef` placeholders
2. **Second pass**: Walk the object tree and resolve each `IncludeRef` relative to the file that contained it

This ensures that includes are always resolved relative to the correct file's directory, even with deeply nested includes.

## Best Practices

1. **Use relative paths**: Always use paths relative to the including file
2. **Organize by concern**: Group related types, schemas, and resources together
3. **Use consistent naming**: Follow a consistent naming convention for included files
4. **Avoid circular includes**: Circular includes will cause infinite recursion

## Example Project Structure

```
api/
├── api.raml
├── types/
│   ├── user.raml
│   ├── order.raml
│   └── error.raml
├── schemas/
│   ├── user.schema.json
│   └── order.schema.json
├── resourceTypes/
│   ├── collection.raml
│   └── member.raml
└── traits/
    ├── paged.raml
    └── secured.raml
```
