#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Task A4: M36 Recursive Probe Wiring Tests."""

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

# Mock the missing omega.library module BEFORE any imports
sys.modules['omega.library'] = MagicMock()
sys.modules['omega.library.indexer'] = MagicMock()

# Now import with src in path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from omega.oracle.m33_probe import M33Probe, CompletionEnvelope, CompletionState, ProbeVerdict  # noqa: E402
from omega.oracle.m36_recursive_probe import (  # noqa: E402
    M36RecursiveProbe, CrossValidationResult,
    _dispatch_cross_validator_via_hivemind, _spawn_local_worker_for_hard_verify,
    CROSS_VALIDATOR_TIMEOUT_SECONDS,
)
from omega.oracle.m34_registry import M34Registry, ActiveSubagent, SessionStatus  # noqa: E402


def _cleanup():
    """Clean up test files."""
    for p in [_test_path, _test_path.with_suffix(_test_path.suffix + ".1.bak"), _test_path.with_suffix(_test_path.suffix + ".lock")]:
        if os.path.exists(p):
            os.unlink(p)


def test_m36_class_exists():
    """Test M36RecursiveProbe class exists and is importable."""
    assert M36RecursiveProbe is not None
    print("✓ M36RecursiveProbe class exists")


def test_dispatch_cross_validator_helper_exists():
    """Test the Hivemind dispatch helper exists."""
    assert callable(_dispatch_cross_validator_via_hivemind)
    assert CROSS_VALIDATOR_TIMEOUT_SECONDS == 120
    print("✓ Hivemind dispatch helper exists (120s timeout)")


def test_spawn_local_worker_helper_exists():
    """Test the local worker hard verification helper exists."""
    assert callable(_spawn_local_worker_for_hard_verify)
    print("✓ spawn_local_worker hard verification helper exists")


def test_dispatch_cross_validator_returns_structured_json():
    """Test Hivemind dispatch returns structured JSON response."""
    envelope = CompletionEnvelope(
        state=CompletionState.EXHAUSTED,
        last_chunk_id=5,
        total_chunks=5,
        queued_findings=[],
        confidence=0.99,
        deliverable_path="/tmp/test.md",
        deliverable_size_bytes=1024,
    )

    result = _dispatch_cross_validator_via_hivemind(
        envelope=envelope,
        deliverable_path="/tmp/test.md",
        priority="P0",
        cross_validator_agent="jem",
    )

    # Must be a structured JSON-compatible response
    assert isinstance(result, dict)
    assert "status" in result
    assert "semantic_coverage_verified" in result
    assert "queued_findings_addressed" in result
    assert "deliverable_meets_purpose" in result
    assert "cross_validator_agent" in result
    assert "cross_validator_timeout" in result
    assert "handoff_dispatched" in result
    assert "priority" in result
    assert "_m23_honesty" in result
    assert result["cross_validator_agent"] == "jem"
    assert result["priority"] == "P0"
    assert result["status"] == "stub_bypass"
    assert result["handoff_dispatched"] is False  # M23: stub does NOT dispatch
    print("✓ Hivemind dispatch returns structured JSON response (M23 honest stub)")


def test_spawn_local_worker_hard_verify_existing_file():
    """Test spawn_local_worker verifies an existing file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        test_file_path = f.name
        f.write("# Test\nContent here")  # 19 bytes

    try:
        test_file = Path(test_file_path)
        actual_size = test_file.stat().st_size
        result = _spawn_local_worker_for_hard_verify(str(test_file), claimed_size=actual_size)
        assert result["file_exists"] is True
        assert result["file_size_valid"] is True
        assert result["hash_computed"] is True
        print("✓ spawn_local_worker hard-verifies existing file")
    finally:
        os.unlink(test_file)


def test_spawn_local_worker_hard_verify_missing_file():
    """Test spawn_local_worker detects missing file."""
    result = _spawn_local_worker_for_hard_verify("/nonexistent/file.md", claimed_size=100)
    assert result["file_exists"] is False
    assert result["file_size_valid"] is False
    assert result["hash_computed"] is False
    print("✓ spawn_local_worker detects missing file")


def test_spawn_local_worker_hard_verify_size_mismatch():
    """Test spawn_local_worker detects size mismatch."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("x" * 100)  # 100 bytes
        test_file = Path(f.name)

    try:
        result = _spawn_local_worker_for_hard_verify(str(test_file), claimed_size=200)
        assert result["file_exists"] is True
        assert result["file_size_valid"] is False
        print("✓ spawn_local_worker detects size mismatch")
    finally:
        os.unlink(test_file)


