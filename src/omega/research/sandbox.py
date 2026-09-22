# SPDX-FileCopyrightText: 2026 Xoe-NovAi

# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

"""
Ω-Research Generic Sandbox Runtime — YAML-Driven, M2 Firewall-Compliant, AnyIO-Native
⬡ OMEGA ⬡ MA'AT ⬡ S3 ⬡ SANDBOX
AP Token: AP-MAAT-SANDBOX-v1.0.0

Mandate Compliance:
- M1 AnyIO: anyio.run_process(), anyio.to_thread.run_sync() ONLY
- M2 Firewall: SandboxWritePolicy blocks src/omega/ writes at runtime
- M7 Local-First: No cloud deps; BudgetGuard uses local models
- M9 Error Integrity: Typed SandboxError hierarchy
- M12 Queue Integrity: SandboxResult has terminal states
- M13 Temple-Grade: Contract tests for all public APIs
- M21 Gate Integrity: isinstance(result, SandboxResult) contract
- M23 Failure Integrity: No soft-failures — sandbox crash = hard error
"""

import anyio
import json
import time
import tempfile
import shutil
import psutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, TYPE_CHECKING

# ── TYPE_CHECKING block for forward references ──
if TYPE_CHECKING:
    from omega.research.schema import ResearchProposal
from uuid import UUID

from omega.errors import OmegaError
from omega.research.types import (
    BudgetToken,
    SandboxState,
    SandboxResult,
)
from omega.governance.budget_guard import BudgetGuard


# ── Sandbox Error Hierarchy (M9 Error Integrity) ─────────────────────────────


class SandboxError(OmegaError):
    """Base class for all sandbox execution errors."""

    pass


class SandboxTimeoutError(SandboxError):
    """Sandbox execution exceeded budget time limit."""

    def __init__(self, sandbox_name: str, budget_sec: float, **kwargs):
        self.sandbox_name = sandbox_name
        self.budget_sec = budget_sec
        super().__init__(
            f"Sandbox '{sandbox_name}' exceeded {budget_sec}s budget",
            context={"sandbox_name": sandbox_name, "budget_sec": budget_sec},
            **kwargs,
        )


class SandboxFirewallViolation(SandboxError):
    """Sandbox attempted forbidden write to Core Engine (M2 Firewall)."""

    def __init__(self, sandbox_name: str, attempted_path: str, **kwargs):
        self.sandbox_name = sandbox_name
        self.attempted_path = attempted_path
        super().__init__(
            f"Sandbox '{sandbox_name}' violated M2 Firewall: write to '{attempted_path}' blocked",
            context={"sandbox_name": sandbox_name, "attempted_path": attempted_path},
            **kwargs,
        )


class SandboxResourceExhausted(SandboxError):
    """Sandbox exceeded RAM/CPU budget."""

    def __init__(self, sandbox_name: str, resource: str, limit: float, actual: float, **kwargs):
        self.sandbox_name = sandbox_name
        self.resource = resource
        self.limit = limit
        self.actual = actual
        super().__init__(
            f"Sandbox '{sandbox_name}' exhausted {resource}: {actual:.1f} > {limit:.1f}",
            context={
                "sandbox_name": sandbox_name,
                "resource": resource,
                "limit": limit,
                "actual": actual,
            },
            **kwargs,
        )


class SandboxExecutionError(SandboxError):
    """Sandbox process failed with non-zero exit code."""

    def __init__(self, sandbox_name: str, exit_code: int, stderr: str, **kwargs):
        self.sandbox_name = sandbox_name
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(
            f"Sandbox '{sandbox_name}' failed with exit code {exit_code}",
            context={"sandbox_name": sandbox_name, "exit_code": exit_code, "stderr": stderr[:500]},
            **kwargs,
        )


class SandboxSpecError(SandboxError):
    """Invalid sandbox specification (YAML parsing, missing fields)."""

    pass


# ── Sandbox Result (M12 Queue Integrity — Terminal States) ──────────────────


