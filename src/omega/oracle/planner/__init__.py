# AP: AP-MAAT-PHASE2-DESIGN-v1.0.0
# 🔱 Planner Package — Cloud Planner / Local Executor Pattern
# ICS: [NODE: N3 | ARCHETYPE: HERMES | CONTEXT: PLANNER-PACKAGE]
"""
Planner package: Cloud Planner / Local Executor pattern (A4).

M7-compliant: Cloud is advisor/planner only; local is executor.
"""

from .dag_schema import (
    ActionType,
    ComplexityTier,
    SubTaskSchema,
    ExecutionPlanSchema,
    SubTask,
    ExecutionPlan,
    TaskResult,
    should_run_locally,
    classify_complexity,
    MAX_DEPENDENCY_DEPTH,
    MAX_LOCAL_TOKENS,
    MAX_LOCAL_COMPLEXITY,
    LOCAL_SAFE_ACTIONS,
    CLOUD_ONLY_ACTIONS,
)
from .hybrid_orchestrator import (
    HybridOrchestrator,
    PLANNER_SYSTEM_PROMPT,
    LOCAL_EXECUTOR_SYSTEM_PROMPT,
    CLOUD_FALLBACK_SYSTEM_PROMPT,
)

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
    "HybridOrchestrator",
    "PLANNER_SYSTEM_PROMPT",
    "LOCAL_EXECUTOR_SYSTEM_PROMPT",
    "CLOUD_FALLBACK_SYSTEM_PROMPT",
]
