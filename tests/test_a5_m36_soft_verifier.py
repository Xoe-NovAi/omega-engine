#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Task A5: M36 Soft Verifier Tests."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Set up env vars and mocks BEFORE imports
_test_path_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
_test_path = Path(_test_path_file.name)
_test_path_file.close()
os.environ["OMEGA_M34_REGISTRY"] = str(_test_path)
os.environ["OMEGA_M34_ENABLED"] = "1"

# Now import with src in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from omega.oracle.m33_probe import CompletionEnvelope, CompletionState  # noqa: E402
from omega.oracle.m36_recursive_probe import (  # noqa: E402
    M36RecursiveProbe, CrossValidationResult,
    _dispatch_cross_validator_via_hivemind,
    _select_cross_validator_agent, _build_cross_validator_prompt,
    _spawn_local_worker_for_hard_verify,
    CROSS_VALIDATOR_TIMEOUT_SECONDS, DEFAULT_CROSS_VALIDATOR_AGENTS,
)
from omega.oracle.m34_registry import M34Registry, ActiveSubagent, SessionStatus  # noqa: E402


def _cleanup():
    """Clean up test files."""
    for p in [_test_path, _test_path.with_suffix(_test_path.suffix + ".1.bak"), _test_path.with_suffix(_test_path.suffix + ".lock")]:
        if os.path.exists(p):
            os.unlink(p)


# ── Test 1: P0 → jem selection ────────────────────────────────────────────

def test_p0_selects_jem():
    """Test P0 priority selects jem as cross-validator."""
    agent = _select_cross_validator_agent("P0")
    assert agent == "jem", f"Expected jem, got {agent}"
    print("✓ P0 priority selects jem cross-validator")


def test_p1_selects_verity():
    """Test P1 priority selects verity as cross-validator."""
    agent = _select_cross_validator_agent("P1")
    assert agent == "verity", f"Expected verity, got {agent}"
    print("✓ P1 priority selects verity cross-validator")


def test_explicit_agent_overrides_default():
    """Test explicit cross_validator_agent overrides default selection."""
    agent = _select_cross_validator_agent("P0", cross_validator_agent="custom_agent")
    assert agent == "custom_agent"
    print("✓ Explicit cross_validator_agent overrides default")


# ── Test 2: 120s timeout ──────────────────────────────────────────────────

def test_timeout_is_120_seconds():
    """Test CROSS_VALIDATOR_TIMEOUT_SECONDS is 120."""
    assert CROSS_VALIDATOR_TIMEOUT_SECONDS == 120
    print("✓ Cross-validator timeout is 120s")


def test_dispatch_includes_timeout():
    """Test Hivemind dispatch includes 120s timeout in structured response."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=5,
        total_chunks=5,
        queued_findings=[],
        confidence=0.99,
    )
    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/test.md",
        priority="P0",
    )
    assert "cross_validator_timeout_seconds" in result
    assert result["cross_validator_timeout_seconds"] == 120
    print("✓ Hivemind dispatch includes 120s timeout")


# ── Test 3: Structured JSON response ───────────────────────────────────────

def test_dispatch_returns_structured_json():
    """Test Hivemind dispatch returns full structured JSON response."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=5,
        total_chunks=5,
        queued_findings=["finding1", "finding2"],
        confidence=0.99,
    )
    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/test.md",
        priority="P0",
    )

    # Verify all required fields (M23 honest disclosure: stub bypass)
    required_fields = [
        "status",
        "semantic_coverage_verified",
        "queued_findings_addressed",
        "deliverable_meets_purpose",
        "cross_validator_agent",
        "cross_validator_timeout",
        "cross_validator_timeout_seconds",
        "handoff_dispatched",
        "handoff_packet_id",
        "priority",
        "deliverable_path",
        "verification_prompt",
        "_m23_honesty",
    ]
    for field in required_fields:
        assert field in result, f"Missing field: {field}"

    # All values should be JSON-serializable
    json_str = json.dumps(result, default=str)
    parsed = json.loads(json_str)
    assert parsed["cross_validator_agent"] == "jem"
    assert parsed["priority"] == "P0"
    assert parsed["status"] == "dispatched"
    assert parsed["handoff_dispatched"] is True
    assert parsed["handoff_packet_id"] is not None
    print("✓ Hivemind dispatch returns full structured JSON response (M23 honest stub)")


