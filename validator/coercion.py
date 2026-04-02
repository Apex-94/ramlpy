"""Advanced type coercion."""

from ramlpy.validator.scalars import coerce_scalar


def coerce_value(type_ref, value):
    """Coerce a value based on type reference.
    
    Args:
        type_ref: Type name or reference
        value: Value to coerce
    
    Returns:
        Coerced value
    """
    if value is None:
        return None
    
    # Handle array types
    if type_ref.startswith("array") or type_ref.startswith("[]"):
        if not isinstance(value, list):
            value = [value]
        return value
    
    # Handle scalar types
    return coerce_scalar(type_ref, value)
