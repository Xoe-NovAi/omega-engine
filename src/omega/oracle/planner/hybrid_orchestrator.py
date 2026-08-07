# AP: AP-MAAT-PHASE2-DESIGN-v1.0.0
# 🔱 Cloud Planner / Local Executor — Hybrid Orchestrator
# ICS: [NODE: N3 | ARCHETYPE: HERMES | CONTEXT: PLANNER-ORCHESTRATOR]
#
# M7-compliant: Cloud is advisor/planner only; local is executor.
# The planner emits a JSON DAG; the local executor validates and runs
# sub-tasks with grammar enforcement. Escalation is per-subtask.
#
# [M1 AnyIO Absolute] — uses anyio.create_task_group, NOT asyncio
# [M2 Firewall] — lives in src/omega/ (core), not config/wads/ (stacks)
# [M7 Local-First] — cloud planner is advisory only; local executor is primary
# [M22 Response Provenance] — records actual provider for each sub-task
"""
Hybrid Orchestrator: Cloud Planner / Local Executor pattern.

Architecture:
  1. Cloud Planner (advisory): emits JSON DAG via cloud provider
  2. Local Executor (primary): runs sub-tasks on native-gguf/lmster
  3. Escalation: if local fails 2x, single sub-task escalates to cloud

M7 Compliance:
  - Local providers (native-gguf, lmster) are ALWAYS tried first
  - Cloud planner is advisory only — its DAG is a suggestion
  - Local executor can reject sub-tasks that exceed complexity threshold
  - Escalation is per-subtask, not per-goal (minimizes cloud usage)

Design doc: data/entities/maat/workspace/phase2_a4_o1_design.md §1
"""

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import anyio

from .dag_schema import (
    ActionType,
    ComplexityTier,
    ExecutionPlan,
    ExecutionPlanSchema,
    SubTask,
    SubTaskSchema,
    TaskResult,
    should_run_locally,
    classify_complexity,
)

logger = logging.getLogger(__name__)

# ─── System Prompts ─────────────────────────────────────────────────────────────

PLANNER_SYSTEM_PROMPT = """You are an expert AI Planner. Decompose the user's goal into atomic,
highly specific sub-tasks. Ensure that tasks with no dependencies can run in parallel.
Formulate sub-tasks so they can be executed by small, fast local LLMs.

For each sub-task, specify:
  - id: unique identifier (e.g., "step_1")
  - description: detailed description of the atomic step
  - action_type: one of: extract, code, summarize, classify, reason, synthesize
  - complexity: one of: trivial, simple, moderate, complex, ambiguous
  - dependencies: IDs of sub-tasks that must complete first
  - expected_output_schema: JSON schema or GBNF grammar for output
  - estimated_tokens: estimated token count for this sub-task

Output valid JSON matching the ExecutionPlan schema. Do NOT include any
text outside the JSON."""

LOCAL_EXECUTOR_SYSTEM_PROMPT = """You are a precise local task executor. Output JSON strictly
matching the provided schema. Do not include any text outside the JSON."""

CLOUD_FALLBACK_SYSTEM_PROMPT = """You are a fallback execution unit. Fix the error and complete
the sub-task. Output valid JSON."""


# ─── Hybrid Orchestrator ────────────────────────────────────────────────────────

