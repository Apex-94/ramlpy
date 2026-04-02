"""Source file representation for RAML files."""

import os


class Source(object):
    """Represents a RAML source file with its location and content."""
    
    def __init__(self, content, path=None, base_path=None):
        """Initialize a Source object.
        
        Args:
            content: The RAML file content as a string
            path: The file path (optional)
            base_path: The base directory for resolving relative includes
        """
        self.content = content
        self.path = path
        self._base_path = base_path or (os.path.dirname(path) if path else None)
    
    @property
    def base_path(self):
        """Get the base path for relative path resolution."""
        return self._base_path
    
    def resolve_relative_path(self, relative_path):
        """Resolve a path relative to this source file.
        
        Args:
            relative_path: A path relative to this source file
        
        Returns:
            str: The resolved absolute path
        """
        if os.path.isabs(relative_path):
            return relative_path
        if self.base_path:
            return os.path.normpath(os.path.join(self.base_path, relative_path))
        return relative_path
    
    def __repr__(self):
        return "Source(path=%r)" % self.path
