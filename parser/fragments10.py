"""RAML 1.0 fragment handling (libraries, resource types, etc.)."""

from ramlpy.loader.yaml_loader import load_yaml


def parse_fragment(text, fragment_type):
    """Parse a RAML 1.0 fragment.
    
    Args:
        text: Fragment YAML content
        fragment_type: 'Library', 'ResourceType', 'Trait', 'DataType', etc.
    
    Returns:
        dict: Parsed fragment data
    """
    data = load_yaml(text)
    return {
        'type': fragment_type,
        'data': data,
    }
