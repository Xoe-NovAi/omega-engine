# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Resource Guard — Concurrency Protection
# AP: AP-RESOURCE-GUARD-v1.2.0
# [heritage: anyio 2024] M1 AnyIO — Semaphore(1) concurrency guard (zone-purge semantics)
# [id-soft: vet-015] ZONEID Pattern — critical sections guarded by ZONEID_PROBE marker
# [id-soft: doom-1993] BSP Culling — precompute hard parts, trade memory for compute
# ICS: [NODE: MAAT | ARCHETYPE: HERMES | CONTEXT: CONCURRENCY]
#
# Updates in v1.2.0 (C-2′ OOMProtector Integration):
#   - Replaced inline OOMProtector with three-signal fusion OOMProtector (PSI + MemAvailable + cgroup v2)
#   - AdmissionResult enum: ALLOW | THROTTLE | DENY_OOM_RISK | DENY_THRASHING
#   - Hardware-aware thresholds calibrated for Ryzen 7 5700U (15W TDP, 8MB L3 victim cache)
#   - Removed dual-counter _current_ram_mb in favor of kernel-authoritative signals
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
from omega.oracle.oom_protector import OOMProtector, AdmissionResult, OOMProtectorConfig

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


# ── OOMProtector replaced by three-signal fusion in src/omega/oracle/oom_protector.py ──
# [C-2′] The old OOMProtector used psutil/MemAvailable only (dual-counter).
# The new OOMProtector fuses three kernel-authoritative signals:
#   1. PSI (Pressure Stall Information) — /proc/pressure/memory
#   2. MemAvailable — /proc/meminfo (kernel's si_mem_available())
#   3. cgroup v2 memory.pressure — per-cgroup PSI
#
# This wrapper maintains backward compatibility for legacy callers
# while delegating to the new three-signal fusion engine.

