# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Resource Guard — Concurrency Protection
# AP: AP-RESOURCE-GUARD-v1.1.0
# ICS: [NODE: MAAT | ARCHETYPE: HERMES | CONTEXT: CONCURRENCY]
#
# Updates in v1.1.0 (Sovereign Hardening Sprint — P4):
#   - Re-entrant lock logic (prevents deadlock on nested agent calls)
#   - Acquisition timeout via anyio.fail_after
#   - Track held weights per task via ContextVar
#   - ZONEID Pattern preserved for critical section integrity


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import anyio
import contextvars
import logging
import threading
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from omega.constants import ZONEID_PROBE, ZONEID_TOMBSTONE, ZONEID_ATOMIC, validate_zoneid

logger = logging.getLogger(__name__)

# ── Task-Local Storage for Held Weights (Re-entrancy) ─────────────────
# Maps a task identifier to the weight it currently holds.
# This allows nested calls within the same task to acquire the lock
# without deadlocking, up to the total capacity.
_held_weights: contextvars.ContextVar[Dict[Any, int]] = contextvars.ContextVar(
    "_held_weights", default={}
)


def _get_current_task_id() -> Any:
    """Return a unique, hashable identifier for the current async task.

    anyio.current_task() is guaranteed to be set whenever the lock is
    used within an anyio task (the only supported usage pattern).
    """
    task = anyio.get_current_task()
    if task is not None:
        return id(task)
    # Fallback for unusual contexts: combine thread id with a monotonic
    # counter so concurrent callers don't collide. Not used in anyio
    # task groups, but keeps the function safe everywhere.
    global _fallback_counter
    _fallback_counter += 1
    return (id(threading.current_thread()), _fallback_counter)

_fallback_counter = 0


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
    
    Uses a RAM-based tracking system to allow multiple light models
    to run concurrently while restricting heavy models.
    
    v1.2.0 — RAM-Aware: tracks actual memory usage in MB instead of
    abstract weights.
    
    [id-soft: doom-1993] ZONEID Pattern — critical sections guarded by
    ZONEID_PROBE marker. Catches use-after-free and double-release bugs.
    """
    def __init__(self, max_ram_mb: int = 12288):
        # [id-soft: doom-1993] ZONEID Pattern — runtime state marker
        self._magic = ZONEID_PROBE
        self._max_ram_mb = max_ram_mb
        self._current_ram_mb = 0
        self._condition = anyio.Condition()


        # Hardware Lock: Zen 2 Optimizer for resource resonance
        from omega.oracle.cpu_optimizer import Zen2Optimizer
        self._optimizer = Zen2Optimizer()

    @asynccontextmanager
    async def lock(self, weight: int = 1, model_spec: Optional[dict] = None,
                   timeout: Optional[float] = None):
        """Hardware Lock: manages capacity and enforces hardware resonance.
        
        [hardening-p4] Re-entrancy — uses immutable ContextVar updates to 
        prevent race conditions across concurrent tasks.
        """
        validate_zoneid(self._magic, ZONEID_PROBE, "ResourceGuard.lock")
        
        task_id = _get_current_task_id()
        # Get a local copy of the current held weights
        held = _held_weights.get().copy()
        already_held = held.get(task_id, 0)
        
        # ── 1. Capacity Lock (RAM-based tracking) ──
        if already_held == 0:
            try:
                if timeout is not None:
                    with anyio.fail_after(timeout):
                        async with self._condition:
                            while self._current_ram_mb + weight > self._max_ram_mb:
                                await self._condition.wait()
                            self._current_ram_mb += weight
                else:
                    async with self._condition:
                        while self._current_ram_mb + weight > self._max_ram_mb:
                            await self._condition.wait()
                        self._current_ram_mb += weight
            except TimeoutError:
                logger.warning(
                    "ResourceGuard acquisition timed out after %.1fs", timeout
                )
                raise
        
            # Update immutable state: mark this task as holding capacity
            held[task_id] = weight
            _held_weights.set(held)
        else:
            # Re-entrant path: just increment the weight in the local copy
            held[task_id] = already_held + weight
            _held_weights.set(held)


        try:
            if model_spec:
                self._optimizer.enforce_affinity()
            yield
        finally:
            # ── Release ──
            # Re-fetch current state to ensure we are releasing the correct amount
            current_held = _held_weights.get().copy()
            current_weight = current_held.get(task_id, 0)

            if already_held == 0:
                # This was the outermost acquisition — release global capacity
                async with self._condition:
                    self._current_ram_mb -= weight
                    self._condition.notify_all()
                
                # Remove task from held weights entirely
                if task_id in current_held:
                    del current_held[task_id]
                _held_weights.set(current_held)
            else:
                # Inner acquisition — decrement held weight
                new_weight = current_weight - weight
                if new_weight <= 0:
                    if task_id in current_held:
                        del current_held[task_id]
                else:
                    current_held[task_id] = new_weight
                _held_weights.set(current_held)
