# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 M33 Sentinel Probe — MCP Tools
# ⬡ OMEGA ⬡ JEM ⬡ M33 ⬡ MCP-TOOLS
# AP: AP-M33-MCP-TOOLS-v1.0.0
#
# MCP tools for the M33 (Anti-Truncation & Stream Exhaustion Gate) mandate.
# Integrates with omega-hub FastMCP server.
#
# Per 5-EIS meta-review §4.1: 3-layer fix (preventive + structured probe + P0/P1 cross-validator).
# Per Jem's dispatch_guard.py hardening: M33 bypass detection, false-exhaust detection,
# tiered confidence thresholds (P0/P1 ≥ 0.95, P2+ ≥ 0.80), session ID spoofing detection.

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional, List, Any

from mcp.server.fastmcp import FastMCP

# Get the MCP instance from the server module
from mcp_servers.omega_hub.server import mcp

# Add src to path so we can import the probe
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Direct file-based import to avoid omega.__init__ chain
import importlib.util
_PROBE_PATH = Path(__file__).parent.parent.parent.parent / "src" / "omega" / "oracle" / "m33_probe.py"
spec = importlib.util.spec_from_file_location("omega.oracle.m33_probe", str(_PROBE_PATH))
assert spec is not None and spec.loader is not None, "Failed to load m33_probe spec"
_m33 = importlib.util.module_from_spec(spec)
sys.modules["omega.oracle.m33_probe"] = _m33
spec.loader.exec_module(_m33)

M33Probe = _m33.M33Probe
CompletionEnvelope = _m33.CompletionEnvelope
ProbeVerdict = _m33.ProbeVerdict
CompletionState = _m33.CompletionState
M34RegistryLike = _m33.M34RegistryLike

# Try to import M34Registry for the probe
try:
    _REGISTRY_PATH = Path(__file__).parent.parent.parent.parent / "src" / "omega" / "oracle" / "m34_registry.py"
    _spec = importlib.util.spec_from_file_location("omega.oracle.m34_registry", str(_REGISTRY_PATH))
    assert _spec is not None and _spec.loader is not None
    _m34 = importlib.util.module_from_spec(_spec)
    sys.modules["omega.oracle.m34_registry"] = _m34
    _spec.loader.exec_module(_m34)
    M34Registry = _m34.M34Registry
except Exception:
    M34Registry = None


def _get_probe(m34_registry: Optional[M34RegistryLike] = None) -> M33Probe:
    """Get an M33Probe instance, optionally with M34 registry for cross-validation."""
    return M33Probe(m34_registry=m34_registry)


@mcp.tool()
async def m33_build_probe_prompt(
    session_id: str,
    expected_chunks: int = 10,
    deliverable_path: Optional[str] = None,
) -> dict:
    """Build the structured M33 probe prompt for a subagent.

    This is the Layer 2 structured probe that replaces free-form "STREAM_EXHAUSTED"
    with a strict JSON envelope requirement.

    Per 5-EIS meta-review §1.1: The probe asks the subagent to provide a structured
    JSON envelope describing its actual completion state.

    Args:
        session_id: Subagent session ID
        expected_chunks: Number of chunks the subagent planned to write (0-indexed)
        deliverable_path: Optional path to the expected deliverable file

    Returns:
        {"prompt": "<structured probe prompt>", "schema": "<JSON schema description>"}
    """
    probe = _get_probe()
    prompt = probe.build_probe_prompt(session_id, expected_chunks, deliverable_path)
    return {
        "prompt": prompt,
        "schema": {
            "state": "exhausted | continuing",
            "last_chunk_id": "int (0-indexed, last chunk written)",
            "total_chunks": "int (total chunks planned)",
            "queued_findings": "list[str] (pending findings, empty if exhausted)",
            "confidence": "float 0.0-1.0 (honest confidence in completion)",
            "deliverable_path": "string | null",
            "deliverable_size_bytes": "int | null",
            "structured_evidence": "object | null (optional citations/evidence)",
        },
        "rules": [
            "Do NOT reply with free-form text. Do NOT reply with 'STREAM_EXHAUSTED' or 'DONE'.",
            "Do NOT reply with markdown code fences. Pure JSON only.",
            "If you have more findings to write, set state='continuing' and list them in queued_findings.",
            "If you have written all planned chunks and the deliverable is complete, set state='exhausted' and queued_findings=[]",
            "Confidence should reflect your honest assessment. 0.99 only if you are certain.",
            "After your JSON response, STOP. Do not add commentary.",
        ],
    }


