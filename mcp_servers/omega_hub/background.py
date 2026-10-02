# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# [id-soft: quake-1996] Hivemind Background — lazy thinker deletion / grace-period reap pattern for pruning stale agents

"""Omega Hub — Background orchestration: pruning, reaping, metrics.

AP Token: AP-OMEGA-HUB-BACKGROUND-v1.0.0

Extracted from server.py (Phase 1a-3). All shared state is accessed at
call-time via ``state.VARIABLE`` to avoid the module-global rebind trap.
"""
import json
import os
import fcntl
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import anyio

from mcp_servers.omega_hub import state
from mcp_servers.omega_hub.state import handoff_index_rebuild

logger = logging.getLogger("omega.hub")


# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND: AWARENESS PRUNING
# ═══════════════════════════════════════════════════════════════════════════

async def _prune_awareness_background() -> None:
    """Background loop to prune stale agents from the hivemind.

    D-kal-052: Respects extended-session check-ins. If an agent
    has called hivemind_extended_checkin(), the pruning loop
    uses their custom TTL (default 3h) instead of HEARTBEAT_TTL (20m).

    [hi-observability-2] Records pruning cycle timestamp and logs
    results. Calls _write_metrics() after each cycle so the metrics
    file always reflects the latest state.
    """
    while True:
        # Pruning and metrics are independent — failure of one must not block the other.
        try:
            now = datetime.now(timezone.utc)
            async with state._awareness_lock:
                stale_clis = []
                for cli, snap in state._awareness.items():
                    if not snap.get("timestamp"):
                        continue
                    age = (now - datetime.fromisoformat(snap["timestamp"])).total_seconds()
                    # Check if agent has an extended check-in (stored in awareness)
                    effective_ttl = snap.get("extended_ttl", state.HEARTBEAT_TTL)
                    if age > effective_ttl:
                        stale_clis.append(cli)
                for cli in stale_clis:
                    del state._awareness[cli]
                if stale_clis:
                    logger.info("Pruned %d stale agent(s) from awareness.", len(stale_clis))
        except Exception as e:
            logger.error("Awareness pruning failed: %s", e)

        # Metrics always run, even if pruning failed
        try:
            state._last_pruning_cycle = datetime.now(timezone.utc).isoformat()
            await _write_metrics()
        except Exception as e:
            logger.error("Metrics write failed: %s", e)

        await anyio.sleep(60)


# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND: DISCOVERY EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