class LegacyOOMWrapper:
    """Legacy-compatible wrapper around the new three-signal OOMProtector.

    Keeps the old `check(model_name, model_spec) -> bool` interface while
    internally using PSI + MemAvailable + cgroup v2 fusion.
    """
    RESERVED_MARGIN_MB: int = 1024

    def __init__(self, min_ram_mb: int = 2048, meminfo_path: Optional[str] = None):
        config = OOMProtectorConfig(
            min_reserve_gb=min_ram_mb / 1024,
            throttle_gb=4.0,
        )
        self._protector = OOMProtector(config=config)
        self._meminfo_path = meminfo_path
        self.min_ram_mb = min_ram_mb

    async def check(
        self,
        model_name: Optional[str] = None,
        model_spec: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Three-signal fusion check with legacy interface.

        Returns True if safe, False if OOM risk detected.

        Decision logic (kernel-authoritative):
        1. MemAvailable < reserve → DENY (hard floor)
        2. PSI full.avg10 > 5% → DENY (system thrashing)
        3. PSI some.avg60 > 10% → THROTTLE → DENY (sustained pressure)
        4. MemAvailable 2-4GB → THROTTLE → DENY (low headroom)
        """
        result = await self._protector.check()

        if result == AdmissionResult.ALLOW:
            logger.debug(
                "OOMProtector SAFE: model='%s' — all three signals healthy",
                model_name or "unknown",
            )
            return True

        if model_spec:
            model_ram_mb = model_spec.get("ram_mb", 0)
            logger.warning(
                "OOMProtector %s: model='%s' needs ~%d MB, refusing: %s",
                result.value,
                model_name or model_spec.get("name", "unknown"),
                model_ram_mb,
                result.value,
            )
        else:
            logger.warning(
                "OOMProtector %s: model='%s' — %s",
                result.value,
                model_name or "unknown",
                result.value,
            )
        return False

    async def check_available(self, required_gb: float) -> bool:
        """Check if required memory is available with safety margin.
        
        Delegates to the underlying OOMProtector's check_available method.
        """
        return await self._protector.check_available(required_gb)

    async def get_pressure_snapshot(self):
        """Get detailed pressure snapshot for diagnostics"""
        return await self._protector.get_snapshot()


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
        # [C-2′] Software RAM counter removed — OOMProtector is sole RAM arbiter.
        # _max_ram_mb and _current_ram_mb eliminated. RAM decisions delegated
        # to kernel-authoritative PSI + MemAvailable + cgroup v2 fusion.

        # Re-entrant lock state (ContextVar-based)
        # Keeps the re-entrancy pattern: same task can acquire multiple times
        # without deadlocking. Weight is used as an abstract nesting counter.
        self._semaphore = anyio.Semaphore(1)

        # Hardware Lock: Zen 2 Optimizer for resource resonance
        from omega.oracle.cpu_optimizer import Zen2Optimizer
        self._optimizer = Zen2Optimizer()

        # ── P0-1: OOM Hard-Stop Protector (Three-Signal Fusion) ──
        # [C-2′] Replaced inline OOMProtector with three-signal fusion:
        #   PSI (/proc/pressure/memory) + MemAvailable + cgroup v2 memory.pressure
        # [M23: Failure Integrity] Explicit hard-stop — raises a typed OmegaError
        # rather than silently degrading inference quality or swapping into oblivion.
        self._oom_protector = LegacyOOMWrapper(
            min_ram_mb=int(cvar_get("config.resource_guard.min_ram_mb", 2048)),
            meminfo_path=meminfo_path,
        )

    @asynccontextmanager
    async def lock(self, weight: int = 1, model_spec: Optional[dict] = None,
                   timeout: Optional[float] = None):
        """Hardware Lock: concurrency gate + OOM pre-check + CPU affinity.
        
        [C-2′] RAM tracking removed — OOMProtector (three-signal fusion) is 
        the sole RAM arbiter. This lock provides:
          1. OOM hard-stop (fail-fast before RAM exhaustion)
          2. Semaphore(1) concurrency gate (one inference at a time)
          3. Zen 2 CPU affinity enforcement
          4. ContextVar re-entrancy (same task can nest without deadlock)
        
        [hardening-p4] Re-entrancy — uses immutable ContextVar updates to 
        prevent race conditions across concurrent tasks.
        """
        validate_zoneid(self._magic, ZONEID_PROBE, "ResourceGuard.lock")

        # ── P0-1: OOM Hard-Stop (fail-fast before RAM exhaustion) ──
        # [M23: Failure Integrity] Refuse the model load if available RAM is
        # below the safety threshold. This is a hard stop, not a soft-failure.
        # Uses model_spec to compute an accurate estimate of required RAM.
        _model_name_for_oom = (model_spec or {}).get("name") or "unknown"
        
        # Calculate required memory from model_spec
        required_gb = 0.0
        if model_spec:
            ram_mb = model_spec.get("ram_mb", 0)
            context_window = model_spec.get("context_window", 8192)
            # Model RAM + KV cache (0.5 GB per 8K context) + reserve (1 GB)
            required_gb = (ram_mb / 1024.0) + (context_window / 8192.0) * 0.5 + 1.0
        else:
            # Fallback: default model + reserve
            required_gb = 1.7 + 0.5 + 1.0  # 3.2 GB
        
        if not await self._oom_protector.check_available(required_gb):
            from omega.errors import InferenceOOMError
            if model_spec:
                raise InferenceOOMError(
                    f"Refusing model load '{_model_name_for_oom}': "
                    f"estimated {required_gb:.1f} GB required "
                    f"(model {ram_mb} MB + KV cache + 1 GB reserve) "
                    f"exceeds available RAM"
                )
            raise InferenceOOMError(
                f"Refusing model load: available RAM below "
                f"{self._oom_protector.config.reserve_gb} GB safety threshold"
            )

        task_id = _get_current_task_id()
        # Get a local copy of the current held weights
        held = _held_weights.get().copy()
        already_held = held.get(task_id, 0)
        
        # ── 1. Concurrency Gate (Semaphore) ──
        # [C-2′] Software RAM counter removed. Semaphore(1) provides
        # mutual exclusion for inference — only one load at a time.
        if already_held == 0:
            try:
                if timeout is not None:
                    with anyio.fail_after(timeout):
                        await self._semaphore.acquire()
                else:
                    await self._semaphore.acquire()
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
                # This was the outermost acquisition — release semaphore
                self._semaphore.release()
                
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


# ── Singleton Factory ──────────────────────────────────────────────────
# [B1] Unify the concurrency gate. Two separate Semaphore(1) gates existed:
#   - admission_controller.LocalInferenceAdmission (singleton, local-only)
#   - ResourceGuard (per-instance, all providers)
# Multiple ResourceGuard instances meant multiple local models could load
# concurrently via direct callers (orchestrator, local_worker_pool,
# model_updater, local_queue) that bypass the admission singleton.
# This factory makes ResourceGuard a process-wide singleton so there is
# exactly ONE Semaphore(1) gate for the engine.
_resource_guard: Optional["ResourceGuard"] = None


def get_resource_guard() -> "ResourceGuard":
    """Get or create the process-wide singleton ResourceGuard.

    [B1] Ensures exactly one concurrency gate engine-wide. Callers that
    previously constructed their own ``ResourceGuard`` (e.g. orchestrator,
    local_worker_pool, model_updater, local_queue) should use this factory
    so all inference shares the same Semaphore(1).
    """
    global _resource_guard
    if _resource_guard is None:
        _resource_guard = ResourceGuard()
    return _resource_guard
