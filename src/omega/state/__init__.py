from .usm import USMManager
from typing import Optional

_usm: Optional[USMManager] = None

def get_usm() -> USMManager:
    """Get the singleton USM instance."""
    global _usm
    if _usm is None:
        _usm = USMManager()
    return _usm

async def initialize_usm() -> None:
    """Initialize the USM singleton."""
    usm = get_usm()
    await usm.initialize()

async def reset_usm() -> None:
    """Reset the USM singleton for testing."""
    global _usm
    _usm = None
