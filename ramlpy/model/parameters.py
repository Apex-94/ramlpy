"""ParameterSpec - A parameter (path, query, header, form, or body property)."""


class ParameterSpec(object):
    """A parameter (path, query, header, form, or body property)."""
    
    def __init__(self, name, location, required=False, type_ref="string",
                 enum=None, default=None, repeat=False, pattern=None,
                 minimum=None, maximum=None, min_length=None,
                 max_length=None, raw_source=None):
        self.name = name
        self.location = location  # path, query, header, form, body-property
        self.required = required
        self.type_ref = type_ref
        self.enum = enum or []
        self.default = default
        self.repeat = repeat
        self.pattern = pattern
        self.minimum = minimum
        self.maximum = maximum
        self.min_length = min_length
        self.max_length = max_length
        self.raw_source = raw_source or {}
    
    def __repr__(self):
        return "ParameterSpec(name=%r, location=%r, type=%r, required=%r)" % (
            self.name, self.location, self.type_ref, self.required
        )
