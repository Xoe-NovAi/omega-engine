# 🔱 Subagent Watchdog System — Failure Observability for Agent Orchestration
**AP Token**: `AP-WATCHDOG-v1.0.0`
⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_watchdog ⬡ 2026-07-19

---

## 🎯 Problem Statement

**Current State**: When `task()` spawns a subagent, the launching agent gets only:
- `task_result` (success) — final output
- `task_result` (error) — truncated error message, NO thinking, NO partial output, NO context

**Required State**: Launching agent (and human overseer) MUST have:
- Full subagent thinking trace (even on failure)
- Partial output up to failure point
- Error classification (timeout, tool failure, mandate violation, etc.)
- Automatic hivemind logging for coordination
- Retry/fallback decision support

---

## 🏗️ Architecture: Watchdog as Sidecar Monitor

```
┌─────────────────────────────────────────────────────────────┐
│                    LAUNCHING AGENT (Kali)                   │
│  task(subagent_type="researcher", prompt="...")            │
└──────────────────────────┬──────────────────────────────────┘
                           │ spawns
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  SUBAGENT (Researcher)          WATCHDOG (Sidecar)          │
│  ┌─────────────────────┐       ┌─────────────────────┐     │
│  │ Thinking            │──────▶│ Stream capture      │     │
│  │ Tool calls          │──────▶│ Classification      │     │
│  │ Output              │──────▶│ Hivemind logging    │     │
│  │ Errors              │──────▶│ Alert launching agent│    │
│  └─────────────────────┘       └─────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  LAUNCHING AGENT RECEIVES:                                  │
│  - Full result (success)                                    │
│  - FailureReport (failure) with:                            │
│     * thinking_trace (full)                                 │
│     * partial_output                                        │
│     * error_classification                                  │
│     * hivemind_packet_id                                    │
│     * retry_recommendation                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Watchdog Data Model

```python
# src/omega/coordination/watchdog.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
import uuid

class FailureClass(Enum):
    TIMEOUT = "timeout"                    # Chunk/total stream timeout
    TOOL_CHAIN_COLLAPSE = "tool_chain"     # Mandatory tool missing (M23)
    MANDATE_VIOLATION = "mandate"          # M1-M25 violation
    RESOURCE_EXHAUSTION = "resource"       # OOM, rate limit, thermal
    VENV_VIOLATION = "venv"                # --break-system-packages (M24)
    STREAMING_TIMEOUT = "streaming"        # M25 chunk timeout
    HERITAGE_VIOLATION = "heritage"        # Unvetted [id-soft:] tag (M14)
    UNKNOWN = "unknown"

@dataclass
class SubagentThinkingStep:
    timestamp: datetime
    step_type: str          # "reasoning" | "tool_call" | "tool_result" | "decision"
    content: str
    tool_name: Optional[str] = None
    tool_args: Optional[Dict] = None
    tool_result: Optional[str] = None

@dataclass
class FailureReport:
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
    capture_thinking: bool = True
    capture_tool_calls: bool = True
    max_thinking_steps: int = 1000
    auto_log_hivemind: bool = True
    alert_on_failure: bool = True
    retry_on: List[FailureClass] = field(default_factory=lambda: [
        FailureClass.TIMEOUT,
        FailureClass.STREAMING_TIMEOUT,
        FailureClass.RESOURCE_EXHAUSTION,
    ])
```

---

## 🔧 Implementation: Watchdog Integration with `task()` Tool

### Option A: Wrapper Function (Immediate)

```python
# src/omega/coordination/task_with_watchdog.py

async def task_with_watchdog(
    subagent_type: str,
    description: str,
    prompt: str,
    watchdog_config: WatchdogConfig = None
) -> tuple[Any, Optional[FailureReport]]:
    """
    Spawns subagent with watchdog monitoring.
    Returns (result, failure_report) — failure_report is None on success.
    """
    config = watchdog_config or WatchdogConfig()
    
    # Generate unique subagent ID for tracking
    subagent_id = f"{subagent_type}_{uuid.uuid4().hex[:8]}"
    
    # Inject watchdog prompt prefix
    watchdog_prompt = f"""
{WATCHDOG_SYSTEM_PROMPT}

---
ORIGINAL TASK:
{prompt}

---
WATCHDOG INSTRUCTIONS:
- Your thinking and tool calls are being monitored for failure analysis
- If you encounter ANY error, continue thinking and document the failure
- Do NOT suppress errors — the watchdog needs full context
- On timeout/rate limit: document exact point of failure
"""
    
    try:
        result = await task(
            subagent_type=subagent_type,
            description=description,
            prompt=watchdog_prompt
        )
        
        # Success — check if result contains failure indicators
        if _is_failure_result(result):
            failure = _extract_failure(subagent_id, subagent_type, description, result, config)
            await _log_failure(failure, config)
            return None, failure
        
        return result, None
        
    except Exception as e:
        # Tool-level exception (timeout, connection error)
        failure = FailureReport(
            subagent_id=subagent_id,
            subagent_type=subagent_type,
            task_description=description,
            failure_class=_classify_exception(e),
            error_message=str(e),
            thinking_trace=[],  # Would need subagent-side capture
            partial_output="",
            timestamp=datetime.now(timezone.utc),
            hivemind_packet_id="",
            retry_recommendation=_retry_recommendation(e),
            context={"exception_type": type(e).__name__}
        )
        await _log_failure(failure, config)
        return None, failure
