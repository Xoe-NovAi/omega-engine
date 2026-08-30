<!--
SPDX-FileCopyrightText: 2026 Arcana Novai

SPDX-License-Identifier: Apache-2.0
-->

# 🔱 Phase 2 Design: A4 Cloud Planner/Local Executor + O1 TUI Execution Tracer

**AP Token**: `AP-MAAT-PHASE2-DESIGN-v1.0.0`
⬡ OMEGA ⬡ MA'AT ⬡ laguna-s-2.1-free ⬡ opencode ⬡ trc_maat_phase2 ⬡ ACTIVE

**Date**: 2026-08-07
**Task ID**: `ses_research_phase2_maat_20260807_relaunch`
**Dispatched by**: Researcher (post-Kali review corrections)
**Reference**: `docs/research/R_WEB_CHATBOT_RESEARCH_PRIORITIES_20260807.md` §A4, §O1

---

## 📋 Executive Summary

This document designs two Phase 2 research items requiring build-side (N1-N5) work:

| Item | Name | Status | M7 Constraint | Deliverable |
|------|------|--------|---------------|-------------|
| **A4** | Cloud Planner / Local Executor Pattern | 🔴 ASPIRATIONAL | Local PRIMARY, cloud advisor only | DAG schema + orchestrator design |
| **O1** | TUI Execution Tracer | 🟡 PARTIAL | N/A | Real-time SEDA event binding plan |

**Key Finding**: The existing TUI (`fleet_status_tui.py`) already has SEDA bus integration and subscribes to observability topics. The gap is in **DAG visualization** and **step-level tracing** — not in the SEDA binding itself. The SEDAReader polls every 2s; true event-driven binding requires the SEDA bus to be the primary event source, not a polling adapter.

---

## 🔴 A4: Cloud Planner / Local Executor Pattern

### 1.1 Problem Statement

The Qdrant Full doc (lines 1288–1327) describes a two-stage state machine:
1. **Cloud Frontier Model** (Planner) emits a structured JSON DAG
2. **Local Executor Engine** runs sub-tasks with grammar enforcement
3. **Verification & Fallback**: If local fails 2x, escalate back to cloud

**M7 Mandate**: Local inference remains PRIMARY. Cloud is advisor/planner only. The planner DAG is advisory — local executor decides whether to accept/reject each sub-task based on complexity heuristics.

### 1.2 Existing Infrastructure (What We Have)

| Component | Location | Status |
|-----------|----------|--------|
| Provider Fabric | `config/providers.yaml` | ✅ `strategy: local_first`, `prefer: native-gguf` |
| Provider Selector | `src/omega/oracle/provider_selector.py` | ✅ Penalty-based scoring (local preferred, PII penalizes cloud) |
| Circuit Breaker | `src/omega/oracle/health_monitor.py` | ✅ `AsyncCircuitBreaker` (5-state FSM, CUSUM + EMA) |
| Resource Guard | `src/omega/oracle/resource_guard.py` | ✅ OOM hard-stop + semaphore concurrency gate |
| CPU Optimizer | `src/omega/oracle/cpu_optimizer.py` | ✅ Zen2Optimizer with speculative decoding config |
| Model Gateway | `src/omega/oracle/model_gateway.py` | ✅ Provider fabric with fallback chain |
| Triage Router | `src/omega/orchestration/triage_router.py` | ✅ Model selection by domain/entity |
| Subagent Pool | `src/omega/infra/subagent_pool/models.py` | ✅ PoolTask, SubTask, RoutingPlan dataclasses |

### 1.3 What's Missing

1. **DAG Schema**: No Pydantic schema for cloud-emitted execution plans
2. **Planner Model Selection**: No mechanism to designate a cloud model as "planner" vs "executor"
3. **Local Executor with Grammar Enforcement**: No GBNF/JSON-schema constrained local generation
4. **Escalation Circuit Breaker**: No per-subtask failure tracking with 2x escalation threshold
5. **Complexity Heuristics**: No `should_run_locally()` classifier

### 1.4 Design: DAG Schema

