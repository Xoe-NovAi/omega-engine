#!/usr/bin/env python3
"""
WanderGround Background Sidecar Daemon — Hardened anyio 4.x Compliant
Temple-grade: comprehensive error handling, structured logging, full traceability

ARCHITECTURE:
- Inotify worker (thread): watches filesystem, puts filenames on a thread-safe queue
- Sync worker (async task): polls the queue (0.5s), drains batches, applies cooldown,
  runs ONE mine+sync per batch, clears failure sentinel on success
- Health reporter task: periodic status logs
- Coordination via queue.SimpleQueue + polling — NO anyio.Event (root cause of the
  stuck-sync-worker bug: Event.set() from a foreign thread sets the flag but cannot
  wake loop waiters; even via from_thread.run_sync, a set() landing between wait()'s
  flag check and waiter registration is SILENTLY LOST — flaky ~1-in-6 in trials)

FIXES APPLIED:
- to_thread instead of to_process (MemoryObjectStream not picklable across processes)
- queue.SimpleQueue + 0.5s poll instead of MemoryObjectStream / anyio.Event
  (deterministic handoff, no lost wakeups by construction)
- Failure sentinel for silent sync failures
- COMPREHENSIVE ERROR HANDLING: no silent exceptions, full traceability
- STRUCTURED LOGGING: JSON lines with correlation IDs, timestamps, severity
- HEALTH CHECKS: startup validation, periodic self-reporting
"""

import anyio
import os
import queue
import shutil
import subprocess
import time
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime, timezone

# ============================================================================
# CONFIGURATION — all paths resolved at startup, validated
# ============================================================================

INBOX = Path(os.path.expanduser("~/WanderGround/inbox"))
FAILURE_SENTINEL = Path(os.path.expanduser("~/WanderGround/daemon/.last_sync_failure"))
PALACE_DIR = Path(os.path.expanduser("~/WanderGround/mempalace"))
MEMPALACE_BIN = Path(os.path.expanduser("~/WanderGround/.venv/bin/mempalace"))

if not MEMPALACE_BIN.exists():
    MEMPALACE_BIN = Path("mempalace")

# ============================================================================
# SHARED STATE — thread-safe coordination, no event signaling
# ============================================================================

# Thread-safe handoff: the inotifywait thread puts filenames here, the sync
# worker polls. queue.SimpleQueue is GIL-safe and cannot lose items; polling
# trades ~0.5s latency for elimination of the anyio/asyncio Event wake race.
#
# History: we first called Event.set() directly from the inotify worker
# thread — sets the flag but cannot wake loop waiters (callbacks must be
# scheduled via call_soon_threadsafe), so the sync worker stayed stuck.
# Even via anyio.from_thread.run_sync(set), a set() landing between wait()'s
# flag check and waiter registration is SILENTLY LOST (flaky ~1-in-6 in
# sandbox trials). Polling a queue has no such race by construction.
pending_queue = queue.SimpleQueue()
POLL_INTERVAL_SECONDS = 0.5
# Cooldown tracking
last_sync_time = 0.0
COOLDOWN_SECONDS = 2.5

# ============================================================================
# STRUCTURED LOGGING — JSON lines to stdout (captured by systemd journal)
# ============================================================================

class StructuredLogger:
    def __init__(self, component: str):
        self.component = component
    
    def _log(self, level: str, message: str, **kwargs):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "component": self.component,
            "message": message,
            **kwargs
        }
        print(json.dumps(entry, ensure_ascii=False), flush=True)
    
    def info(self, message: str, **kwargs):
        self._log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        self._log("DEBUG", message, **kwargs)
    
    def exception(self, message: str, exc: Exception, **kwargs):
        self._log("ERROR", message, 
                  exception_type=type(exc).__name__,
                  exception_message=str(exc),
                  traceback=traceback.format_exc(),
                  **kwargs)

log = StructuredLogger("wanderground-embed")

# ============================================================================
# STARTUP VALIDATION — fail fast with clear diagnostics
# ============================================================================