async def _run_discovery_background(job_id: str) -> None:
    """Run a discovery task in the background without blocking the tool response."""
    try:
        await state.discovery.run_discovery_task(job_id)
    except Exception as e:
        logger.error(f"Discovery background task {job_id} failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND: LOCK REAPING
# ═══════════════════════════════════════════════════════════════════════════

async def _reap_stale_locks() -> None:
    """Remove expired lock files.

    Scans data/coordination/locks/ and removes any lock whose
    acquired_at + ttl has passed. Called on acquire and periodically.
    """
    now = datetime.now(timezone.utc).timestamp()
    reaped = 0
    for lock_file in state.LOCKS_BASE.glob("*.lock"):
        try:
            def _read_lock():
                with open(lock_file) as f:
                    return json.load(f)
            lock_data = await anyio.to_thread.run_sync(_read_lock)
            acquired_at = lock_data.get("acquired_at", 0)
            ttl = lock_data.get("ttl", 3600)
            if now > acquired_at + ttl:
                lock_file.unlink()
                reaped += 1
        except Exception as e:
            logger.debug("Failed to reap stale lock %s: %s", lock_file, e)
    if reaped:
        logger.info("Reaped %d stale lock(s)", reaped)


# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND: HANDOFF REAPING
# ═══════════════════════════════════════════════════════════════════════════

async def _reap_stale_handoffs() -> None:
    """Reap stale handoff packets by MOVING them. Never by deleting.

    - pending/   older than 24h -> stale/   with {ttl_expired: true}
    - active/    older than 48h -> stale/
    - completed/ older than  7d -> archive/

    ══ M29 SOVEREIGN ARTIFACT PRESERVATION — deletion removed 2026-09-28 ══
    The previous version of this docstring read:

        - stale/   older than 14 days -> delete (M12)
        - archive/ older than 30 days -> delete (M12)

    and implemented both via `_delete_dir()`. That was a 37-day annihilation
    with no tombstone: a packet that aged out of `stale/` simply stopped
    existing, so an agent could not distinguish "never existed" from "purged",
    and no continuity reference to it could ever be resolved again. The "M12"
    citation was decoration — M12 is a token-state mandate, not a retention
    licence, and no mandate authorises silent destruction of the only record.

    `_delete_dir` and BOTH call sites are deleted, not commented out. There is
    now no code path in the Hivemind that unlinks an envelope. Retention is a
    query over timestamps against a policy constant (see
    `derived_retention_expires_at` in the envelope spec), never a transition
    some other process can trigger on a timer.
    """
    now = datetime.now(timezone.utc)

    def _reap_dir(src_dir: Path, dst_dir: Path, max_age_seconds: int, extra: dict = None):
        reaped = 0
        for f in src_dir.glob("*.json"):
            age = (now - datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)).total_seconds()
            if age > max_age_seconds:
                try:
                    with open(f) as fh:
                        packet = json.load(fh)
                    packet["status"] = dst_dir.name
                    packet["reaped_at"] = now.isoformat()
                    if extra:
                        packet.update(extra)
                    dst_path = dst_dir / f.name
                    with open(dst_path, "w") as fh:
                        fcntl.flock(fh, fcntl.LOCK_EX)
                        json.dump(packet, fh, indent=2)
                        fcntl.flock(fh, fcntl.LOCK_UN)
                    f.unlink()
                    # P0-4: carry the receipt journal alongside the packet.
                    # Without this, every journaled read becomes invisible the
                    # moment the packet reaps — the fix un-fixes itself.
                    journal = f.with_name(f.stem + ".receipts.jsonl")
                    if journal.is_file():
                        journal.replace(dst_dir / journal.name)
                    reaped += 1
                except Exception as e:
                    logger.debug("Failed to reap handoff %s: %s", f, e)
        return reaped

    # [M29 2026-09-28] `_delete_dir` DELETED, not commented out, and both of its
    # call sites removed with it. It is defined nowhere in the Hivemind now.
    # Three MOVES remain, all of which preserve the packet:
    #   pending/   > 24h -> stale/    {ttl_expired: true}
    #   active/    > 48h -> stale/    {ttl_expired: true}
    #   completed/ >  7d -> archive/
    # Nothing is ever unlinked from a queue that still holds live envelopes.
    reaped = await anyio.to_thread.run_sync(
        lambda: (
            _reap_dir(state.HANDOFF_PENDING, state.HANDOFF_STALE, 86400, {"ttl_expired": True})
            + _reap_dir(state.HANDOFF_ACTIVE, state.HANDOFF_STALE, 172800, {"ttl_expired": True})
            + _reap_dir(state.HANDOFF_COMPLETED, state.HANDOFF_ARCHIVE, 604800)
        )
    )
    if reaped:
        # [M29] Wording is "reaped", never "reaped/deleted": nothing is deleted.
        logger.info("Reaped %d handoff(s) to a later queue (nothing deleted)", reaped)
        # Rebuild index after reaping to prevent drift
        try:
            count = await handoff_index_rebuild()
            logger.debug("Handoff index rebuilt after reaping: %d packets", count)
        except Exception as e:
            logger.warning("Handoff index rebuild after reaping failed: %s", e)


# ═══════════════════════════════════════════════════════════════════════════
# BACKGROUND: REAPER LOOP
# ═══════════════════════════════════════════════════════════════════════════

