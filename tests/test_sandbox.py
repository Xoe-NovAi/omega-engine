# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""
Contract Tests for Ω-Research Sandbox Runtime (M21 Gate Integrity)
⬡ OMEGA ⬡ MA'AT ⬡ P3/P10 ⬡ TEST-SANDBOX
AP Token: AP-MAAT-SANDBOX-TEST-v1.0.0

Tests verify:
- isinstance(result, SandboxResult) for all public APIs
- SandboxSpec.from_yaml() returns SandboxSpec with correct fields
- SandboxRuntime.execute() returns SandboxResult
- BudgetGuard.check() returns BudgetToken
- Error hierarchy is typed and traceable
"""

import anyio
import pytest
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

from src.omega.research.sandbox import (
    SandboxSpec,
    SandboxMetric,
    SandboxResult,
    SandboxState,
    SandboxRuntime,
    SandboxWritePolicy,
    ExperimentCircuitBreaker,
    get_circuit_breaker,
    SandboxError,
    SandboxTimeoutError,
    SandboxFirewallViolation,
    SandboxResourceExhausted,
    SandboxExecutionError,
    SandboxSpecError,
    assert_sandbox_result_type,
    assert_sandbox_spec_type,
    assert_sandbox_runtime_type,
)
from src.omega.research.schema import ResearchProposal, CLEARScore
from src.omega.governance.budget_guard import BudgetGuard, BudgetToken, TIER_BUDGETS
from src.omega.governance.budget_guard import (
    BudgetError,
    BudgetExceededError,
    BudgetUnavailableError,
    BudgetTokenExpiredError,
    assert_budget_guard_type,
    assert_budget_token_type,
)
# ── SandboxSpec Tests ──────────────────────────────────────────────────────────

def test_sandbox_spec_from_yaml():
    """M21: SandboxSpec.from_yaml() returns SandboxSpec with correct fields."""
    yaml_content = """
spec:
  name: "test_sandbox"
  node: "N3"
  infrastructure:
    benchmark_harness: "test"
    target_hw: "zen2"
  mutable_surface:
    - "config/wads/omega_research/workspaces/*"
  metrics:
    - {name: "latency_ms", weight: -0.4, direction: "minimize"}
    - {name: "occupancy", weight: 0.2, direction: "maximize"}
  adversarial_validators: ["chaos_cache_flush"]
  budget_tier: "cpu_intensive"
"""
    spec = SandboxSpec.from_yaml(yaml_content)

    assert_sandbox_spec_type(spec)
    assert spec.name == "test_sandbox"
    assert spec.node == "N3"
    assert spec.infrastructure["benchmark_harness"] == "test"
    assert len(spec.metrics) == 2
    assert spec.metrics[0].name == "latency_ms"
    assert spec.metrics[0].weight == -0.4
    assert spec.metrics[0].direction == "minimize"
    assert spec.adversarial_validators == ["chaos_cache_flush"]
    assert spec.budget_tier == "cpu_intensive"

def test_sandbox_spec_validate_write_allowed():
    """M2: SandboxSpec.validate_write() allows WAD workspace writes."""
    yaml_content = """
spec:
  name: "test"
  node: "N3"
  mutable_surface:
    - "config/wads/omega_research/workspaces"
"""
    spec = SandboxSpec.from_yaml(yaml_content)

    # Should not raise for allowed path
    assert spec.validate_write("config/wads/omega_research/workspaces/exp123/output.json") is True

def test_sandbox_spec_validate_write_forbidden_core():
    """M2: SandboxSpec.validate_write() blocks Core Engine writes."""
    yaml_content = """
spec:
  name: "test"
  node: "N3"
  mutable_surface:
    - "config/wads/omega_research/workspaces/*"
"""
    spec = SandboxSpec.from_yaml(yaml_content)

    # Should raise for Core Engine paths
    with pytest.raises(SandboxFirewallViolation):
        spec.validate_write("src/omega/oracle/oracle.py")

    with pytest.raises(SandboxFirewallViolation):
        spec.validate_write("config/omega.yaml")

    with pytest.raises(SandboxFirewallViolation):
        spec.validate_write("config/providers.yaml")

def test_sandbox_spec_validate_write_forbidden_outside_workspace():
    """M2: SandboxSpec.validate_write() blocks writes outside workspace."""
    yaml_content = """
spec:
  name: "test"
  node: "N3"
  mutable_surface:
    - "config/wads/omega_research/workspaces/*"
