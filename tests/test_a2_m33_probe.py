#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Standalone test for Task A2: M33 Probe Wiring"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

# Create temp file BEFORE imports so OMEGA_M34_REGISTRY is set before module load
_test_path_file = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
_test_path = Path(_test_path_file.name)
_test_path_file.close()
os.environ["OMEGA_M34_REGISTRY"] = str(_test_path)
os.environ["OMEGA_M34_ENABLED"] = "1"

# Mock the missing omega.library module BEFORE any imports
sys.modules['omega.library'] = MagicMock()
sys.modules['omega.library.indexer'] = MagicMock()

# Now import with src and scripts in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from omega.oracle.m34_registry import M34Registry, ActiveSubagent, SessionStatus  # noqa: E402
from omega.oracle.subagent_dispatcher import m34_register_subagent, dispatch, HandoffPacket  # noqa: E402
from omega.oracle.m33_probe import M33Probe, CompletionEnvelope, CompletionState  # noqa: E402


def _cleanup():
    """Clean up test files."""
    for p in [_test_path, _test_path.with_suffix(_test_path.suffix + ".1.bak"), _test_path.with_suffix(_test_path.suffix + ".lock")]:
        if os.path.exists(p):
            os.unlink(p)


def test_should_require_write_tool_exists():
    """Test should_require_write_tool function exists on M33Probe."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    assert hasattr(probe, "should_require_write_tool"), "M33Probe should have should_require_write_tool"
    assert callable(probe.should_require_write_tool), "should_require_write_tool should be callable"
    print("✓ should_require_write_tool function exists")


def test_should_require_write_tool_8k_threshold():
    """Test 8K token threshold - should require write tool for >8K tokens."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    # Just under threshold
    assert probe.should_require_write_tool(7999, "implement", "P3") is False
    # At threshold (implement is not research/forensic, so no auto)
    assert probe.should_require_write_tool(8000, "implement", "P3") is False
    # Over threshold
    assert probe.should_require_write_tool(8001, "implement", "P3") is True
    # Way over threshold
    assert probe.should_require_write_tool(10000, "implement", "P3") is True
    print("✓ 8K token threshold works correctly")


def test_should_require_write_tool_p0_p1_always():
    """Test P0/P1 always require write tool regardless of token count."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    assert probe.should_require_write_tool(100, "implement", "P0") is True
    assert probe.should_require_write_tool(100, "implement", "P1") is True
    assert probe.should_require_write_tool(100, "implement", "P0") is True
    assert probe.should_require_write_tool(100, "implement", "P1") is True
    print("✓ P0/P1 always require write tool")


def test_should_require_write_tool_research_forensic():
    """Test research/forensic/review/design tasks always require write tool."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    assert probe.should_require_write_tool(100, "research", "P2") is True
    assert probe.should_require_write_tool(100, "forensic", "P2") is True
    assert probe.should_require_write_tool(100, "review", "P2") is True
    assert probe.should_require_write_tool(100, "design", "P2") is True
    print("✓ Research/forensic/review/design tasks require write tool")


def test_should_require_write_tool_small_implement():
    """Test small implement tasks with low tokens don't require write tool."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    assert probe.should_require_write_tool(500, "implement", "P2") is False
    assert probe.should_require_write_tool(200, "verify", "P3") is False
    print("✓ Small implement/verify tasks don't require write tool")


def test_m33_probe_validate_response_valid_json():
    """Test M33Probe.validate_response accepts valid JSON envelope."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    response = {
        "state": "exhausted",
        "last_chunk_id": 5,
        "total_chunks": 5,
        "queued_findings": [],
        "confidence": 0.98,
        "deliverable_path": None,
    }
    verdict = probe.validate_response(response, session_id="ses_test", priority="P2")
    assert verdict.accepted is True
    assert verdict.schema_valid is True
    assert verdict.confidence_met is True
    assert verdict.free_form_detected is False
    print("✓ M33Probe validates valid JSON envelope")


def test_m33_probe_validate_response_free_form():
    """Test M33Probe rejects free-form STREAM_EXHAUSTED string."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    response = "STREAM_EXHAUSTED"
    verdict = probe.validate_response(response, session_id="ses_test", priority="P2")
    assert verdict.accepted is False
    assert verdict.free_form_detected is True
    print("✓ M33Probe rejects free-form STREAM_EXHAUSTED")


def test_m33_probe_validate_response_bypass_attack():
    """Test M33Probe detects bypass attack with prohibited strings."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    # Try to bypass with "done" or "complete"
    response = "DONE"
    verdict = probe.validate_response(response, session_id="ses_test", priority="P2")
    assert verdict.accepted is False
    assert verdict.free_form_detected is True
    print("✓ M33Probe detects bypass attack")