async def _reaper_background() -> None:
    """Background loop that reaps stale locks and handoffs.

    [id-soft: quake-1996] Lazy Thinker Deletion — each reap is independent.
    If _reap_stale_locks() fails, _reap_stale_handoffs() still runs.
    """
    while True:
        try:
            await _reap_stale_locks()
        except Exception as e:
            logger.error("Reaper: stale locks failed: %s", e)

        try:
            await _reap_stale_handoffs()
        except Exception as e:
            logger.error("Reaper: stale handoffs failed: %s", e)

        await anyio.sleep(300)


# ═══════════════════════════════════════════════════════════════════════════
# HIVEMIND METRICS COLLECTION (hi-observability-1)
# ═══════════════════════════════════════════════════════════════════════════

async def _write_metrics() -> Dict[str, Any]:
    """Write Hivemind coordination metrics atomically to data/coordination/metrics.json.

    Collects real-time state from awareness, handoff queues, workspace locks,
    and extended sessions. Writes atomically (write .tmp, rename) for crash safety.

    Returns:
        The metrics dict for immediate use without re-reading from disk.

    [hi-observability-1] Hivemind Metrics Collection — local observability only.
    Does NOT send data anywhere (Mandate 8 — Zero Telemetry).
    """
    now = datetime.now(timezone.utc)
    now_ts = now.isoformat()

    # Count active agents (respect TTL)
    active_agents = 0
    async with state._awareness_lock:
        for _cli, snap in state._awareness.items():
            ts_str = snap.get("timestamp")
            if ts_str:
                ts = datetime.fromisoformat(ts_str)
                if (now - ts).total_seconds() <= state.HEARTBEAT_TTL:
                    active_agents += 1
            else:
                active_agents += 1

    # Count handoff queue items
    def _scan_handoffs():
        pending = len(list(state.HANDOFF_PENDING.glob("*.json")))
        active = len(list(state.HANDOFF_ACTIVE.glob("*.json")))
        completed = len(list(state.HANDOFF_COMPLETED.glob("*.json")))
        stale = len(list(state.HANDOFF_STALE.glob("*.json")))
        return pending, active, completed, stale

    pending_h, active_h, completed_h, stale_h = await anyio.to_thread.run_sync(_scan_handoffs)

    # Count workspace locks (active vs expired)
    def _scan_locks():
        active_locks = 0
        expired_locks = 0
        for lock_file in state.LOCKS_BASE.glob("*.lock"):
            try:
                with open(lock_file) as f:
                    ld = json.load(f)
                acquired_at = ld.get("acquired_at", 0)
                ttl = ld.get("ttl", 3600)
                if now.timestamp() > acquired_at + ttl:
                    expired_locks += 1
                else:
                    active_locks += 1
            except Exception:
                active_locks += 1
        return active_locks, expired_locks

    active_locks, expired_locks = await anyio.to_thread.run_sync(_scan_locks)

    # Count extended sessions (from awareness hot store)
    async with state._awareness_lock:
        extended_count = sum(1 for snap in state._awareness.values() if "extended_ttl" in snap)

    metrics: Dict[str, Any] = {
        "hivemind": {
            "active_agents": active_agents,
            "handoff_queue": {
                "pending": pending_h,
                "active": active_h,
                "completed": completed_h,
                "stale": stale_h,
                "total": pending_h + active_h + completed_h + stale_h,
            },
            "workspace_locks": {
                "active": active_locks,
                "expired": expired_locks,
            },
            "extended_sessions": extended_count,
            "pruning_cycle_last_run": state._last_pruning_cycle,
        },
        "updated_at": now_ts,
    }

    # Atomic write: .tmp -> rename
    state.METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = state.METRICS_PATH.with_suffix(".json.tmp")

    def _persist():
        with open(tmp_path, "w") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            json.dump(metrics, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
            fcntl.flock(f, fcntl.LOCK_UN)
        os.replace(str(tmp_path), str(state.METRICS_PATH))

    await anyio.to_thread.run_sync(_persist)
    return metrics