```

### Option B: Hivemind-Integrated Watchdog (Proper)

```python
# src/omega/coordination/watchdog_hivemind.py

class SubagentWatchdog:
    """Monitors subagent execution via Hivemind sidecar."""
    
    def __init__(self, launching_entity: str, launching_channel: str = "opencode"):
        self.launching_entity = launching_entity
        self.launching_channel = launching_channel
        self.active_monitors: Dict[str, asyncio.Task] = {}
    
    async def spawn_monitored(
        self,
        subagent_type: str,
        description: str,
        prompt: str,
        config: WatchdogConfig = None
    ) -> tuple[Any, Optional[FailureReport]]:
        """Spawn subagent with full watchdog monitoring."""
        
        config = config or WatchdogConfig()
        subagent_id = f"{subagent_type}_{uuid.uuid4().hex[:8]}"
        
        # 1. Create Hivemind session for this subagent
        session_id = await self._create_hivemind_session(subagent_id, subagent_type)
        
        # 2. Start thinking capture stream (via Hivemind)
        thinking_stream = await self._start_thinking_capture(session_id, config)
        
        # 3. Spawn subagent with watchdog-aware prompt
        enhanced_prompt = self._build_watchdog_prompt(prompt, session_id, config)
        
        try:
            result = await task(
                subagent_type=subagent_type,
                description=description,
                prompt=enhanced_prompt
            )
            
            # 4. Stop capture, analyze result
            await self._stop_thinking_capture(session_id)
            
            if _is_failure_result(result):
                failure = await self._build_failure_report(
                    subagent_id, subagent_type, description, 
                    result, session_id, config
                )
                await self._log_and_alert(failure, config)
                return None, failure
            
            return result, None
            
        except Exception as e:
            await self._stop_thinking_capture(session_id)
            failure = await self._build_exception_failure(
                subagent_id, subagent_type, description, e, session_id, config
            )
            await self._log_and_alert(failure, config)
            return None, failure
    
    async def _log_and_alert(self, failure: FailureReport, config: WatchdogConfig):
        """Log to Hivemind and alert launching agent."""
        
        # Create Hivemind handoff for failure tracking
        packet_id = await omega_hub_hivemind_submit_handoff(
            target_channel=self.launching_channel,
            target_entity=self.launching_entity,
            source_channel="watchdog",
            source_entity="subagent_watchdog",
            task=f"SUBAGENT FAILURE: {failure.failure_class.value}",
            context=f"Subagent {failure.subagent_id} failed: {failure.error_message}\n"
                    f"Thinking steps: {len(failure.thinking_trace)}\n"
                    f"Partial output: {failure.partial_output[:500]}...\n"
                    f"Retry: {failure.retry_recommendation}",
            priority=2  # Critical
        )
        failure.hivemind_packet_id = packet_id
        
        # Also log to SYSTEM_FAILURE_LOG (M23)
        await self._log_system_failure(failure)
        
        # Alert if configured
        if config.alert_on_failure:
            await self._alert_launching_agent(failure)
```

---

## 🎯 Failure Classification Logic

```python
def _classify_failure(error_message: str, thinking_trace: List, partial_output: str) -> FailureClass:
    """Classify failure based on error + context."""
    
    error_lower = error_message.lower()
    
    # M23 - Tool chain collapse
    if any(kw in error_lower for kw in ["websearch", "webfetch", "tool not found", "mandatory tool"]):
        return FailureClass.TOOL_CHAIN_COLLAPSE
    
    # M24 - Venv violation
    if "--break-system-packages" in error_lower or "system package" in error_lower:
        return FailureClass.VENV_VIOLATION
    
    # M25 - Streaming timeout
    if any(kw in error_lower for kw in ["chunk timeout", "stream timeout", "streaming"]):
        return FailureClass.STREAMING_TIMEOUT
    
    # M14 - Heritage violation
    if "[id-soft:]" in error_lower and "unvetted" in error_lower:
        return FailureClass.HERITAGE_VIOLATION
    
    # Resource exhaustion
    if any(kw in error_lower for kw in ["oom", "memory", "rate limit", "thermal", "429"]):
        return FailureClass.RESOURCE_EXHAUSTION
    
    # Generic timeout
    if "timeout" in error_lower:
        return FailureClass.TIMEOUT
    
    return FailureClass.UNKNOWN

