"""YAML loading utilities using ruamel.yaml."""

import os
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError
from ramlpy.exceptions import RamlParseError


def load_yaml(text, path=None, base_path=None):
    """Load YAML text into Python objects with !include support.
    
    Args:
        text: YAML string content
        path: Optional file path for error messages
        base_path: Optional base directory for resolving !include
    
    Returns:
        dict or list: Parsed YAML content
    
    Raises:
        RamlParseError: If YAML is invalid or included file is missing
    """
    yaml = YAML(typ='safe')
    yaml.preserve_quotes = True
    
    if base_path is None and path is not None:
        base_path = os.path.dirname(os.path.abspath(path))

    def include_constructor(loader, node):
        filename = loader.construct_scalar(node)
        include_base_path = getattr(loader, "_raml_base_path", None)
        include_source_path = getattr(loader, "_raml_source_path", path)
        if not include_base_path:
            raise RamlParseError(
                "Cannot use !include without a base path",
                path=include_source_path,
            )

        target_path = os.path.normpath(os.path.join(include_base_path, filename))
        if not os.path.exists(target_path):
            raise RamlParseError(
                "Included file not found: %s" % target_path,
                path=include_source_path,
            )

        with open(target_path, 'r', encoding='utf-8') as f:
            # Recursively load the included file
            return load_yaml(f.read(), path=target_path, base_path=os.path.dirname(target_path))

    yaml.constructor.add_constructor('!include', include_constructor)
    yaml.constructor._raml_base_path = base_path
    yaml.constructor._raml_source_path = path
    
    try:
        return yaml.load(text)
    except ScannerError as e:
        raise RamlParseError("Invalid YAML syntax: %s" % e, path=path)
    except Exception as e:
        if isinstance(e, RamlParseError):
            raise
        raise RamlParseError("Error loading YAML: %s" % e, path=path)
