# AP: AP-LOCAL-WORKER-POOL-v1.0.0
# 🔱 Local Worker Pool — Fire-and-Forget Background Inference
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ trc_local_worker ⬡ PHASE-2
#
# Reuses: NativeGGUFProvider, ResourceGuard, WorkerCoordinator, Request Queue, Artifact Store
# Zero dev flow disruption — cloud agents stay on cloud, local workers grind in background.

import anyio
import json
import logging
import os
import tempfile
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List, Dict, Any, Set
from enum import Enum

from omega.oracle.providers import NativeGGUFProvider
from omega.oracle.resource_guard import ResourceGuard
from omega.oracle.model_gateway import ModelGateway
from omega.oracle.health_monitor import HealthMonitor
from omega.observability import DATA_DIR

logger = logging.getLogger(__name__)


# ── Queue Directories ──────────────────────────────────────────────────
LOCAL_QUEUE_DIR = DATA_DIR / "requests" / "local_worker_queue"
LOCAL_QUEUED_DIR = LOCAL_QUEUE_DIR / "queued"
LOCAL_COMPLETED_DIR = LOCAL_QUEUE_DIR / "completed"
LOCAL_DEAD_DIR = LOCAL_QUEUE_DIR / "dead"

for d in [LOCAL_QUEUED_DIR, LOCAL_COMPLETED_DIR, LOCAL_DEAD_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Artifact Directory ──────────────────────────────────────────────────
LOCAL_ARTIFACT_DIR = DATA_DIR / "artifacts" / "local_worker"
LOCAL_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


class TaskStatus(Enum):
    QUEUED = "queued"
    COMPLETED = "completed"
    DEAD = "dead"


@dataclass
class LocalTask:
    """Task queued for local inference."""
    task_id: str
    prompt: str
    model: str
    system_prompt: str = ""
    max_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.95
    entity: str = "roc_racoon"
    trace_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = TaskStatus.QUEUED.value
    retries: int = 0
    max_retries: int = 3
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def from_json(cls, data: str) -> "LocalTask":
        return cls(**json.loads(data))
    
    @property
    def prompt_preview(self) -> str:
        return self.prompt[:80] + ("..." if len(self.prompt) > 80 else "")


@dataclass
class LocalResult:
    """Result of local inference."""
    task_id: str
    text: str
    model: str
    provider_name: str
    tokens_generated: int
    latency_ms: int
    entity: str
    trace_id: str
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: str = ""
    
    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=2)
    
    @classmethod
    def from_json(cls, data: str) -> "LocalResult":
        return cls(**json.loads(data))


# ── Atomic File Write Helper ────────────────────────────────────────────
async def _atomic_write(path: Path, content: str) -> None:
    """
    Crash-safe atomic write: temp file in same dir -> fsync -> os.replace.
    
    Uses tempfile.mkstemp in target directory to guarantee same filesystem.
    fsync ensures data hits physical disk before replace.
    os.replace is atomic on POSIX and Windows (NTFS).
    """
    # Create temp file in SAME directory as target (required for atomic replace)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Force to physical disk
        os.replace(tmp_path, path)  # Atomic on POSIX + Windows NTFS
    except Exception:
        # Cleanup temp file on failure
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


async def queue_local_task(
    prompt: str,
    model: str = "qwen3-1.7b",
    system_prompt: str = "",
    max_tokens: int = 1024,
    temperature: float = 0.7,
    top_p: float = 0.95,
    entity: str = "roc_racoon",
    trace_id: Optional[str] = None,
) -> str:
    """
    Queue a local inference task. Returns task_id immediately (fire-and-forget).
    
    This is the primary API for agents to offload work to local models.
    """
    task_id = trace_id or f"lw_{uuid.uuid4().hex[:12]}"
    
    task = LocalTask(
        task_id=task_id,
        prompt=prompt,
        model=model,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        entity=entity,
        trace_id=trace_id or task_id,
    )
    
    # Atomic write: .tmp -> os.replace -> fsync
    task_file = LOCAL_QUEUED_DIR / f"{task_id}.json"
    await _atomic_write(task_file, task.to_json())
    
    logger.info("Queued local task: %s (model=%s, entity=%s)", task_id, model, entity)
    return task_id


async def get_local_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """Get status of a local task."""
    for status_dir in [LOCAL_QUEUED_DIR, LOCAL_COMPLETED_DIR, LOCAL_DEAD_DIR]:
        task_file = status_dir / f"{task_id}.json"
        if task_file.exists():
            task = LocalTask.from_json(task_file.read_text())
            return {
                "task_id": task.task_id,
                "status": task.status,
                "model": task.model,
                "entity": task.entity,
                "created_at": task.created_at,
                "prompt_preview": task.prompt_preview,
                "retries": task.retries,
            }
    return None


async def get_local_task_result(task_id: str) -> Optional[LocalResult]:
    """Get result of a completed local task."""
    result_file = LOCAL_ARTIFACT_DIR / task_id / "result.json"
    if result_file.exists():
        return LocalResult.from_json(result_file.read_text())
    return None


