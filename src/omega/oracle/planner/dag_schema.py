# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-MAAT-PHASE2-DESIGN-v1.0.0
# 🔱 Cloud Planner / Local Executor — DAG Schema & Complexity Heuristic
#
# M7-compliant design: Cloud is advisor/planner only; local is executor.
# The planner emits a JSON DAG; the local executor validates and may reject
# sub-tasks that exceed the complexity threshold.
#
# [M1 AnyIO Absolute] — pure dataclasses, no asyncio
# [M2 Firewall] — lives in src/omega/ (core), not config/wads/ (stacks)
# [M7 Local-First] — cloud planner is advisory only; local executor is primary
# [M14 Heritage] — inspired by [heritage: litellm-2024] capability flag pattern
"""
DAG schema and complexity heuristics for the Cloud Planner / Local Executor pattern.

This module provides:
  - Pydantic schemas for cloud-emitted execution DAGs
  - Complexity heuristic (should_run_locally) as the M7 gatekeeper
  - ActionType and ComplexityTier enums for sub-task classification

Design doc: data/entities/maat/workspace/phase2_a4_o1_design.md §1
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ─── Enums ──────────────────────────────────────────────────────────────────────


class ActionType(str, Enum):
    """Action types for sub-tasks in the execution DAG.

    Tasks are classified by the type of work they require.
    Only EXTRACT, CODE, SUMMARIZE, and CLASSIFY are safe for local execution.
    REASON and SYNTHESIZE require cloud-level reasoning and are cloud-only.
    """

    EXTRACT = "extract"  # Deterministic extraction (names, dates, etc.)
    CODE = "code"  # Atomic code operations (single function, test, regex)
    SUMMARIZE = "summarize"  # Text translation/formatting
    CLASSIFY = "classify"  # Discrete output choices
    REASON = "reason"  # Multi-step deductive reasoning (cloud-only)
    SYNTHESIZE = "synthesize"  # Long context cross-referencing (cloud-only)


class ComplexityTier(str, Enum):
    """Complexity classification for local execution feasibility.

    Used by should_run_local() to determine if a sub-task can run
    on local inference hardware (Zen 2, 12GB RAM).
    """

    TRIVIAL = "trivial"  # 0-2 steps, <512 tokens, deterministic
    SIMPLE = "simple"  # 2-4 steps, <2048 tokens, schema-constrained
    MODERATE = "moderate"  # 4-8 steps, <8192 tokens, some ambiguity
    COMPLEX = "complex"  # 8+ steps, >8192 tokens, multi-domain
    AMBIGUOUS = "ambiguous"  # Underspecified, requires judgment


# ─── Pydantic Schemas (for cloud-emitted JSON DAGs) ─────────────────────────────


class SubTaskSchema(BaseModel):
    """Pydantic schema for a single sub-task in the execution DAG.

    This is the schema enforced on cloud planner output. The local
    executor validates each sub-task against this schema before
    attempting local execution.

    [M7] The local_feasible field is set by should_run_local() —
    the local executor can reject cloud planner sub-tasks.
    """

    model_config = {"extra": "forbid"}

    id: str = Field(..., description="Unique sub-task identifier, e.g. 'step_1'")
    description: str = Field(..., description="Detailed description of the atomic step")
    action_type: str = Field(
        ..., description="Type of action: extract|code|summarize|classify|reason|synthesize"
    )
    complexity: str = Field(
        ..., description="Complexity tier: trivial|simple|moderate|complex|ambiguous"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="IDs of sub-tasks that must complete first"
    )
    input_context: Dict[str, Any] = Field(
        default_factory=dict, description="Input data from dependency tasks"
    )
    expected_output_schema: Optional[str] = Field(
        None, description="JSON schema or GBNF grammar for output"
    )
    estimated_tokens: int = Field(default=0, description="Estimated token count for this sub-task")
    local_feasible: bool = Field(
        default=True, description="Set by complexity heuristic — can this run locally?"
    )


class ExecutionPlanSchema(BaseModel):
    """Pydantic schema for a cloud-emitted execution plan (DAG).

    [M7] The cloud planner is advisory only. This schema is used to
    validate the cloud's DAG output. The local executor then applies
    should_run_local() to each sub-task and may reject cloud suggestions.
    """

    model_config = {"extra": "forbid"}

    goal: str = Field(..., description="Original user goal")
    reasoning: str = Field(..., description="High-level breakdown strategy from the planner")
    tasks: List[SubTaskSchema] = Field(..., description="Ordered list or DAG of atomic sub-tasks")
    planner_model: str = Field(
        ..., description="Cloud model that emitted this plan (advisory only)"
    )
    planner_provider: str = Field(..., description="Cloud provider name (advisory only)")
    created_at: str = Field(..., description="ISO 8601 timestamp of plan creation")
    trace_id: str = Field(..., description="Correlation ID for tracing")


# ─── Internal Dataclasses (for local use) ──────────────────────────────────────


@dataclass
class SubTask:
    """Internal representation of a sub-task for local execution.

    Wraps SubTaskSchema with runtime state (status, result, error).
    """

    id: str
    description: str
    action_type: ActionType
    complexity: ComplexityTier
    dependencies: List[str] = field(default_factory=list)
    input_context: Dict[str, Any] = field(default_factory=dict)
    expected_output_schema: Optional[str] = None
    estimated_tokens: int = 0
    local_feasible: bool = True
    # Runtime state
    status: str = "pending"  # pending, running, completed, failed, escalated
    result: Optional[Any] = None
    error: Optional[str] = None

    @classmethod
    def from_schema(cls, schema: SubTaskSchema) -> "SubTask":
        """Create a SubTask from a validated Pydantic schema."""
        return cls(
            id=schema.id,
            description=schema.description,
            action_type=ActionType(schema.action_type),
            complexity=ComplexityTier(schema.complexity),
            dependencies=schema.dependencies,
            input_context=schema.input_context,
            expected_output_schema=schema.expected_output_schema,
            estimated_tokens=schema.estimated_tokens,
            local_feasible=schema.local_feasible,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "action_type": self.action_type.value,
            "complexity": self.complexity.value,
            "dependencies": self.dependencies,
            "input_context": self.input_context,
            "expected_output_schema": self.expected_output_schema,
            "estimated_tokens": self.estimated_tokens,
            "local_feasible": self.local_feasible,
            "status": self.status,
            "result": self.result,
            "error": self.error,
        }


@dataclass
class ExecutionPlan:
    """Internal representation of an execution plan (DAG).

    Created from a validated ExecutionPlanSchema, with runtime
    state tracking for each sub-task.
    """

    goal: str
    reasoning: str
    tasks: List[SubTask]
    planner_model: str
    planner_provider: str
    created_at: str
    trace_id: str
    # Runtime state
    dag_id: str = field(default_factory=lambda: "")
    status: str = "pending"  # pending, running, completed, failed

    def __post_init__(self):
        if not self.dag_id:
            self.dag_id = self.trace_id

    @classmethod
    def from_schema(cls, schema: ExecutionPlanSchema) -> "ExecutionPlan":
        """Create an ExecutionPlan from a validated Pydantic schema."""
        tasks = [SubTask.from_schema(t) for t in schema.tasks]
        return cls(
            goal=schema.goal,
            reasoning=schema.reasoning,
            tasks=tasks,
            planner_model=schema.planner_model,
            planner_provider=schema.planner_provider,
            created_at=schema.created_at,
            trace_id=schema.trace_id,
        )

    def get_task(self, task_id: str) -> Optional[SubTask]:
        """Look up a sub-task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def ready_tasks(self, completed: set) -> List[SubTask]:
        """Return tasks whose dependencies are all completed."""
        return [
            t
            for t in self.tasks
            if t.status == "pending" and set(t.dependencies).issubset(completed)
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dag_id": self.dag_id,
            "goal": self.goal,
            "reasoning": self.reasoning,
            "tasks": [t.to_dict() for t in self.tasks],
            "planner_model": self.planner_model,
            "planner_provider": self.planner_provider,
            "created_at": self.created_at,
            "trace_id": self.trace_id,
            "status": self.status,
        }


