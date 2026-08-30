# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-DEGRAD-MGR-v1.0.0
# AP: AP-DEGRAD-MGR-v1.0.0
# 🔱 Graceful Degradation Manager — Fallback Chains for Stressed Systems
# Ported from xna-omega-legacy/src/omega/core/degradation.py


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
from typing import Any, Dict, Callable
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DegradationLevel:
    name: str
    threshold: float  # Trigger threshold (e.g., CPU > 90% or RAM < 1GB)
    action: Callable
    priority: int


class DegradationManager:
    """
    Monitors system pressure and applies degradation levels to preserve core functionality.

    Levels:
    - Optimal: Full features, max context.
    - Stressed: Reduced context, disabled non-critical tools.
    - Critical: Minimal context, basic routing only.
    - Disabled: Engine enters safe-mode, only basic health probes active.
    """

    def __init__(self):
        self._current_level = "Optimal"
        self._levels = {
            "Optimal": 0,
            "Stressed": 1,
            "Critical": 2,
            "Disabled": 3,
        }
        self._active_actions = []

    async def evaluate_pressure(self, metrics: Dict[str, Any]):
        """Evaluates system metrics and transitions to the appropriate degradation level."""
        cpu_load = metrics.get("cpu_load", 0.0)
        ram_free = metrics.get("ram_free_mb", 1024)

        new_level = "Optimal"
        if cpu_load > 0.95 or ram_free < 256:
            new_level = "Disabled"
        elif cpu_load > 0.85 or ram_free < 512:
            new_level = "Critical"
        elif cpu_load > 0.70 or ram_free < 1024:
            new_level = "Stressed"

        if new_level != self._current_level:
            logger.warning(f"System pressure change: {self._current_level} -> {new_level}")
            await self._transition_to(new_level)
            self._current_level = new_level

    async def _transition_to(self, level: str):
        """Executes the actions associated with a degradation level."""
        # In a full implementation, this would call registered callbacks
        # e.g., reducing n_ctx in ModelGateway or disabling certain MCP tools.
        logger.info(f"Applying degradation level: {level}")

    def get_current_level(self) -> str:
        return self._current_level

    def is_at_least(self, level: str) -> bool:
        """Check if the system is at or above a certain degradation level."""
        return self._levels.get(self._current_level, 0) >= self._levels.get(level, 0)
