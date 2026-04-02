"""Object type validation."""

from ramlpy.validator.errors import ValidationIssue
from ramlpy.validator.scalars import coerce_scalar


def validate_object(type_spec, value, pointer=""):
    """Validate a value against a TypeSpec object definition.
    
    Args:
        type_spec: TypeSpec with properties
        value: Dictionary to validate
        pointer: JSON pointer for error messages
    
    Returns:
        tuple: (validated_value, list of ValidationIssue)
    """
    if not isinstance(value, dict):
        return None, [ValidationIssue(
            code="invalid_object",
            message="Expected object, got %s" % type(value).__name__,
            pointer=pointer,
            expected="object",
            actual=type(value).__name__,
        )]
    
    errors = []
    validated = {}
    properties = type_spec.properties if type_spec else {}
    
    for prop_name, prop_spec in properties.items():
        prop_value = value.get(prop_name)
        prop_pointer = "%s.%s" % (pointer, prop_name) if pointer else prop_name
        
        if prop_value is None:
            if getattr(prop_spec, 'required', False):
                errors.append(ValidationIssue(
                    code="missing_required_property",
                    message="Missing required property '%s'" % prop_name,
                    pointer=prop_pointer,
                ))
            continue
        
        # Coerce and validate property value
        try:
            coerced = coerce_scalar(getattr(prop_spec, 'type_ref', 'string'), prop_value)
            validated[prop_name] = coerced
        except ValueError as e:
            errors.append(ValidationIssue(
                code="invalid_property",
                message=str(e),
                pointer=prop_pointer,
            ))
    
    return validated, errors