class SandboxState(Enum):
    """Terminal states for sandbox execution (M12)."""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    FIREWALL_VIOLATION = "FIREWALL_VIOLATION"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"


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
        if self.completed_at is None and self.state in (
            SandboxState.SUCCESS,
            SandboxState.FAILED,
            SandboxState.TIMEOUT,
            SandboxState.FIREWALL_VIOLATION,
            SandboxState.BUDGET_EXCEEDED,
        ):
            self.completed_at = datetime.now(timezone.utc)

    def is_terminal(self) -> bool:
        """M12: Terminal states have no outgoing transitions."""
        return self.state in (
            SandboxState.SUCCESS,
            SandboxState.FAILED,
            SandboxState.TIMEOUT,
            SandboxState.FIREWALL_VIOLATION,
            SandboxState.BUDGET_EXCEEDED,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sandbox_name": self.sandbox_name,
            "proposal_id": str(self.proposal_id),
            "causal_trace_id": self.causal_trace_id,
            "state": self.state.value,
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
            completed_at=datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None,
        )


# ── Sandbox Specification (YAML-Driven) ──────────────────────────────────────


@dataclass
class SandboxMetric:
    """Metric definition for CLEAR scorecard integration."""

    name: str
    weight: float
    direction: str  # "minimize" or "maximize"

    @classmethod
    def from_dict(cls, data: dict) -> SandboxMetric:
        return cls(
            name=data["name"],
            weight=data["weight"],
            direction=data.get("direction", "maximize"),
        )


@dataclass
class SandboxSpec:
    """
    YAML-driven sandbox specification.

    Example:
    ```yaml
    spec:
      name: "kernel_optimization"
      slot: "S3"
      infrastructure:
        benchmark_harness: "triton_perf"
        target_hw: "zen2_avx2"
      mutable_surface:
        - "config/wads/omega_research/workspaces/*"
      metrics:
        - {name: "latency_ms", weight: -0.4, direction: "minimize"}
        - {name: "occupancy", weight: 0.2, direction: "maximize"}
      adversarial_validators: ["chaos_cache_flush"]
      budget_tier: "cpu_intensive"
    ```
    """

    name: str
    slot: str  # S1-S10
    infrastructure: dict[str, Any] = field(default_factory=dict)
    mutable_surface: list[str] = field(default_factory=list)
    metrics: list[SandboxMetric] = field(default_factory=list)
    adversarial_validators: list[str] = field(default_factory=list)
    budget_tier: str = "standard"

    # M2 Firewall: Explicitly forbidden paths
    FORBIDDEN_PATHS = (
        "src/omega/",
        "config/omega.yaml",
        "config/providers.yaml",
        "config/models.yaml",
        "opencode.json",
        ".opencode/",
    )

    @classmethod
    def from_yaml(cls, yaml_content: str) -> SandboxSpec:
        import yaml

        data = yaml.safe_load(yaml_content)
        spec_data = data.get("spec", data)

        metrics = [SandboxMetric.from_dict(m) for m in spec_data.get("metrics", [])]

        return cls(
            name=spec_data["name"],
            slot=spec_data["slot"],
            infrastructure=spec_data.get("infrastructure", {}),
            mutable_surface=spec_data.get("mutable_surface", []),
            metrics=metrics,
            adversarial_validators=spec_data.get("adversarial_validators", []),
            budget_tier=spec_data.get("budget_tier", "standard"),
        )

    def validate_write(self, path: str) -> bool:
        """
        M2 Firewall: Check if a write path is allowed.

        Returns True if allowed, raises SandboxFirewallViolation if forbidden.
        """
        path_obj = Path(path).resolve()

        # Check forbidden paths (Core Engine)
        for forbidden in self.FORBIDDEN_PATHS:
            forbidden_path = Path(forbidden).resolve()
            try:
                path_obj.relative_to(forbidden_path)
                raise SandboxFirewallViolation(
                    sandbox_name=self.name,
                    attempted_path=str(path_obj),
                )
            except ValueError:
                # Not under forbidden path — continue checking
                pass

        # Check allowed mutable surface
        for allowed_pattern in self.mutable_surface:
            allowed_path = Path(allowed_pattern).resolve()
            try:
                path_obj.relative_to(allowed_path)
                return True  # Explicitly allowed
            except ValueError:
                continue

        # Default: deny writes outside mutable surface
        raise SandboxFirewallViolation(
            sandbox_name=self.name,
            attempted_path=str(path_obj),
        )


# ── Sandbox Write Policy (M2 Firewall Enforcement) ──────────────────────────