# ── Test 4: P0/P1 escalation works ────────────────────────────────────────

def test_p0_escalation_uses_jem():
    """Test P0 escalation dispatches to jem cross-validator."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=5,
        total_chunks=5,
        queued_findings=[],
        confidence=0.99,
    )
    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/p0_test.md",
        priority="P0",
    )
    assert result["cross_validator_agent"] == "jem"
    assert result["priority"] == "P0"
    assert result["handoff_dispatched"] is True  # real dispatch (stub removed)
    assert result["status"] == "dispatched"
    print("✓ P0 escalation uses jem (M23 honest stub)")


def test_p1_escalation_uses_verity():
    """Test P1 escalation dispatches to verity cross-validator."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=5,
        total_chunks=5,
        queued_findings=[],
        confidence=0.98,
    )
    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/p1_test.md",
        priority="P1",
    )
    assert result["cross_validator_agent"] == "verity"
    assert result["priority"] == "P1"
    assert result["handoff_dispatched"] is True  # real dispatch (stub removed)
    assert result["status"] == "dispatched"
    print("✓ P1 escalation uses verity (M23 honest stub)")


# ── Test 5: Verification prompt is well-formed ──────────────────────────

def test_verification_prompt_contains_envelope():
    """Test verification prompt contains the envelope JSON."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=3,
        total_chunks=3,
        queued_findings=["important_finding"],
        confidence=0.99,
        deliverable_path="/tmp/test.md",
    )
    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/test.md",
        priority="P0",
    )
    prompt = result["verification_prompt"]
    # Prompt should contain the envelope JSON
    assert "important_finding" in prompt
    assert "M36 Soft Verifier" in prompt
    assert "120 seconds" in prompt
    assert '"semantic_coverage_verified"' in prompt
    assert "jem" in prompt
    print("✓ Verification prompt is well-formed")


def test_verification_prompt_uses_correct_agent():
    """Test verification prompt identifies the correct cross-validator agent."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=1,
        total_chunks=1,
        queued_findings=[],
        confidence=0.95,
    )

    # P0 should mention jem
    p0_result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/p0.md",
        priority="P0",
    )
    assert "jem" in p0_result["verification_prompt"]

    # P1 should mention verity
    p1_result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/p1.md",
        priority="P1",
    )
    assert "verity" in p1_result["verification_prompt"]
    print("✓ Verification prompt uses correct agent per priority")


# ── Test 6: Handoff packet ID is generated ───────────────────────────────

