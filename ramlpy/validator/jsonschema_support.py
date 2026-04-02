"""JSON Schema validation support."""

try:
    import jsonschema
    from jsonschema import Draft202012Validator
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

from ramlpy.validator.errors import ValidationIssue


def validate_with_jsonschema(schema, value, pointer=""):
    """Validate a value against a JSON Schema, collecting all errors.
    
    Args:
        schema: JSON Schema dict
        value: Value to validate
        pointer: JSON pointer for error messages
    
    Returns:
        list: List of ValidationIssue objects
    """
    if not HAS_JSONSCHEMA:
        return [ValidationIssue(
            code="jsonschema_unavailable",
            message="jsonschema package is not installed",
            pointer=pointer,
        )]
    
    errors = []
    validator = Draft202012Validator(schema)
    for e in validator.iter_errors(value):
        # Build a clean path from the error
        path = ".".join(str(p) for p in e.absolute_path) if e.absolute_path else ""
        error_pointer = "%s.%s" % (pointer, path) if pointer and path else (pointer or path)
        errors.append(ValidationIssue(
            code="jsonschema_validation_error",
            message=e.message,
            pointer=error_pointer,
        ))
    
    return errors
