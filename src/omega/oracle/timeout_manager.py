# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-TIMEOUT-MGR-v1.0.0
# AP: AP-TIMEOUT-MGR-v1.0.0
# 🔱 Timeout Manager — 4-Layer Nested Cancellation Hierarchy
# Ported from xna-omega-legacy/scripts/ssa/timeout_manager.py


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import anyio
import logging
import time
from typing import Callable, Any, Dict
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class TimeoutContext:
    """Context for a specific timeout layer."""

    name: str
    timeout: float
    start_time: float = field(default_factory=time.time)
    cancelled: bool = False


class TimeoutManager:
    """
    Implements a 4-layer nested cancellation hierarchy:
    Tool -> Group -> Turn -> Workflow

    If a higher layer times out, all nested lower layers are immediately cancelled.
    """

    def __init__(self):
        self._layers = {
            "workflow": 300.0,  # 5 mins
            "turn": 60.0,  # 1 min
            "group": 30.0,  # 30 secs
            "tool": 10.0,  # 10 secs
        }
        self._active_contexts: Dict[str, TimeoutContext] = {}

    async def execute(self, layer: str, func: Callable, *args, **kwargs) -> Any:
        """Executes a function within a specific timeout layer."""
        if layer not in self._layers:
            raise ValueError(
                f"Invalid timeout layer: {layer}. Must be one of {list(self._layers.keys())}"
            )

        timeout = self._layers[layer]
        ctx = TimeoutContext(name=layer, timeout=timeout)
        self._active_contexts[layer] = ctx

        try:
            # [AnyIO 4.x] fail_after is a synchronous context manager
            with anyio.fail_after(timeout):
                return await func(*args, **kwargs)
        except TimeoutError:
            logger.warning(f"Timeout reached at {layer} layer ({timeout}s)")
            ctx.cancelled = True
            raise
        finally:
            if layer in self._active_contexts and self._active_contexts[layer] == ctx:
                del self._active_contexts[layer]

    def set_timeout(self, layer: str, seconds: float):
        """Update the timeout for a specific layer."""
        if layer in self._layers:
            self._layers[layer] = seconds
            logger.info(f"Timeout for {layer} updated to {seconds}s")
        else:
            raise ValueError(f"Invalid layer: {layer}")

    def get_timeout(self, layer: str) -> float:
        """Get current timeout for a layer."""
        return self._layers.get(layer, 0.0)
