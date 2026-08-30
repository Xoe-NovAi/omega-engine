# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 M34 Registration Wiring Tests (Task A1)
# ⬡ OMEGA ⬡ LILITH ⬡ M34 ⬡ REGISTRATION-TEST
# AP: AP-M34-REGISTRATION-TEST-v1.0.0
#
# Tests for Build Wave Phase 1 Task A1: M34 Registry Wiring
# Verifies that dispatch_guard.py Step 6b calls m34_register_subagent()
# and that the M34 registry is populated when subagents are dispatched.

"""
Test M34 Registration Wiring:
1. m34_register_subagent() function exists and works
2. dispatch_guard.py Step 6b calls m34_register_subagent()
3. M34 registry is populated when subagents are dispatched
4. Integration with dispatch() flow
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path - import modules directly to avoid package chain
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import directly from module files to avoid omega package import chain
import importlib.util

def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load m34_registry directly
m34_registry = _load_module("m34_registry", Path(__file__).parent.parent / "src/omega/oracle/m34_registry.py")
M34Registry = m34_registry.M34Registry
ActiveSubagent = m34_registry.ActiveSubagent
SessionStatus = m34_registry.SessionStatus

# Load subagent_dispatcher directly
subagent_dispatcher = _load_module("subagent_dispatcher", Path(__file__).parent.parent / "src/omega/oracle/subagent_dispatcher.py")
m34_register_subagent = subagent_dispatcher.m34_register_subagent
dispatch = subagent_dispatcher.dispatch
HandoffPacket = subagent_dispatcher.HandoffPacket

# Load dispatch_guard directly
dispatch_guard = _load_module("dispatch_guard", Path(__file__).parent.parent / "scripts/dispatch_guard.py")


class TestM34RegistrationFunction:
    """Test the m34_register_subagent() convenience function."""

    def test_m34_register_subagent_exists(self):
        """m34_register_subagent function is importable."""
        assert callable(m34_register_subagent)

    def test_m34_register_subagent_basic(self):
        """Basic registration via m34_register_subagent()."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            # Set env var for registry path
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "1"

            # Call the function
            result = m34_register_subagent(
                session_id="ses_test_001",
                target_agent="jem",
                task_description="Test task for M34 registration",
                task_type="research",
                expected_output="data/coordination/TEST.md",
            )

            assert result is True, "Registration should succeed"

            # Verify registry was populated
            registry = M34Registry(registry_path=test_path)
            data = registry.read()
            assert "ses_test_001" in data["sessions"]
            session = data["sessions"]["ses_test_001"]
            assert session["agent"] == "jem"
            assert session["task_brief"] == "Test task for M34 registration"
            assert session["task_type"] == "research"
            assert session["expected_deliverable"] == "data/coordination/TEST.md"
            assert session["status"] == "ALIVE"

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_m34_register_subagent_with_write_tool_required(self):
        """Registration with write_tool_required flag."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "1"

            result = m34_register_subagent(
                session_id="ses_test_002",
                target_agent="researcher",
                task_description="Large research task >8K tokens",
                task_type="research",
                expected_output="data/coordination/LARGE_RESEARCH.md",
                write_tool_required=True,
            )

            assert result is True

            registry = M34Registry(registry_path=test_path)
            data = registry.read()
            session = data["sessions"]["ses_test_002"]
            assert session["write_tool_required"] is True

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_m34_register_subagent_with_cross_validator(self):
        """Registration with cross_validator_agent for P0/P1."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "1"

            result = m34_register_subagent(
                session_id="ses_test_003",
                target_agent="verity",
                task_description="P0 compliance audit",
                task_type="verify",
                expected_output="data/coordination/AUDIT.md",
                priority="P0",
                cross_validator_agent="jem",
            )

            assert result is True

            registry = M34Registry(registry_path=test_path)
            data = registry.read()
            session = data["sessions"]["ses_test_003"]
            assert session["cross_validator_agent"] == "jem"

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_m34_register_subagent_graceful_degradation(self):
        """Registration fails gracefully when M34 is disabled."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            # M34 disabled
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "0"

            result = m34_register_subagent(
                session_id="ses_test_004",
                target_agent="jem",
                task_description="Test with M34 disabled",
            )

            # Should return False, not raise
            assert result is False

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)


class TestDispatchGuardStep6b:
    """Test dispatch_guard.py Step 6b integration."""

    def test_step6b_function_exists(self):
        """step6b_m34_register_subagent function exists in dispatch_guard."""
        import scripts.dispatch_guard as dg
        assert hasattr(dg, "step6b_m34_register_subagent")
        assert callable(dg.step6b_m34_register_subagent)

    def test_step6b_registers_when_m34_enabled(self):
        """Step 6b registers subagent when OMEGA_M34_ENABLED=1."""
        import scripts.dispatch_guard as dg

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "1"

            result = dg.GuardResult()
            dg.step6b_m34_register_subagent(
                subagent_type="researcher",
                prompt="Research task with estimated >8K tokens output",
                entity="researcher",
                result=result,
            )

            assert result.metadata.get("m34_registered") is True
            assert "m34_session_id" in result.metadata

            # Verify registry populated
            registry = M34Registry(registry_path=test_path)
            data = registry.read()
            session_id = result.metadata["m34_session_id"]
            assert session_id in data["sessions"]

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_step6b_skips_when_m34_disabled(self):
        """Step 6b passes without registering when M34 disabled."""
        import scripts.dispatch_guard as dg

        result = dg.GuardResult()
        dg.step6b_m34_register_subagent(
            subagent_type="researcher",
            prompt="Test prompt",
            entity="researcher",
            result=result,
        )

        assert result.metadata.get("m34_registered") is False
        assert result.passed >= 1  # Step passed

    def test_step6b_skips_for_spt(self):
        """Step 6b skips registration for SPT (general/spt) types."""
        import scripts.dispatch_guard as dg

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "1"

            result = dg.GuardResult()
            dg.step6b_m34_register_subagent(
                subagent_type="general",  # SPT type
                prompt="Test prompt",
                entity="general",
                result=result,
            )

            assert result.metadata.get("m34_registered") is False
            assert result.passed >= 1

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)


class TestDispatchIntegration:
    """Test M34 registration in the dispatch() flow."""

    def test_dispatch_registers_in_m34(self):
        """dispatch() registers subagent in M34 registry (M34-HOOK-001)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "1"

            packet = HandoffPacket(
                source_agent="kali",
                target_agent="jem",
                task_type="research",
                task_description="Research task from dispatch",
                expected_output="data/coordination/RESEARCH.md",
            )

            prompt = dispatch(packet)

            # Verify registry populated
            registry = M34Registry(registry_path=test_path)
            data = registry.read()
            # The session_id is based on packet.packet_id
            session_id = packet.packet_id
            assert session_id in data["sessions"]
            session = data["sessions"][session_id]
            assert session["agent"] == "jem"
            assert session["task_type"] == "research"

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)

    def test_dispatch_prompt_contains_task(self):
        """dispatch() returns prompt with task description."""
        packet = HandoffPacket(
            source_agent="kali",
            target_agent="jem",
            task_type="research",
            task_description="Research the meaning of life",
        )

        prompt = dispatch(packet)

        assert "Research the meaning of life" in prompt
        assert "jem" in prompt
        assert "kali" in prompt