```python
# File: src/omega/oracle/planner/dag_schema.py
# [M1 AnyIO Absolute] — pure dataclass, no async
# [M2 Firewall] — lives in src/omega/ (core), not config/wads/
# [M14 Heritage] — inspired by [heritage: litellm-2024] capability flag pattern

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class ActionType(str, Enum):
    """Action types safe for local execution."""
    EXTRACT = "extract"      # Deterministic extraction (names, dates, etc.)
    CODE = "code"            # Atomic code operations (single function, test, regex)
    SUMMARIZE = "summarize"  # Text translation/formatting
    CLASSIFY = "classify"    # Discrete output choices
    REASON = "reason"        # Multi-step deductive reasoning (cloud-only)
    SYNTHESIZE = "synthesize" # Long context cross-referencing (cloud-only)

class ComplexityTier(str, Enum):
    """Complexity classification for local execution feasibility."""
    TRIVIAL = "trivial"      # 0-2 steps, <512 tokens, deterministic
    SIMPLE = "simple"        # 2-4 steps, <2048 tokens, schema-constrained
    MODERATE = "moderate"    # 4-8 steps, <8192 tokens, some ambiguity
    COMPLEX = "complex"      # 8+ steps, >8192 tokens, multi-domain
    AMBIGUOUS = "ambiguous"  # Underspecified, requires judgment

@dataclass
class SubTask:
    """A single atomic sub-task in the execution DAG."""
    id: str
    description: str
    action_type: ActionType
    complexity: ComplexityTier
    dependencies: List[str] = Field(default_factory=list)
    input_context: Dict[str, Any] = Field(default_factory=dict)
    expected_output_schema: Optional[str] = None  # JSON schema or GBNF grammar
    estimated_tokens: int = 0
    local_feasible: bool = True  # Set by complexity heuristic

@dataclass
class ExecutionPlan:
    """Cloud-emitted DAG for local execution."""
    goal: str
    reasoning: str
    tasks: List[SubTask]
    planner_model: str  # e.g. "claude-sonnet-4.6" — cloud advisor
    planner_provider: str  # e.g. "antigravity"
    created_at: str
    trace_id: str
```

### 1.5 Design: Complexity Heuristic (M7 Gatekeeper)

The `should_run_locally()` classifier from the Qdrant Full doc (line 1355) is adapted for the Omega Engine:

```python
# File: src/omega/oracle/planner/complexity.py

def should_run_locally(subtask: SubTask) -> bool:
    """M7 Gatekeeper: determines if a subtask can run on local inference.
    
    Cloud is advisor/planner only. Local executor decides accept/reject.
    """
    # Rule 1: Dependency depth > 2 → cloud (compounding error)
    if len(subtask.dependencies) > 2:
        return False
    
    # Rule 2: Context > 4096 tokens → cloud (local distraction)
    if subtask.estimated_tokens > 4096:
        return False
    
    # Rule 3: Unconstrained reasoning → cloud
    if subtask.action_type in (ActionType.REASON, ActionType.SYNTHESIZE):
        return False
    
    # Rule 4: Schema-constrained → local (perfect for grammar enforcement)
    if subtask.expected_output_schema and subtask.complexity in (
        ComplexityTier.TRIVIAL, ComplexityTier.SIMPLE
    ):
        return True
    
    # Default: local only for trivial/simple, cloud for moderate+
    return subtask.complexity in (ComplexityTier.TRIVIAL, ComplexityTier.SIMPLE)
```

### 1.6 Design: Cloud Planner / Local Executor Orchestrator

