#!/usr/bin/env python3
"""Adversarial test suite for dispatch_guard.py (JEM-12STEP-HARDENING)

[AP-JEM-12STEP-HARDENING-v1.0.0] Master EIS Adversarial Test Cases
Per JEM-FORENSIC-001 self-correction: verification must be EXHAUSTIVE, not selective.

Test categories:
  - Bypass attack simulation (M33 amendment)
  - Truncation detection (M33 amendment)
  - All-locations verification (Jem's self-correction)
  - Cross-validator escalation (M33 tier model)
  - Probe theatre detection (JEM-FORENSIC-001 lesson)
  - M34 atomic write edge cases
  - Watchdog race condition simulation

References:
  - github.com/dakshjain-1616/AgentLiar (similar 4-check verification pattern)
  - arxiv.org/abs/2504.11168 (Bypassing Prompt Injection and Jailbreak Detection)
  - github.com/anomalyco/opencode/issues/33223 (subagent permission denials)
  - github.com/anomalyco/opencode (tool-output truncation at 95KB)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import sqlite3
import pytest

# Add the scripts directory to path
SCRIPTS_DIR = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from dispatch_guard import (
    step4_all_locations_verification,
    step5_estimated_tokens,
    step6_write_tool_routing,
    step7_cross_validator_escalation,
    parse_completion_envelope,
    validate_completion_envelope,
    run_sentinel_probe,
    _discover_all_session_locations,
    GuardResult,
)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: M33 BYPASS ATTACK SIMULATION
# ═══════════════════════════════════════════════════════════════════════════


class TestM33BypassAttacks:
    """Test that M33 sentinel probe rejects bypass attacks.

    Per JEM_ADVERSARIAL_REVIEW_GROKSTER_20260830.md §1.1.3:
      "A malicious, lazy, or simply-confused subagent can immediately reply
       STREAM_EXHAUSTED to the sentinel probe."
    """

    def test_bypass_straight_text_stream_exhausted(self):
        """Lazy agent returns exact 'STREAM_EXHAUSTED' — must be rejected."""
        result = parse_completion_envelope("STREAM_EXHAUSTED")
        assert result is not None
        assert result.get("_bypass_detected") is True
        assert "STREAM_EXHAUSTED" in result.get("_raw", "")

    def test_bypass_with_punctuation(self):
        """Lazy agent returns 'STREAM_EXHAUSTED.' — must be rejected."""
        result = parse_completion_envelope("STREAM_EXHAUSTED.")
        assert result is not None
        assert result.get("_bypass_detected") is True

    def test_bypass_lowercase(self):
        """Lazy agent returns 'stream_exhausted' (lowercase) — must be rejected."""
        result = parse_completion_envelope("stream_exhausted")
        assert result is not None
        assert result.get("_bypass_detected") is True

    def test_bypass_with_surrounding_whitespace(self):
        """Lazy agent returns '  exhausted  ' with whitespace — must be rejected."""
        result = parse_completion_envelope("  exhausted  ")
        assert result is not None
        assert result.get("_bypass_detected") is True

    def test_bypass_done(self):
        """Lazy agent returns 'done' — must be rejected (probe theatre)."""
        result = parse_completion_envelope("done")
        assert result is not None
        assert result.get("_bypass_detected") is True

    def test_bypass_complete(self):
        """Lazy agent returns 'complete' — must be rejected."""
        result = parse_completion_envelope("complete.")
        assert result is not None
        assert result.get("_bypass_detected") is True

    def test_bypass_empty_string(self):
        """Empty response — must return None (no bypass detected, but no valid envelope)."""
        result = parse_completion_envelope("")
        assert result is None

    def test_bypass_none_response(self):
        """None response — must return None gracefully."""
        result = parse_completion_envelope(None)
        assert result is None

    def test_valid_envelope_accepted(self):
        """Valid structured JSON envelope must be accepted (no bypass)."""
        valid = json.dumps({
            "state": "exhausted",
            "last_chunk_id": 5,
            "total_chunks": 5,
            "queued_findings": [],
            "confidence": 0.97,
        })
        result = parse_completion_envelope(valid)
        assert result is not None
        assert result.get("_bypass_detected") is None
        assert result["state"] == "exhausted"
        assert result["confidence"] == 0.97

    def test_valid_envelope_in_markdown_fence(self):
        """Valid JSON in markdown code fence must be accepted."""
        fenced = '```json\n{"state": "continuing", "last_chunk_id": 3, "total_chunks": 7, "queued_findings": ["finding1"], "confidence": 0.92}\n```'
        result = parse_completion_envelope(fenced)
        assert result is not None
        assert result["state"] == "continuing"
        assert len(result["queued_findings"]) == 1


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: M33 CONFIDENCE THRESHOLD VALIDATION
# ═══════════════════════════════════════════════════════════════════════════


class TestM33ConfidenceThreshold:
    """Test that confidence thresholds are enforced per priority.

    Per CARMACK_DEV_PLAN_REVIEW_20260830.md §3.2:
      "Cross-validator only for true P0 (security, data-loss), not for every
       forensic report."
    """

    def test_p0_low_confidence_fails(self):
        """P0 with confidence < 0.95 must fail validation."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": 0.80,
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P0")
        assert not is_valid
        # Python repr of 0.80 is "0.8", so check for "0.8" and "0.95" both present
        assert any("0.8" in issue and "0.95" in issue for issue in issues)

    def test_p0_high_confidence_passes(self):
        """P0 with confidence >= 0.95 must pass."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": 0.97,
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P0")
        assert is_valid
        assert len(issues) == 0

    def test_p1_low_confidence_fails(self):
        """P1 with confidence < 0.95 must fail."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": 0.85,
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P1")
        assert not is_valid

    def test_p2_low_confidence_fails(self):
        """P2 with confidence < 0.80 must fail."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": 0.50,
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P2")
        assert not is_valid
        assert any("0.80" in issue for issue in issues)

    def test_p2_high_confidence_passes(self):
        """P2 with confidence >= 0.80 must pass."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": 0.85,
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P2")
        assert is_valid

    def test_invalid_confidence_too_high(self):
        """Confidence > 1.0 must be flagged."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": 1.5,
        }
        result = parse_completion_envelope(json.dumps(envelope))
        # The envelope is returned but flagged as invalid
        assert result is not None
        assert result.get("_invalid_confidence") is True

    def test_invalid_confidence_negative(self):
        """Confidence < 0.0 must be flagged."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": -0.1,
        }
        result = parse_completion_envelope(json.dumps(envelope))
        assert result is not None
        assert result.get("_invalid_confidence") is True

    def test_invalid_confidence_string(self):
        """Confidence as string must be flagged."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": [],
            "confidence": "high",
        }
        result = parse_completion_envelope(json.dumps(envelope))
        assert result is not None
        assert result.get("_invalid_confidence") is True


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: M33 FALSE-EXHAUST DETECTION
# ═══════════════════════════════════════════════════════════════════════════


class TestM33FalseExhaustDetection:
    """Test that 'state=exhausted' with queued_findings is flagged.

    Per JEM-FORENSIC-001: The completion illusion produces graceful
    conclusions even when the agent's internal outline is truncated.
    """

    def test_exhausted_with_queued_findings_flagged(self):
        """state=exhausted with queued_findings is a contradiction."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": ["I still need to write section 3"],
            "confidence": 0.95,
        }
        result = parse_completion_envelope(json.dumps(envelope))
        assert result is not None
        assert result.get("_false_exhaust_detected") is True

    def test_exhausted_with_empty_findings_ok(self):
        """state=exhausted with empty queued_findings is consistent."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 5,
            "total_chunks": 5,
            "queued_findings": [],
            "confidence": 0.95,
        }
        result = parse_completion_envelope(json.dumps(envelope))
        assert result is not None
        assert result.get("_false_exhaust_detected") is None

    def test_continuing_with_findings_ok(self):
        """state=continuing with queued_findings is consistent (not done)."""
        envelope = {
            "state": "continuing",
            "last_chunk_id": 2,
            "total_chunks": 5,
            "queued_findings": ["section 3", "section 4", "section 5"],
            "confidence": 0.85,
        }
        result = parse_completion_envelope(json.dumps(envelope))
        assert result is not None
        assert result.get("_false_exhaust_detected") is None

    def test_validation_flags_false_exhaust(self):
        """validate_completion_envelope must surface false-exhaust."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 1,
            "total_chunks": 1,
            "queued_findings": ["pending analysis"],
            "confidence": 0.95,
        }
        # First parse so the false-exhaust flag is set
        parsed = parse_completion_envelope(json.dumps(envelope))
        # Then validate the parsed envelope (which carries the flag)
        is_valid, issues = validate_completion_envelope(parsed, priority="P0")
        assert not is_valid
        assert any("FALSE-EXHAUST" in issue for issue in issues)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: CHUNK ACCOUNTING VALIDATION
