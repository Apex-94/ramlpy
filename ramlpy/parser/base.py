"""Base parser class."""

from ramlpy.exceptions import RamlParseError


class BaseParser(object):
    """Base class for RAML parsers."""
    
    def __init__(self, base_path=None):
        self.base_path = base_path
    
    def parse(self, text):
        """Parse RAML text into AST. Must be implemented by subclasses."""
        raise NotImplementedError
    
    def _error(self, message, line=None):
        """Create a parse error."""
        return RamlParseError(message, line=line)