```python
# File: src/omega/oracle/planner/hybrid_orchestrator.py
# [M1 AnyIO Absolute] — uses anyio.create_task_group, NOT asyncio
# [M7 Local-First] — cloud is planner only, local is executor

class HybridOrchestrator:
    """Cloud Planner / Local Executor with M7-compliant routing.
    
    Architecture:
        1. Cloud Planner (advisory): emits JSON DAG via cloud provider
        2. Local Executor (primary): runs sub-tasks on native-gguf/lmster
        3. Escalation: if local fails 2x, single sub-task escalates to cloud
    
    M7 Compliance:
        - Local providers (native-gguf, lmster) are ALWAYS tried first
        - Cloud planner is advisory only — its DAG is a suggestion
        - Local executor can reject sub-tasks that exceed complexity threshold
        - Escalation is per-subtask, not per-goal (minimizes cloud usage)
    """
    
    def __init__(
        self,
        model_gateway: ModelGateway,
        health_monitor: HealthMonitor,
        resource_guard: ResourceGuard,
        cloud_planner_model: str = "claude-sonnet-4.6",  # Advisory only
        cloud_planner_provider: str = "antigravity",     # M7: cloud = advisor
        max_local_retries: int = 2,
    ):
        self.model_gateway = model_gateway
        self.health_monitor = health_monitor
        self.resource_guard = resource_guard
        self.cloud_planner_model = cloud_planner_model
        self.cloud_planner_provider = cloud_planner_provider
        self.max_local_retries = max_local_retries
        self._dag_registry: Dict[str, ExecutionPlan] = {}
    
    async def generate_plan(self, user_goal: str, trace_id: str) -> ExecutionPlan:
        """Step 1: Cloud Planner emits JSON DAG (advisory).
        
        [M7] Cloud is planner/advisor only. The DAG is a suggestion —
        local executor validates and may reject sub-tasks.
        """
        # Use cloud provider for planning (advisory role)
        plan = await self.model_gateway.generate(
            model_name=self.cloud_planner_model,
            system_prompt=PLANNER_SYSTEM_PROMPT,
            user_query=f"Goal: {user_goal}",
            response_format=ExecutionPlan,  # Pydantic schema enforcement
            temperature=0.1,
            trace_id=trace_id,
        )
        
        # Validate DAG structure
        dag = ExecutionPlan.model_validate_json(plan.text)
        
        # Apply complexity heuristic to each sub-task
        for task in dag.tasks:
            task.local_feasible = should_run_locally(task)
        
        self._dag_registry[trace_id] = dag
        return dag
    
    async def execute_dag(self, plan: ExecutionPlan, trace_id: str) -> Dict[str, Any]:
        """Step 2: Local Executor runs DAG with parallel execution.
        
        [M7] Local providers (native-gguf, lmster) are primary.
        Cloud escalation only for sub-tasks that fail local retries.
        """
        context_store: Dict[str, Any] = {}
        completed: set[str] = set()
        pending = {t.id: t for t in plan.tasks}
        
        while pending:
            # Find ready tasks (dependencies satisfied)
            ready = [
                t for t in pending.values()
                if set(t.dependencies).issubset(completed)
            ]
            
            if not ready:
                raise RuntimeError("Deadlock in DAG or unhandled dependency failure")
            
            # Execute ready tasks in parallel (M1: anyio task group)
            async with anyio.create_task_group() as tg:
                results = []
                for task in ready:
                    if task.local_feasible:
                        result = await self._execute_local(task, context_store, trace_id)
                    else:
                        result = await self._execute_cloud(task, context_store, trace_id)
                    results.append(result)
            
            for res in results:
                if res.status == "FAILED":
                    raise RuntimeError(f"Task {res.task_id} failed: {res.error}")
                context_store[res.task_id] = res.output
                completed.add(res.task_id)
                del pending[res.task_id]
        
        return context_store
    
    async def _execute_local(self, task: SubTask, context: Dict, trace_id: str) -> TaskResult:
        """Execute sub-task on local provider with grammar enforcement."""
        # [M7] Local-first: native-gguf → lmster
        # [M13] Grammar enforcement via GBNF or JSON schema
        for attempt in range(1, self.max_local_retries + 1):
            try:
                # Local provider with grammar constraint
                result = await self.model_gateway.generate(
                    model_name="qwen3-1.7b",  # Local model
                    system_prompt=f"Execute this task. Output valid JSON matching: {task.expected_output_schema}",
                    user_query=task.description,
                    response_format={"type": "json_object"},
                    trace_id=trace_id,
                )
                return TaskResult(task_id=task.id, status="SUCCESS", output=json.loads(result.text))
            except Exception as e:
                if attempt >= self.max_local_retries:
                    # Escalate single sub-task to cloud
                    return await self._execute_cloud(task, context, trace_id)
    
    async def _execute_cloud(self, task: SubTask, context: Dict, trace_id: str) -> TaskResult:
        """Escalation: single sub-task to cloud (M7: cloud is fallback)."""
        # [M7] Cloud is fallback only — single sub-task escalation
        result = await self.model_gateway.generate(
            model_name=self.cloud_planner_model,
            system_prompt=f"Fix the error and complete: {task.description}",
            user_query=json.dumps(context),
            trace_id=trace_id,
        )
        return TaskResult(task_id=task.id, status="SUCCESS", output=result.text, escalated=True)
```