def test_m36_cross_validate_p2_no_soft():
    """Test M36 hard validator only for P2 (no soft verifier)."""
    # Create a deliverable file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test deliverable\nContent here for testing.")
        deliverable = Path(f.name)

    try:
        # Create a fake M34 registry entry
        registry = M34Registry(registry_path=_test_path)
        entry = ActiveSubagent(
            session_id="ses_p2_test",
            parent_session_id=None,
            parent_task_id=None,
            subagent_type="EIS",
            agent="researcher",
            model="test",
            channel="opencode",
            entity="researcher",
            task_brief="P2 test task",
            expected_deliverable=str(deliverable),
        )
        registry.register(entry)

        # Create envelope
        envelope = CompletionEnvelope(
            state=CompletionState.EXHAUSTED,
            last_chunk_id=5,
            total_chunks=5,
            queued_findings=[],
            confidence=0.96,
            deliverable_path=str(deliverable),
            deliverable_size_bytes=deliverable.stat().st_size,
        )

        # Cross-validate at P2 (no soft verifier expected)
        m36 = M36RecursiveProbe(m34_registry=registry)
        result = m36.cross_validate(
            session_id="ses_p2_test",
            envelope=envelope,
            expected_deliverable=str(deliverable),
            priority="P2",
        )

        assert result.verified is True
        assert result.soft_checks_passed is None  # P2 doesn't run soft
        print("✓ M36 P2 hard-only validation works")
    finally:
        if deliverable.exists():
            os.unlink(deliverable)


def test_m36_cross_validate_p0_with_soft():
    """Test M36 cross-validation for P0 with soft verifier."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# P0 Test deliverable\nThis is a critical deliverable for P0 validation.")
        deliverable = Path(f.name)

    try:
        # Create a fake M34 registry entry with cross_validator_agent
        registry = M34Registry(registry_path=_test_path)
        entry = ActiveSubagent(
            session_id="ses_p0_test",
            parent_session_id=None,
            parent_task_id=None,
            subagent_type="EIS",
            agent="verity",
            model="test",
            channel="opencode",
            entity="verity",
            task_brief="P0 critical task",
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
            session_id="ses_p0_test",
            envelope=envelope,
            expected_deliverable=str(deliverable),
            priority="P0",
        )

        # P0 should run soft verifier
        assert result.soft_checks_passed is not None
        assert "cross_validator_agent" in str(result.cross_validator_agent) or result.cross_validator_agent == "jem"
        print("✓ M36 P0 with soft verifier (jem)")
    finally:
        if deliverable.exists():
            os.unlink(deliverable)


def test_m36_cross_validate_p0_uses_verity():
    """Test M36 cross-validator uses verity for P1."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# P1 Test deliverable")
        deliverable = Path(f.name)

    try:
        registry = M34Registry(registry_path=_test_path)
        entry = ActiveSubagent(
            session_id="ses_p1_test",
            parent_session_id=None,
            parent_task_id=None,
            subagent_type="EIS",
            agent="verity",
            model="test",
            channel="opencode",
            entity="verity",
            task_brief="P1 important task",
            expected_deliverable=str(deliverable),
            cross_validator_agent="verity",
        )
        registry.register(entry)

        envelope = CompletionEnvelope(
            state=CompletionState.EXHAUSTED,
            last_chunk_id=3,
            total_chunks=3,
            queued_findings=[],
            confidence=0.98,
            deliverable_path=str(deliverable),
            deliverable_size_bytes=deliverable.stat().st_size,
        )

        m36 = M36RecursiveProbe(m34_registry=registry)
        result = m36.cross_validate(
            session_id="ses_p1_test",
            envelope=envelope,
            expected_deliverable=str(deliverable),
            priority="P1",
        )

        assert result.cross_validator_agent == "verity"
        print("✓ M36 P1 cross-validator uses verity")
    finally:
        if deliverable.exists():
            os.unlink(deliverable)