"""
    spec = SandboxSpec.from_yaml(yaml_content)

    # Should raise for paths outside workspace
    with pytest.raises(SandboxFirewallViolation):
        spec.validate_write("/tmp/some_random_file.txt")

    with pytest.raises(SandboxFirewallViolation):
        spec.validate_write("data/some_other_path.txt")

def test_sandbox_write_policy_check_write():
    """M2: SandboxWritePolicy.check_write() enforces firewall."""
    # Allowed: WAD workspace
    SandboxWritePolicy.check_write("test", "config/wads/omega_research/workspaces/exp123/file.txt")

    # Blocked: Core Engine
    with pytest.raises(SandboxFirewallViolation):
        SandboxWritePolicy.check_write("test", "src/omega/oracle/oracle.py")

    with pytest.raises(SandboxFirewallViolation):
        SandboxWritePolicy.check_write("test", "config/omega.yaml")

def test_sandbox_write_policy_is_allowed():
    """SandboxWritePolicy.is_allowed() returns bool without raising."""
    assert SandboxWritePolicy.is_allowed("config/wads/omega_research/workspaces/file.txt") is True
    assert SandboxWritePolicy.is_allowed("src/omega/oracle/oracle.py") is False

# ── SandboxResult Tests ────────────────────────────────────────────────────────

def test_sandbox_result_creation():
    """M21: SandboxResult creation with all required fields."""
    proposal_id = uuid4()
    result = SandboxResult(
        sandbox_name="test_sandbox",
        proposal_id=proposal_id,
        causal_trace_id="trace_123",
        state=SandboxState.SUCCESS,
        metrics={"val_bpb": 2.5, "accuracy": 0.95},
        stdout="output",
        stderr="",
        exit_code=0,
        execution_time_sec=1.5,
        peak_ram_mb=512.0,
        provider_name="sandbox",
    )

    assert_sandbox_result_type(result)
    assert result.sandbox_name == "test_sandbox"
    assert result.proposal_id == proposal_id
    assert result.causal_trace_id == "trace_123"
    assert result.state == SandboxState.SUCCESS
    assert result.metrics["val_bpb"] == 2.5

def test_sandbox_result_terminal_states():
    """M12: SandboxResult.is_terminal() correctly identifies terminal states."""
    proposal_id = uuid4()

    # Terminal states
    for state in [SandboxState.SUCCESS, SandboxState.FAILED,
                  SandboxState.TIMEOUT, SandboxState.FIREWALL_VIOLATION,
                  SandboxState.BUDGET_EXCEEDED]:
        result = SandboxResult(
            sandbox_name="test", proposal_id=proposal_id, causal_trace_id="trace",
            state=state, metrics={}
        )
        assert result.is_terminal() is True, f"{state} should be terminal"

    # Non-terminal states
    for state in [SandboxState.PENDING, SandboxState.RUNNING]:
        result = SandboxResult(
            sandbox_name="test", proposal_id=proposal_id, causal_trace_id="trace",
            state=state, metrics={}
        )
        assert result.is_terminal() is False, f"{state} should not be terminal"

def test_sandbox_result_to_dict_from_dict():
    """SandboxResult.to_dict() and from_dict() round-trip."""
    proposal_id = uuid4()
    original = SandboxResult(
        sandbox_name="test_sandbox",
        proposal_id=proposal_id,
        causal_trace_id="trace_123",
        state=SandboxState.SUCCESS,
        metrics={"val_bpb": 2.5, "accuracy": 0.95},
        stdout="output",
        stderr="",
        exit_code=0,
        execution_time_sec=1.5,
        peak_ram_mb=512.0,
        provider_name="sandbox",
    )

    data = original.to_dict()
    restored = SandboxResult.from_dict(data)

    assert restored.sandbox_name == original.sandbox_name
    assert restored.proposal_id == original.proposal_id
    assert restored.causal_trace_id == original.causal_trace_id
    assert restored.state == original.state
    assert restored.metrics == original.metrics
    assert restored.execution_time_sec == original.execution_time_sec

# ── SandboxError Hierarchy Tests ──────────────────────────────────────────────

def test_sandbox_error_hierarchy():
    """M9: All sandbox errors inherit from SandboxError (typed, traceable)."""
    errors = [
        SandboxTimeoutError("test", 60.0),
        SandboxFirewallViolation("test", "/forbidden/path"),
        SandboxResourceExhausted("test", "RAM", 1024, 2048),
        SandboxExecutionError("test", 1, "stderr output"),
        SandboxSpecError("Invalid spec"),
    ]

    for err in errors:
        assert isinstance(err, SandboxError)
        assert isinstance(err, Exception)
        assert hasattr(err, "trace_id")  # From OmegaError

# ── BudgetGuard Tests ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_budget_guard_check_returns_budget_token():
    """M21: BudgetGuard.check() returns BudgetToken."""
    guard = BudgetGuard(enable_redis=False)

    token = await guard.check("scout", "exp_123")

    assert_budget_token_type(token)
    assert token.experiment_id == "exp_123"
    assert token.tier == "scout"
    assert token.time_budget_sec == 60
    assert token.ram_budget_mb == 2048
    assert token.model == "qwen3-0.6b-q6_k"
    assert not token.is_expired()

@pytest.mark.asyncio
async def test_budget_guard_tier_budgets():
    """BudgetGuard has correct tier budgets for AMFO."""
    guard = BudgetGuard(enable_redis=False)

    for tier_name, budget in TIER_BUDGETS.items():
        token = await guard.check(tier_name, f"exp_{tier_name}")
        assert token.time_budget_sec == budget["time_sec"]
        assert token.ram_budget_mb == budget["ram_mb"]
        assert token.model == budget["model"]

@pytest.mark.asyncio
async def test_budget_guard_concurrency_limit():
    """BudgetGuard enforces max concurrent per tier."""
    guard = BudgetGuard(enable_redis=False, max_concurrent_per_tier=2)

    # First two should succeed
    token1 = await guard.check("scout", "exp_1")
    token2 = await guard.check("scout", "exp_2")

    # Third should fail
    with pytest.raises(BudgetUnavailableError):
        await guard.check("scout", "exp_3")

    # Release one
    await guard.release("scout", "exp_1")

    # Now should succeed
    token3 = await guard.check("scout", "exp_3")
    assert token3.experiment_id == "exp_3"

@pytest.mark.asyncio
async def test_budget_guard_enforce_context_manager():
    """BudgetGuard.enforce() context manager enforces time budget."""
    guard = BudgetGuard(enable_redis=False)
    token = await guard.check("scout", "exp_test")

    async with guard.enforce(token) as t:
        assert t.experiment_id == "exp_test"
        # Small delay
        await anyio.sleep(0.01)

    # Should have released automatically
    status = await guard.get_tier_status("scout")
    assert status["current_usage"] == 0

@pytest.mark.asyncio
async def test_budget_guard_enforce_timeout():
    """BudgetGuard.enforce() raises on timeout (M23: hard failure)."""
    guard = BudgetGuard(enable_redis=False)
    # Create token with very short expiry
    from src.omega.research.types import BudgetToken
    from datetime import datetime, timedelta, timezone

    token = BudgetToken(
        experiment_id="exp_timeout",
        tier="scout",
        time_budget_sec=0,  # Immediate expiry
        ram_budget_mb=2048,
        model="qwen3-0.6b-q6_k",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
    )

    with pytest.raises(BudgetTokenExpiredError):
        async with guard.enforce(token):
            pass

@pytest.mark.asyncio
async def test_budget_guard_get_tier_status():
    """BudgetGuard.get_tier_status() returns correct info."""
    guard = BudgetGuard(enable_redis=False)

    status = await guard.get_tier_status("scout")

    assert status["tier"] == "scout"
    assert status["current_usage"] == 0
    assert status["max_concurrent"] == 4
    assert status["time_budget_sec"] == 60
    assert status["ram_budget_mb"] == 2048
    assert status["model"] == "qwen3-0.6b-q6_k"
    assert status["backend"] == "local"

@pytest.mark.asyncio
async def test_budget_guard_get_all_tiers_status():
    """BudgetGuard.get_all_tiers_status() returns all tiers."""
    guard = BudgetGuard(enable_redis=False)

    all_status = await guard.get_all_tiers_status()

    assert len(all_status) == len(TIER_BUDGETS)
    for tier_name in TIER_BUDGETS:
        assert tier_name in all_status
        assert all_status[tier_name]["tier"] == tier_name

# ── BudgetToken Tests ──────────────────────────────────────────────────────────

def test_budget_token_is_expired():
    """BudgetToken.is_expired() works correctly."""
    from src.omega.research.types import BudgetToken
    from datetime import datetime, timedelta

    # Not expired
    token = BudgetToken(
        experiment_id="exp_1",
        tier="scout",
        time_budget_sec=60,
        ram_budget_mb=2048,
        model="qwen3-0.6b-q6_k",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )
    assert token.is_expired() is False
    assert token.remaining_sec > 0

    # Expired
    token_expired = BudgetToken(
        experiment_id="exp_2",
        tier="scout",
        time_budget_sec=60,
        ram_budget_mb=2048,
        model="qwen3-0.6b-q6_k",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=10),
    )
    assert token_expired.is_expired() is True
    assert token_expired.remaining_sec < 0

# ── Circuit Breaker Tests ──────────────────────────────────────────────────────

def test_circuit_breaker_records_success():
    """ExperimentCircuitBreaker records success and resets failures."""
    cb = ExperimentCircuitBreaker(failure_threshold=3)

    cb.record_failure("test_sandbox")
    cb.record_failure("test_sandbox")
    assert cb.get_state("test_sandbox") == "closed"

    cb.record_success("test_sandbox")
    assert cb.get_state("test_sandbox") == "closed"
    assert cb._failures["test_sandbox"] == 0

def test_circuit_breaker_opens_after_threshold():
    """ExperimentCircuitBreaker opens circuit after threshold failures."""
    cb = ExperimentCircuitBreaker(failure_threshold=3)

    cb.record_failure("test_sandbox")
    cb.record_failure("test_sandbox")
    assert cb.can_execute("test_sandbox") is True

    cb.record_failure("test_sandbox")  # 3rd failure
    assert cb.get_state("test_sandbox") == "open"
    assert cb.can_execute("test_sandbox") is False

def test_circuit_breaker_half_open_after_timeout():
    """ExperimentCircuitBreaker goes half-open after recovery timeout."""
    cb = ExperimentCircuitBreaker(failure_threshold=2, recovery_timeout_sec=0.01)

    cb.record_failure("test_sandbox")
    cb.record_failure("test_sandbox")
    assert cb.can_execute("test_sandbox") is False

    # Wait for recovery timeout
    import time
    time.sleep(0.02)

    assert cb.can_execute("test_sandbox") is True
    assert cb.get_state("test_sandbox") == "half-open"

def test_get_circuit_breaker_singleton():
    """get_circuit_breaker() returns singleton instance."""
    cb1 = get_circuit_breaker()
    cb2 = get_circuit_breaker()
    assert cb1 is cb2

# ── Contract Test Helper Tests ────────────────────────────────────────────────

def test_assert_sandbox_result_type():
    """M21: assert_sandbox_result_type validates SandboxResult contract."""
    proposal_id = uuid4()
    result = SandboxResult(
        sandbox_name="test", proposal_id=proposal_id, causal_trace_id="trace",
        state=SandboxState.SUCCESS, metrics={}
    )

    # Should not raise
    assert_sandbox_result_type(result)

    # Should raise for wrong type
    with pytest.raises(AssertionError):
        assert_sandbox_result_type("not a result")

def test_assert_sandbox_spec_type():
    """M21: assert_sandbox_spec_type validates SandboxSpec contract."""
    yaml_content = """
