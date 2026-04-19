# How to handle validation errors

This guide shows how to work with validation failures from `validator.validate(...)` and `validator.validate_or_raise(...)`.

## `ValidationResult`

```python
validator = api.validator_for("/users", "get")
result = validator.validate(query_params={"limit": "abc"})

if not result.ok:
    for error in result.errors:
        print(error)
```

Each error is a dictionary with fields like:

```python
{
    "code": "invalid_type",
    "message": "Parameter 'limit' is not a valid integer",
    "pointer": "query.limit",
    "expected": "integer",
    "actual": "abc",
}
```

## Common Error Codes

| Code | Description |
|------|-------------|
| `missing_required` | Required parameter is missing |
| `invalid_type` | Value cannot be coerced to the expected type |
| `invalid_enum` | Value is not in the allowed enum set |
| `jsonschema_validation_error` | Body validation failed against generated schema |

## Raising Instead of Branching

```python
from ramlpy.exceptions import RamlValidationError

validator = api.validator_for("/users", "get")

try:
    validated = validator.validate_or_raise(query_params={"limit": "abc"})
except RamlValidationError as exc:
    print(exc.errors)
```

## Format Errors for Your Framework

The library intentionally leaves response formatting to your application:

```python
from ramlpy.exceptions import RamlValidationError


def run_with_validation(validator, **kwargs):
    try:
        data = validator.validate_or_raise(**kwargs)
        return {"status": 200, "body": data}
    except RamlValidationError as exc:
        return {
            "status": 400,
            "body": {
                "errors": [
                    {
                        "field": error["pointer"],
                        "message": error["message"],
                        "code": error["code"],
                    }
                    for error in exc.errors
                ]
            },
        }
```

## Logging Validation Errors

```python
import logging

logger = logging.getLogger(__name__)


def log_validation_errors(errors):
    for error in errors:
        logger.warning(
            "Validation error: %s at %s (expected=%s actual=%s)",
            error["message"],
            error["pointer"],
            error["expected"],
            error["actual"],
        )


result = validator.validate(query_params={"limit": "abc"})
if not result.ok:
    log_validation_errors(result.errors)
```
