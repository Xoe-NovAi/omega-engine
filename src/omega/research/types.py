"""
Ω-Research Shared Types — Breaks circular imports between sandbox and budget_guard
⬡ OMEGA ⬡ MA'AT ⬡ N2/N3 ⬡ TYPES
AP Token: AP-MAAT-TYPES-v1.0.0
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID


# ── BudgetToken (shared between sandbox.py and budget_guard.py) ────────────────

@dataclass
class BudgetToken:
    """
    Token representing allocated budget for an experiment.
    
    M12 Queue Integrity: BudgetToken has terminal states (expired/active).
    M21 Gate Integrity: isinstance(token, BudgetToken) contract test.
    M23 Failure Integrity: Hard failure on expiration.
    """
    experiment_id: str
    tier: str
    time_budget_sec: int
    ram_budget_mb: int
    model: str
    expires_at: datetime
    allocated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def remaining_sec(self) -> float:
        """Seconds remaining until budget expires."""
        return (self.expires_at - datetime.now(timezone.utc)).total_seconds()
    
    def is_expired(self) -> bool:
        """Check if budget token has expired."""
        return self.remaining_sec <= 0
    
    def __post_init__(self):
        if isinstance(self.expires_at, str):
            self.expires_at = datetime.fromisoformat(self.expires_at)
        if isinstance(self.allocated_at, str):
            self.allocated_at = datetime.fromisoformat(self.allocated_at)


# ── ExperimentProposal (shared with schema.py) ────────────────────────────────

@dataclass
class ExperimentProposal:
    """Minimal proposal reference for sandbox execution."""
    id: UUID
    causal_trace_id: str
    domain: str
    hypothesis: str
    experiment_spec: dict[str, Any]
    estimated_clear: Any  # CLEARScore - avoid circular import
    budget_usd: float
    assigned_agents: list[str]
    status: str = "DRAFT"


# ── SandboxResult (shared) ───────────────────────────────────────────────────

class SandboxState(str):
    """Terminal states for sandbox execution (M12 Queue Integrity)."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    FIREWALL_VIOLATION = "FIREWALL_VIOLATION"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    
    def is_terminal(self) -> bool:
        return self in (
            SandboxState.SUCCESS, SandboxState.FAILED,
            SandboxState.TIMEOUT, SandboxState.FIREWALL_VIOLATION,
            SandboxState.BUDGET_EXCEEDED
        )


@dataclass
class SandboxResult:
    """
    Result of sandbox execution with full provenance (M21, M22).
    
    Contract: isinstance(result, SandboxResult) must pass (M21).
    """
    sandbox_name: str
    proposal_id: UUID
    causal_trace_id: str
    state: SandboxState
    metrics: dict[str, float] = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time_sec: float = 0.0
    peak_ram_mb: float = 0.0
    error: str | None = None
    provider_name: str = "sandbox"  # M22: Actual execution backend
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    
    def __post_init__(self):
        if isinstance(self.state, str):
            self.state = SandboxState(self.state)
        if isinstance(self.proposal_id, str):
            self.proposal_id = UUID(self.proposal_id)
        if self.completed_at is None and self.state.is_terminal():
            self.completed_at = datetime.now(timezone.utc)
    
    def is_terminal(self) -> bool:
        """M12: Terminal states have no outgoing transitions."""
        return self.state.is_terminal()
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "sandbox_name": self.sandbox_name,
            "proposal_id": str(self.proposal_id),
            "causal_trace_id": self.causal_trace_id,
            "state": self.state.value if hasattr(self.state, 'value') else str(self.state),
            "metrics": self.metrics,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time_sec": self.execution_time_sec,
            "peak_ram_mb": self.peak_ram_mb,
            "error": self.error,
            "provider_name": self.provider_name,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SandboxResult:
        return cls(
            sandbox_name=data["sandbox_name"],
            proposal_id=UUID(data["proposal_id"]),
            causal_trace_id=data["causal_trace_id"],
            state=SandboxState(data["state"]),
            metrics=data.get("metrics", {}),
            stdout=data.get("stdout", ""),
            stderr=data.get("stderr", ""),
            exit_code=data.get("exit_code", 0),
            execution_time_sec=data.get("execution_time_sec", 0.0),
            peak_ram_mb=data.get("peak_ram_mb", 0.0),
            error=data.get("error"),
            provider_name=data.get("provider_name", "sandbox"),
            started_at=datetime.fromisoformat(data["started_at"]),
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )


# Export
__all__ = [
    "BudgetToken",
    "ExperimentProposal", 
    "SandboxState",
    "SandboxResult",
]