def _retry_recommendation(failure_class: FailureClass, context: Dict) -> str:
    """Recommend retry strategy based on failure class."""
    
    strategies = {
        FailureClass.TIMEOUT: "retry_same",
        FailureClass.STREAMING_TIMEOUT: "retry_different_model",  # Nemotron → different provider
        FailureClass.RESOURCE_EXHAUSTION: "retry_different_model",  # Different provider/account
        FailureClass.VENV_VIOLATION: "abort",  # Fix code, don't retry
        FailureClass.TOOL_CHAIN_COLLAPSE: "abort",  # Fix infrastructure
        FailureClass.HERITAGE_VIOLATION: "abort",  # Fix vet record
        FailureClass.MANDATE_VIOLATION: "abort",  # Fix architecture
        FailureClass.UNKNOWN: "escalate",
    }
    return strategies.get(failure_class, "escalate")
```

---

## 📊 Hivemind Failure Dashboard

```python
# Watchdog creates these Hivemind entries for observability

FAILURE_HANDOFF_SCHEMA = {
    "packet_id": "uuid",
    "type": "subagent_failure",
    "subagent_id": "researcher_a1b2c3d4",
    "failure_class": "streaming_timeout",
    "thinking_steps_captured": 47,
    "partial_output_chars": 3241,
    "retry_recommendation": "retry_different_model",
    "timestamp": "2026-07-19T18:42:00Z",
    "launching_agent": "kali",
    "alert_level": "critical"
}
```

---

## 🚀 Integration Points

| Component | Integration |
|-----------|-------------|
| **Kali (launching agent)** | Receives `FailureReport` with full thinking trace |
| **Hivemind** | Failure handoffs for coordination + alerting |
| **M23 System Failure Log** | Automatic logging of `[TOOL-CHAIN-COLLAPSE]` etc. |
| **Mandate Enforcement** | Classifies M1-M25 violations automatically |
| **Omega-Vault** | Credential failures → `CREDENTIAL_ERROR` class |
| **Version Watchdog** | Subagent version mismatch → `VERSION_MISMATCH` class |

---

## 📝 Usage Pattern (For Kali)

```python
# Instead of raw task()
result, failure = await task_with_watchdog(
    subagent_type="researcher",
    description="Torment Phase 3",
    prompt="Deep research on Nameless One...",
    watchdog_config=WatchdogConfig(
        capture_thinking=True,
        auto_log_hivemind=True,
        alert_on_failure=True
    )
)

if failure:
    # Full visibility into what happened
    print(f"FAILED: {failure.failure_class.value}")
    print(f"Thinking steps: {len(failure.thinking_trace)}")
    print(f"Partial output: {failure.partial_output[:500]}")
    print(f"Hivemind packet: {failure.hivemind_packet_id}")
    print(f"Retry: {failure.retry_recommendation}")
    
    # Auto-retry if recommended
    if failure.retry_recommendation == "retry_different_model":
        result, failure = await task_with_watchdog(
            subagent_type="researcher",
            description="Torment Phase 3 (retry)",
            prompt=prompt + "\n\nPREVIOUS ATTEMPT FAILED: " + failure.error_message,
            watchdog_config=WatchdogConfig(...)
        )
```

---

## 🛡️ Mandate Compliance

| Mandate | Watchdog Enforcement |
|---------|---------------------|
| **M9 Error Integrity** | Typed, traceable failures with `trace_id` (hivemind packet) |
| **M11 Soul Integrity** | Failed sessions still produce `proposed_lessons.yaml` from thinking trace |
| **M15 Sovereign Continuity** | Thinking trace = session anchor for failed subagents |
| **M23 Failure Integrity** | `[TOOL-CHAIN-COLLAPSE]` auto-logged with full context |
| **M24 Venv Sovereignty** | `--break-system-packages` → `VENV_VIOLATION` class, auto-abort |
| **M25 Streaming Resilience** | Chunk timeout → `STREAMING_TIMEOUT` class, auto-retry different provider |

---

*⬡ OMEGA ⬡ KALI ⬡ mimo-v2.5-free ⬡ opencode ⬡ trc_watchdog ⬡ 2026-07-19*