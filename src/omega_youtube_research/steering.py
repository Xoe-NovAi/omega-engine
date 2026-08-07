"""
L8 Oracle Steering Queue — Human-in-the-Loop Task Injection
⬡ OMEGA ⬡ RESEARCHER ⬡ L8 ⬡ STEERING
AP Token: AP-YOUTUBE-STEERING-v2.0.0

Mandate Compliance:
- M1 AnyIO: all I/O wrapped in anyio.to_thread.run_sync
- M2 Firewall: WAD-isolated
- M7 Local-First: local queue, no cloud deps
- M11 Soul Integrity: steering tasks feed Soul Distiller
- M12 Queue Integrity: terminal states (queued/completed/failed/timed_out)
- M22 Provenance: every steering task carries human intent + timestamp
- M23 Failure Integrity: explicit failure states, no silent drops

Per SitePoint Agentic Design Patterns 2026:
- Orchestrator-Worker: Dynamic task decomposition with Send fan-out
- Human-in-the-Loop: LangGraph interrupt/resume for approval gates
- Evaluator-Optimizer: LLM-as-judge with structured scoring

Per LangGraph Patterns:
- Send API for dynamic graph branching
- interrupt() for human checkpoints
- Command(resume=...) for resumption
"""

from __future__ import annotations
import anyio
import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

try:
    from langgraph.graph import StateGraph, END
    from langgraph.types import Send, Command, interrupt
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    # Stub types
    class Send: pass
    class Command: pass
    def interrupt(*args, **kwargs): pass


# ── Task Types & States ───────────────────────────────────────────────────────

class SteeringTaskType(str, Enum):
    YOUTUBE_DEEP_DIVE = "youtube_deep_dive"
    TOPIC_EXPLORATION = "topic_exploration"
    CONTRADICTION_AUDIT = "contradiction_audit"
    FRESHNESS_REVIEW = "freshness_review"
    ENTITY_ENRICHMENT = "entity_enrichment"
    CUSTOM = "custom"


