#!/usr/bin/env python3
"""Standalone test for Task A1: M34 Registry Wiring"""

import json
import os
import sys
import tempfile
from pathlib import Path

# Direct module loading to avoid package import chain
import importlib.util

def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        raise ImportError(f"Could not load spec for {file_path}")
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise ImportError(f"Could not load module {module_name}")
    spec.loader.exec_module(module)
    return module

# Load modules directly
base = Path(__file__).parent.parent
m34_registry = _load_module("m34_registry", base / "src/omega/oracle/m34_registry.py")
M34Registry = m34_registry.M34Registry
ActiveSubagent = m34_registry.ActiveSubagent
SessionStatus = m34_registry.SessionStatus

subagent_dispatcher = _load_module("subagent_dispatcher", base / "src/omega/oracle/subagent_dispatcher.py")
m34_register_subagent = subagent_dispatcher.m34_register_subagent
dispatch = subagent_dispatcher.dispatch
HandoffPacket = subagent_dispatcher.HandoffPacket

dispatch_guard = _load_module("dispatch_guard", base / "scripts/dispatch_guard.py")

def test_m34_register_subagent_exists():
    """Test that m34_register_subagent function exists."""
    assert callable(m34_register_subagent), "m34_register_subagent should be callable"
    print("✓ m34_register_subagent function exists")

def test_m34_register_subagent_basic():
    """Test basic registration via m34_register_subagent()."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_path = Path(f.name)

    try:
        os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
        os.environ["OMEGA_M34_ENABLED"] = "1"

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
        print("✓ m34_register_subagent basic registration works")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

def test_m34_register_subagent_with_write_tool():
    """Test registration with write_tool_required flag."""
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
        print("✓ m34_register_subagent with write_tool_required works")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

def test_m34_register_subagent_with_cross_validator():
    """Test registration with cross_validator_agent for P0/P1."""
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
        print("✓ m34_register_subagent with cross_validator_agent works")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

def test_m34_register_subagent_graceful_degradation():
    """Test registration fails gracefully when M34 is disabled."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_path = Path(f.name)

    try:
        os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
        os.environ["OMEGA_M34_ENABLED"] = "0"

        result = m34_register_subagent(
            session_id="ses_test_004",
            target_agent="jem",
            task_description="Test with M34 disabled",
        )

        assert result is False, "Should return False when M34 disabled"
        print("✓ m34_register_subagent graceful degradation works")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

def test_step6b_function_exists():
    """Test step6b_m34_register_subagent function exists in dispatch_guard."""
    assert hasattr(dispatch_guard, "step6b_m34_register_subagent"), "step6b_m34_register_subagent should exist"
    assert callable(dispatch_guard.step6b_m34_register_subagent), "step6b_m34_register_subagent should be callable"
    print("✓ step6b_m34_register_subagent function exists in dispatch_guard")

def test_step6b_registers_when_m34_enabled():
    """Test Step 6b registers subagent when OMEGA_M34_ENABLED=1."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_path = Path(f.name)

    try:
        os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
        os.environ["OMEGA_M34_ENABLED"] = "1"

        result = dispatch_guard.GuardResult()
        dispatch_guard.step6b_m34_register_subagent(
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
        print("✓ Step 6b registers subagent when M34 enabled")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

def test_step6b_skips_when_m34_disabled():
    """Test Step 6b passes without registering when M34 disabled."""
    result = dispatch_guard.GuardResult()
    dispatch_guard.step6b_m34_register_subagent(
        subagent_type="researcher",
        prompt="Test prompt",
        entity="researcher",
        result=result,
    )

    assert result.metadata.get("m34_registered") is False
    assert result.passed >= 1
    print("✓ Step 6b skips when M34 disabled")

def test_step6b_skips_for_spt():
    """Test Step 6b skips registration for SPT (general/spt) types."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_path = Path(f.name)

    try:
        os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
        os.environ["OMEGA_M34_ENABLED"] = "1"

        result = dispatch_guard.GuardResult()
        dispatch_guard.step6b_m34_register_subagent(
            subagent_type="general",  # SPT type
            prompt="Test prompt",
            entity="general",
            result=result,
        )

        assert result.metadata.get("m34_registered") is False
        assert result.passed >= 1
        print("✓ Step 6b skips for SPT types")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

def test_dispatch_registers_in_m34():
    """Test dispatch() registers subagent in M34 registry (M34-HOOK-001)."""
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
        session_id = packet.packet_id
        assert session_id in data["sessions"]
        session = data["sessions"][session_id]
        assert session["agent"] == "jem"
        assert session["task_type"] == "research"
        print("✓ dispatch() registers in M34 registry (M34-HOOK-001)")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

def test_full_12_step_with_m34_registration():
    """Test full 12-step guard with M34 enabled - verifies Step 6b runs."""
    import argparse

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        test_path = Path(f.name)

    try:
        os.environ["OMEGA_M34_REGISTRY"] = str(test_path)
        os.environ["OMEGA_M34_ENABLED"] = "1"

        args = argparse.Namespace(
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

        result = dispatch_guard.run_12_step_guard(args)

        # Step 6b should have run and registered
        assert result.metadata.get("m34_registered") is True
        assert "m34_session_id" in result.metadata

        # Verify registry populated
        registry = M34Registry(registry_path=test_path)
        data = registry.read()
        session_id = result.metadata["m34_session_id"]
        assert session_id in data["sessions"]
        print("✓ Full 12-step guard with M34 registration works")

    finally:
        os.environ.pop("OMEGA_M34_REGISTRY", None)
        os.environ.pop("OMEGA_M34_ENABLED", None)
        for p in [test_path, test_path.with_suffix(test_path.suffix + ".1.bak"), test_path.with_suffix(test_path.suffix + ".lock")]:
            if os.path.exists(p):
                os.unlink(p)

if __name__ == "__main__":
    print("Running Task A1: M34 Registry Wiring Tests\n")
    
    test_m34_register_subagent_exists()
    test_m34_register_subagent_basic()
    test_m34_register_subagent_with_write_tool()
    test_m34_register_subagent_with_cross_validator()
    test_m34_register_subagent_graceful_degradation()
    test_step6b_function_exists()
    test_step6b_registers_when_m34_enabled()
    test_step6b_skips_when_m34_disabled()
    test_step6b_skips_for_spt()
    test_dispatch_registers_in_m34()
    test_full_12_step_with_m34_registration()
    
    print("\n✅ All Task A1 tests PASSED!")