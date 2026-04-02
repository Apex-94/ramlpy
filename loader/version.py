"""RAML version detection utilities."""

import re
from ramlpy.exceptions import RamlVersionError

RAML_HEADER_RE = re.compile(r"^#%RAML\s+(0\.8|1\.0)(?:\s+.+)?\s*$", re.MULTILINE)


def detect_raml_version(text):
    """Detect RAML version from file content.
    
    Args:
        text: RAML file content as string
    
    Returns:
        str: '0.8' or '1.0'
    
    Raises:
        RamlVersionError: If version cannot be detected
    
    Examples:
        >>> detect_raml_version("#%RAML 0.8\\ntitle: Test")
        '0.8'
        >>> detect_raml_version("#%RAML 1.0\\ntitle: Test")
        '1.0'
        >>> detect_raml_version("#%RAML 1.0 Library\\ntitle: Test")
        '1.0'
    """
    if not text:
        raise RamlVersionError("Missing or invalid RAML header")
    
    first_line = text.splitlines()[0].strip() if text.splitlines() else ""
    match = RAML_HEADER_RE.match(first_line)
    if not match:
        raise RamlVersionError("Missing or invalid RAML header")
    return match.group(1)
