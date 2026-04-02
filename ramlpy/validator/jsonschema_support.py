"""JSON Schema validation support."""

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

from ramlpy.validator.errors import ValidationIssue


def validate_with_jsonschema(schema, value, pointer=""):
    """Validate a value against a JSON Schema.
    
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
    try:
        jsonschema.validate(instance=value, schema=schema)
    except jsonschema.ValidationError as e:
        errors.append(ValidationIssue(
            code="jsonschema_validation_error",
            message=e.message,
            pointer="%s.%s" % (pointer, e.json_path) if pointer else e.json_path,
        ))
    
    return errors
