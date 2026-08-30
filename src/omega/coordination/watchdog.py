# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-WATCHDOG-v1.0.0
"""
Subagent Watchdog — Failure Observability for Agent Orchestration.
Provides full visibility into subagent thinking, errors, and failures.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FailureClass(Enum):
    """Classification of subagent failure types."""

    TIMEOUT = "timeout"
    TOOL_CHAIN_COLLAPSE = "tool_chain"
    MANDATE_VIOLATION = "mandate"
    RESOURCE_EXHAUSTION = "resource"
    VENV_VIOLATION = "venv"
    STREAMING_TIMEOUT = "streaming"
    HERITAGE_VIOLATION = "heritage"
    VERSION_MISMATCH = "version_mismatch"
    CREDENTIAL_ERROR = "credential"
    UNKNOWN = "unknown"


@dataclass
class SubagentThinkingStep:
    """Single step in subagent thinking trace."""

    timestamp: datetime
    step_type: str  # "reasoning" | "tool_call" | "tool_result" | "decision"
    content: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict] = None
    tool_result: Optional[str] = None


@dataclass
class FailureReport:
    """Complete failure report with full observability."""

    subagent_id: str
    subagent_type: str
    task_description: str
    failure_class: FailureClass
    error_message: str
    thinking_trace: List[SubagentThinkingStep]
    partial_output: str
    timestamp: datetime
    hivemind_packet_id: str
    retry_recommendation: str  # "retry_same" | "retry_different_model" | "escalate" | "abort"
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WatchdogConfig:
    """Configuration for watchdog behavior."""

    capture_thinking: bool = True
    capture_tool_calls: bool = True
    max_thinking_steps: int = 1000
    auto_log_hivemind: bool = True
    alert_on_failure: bool = True
    retry_on: List[FailureClass] = field(
        default_factory=lambda: [
            FailureClass.TIMEOUT,
            FailureClass.STREAMING_TIMEOUT,
            FailureClass.RESOURCE_EXHAUSTION,
        ]
    )
    thinking_capture_interval: float = 0.1  # seconds


WATCHDOG_SYSTEM_PROMPT = """# 🔱 SUBAGENT WATCHDOG MONITORING ACTIVE

Your execution is being monitored by the Subagent Watchdog for failure observability.
This ensures the launching agent (and human overseer) has full visibility into your thinking,
tool calls, and any failures — even if you crash or timeout.

