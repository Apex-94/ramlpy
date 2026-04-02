"""Custom exception classes for ramlpy."""


class RamlError(Exception):
    """Base exception for all ramlpy errors."""
    pass


class RamlParseError(RamlError):
    """Raised when RAML parsing fails."""

    def __init__(self, message, path=None, line=None):
        super(RamlParseError, self).__init__(message)
        self.path = path
        self.line = line


class RamlValidationError(RamlError):
    """Raised when RAML validation fails."""

    def __init__(self, message, errors=None):
        super(RamlValidationError, self).__init__(message)
        self.errors = errors or []


class RamlVersionError(RamlParseError):
    """Raised when RAML version is unsupported or missing."""
    pass


class IncludeResolutionError(RamlParseError):
    """Raised when an !include directive cannot be resolved."""
    pass


class TypeResolutionError(RamlParseError):
    """Raised when a type reference cannot be resolved."""
    pass