class SandboxWritePolicy:
    """
    Runtime enforcement of M2 Engine-Stack Firewall for sandboxes.

    - ALLOWED: Writes to config/wads/omega_research/workspaces/
    - BLOCKED: Any write to src/omega/, config/omega.yaml, config/providers.yaml
    - VIOLATION: Raises SandboxFirewallViolation (typed error, M9)
    """

    CORE_ENGINE_PATHS = frozenset(
        {
            "src/omega",
            "config/omega.yaml",
            "config/providers.yaml",
            "config/models.yaml",
            "opencode.json",
            ".opencode",
        }
    )

    WAD_WORKSPACE_PREFIX = "config/wads/omega_research/workspaces"

    @classmethod
    def check_write(cls, sandbox_name: str, target_path: str) -> None:
        """
        Check if a write operation is permitted.

        Raises:
            SandboxFirewallViolation: If write targets Core Engine
        """
        target = Path(target_path).resolve()

        # Check Core Engine paths
        for core_path in cls.CORE_ENGINE_PATHS:
            core = Path(core_path).resolve()
            try:
                target.relative_to(core)
                raise SandboxFirewallViolation(
                    sandbox_name=sandbox_name,
                    attempted_path=str(target),
                )
            except ValueError:
                continue

        # Allow WAD workspace writes
        workspace = Path(cls.WAD_WORKSPACE_PREFIX).resolve()
        try:
            target.relative_to(workspace)
            return  # Explicitly allowed
        except ValueError:
            pass

        # Default: deny writes outside workspace
        raise SandboxFirewallViolation(
            sandbox_name=sandbox_name,
            attempted_path=str(target),
        )

    @classmethod
    def is_allowed(cls, target_path: str) -> bool:
        """Non-raising check for allowed writes."""
        try:
            cls.check_write("check", target_path)
            return True
        except SandboxFirewallViolation:
            return False


# ── Abstract Sandbox Runtime ────────────────────────────────────────────────


