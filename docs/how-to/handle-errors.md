# How to handle validation errors

This guide shows you how to handle and customize validation error responses.

## Understanding Validation Errors

When validation fails, ramlpy returns a `ValidationResult` with structured errors:

```python
result = api.validate_request(
    path="/users",
    method="get",
    query_params={"limit": "abc"},
)

if not result.ok:
    for error in result.errors:
        print(error)
        # {
        #     "code": "invalid_type",
        #     "message": "Parameter 'limit' is not a valid integer",
        #     "pointer": "query.limit",
        #     "expected": "integer",
        #     "actual": "abc"
        # }
```

## Error Codes

| Code | Description | Example |
|------|-------------|---------|
| `missing_required` | Required parameter is missing | `{"code": "missing_required", "pointer": "query.limit"}` |
| `invalid_type` | Value cannot be coerced to expected type | `{"code": "invalid_type", "expected": "integer", "actual": "abc"}` |
| `invalid_enum` | Value not in allowed enum values | `{"code": "invalid_enum", "expected": ["admin", "user"], "actual": "superadmin"}` |
| `route_not_found` | No matching route in RAML spec | `{"code": "route_not_found", "pointer": "request"}` |

## Custom Error Formatting

To customize error responses in Flask:

```python
from functools import wraps
from flask import request, jsonify, g

def custom_validate(api, path=None, method=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = api.validate_request(
                path=path or request.path,
                method=method or request.method,
                path_params=kwargs,
                query_params=request.args.to_dict(flat=True),
                headers=dict(request.headers),
                body=request.get_json(silent=True),
                content_type=request.content_type,
            )
            if not result.ok:
                # Custom error format
                return jsonify({
                    "status": "error",
                    "code": "VALIDATION_ERROR",
                    "details": [
                        {
                            "field": e["pointer"],
                            "message": e["message"],
                            "code": e["code"]
                        }
                        for e in result.errors
                    ]
                }), 400
            g.raml_validated = result.data
            request.raml = type("RamlContext", (), {"validated": result.data})()
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

## Error Handling in Non-Flask Applications

For non-Flask applications, handle errors directly:

```python
from ramlpy import parse

api = parse("api.raml")

def handle_request(path, method, query_params, body=None):
    result = api.validate_request(
        path=path,
        method=method,
        query_params=query_params,
        body=body,
    )
    
    if not result.ok:
        # Return custom error response
        return {
            "status": 400,
            "body": {
                "errors": [
                    {
                        "field": e["pointer"],
                        "message": e["message"]
                    }
                    for e in result.errors
                ]
            }
        }
    
    # Process valid request
    return {"status": 200, "body": result.data}
```

## Logging Validation Errors

For debugging and monitoring:

```python
import logging

logger = logging.getLogger(__name__)

def log_validation_errors(result):
    for error in result.errors:
        logger.warning(
            "Validation error: %s at %s (expected: %s, got: %s)",
            error["message"],
            error["pointer"],
            error["expected"],
            error["actual"]
        )

# Usage
result = api.validate_request(...)
if not result.ok:
    log_validation_errors(result)
    return error_response(result.errors)
```

## Aggregating Errors

When multiple fields fail validation, all errors are returned:

```python
result = api.validate_request(
    path="/users",
    method="post",
    body={"name": 123, "email": "invalid"},
)

# Multiple errors
for error in result.errors:
    print(f"{error['pointer']}: {error['message']}")
# body.name: Expected string, got integer
# body.email: Invalid email format
```