def test_m33_to_m36_wiring_complete_with_validation():
    """Test M33 complete_with_validation wires M36 for P0/P1."""
    probe = M33Probe(m34_registry=None)  # type: ignore

    # P0 response with valid envelope
    response = {
        "state": "exhausted",
        "last_chunk_id": 5,
        "total_chunks": 5,
        "queued_findings": [],
        "confidence": 0.99,
    }

    result = probe.complete_with_validation(
        response=response,
        session_id="ses_test_p0",
        priority="P0",
    )

    # Should have M33 verdict
    assert "m33_verdict" in result
    assert "m36_result" in result
    assert "final_accepted" in result
    # P0 should trigger M36 cross-validation
    assert result["m33_verdict"].cross_validation_required is True
    print("✓ M33 complete_with_validation wires M36 for P0")


def test_m33_to_m36_wiring_p2_no_m36():
    """Test M33 complete_with_validation does NOT wire M36 for P2."""
    probe = M33Probe(m34_registry=None)  # type: ignore

    response = {
        "state": "exhausted",
        "last_chunk_id": 5,
        "total_chunks": 5,
        "queued_findings": [],
        "confidence": 0.96,
    }

    result = probe.complete_with_validation(
        response=response,
        session_id="ses_test_p2",
        priority="P2",
    )

    # P2 should NOT have M36 result
    assert result["m36_result"] is None
    assert result["final_accepted"] is True
    print("✓ M33 complete_with_validation skips M36 for P2")


def test_m33_to_m36_wiring_p0_envelope_parse_failure():
    """Test M33 handles envelope parse failure gracefully."""
    probe = M33Probe(m34_registry=None)  # type: ignore

    # Invalid response (not an envelope, not a prohibited string)
    response = "this is just some random text not matching anything"

    result = probe.complete_with_validation(
        response=response,
        session_id="ses_test_invalid",
        priority="P0",
    )

    # M33 should reject; M36 should not be called
    assert result["m33_verdict"].accepted is False
    # Either free_form_detected or schema_valid=False (depends on matching)
    assert result["m33_verdict"].schema_valid is False or result["m33_verdict"].free_form_detected is True
    print("✓ M33 handles envelope parse failure gracefully")


def test_m33_to_m36_wiring_p0_free_form_bypass():
    """Test M33 detects free-form bypass attack (STREAM_EXHAUSTED)."""
    probe = M33Probe(m34_registry=None)  # type: ignore

    response = "STREAM_EXHAUSTED"

    result = probe.complete_with_validation(
        response=response,
        session_id="ses_test_bypass",
        priority="P0",
    )

    # M33 should detect free-form bypass
    assert result["m33_verdict"].accepted is False
    assert result["m33_verdict"].free_form_detected is True
    print("✓ M33 detects free-form bypass attack")


if __name__ == "__main__":
    print("=" * 60)
    print("Task A4: M36 Recursive Probe Wiring Tests")
    print("=" * 60)
    print()

    try:
        test_m36_class_exists()
        test_dispatch_cross_validator_helper_exists()
        test_spawn_local_worker_helper_exists()
        test_dispatch_cross_validator_returns_structured_json()
        test_spawn_local_worker_hard_verify_existing_file()
        test_spawn_local_worker_hard_verify_missing_file()
        test_spawn_local_worker_hard_verify_size_mismatch()
        test_m36_cross_validate_p2_no_soft()
        test_m36_cross_validate_p0_with_soft()
        test_m36_cross_validate_p0_uses_verity()
        test_m33_to_m36_wiring_complete_with_validation()
        test_m33_to_m36_wiring_p2_no_m36()
        test_m33_to_m36_wiring_p0_envelope_parse_failure()
        test_m33_to_m36_wiring_p0_free_form_bypass()

        print()
        print("=" * 60)
        print("✅ All Task A4 tests PASSED")
        print("=" * 60)
    finally:
        _cleanup()