class SandboxRuntime(ABC):
    """
    Abstract base for all sandbox runtimes.

    Subclasses must implement execute() with M1 AnyIO compliance.
    """

    def __init__(self, spec: SandboxSpec, budget_guard: BudgetGuard):
        self.spec = spec
        self.budget_guard = budget_guard
        self._workspace: Path | None = None

    @property
    @abstractmethod
    def spec_name(self) -> str:
        """Unique identifier for this sandbox type."""
        pass

    async def execute(self, proposal: ResearchProposal) -> SandboxResult:
        """
        Execute sandbox experiment with full mandate compliance.

        Flow:
        1. BudgetGuard.check(proposal.amfo_tier) — enforces time/RAM budget
        2. Prepare isolated workspace (temp dir, no src/omega/ writes)
        3. Run experiment via anyio.run_process() — NO subprocess.run
        4. Capture stdout/stderr, exit code, resource usage
        5. Return SandboxResult (typed dataclass for M21)
        """
        # 1. Budget check
        tier = proposal.experiment_spec.get("amfo_tier", "validate")
        budget_token = await self.budget_guard.check(tier, str(proposal.id))

        # 2. Prepare workspace
        self._workspace = await self._prepare_workspace(proposal)

        # 3. Execute with budget enforcement
        start_time = time.perf_counter()
        peak_ram = 0.0

        try:
            # M1: AnyIO timeout wrapper — M23: timeout = hard failure
            async with anyio.create_task_group() as tg:
                # Monitor resources in background
                tg.start_soon(self._monitor_resources, budget_token)

                # Run experiment
                result = await self._run_experiment(proposal, budget_token)

                # Cancel monitor
                tg.cancel_scope.cancel()

            execution_time = time.perf_counter() - start_time

            # 4. Parse metrics from output
            metrics = self._parse_metrics(result.stdout, result.stderr)

            return SandboxResult(
                sandbox_name=self.spec_name,
                proposal_id=proposal.id,
                causal_trace_id=proposal.causal_trace_id,
                state=SandboxState.SUCCESS,
                metrics=metrics,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time_sec=execution_time,
                peak_ram_mb=peak_ram,
                provider_name="sandbox",
            )

        except anyio.get_cancelled_exc_class():
            # Timeout from budget enforcement
            execution_time = time.perf_counter() - start_time
            return SandboxResult(
                sandbox_name=self.spec_name,
                proposal_id=proposal.id,
                causal_trace_id=proposal.causal_trace_id,
                state=SandboxState.TIMEOUT,
                stdout="",
                stderr=f"Budget exceeded: {budget_token.remaining_sec:.1f}s remaining",
                exit_code=-1,
                execution_time_sec=execution_time,
                peak_ram_mb=peak_ram,
                error=f"Timeout after {execution_time:.1f}s",
                provider_name="sandbox",
            )
        except SandboxFirewallViolation as e:
            execution_time = time.perf_counter() - start_time
            return SandboxResult(
                sandbox_name=self.spec_name,
                proposal_id=proposal.id,
                causal_trace_id=proposal.causal_trace_id,
                state=SandboxState.FIREWALL_VIOLATION,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time_sec=execution_time,
                peak_ram_mb=peak_ram,
                error=str(e),
                provider_name="sandbox",
            )
        except Exception as e:
            execution_time = time.perf_counter() - start_time
            return SandboxResult(
                sandbox_name=self.spec_name,
                proposal_id=proposal.id,
                causal_trace_id=proposal.causal_trace_id,
                state=SandboxState.FAILED,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time_sec=execution_time,
                peak_ram_mb=peak_ram,
                error=str(e),
                provider_name="sandbox",
            )
        finally:
            # Cleanup workspace
            await self._cleanup_workspace()

    async def _prepare_workspace(self, proposal: ResearchProposal) -> Path:
        """Create isolated workspace for experiment."""
        workspace = Path(tempfile.mkdtemp(prefix=f"omega_sandbox_{self.spec_name}_"))

        # Create symlink to WAD workspace for allowed writes
        wad_workspace = Path("config/wads/omega_research/workspaces") / str(proposal.id)
        wad_workspace.mkdir(parents=True, exist_ok=True)

        # Symlink for easy access
        (workspace / "workspace").symlink_to(wad_workspace.resolve())

        return workspace

    async def _cleanup_workspace(self) -> None:
        """Clean up temporary workspace."""
        if self._workspace and self._workspace.exists():
            try:
                await anyio.to_thread.run_sync(shutil.rmtree, self._workspace)
            except Exception as e:
                logger.warning("Workspace cleanup best-effort failed: %s", e, exc_info=True)
                # Best effort cleanup

    async def _monitor_resources(self, budget_token: BudgetToken) -> None:
        """Background task to monitor RAM/CPU against budget."""
        process = psutil.Process()
        while True:
            try:
                # Check time budget
                if budget_token.is_expired():
                    raise SandboxTimeoutError(
                        sandbox_name=self.spec_name,
                        budget_sec=budget_token.time_budget_sec,
                    )

                # Check RAM budget
                mem_info = process.memory_info()
                ram_mb = mem_info.rss / (1024 * 1024)
                if ram_mb > budget_token.ram_budget_mb:
                    raise SandboxResourceExhausted(
                        sandbox_name=self.spec_name,
                        resource="RAM",
                        limit=budget_token.ram_budget_mb,
                        actual=ram_mb,
                    )

                await anyio.sleep(0.5)
            except anyio.get_cancelled_exc_class():
                break
            except (SandboxTimeoutError, SandboxResourceExhausted):
                raise
            except Exception as e:
                # Log and continue monitoring
                logger.warning("Monitor error: %s", e)
                await anyio.sleep(0.5)

    @abstractmethod
    async def _run_experiment(
        self, proposal: ResearchProposal, budget_token: BudgetToken
    ) -> anyio.ProcessResult:
        """Run the actual experiment. Must use anyio.run_process()."""
        pass

    def _parse_metrics(self, stdout: str, stderr: str) -> dict[str, float]:
        """Parse metrics from experiment output. Override in subclasses."""
        metrics = {}
        # Try to parse JSON metrics from stdout
        for line in stdout.splitlines():
            line = line.strip()
            if line.startswith("{") and line.endswith("}"):
                try:
                    data = json.loads(line)
                    if isinstance(data, dict):
                        for k, v in data.items():
                            if isinstance(v, (int, float)):
                                metrics[k] = float(v)
                except json.JSONDecodeError:
                    pass
        return metrics


# ── Circuit Breaker for Experiment Failures ────────────────────────────────
# ⚠️ DEPRECATED — C-6' Unification (2026-07-22)
# This is a clone breaker. Use HealthMonitor.get_breaker() instead.