def test_handoff_packet_id_generated():
    """Test that a handoff packet ID is generated for tracking."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=1,
        total_chunks=1,
        queued_findings=[],
        confidence=0.99,
    )
    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/test.md",
        priority="P0",
    )
    assert result["handoff_packet_id"] is not None
    assert result["handoff_packet_id"].startswith("ho_")
    assert len(result["handoff_packet_id"]) > 10
    print("✓ Handoff packet ID generated (ho_XXXX format)")


# ── Test 7: Cross-validator agent mapping is correct ─────────────────────

def test_default_agent_mapping():
    """Test DEFAULT_CROSS_VALIDATOR_AGENTS mapping is correct."""
    assert DEFAULT_CROSS_VALIDATOR_AGENTS["P0"] == "jem"
    assert DEFAULT_CROSS_VALIDATOR_AGENTS["P1"] == "verity"
    print("✓ Default agent mapping correct: P0→jem, P1→verity")


# ── Test 8: Full P0 escalation flow with M36 ─────────────────────────────

def test_full_p0_escalation_flow():
    """Test full P0 escalation flow with M36 cross-validation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# P0 Critical Deliverable\nThis is the critical P0 deliverable content.")
        deliverable = Path(f.name)

    try:
        # Setup M34 entry with cross_validator_agent
        registry = M34Registry(registry_path=_test_path)
        entry = ActiveSubagent(
            session_id="ses_p0_full_test",
            parent_session_id=None,
            parent_task_id=None,
            subagent_type="EIS",
            agent="verity",
            model="test",
            channel="opencode",
            entity="verity",
            task_brief="P0 full flow test",
            expected_deliverable=str(deliverable),
            cross_validator_agent="jem",
        )
        registry.register(entry)

        envelope = CompletionEnvelope(
            state=CompletionState.EXHAUSTED,
            last_chunk_id=5,
            total_chunks=5,
            queued_findings=[],
            confidence=0.99,
            deliverable_path=str(deliverable),
            deliverable_size_bytes=deliverable.stat().st_size,
        )

        m36 = M36RecursiveProbe(m34_registry=registry)
        result = m36.cross_validate(
            session_id="ses_p0_full_test",
            envelope=envelope,
            expected_deliverable=str(deliverable),
            priority="P0",
        )

        # P0 should run soft verifier
        assert result.soft_checks_passed is not None
        assert result.cross_validator_agent == "jem"

        # Hard checks should pass (file exists, size matches)
        assert result.hard_checks_passed["file_exists"] is True
        assert result.hard_checks_passed["file_size_valid"] is True
        print("✓ Full P0 escalation flow works end-to-end")
    finally:
        if deliverable.exists():
            os.unlink(deliverable)


# ── Test 9: Escalation with timeout (verification timeout) ───────────────

def test_p0_escalation_with_timeout():
    """Test P0 escalation includes timeout tracking in response."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=1,
        total_chunks=1,
        queued_findings=[],
        confidence=0.99,
    )
    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/timeout_test.md",
        priority="P0",
    )
    # Timeout tracking is present
    assert "cross_validator_timeout" in result
    assert "cross_validator_timeout_seconds" in result
    assert result["cross_validator_timeout_seconds"] == 120
    print("✓ P0 escalation includes timeout tracking")


# ── Test 10: M36 cross_validate with soft verifier failure ───────────────

def test_m36_p0_with_missing_deliverable():
    """Test M36 P0 cross-validate with missing deliverable still works (hard fail)."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=1,
        total_chunks=1,
        queued_findings=[],
        confidence=0.99,
        deliverable_path="/nonexistent/deliverable.md",
    )

    # Use a mock registry
    mock_registry = MagicMock()
    mock_registry.get.return_value = {"cross_validator_agent": "jem"}

    m36 = M36RecursiveProbe(m34_registry=mock_registry)
    result = m36.cross_validate(
        session_id="ses_missing",
        envelope=envelope,
        expected_deliverable="/nonexistent/deliverable.md",
        priority="P0",
    )

    # Hard checks should fail
    assert result.hard_checks_passed["file_exists"] is False
    assert result.verified is False
    # Soft verifier was still attempted
    assert result.soft_checks_passed is not None
    print("✓ M36 P0 handles missing deliverable (hard fail, soft attempted)")


if __name__ == "__main__":
    print("=" * 60)
    print("Task A5: M36 Soft Verifier Tests")
    print("=" * 60)
    print()

    try:
        test_p0_selects_jem()
        test_p1_selects_verity()
        test_explicit_agent_overrides_default()
        test_timeout_is_120_seconds()
        test_dispatch_includes_timeout()
        test_dispatch_returns_structured_json()
        test_p0_escalation_uses_jem()
        test_p1_escalation_uses_verity()
        test_verification_prompt_contains_envelope()
        test_verification_prompt_uses_correct_agent()
        test_handoff_packet_id_generated()
        test_default_agent_mapping()
        test_full_p0_escalation_flow()
        test_p0_escalation_with_timeout()
        test_m36_p0_with_missing_deliverable()

        print()
        print("=" * 60)
        print("✅ All Task A5 tests PASSED — P0/P1 escalation with timeout verified")
        print("=" * 60)
    finally:
        _cleanup()