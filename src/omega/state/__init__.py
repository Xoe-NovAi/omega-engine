# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — State Core
# AP: AP-STATE-CORE-v1.0.0
# Status: ACTIVE
#
# Core state management for the Omega Engine, providing the USM singleton.
#
from .cas import CASManager
from .somatic_state import SomaticStateManager
from .usm import USMManager as UnifiedStateManager
from typing import Optional

_usm: Optional[UnifiedStateManager] = None


def get_usm() -> UnifiedStateManager:
    """Get the singleton USM instance."""
    global _usm
    if _usm is None:
        _usm = UnifiedStateManager()
    return _usm


async def initialize_usm() -> None:
    """Initialize the USM singleton."""
    usm = get_usm()
    await usm.initialize()


async def reset_usm() -> None:
    """Reset the USM singleton for testing."""
    global _usm
    _usm = None


__all__ = [
    "CASManager",
    "SomaticStateManager",
    "UnifiedStateManager",
    "get_usm",
    "initialize_usm",
    "reset_usm",
]
