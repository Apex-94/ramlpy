"""SecuritySchemeSpec - A security scheme definition."""


class SecuritySchemeSpec(object):
    """A security scheme definition."""
    
    def __init__(self, name, scheme_type, described_by=None, settings=None):
        self.name = name
        self.scheme_type = scheme_type  # OAuth 1.0, OAuth 2.0, Basic Auth, etc.
        self.described_by = described_by or {}
        self.settings = settings or {}
    
    def __repr__(self):
        return "SecuritySchemeSpec(name=%r, type=%r)" % (self.name, self.scheme_type)