spec:
  name: "test"
  node: "N3"
"""
    spec = SandboxSpec.from_yaml(yaml_content)

    # Should not raise
    assert_sandbox_spec_type(spec)

    # Should raise for wrong type
    with pytest.raises(AssertionError):
        assert_sandbox_spec_type("not a spec")

def test_assert_sandbox_runtime_type():
    """M21: assert_sandbox_runtime_type validates SandboxRuntime contract."""
    # Create a mock runtime
    class MockRuntime(SandboxRuntime):
        spec_name = "mock"
        async def _run_experiment(self, proposal, budget_token):
            pass

    spec = SandboxSpec(name="test", node="N3")
    guard = BudgetGuard(enable_redis=False)
    runtime = MockRuntime(spec, guard)

    # Should not raise
    assert_sandbox_runtime_type(runtime)

    # Should raise for wrong type
    with pytest.raises(AssertionError):
        assert_sandbox_runtime_type("not a runtime")

def test_assert_budget_guard_type():
    """M21: assert_budget_guard_type validates BudgetGuard contract."""
    guard = BudgetGuard(enable_redis=False)

    # Should not raise
    assert_budget_guard_type(guard)

    # Should raise for wrong type
    with pytest.raises(AssertionError):
        assert_budget_guard_type("not a guard")

def test_assert_budget_token_type():
    """M21: assert_budget_token_type validates BudgetToken contract."""
    from omega.research.types import BudgetToken
    from datetime import datetime, timedelta

    token = BudgetToken(
        experiment_id="exp_1",
        tier="scout",
        time_budget_sec=60,
        ram_budget_mb=2048,
        model="qwen3-0.6b-q6_k",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=30),
    )

    # Should not raise
    assert_budget_token_type(token)

    # Should raise for wrong type
    with pytest.raises(AssertionError):
        assert_budget_token_type("not a token")

# ── MLTrainingSandbox Tests ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ml_training_sandbox_creation():
    """MLTrainingSandbox can be instantiated."""
    from src.omega.research.sandboxes.ml_training import MLTrainingSandbox
    from omega.research.sandbox import SandboxRuntime

    spec = SandboxSpec(name="ml_training", node="N6")
    guard = BudgetGuard(enable_redis=False)

    sandbox = MLTrainingSandbox(spec, guard)

    assert sandbox.spec_name == "ml_training"
    assert isinstance(sandbox, SandboxRuntime)

# Import at bottom to avoid circular imports
import os
import sys