@dataclass
class TaskResult:
    """Result of executing a single sub-task."""

    task_id: str
    status: str  # "SUCCESS" or "FAILED"
    output: Any = None
    error: Optional[str] = None
    provider: str = "unknown"
    is_local: bool = True
    tokens_used: int = 0
    latency_ms: float = 0.0
    escalated: bool = False


# ─── M7 Gatekeeper: Complexity Heuristic ───────────────────────────────────────

# Complexity thresholds (from Qdrant Full doc §3, line 1355)
# Adapted for Omega Engine's Zen 2 + 12GB RAM hardware profile
MAX_DEPENDENCY_DEPTH = 2  # >2 deps → cloud (compounding error)
MAX_LOCAL_TOKENS = 4096  # >4096 tokens → cloud (local distraction)
MAX_LOCAL_COMPLEXITY = ComplexityTier.SIMPLE  # Only trivial/simple run local

# Action types safe for local execution
LOCAL_SAFE_ACTIONS = {
    ActionType.EXTRACT,
    ActionType.CODE,
    ActionType.SUMMARIZE,
    ActionType.CLASSIFY,
}

# Action types that require cloud-level reasoning
CLOUD_ONLY_ACTIONS = {
    ActionType.REASON,
    ActionType.SYNTHESIZE,
}