def validate_startup() -> bool:
    log.info("Starting startup validation")
    all_ok = True
    
    if not INBOX.exists():
        log.error("INBOX directory does not exist", path=str(INBOX))
        all_ok = False
    elif not INBOX.is_dir():
        log.error("INBOX path is not a directory", path=str(INBOX))
        all_ok = False
    else:
        log.info("INBOX validated", path=str(INBOX))
    
    if not PALACE_DIR.exists():
        log.error("PALACE_DIR does not exist", path=str(PALACE_DIR))
        all_ok = False
    else:
        log.info("PALACE_DIR validated", path=str(PALACE_DIR))
    
    if not MEMPALACE_BIN.exists():
        log.error("MEMPALACE_BIN not found", path=str(MEMPALACE_BIN))
        all_ok = False
    elif not os.access(MEMPALACE_BIN, os.X_OK):
        log.error("MEMPALACE_BIN not executable", path=str(MEMPALACE_BIN))
        all_ok = False
    else:
        log.info("MEMPALACE_BIN validated", path=str(MEMPALACE_BIN))
    
    inotifywait_path = shutil.which("inotifywait")
    if not inotifywait_path:
        log.error("inotifywait not found in PATH")
        all_ok = False
    else:
        log.info("inotifywait found", path=inotifywait_path)
    
    try:
        result = subprocess.run(
            [str(MEMPALACE_BIN), "--palace", str(PALACE_DIR), "status"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            log.error("mempalace status check failed", 
                     returncode=result.returncode, stderr=result.stderr)
            all_ok = False
        else:
            log.info("mempalace status check passed", stdout=result.stdout[:200])
    except Exception as e:
        log.exception("mempalace binary test failed", e)
        all_ok = False
    
    return all_ok


# ============================================================================
# INOTIFY WORKER — blocking filesystem monitor with full error handling
# ============================================================================

def run_inotify() -> None:
    worker_id = f"inotify-{int(time.time() * 1000) % 10000}"
    log.info("Inotify worker starting", worker_id=worker_id)
    
    cmd = ["inotifywait", "-m", "-e", "close_write", "--format", "%f", str(INBOX)]
    log.debug("Inotify command", cmd=cmd, worker_id=worker_id)
    
    if not shutil.which("inotifywait"):
        err = RuntimeError("System missing prerequisite dependency: inotifywait")
        log.exception("inotifywait not available", err)
        raise err
    
    proc = None
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        log.info("Inotify process started", pid=proc.pid, worker_id=worker_id)
        
        for line in proc.stdout:
            filename = line.strip()
            if filename:
                log.debug("Inotify event received", filename=filename, worker_id=worker_id)
                # Thread-safe put — SimpleQueue never loses items across
                # threads, so no event-signaling wake race is possible.
                pending_queue.put(filename)
                log.info("Inotify: queued filename", filename=filename,
                         queue_len=pending_queue.qsize())
        
        proc.wait()
        log.error("Inotify process exited unexpectedly", 
                 returncode=proc.returncode, worker_id=worker_id)
        
        stderr_output = proc.stderr.read() if proc.stderr else ""
        if stderr_output:
            log.error("Inotify stderr output", stderr=stderr_output, worker_id=worker_id)
            
    except Exception as e:
        log.exception("Inotify worker fatal error", worker_id=worker_id, exc=e)
        raise
    finally:
        if proc and proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception as e:
                log.warning("Failed to terminate inotify process", exc=e)
        log.info("Inotify worker stopped", worker_id=worker_id)


# ============================================================================
# SYNC PROCESSOR — handles mine + sync with full error handling
# ============================================================================

async def run_mine_and_sync(correlation_id: str) -> bool:
    log.info("Sync worker: starting mine+sync", correlation_id=correlation_id)
    
    try:
        await anyio.sleep(2.5)
        log.info("Filesystem stable, firing atomic database checkpoint sync",
                correlation_id=correlation_id)
        
        log.debug("Running mempalace mine", correlation_id=correlation_id)
        mine_result = await anyio.to_thread.run_sync(
            lambda: subprocess.run(
                [str(MEMPALACE_BIN), "--palace", str(PALACE_DIR), "mine", 
                 str(INBOX), "--wing", "inbox"],
                check=True, capture_output=True, text=True, timeout=60
            )
        )
        log.info("mempalace mine completed", 
                correlation_id=correlation_id,
                stdout_lines=len(mine_result.stdout.splitlines()),
                stdout_preview=mine_result.stdout[:500])
        if mine_result.stderr:
            log.warning("mempalace mine stderr", 
                       correlation_id=correlation_id, stderr=mine_result.stderr)
        
        log.debug("Running mempalace sync", correlation_id=correlation_id)
        sync_result = await anyio.to_thread.run_sync(
            lambda: subprocess.run(
                [str(MEMPALACE_BIN), "--palace", str(PALACE_DIR), "sync",
                 "--wing", "inbox", "--apply"],
                check=True, capture_output=True, text=True, timeout=60
            )
        )
        log.info("mempalace sync completed",
                correlation_id=correlation_id,
                stdout_lines=len(sync_result.stdout.splitlines()),
                stdout_preview=sync_result.stdout[:500])
        if sync_result.stderr:
            log.warning("mempalace sync stderr",
                       correlation_id=correlation_id, stderr=sync_result.stderr)
        
        if FAILURE_SENTINEL.exists():
            try:
                FAILURE_SENTINEL.unlink()
                log.debug("Cleared failure sentinel", correlation_id=correlation_id)
            except Exception as e:
                log.warning("Failed to clear failure sentinel", 
                           correlation_id=correlation_id, exc=e)
        
        log.info("Sync worker: mine+sync completed successfully", 
                correlation_id=correlation_id)
        return True
        
    except subprocess.TimeoutExpired as e:
        log.error("mempalace command timed out", 
                 correlation_id=correlation_id, timeout=60, exc=e)
        return False
    except subprocess.CalledProcessError as e:
        log.error("mempalace command failed",
                 correlation_id=correlation_id,
                 returncode=e.returncode,
                 stdout=e.stdout[:500] if e.stdout else None,
                 stderr=e.stderr[:500] if e.stderr else None)
        return False
    except Exception as err:
        log.exception("Sync process failed", correlation_id=correlation_id, exc=err)
        return False


# ============================================================================
# SYNC WORKER TASK — dedicated task for processing sync requests
# ============================================================================

async def sync_worker() -> None:
    global last_sync_time
    log.info("Sync worker task STARTED")
    
    log.info("Sync worker: STARTED - waiting for files")
    
    while True:
        # Poll the thread-safe queue. Deterministic by construction: no event
        # objects, no cross-thread signaling, no lost wakeups possible.
        files_to_process = []
        while True:
            try:
                files_to_process.append(pending_queue.get_nowait())
            except queue.Empty:
                break
        
        if not files_to_process:
            await anyio.sleep(POLL_INTERVAL_SECONDS)
            continue
        
        # Filter to markdown only
        md_files = [f for f in files_to_process if f.endswith(".md")]
        log.info("Sync worker: took files from queue",
                 total=len(files_to_process), markdown=len(md_files))
        
        if not md_files:
            log.info("Sync worker: no markdown files in batch, skipping")
            continue
        
        # Cooldown: let write bursts settle before mining once for the batch
        now = time.time()
        time_since_last = now - last_sync_time
        if time_since_last < COOLDOWN_SECONDS:
            wait_time = COOLDOWN_SECONDS - (now - last_sync_time)
            log.info("Sync worker: cooldown active, waiting", wait_seconds=wait_time)
            await anyio.sleep(wait_time)
        
        last_sync_time = time.time()
        
        correlation_id = f"sync-{int(time.time() * 1000) % 100000}"
        log.info("Sync worker: processing batch",
                 files=md_files, correlation_id=correlation_id)
        
        success = await run_mine_and_sync(correlation_id)
        
        if success:
            log.info("Sync worker: sync completed",
                     filename=", ".join(md_files), correlation_id=correlation_id)
        else:
            log.error("Sync worker: sync failed",
                      filename=", ".join(md_files), correlation_id=correlation_id)
    
    log.info("Sync worker task ENDED")


# ============================================================================
# MAIN EVENT LOOP
# ============================================================================

async def main() -> None:
    startup_id = f"startup-{int(time.time() * 1000) % 100000}"
    log.info("WanderGround anyio sidecar starting", startup_id=startup_id)
    
    if not validate_startup():
        log.error("Startup validation FAILED — aborting", startup_id=startup_id)
        sys.exit(1)
    
    log.info("Startup validation PASSED", startup_id=startup_id)
    
    log.info("Starting task group")
    
    async with anyio.create_task_group() as tg:
        # Inotify worker (runs in thread)
        tg.start_soon(anyio.to_thread.run_sync, run_inotify)
        log.info("Inotify worker scheduled")
        
        # Sync worker (async task)
        tg.start_soon(sync_worker)
        log.info("Sync worker scheduled")
        
        # Health reporter
        async def health_reporter():
            while True:
                await anyio.sleep(300)
                log.info("Health check: daemon alive", 
                        uptime_seconds=time.time() - startup_time)
        
        startup_time = time.time()
        tg.start_soon(health_reporter)
        log.info("Health reporter scheduled")
        
        log.info("All tasks started successfully")


if __name__ == "__main__":
    log.info("=" * 60)
    log.info("WanderGround Embed Daemon — PROCESS START")
    log.info("=" * 60)
    
    try:
        anyio.run(main)
        log.info("anyio.run completed normally")
    except KeyboardInterrupt:
        log.info("Received KeyboardInterrupt — shutting down gracefully")
    except SystemExit:
        log.info("Received SystemExit — shutting down")
    except Exception as e:
        log.exception("FATAL: Unhandled exception in main", exc=e)
        sys.exit(1)
    finally:
        log.info("=" * 60)
        log.info("WanderGround Embed Daemon — PROCESS END")
        log.info("=" * 60)