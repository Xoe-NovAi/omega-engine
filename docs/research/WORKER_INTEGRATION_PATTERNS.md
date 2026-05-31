# 🔱 Omega Engine — Background Worker Integration Patterns
# ⬡ OMEGA ⬡ PROMETHEUS ⬡ gemma-4-31b-it ⬡ opencode ⬡ trc_worker_integration ⬡ PHASE-1

**AP Token**: `AP-WORKER-INTEGRATION-v1.0.0`
**Status**: ✅ READY FOR IMPLEMENTATION
**Last Updated**: 2026-05-16

---

## §1 Executive Summary

This guide specifies how to integrate background workers (model updater, Gemma maintenance) into the existing Omega Engine architecture. All workers must:

1. **Use AnyIO** for async operations (not asyncio)
2. **Emit events** to the existing `ObservabilityEngine`
3. **Use SessionManager** patterns for entity-scoped state
4. **Register CLI commands** via Typer
5. **Follow ResourceGuard** patterns for concurrency control

---

## §2 Worker Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      OMEGA ENGINE CORE                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐              │
│  │  Oracle      │   │  Observab.   │   │  SessionMgr │              │
│  │  (talk/summ) │   │  (log_event) │   │  (sessions) │              │
│  └──────┬───────┘   └──────┬───────┘   └──────┬───────┘              │
│         │                  │                  │                        │
│         ▼                  ▼                  ▼                        │
│  ┌─────────────────────────────────────────────────────────┐         │
│  │                   WORKER LAYER                           │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │         │
│  │  │ ModelUpdater │  │ GemmaWorker  │  │ Custom      │  │         │
│  │  │ (scheduler)  │  │ (maintenance)│  │ Workers    │  │         │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │         │
│  │         │                  │                  │         │         │
│  │         └──────────────────┼──────────────────┘         │         │
│  │                            ▼                              │         │
│  │                    ResourceGuard                          │         │
│  │                    (Semaphore concurrency)               │         │
│  └─────────────────────────────────────────────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## §3 Integration Point 1: AnyIO Patterns

### 3.1 Background Task Spawning

Workers run inside the Omega Engine's AnyIO event loop using `anyio.create_task()`:

```python
# src/omega/workers/my_worker.py
import anyio
from typing import Optional

class MyWorker:
    def __init__(self, config: dict):
        self.config = config
        self._running = False
        self._task: Optional[anyio.Task] = None

    async def start(self):
        """Start the worker as a background task."""
        if self._running:
            return

        self._running = True
        # Create background task within the main event loop
        self._task = anyio.create_task(self._run_loop())

    async def stop(self):
        """Gracefully stop the worker."""
        self._running = False
        if self._task:
            self._task.cancel()
            with anyio.move_on_after(5):  # 5 second graceful shutdown
                await self._task

    async def _run_loop(self):
        """Main worker loop - runs until stopped."""
        while self._running:
            await self._do_work()
            await anyio.sleep(self.config.get("interval_seconds", 60))
```

### 3.2 Concurrent Task Groups

For workers that need concurrent operations (e.g., fetching from multiple providers):

```python
# Use anyio.TaskGroup for concurrent operations
async def fetch_all_providers(self):
    async with anyio.create_task_group() as tg:
        tg.start_soon(self._fetch_openrouter)
        tg.start_soon(self._fetch_google)
        tg.start_soon(self._fetch_opencode_zen)

    # All three completed - aggregate results
    return self._aggregate_results()

async def _fetch_openrouter(self):
    # Individual provider fetch with error handling
    try:
        result = await self._make_request(...)
        self._results["openrouter"] = result
    except Exception as e:
        logger.warning(f"OpenRouter fetch failed: {e}")
        self._results["openrouter"] = None
```

### 3.3 Integration with ResourceGuard

Workers that use the ModelGateway must use ResourceGuard to prevent OOM:

```python
from omega.oracle.resource_guard import ResourceGuard

class MyWorker:
    def __init__(self, config: dict):
        self.guard = ResourceGuard(limit=1)

    async def do_inference(self, prompt: str):
        async with self.guard.lock():
            # Safe inference - only one model at a time
            return await self.model_gateway.generate(prompt)
```

**Reference**: `src/omega/oracle/resource_guard.py` (19 lines, Semaphore pattern)

---

## §4 Integration Point 2: Observability Integration

### 4.1 Event Types for Workers

Add worker-specific event types to the `EventType` class:

