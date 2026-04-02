"""YAML loading utilities using ruamel.yaml."""

from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError
from ramlpy.exceptions import RamlParseError


def load_yaml(text, path=None):
    """Load YAML text into Python objects.
    
    Args:
        text: YAML string content
        path: Optional file path for error messages
    
    Returns:
        dict or list: Parsed YAML content
    
    Raises:
        RamlParseError: If YAML is invalid
    """
    yaml = YAML(typ='safe')
    yaml.preserve_quotes = True
    try:
        return yaml.load(text)
    except ScannerError as e:
        raise RamlParseError("Invalid YAML syntax: %s" % e, path=path)
    except Exception as e:
        raise RamlParseError("Error loading YAML: %s" % e, path=path)
