# Framework Integration

This guide replaces the old Flask-specific integration. ramlpy now provides a framework-agnostic validation layer that you can wire into any REST API framework.

## Core Pattern

1. Parse the RAML file once at startup.
2. Build route validators once with `api.validator_for(path, method)`.
3. Let your framework parse the request into path params, query params, headers, and body.
4. Pass those parsed values into `validate(...)` or `validate_or_raise(...)`.
5. Return or raise your own framework-specific error response.

## Generic Adapter Example

```python
from ramlpy import parse
from ramlpy.exceptions import RamlValidationError

api = parse("api.raml")

validators = {
    ("GET", "/users"): api.validator_for("/users", "get"),
    ("POST", "/users"): api.validator_for("/users", "post"),
    ("GET", "/users/{userId}"): api.validator_for("/users/{userId}", "get"),
}


def validate_request(path, method, *, path_params=None, query_params=None, headers=None, body=None, content_type=None):
    validator = validators[(method.upper(), path)]
    return validator.validate_or_raise(
        path_params=path_params,
        query_params=query_params,
        headers=headers,
        body=body,
        content_type=content_type,
    )
```

## Example: Use in a Framework Handler

```python
def get_user_handler(framework_request, user_id):
    validated = validators[("GET", "/users/{userId}")].validate_or_raise(
        path_params={"userId": user_id},
        query_params=framework_request.query,
        headers=framework_request.headers,
    )
    return {"status": 200, "body": {"id": validated["path_params"]["userId"]}}
```

## Example: Centralized Error Mapping

```python
from ramlpy.exceptions import RamlValidationError


def dispatch(handler, **kwargs):
    try:
        return handler(**kwargs)
    except RamlValidationError as exc:
        return {"status": 400, "body": {"errors": exc.errors}}
```

## Notes

- Route validators are reusable and cheap to call repeatedly.
- Header lookup is case-insensitive.
- Body validation supports media-type matching such as `application/json; charset=utf-8`.
- The library does not impose request or response objects on your framework.