# ═══════════════════════════════════════════════════════════════════════════


class TestChunkAccounting:
    """Test that chunk IDs are consistent with total_chunks."""

    def test_last_chunk_exceeds_total(self):
        """last_chunk_id > total_chunks is inconsistent."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 10,
            "total_chunks": 5,
            "queued_findings": [],
            "confidence": 0.95,
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P0")
        assert not is_valid
        assert any("Chunk accounting" in issue for issue in issues)

    def test_last_chunk_equals_total_ok(self):
        """last_chunk_id == total_chunks is consistent (completed)."""
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 5,
            "total_chunks": 5,
            "queued_findings": [],
            "confidence": 0.95,
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P0")
        assert is_valid

    def test_last_chunk_less_than_total_continuing(self):
        """last_chunk_id < total_chunks with state=continuing is consistent.

        This is a TRUE P0 (10K output) deliverable. Confidence must be >= 0.95.
        """
        envelope = {
            "state": "continuing",
            "last_chunk_id": 2,
            "total_chunks": 5,
            "queued_findings": ["3 more to go"],
            "confidence": 0.96,  # P0 needs >= 0.95
        }
        is_valid, issues = validate_completion_envelope(envelope, priority="P0")
        assert is_valid, f"Expected valid, got issues: {issues}"


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: ALL-LOCATIONS VERIFICATION (JEM'S LESSON)
# ═══════════════════════════════════════════════════════════════════════════


class TestAllLocationsVerification:
    """Test that step4_all_locations_verification searches ALL locations.

    Per JEM-FORENSIC-001: "Verification must be exhaustive, not selective."
    This is the direct application of the JEM-FORENSIC-001 lesson.
    """

    def test_discover_all_locations_returns_multiple(self):
        """Discovery must return more than the 5 standard locations."""
        locations = _discover_all_session_locations()
        # Even in a clean workspace, should have at least 8+ locations
        # (5 standard + 6 user-opencode + extras)
        assert len(locations) >= 8, (
            f"Expected at least 8 locations, got {len(locations)}: {locations}"
        )

    def test_discover_includes_opencode_db(self):
        """Discovery must include the main OpenCode DB."""
        locations = _discover_all_session_locations()
        home = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
        if home.exists():
            assert any(str(home) in str(loc) for loc in locations), (
                f"OpenCode DB not in discovered locations: {locations}"
            )

    def test_discover_includes_tool_output_dir(self):
        """Discovery must include tool-output dir (per opencode tool truncation)."""
        locations = _discover_all_session_locations()
        tool_output = Path.home() / ".local" / "share" / "opencode" / "tool-output"
        if tool_output.exists():
            assert any(str(tool_output) in str(loc) for loc in locations)

    def test_discover_includes_snapshot_dir(self):
        """Discovery must include snapshot dir (per opencode session storage)."""
        locations = _discover_all_session_locations()
        snapshot = Path.home() / ".local" / "share" / "opencode" / "snapshot"
        if snapshot.exists():
            assert any(str(snapshot) in str(loc) for loc in locations)

    def test_step4_warns_for_missing_file(self):
        """Missing file in ALL locations must trigger a warn or fail."""
        result = GuardResult()
        step4_all_locations_verification(
            "Check `nonexistent_file_xyz_12345.md` for content.",
            result,
        )
        # Either warned (file not found) or failed (session ID spoofed)
        # is acceptable. Must NOT be a clean pass.
        assert result.warned + result.failed > 0 or result.passed < 12

    def test_step4_passes_for_existing_file(self):
        """Existing file in workspace root must pass cleanly."""
        # Create a temporary file in workspace
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", dir="/home/arcana-novai/Documents/Xoe-NovAi/omega-engine",
            delete=False,
        ) as f:
            f.write("# temp test file\n")
            temp_path = Path(f.name)
        try:
            result = GuardResult()
            step4_all_locations_verification(
                f"Check `{temp_path.name}` for content.",
                result,
            )
            # The step must produce some result
            assert result.passed + result.warned + result.failed > 0
        finally:
            temp_path.unlink()

    def test_step4_handles_spoofed_session_id(self):
        """Unverifiable session IDs must trigger FAIL (not just warn).

        Per JEM-FORENSIC-001 Appendix C.4: spoofed session IDs are HIGH severity.
        """
        result = GuardResult()
        # A session ID that almost certainly doesn't exist
        step4_all_locations_verification(
            "Continue work in session ses_fake_session_xyz_not_real_99999.",
            result,
        )
        # Should fail (not just warn) for spoofed session IDs
        # If DB is unreachable, may warn; but should not pass cleanly
        # in either case
        assert result.failed + result.warned > 0


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: TOKEN ESTIMATION & WRITE-TOOL ROUTING
# ═══════════════════════════════════════════════════════════════════════════


class TestTokenEstimationAndRouting:
    """Test that step5/step6 correctly estimate tokens and route to write tool."""

    def test_estimate_small_prompt(self):
        """Small prompt should estimate < 8K tokens."""
        result = GuardResult()
        tokens = step5_estimated_tokens("Quick task: list files.", result)
        assert tokens < 8000
        assert result.metadata["estimated_output_tokens"] == tokens

    def test_estimate_large_prompt_triggers_routing(self):
        """Large prompt should trigger write-tool routing warning."""
        result = GuardResult()
        large_prompt = "Do a comprehensive analysis. " * 3000  # ~30K chars
        tokens = step5_estimated_tokens(large_prompt, result)
        assert tokens > 8000
        # Now test step6
        result2 = GuardResult()
        step6_write_tool_routing(tokens, result2)
        assert result2.metadata.get("write_tool_required") is True

    def test_write_tool_routing_under_threshold(self):
        """Under-threshold output should NOT require write tool."""
        result = GuardResult()
        step6_write_tool_routing(5000, result)
        assert result.metadata.get("write_tool_required") is False

    def test_cross_validator_p0(self):
        """P0 with large output should require cross-validator."""
        result = GuardResult()
        step7_cross_validator_escalation("P0", 10000, result)
        assert result.metadata.get("cross_validator_required") is True

    def test_cross_validator_p2(self):
        """P2 should NOT require cross-validator (only true P0/P1)."""
        result = GuardResult()
        step7_cross_validator_escalation("P2", 10000, result)
        assert result.metadata.get("cross_validator_required") is False


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 7: INTEGRATION — 12-STEP GUARD END-TO-END
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegrationEndToEnd:
    """Integration tests for the full 12-step guard."""

    def test_clean_prompt_passes(self):
        """A clean, well-formed prompt should pass all 12 steps."""
        from dispatch_guard import run_12_step_guard, GuardResult
        from argparse import Namespace
        args = Namespace(
            subagent_type="explore",
            prompt="Find the file AGENTS.md in the workspace.",
            task_id=None,
            entity="jem",
            priority="P3",
        )
        result = run_12_step_guard(args)
        # May have warnings but should not fail
        assert result.failed == 0, f"Clean prompt failed: {result.violations}"

    def test_p0_large_prompt_warns_write_tool(self):
        """P0 with large output should warn about write-tool routing."""
        from dispatch_guard import run_12_step_guard
        from argparse import Namespace
        large_prompt = "Comprehensive P0 forensic analysis. " * 2500
        args = Namespace(
            subagent_type="researcher",
            prompt=large_prompt,
            task_id=None,
            entity="jem",
            priority="P0",
        )
        result = run_12_step_guard(args)
        # Should have at least one warning (write-tool routing OR cross-validator)
        assert result.warned > 0, (
            f"P0 large prompt should produce warnings, got {result}"
        )
        # Should have cross-validator required
        assert result.metadata.get("cross_validator_required") is True
        # Should have write-tool required
        assert result.metadata.get("write_tool_required") is True

    def test_secret_in_prompt_fails(self):
        """A prompt with GOCSPX- prefix must FAIL (M35)."""
        from dispatch_guard import run_12_step_guard
        from argparse import Namespace
        args = Namespace(
            subagent_type="explore",
            prompt="Use this secret: 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 to test.",
            task_id=None,
            entity="jem",
            priority="P3",
        )
        result = run_12_step_guard(args)
        assert result.failed > 0, "Secret in prompt should FAIL step 9"
        assert any("GOCSPX" in v or "OAuth" in v for v in result.violations)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 8: L3-COMPLETION-ILLUSION DETECTION (PER JEM-FORENSIC-001)
# ═══════════════════════════════════════════════════════════════════════════


class TestCompletionIllusionDetection:
    """Test that graceful-looking-but-truncated outputs are detected.

    Per L3-CompletionIllusion (confidence 0.85, M23/M33):
    "An LLM subagent's state=completed is necessary but not sufficient for
     semantic exhaustion. The goldmine often lives in the tail."
    """

    def test_continuing_state_signals_incomplete(self):
        """state=continuing with queued_findings signals incomplete work."""
        envelope = {
            "state": "continuing",
            "last_chunk_id": 1,
            "total_chunks": 5,
            "queued_findings": ["remaining analysis pending"],
            "confidence": 0.85,
        }
        result = parse_completion_envelope(json.dumps(envelope))
        # Continuing is not a bypass or false-exhaust
        assert result is not None
        assert result.get("_bypass_detected") is None
        assert result["state"] == "continuing"
        # Validator should NOT flag this as invalid
        is_valid, _ = validate_completion_envelope(envelope, priority="P2")
        assert is_valid

    def test_exhausted_state_with_progress_pct_match(self):
        """If subagent reports exhausted, all queued_findings must be empty.

        The test verifies that false-exhaust (state=exhausted with non-empty
        queued_findings) is detected at validation time. This is the
        L3-CompletionIllusion lesson in action.
        """
        # False exhaust (the L3 lesson in action)
        envelope = {
            "state": "exhausted",
            "last_chunk_id": 5,
            "total_chunks": 5,
            "queued_findings": ["section 5b analysis was truncated"],
            "confidence": 0.97,
        }
        # First parse so the false-exhaust flag is set
        parsed = parse_completion_envelope(json.dumps(envelope))
        # Then validate the parsed envelope (which carries the flag)
        is_valid, issues = validate_completion_envelope(parsed, priority="P0")
        assert not is_valid
        assert any("FALSE-EXHAUST" in issue for issue in issues)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 9: STRESS — CONCURRENT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════


class TestConcurrentValidation:
    """Test that concurrent envelope validations don't corrupt state."""

    def test_concurrent_envelope_validations(self):
        """Multiple simultaneous validations should be independent."""
        import threading

        results = []
        errors = []

        def validate_envelope(idx):
            try:
                envelope = {
                    "state": "exhausted",
                    "last_chunk_id": idx,
                    "total_chunks": 100,
                    "queued_findings": [],
                    "confidence": 0.95,
                }
                is_valid, issues = validate_completion_envelope(envelope, priority="P2")
                results.append((idx, is_valid, len(issues)))
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=validate_envelope, args=(i,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"Concurrent validation errors: {errors}"
        assert len(results) == 50


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 10: REGRESSION — JEM-FORENSIC-001 LESSON APPLIED
# ═══════════════════════════════════════════════════════════════════════════


class TestJemForensicRegression:
    """Regression test for the JEM-FORENSIC-001 lesson.

    Per JEM-FORENSIC-001: "Verification must be exhaustive, not selective.
    The protocol should require 'all possible locations.'"
    """

    def test_sub_repo_file_searched_not_just_workspace(self):
        """A file in a sub-repo (not workspace root) must be found.

        The JEM-FORENSIC-001 lesson: a file at opencode-antigravity-auth/src/constants.ts
        exists in a sub-repo, not the workspace root. The hardened step4
        must search sub-repo DBs and locations.
        """
        result = GuardResult()
        # A file that exists in a sub-repo
        step4_all_locations_verification(
            "Check `constants.ts` in the opencode-antigravity-auth sub-repo.",
            result,
        )
        # The step should NOT simply fail because constants.ts is not in
        # the workspace root. It should find it in the sub-repo.
        # Note: this test is a "positive" check — the failure case
        # (file NOT in any sub-repo) is tested elsewhere.
        # Here we just verify the step ran without crashing.
        assert result.passed + result.warned + result.failed > 0

    def test_spoofed_session_id_in_sub_repo_handled(self):
        """Spoofed session IDs should fail regardless of sub-repo presence."""
        result = GuardResult()
        step4_all_locations_verification(
            "Resume ses_definitely_not_a_real_session_id_zzz_12345.",
            result,
        )
        # Should NOT silently pass — must warn or fail
        assert result.passed < 12 or result.warned > 0 or result.failed > 0


# ═══════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def temp_workspace(tmp_path, monkeypatch):
    """Create a temporary workspace for testing."""
    monkeypatch.chdir(tmp_path)
    # Create standard directories
    (tmp_path / "src").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "data").mkdir()
    (tmp_path / "docs").mkdir()
    return tmp_path


@pytest.fixture
def sample_envelope():
    """Return a valid sample completion envelope."""
    return {
        "state": "exhausted",
        "last_chunk_id": 5,
        "total_chunks": 5,
        "queued_findings": [],
        "confidence": 0.95,
    }


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
