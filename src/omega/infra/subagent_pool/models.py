# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Headless Subagent Pool — Core Data Models

AP Token: AP-HEADLESS-POOL-v1.0.0
⬡ OMEGA ⬡ RESEARCHER ⬡ nemotron-3-ultra-free ⬡ opencode ⬡ trc_headless_pool ⬡ MODELS
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4


class PoolType(str, Enum):
    """CLI agent pool types."""

    GROK = "grok"
    COPILOT = "copilot"
    CLINE = "cline"


class AccountHealth(str, Enum):
    """Health states for pool accounts."""

    HEALTHY = "healthy"
    RATE_LIMITED = "rate_limited"
    CREDENTIAL_ERROR = "credential_error"
    OFFLINE = "offline"


class TaskType(str, Enum):
    """Task types for routing."""

    DEEP_RESEARCH = "deep_research"
    CODE_IMPL = "code_impl"
    CODE_REVIEW = "code_review"
    LARGE_REFACTOR = "large_refactor"
    PARALLEL_VERIFY = "parallel_verify"
    WEB_SEARCH = "web_search"
    SYNTHESIS = "synthesis"


class RoutingHint(str, Enum):
    """Optional routing hints for task dispatch."""

    PREFER_GROK = "prefer_grok"
    PREFER_COPILOT = "prefer_copilot"
    PREFER_CLINE = "prefer_cline"
    REQUIRE_1M_CONTEXT = "require_1m_context"
    REQUIRE_512K_CONTEXT = "require_512k_context"
    PREFER_FREE_TIER = "prefer_free_tier"
    COGNITIVE_DIVERSITY = "cognitive_diversity"


@dataclass
class Account:
    """Represents a single CLI agent account in the pool."""

    id: str  # e.g., "grok-cli-3"
    pool: PoolType
    model: str  # Current model assignment
    context_window: int  # 128_000, 512_000, 1_000_000
    health: AccountHealth = AccountHealth.HEALTHY
    rate_limit_remaining: int = 1000
    rate_limit_reset: Optional[datetime] = None
    last_used: Optional[datetime] = None
    credentials_ref: str = ""  # Omega-Vault reference
    capabilities: set[str] = field(default_factory=set)  # "web_search", "reasoning", "code_gen"
    tmux_session: Optional[str] = None
    mcp_endpoint: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.pool, str):
            self.pool = PoolType(self.pool)
        if isinstance(self.health, str):
            self.health = AccountHealth(self.health)
        if self.last_used is None:
            self.last_used = datetime.now()

    def is_available(self, min_context: int = 0) -> bool:
        """Check if account is available for a task requiring min_context."""
        return (
            self.health == AccountHealth.HEALTHY
            and self.context_window >= min_context
            and self.rate_limit_remaining > 0
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "pool": self.pool.value,
            "model": self.model,
            "context_window": self.context_window,
            "health": self.health.value,
            "rate_limit_remaining": self.rate_limit_remaining,
            "rate_limit_reset": self.rate_limit_reset.isoformat()
            if self.rate_limit_reset
            else None,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "credentials_ref": self.credentials_ref,
            "capabilities": list(self.capabilities),
            "tmux_session": self.tmux_session,
            "mcp_endpoint": self.mcp_endpoint,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Account:
        """Deserialize from dictionary."""
        data = data.copy()
        data["pool"] = PoolType(data["pool"])
        data["health"] = AccountHealth(data["health"])
        if data.get("rate_limit_reset"):
            data["rate_limit_reset"] = datetime.fromisoformat(data["rate_limit_reset"])
        if data.get("last_used"):
            data["last_used"] = datetime.fromisoformat(data["last_used"])
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        data["capabilities"] = set(data.get("capabilities", []))
        return cls(**data)


@dataclass
class PoolTask:
    """A task to be dispatched to the pool."""

    id: str = field(default_factory=lambda: str(uuid4())[:8])
    type: TaskType = TaskType.DEEP_RESEARCH
    prompt: str = ""
    context_size_estimate: int = 0
    deadline: Optional[datetime] = None
    decomposable: bool = False
    routing_hint: Optional[RoutingHint] = None
    priority: int = 0  # 0=normal, 1=high, 2=critical
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = TaskType(self.type)
        if isinstance(self.routing_hint, str):
            self.routing_hint = RoutingHint(self.routing_hint)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type.value,
            "prompt": self.prompt,
            "context_size_estimate": self.context_size_estimate,
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "decomposable": self.decomposable,
            "routing_hint": self.routing_hint.value if self.routing_hint else None,
            "priority": self.priority,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PoolTask:
        data = data.copy()
        data["type"] = TaskType(data["type"])
        if data.get("routing_hint"):
            data["routing_hint"] = RoutingHint(data["routing_hint"])
        if data.get("deadline"):
            data["deadline"] = datetime.fromisoformat(data["deadline"])
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class SubTask:
    """A decomposed subtask for parallel execution."""

    id: str = field(default_factory=lambda: str(uuid4())[:8])
    parent_task_id: str = ""
    prompt: str = ""
    context_size_estimate: int = 0
    assigned_account_id: Optional[str] = None
    routing_hint: Optional[RoutingHint] = None
    priority: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "parent_task_id": self.parent_task_id,
            "prompt": self.prompt,
            "context_size_estimate": self.context_size_estimate,
            "assigned_account_id": self.assigned_account_id,
            "routing_hint": self.routing_hint.value if self.routing_hint else None,
            "priority": self.priority,
        }