def should_run_locally(subtask: SubTask) -> bool:
    """M7 Gatekeeper: determines if a sub-task can run on local inference.

    Cloud is advisor/planner only. Local executor decides accept/reject.
    This is the M7 enforcement point — when in doubt, route to cloud.

    Rules (adapted from Qdrant Full doc §3, line 1355):
      1. Dependency depth > 2 → cloud (compounding error rate)
      2. Context > 4096 tokens → cloud (local distraction)
      3. Unconstrained reasoning (REASON/SYNTHESIZE) → cloud
      4. Schema-constrained trivial/simple → local (grammar enforcement)
      5. Default: local only for trivial/simple, cloud for moderate+

    Args:
        subtask: The SubTask to evaluate.

    Returns:
        True if the sub-task can run on local inference, False for cloud.
    """
    # Rule 1: Dependency depth > 2 → cloud
    if len(subtask.dependencies) > MAX_DEPENDENCY_DEPTH:
        logger.debug(
            f"SubTask '{subtask.id}' → cloud: dependency depth "
            f"{len(subtask.dependencies)} > {MAX_DEPENDENCY_DEPTH}"
        )
        return False

    # Rule 2: Context > 4096 tokens → cloud
    if subtask.estimated_tokens > MAX_LOCAL_TOKENS:
        logger.debug(
            f"SubTask '{subtask.id}' → cloud: estimated tokens "
            f"{subtask.estimated_tokens} > {MAX_LOCAL_TOKENS}"
        )
        return False

    # Rule 3: Unconstrained reasoning → cloud
    if subtask.action_type in CLOUD_ONLY_ACTIONS:
        logger.debug(
            f"SubTask '{subtask.id}' → cloud: action_type {subtask.action_type.value} is cloud-only"
        )
        return False

    # Rule 4: Schema-constrained trivial/simple → local
    if subtask.expected_output_schema and subtask.complexity in (
        ComplexityTier.TRIVIAL,
        ComplexityTier.SIMPLE,
    ):
        logger.debug(
            f"SubTask '{subtask.id}' → local: schema-constrained {subtask.complexity.value} task"
        )
        return True

    # Rule 5: Default — local only for trivial/simple
    if subtask.complexity in (ComplexityTier.TRIVIAL, ComplexityTier.SIMPLE):
        logger.debug(f"SubTask '{subtask.id}' → local: complexity {subtask.complexity.value}")
        return True

    logger.debug(
        f"SubTask '{subtask.id}' → cloud: complexity "
        f"{subtask.complexity.value} exceeds local threshold"
    )
    return False


def classify_complexity(
    description: str,
    action_type: ActionType,
    estimated_tokens: int = 0,
    dependency_depth: int = 0,
) -> ComplexityTier:
    """Classify a sub-task's complexity tier.

    This is a heuristic classifier used by the cloud planner to tag
    sub-tasks. The local executor re-validates via should_run_locally().

    Args:
        description: Task description text.
        action_type: The ActionType for this task.
        estimated_tokens: Estimated token count.
        dependency_depth: Number of dependencies in the chain.

    Returns:
        ComplexityTier classification.
    """
    # Cloud-only actions are always complex/ambiguous
    if action_type in CLOUD_ONLY_ACTIONS:
        return ComplexityTier.COMPLEX

    # Trivial: deterministic, single-step, <512 tokens
    if action_type in LOCAL_SAFE_ACTIONS and estimated_tokens < 512 and dependency_depth <= 1:
        return ComplexityTier.TRIVIAL

    # Simple: 2-4 steps, <2048 tokens, schema-constrained
    if action_type in LOCAL_SAFE_ACTIONS and estimated_tokens < 2048 and dependency_depth <= 2:
        return ComplexityTier.SIMPLE

    # Moderate: 4-8 steps, <8192 tokens
    if estimated_tokens < 8192 and dependency_depth <= 4:
        return ComplexityTier.MODERATE

    # Complex: 8+ steps, >8192 tokens
    if estimated_tokens >= 8192:
        return ComplexityTier.COMPLEX

    # Ambiguous: falls through all checks
    return ComplexityTier.AMBIGUOUS


# ─── Module exports ─────────────────────────────────────────────────────────────

__all__ = [
    "ActionType",
    "ComplexityTier",
    "SubTaskSchema",
    "ExecutionPlanSchema",
    "SubTask",
    "ExecutionPlan",
    "TaskResult",
    "should_run_locally",
    "classify_complexity",
    "MAX_DEPENDENCY_DEPTH",
    "MAX_LOCAL_TOKENS",
    "MAX_LOCAL_COMPLEXITY",
    "LOCAL_SAFE_ACTIONS",
    "CLOUD_ONLY_ACTIONS",
]