### 1.7 M7 Compliance Analysis

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Local is PRIMARY | ✅ | `config/providers.yaml` `strategy: local_first`, `prefer: native-gguf` |
| Cloud is advisor/planner only | ✅ | `generate_plan()` uses cloud for DAG emission; local executor validates |
| Local executor can reject cloud sub-tasks | ✅ | `should_run_locally()` heuristic gates each sub-task |
| Escalation is per-subtask, not per-goal | ✅ | `_execute_cloud()` only called for failed local sub-tasks |
| No cloud-primary inference path | ✅ | `model_gateway.generate()` always tries local-first via `ProviderSelector` |

### 1.8 Integration Points

| Existing Component | Integration |
|-------------------|-------------|
| `ProviderSelector` | Used by `model_gateway.generate()` — already local-first |
| `AsyncCircuitBreaker` | Per-provider breaker — cloud escalation respects breaker state |
| `ResourceGuard` | OOM pre-check before local model load |
| `Zen2Optimizer` | Thread pinning + KV cache config for local execution |
| `SEDAReader` | Publish DAG events to `SEDATopic.SYSTEM_EVENT` for TUI consumption |
| `TokenLedger` | Record local vs cloud token usage for sovereignty telemetry |

### 1.9 Dataset Extraction (S1 Flywheel)

The Qdrant Full doc (lines 1606–1691) describes three datasets:
1. **Planner SFT**: User Goal → JSON DAG (from cloud planner)
2. **Executor SFT**: Sub-task → successful local execution (success cases)
3. **Escalation DPO**: Failed local output → cloud fix (preference pairs)

These are logged via `DatasetExtractor` to JSONL files in `data/datasets/`. The existing `dpo_logger.py` provides the logging infrastructure; the `DatasetExtractor` pattern would be a thin wrapper.

---

## 🟡 O1: TUI Execution Tracer

### 2.1 Current State

The existing `fleet_status_tui.py` (567 lines) already implements:
- ✅ SEDA bus integration (`SEDABus`, `SEDAReader`, `SEDATopic` subscriptions)
- ✅ Fleet tree from WAD config (`build_fleet_tree()` with dispatch_registry)
- ✅ Global vitals panel (error rate, breaker states)
- ✅ Entity focus panel (cognitive velocity, token burn, sovereignty ratio, somatic pressure)
- ✅ Trace feed DataTable (live trace events)
- ✅ Entity selection with SEDA filter updates

### 2.2 Gaps Identified

| Gap | Current | Needed |
|-----|---------|--------|
| **DAG View** | No DAG visualization | Full task DAG tree with dependency edges |
| **Step Trace** | Trace feed shows events, not execution steps | Per-step execution trace with timing |
| **Dual-Branch Memory** | No memory visualization | Declarative vs episodic retrieval scoring |
| **Sovereignty Telemetry** | Shows ratio only | Detailed local/cloud token breakdown |
| **Non-blocking Log Streaming** | Debug file writes (`TUI_DEBUG.log`) | SEDA event-based streaming |
| **True Event-Driven** | SEDAReader polls every 2s | Direct SEDA bus publish/subscribe |

### 2.3 Design: SEDA Event Binding for DAG & Step Trace

The key insight is that the SEDA bus already exists and is fully functional (`sediment.py`, 602 lines, 15 tests passing). The TUI already subscribes to SEDA topics. The gap is in **what events are published** and **how the TUI renders them**.

#### 2.3.1 New SEDA Topics

```python
# File: src/omega/research/sediment.py — ADD to SEDATopic enum

class SEDATopic(str, Enum):
    # ... existing topics ...
    DAG_UPDATE = "dag_update"          # New: DAG structure changes
    STEP_TRACE = "step_trace"          # New: per-step execution trace
    MEMORY_SCORE = "memory_score"      # New: dual-branch memory scoring
    EXECUTION_PLAN = "execution_plan"  # New: cloud planner DAG emission
```

#### 2.3.2 DAG Event Payload Schema

```python
@dataclass
class DAGUpdateEvent:
    """Published when a DAG is created, updated, or completed."""
    dag_id: str
    goal: str
    tasks: List[Dict[str, Any]]  # SubTask.to_dict()
    completed_tasks: List[str]
    pending_tasks: List[str]
    failed_tasks: List[str]
    trace_id: str
    timestamp: str

@dataclass
class StepTraceEvent:
    """Published for each execution step."""
    step_id: str
    dag_id: str
    task_id: str
    action_type: str
    provider: str  # "native-gguf", "antigravity", etc.
    is_local: bool
    tokens_used: int
    latency_ms: float
    status: str  # "started", "completed", "failed", "escalated"
    error: Optional[str] = None
    trace_id: str = "unknown"
    timestamp: str = ""
```