```python
# src/omega/observability.py - Add to existing EventType class
class EventType:
    # ... existing events ...

    # Worker-specific events
    WORKER_STARTED = "worker.started"
    WORKER_STOPPED = "worker.stopped"
    WORKER_HEALTH_CHECK = "worker.health_check"
    WORKER_ERROR = "worker.error"
    WORKER_TASK_COMPLETE = "worker.task_complete"

    # Model updater events
    MODEL_UPDATE_START = "model.update.start"
    MODEL_UPDATE_COMPLETE = "model.update.complete"
    MODEL_CHANGE_DETECTED = "model.change.detected"

    # Gemma worker events
    GEMMA_HEALTH_CHECK = "gemma.health_check"
    GEMMA_QUOTA_WARNING = "gemma.quota_warning"
    GEMMA_FAILOVER = "gemma.failover"
```

### 4.2 Logging Worker Events

```python
# Inside your worker
from omega.observability import get_engine, EventType, new_trace_id

class MyWorker:
    def __init__(self, config: dict):
        self.observability = get_engine()
        self.trace_id = new_trace_id()

    async def start(self):
        # Log worker started event
        self.observability.log_event(
            event_type=EventType.WORKER_STARTED,
            trace_id=self.trace_id,
            data={
                "worker": "my_worker",
                "config": self.config,
            }
        )

    async def _health_check_loop(self):
        while self._running:
            try:
                await self._check_health()
                self.observability.log_event(
                    event_type=EventType.WORKER_HEALTH_CHECK,
                    trace_id=self.trace_id,
                    data={"status": "healthy", "timestamp": ...}
                )
            except Exception as e:
                self.observability.log_event(
                    event_type=EventType.WORKER_ERROR,
                    trace_id=self.trace_id,
                    data={"error": str(e), "worker": "my_worker"}
                )
            await anyio.sleep(60)
```

### 4.3 Using TraceSession for Context

```python
# For complex operations, use TraceSession
async def run_update_cycle(self):
    with self.observability.trace() as trace:
        trace.log(EventType.MODEL_UPDATE_START, providers=["openrouter", "google"])

        # Do work...
        results = await self._fetch_all()

        trace.log(
            EventType.MODEL_UPDATE_COMPLETE,
            models_found=len(results),
            changes_detected=len(self._diff_results(results))
        )

        # Automatically records latency_ms in trace.data
```

**Reference**: `src/omega/observability.py` (276 lines, `log_event()` and `TraceSession`)

---

## §5 Integration Point 3: CLI Extension

### 5.1 Adding Worker Commands

Add worker status and control commands to the existing CLI:

```python
# src/omega/cli/oracle_cli.py - Add new commands

@app.command(name="worker-status")
def worker_status(
    worker: Optional[str] = typer.Argument(None, help="Specific worker name or omit for all"),
):
    """Show status of background workers."""
    # Load worker registry
    from omega.workers import get_worker_registry

    registry = get_worker_registry()
    if worker:
        status = registry.get_status(worker)
        console.print(f"[bold]{worker}[/bold]: {status}")
    else:
        table = Table(title="Background Workers")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Last Run")
        for name, status in registry.get_all_status():
            table.add_row(name, status["status"], status["last_run"])
        console.print(table)


@app.command(name="worker-logs")
def worker_logs(
    worker: str = typer.Argument(..., help="Worker name"),
    lines: int = typer.Option(50, "-n", help="Number of lines"),
):
    """Show recent logs for a specific worker."""
    log_path = Path("data/logs/workers") / f"{worker}.log"
    if not log_path.exists():
        console.print(f"[red]No logs found for {worker}[/red]")
        return

    content = log_path.read_text().splitlines()[-lines:]
    for line in content:
        console.print(line)
```

### 5.2 Worker Management Commands

```python
@app.command(name="worker-stop")
def worker_stop(
    worker: str = typer.Argument(..., help="Worker to stop"),
    force: bool = typer.Option(False, "--force", "-f", help="Force stop"),
):
    """Stop a running background worker."""
    from omega.workers import get_worker_registry
    registry = get_worker_registry()
    success = await registry.stop_worker(worker, force=force)
    if success:
        console.print(f"[green]✅ Worker '{worker}' stopped[/green]")
    else:
        console.print(f"[red]❌ Failed to stop worker '{worker}'[/red]")


@app.command(name="worker-start")
def worker_start(
    worker: str = typer.Argument(..., help="Worker to start"),
):
    """Start a background worker."""
    from omega.workers import get_worker_registry
    registry = get_worker_registry()
    success = await registry.start_worker(worker)
    if success:
        console.print(f"[green]✅ Worker '{worker}' started[/green]")
    else:
        console.print(f"[red]❌ Failed to start worker '{worker}'[/red]")
```