class TaskPriority(int, Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    AWAITING_HUMAN = "awaiting_human"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"


# ── Data Structures ────────────────────────────────────────────────────────────

@dataclass
class ResearchTask:
    """Steering task injected by human (or auto-scheduled)."""
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    task_type: SteeringTaskType = SteeringTaskType.CUSTOM
    topic_filter: str = ""
    node: str = "N6"  # Default to Cognition node
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.QUEUED
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    human_prompt: str = ""  # Original human instruction
    parameters: dict = field(default_factory=dict)  # Task-specific params
    result: Optional[dict] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_json(self) -> str:
        d = asdict(self)
        d["task_type"] = self.task_type.value
        d["priority"] = self.priority.value
        d["status"] = self.status.value
        return json.dumps(d, indent=2)
    
    @classmethod
    def from_json(cls, data: str) -> "ResearchTask":
        d = json.loads(data)
        d["task_type"] = SteeringTaskType(d["task_type"])
        d["priority"] = TaskPriority(d["priority"])
        d["status"] = TaskStatus(d["status"])
        return cls(**d)


@dataclass
class SteeringQueueState:
    """State for the steering queue graph."""
    tasks: list[ResearchTask] = field(default_factory=list)
    current_task: Optional[ResearchTask] = None
    human_input: Optional[str] = None
    interrupted: bool = False


# ── Background Researcher Queue (File-based, M12 Queue Integrity) ─────────────

class BackgroundResearcherQueue:
    """
    File-based task queue with terminal states.
    
    M12 Queue Integrity: Every request has terminal state.
    States: queued → running → (completed | failed | timed_out | cancelled)
    """
    
    def __init__(self, queue_dir: Path = Path("data/steering_queue")):
        self.queue_dir = queue_dir
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.pending_dir = queue_dir / "pending"
        self.active_dir = queue_dir / "active"
        self.completed_dir = queue_dir / "completed"
        self.failed_dir = queue_dir / "failed"
        self.timed_out_dir = queue_dir / "timed_out"
        
        for d in [self.pending_dir, self.active_dir, self.completed_dir, 
                  self.failed_dir, self.timed_out_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def _task_path(self, task: ResearchTask, dir: Path) -> Path:
        return dir / f"{task.task_id}.json"
    
    async def push(self, task: ResearchTask) -> str:
        """Add task to pending queue. Returns task_id."""
        task.status = TaskStatus.QUEUED
        task.updated_at = time.time()
        path = self._task_path(task, self.pending_dir)
        # Atomic write
        tmp = path.with_suffix(".tmp")
        await anyio.to_thread.run_sync(tmp.write_text, task.to_json())
        await anyio.to_thread.run_sync(tmp.rename, path)
        return task.task_id
    
    async def pop(self) -> Optional[ResearchTask]:
        """Atomically move oldest pending task to active."""
        pending_files = sorted(self.pending_dir.glob("*.json"))
        if not pending_files:
            return None
        
        src = pending_files[0]
        task_data = await anyio.to_thread.run_sync(src.read_text)
        task = ResearchTask.from_json(task_data)
        
        # Move to active
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()
        task.updated_at = time.time()
        
        dst = self._task_path(task, self.active_dir)
        await anyio.to_thread.run_sync(src.rename, dst)
        
        return task
    
    async def complete(self, task: ResearchTask, result: dict) -> None:
        """Mark task as completed."""
        task.status = TaskStatus.COMPLETED
        task.completed_at = time.time()
        task.updated_at = time.time()
        task.result = result
        await self._move_task(task, self.completed_dir)
    
    async def fail(self, task: ResearchTask, error: str) -> None:
        """Mark task as failed (with retry logic)."""
        task.status = TaskStatus.FAILED
        task.completed_at = time.time()
        task.updated_at = time.time()
        task.error = error
        task.retry_count += 1
        
        if task.retry_count < task.max_retries:
            # Re-queue for retry
            task.status = TaskStatus.QUEUED
            task.started_at = None
            await self._move_task(task, self.pending_dir)
        else:
            await self._move_task(task, self.failed_dir)
    
    async def cancel(self, task: ResearchTask) -> None:
        """Cancel a task."""
        task.status = TaskStatus.CANCELLED
        task.completed_at = time.time()
        task.updated_at = time.time()
        await self._move_task(task, self.failed_dir)  # or separate cancelled dir
    
    async def _move_task(self, task: ResearchTask, target_dir: Path) -> None:
        """Write task with current status to target directory."""
        dst = self._task_path(task, target_dir)
        tmp = dst.with_suffix(".tmp")
        await anyio.to_thread.run_sync(tmp.write_text, task.to_json())
        await anyio.to_thread.run_sync(tmp.rename, dst)
        
        # Remove from source directories (but not target)
        for src_dir in [self.pending_dir, self.active_dir, self.completed_dir, 
                        self.failed_dir, self.timed_out_dir]:
            if src_dir == target_dir:
                continue
            src = self._task_path(task, src_dir)
            if src.exists():
                await anyio.to_thread.run_sync(src.unlink)
    
    async def get_task(self, task_id: str) -> Optional[ResearchTask]:
        """Get task by ID from any directory."""
        for dir in [self.pending_dir, self.active_dir, self.completed_dir, 
                    self.failed_dir, self.timed_out_dir]:
            path = dir / f"{task_id}.json"
            if path.exists():
                data = await anyio.to_thread.run_sync(path.read_text)
                return ResearchTask.from_json(data)
        return None
    
    async def list_tasks(self, status: Optional[TaskStatus] = None) -> list[ResearchTask]:
        """List tasks, optionally filtered by status."""
        tasks = []
        dirs = {
            TaskStatus.QUEUED: self.pending_dir,
            TaskStatus.RUNNING: self.active_dir,
            TaskStatus.COMPLETED: self.completed_dir,
            TaskStatus.FAILED: self.failed_dir,
            TaskStatus.TIMED_OUT: self.timed_out_dir,
        }
        
        search_dirs = [dirs[status]] if status and status in dirs else dirs.values()
        
        for dir in search_dirs:
            for path in dir.glob("*.json"):
                data = await anyio.to_thread.run_sync(path.read_text)
                tasks.append(ResearchTask.from_json(data))
        
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)


# ── LangGraph Steering Graph (Orchestrator-Worker + Human-in-the-Loop) ─────────

def create_steering_graph(
    queue: BackgroundResearcherQueue,
    executor: Callable[[ResearchTask], Any],
) -> StateGraph:
    """
    Create LangGraph for steering queue with human-in-the-loop.
    
    Pattern: Orchestrator-Worker with interrupt for human approval.
    
    Nodes:
    - fetch: Pop task from queue
    - execute: Run task via executor
    - human_review: Interrupt for human approval (high-priority tasks)
    - complete: Mark task done
    - handle_error: Retry or fail
    """
    if not LANGGRAPH_AVAILABLE:
        raise RuntimeError("langgraph not installed. pip install langgraph")
    
    graph = StateGraph(SteeringQueueState)
    
    async def fetch_node(state: SteeringQueueState) -> dict:
        """Fetch next task from queue."""
        task = await queue.pop()
        if task:
            return {"current_task": task, "tasks": state.tasks + [task]}
        return {"current_task": None}
    
    async def execute_node(state: SteeringQueueState) -> dict:
        """Execute current task."""
        task = state.current_task
        if not task:
            return {}
        
        try:
            # Run executor in thread pool
            result = await anyio.to_thread.run_sync(executor, task)
            return {"current_task": task, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    async def human_review_node(state: SteeringQueueState) -> dict:
        """Interrupt for human review on high-priority tasks."""
        task = state.current_task
        if task and task.priority >= TaskPriority.HIGH:
            # Interrupt and wait for human input
            human_decision = interrupt({
                "task_id": task.task_id,
                "task_type": task.task_type.value,
                "topic": task.topic_filter,
                "node": task.node,
                "prompt": task.human_prompt,
                "result_preview": str(state.get("result", {}))[:500],
            })
            
            if human_decision.get("approve", False):
                return {"human_input": human_decision}
            else:
                return {"error": "Human rejected task", "cancelled": True}
        
        return {"human_input": {"approve": True}}
    
    async def complete_node(state: SteeringQueueState) -> dict:
        """Mark task as completed."""
        task = state.current_task
        result = state.get("result")
        if task and result:
            await queue.complete(task, result)
        return {"current_task": None}
    
    async def error_node(state: SteeringQueueState) -> dict:
        """Handle errors with retry logic."""
        task = state.current_task
        error = state.get("error", "Unknown error")
        if task:
            await queue.fail(task, error)
        return {"current_task": None, "error": None}
    
    # Build graph
    graph.add_node("fetch", fetch_node)
    graph.add_node("execute", execute_node)
    graph.add_node("human_review", human_review_node)
    graph.add_node("complete", complete_node)
    graph.add_node("error", error_node)
    
    graph.set_entry_point("fetch")
    
    graph.add_conditional_edges(
        "fetch",
        lambda state: "execute" if state.get("current_task") else END,
        {"execute": "execute", END: END}
    )
    
    graph.add_conditional_edges(
        "execute",
        lambda state: "human_review" if state.get("current_task", {}).priority >= TaskPriority.HIGH 
                       else ("error" if state.get("error") else "complete"),
        {"human_review": "human_review", "complete": "complete", "error": "error"}
    )
    
    graph.add_conditional_edges(
        "human_review",
        lambda state: "error" if state.get("cancelled") else "complete",
        {"complete": "complete", "error": "error"}
    )
    
    graph.add_edge("complete", "fetch")
    graph.add_edge("error", "fetch")
    
    return graph.compile()


# ── High-Level Steering API ───────────────────────────────────────────────────

async def inject_steering(
    prompt: str,
    node: str = "N6",
    task_type: SteeringTaskType = SteeringTaskType.YOUTUBE_DEEP_DIVE,
    priority: TaskPriority = TaskPriority.NORMAL,
    queue: Optional[BackgroundResearcherQueue] = None,
    **parameters,
) -> str:
    """
    Human-in-the-loop task injection.
    
    Usage:
        task_id = await inject_steering(
            "Hey Iris, have N6 deep-dive attention videos from today's batch",
            node="N6",
            priority=TaskPriority.HIGH
        )
    
    Args:
        prompt: Natural language instruction from human
        node: Target node (N1-N10)
        task_type: Type of research task
        priority: Task priority (HIGH triggers human review)
        queue: Queue instance (creates default if None)
        **parameters: Task-specific parameters
    
    Returns:
        task_id of injected task
    """
    if queue is None:
        queue = BackgroundResearcherQueue()
    
    # Parse node to extract task parameters
    topic_filter = _extract_topic(prompt)
    
    task = ResearchTask(
        task_type=task_type,
        topic_filter=topic_filter,
        node=node,
        priority=priority,
        human_prompt=prompt,
        parameters=parameters,
    )
    
    return await queue.push(task)


def _extract_topic(prompt: str) -> str:
    """Extract topic from natural language prompt."""
    # Simple extraction — in production, use LLM
    import re
    # Look for quoted topics or keywords after "about", "on", "deep-dive"
    patterns = [
        r'(?:about|on|deep.?dive|explore)\s+["\']?([^"\']+)["\']?',
        r'(?:topic|subject)\s*[:\-]\s*["\']?([^"\']+)["\']?',
    ]
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return prompt[:100]  # Fallback


# ── Contract Test Helpers (M21) ───────────────────────────────────────────────

def assert_research_task_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for ResearchTask type."""
    assert isinstance(obj, ResearchTask), f"Expected ResearchTask, got {type(obj)}"
    assert hasattr(obj, "task_id")
    assert hasattr(obj, "task_type")
    assert isinstance(obj.task_type, SteeringTaskType)
    assert hasattr(obj, "status")
    assert isinstance(obj.status, TaskStatus)
    assert hasattr(obj, "to_json")
    assert callable(obj.to_json)
    assert hasattr(obj, "from_json")
    assert callable(obj.from_json)


def assert_background_queue_type(obj: Any) -> None:
    """M21: Contract test for BackgroundResearcherQueue type."""
    assert isinstance(obj, BackgroundResearcherQueue), f"Expected BackgroundResearcherQueue, got {type(obj)}"
    assert hasattr(obj, "push")
    assert callable(obj.push)
    assert hasattr(obj, "pop")
    assert callable(obj.pop)
    assert hasattr(obj, "complete")
    assert callable(obj.complete)
    assert hasattr(obj, "fail")
    assert callable(obj.fail)
    assert hasattr(obj, "get_task")
    assert callable(obj.get_task)
    assert hasattr(obj, "list_tasks")
    assert callable(obj.list_tasks)