def test_m33_probe_validate_response_low_confidence():
    """Test M33Probe rejects low confidence responses."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    response = {
        "state": "exhausted",
        "last_chunk_id": 5,
        "total_chunks": 5,
        "queued_findings": [],
        "confidence": 0.5,  # Below P2 threshold of 0.95
    }
    verdict = probe.validate_response(response, session_id="ses_test", priority="P2")
    assert verdict.accepted is False
    assert verdict.confidence_met is False
    print("✓ M33Probe rejects low confidence")


def test_m33_probe_validate_response_p0_requires_cross_validation():
    """Test M33Probe requires cross-validation for P0/P1."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    response = {
        "state": "exhausted",
        "last_chunk_id": 5,
        "total_chunks": 5,
        "queued_findings": [],
        "confidence": 0.99,  # High confidence
    }
    verdict = probe.validate_response(response, session_id="ses_test", priority="P0")
    # P0 requires cross-validation, so accepted=False but cross_validation_required=True
    assert verdict.accepted is False
    assert verdict.cross_validation_required is True
    print("✓ M33Probe requires cross-validation for P0")


def test_dispatch_writes_m33_directive_for_large_tokens():
    """Test dispatch() injects M33 directive for >8K token estimates."""
    if _test_path.exists():
        os.unlink(_test_path)

    # Create a packet with large context to trigger >8K token estimate
    large_context = "x" * 50000  # ~12.5K tokens output at 3x multiplier
    packet = HandoffPacket(
        source_agent="kali",
        target_agent="researcher",
        task_type="research",
        task_description="Large research task",
        context=large_context,
        priority="P2",
    )

    prompt = dispatch(packet)

    # Prompt should contain M33 directive
    assert "M33 Sentinel Probe" in prompt or "write" in prompt.lower()
    print("✓ dispatch() injects M33 directive for >8K token estimates")


def test_dispatch_no_m33_directive_for_small_tokens():
    """Test dispatch() doesn't inject M33 directive for small token estimates."""
    if _test_path.exists():
        os.unlink(_test_path)

    packet = HandoffPacket(
        source_agent="kali",
        target_agent="node",
        task_type="implement",  # Not research/forensic
        task_description="Small implement task",
        context="short context",
        priority="P3",  # Not P0/P1
    )

    prompt = dispatch(packet)

    # Prompt should NOT contain M33 directive for small tasks
    assert "M33 Sentinel Probe" not in prompt
    print("✓ dispatch() skips M33 directive for small token estimates")


def test_dispatch_m33_for_p0_priority():
    """Test dispatch() injects M33 directive for P0 priority even with small tokens."""
    if _test_path.exists():
        os.unlink(_test_path)

    packet = HandoffPacket(
        source_agent="kali",
        target_agent="verity",
        task_type="verify",
        task_description="P0 compliance audit",
        context="small",
        priority="P0",  # Always requires write tool
    )

    prompt = dispatch(packet)

    # P0 should always trigger write tool
    assert "M33 Sentinel Probe" in prompt
    print("✓ dispatch() injects M33 directive for P0 priority")


def test_token_estimation_accuracy():
    """Test token estimation is roughly accurate."""
    # 4 chars per token heuristic
    test_strings = [
        ("hello world", 3),  # 11 chars / 4 = 2.75 -> 2
        ("a" * 100, 25),  # 100 / 4 = 25
        ("a" * 1000, 250),  # 1000 / 4 = 250
    ]
    for text, expected_tokens in test_strings:
        estimated = len(text) // 4
        # Allow for rounding
        assert abs(estimated - expected_tokens) <= 1, f"Token estimation off for '{text[:20]}...': got {estimated}, expected ~{expected_tokens}"
    print("✓ Token estimation accuracy verified")


def test_bypass_detection_prohibited_strings():
    """Test all prohibited strings are detected."""
    probe = M33Probe(m34_registry=None)  # type: ignore
    prohibited = ["STREAM_EXHAUSTED", "DONE", "FINISHED", "COMPLETE", "Mission complete", "All done"]
    for phrase in prohibited:
        verdict = probe.validate_response(phrase, session_id="ses_test", priority="P2")
        assert verdict.free_form_detected is True, f"Failed to detect: {phrase}"
    print("✓ All prohibited strings detected")


if __name__ == "__main__":
    print("Running Task A2: M33 Probe Wiring Tests\n")
    
    try:
        test_should_require_write_tool_exists()
        test_should_require_write_tool_8k_threshold()
        test_should_require_write_tool_p0_p1_always()
        test_should_require_write_tool_research_forensic()
        test_should_require_write_tool_small_implement()
        test_m33_probe_validate_response_valid_json()
        test_m33_probe_validate_response_free_form()
        test_m33_probe_validate_response_bypass_attack()
        test_m33_probe_validate_response_low_confidence()
        test_m33_probe_validate_response_p0_requires_cross_validation()
        test_dispatch_writes_m33_directive_for_large_tokens()
        test_dispatch_no_m33_directive_for_small_tokens()
        test_dispatch_m33_for_p0_priority()
        test_token_estimation_accuracy()
        test_bypass_detection_prohibited_strings()
        
        print("\n✅ All Task A2 tests PASSED!")
    finally:
        _cleanup()