**Reference**: `src/omega/cli/oracle_cli.py` (411 lines, Typer pattern)

---

## §6 Integration Point 4: Configuration Management

### 6.1 Worker Configuration Schema

Workers add their config to `config/omega.yaml` under a namespaced key:

```yaml
# config/omega.yaml
omega:
  # ... existing config ...

# Worker configurations
workers:
  enabled: true

# Model Updater Worker
model_updater:
  enabled: true
  schedule:
    type: interval
    minutes: 60
  providers:
    - openrouter
    - google
    - opencode_zen
  change_threshold: 3

# Gemma Maintenance Worker
gemma_maintenance:
  enabled: true
  model: gemma-4-31b-it
  health_monitor:
    check_interval_seconds: 60
    timeout_seconds: 10
  quota_tracker:
    check_interval_seconds: 300
    warning_threshold_percent: 80
  observability:
    metrics_interval_seconds: 60

# Custom Worker
my_custom_worker:
  enabled: false
  interval_seconds: 300
  api_key: env:MY_WORKER_API_KEY
```

### 6.2 Loading Worker Config

```python
# src/omega/workers/registry.py
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class WorkerRegistry:
    """Central registry for all Omega background workers."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path("config/omega.yaml")
        self.config = self._load_config()
        self._workers: Dict[str, Any] = {}

    def _load_config(self) -> dict:
        """Load omega.yaml and extract worker configs."""
        with open(self.config_path) as f:
            full_config = yaml.safe_load(f)

        # Workers namespace
        return full_config.get("workers", {})

    def register_worker(self, name: str, worker: Any):
        """Register a worker instance."""
        self._workers[name] = worker

    async def start_all(self):
        """Start all enabled workers."""
        for name, worker in self._workers.items():
            worker_config = self.config.get(name, {})
            if worker_config.get("enabled", False):
                await worker.start()

    async def stop_all(self):
        """Stop all workers gracefully."""
        for name, worker in self._workers.items():
            await worker.stop()
```

### 6.3 Initialization in Omega Engine

```python
# src/omega/engine.py (or oracle.py __init__)
async def _init_workers(self):
    """Initialize and start background workers."""
    from omega.workers.registry import WorkerRegistry
    from omega.model_updater.scheduler import ModelUpdaterScheduler
    from omega.gemma_maintenance_worker import GemmaMaintenanceWorker

    registry = WorkerRegistry()

    # Register workers
    registry.register_worker(
        "model_updater",
        ModelUpdaterScheduler(registry.config.get("model_updater", {}))
    )
    registry.register_worker(
        "gemma_maintenance",
        GemmaMaintenanceWorker(registry.config.get("gemma_maintenance", {}))
    )

    # Start all enabled workers
    await registry.start_all()

    return registry
```

**Reference**: `config/omega.yaml` (22 lines, existing config structure)

---

## §7 Integration Point 5: Security & Permissions

### 7.1 Worker Pattern: Idempotent File Locking

Workers that might run in multiple instances use file-based locking:

```python
import fcntl
from pathlib import Path

class WorkerLock:
    """Ensure only one instance of a worker runs at a time."""

    def __init__(self, lock_name: str):
        self.lock_path = Path(f"data/locks/{lock_name}.lock")
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.lock_file = None

    def __enter__(self):
        self.lock_file = open(self.lock_path, "w")
        try:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return self
        except BlockingIOError:
            self.lock_file.close()
            raise RuntimeError(f"Another instance is running. Remove {self.lock_path} if stuck.")

    def __exit__(self, *args):
        if self.lock_file:
            fcntl.flock(self.lock_file.fileno(), fcntl.LOCK_UN)
            self.lock_file.close()
```

### 7.2 API Key Management

Workers use the same `.env` pattern as the rest of Omega:

```python
# Load API keys from environment with fallback
def get_worker_api_key(key_name: str, required: bool = True) -> Optional[str]:
    value = os.environ.get(key_name)
    if required and not value:
        logger.warning(f"Worker requires {key_name} but not set in environment")
    return value

# Usage in worker
api_key = get_worker_api_key("GOOGLE_API_KEY")
if not api_key:
    logger.warning("Gemma maintenance worker disabled - no API key")
    return
```

### 7.3 Permission Patterns

Follow existing patterns for file and resource access:

```python
# Workers should use the same DATA_DIR as the rest of Omega
from omega.observability import DATA_DIR as OBSERVABILITY_DATA_DIR
from omega.oracle.oracle import DATA_DIR as ORACLE_DATA_DIR

# All should resolve to the same path
WORKER_DATA_DIR = OBSERVABILITY_DATA_DIR  # Use the canonical path
```

---

