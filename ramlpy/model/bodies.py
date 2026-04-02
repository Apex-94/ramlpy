"""BodySpec - A request or response body specification."""


class BodySpec(object):
    """A request or response body specification."""
    
    def __init__(self, media_type, type_ref=None, example=None,
                 examples=None, schema_ref=None):
        self.media_type = media_type
        self.type_ref = type_ref
        self.example = example
        self.examples = examples or {}
        self.schema_ref = schema_ref
    
    def __repr__(self):
        return "BodySpec(media_type=%r)" % self.media_type