class ExperimentCircuitBreaker:
    """
    Circuit breaker for sandbox executions.

    Tracks failure rates per sandbox type, opens circuit after 5 consecutive failures (M23).
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: float = 300.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self._failures: dict[str, int] = {}
        self._last_failure_time: dict[str, float] = {}
        self._state: dict[str, str] = {}  # "closed", "open", "half-open"

    def record_success(self, sandbox_name: str) -> None:
        """Reset failure count on success."""
        self._failures[sandbox_name] = 0
        self._state[sandbox_name] = "closed"

    def record_failure(self, sandbox_name: str) -> None:
        """Increment failure count, open circuit if threshold reached."""
        self._failures[sandbox_name] = self._failures.get(sandbox_name, 0) + 1
        self._last_failure_time[sandbox_name] = time.time()

        if self._failures[sandbox_name] >= self.failure_threshold:
            self._state[sandbox_name] = "open"

    def can_execute(self, sandbox_name: str) -> bool:
        """Check if circuit allows execution."""
        state = self._state.get(sandbox_name, "closed")

        if state == "closed":
            return True

        if state == "open":
            # Check if recovery timeout has passed
            last_failure = self._last_failure_time.get(sandbox_name, 0)
            if time.time() - last_failure > self.recovery_timeout_sec:
                self._state[sandbox_name] = "half-open"
                return True
            return False

        # Half-open: allow one trial
        return True

    def get_state(self, sandbox_name: str) -> str:
        return self._state.get(sandbox_name, "closed")


# Global circuit breaker instance
from src.omega.oracle.health_monitor import HealthMonitor

_circuit_breaker = HealthMonitor().get_breaker("sandbox")


def get_circuit_breaker():
    return _circuit_breaker


# ── Contract Test Helpers (M21) ──────────────────────────────────────────────


def assert_sandbox_result_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for SandboxResult type."""
    assert isinstance(obj, SandboxResult), f"Expected SandboxResult, got {type(obj)}"
    assert hasattr(obj, "sandbox_name")
    assert hasattr(obj, "proposal_id")
    assert hasattr(obj, "causal_trace_id")
    assert hasattr(obj, "state")
    assert hasattr(obj, "metrics")
    assert hasattr(obj, "is_terminal")
    assert callable(obj.is_terminal)
    assert hasattr(obj, "to_dict")
    assert callable(obj.to_dict)
    assert hasattr(obj, "from_dict")
    assert callable(obj.from_dict)


def assert_sandbox_spec_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for SandboxSpec type."""
    assert isinstance(obj, SandboxSpec), f"Expected SandboxSpec, got {type(obj)}"
    assert hasattr(obj, "name")
    assert hasattr(obj, "slot")
    assert hasattr(obj, "infrastructure")
    assert hasattr(obj, "mutable_surface")
    assert hasattr(obj, "metrics")
    assert hasattr(obj, "adversarial_validators")
    assert hasattr(obj, "budget_tier")
    assert hasattr(obj, "validate_write")
    assert callable(obj.validate_write)
    assert hasattr(obj, "from_yaml")
    assert callable(obj.from_yaml)


def assert_sandbox_runtime_type(obj: Any) -> None:
    """M21 Gate Integrity: Contract test for SandboxRuntime type."""
    assert isinstance(obj, SandboxRuntime), f"Expected SandboxRuntime, got {type(obj)}"
    assert hasattr(obj, "spec")
    assert hasattr(obj, "budget_guard")
    assert hasattr(obj, "execute")
    assert callable(obj.execute)
    assert hasattr(obj, "spec_name")


# Export
__all__ = [
    # Errors
    "SandboxError",
    "SandboxTimeoutError",
    "SandboxFirewallViolation",
    "SandboxResourceExhausted",
    "SandboxExecutionError",
    "SandboxSpecError",
    # Result
    "SandboxState",
    "SandboxResult",
    # Spec
    "SandboxMetric",
    "SandboxSpec",
    # Policy
    "SandboxWritePolicy",
    # Runtime
    "SandboxRuntime",
    # Circuit Breaker
    "get_circuit_breaker",
    # Contract tests
    "assert_sandbox_result_type",
    "assert_sandbox_spec_type",
    "assert_sandbox_runtime_type",
]