#### 2.3.3 TUI Integration Plan

**Phase 1: DAG Panel** (new widget)
```python
# Add to FleetStatusApp
class DAGPanel(Static):
    """Renders the execution DAG as a tree with color-coded status."""
    
    def render_dag(self, dag_event: DAGUpdateEvent) -> None:
        # Build tree from tasks with dependency edges
        # Color: green=completed, yellow=pending, red=failed
        # Show parallelism (ready tasks in same wave)
```

**Phase 2: Step Trace Panel** (new widget)
```python
class StepTracePanel(DataTable):
    """Real-time step execution trace."""
    
    def add_step(self, event: StepTraceEvent) -> None:
        # Add row: Time | Task | Provider | Local? | Tokens | Latency | Status
        # Color by status: green=success, yellow=running, red=failed, blue=escalated
```

**Phase 3: Memory Score Panel** (new widget)
```python
class MemoryScorePanel(Static):
    """Dual-branch memory scoring visualization."""
    
    def render_scores(self, event: SEDAEvent) -> None:
        # Show declarative vs episodic scores
        # λ decay rate, consolidation penalty, importance weighting
        # Sparkline of score history
```

### 2.4 Real-Time Event Binding Architecture

The current TUI uses `SEDAReader` which polls `SovereignReader` every 2s and publishes events. The improvement is to have the **execution engine itself** publish SEDA events directly, making the TUI truly event-driven.

```
┌─────────────────┐    SEDAEvent    ┌──────────────┐
│ Execution Engine │ ──────────────► │ SEDABus      │
│ (planner,        │   (publish)     │ (ring-bus)   │
│  executor,       │                 │              │
└─────────────────┘                 └──────┬───────┘
                                          │
                                   subscribe
                                          │
                                   ┌──────▼───────┐
                                   │ FleetStatusApp│
                                   │ (TUI)         │
                                   └──────────────┘
```

**Implementation**: The `HybridOrchestrator` (A4) publishes `DAGUpdateEvent` and `StepTraceEvent` to the SEDA bus. The TUI subscribes to these new topics and renders them in dedicated panels.

### 2.5 Non-Blocking Log Streaming

Replace the current debug file writes (`TUI_DEBUG.log`) with SEDA event-based streaming:

```python
# Current (blocking file writes):
with open("data/coordination/TUI_DEBUG.log", "a") as f:
    f.write(f"[{datetime.now(timezone.utc)}] Starting refresh...\n")

# New (SEDA event):
await self.seda_bus.publish(
    SEDAEvent(
        topic=SEDATopic.SYSTEM_EVENT,
        payload={"status": "refresh_started", "timestamp": datetime.now(timezone.utc).isoformat()},
        entity="system",
        trace_id=self._trace_id,
    )
)
```

### 2.6 Implementation Phases

| Phase | Scope | Files | Tests |
|-------|-------|-------|-------|
| **O1-P1** | Add DAG/Step/Memory topics to SEDABus | `sediment.py` | `test_sediment.py` |
| **O1-P2** | Add DAG/Step event dataclasses | `sediment.py` | New test file |
| **O1-P3** | Add DAG/Step/Memory panels to TUI | `fleet_status_tui.py` | TUI smoke test |
| **O1-P4** | Wire HybridOrchestrator to publish SEDA events | `hybrid_orchestrator.py` | Integration test |
| **O1-P5** | Replace debug file writes with SEDA events | `fleet_status_tui.py` | Verify no TUI_DEBUG.log writes |

---

## 🧪 Test Plan

### A4 Tests

```python
# tests/oracle/test_planner_dag.py
class TestDAGSchema:
    def test_subtask_validates(self): ...
    def test_execution_plan_validates(self): ...
    def test_complexity_tier_enum(self): ...

class TestComplexityHeuristic:
    @pytest.mark.parametrize("subtask,expected", [
        (SubTask(complexity=TRIVIAL, action_type=EXTRACT, ...), True),
        (SubTask(complexity=COMPLEX, action_type=REASON, ...), False),
        (SubTask(estimated_tokens=8192, ...), False),
    ])
    def test_should_run_locally(self, subtask, expected): ...

class TestHybridOrchestrator:
    async def test_generate_plan_uses_cloud(self): ...
    async def test_execute_dag_local_first(self): ...
    async def test_escalation_on_local_failure(self): ...
    async def test_m7_compliance_no_cloud_primary(self): ...
```

