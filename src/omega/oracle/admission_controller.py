# 🔱 Local Inference Admission Control — C-10
# AP: AP-ADMISSION-CONTROL-v1.0.0
# [M7: Local-First] Ensures max 1 concurrent local inference instance
# [M13: Temple-Grade] T8 Resilience — fail-fast to cloud on contention
# [id-soft: vet-015] ZONEID Pattern — critical section markers
#
# Hardware: Ryzen 5700U (2 CCX × 4 cores, 4MB L3/CCX, DDR4-3200 ~51GB/s)
# Bottleneck: memory bandwidth — one concurrent llama.cpp instance optimal.
#
# Decision: C-10 (Local Inference Admission Control)
# Spec: docs/strategy/IMPLEMENTATION_MANUAL_C0_C2.md §C-10

"""
Local inference admission control for Ryzen 5700U.

Enforces max 1 concurrent local inference via Semaphore(1).
Integrates with OOMProtector for memory check before load.
Fail-fast to cloud on contention or OOM risk.
"""

import logging
from typing import Optional

import anyio

from omega.oracle.oom_protector import OOMProtector, OOMProtectorConfig

logger = logging.getLogger(__name__)


class LocalInferenceBusyError(Exception):
    """Local inference slot is busy — route to cloud."""
    pass


class OOMRiskError(Exception):
    """Insufficient RAM for model load — route to cloud."""
    pass


class LocalInferenceAdmission:
    """Enforce max 1 concurrent local inference instance.

    Uses Semaphore(1) — FIFO acquisition, fail-fast on contention.
    Combines with OOMProtector for memory-aware admission.
    """

    def __init__(self, oom_config: Optional[OOMProtectorConfig] = None):
        self._semaphore = anyio.Semaphore(1)
        self._current_model: Optional[str] = None
        self._oom_protector = OOMProtector(config=oom_config or OOMProtectorConfig())

    async def acquire(self, model_name: str, model_ram_mb: int = 1700,
                      kv_cache_mb: int = 512) -> bool:
        """Try to acquire local inference slot.

        Checks:
        1. OOMProtector — is there enough RAM?
        2. Semaphore — is the slot free?

        Returns True if acquired, False if another model is loaded or OOM risk.
        """
        # Step 1: OOM check (fail-fast before semaphore)
        # Uses OOMProtector.check_available() — three-signal fusion
        required_gb = (model_ram_mb + kv_cache_mb) / 1024.0
        if not await self._oom_protector.check_available(required_gb):
            logger.warning(
                "OOM risk for %s (need %.1fGB) — failing fast to cloud",
                model_name, required_gb,
            )
            return False

        # Step 2: Semaphore acquisition
        if self._semaphore.value <= 0:
            # Already at capacity
            logger.warning(
                "Local inference busy with %s — %s would queue",
                self._current_model, model_name,
            )
            return False

        await self._semaphore.acquire()
        self._current_model = model_name
        logger.info("Local inference acquired: %s (RAM: %dMB)", model_name, model_ram_mb)
        return True

    def release(self) -> None:
        """Release local inference slot."""
        model_name = self._current_model
        self._current_model = None
        self._semaphore.release()
        logger.info("Local inference released: %s", model_name)

    @property
    def is_available(self) -> bool:
        """Check if local inference slot is free."""
        return self._semaphore.value > 0

    @property
    def current_model(self) -> Optional[str]:
        """Get the currently loaded model name."""
        return self._current_model


# Singleton — one admission controller for the engine
_admission: Optional[LocalInferenceAdmission] = None


def get_admission_controller() -> LocalInferenceAdmission:
    """Get or create the singleton admission controller."""
    global _admission
    if _admission is None:
        _admission = LocalInferenceAdmission()
    return _admission