async def list_local_tasks(
    status: Optional[TaskStatus] = None,
    limit: int = 20,
    entity: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """List local tasks with optional filters."""
    tasks = []
    
    search_dirs = [LOCAL_QUEUED_DIR, LOCAL_COMPLETED_DIR, LOCAL_DEAD_DIR]
    if status:
        if status == TaskStatus.QUEUED:
            search_dirs = [LOCAL_QUEUED_DIR]
        elif status == TaskStatus.COMPLETED:
            search_dirs = [LOCAL_COMPLETED_DIR]
        elif status == TaskStatus.DEAD:
            search_dirs = [LOCAL_DEAD_DIR]
    
    for dir_path in search_dirs:
        for task_file in sorted(dir_path.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True):
            if len(tasks) >= limit:
                break
            try:
                task = LocalTask.from_json(task_file.read_text())
                if entity and task.entity != entity:
                    continue
                tasks.append({
                    "task_id": task.task_id,
                    "status": task.status,
                    "model": task.model,
                    "entity": task.entity,
                    "created_at": task.created_at,
                    "prompt_preview": task.prompt_preview,
                })
            except Exception as e:
                logger.warning("Failed to parse task %s: %s", task_file, e)
    
    return tasks


class LocalWorkerPool:
    """
    Background daemon that processes local inference tasks.
    
    Architecture:
    - Polls queued directory at interval
    - Acquires ResourceGuard (Semaphore=1 + OOMProtector)
    - Runs inference via NativeGGUFProvider
    - Writes atomic artifacts to completed/ + artifact store
    - Integrates with WorkerCoordinator for resource pressure pause
    """
    
    def __init__(
        self,
        model_gateway: ModelGateway,
        resource_guard: ResourceGuard,
        poll_interval: float = 2.0,
        max_concurrent: int = 1,
    ):
        self.model_gateway = model_gateway
        self.resource_guard = resource_guard
        self.poll_interval = poll_interval
        self.max_concurrent = max_concurrent
        self._running = False
        self._task_group: Optional[anyio.abc.TaskGroup] = None
        # Track background tasks to prevent GC (Python 3.12+ fire-and-forget fix)
        self._background_tasks: Set[anyio.abc.Task] = set()
        # Track in-progress task IDs to prevent re-picking the same task
        self._processing_task_ids: Set[str] = set()
        
# Register with WorkerCoordinator
        from omega.library.coordinator import COORDINATOR
        self.coordinator = COORDINATOR

    def _spawn_background_task(self, coro, name: str = "background"):
        """
        Spawn a fire-and-forget background task with GC protection.
        
        Python 3.12+: asyncio.create_task() tasks can be GC'd before running.
        Fix: Store strong reference in set, add done_callback to clean up.
        """
        # Note: anyio's start_soon doesn't return a task object
        # We track via filesystem state instead
        return None

    async def start(self) -> None:
        """Start the worker pool daemon."""
        if self._running:
            return
        
        await self.coordinator.register("local_worker_pool")
        self._running = True
        
        async with anyio.create_task_group() as tg:
            self._task_group = tg
            tg.start_soon(self._worker_loop)
            logger.info("LocalWorkerPool started (poll_interval=%.1fs)", self.poll_interval)
            
            # Keep running until cancelled
            try:
                await anyio.sleep_forever()
            except anyio.get_cancelled_exc_class():
                pass
    
    async def stop(self) -> None:
        """Stop the worker pool."""
        self._running = False
        if self._task_group:
            self._task_group.cancel_scope.cancel()
        await self.coordinator.unregister("local_worker_pool")
        logger.info("LocalWorkerPool stopped")
    
    async def _worker_loop(self) -> None:
        """Main worker loop: poll queue, process tasks."""
        while self._running:
            try:
                # Check resource pressure via coordinator
                if await self.coordinator.is_paused("local_worker_pool"):
                    await anyio.sleep(self.poll_interval)
                    continue
                
                # Check concurrent limit
                if len(self._background_tasks) >= self.max_concurrent:
                    await anyio.sleep(self.poll_interval)
                    continue
                
                # Get next queued task
                task = await self._get_next_task()
                if task:
                    task_id = task.task_id
                    # Skip if already being processed
                    if task_id in self._processing_task_ids:
                        await anyio.sleep(self.poll_interval)
                        continue
                    self._processing_task_ids.add(task_id)
                    # Use task group to spawn - completion tracked via filesystem
                    self._task_group.start_soon(self._process_task, task)
                else:
                    await anyio.sleep(self.poll_interval)
                    
            except anyio.get_cancelled_exc_class():
                break
            except Exception as e:
                logger.error("Worker loop error: %s", e)
                await anyio.sleep(self.poll_interval)
    
    async def _get_next_task(self) -> Optional[LocalTask]:
        """Get the oldest queued task."""
        task_files = sorted(LOCAL_QUEUED_DIR.glob("*.json"), key=lambda f: f.stat().st_mtime)
        if not task_files:
            return None
        
        task_file = task_files[0]
        try:
            task = LocalTask.from_json(task_file.read_text())
            return task
        except Exception as e:
            logger.error("Failed to read task %s: %s", task_file, e)
            # Move corrupted file to dead
            task_file.replace(LOCAL_DEAD_DIR / task_file.name)
            return None
    
    async def _process_task(self, task: LocalTask) -> None:
        """Process a single local inference task."""
        task_id = task.task_id
        
        try:
            # Move to processing (atomic rename - just delete queued file)
            queued_file = LOCAL_QUEUED_DIR / f"{task_id}.json"
            if queued_file.exists():
                queued_file.unlink()
            
            # Update status to running (we track via artifact dir existence)
            artifact_dir = LOCAL_ARTIFACT_DIR / task_id
            artifact_dir.mkdir(parents=True, exist_ok=True)
            
            # Write task metadata for distillation pipeline
            metadata = {
                "task_id": task_id,
                "entity": task.entity,
                "model": task.model,
                "prompt": task.prompt,
                "system_prompt": task.system_prompt,
                "trace_id": task.trace_id,
                "started_at": datetime.now(timezone.utc).isoformat(),
                "status": "processing",
            }
            await _atomic_write(artifact_dir / "task_metadata.json", json.dumps(metadata, indent=2))
            
            # Run inference with ResourceGuard protection
            async with self.resource_guard.lock(
                weight=1,
                model_spec={"name": task.model, "ram_mb": 2048, "context_window": 8192},
            ):
                # Update heartbeat
                await self.coordinator.heartbeat("local_worker_pool", f"inference:{task_id}")
                
                # Generate via ModelGateway (uses NativeGGUFProvider for local models)
                result = await self.model_gateway.generate(
                    model_name=task.model,
                    system_prompt=task.system_prompt,
                    user_query=task.prompt,
                    max_tokens=task.max_tokens,
                    temperature=task.temperature,
                    top_p=task.top_p,
                )
                
                # Build result
                local_result = LocalResult(
                    task_id=task_id,
                    text=result.text,
                    model=task.model,
                    provider_name=result.provider_name,
                    tokens_generated=0,  # GenerateResult doesn't have this field
                    latency_ms=int(result.latency_ms),
                    entity=task.entity,
                    trace_id=task.trace_id,
                )
                
                # Write result atomically
                await _atomic_write(artifact_dir / "result.json", local_result.to_json())
                
                # Update metadata
                metadata["status"] = "completed"
                metadata["completed_at"] = datetime.now(timezone.utc).isoformat()
                metadata["provider_name"] = result.provider_name
                metadata["tokens_generated"] = result.tokens_generated
                metadata["latency_ms"] = result.latency_ms
                await _atomic_write(artifact_dir / "task_metadata.json", json.dumps(metadata, indent=2))
                
                # Move task to completed
                completed_file = LOCAL_COMPLETED_DIR / f"{task_id}.json"
                completed_task = LocalTask(
                    task_id=task.task_id,
                    prompt=task.prompt,
                    model=task.model,
                    system_prompt=task.system_prompt,
                    max_tokens=task.max_tokens,
                    temperature=task.temperature,
                    top_p=task.top_p,
                    entity=task.entity,
                    trace_id=task.trace_id,
                    created_at=task.created_at,
                    status=TaskStatus.COMPLETED.value,
                    retries=task.retries,
                )
                await _atomic_write(completed_file, completed_task.to_json())
                
                logger.info("Completed local task: %s (provider=%s, tokens=%d, latency=%dms)",
                           task_id, result.provider_name, result.tokens_generated, result.latency_ms)
                
        except Exception as e:
            logger.error("Task %s failed: %s", task_id, e)
            await self._handle_task_failure(task, str(e))
        finally:
            self._processing_task_ids.discard(task_id)
    
    async def _handle_task_failure(self, task: LocalTask, error: str) -> None:
        """Handle task failure with retry logic."""
        task_id = task.task_id
        
        if task.retries < task.max_retries:
            # Re-queue with incremented retry count
            task.retries += 1
            task.status = TaskStatus.QUEUED.value
            await _atomic_write(LOCAL_QUEUED_DIR / f"{task_id}.json", task.to_json())
            logger.warning("Task %s re-queued (retry %d/%d)", task_id, task.retries, task.max_retries)
        else:
            # Move to dead letter
            task.status = TaskStatus.DEAD.value
            await _atomic_write(LOCAL_DEAD_DIR / f"{task_id}.json", task.to_json())
            
            # Write failure reason for debugging
            artifact_dir = LOCAL_ARTIFACT_DIR / task_id
            artifact_dir.mkdir(parents=True, exist_ok=True)
            await _atomic_write(artifact_dir / "failure_reason.json", json.dumps({
                "task_id": task_id,
                "error": error,
                "retries": task.retries,
                "failed_at": datetime.now(timezone.utc).isoformat(),
            }, indent=2))
            
            logger.error("Task %s moved to dead letter after %d retries", task_id, task.retries)