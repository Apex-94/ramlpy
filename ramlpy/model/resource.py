"""ResourceSpec - A RAML resource with its methods and nested resources."""


class ResourceSpec(object):
    """A RAML resource with its methods and nested resources."""
    
    def __init__(self, full_path, relative_path=None,
                 uri_parameters=None, methods=None,
                 nested_resources=None, applied_traits=None,
                 applied_resource_type=None):
        self.full_path = full_path
        self.relative_path = relative_path or full_path
        self.uri_parameters = uri_parameters or {}
        self.methods = methods or {}
        self.nested_resources = nested_resources or []
        self.applied_traits = applied_traits or []
        self.applied_resource_type = applied_resource_type
    
    def method(self, name):
        """Get a method by name (case-insensitive).
        
        Args:
            name: HTTP method name (e.g., 'get', 'post')
        
        Returns:
            MethodSpec: The method specification
        
        Raises:
            KeyError: If the method doesn't exist
        """
        return self.methods[name.lower()]
    
    def __repr__(self):
        return "ResourceSpec(full_path=%r, methods=%r)" % (
            self.full_path, list(self.methods.keys())
        )