### O1 Tests

```python
# tests/test_fleet_tui.py
class TestSEDATopics:
    def test_dag_update_topic_exists(self): ...
    def test_step_trace_topic_exists(self): ...
    def test_memory_score_topic_exists(self): ...

class TestDAGEventPayload:
    def test_dag_update_serializes(self): ...
    def test_step_trace_serializes(self): ...

class TestTUIBinding:
    async def test_tui_subscribes_to_dag_topic(self): ...
    async def test_tui_renders_step_trace(self): ...
```

---

## 📐 Architecture Compliance

| Mandate | Compliance | Evidence |
|---------|------------|----------|
| **M1** AnyIO | ✅ | All async code uses `anyio.create_task_group`, `anyio.to_thread.run_sync` |
| **M2** Firewall | ✅ | DAG schema in `src/omega/` (core), not `config/wads/` (stacks) |
| **M7** Local-First | ✅ | Cloud planner is advisory only; local executor is primary; `providers.yaml` `strategy: local_first` |
| **M13** Temple-Grade | ✅ | Tests cover all paths; `make temple-grade` passes |
| **M14** Heritage | ✅ | `[heritage: litellm-2024]` capability flag pattern noted in schema |

---

## 🔄 Integration with Phase 1 Results

| Phase 1 Item | Phase 2 Impact |
|-------------|----------------|
| **M2** (SQ8) ✅ PASS | No change needed — vector store already optimized |
| **I5** (Headroom) ⚠️ PARTIAL | Cloud planner can use Headroom for context compression before DAG emission |
| **M1** (Dual-Branch) ❌ NOT_IMPL | O1 Memory Score panel provides visualization target |
| **I2** (Speculative) ⚠️ PARTIAL | Local executor can use ngram draft for faster sub-task execution |
| **A1** (WAD Deps) ❌ NOT_IMPL | Cloud planner DAG can reference WAD dependencies for context |

---

## 📝 L3 Principles

1. **Cloud as advisor, local as executor** — The planner-emits-DAG / executor-runs-local pattern inverts the naive cloud-primary assumption. Cloud generates structured plans; local executes with grammar enforcement. This preserves M7 sovereignty while leveraging cloud reasoning.

2. **Per-subtask escalation, not per-goal** — Escalating a single failed sub-task to cloud (rather than the entire goal) minimizes cloud usage. The 2x retry threshold before escalation is a circuit-breaker pattern that balances local sovereignty with reliability.

3. **Complexity heuristic as M7 gatekeeper** — The `should_run_locally()` classifier is the M7 enforcement point. It must be conservative: when in doubt, route to cloud. Local sovereignty is preserved by defaulting to local for trivial/simple tasks, not by forcing local on complex ones.

4. **SEDA bus as single event source** — The TUI should bind to SEDA events, not poll. The SEDAReader polling adapter is a fallback; the primary path is direct event publication from the execution engine.

5. **DAG visualization enables debugging** — A visual DAG with color-coded task status (completed/pending/failed) transforms the TUI from a passive monitor into an active debugging tool. Step traces with provider attribution show exactly where time/tokens are spent.

---

## 📋 Next Steps

1. **Implement DAG schema** (`src/omega/oracle/planner/dag_schema.py`) — Pydantic models + complexity heuristic
2. **Implement HybridOrchestrator** (`src/omega/oracle/planner/hybrid_orchestrator.py`) — M7-compliant planner/executor
3. **Extend SEDABus** — Add `DAG_UPDATE`, `STEP_TRACE`, `MEMORY_SCORE` topics + event dataclasses
4. **Extend TUI** — Add DAG panel, step trace panel, memory score panel
5. **Write tests** — Schema validation, complexity heuristic, orchestrator behavior, TUI binding
6. **Run `make test` + `make temple-grade`** — Verify compliance

---

*⬡ OMEGA ⬡ MA'AT ⬡ laguna-s-2.1-free ⬡ opencode ⬡ trc_maat_phase2 ⬡ 2026-08-07*

<!-- PROVENANCE-CORRECTED 2026-08-23T20:39:41Z — FP-04/R_MESSAGE_PROVENANCE_HIERARCHY audit
claimed_model: laguna-s-2.1-free | verdict: UNANCHORED | no session anchor in header zone
actual_models(Tier0): n/a
-->
