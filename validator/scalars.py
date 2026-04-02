"""Scalar type coercion and validation."""

from ramlpy._compat import parse_datetime


def coerce_scalar(type_name, value):
    """Coerce a string value to the specified scalar type.
    
    Args:
        type_name: Target type name (string, integer, number, boolean, etc.)
        value: Value to coerce
    
    Returns:
        Coerced value
    
    Raises:
        ValueError: If coercion fails
    """
    if value is None:
        return None
    
    if type_name == "string":
        return str(value)
    
    if type_name == "integer":
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValueError("Cannot convert %r to integer" % value)
    
    if type_name == "number":
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValueError("Cannot convert %r to number" % value)
    
    if type_name == "boolean":
        if isinstance(value, bool):
            return value
        lowered = str(value).strip().lower()
        if lowered in ("true", "1", "yes"):
            return True
        if lowered in ("false", "0", "no"):
            return False
        raise ValueError("Invalid boolean: %r" % value)
    
    if type_name in ("datetime", "datetime-only"):
        try:
            return parse_datetime(str(value))
        except (ValueError, TypeError):
            raise ValueError("Cannot convert %r to datetime" % value)
    
    if type_name == "date":
        try:
            return parse_datetime(str(value)).date()
        except (ValueError, TypeError):
            raise ValueError("Cannot convert %r to date" % value)
    
    if type_name == "time":
        try:
            return parse_datetime(str(value)).time()
        except (ValueError, TypeError):
            raise ValueError("Cannot convert %r to time" % value)
    
    if type_name == "file":
        return value
    
    return value
