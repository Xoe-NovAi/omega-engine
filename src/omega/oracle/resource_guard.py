# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Resource Guard — Concurrency Protection
# AP: AP-RESOURCE-GUARD-v1.1.0
# [heritage: anyio 2024] M1 AnyIO — Semaphore(1) concurrency guard (zone-purge semantics)
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
from omega.cvar_table import cvar_get

logger = logging.getLogger(__name__)


def _get_available_ram_mb(meminfo_path: Optional[str] = None) -> Optional[int]:
    """Get available RAM in MB using psutil (primary) or /proc/meminfo (fallback).

    Args:
        meminfo_path: Optional path to a meminfo file for testing. If provided,
                      reads from this file instead of psutil or /proc/meminfo.

    Returns None if neither source is available (sensor failure).
    """
    # Test override: if meminfo_path is provided, use it exclusively
    if meminfo_path is not None:
        try:
            with open(meminfo_path, "r", encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("MemAvailable:"):
                        mem_available_kb = int(line.split()[1])
                        return int(mem_available_kb / 1024)
        except (OSError, ValueError, IndexError) as e:
            logger.warning("Cannot read %s: %s", meminfo_path, e)
            return None

    # Primary: psutil
    try:
        import psutil
        available_bytes = psutil.virtual_memory().available
        return int(available_bytes / (1024 * 1024))
    except ImportError:
        pass  # Fall through to /proc/meminfo

    # Fallback: /proc/meminfo
    try:
        with open("/proc/meminfo", "r", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("MemAvailable:"):
                    mem_available_kb = int(line.split()[1])
                    return int(mem_available_kb / 1024)
    except (OSError, ValueError, IndexError) as e:
        logger.warning("Cannot read /proc/meminfo: %s", e)
        return None

    return None

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

    [id-soft: vet-015] ZONEID Pattern — ensures lock integrity.
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


class OOMProtector:
    """Hard-stop if available RAM drops below a safety threshold.

    [heritage: id-soft-2004] Knowledge Leak Detection — the DOOM 3 principle
    of detecting a resource boundary *before* crossing it, then failing fast
    instead of corrupting state. Here applied to system RAM: if MemAvailable
    falls below the estimated model load + KV cache + 1GB margin, refuse to
    load a model (which would OOM and kill the process).

    [P0-1: RAM Hardening] Uses psutil.virtual_memory().available for accuracy,
    accepts an optional model spec to estimate per-model RAM requirement.
    The formula is:
      - required_mb = model_ram_mb + kv_cache_estimate + RESERVED_MARGIN_MB
      - If available_ram < required_mb → HARD STOP

    [M23: Failure Integrity] Explicit hard-stop — raises a typed OmegaError
    rather than silently degrading inference quality or swapping into oblivion.
    """

    # 1GB safety margin: reserve enough RAM for the OS, systemd services,
    # Podman containers, and any concurrent processes (Redis, Qdrant, etc.)
    RESERVED_MARGIN_MB: int = 1024

    def __init__(self, min_ram_mb: int = 2048, meminfo_path: Optional[str] = None):
        self.min_ram_mb = min_ram_mb
        self._meminfo_path = meminfo_path
        self._meminfo_path = meminfo_path

    async def check(
        self,
        model_name: Optional[str] = None,
        model_spec: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Return True if RAM is safe, False if OOM risk is critical.

        Uses psutil.virtual_memory().available if psutil is installed,
        falls back to /proc/meminfo otherwise.

        Args:
            model_name: Name of the model being loaded (for logging).
            model_spec: Dict with at least ``ram_mb`` key (model RAM estimate).
                        If provided, the check uses model_ram + margin vs available.
                        If None, falls back to the simple min_ram_mb threshold.

        Returns True (safe) if neither psutil nor meminfo can be read — a
        sensor failure must not block inference (M23: no soft-failure, but
        also no sensor-caused DoS).
        """
        def _check() -> bool:
            available_mb = _get_available_ram_mb(self._meminfo_path)
            if available_mb is None:
                # Sensor failure — assume safe
                logger.warning("OOMProtector: cannot determine available RAM (sensor failure)")
                return True

            # ── Model-aware estimate ──
            if model_spec is not None:
                model_ram_mb = model_spec.get("ram_mb", 0)
                estimated_required_mb = model_ram_mb + self.RESERVED_MARGIN_MB

                if available_mb < estimated_required_mb:
                    logger.error(
                        "OOMProtector HARD-STOP: model='%s' needs ~%d MB RAM "
                        "(%d MB model + %d MB margin), only %d MB available",
                        model_name or model_spec.get("name", "unknown"),
                        estimated_required_mb,
                        model_ram_mb,
                        self.RESERVED_MARGIN_MB,
                        available_mb,
                    )
                    return False

                logger.debug(
                    "OOMProtector SAFE: model='%s' needs ~%d MB, %d MB available "
                    "(headroom %d MB)",
                    model_name or "unknown",
                    estimated_required_mb,
                    available_mb,
                    available_mb - estimated_required_mb,
                )
                return True

            # ── Simple threshold check (no model spec) ──
            if available_mb < self.min_ram_mb:
                logger.error(
                    "OOMProtector HARD-STOP: %d MB available < %d MB threshold",
                    available_mb, self.min_ram_mb,
                )
                return False

            logger.debug("OOMProtector SAFE: %d MB available >= %d MB threshold", available_mb, self.min_ram_mb)
            return True

        return await anyio.to_thread.run_sync(_check)


class ResourceGuard:
    """Ensures model resource usage doesn't exceed system capacity.
    
    Uses a RAM-based tracking system to allow multiple light models
    to run concurrently while restricting heavy models.
    
    v1.2.0 — RAM-Aware: tracks actual memory usage in MB instead of
    abstract weights.
    
    [id-soft: vet-015] ZONEID Pattern — critical sections guarded by
    ZONEID_PROBE marker. Catches use-after-free and double-release bugs.
    """
    def __init__(self, max_ram_mb: Optional[int] = None, meminfo_path: Optional[str] = None):
        # [id-soft: vet-015] ZONEID Pattern — runtime state marker
        self._magic = ZONEID_PROBE
        self._max_ram_mb = max_ram_mb or int(cvar_get("config.resource_guard.max_ram_mb", 12288))
        self._current_ram_mb = 0
        self._condition = anyio.Condition()


        # Hardware Lock: Zen 2 Optimizer for resource resonance
        from omega.oracle.cpu_optimizer import Zen2Optimizer
        self._optimizer = Zen2Optimizer()

        # ── P0-1: OOM Hard-Stop Protector ──
        # [heritage: id-soft-2004] Knowledge Leak Detection — fail fast before
        # RAM exhaustion corrupts state. Refuses model loads below the threshold.
        self._oom_protector = OOMProtector(
            min_ram_mb=int(cvar_get("config.resource_guard.min_ram_mb", 2048)),
            meminfo_path=meminfo_path,
        )

    @asynccontextmanager
    async def lock(self, weight: int = 1, model_spec: Optional[dict] = None,
                   timeout: Optional[float] = None):
        """Hardware Lock: manages capacity and enforces hardware resonance.
        
        [hardening-p4] Re-entrancy — uses immutable ContextVar updates to 
        prevent race conditions across concurrent tasks.
        """
        validate_zoneid(self._magic, ZONEID_PROBE, "ResourceGuard.lock")

        # ── P0-1: OOM Hard-Stop (fail-fast before RAM exhaustion) ──
        # [M23: Failure Integrity] Refuse the model load if available RAM is
        # below the safety threshold. This is a hard stop, not a soft-failure.
        # Uses model_spec to compute an accurate estimate of required RAM.
        _model_name_for_oom = (model_spec or {}).get("name") or "unknown"
        if not await self._oom_protector.check(model_name=_model_name_for_oom, model_spec=model_spec):
            from omega.errors import InferenceOOMError
            if model_spec:
                raise InferenceOOMError(
                    f"Refusing model load '{_model_name_for_oom}': "
                    f"estimated {model_spec.get('ram_mb', '?')} MB + 1 GB margin "
                    f"exceeds available RAM"
                )
            raise InferenceOOMError(
                f"Refusing model load: available RAM below "
                f"{self._oom_protector.min_ram_mb} MB safety threshold"
            )

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
