"""TypeSpec and TypeRef - Type definitions for RAML."""


class TypeSpec(object):
    """A type definition (from RAML 1.0 types or 0.8 schemas)."""
    
    def __init__(self, name, base_type=None, facets=None,
                 properties=None, items=None, enum=None,
                 schema_source=None, inline_definition=None):
        self.name = name
        self.base_type = base_type
        self.facets = facets or {}
        self.properties = properties or {}
        self.items = items
        self.enum = enum or []
        self.schema_source = schema_source
        self.inline_definition = inline_definition
    
    def __repr__(self):
        return "TypeSpec(name=%r, base_type=%r)" % (self.name, self.base_type)


class TypeRef(object):
    """A reference to a type by name."""
    
    def __init__(self, name, namespace=None):
        self.name = name
        self.namespace = namespace
    
    def __repr__(self):
        if self.namespace:
            return "TypeRef(%s.%s)" % (self.namespace, self.name)
        return "TypeRef(%s)" % self.name