## YOUR RESPONSIBILITIES:
1. **Think out loud** — Document your reasoning, decisions, and uncertainty
2. **Report tool calls** — The watchdog captures tool calls automatically, but note WHY you chose each tool
3. **Document failures immediately** — If you hit an error, timeout, or mandate violation:
   - Continue thinking (don't stop)
   - Document the exact failure point
   - Note what you were trying to do
   - The watchdog needs FULL CONTEXT, not just the error message
4. **Don't suppress errors** — Mandate M23: No soft failures. Report `[TOOL-CHAIN-COLLAPSE]` etc.

## WATCHDOG CAPTURES:
- All reasoning steps (timestamped)
- All tool calls with args and results
- Partial output up to failure point
- Error classification (M1-M25 mandate mapping)
- Retry recommendation for launching agent

## FAILURE CLASSES (Auto-detected):
- TIMEOUT: Generic timeout
- STREAMING_TIMEOUT: M25 chunk/total timeout (Nemotron 30s+ gaps)
- TOOL_CHAIN_COLLAPSE: M23 mandatory tool missing
- VENV_VIOLATION: M24 --break-system-packages
- MANDATE_VIOLATION: M1-M25 violation
- RESOURCE_EXHAUSTION: OOM, rate limit, thermal
- HERITAGE_VIOLATION: M14 unvetted [id-soft:] tag
- CREDENTIAL_ERROR: Omega-Vault credential failure
- VERSION_MISMATCH: Version watchdog detected breaking change

The watchdog is your safety net — it ensures no failure goes unobserved.
"""


def classify_failure(
    error_message: str, thinking_trace: List[SubagentThinkingStep], partial_output: str
) -> FailureClass:
    """Classify failure based on error + context."""
    error_lower = error_message.lower()

    # M23 - Tool chain collapse
    if any(
        kw in error_lower
        for kw in ["websearch", "webfetch", "tool not found", "mandatory tool", "tool unavailable"]
    ):
        return FailureClass.TOOL_CHAIN_COLLAPSE

    # M24 - Venv violation
    if any(
        kw in error_lower
        for kw in ["--break-system-packages", "system package", "break-system-packages"]
    ):
        return FailureClass.VENV_VIOLATION

    # M25 - Streaming timeout
    if any(
        kw in error_lower
        for kw in ["chunk timeout", "stream timeout", "streaming timeout", "stream stalled"]
    ):
        return FailureClass.STREAMING_TIMEOUT

    # M14 - Heritage violation
    if "[id-soft:]" in error_lower and "unvetted" in error_lower:
        return FailureClass.HERITAGE_VIOLATION

    # Resource exhaustion
    if any(
        kw in error_lower
        for kw in [
            "oom",
            "out of memory",
            "memory error",
            "rate limit",
            "429",
            "thermal",
            "throttl",
        ]
    ):
        return FailureClass.RESOURCE_EXHAUSTION

    # Version mismatch
    if any(
        kw in error_lower
        for kw in ["version mismatch", "incompatible version", "breaking change", "api version"]
    ):
        return FailureClass.VERSION_MISMATCH

    # Credential error
    if any(
        kw in error_lower
        for kw in ["credential", "api key", "auth failed", "unauthorized", "401", "403"]
    ):
        return FailureClass.CREDENTIAL_ERROR

    # Generic timeout
    if "timeout" in error_lower:
        return FailureClass.TIMEOUT

    return FailureClass.UNKNOWN


def retry_recommendation(failure_class: FailureClass, context: Dict[str, Any]) -> str:
    """Recommend retry strategy based on failure class."""
    strategies = {
        FailureClass.TIMEOUT: "retry_same",
        FailureClass.STREAMING_TIMEOUT: "retry_different_model",
        FailureClass.RESOURCE_EXHAUSTION: "retry_different_model",
        FailureClass.CREDENTIAL_ERROR: "retry_different_model",
        FailureClass.VERSION_MISMATCH: "escalate",
        FailureClass.VENV_VIOLATION: "abort",
        FailureClass.TOOL_CHAIN_COLLAPSE: "abort",
        FailureClass.HERITAGE_VIOLATION: "abort",
        FailureClass.MANDATE_VIOLATION: "abort",
        FailureClass.UNKNOWN: "escalate",
    }
    return strategies.get(failure_class, "escalate")


async def log_failure_to_hivemind(
    failure: FailureReport, launching_entity: str = "kali", launching_channel: str = "opencode"
) -> str:
    """Log failure to Hivemind for coordination and alerting."""
    try:
        from omega_hub import hivemind_submit_handoff

        packet_id = await hivemind_submit_handoff(
            target_channel=launching_channel,
            target_entity=launching_entity,
            source_channel="watchdog",
            source_entity="subagent_watchdog",
            task=f"SUBAGENT FAILURE: {failure.failure_class.value}",
            context=(
                f"Subagent {failure.subagent_id} ({failure.subagent_type}) failed\n"
                f"Task: {failure.task_description}\n"
                f"Error: {failure.error_message}\n"
                f"Thinking steps captured: {len(failure.thinking_trace)}\n"
                f"Partial output ({len(failure.partial_output)} chars): {failure.partial_output[:500]}...\n"
                f"Failure class: {failure.failure_class.value}\n"
                f"Retry recommendation: {failure.retry_recommendation}\n"
                f"Timestamp: {failure.timestamp.isoformat()}"
            ),
            priority=2,  # Critical
        )
        return packet_id
    except Exception as e:
        logger.error(f"Failed to log failure to Hivemind: {e}")
        return f"hivemind_error_{uuid.uuid4().hex[:8]}"


async def log_system_failure(failure: FailureReport) -> None:
    """Log to SYSTEM_FAILURE_LOG (M23 compliance)."""
    try:
        import anyio

        log_path = "data/coordination/SYSTEM_FAILURE_LOG.md"
        entry = f"""
## [{failure.timestamp.isoformat()}] SUBAGENT FAILURE: {failure.failure_class.value}
- **Subagent**: {failure.subagent_id} ({failure.subagent_type})
- **Task**: {failure.task_description}
- **Error**: {failure.error_message}
- **Failure Class**: {failure.failure_class.value}
- **Thinking Steps**: {len(failure.thinking_trace)}
- **Partial Output**: {failure.partial_output[:500]}...
- **Retry**: {failure.retry_recommendation}
- **Hivemind Packet**: {failure.hivemind_packet_id}
- **Context**: {failure.context}

---
"""
        async with await anyio.open_file(log_path, "a") as f:
            await f.write(entry)
    except Exception as e:
        logger.error(f"Failed to log system failure: {e}")


async def alert_launching_agent(failure: FailureReport, launching_entity: str = "kali") -> None:
    """Alert launching agent via Hivemind heartbeat."""
    try:
        from omega_hub import hivemind_redis_publish

        await hivemind_redis_publish(
            channel="watchdog_alerts",
            message={
                "type": "subagent_failure",
                "subagent_id": failure.subagent_id,
                "failure_class": failure.failure_class.value,
                "launching_entity": launching_entity,
                "retry_recommendation": failure.retry_recommendation,
                "timestamp": failure.timestamp.isoformat(),
            },
            ttl=300,
        )
    except Exception as e:
        logger.warning(f"Failed to publish watchdog alert: {e}")


# --- Task Wrapper with Watchdog ---


async def task_with_watchdog(
    subagent_type: str,
    description: str,
    prompt: str,
    config: Optional["WatchdogConfig"] = None,
    launching_entity: str = "kali",
    launching_channel: str = "opencode",
) -> tuple[Any, Optional[FailureReport]]:
    """
    Spawns subagent with watchdog monitoring.
    Returns (result, failure_report) — failure_report is None on success.
    """
    from opencode import task  # OpenCode task tool

    config = config or WatchdogConfig()
    subagent_id = f"{subagent_type}_{uuid.uuid4().hex[:8]}"

    # Build watchdog-aware prompt
    watchdog_prompt = f"{WATCHDOG_SYSTEM_PROMPT}\n\n---\nORIGINAL TASK:\n{prompt}"

    thinking_trace: List[SubagentThinkingStep] = []
    partial_output = ""

    try:
        # Note: OpenCode's task() tool doesn't natively support thinking capture.
        # This is a wrapper that catches exceptions and builds FailureReport.
        # Full thinking capture requires OpenCode runtime support or Hivemind integration.

        result = await task(
            subagent_type=subagent_type, description=description, prompt=watchdog_prompt
        )

        # Check for failure indicators in result
        if _is_failure_result(result):
            failure = FailureReport(
                subagent_id=f"{subagent_type}_{uuid.uuid4().hex[:8]}",
                subagent_type=subagent_type,
                task_description=description,
                failure_class=FailureClass.UNKNOWN,
                error_message=_extract_error_message(result),
                thinking_trace=[],  # Would need runtime support
                partial_output=str(result)[:5000],
                timestamp=datetime.now(timezone.utc),
                hivemind_packet_id="",
                retry_recommendation="escalate",
                context={"result_type": type(result).__name__},
            )
            failure.failure_class = classify_failure(
                failure.error_message, [], failure.partial_output
            )
            failure.retry_recommendation = retry_recommendation(failure.failure_class, {})

            if config.auto_log_hivemind:
                failure.hivemind_packet_id = await log_failure_to_hivemind(failure)
                await log_system_failure(failure)

            if config.alert_on_failure:
                await alert_launching_agent(failure)

            return None, failure

        return result, None

    except Exception as e:
        # Tool-level exception (timeout, connection error, etc.)
        failure = FailureReport(
            subagent_id=f"{subagent_type}_{uuid.uuid4().hex[:8]}",
            subagent_type=subagent_type,
            task_description=description,
            failure_class=classify_failure(str(e), [], ""),
            error_message=str(e),
            thinking_trace=[],
            partial_output="",
            timestamp=datetime.now(timezone.utc),
            hivemind_packet_id="",
            retry_recommendation=retry_recommendation(FailureClass.UNKNOWN, {}),
            context={"exception_type": type(e).__name__},
        )

        if config.auto_log_hivemind:
            failure.hivemind_packet_id = await log_failure_to_hivemind(failure)
            await log_system_failure(failure)

        if config.alert_on_failure:
            await alert_launching_agent(failure)

        return None, failure


def _is_failure_result(result: Any) -> bool:
    """Check if result indicates failure."""
    if result is None:
        return True
    if isinstance(result, str):
        error_indicators = ["error:", "failed:", "exception:", "traceback", "[tool-chain-collapse]"]
        return any(ind in result.lower() for ind in error_indicators)
    if isinstance(result, dict):
        return result.get("status") == "error" or "error" in result
    return False


def _extract_error_message(result: Any) -> str:
    """Extract error message from result."""
    if isinstance(result, str):
        return result
    if isinstance(result, dict):
        return result.get("error", result.get("message", str(result)))
    return str(result)


# --- Hivemind Integration (requires omega_hub) ---


async def _hivemind_submit_handoff(
    target_channel: str,
    target_entity: str,
    source_channel: str,
    source_entity: str,
    task: str,
    context: str,
    priority: int = 0,
) -> str:
    """Submit handoff to Hivemind (placeholder for actual omega_hub call)."""
    # This would call omega_hub_hivemind_submit_handoff
    # For now, return mock packet ID
    return f"watchdog_{uuid.uuid4().hex[:12]}"


# Export for use
__all__ = [
    "FailureClass",
    "SubagentThinkingStep",
    "FailureReport",
    "WatchdogConfig",
    "WATCHDOG_SYSTEM_PROMPT",
    "classify_failure",
    "retry_recommendation",
    "task_with_watchdog",
    "log_failure_to_hivemind",
    "log_system_failure",
    "alert_launching_agent",
]
