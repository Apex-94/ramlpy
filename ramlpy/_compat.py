"""Compatibility utilities for cross-version Python support (3.6-3.12+)."""

import sys

# Version detection
PYTHON_36 = sys.version_info < (3, 7)
PYTHON_37 = (3, 7) <= sys.version_info < (3, 8)
PYTHON_38 = (3, 8) <= sys.version_info < (3, 9)
PYTHON_39 = (3, 9) <= sys.version_info < (3, 10)
PYTHON_310_PLUS = sys.version_info >= (3, 10)
PYTHON_311_PLUS = sys.version_info >= (3, 11)

# Datetime parsing compatibility
if PYTHON_36:
    # Python 3.6 doesn't have datetime.fromisoformat()
    from dateutil.parser import isoparse as _isoparse

    def parse_datetime(value):
        """Parse ISO datetime string across all Python versions."""
        if value is None:
            return None
        return _isoparse(str(value))
else:
    from datetime import datetime

    def parse_datetime(value):
        """Parse ISO datetime string across all Python versions."""
        if value is None:
            return None
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            # Fallback for edge cases
            from dateutil.parser import isoparse
            return isoparse(str(value))

# Type hints compatibility
# For Python 3.6-3.9, use typing_extensions for newer typing features
try:
    from typing import Literal, Protocol, TypedDict, runtime_checkable
except ImportError:
    from typing_extensions import Literal, Protocol, TypedDict, runtime_checkable

# Union type helper for type annotations
from typing import Union, Optional, List, Dict, Any

# Match statement helper
def use_match_statement():
    """Returns True if match/case is available (Python 3.10+)."""
    return PYTHON_310_PLUS


# Dataclass compatibility
if PYTHON_36:
    try:
        from dataclasses import dataclass, field, asdict
    except ImportError:
        # Fallback: provide no-op decorators
        def dataclass(cls):
            return cls

        def field(default_factory=None, default=None):
            return default

        def asdict(obj):
            return {k: v for k, v in obj.__dict__.items()}
else:
    from dataclasses import dataclass, field, asdict
