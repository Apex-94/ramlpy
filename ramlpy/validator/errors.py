"""Validation error classes."""


class ValidationIssue(object):
    """A single validation issue."""
    
    def __init__(self, code, message, pointer=None, expected=None, actual=None):
        self.code = code
        self.message = message
        self.pointer = pointer
        self.expected = expected
        self.actual = actual
    
    def as_dict(self):
        """Convert to dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "pointer": self.pointer,
            "expected": self.expected,
            "actual": self.actual,
        }
    
    def __repr__(self):
        return "ValidationIssue(code=%r, message=%r)" % (self.code, self.message)


class ValidationResult(object):
    """Result of a validation check."""
    
    def __init__(self, ok, data=None, errors=None):
        self.ok = ok
        self.data = data or {}
        self.errors = errors or []
    
    def raise_unless_ok(self):
        """Raise :class:`~ramlpy.exceptions.RamlValidationError` if validation failed."""
        if self.ok:
            return
        from ramlpy.exceptions import RamlValidationError
        raise RamlValidationError("Request validation failed", errors=self.errors)
    
    def __repr__(self):
        return "ValidationResult(ok=%r, errors=%d)" % (self.ok, len(self.errors))
