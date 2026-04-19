# Tutorial: Building a Validated API

This tutorial shows how to use ramlpy as a framework-agnostic validation layer. The handler examples are plain Python so you can adapt them to Flask, FastAPI, Django, aiohttp, serverless handlers, or your own request pipeline.

By the end, you will:

- define a RAML API
- parse it with ramlpy
- create reusable route validators
- validate handler inputs
- return structured error responses

## Step 1: Define the API

Create `api.raml`:

```raml
#%RAML 1.0
title: User Management API
version: v1
baseUri: https://api.example.com/{version}
mediaType: application/json

types:
  User:
    type: object
    properties:
      id: integer
      name: string
      email: string
      role:
        type: string
        enum: [admin, user, guest]

  UserCreateRequest:
    type: object
    properties:
      name: string
      email: string
      role?:
        type: string
        enum: [admin, user, guest]

/users:
  get:
    queryParameters:
      limit?:
        type: integer
        default: 20
        minimum: 1
        maximum: 100
      offset?:
        type: integer
        default: 0
        minimum: 0
      role?:
        type: string
        enum: [admin, user, guest]

  post:
    body:
      application/json:
        type: UserCreateRequest

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

## Step 2: Parse the RAML and Build Validators

Create `app_logic.py`:

```python
from ramlpy import parse

api = parse("api.raml")

list_users_validator = api.validator_for("/users", "get")
create_user_validator = api.validator_for("/users", "post")
get_user_validator = api.validator_for("/users/{userId}", "get")

USERS = [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
]
```

## Step 3: Use Validators Inside Handlers

These handlers accept already-parsed input values. Your framework can extract path params, query params, headers, and JSON body in whatever way it prefers.

```python
def list_users_handler(query_params, headers=None):
    validated = list_users_validator.validate_or_raise(
        query_params=query_params,
        headers=headers or {},
    )
    query = validated["query_params"]

    users = USERS[:]
    if "role" in query:
        users = [u for u in users if u["role"] == query["role"]]

    offset = query.get("offset", 0)
    limit = query.get("limit", 20)
    return {"status": 200, "body": users[offset:offset + limit]}


def create_user_handler(body, headers=None):
    validated = create_user_validator.validate_or_raise(
        body=body,
        headers=headers or {},
        content_type="application/json",
    )
    payload = validated["body"]

    new_id = max(u["id"] for u in USERS) + 1 if USERS else 1
    new_user = {
        "id": new_id,
        "name": payload["name"],
        "email": payload["email"],
        "role": payload.get("role", "user"),
    }
    USERS.append(new_user)
    return {"status": 201, "body": new_user}


def get_user_handler(path_params):
    validated = get_user_validator.validate_or_raise(path_params=path_params)
    user_id = validated["path_params"]["userId"]

    user = next((u for u in USERS if u["id"] == user_id), None)
    if user is None:
        return {
            "status": 404,
            "body": {"errors": [{"code": "not_found", "message": "User not found"}]},
        }
    return {"status": 200, "body": user}
```

## Step 4: Wrap Validation Errors

`validate_or_raise(...)` raises `RamlValidationError`. Catch that at your framework boundary and format a response once.

```python
from ramlpy.exceptions import RamlValidationError


def run_handler(handler, **kwargs):
    try:
        return handler(**kwargs)
    except RamlValidationError as exc:
        return {
            "status": 400,
            "body": {
                "errors": exc.errors,
            },
        }
```

## Step 5: Try Example Calls

```python
print(run_handler(list_users_handler, query_params={"limit": "1"}))
print(run_handler(create_user_handler, body={"name": "Charlie", "email": "charlie@example.com"}))
print(run_handler(get_user_handler, path_params={"userId": "1"}))
```

Invalid input produces structured validation errors:

```python
print(run_handler(list_users_handler, query_params={"limit": "abc"}))
print(run_handler(create_user_handler, body={"name": "Charlie"}))
```

## Step 6: Integration Pattern

No matter which framework you use, the pattern is the same:

1. Parse the RAML file once at startup.
2. Build route validators once with `api.validator_for(...)`.
3. Let the framework parse the incoming request.
4. Pass parsed values into `validate(...)` or `validate_or_raise(...)`.
5. Use the coerced values from the returned data.

## Next Steps

- [How to handle validation errors](../how-to/handle-errors.md)
- [How to validate request parameters](../how-to/validate-parameters.md)
- [How to validate request bodies](../how-to/validate-bodies.md)
