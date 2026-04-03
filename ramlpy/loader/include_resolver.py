"""Include resolver for RAML !include directives.

Uses a two-step approach to avoid context leaking:
1. First pass: Load YAML with !include replaced by IncludeRef placeholders
2. Second pass: Walk the object tree and resolve each IncludeRef relative
   to the file that contained it
"""

import os
from ruamel.yaml import YAML
from ramlpy.exceptions import IncludeResolutionError

YAML_EXTS = {".raml", ".yaml", ".yml"}
TEXT_EXTS = {".json", ".xml", ".xsd", ".txt"}


class IncludeRef(object):
    """Placeholder for an unresolved !include directive."""
    
    def __init__(self, value):
        self.value = value
    
    def __repr__(self):
        return "IncludeRef({!r})".format(self.value)


class IncludeResolver(object):
    """Resolve !include directives in RAML files.
    
    Uses a two-step approach:
    1. Load raw YAML with !include -> IncludeRef placeholders
    2. Walk the tree and resolve each IncludeRef relative to its file's directory
    
    This avoids context leaking between nested includes.
    """
    
    def __init__(self, base_path=None):
        """Initialize the include resolver.
        
        Args:
            base_path: Base directory for resolving relative includes
        """
        self.base_path = base_path
        self._include_cache = {}
    
    def resolve(self, source):
        """Load and resolve includes from a file path.
        
        Args:
            source: Path to the RAML file
        
        Returns:
            tuple: (resolved_content_dict, Source object)
        """
        from ramlpy.loader.source import Source
        
        path = os.path.abspath(os.fspath(source))
        if not os.path.exists(path):
            raise IncludeResolutionError(
                "Cannot resolve include: %s" % path, path=path
            )
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        src = Source(content, path=path)
        resolved_content = self.load(path)
        return resolved_content, src
    
    def resolve_string(self, text, base_path=None):
        """Resolve includes from a string content.
        
        Args:
            text: RAML content as string
            base_path: Base directory for resolving relative includes
        
        Returns:
            dict: Resolved content
        """
        bp = base_path or self.base_path
        if bp:
            bp = os.fspath(bp)
            dummy_path = os.path.join(bp, "dummy.raml")
        else:
            dummy_path = 'dummy.raml'
        raw = self._load_raw_yaml(text, dummy_path)
        return self._resolve_tree(raw, os.path.dirname(dummy_path))
    
    def load(self, path):
        """Load a file and resolve all includes.
        
        Args:
            path: Absolute path to the file
        
        Returns:
            Parsed content with includes resolved
        """
        path = os.path.abspath(path)
        raw = self._load_raw_yaml_file(path)
        return self._resolve_tree(raw, os.path.dirname(path))
    
    def _load_raw_yaml_file(self, current_path):
        """Load YAML from file with !include -> IncludeRef placeholders.
        
        Args:
            current_path: Absolute path to the file
        
        Returns:
            Raw YAML with IncludeRef placeholders
        """
        with open(current_path, "r", encoding="utf-8") as f:
            content = f.read()
        return self._load_raw_yaml(content, current_path)
    
    def _load_raw_yaml(self, text, current_path):
        """Load YAML from text with !include -> IncludeRef placeholders.
        
        Args:
            text: YAML content as string
            current_path: Path for error messages
        
        Returns:
            Raw YAML with IncludeRef placeholders
        """
        yaml = YAML(typ="safe")
        
        def include_constructor(loader, node):
            rel_path = loader.construct_scalar(node)
            return IncludeRef(rel_path)
        
        yaml.constructor.add_constructor("!include", include_constructor)
        return yaml.load(text)
    
    def _resolve_tree(self, value, base_dir):
        """Walk the object tree and resolve IncludeRef placeholders.
        
        Args:
            value: Object to resolve (may contain IncludeRef)
            base_dir: Base directory for resolving relative includes
        
        Returns:
            Object with all IncludeRef resolved
        """
        if isinstance(value, IncludeRef):
            return self._resolve_include(value, base_dir)
        
        if isinstance(value, dict):
            return {
                k: self._resolve_tree(v, base_dir)
                for k, v in value.items()
            }
        
        if isinstance(value, list):
            return [self._resolve_tree(item, base_dir) for item in value]
        
        return value
    
    def _resolve_include(self, ref, base_dir):
        """Resolve a single IncludeRef.
        
        Args:
            ref: IncludeRef to resolve
            base_dir: Base directory for resolving relative includes
        
        Returns:
            Resolved content
        """
        include_path = os.path.abspath(os.path.join(base_dir, ref.value))
        
        if include_path in self._include_cache:
            return self._include_cache[include_path]
        
        if not os.path.exists(include_path):
            raise IncludeResolutionError(
                "Cannot resolve include: %s" % include_path,
                path=base_dir
            )
        
        ext = os.path.splitext(include_path)[1].lower()
        
        if ext in YAML_EXTS:
            # Load YAML recursively with its own base directory
            loaded = self._load_raw_yaml_file(include_path)
            result = self._resolve_tree(loaded, os.path.dirname(include_path))
        elif ext in TEXT_EXTS:
            # JSON/XSD/XML/TXT files should be included as raw text
            with open(include_path, "r", encoding="utf-8") as f:
                result = f.read()
        else:
            # Default: include as raw text
            with open(include_path, "r", encoding="utf-8") as f:
                result = f.read()
        
        self._include_cache[include_path] = result
        return result