class TestEndToEndDispatchGuard:
    """End-to-end test of dispatch_guard 12-step with M34 registration."""

    def test_full_12_step_with_m34_registration(self):
        """Run full 12-step guard with M34 enabled - verifies Step 6b runs."""
        import scripts.dispatch_guard as dg

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_path = Path(f.name)

        try:
            os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
            os.environ["OMEGA_M34_ENABLED"] = "1"

            args = dg.argparse.Namespace(
                subagent_type="researcher",
                task_id=None,
                prompt="Research task with large output requiring write tool",
                entity="researcher",
                priority="P2",
                check_only=False,
                dry_run=False,
                json=False,
                strict=False,
            )

            result = dg.run_12_step_guard(args)

            # Step 6b should have run and registered
            assert result.metadata.get("m34_registered") is True
            assert "m34_session_id" in result.metadata

            # Verify registry populated
            registry = M34Registry(registry_path=test_path)
            data = registry.read()
            session_id = result.metadata["m34_session_id"]
            assert session_id in data["sessions"]

        finally:
            os.environ.pop("OMEGA_M34_REGISTRY", None)
            os.environ.pop("OMEGA_M34_ENABLED", None)
            for p in [test_path, test_path + ".1.bak", test_path + ".lock"]:
                if os.path.exists(p):
                    os.unlink(p)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])