@mcp.tool()
async def m33_validate_probe_response(
    session_id: str,
    response: str,
    priority: Literal["P0", "P1", "P2", "P3"] = "P2",
) -> dict:
    """Validate a subagent's probe response against the M33 schema.

    Per 5-EIS meta-review §1.1: Reject free-form STREAM_EXHAUSTED, require
    JSON envelope, check confidence threshold, flag P0/P1 for cross-validation.

    Args:
        session_id: Subagent session ID
        response: Raw response from subagent (JSON string or free-form text)
        priority: Task priority (P0/P1/P2/P3) - determines confidence threshold

    Returns:
        ProbeVerdict as dict with fields:
        - accepted: bool
        - retry_recommended: bool
        - reason: str
        - confidence_met: bool
        - confidence_threshold: float
        - cross_validation_required: bool
        - schema_valid: bool
        - free_form_detected: bool
    """
    probe = _get_probe()
    verdict = probe.validate_response(response, session_id, priority)
    return {
        "accepted": verdict.accepted,
        "retry_recommended": verdict.retry_recommended,
        "reason": verdict.reason,
        "confidence_met": verdict.confidence_met,
        "confidence_threshold": verdict.confidence_threshold,
        "cross_validation_required": verdict.cross_validation_required,
        "schema_valid": verdict.schema_valid,
        "free_form_detected": verdict.free_form_detected,
    }


@mcp.tool()
async def m33_should_require_write_tool(
    estimated_output_tokens: int,
    task_type: Literal["research", "forensic", "review", "design", "implement", "verify"],
    priority: Literal["P0", "P1", "P2", "P3"] = "P2",
) -> dict:
    """Layer 1: Decide if a subagent should be required to use write tool at dispatch time.

    Per meta-review §1.1: For reports > 8K tokens, the orchestrator must
    require the subagent to use the write tool, not the chat stream.
    Archangel Architecture: Dynamic threshold based on hardware state.

    Args:
        estimated_output_tokens: Estimated deliverable size in tokens
        task_type: Type of task
        priority: Task priority

    Returns:
        {"write_tool_required": bool, "threshold_used": int, "reason": str}
    """
    probe = _get_probe()
    required = probe.should_require_write_tool(estimated_output_tokens, task_type, priority)
    threshold = probe.calculate_dynamic_write_threshold()
    return {
        "write_tool_required": required,
        "threshold_used": threshold,
        "reason": (
            f"Estimated {estimated_output_tokens} tokens > threshold {threshold}"
            if required else f"Estimated {estimated_output_tokens} tokens <= threshold {threshold}"
        ),
    }


@mcp.tool()
async def m33_calculate_dynamic_threshold() -> dict:
    """Get the current dynamic write-tool threshold based on hardware state.

    Archangel Architecture: Adjusts threshold based on memory pressure,
    thermal throttling, and OOM risk.

    Returns:
        {"threshold": int, "base_threshold": int, "factors": {...}}
    """
    probe = _get_probe()
    threshold = probe.calculate_dynamic_write_threshold()
    base = _m33.WRITE_TOOL_TOKEN_THRESHOLD
    hw = probe._get_hw_monitor()
    factors = {}
    if hw:
        try:
            mem = hw.get_memory_status()
            factors = {
                "memory_pressure": mem.get("memory_pressure", 0.0),
                "thermal_throttling": hw.is_thermal_throttling(),
                "oom_risk": mem.get("oom_risk", {}).get("risk_level", "SAFE"),
            }
        except Exception as e:
            factors = {"error": str(e)}
    return {
        "threshold": threshold,
        "base_threshold": base,
        "factors": factors,
    }


@mcp.tool()
async def m33_audit_probe_log(
    limit: int = 100,
    session_id: Optional[str] = None,
) -> dict:
    """Read the M33 probe audit log.

    Returns recent probe audit entries for verification.

    Args:
        limit: Maximum number of entries to return
        session_id: Optional filter by session ID

    Returns:
        {"entries": [...], "count": N}
    """
    probe = _get_probe()
    log_path = probe.log_path
    if not log_path.exists():
        return {"entries": [], "count": 0}

    entries = []
    with open(log_path, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if session_id is None or entry.get("session_id") == session_id:
                    entries.append(entry)
            except json.JSONDecodeError:
                pass

    return {"entries": entries[-limit:], "count": len(entries)}


@mcp.tool()
async def m33_verify_deliverable(
    session_id: str,
    deliverable_path: str,
) -> dict:
    """Verify a claimed deliverable exists and is non-empty.

    Used by the probe validation to check deliverable_path claims.

    Args:
        session_id: Subagent session ID
        deliverable_path: Path to the deliverable file

    Returns:
        {"exists": bool, "size_bytes": int, "valid": bool}
    """
    p = Path(deliverable_path)
    if not p.exists():
        return {"exists": False, "size_bytes": 0, "valid": False}
    size = p.stat().st_size
    return {"exists": True, "size_bytes": size, "valid": size > 0}


# Ensure module is importable
__all__ = [
    "m33_build_probe_prompt",
    "m33_validate_probe_response",
    "m33_should_require_write_tool",
    "m33_calculate_dynamic_threshold",
    "m33_audit_probe_log",
    "m33_verify_deliverable",
]