## §8 Implementation Checklist

When adding a new worker to Omega:

| # | Task | File/Location | Reference |
|---|------|---------------|-----------|
| 1 | Define worker class | `src/omega/workers/<worker_name>.py` | §3.1 |
| 2 | Add event types | `src/omega/observability.py` EventType | §4.1 |
| 3 | Register in CLI | `src/omega/cli/oracle_cli.py` | §5.1 |
| 4 | Add config schema | `config/omega.yaml` | §6.1 |
| 5 | Register worker | `src/omega/workers/registry.py` | §6.3 |
| 6 | Add idempotent lock | Worker class | §7.1 |
| 7 | Add tests | `tests/test_<worker>.py` | — |

---

## §9 Code Reference Summary

| Component | File | Key Patterns |
|-----------|------|--------------|
| AnyIO Background Tasks | `orchestrator.py:24-60` | `BackgroundWorker`, `Semaphore`, `create_task()` |
| Observability | `observability.py:125-143` | `log_event()`, `TraceSession`, `EventType` |
| Session Manager | `session_manager.py:18-51` | `anyio.Path` async file I/O |
| Resource Guard | `resource_guard.py:15-18` | `async with self.guard.lock()` |
| CLI Commands | `oracle_cli.py:50-145` | `@app.command()`, Typer |
| Config Loading | `oracle_cli.py:31-46` | `_load_config()`, `_save_config()` |
| Worker Design | `AUTOMATED_MODEL_UPDATER_DESIGN.md` | Full implementation spec |
| Gemma Worker | `GEMMA_MAINTENANCE_WORKER_DESIGN.md` | Full implementation spec |

---

## §10 Example: Full Worker Integration

```python
# src/omega/workers/example_worker.py
"""Example worker showing all integration patterns."""

import logging
import anyio
from typing import Optional
from pathlib import Path

from omega.observability import get_engine, EventType, new_trace_id
from omega.oracle.resource_guard import ResourceGuard

logger = logging.getLogger(__name__)


class ExampleWorker:
    """
    Background worker demonstrating all integration patterns.

    Integrates with:
    - AnyIO for async operations
    - ObservabilityEngine for logging
    - ResourceGuard for concurrency
    - SessionManager for entity-scoped state
    """

    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get("enabled", False)
        self.interval = config.get("interval_seconds", 60)

        # Observability
        self.observability = get_engine()
        self.trace_id = new_trace_id()

        # Concurrency control
        self.guard = ResourceGuard(limit=1)

        # State
        self._running = False
        self._task: Optional[anyio.Task] = None

    # ── Lifecycle ───────────────────────────────────────────────────────
    async def start(self):
        """Start the worker."""
        if not self.enabled:
            logger.info(f"ExampleWorker disabled in config")
            return

        self._running = True
        self._task = anyio.create_task(self._run_loop())

        # Emit start event
        self.observability.log_event(
            event_type=EventType.WORKER_STARTED,
            trace_id=self.trace_id,
            data={"worker": "example_worker", "interval": self.interval}
        )
        logger.info("ExampleWorker started")

    async def stop(self):
        """Gracefully stop the worker."""
        self._running = False
        if self._task:
            self._task.cancel()
            with anyio.move_on_after(5):
                await self._task

        # Emit stop event
        self.observability.log_event(
            event_type=EventType.WORKER_STOPPED,
            trace_id=self.trace_id,
            data={"worker": "example_worker"}
        )
        logger.info("ExampleWorker stopped")

    # ── Main Loop ───────────────────────────────────────────────────────
    async def _run_loop(self):
        """Main worker loop."""
        while self._running:
            try:
                await self._do_work()
            except Exception as e:
                self.observability.log_event(
                    event_type=EventType.WORKER_ERROR,
                    trace_id=self.trace_id,
                    data={"worker": "example_worker", "error": str(e)}
                )
                logger.error(f"ExampleWorker error: {e}")

            await anyio.sleep(self.interval)

    async def _do_work(self):
        """Perform the actual work."""
        # Emit health check
        self.observability.log_event(
            event_type=EventType.WORKER_HEALTH_CHECK,
            trace_id=self.trace_id,
            data={"worker": "example_worker", "status": "ok"}
        )

        # Example: Use ResourceGuard for safe inference
        # async with self.guard.lock():
        #     result = await self.model_gateway.generate(prompt)

        # Emit completion
        self.observability.log_event(
            event_type=EventType.WORKER_TASK_COMPLETE,
            trace_id=self.trace_id,
            data={"worker": "example_worker", "task": "example_task"}
        )
```

---

*Every worker integrates into the Omega Engine as a first-class component.*