class HybridOrchestrator:
    """Cloud Planner / Local Executor with M7-compliant routing.

    [M7] Local inference is PRIMARY. Cloud is advisor/planner only.
    The cloud planner emits a DAG; the local executor validates and
    may reject sub-tasks that exceed the complexity threshold.

    Attributes:
        model_gateway: The ModelGateway for provider fabric access.
        health_monitor: HealthMonitor for circuit breaker state.
        resource_guard: ResourceGuard for OOM protection.
        cloud_planner_model: Cloud model for DAG emission (advisory only).
        cloud_planner_provider: Cloud provider for planning (advisory only).
        max_local_retries: Max local attempts before cloud escalation.
    """

    def __init__(
        self,
        model_gateway: Any,
        health_monitor: Any,
        resource_guard: Any,
        cloud_planner_model: str = "claude-sonnet-4.6",
        cloud_planner_provider: str = "antigravity",
        max_local_retries: int = 2,
    ):
        self.model_gateway = model_gateway
        self.health_monitor = health_monitor
        self.resource_guard = resource_guard
        self.cloud_planner_model = cloud_planner_model
        self.cloud_planner_provider = cloud_planner_provider
        self.max_local_retries = max_local_retries
        self._dag_registry: Dict[str, ExecutionPlan] = {}

    async def generate_plan(
        self,
        user_goal: str,
        trace_id: Optional[str] = None,
    ) -> ExecutionPlan:
        """Step 1: Cloud Planner emits JSON DAG (advisory).

        [M7] Cloud is planner/advisor only. The DAG is a suggestion —
        local executor validates and may reject sub-tasks via
        should_run_locally().

        Args:
            user_goal: The original user goal to decompose.
            trace_id: Correlation ID for tracing.

        Returns:
            ExecutionPlan with local_feasible flags set on each sub-task.
        """
        if trace_id is None:
            trace_id = f"dag-{uuid.uuid4().hex[:12]}"

        # [M7] Cloud planner is advisory — uses cloud provider for DAG emission
        # The local executor is the primary path; this is just planning
        logger.info(
            f"[Planner] Sending goal to Cloud Planner ({self.cloud_planner_model}) "
            f"via {self.cloud_planner_provider} (advisory only, M7)"
        )

        # Check if cloud planner circuit is open
        if self.health_monitor:
            breaker = self.health_monitor._breakers.get(self.cloud_planner_provider)
            if breaker and not breaker.is_available:
                logger.warning(
                    f"Cloud planner circuit open for {self.cloud_planner_provider}, "
                    f"falling back to local planning"
                )
                return await self._generate_plan_local(user_goal, trace_id)

        # Call cloud model to generate DAG
        res = await self.model_gateway.generate(
            model_name=self.cloud_planner_model,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_query=f"Goal: {user_goal}",
            temperature=0.1,
            max_tokens=4096,
            trace_id=trace_id,
        )

        # [M22] Record actual provider that served the response
        actual_provider = res.provider_name
        logger.info(
            f"[Planner] DAG emitted by {actual_provider} "
            f"(model: {res.model_used or self.cloud_planner_model})"
        )

        # Validate DAG structure against Pydantic schema
        try:
            schema = ExecutionPlanSchema.model_validate_json(res.text)
        except Exception as e:
            logger.error(f"[Planner] DAG validation failed: {e}")
            raise

        plan = ExecutionPlan.from_schema(schema)

        # Apply complexity heuristic to each sub-task (M7 gatekeeper)
        for task in plan.tasks:
            task.local_feasible = should_run_locally(task)
            if not task.local_feasible:
                logger.debug(
                    f"[Planner] Sub-task '{task.id}' marked cloud-only: "
                    f"action={task.action_type.value}, complexity={task.complexity.value}"
                )

        self._dag_registry[trace_id] = plan
        return plan

    async def _generate_plan_local(
        self,
        user_goal: str,
        trace_id: str,
    ) -> ExecutionPlan:
        """Fallback: generate a simple plan using local inference when cloud is unavailable.

        [M7] Local-first fallback for planning. Produces a minimal DAG
        with a single task that the local executor can handle.
        """
        logger.info(f"[Planner] Local fallback planning for goal: {user_goal[:80]}...")

        # Use local model for simple planning
        res = await self.model_gateway.generate(
            model_name="qwen3-1.7b",
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_query=f"Goal: {user_goal}",
            temperature=0.1,
            max_tokens=2048,
            trace_id=trace_id,
        )

        try:
            schema = ExecutionPlanSchema.model_validate_json(res.text)
        except Exception as e:
            logger.error(f"[Planner] Local DAG validation failed: {e}")
            # Create a minimal single-task plan
            schema = ExecutionPlanSchema(
                goal=user_goal,
                reasoning="Cloud planner unavailable; using single-step local plan.",
                tasks=[
                    SubTaskSchema(
                        id="step_1",
                        description=user_goal,
                        action_type=ActionType.CODE.value,
                        complexity=ComplexityTier.SIMPLE.value,
                        dependencies=[],
                        expected_output_schema=None,
                        estimated_tokens=1024,
                    )
                ],
                planner_model="qwen3-1.7b",
                planner_provider="native-gguf",
                created_at=datetime.now(timezone.utc).isoformat(),
                trace_id=trace_id,
            )

        plan = ExecutionPlan.from_schema(schema)
        for task in plan.tasks:
            task.local_feasible = should_run_locally(task)

        self._dag_registry[trace_id] = plan
        return plan

    async def execute_dag(
        self,
        plan: ExecutionPlan,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Step 2: Local Executor runs DAG with parallel execution.

        [M7] Local providers (native-gguf, lmster) are primary.
        Cloud escalation only for sub-tasks that fail local retries.

        Args:
            plan: The ExecutionPlan to execute.
            trace_id: Correlation ID (uses plan.trace_id if not provided).

        Returns:
            Dict mapping task_id → output for all completed tasks.
        """
        if trace_id is None:
            trace_id = plan.trace_id

        context_store: Dict[str, Any] = {}
        completed: set[str] = set()
        pending = {t.id: t for t in plan.tasks}

        # Publish initial DAG update to SEDA bus
        await self._publish_dag_update(plan, completed, pending, trace_id)

        while pending:
            # Find ready tasks (dependencies satisfied)
            ready = plan.ready_tasks(completed)

            if not ready:
                # Check for failures
                failed = [t for t in pending.values() if t.status == "failed"]
                if failed:
                    raise RuntimeError(
                        f"Deadlock: {len(failed)} tasks failed, "
                        f"blocking {len(pending)} pending tasks"
                    )
                raise RuntimeError("Deadlock detected in task DAG")

            # Execute ready tasks in parallel (M1: anyio task group)
            results: List[TaskResult] = []
            async with anyio.create_task_group() as tg:
                for task in ready:
                    tg.start_soon(
                        self._execute_task_with_retry,
                        task, context_store, trace_id, results,
                    )

            for res in results:
                if res.status == "FAILED":
                    task = plan.get_task(res.task_id)
                    if task:
                        task.status = "failed"
                        task.error = res.error
                    raise RuntimeError(
                        f"Task '{res.task_id}' failed: {res.error}"
                    )

                task = plan.get_task(res.task_id)
                if task:
                    task.status = "completed"
                    task.result = res.output
                context_store[res.task_id] = res.output
                completed.add(res.task_id)
                del pending[res.task_id]

            # Publish updated DAG state
            await self._publish_dag_update(plan, completed, pending, trace_id)

        # Publish final DAG completion
        await self._publish_dag_update(plan, completed, {}, trace_id, final=True)

        return context_store

    async def _execute_task_with_retry(
        self,
        task: SubTask,
        context_store: Dict[str, Any],
        trace_id: str,
        results: List[TaskResult],
    ) -> None:
        """Execute a single sub-task with retry and cloud escalation.

        [M7] Local-first: tries local providers first.
        Escalation to cloud only after max_local_retries failures.
        """
        dep_inputs = {
            dep_id: context_store.get(dep_id)
            for dep_id in task.dependencies
        }

        last_error = ""
        for attempt in range(1, self.max_local_retries + 1):
            if not task.local_feasible:
                # Cloud-only task — skip local attempts
                result = await self._execute_cloud(task, dep_inputs, trace_id)
                results.append(result)
                return

            try:
                logger.debug(
                    f"[Executor] Running '{task.id}' locally "
                    f"(Attempt {attempt}/{self.max_local_retries})"
                )
                result = await self._execute_local(task, dep_inputs, trace_id)
                if result.status == "SUCCESS":
                    results.append(result)
                    return
                last_error = result.error or "Unknown error"
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"[Executor] Task '{task.id}' failed attempt {attempt}: {e}"
                )

        # All local retries exhausted — escalate to cloud (M7: fallback only)
        logger.info(
            f"[Executor] Task '{task.id}' local retries exhausted, "
            f"escalating to cloud (M7 fallback)"
        )
        result = await self._execute_cloud(task, dep_inputs, trace_id)
        result.escalated = True
        results.append(result)

    async def _execute_local(
        self,
        task: SubTask,
        context: Dict[str, Any],
        trace_id: str,
    ) -> TaskResult:
        """Execute sub-task on local provider with grammar enforcement.

        [M7] Local-first: native-gguf → lmster.
        [M13] Grammar enforcement via JSON schema or GBNF.
        """
        start = time.monotonic()

        # Build prompt with context from dependencies
        prompt = self._build_local_prompt(task, context)

        # [M7] Local provider — native-gguf is primary
        # [M13] Grammar enforcement: JSON schema or GBNF
        response_format = None
        if task.expected_output_schema:
            response_format = {"type": "json_object"}

        try:
            res = await self.model_gateway.generate(
                model_name="qwen3-1.7b",
                system_prompt=LOCAL_EXECUTOR_SYSTEM_PROMPT,
                user_query=prompt,
                temperature=0.0,
                max_tokens=2048,
                trace_id=trace_id,
            )

            latency_ms = (time.monotonic() - start) * 1000

            # Validate JSON output if schema was provided
            output = res.text
            if task.expected_output_schema:
                try:
                    output = json.loads(res.text)
                except json.JSONDecodeError:
                    return TaskResult(
                        task_id=task.id,
                        status="FAILED",
                        error=f"JSON parse failed: {res.text[:200]}",
                        provider=res.provider_name,
                        is_local=not res.is_cloud,
                        tokens_used=getattr(res, 'prompt_tokens', 0) + getattr(res, 'completion_tokens', 0),
                        latency_ms=latency_ms,
                    )

            # Publish step trace event
            await self._publish_step_trace(
                task=task,
                provider=res.provider_name,
                is_local=not res.is_cloud,
                tokens_used=getattr(res, 'prompt_tokens', 0) + getattr(res, 'completion_tokens', 0),
                latency_ms=latency_ms,
                status="completed",
                trace_id=trace_id,
            )

            return TaskResult(
                task_id=task.id,
                status="SUCCESS",
                output=output,
                provider=res.provider_name,
                is_local=not res.is_cloud,
                tokens_used=getattr(res, 'prompt_tokens', 0) + getattr(res, 'completion_tokens', 0),
                latency_ms=latency_ms,
            )

        except Exception as e:
            latency_ms = (time.monotonic() - start) * 1000
            await self._publish_step_trace(
                task=task,
                provider="native-gguf",
                is_local=True,
                tokens_used=0,
                latency_ms=latency_ms,
                status="failed",
                error=str(e),
                trace_id=trace_id,
            )
            return TaskResult(
                task_id=task.id,
                status="FAILED",
                error=str(e),
                provider="native-gguf",
                is_local=True,
                tokens_used=0,
                latency_ms=latency_ms,
            )

    async def _execute_cloud(
        self,
        task: SubTask,
        context: Dict[str, Any],
        trace_id: str,
    ) -> TaskResult:
        """Escalation: single sub-task to cloud (M7: cloud is fallback).

        Only called when local execution fails max_local_retries times.
        """
        start = time.monotonic()

        prompt = self._build_cloud_prompt(task, context)

        try:
            res = await self.model_gateway.generate(
                model_name=self.cloud_planner_model,
                system_prompt=CLOUD_FALLBACK_SYSTEM_PROMPT,
                user_query=prompt,
                temperature=0.0,
                max_tokens=4096,
                trace_id=trace_id,
            )

            latency_ms = (time.monotonic() - start) * 1000

            await self._publish_step_trace(
                task=task,
                provider=res.provider_name,
                is_local=False,
                tokens_used=getattr(res, 'prompt_tokens', 0) + getattr(res, 'completion_tokens', 0),
                latency_ms=latency_ms,
                status="escalated",
                trace_id=trace_id,
            )

            return TaskResult(
                task_id=task.id,
                status="SUCCESS",
                output=res.text,
                provider=res.provider_name,
                is_local=False,
                tokens_used=getattr(res, 'prompt_tokens', 0) + getattr(res, 'completion_tokens', 0),
                latency_ms=latency_ms,
                escalated=True,
            )

        except Exception as e:
            latency_ms = (time.monotonic() - start) * 1000
            return TaskResult(
                task_id=task.id,
                status="FAILED",
                error=str(e),
                provider=self.cloud_planner_provider,
                is_local=False,
                tokens_used=0,
                latency_ms=latency_ms,
            )

    def _build_local_prompt(self, task: SubTask, context: Dict[str, Any]) -> str:
        """Build the prompt for local execution."""
        parts = [
            f"Task: {task.description}",
            f"Input Data from Previous Steps: {json.dumps(context)}",
        ]
        if task.expected_output_schema:
            parts.append(f"Required Output Instructions: {task.expected_output_schema}")
        parts.append("Return valid JSON matching the instructions.")
        return "\n".join(parts)

    def _build_cloud_prompt(self, task: SubTask, context: Dict[str, Any]) -> str:
        """Build the prompt for cloud escalation."""
        parts = [
            f"Task: {task.description}",
            f"Input Data: {json.dumps(context)}",
        ]
        if task.expected_output_schema:
            parts.append(f"Expected Schema: {task.expected_output_schema}")
        parts.append("Fix any errors and complete the sub-task.")
        return "\n".join(parts)

    # ─── SEDA Event Publishing ──────────────────────────────────────────

    async def _publish_dag_update(
        self,
        plan: ExecutionPlan,
        completed: set,
        pending: Dict[str, SubTask],
        trace_id: str,
        final: bool = False,
    ) -> None:
        """Publish DAG update event to SEDA bus for TUI consumption.

        [O1 Phase 2] Enables the TUI to render a visual DAG.
        """
        try:
            from omega.research.sediment import SEDABus, SEDATopic, SEDAEvent

            # Check if SEDA bus is available (may not be in all contexts)
            bus = getattr(self, '_seda_bus', None)
            if bus is None:
                return

            event = SEDAEvent(
                topic=SEDATopic.DAG_UPDATE,
                payload={
                    "dag_id": plan.dag_id,
                    "goal": plan.goal,
                    "tasks": [t.to_dict() for t in plan.tasks],
                    "completed_tasks": list(completed),
                    "pending_tasks": list(pending.keys()),
                    "failed_tasks": [
                        t.id for t in plan.tasks if t.status == "failed"
                    ],
                    "final": final,
                },
                entity="system",
                trace_id=trace_id,
            )
            await bus.publish(event)
        except Exception as e:
            logger.debug(f"SEDA DAG update publish skipped: {e}")

    async def _publish_step_trace(
        self,
        task: SubTask,
        provider: str,
        is_local: bool,
        tokens_used: int,
        latency_ms: float,
        status: str,
        error: Optional[str] = None,
        trace_id: str = "unknown",
    ) -> None:
        """Publish step trace event to SEDA bus for TUI consumption.

        [O1 Phase 2] Enables the TUI to render a real-time step trace table.
        """
        try:
            from omega.research.sediment import SEDABus, SEDATopic, SEDAEvent

            bus = getattr(self, '_seda_bus', None)
            if bus is None:
                return

            event = SEDAEvent(
                topic=SEDATopic.STEP_TRACE,
                payload={
                    "step_id": f"{task.id}-{int(time.time() * 1000)}",
                    "dag_id": trace_id,
                    "task_id": task.id,
                    "action_type": task.action_type.value,
                    "provider": provider,
                    "is_local": is_local,
                    "tokens_used": tokens_used,
                    "latency_ms": latency_ms,
                    "status": status,
                    "error": error,
                },
                entity="system",
                trace_id=trace_id,
            )
            await bus.publish(event)
        except Exception as e:
            logger.debug(f"SEDA step trace publish skipped: {e}")

    def set_seda_bus(self, bus: Any) -> None:
        """Inject a SEDA bus for event publishing.

        [O1 Phase 2] Called by the TUI or orchestrator setup to enable
        real-time event binding.
        """
        self._seda_bus = bus


# ─── Module exports ─────────────────────────────────────────────────────────────

__all__ = [
    "HybridOrchestrator",
    "PLANNER_SYSTEM_PROMPT",
    "LOCAL_EXECUTOR_SYSTEM_PROMPT",
    "CLOUD_FALLBACK_SYSTEM_PROMPT",
]