@dataclass
class RoutingPlan:
    """Plan for routing a task to one or more accounts."""

    parallel: bool = False
    account: Optional[Account] = None
    subtasks: list[SubTask] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "parallel": self.parallel,
            "account": self.account.to_dict() if self.account else None,
            "subtasks": [s.to_dict() for s in self.subtasks],
        }


@dataclass
class AccountResult:
    """Result from a single account execution."""

    account_id: str
    pool: PoolType
    task_id: str
    success: bool
    output: str = ""
    error: Optional[str] = None
    tokens_used: int = 0
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "account_id": self.account_id,
            "pool": self.pool.value,
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
            "completed_at": self.completed_at.isoformat(),
        }


@dataclass
class AggregatedResult:
    """Aggregated result from multiple accounts with diversity weighting."""

    synthesis: str = ""
    confidence: float = 0.0
    minority_dissent: list[str] = field(default_factory=list)
    contributing_accounts: list[str] = field(default_factory=list)
    weights: dict[str, float] = field(default_factory=dict)
    individual_results: list[AccountResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "synthesis": self.synthesis,
            "confidence": self.confidence,
            "minority_dissent": self.minority_dissent,
            "contributing_accounts": self.contributing_accounts,
            "weights": self.weights,
            "individual_results": [r.to_dict() for r in self.individual_results],
        }


@dataclass
class PoolHealthReport:
    """Health report for the entire pool."""

    total_accounts: int = 0
    healthy: int = 0
    rate_limited: int = 0
    credential_errors: int = 0
    offline: int = 0
    by_pool: dict[str, dict[str, int]] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_accounts": self.total_accounts,
            "healthy": self.healthy,
            "rate_limited": self.rate_limited,
            "credential_errors": self.credential_errors,
            "offline": self.offline,
            "by_pool": self.by_pool,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class PoolStatus:
    """Real-time pool status."""

    available_accounts: int = 0
    queue_depth: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_latency_ms: float = 0.0
    throughput_per_min: float = 0.0
    by_pool: dict[str, dict[str, int]] = field(default_factory=dict)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "available_accounts": self.available_accounts,
            "queue_depth": self.queue_depth,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_latency_ms": self.avg_latency_ms,
            "throughput_per_min": self.throughput_per_min,
            "by_pool": self.by_pool,
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class RebalanceReport:
    """Report from a rebalance operation."""

    accounts_restored: list[str] = field(default_factory=list)
    accounts_marked_offline: list[str] = field(default_factory=list)
    tasks_redistributed: int = 0
    rebalanced_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "accounts_restored": self.accounts_restored,
            "accounts_marked_offline": self.accounts_marked_offline,
            "tasks_redistributed": self.tasks_redistributed,
            "rebalanced_at": self.rebalanced_at.isoformat(),
        }


# Default account configurations for the 24-account pool
DEFAULT_ACCOUNTS: list[dict[str, Any]] = [
    # Grok CLI - 8 accounts
    *[
        {
            "id": f"grok-cli-{i}",
            "pool": "grok",
            "model": "grok-3" if i <= 3 else "grok-2",
            "context_window": 1_000_000 if i <= 4 else 128_000,
            "health": "healthy",
            "capabilities": ["web_search", "reasoning", "synthesis"],
            "credentials_ref": f"vault:grok-cli-{i}",
        }
        for i in range(1, 9)
    ],
    # Copilot CLI - 8 accounts
    *[
        {
            "id": f"copilot-cli-{i}",
            "pool": "copilot",
            "model": "gpt-4o" if i <= 4 else "o1",
            "context_window": 128_000,
            "health": "healthy",
            "capabilities": ["code_gen", "code_review", "implementation"],
            "credentials_ref": f"vault:copilot-cli-{i}",
        }
        for i in range(1, 9)
    ],
    # Cline CLI - 8 accounts
    *[
        {
            "id": f"cline-cli-{i}",
            "pool": "cline",
            "model": "deepseek-v4-flash" if i <= 4 else "mimo-v2.5",
            "context_window": 1_000_000 if i <= 4 else 512_000,
            "health": "healthy",
            "capabilities": ["deep_research", "large_refactor", "code_gen"]
            if i <= 4
            else ["code_gen", "code_review"],
            "credentials_ref": f"vault:cline-cli-{i}",
        }
        for i in range(1, 9)
    ],
]


def create_default_accounts() -> list[Account]:
    """Create the default 24-account pool."""
    return [Account.from_dict(d) for d in DEFAULT_ACCOUNTS]
