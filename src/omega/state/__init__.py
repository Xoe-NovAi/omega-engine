# 🔱 Omega Engine — State Core
# AP: AP-STATE-CORE-v1.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | CONTEXT: STATE-MANAGEMENT]
# Status: ACTIVE
# 
# Core state management for the Omega Engine, providing the USM singleton.
# 
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
