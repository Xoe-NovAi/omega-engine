# 🔱 Resource Guard — Concurrency Protection
# AP: AP-RESOURCE-GUARD-v1.0.0

import anyio
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from omega.constants import ZONEID_PROBE, ZONEID_TOMBSTONE, ZONEID_ATOMIC, validate_zoneid

logger = logging.getLogger(__name__)

class AtomicLock:
    """Sovereign Atomic Lock for critical state transitions.
    
    [id-soft: doom-1993] ZONEID Pattern — ensures lock integrity.
    """
    def __init__(self):
        self._magic = ZONEID_ATOMIC
        self._lock = anyio.Lock()

    async def __aenter__(self):
        validate_zoneid(self._magic, ZONEID_ATOMIC, "AtomicLock.__aenter__")
        await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        validate_zoneid(self._magic, ZONEID_ATOMIC, "AtomicLock.__aexit__")
        self._lock.release()

class ResourceGuard:
    """Ensures model resource usage doesn't exceed system capacity.
    
    Uses a weighted semaphore pattern to allow multiple light models 
    to run concurrently while restricting heavy models.
    
    [id-soft: doom-1993] ZONEID Pattern — critical sections guarded by
    ZONEID_PROBE marker. Catches use-after-free and double-release bugs.
    """
    def __init__(self, total_capacity: int = 8):
        # [id-soft: doom-1993] ZONEID Pattern — runtime state marker
        self._magic = ZONEID_PROBE
        self._capacity = total_capacity
        self._current_usage = 0
        self._condition = anyio.Condition()
        
        # Hardware Lock: Zen 2 Optimizer for resource resonance
        from omega.oracle.cpu_optimizer import Zen2Optimizer
        self._optimizer = Zen2Optimizer()

    @asynccontextmanager
    async def lock(self, weight: int = 1, model_spec: Optional[dict] = None):
        """Hardware Lock: manages capacity and enforces hardware resonance.
        
        [id-soft: doom-1993] ZONEID Pattern — pre-lock integrity check.
        """
        validate_zoneid(self._magic, ZONEID_PROBE, "ResourceGuard.lock")
        
        # 1. Capacity Lock (Weighted Semaphore)
        async with self._condition:
            while self._current_usage + weight > self._capacity:
                await self._condition.wait()
            self._current_usage += weight
        
        try:
            # 2. Hardware Lock: Enforce resonance if model_spec is provided
            if model_spec:
                # Enforce CPU affinity to compute cores to prevent contention
                self._optimizer.enforce_affinity()
                
                # Log hardware lock state
                logger.debug(
                    "Hardware Lock active: pinned to compute cores, "
                    "optimized for %s", model_spec.get("entity", "unknown")
                )
            
            yield
        finally:
            async with self._condition:
                self._current_usage -= weight
                self._condition.notify_all()

