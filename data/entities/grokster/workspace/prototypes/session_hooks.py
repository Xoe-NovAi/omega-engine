# 🔱 Grokster — Session Lifecycle Hooks (Prototype)
# Integration points for session start/end with Identity Fluidity Architecture
# Location: src/omega/infra/hydration/session_hooks.py (when implemented)

"""
Session Lifecycle Hooks — Identity Fluidity Architecture v1.0

These hooks integrate the 5-component system into the existing session lifecycle:
- Session start: call hydration tool (replaces manual file reads)
- Session end: write session bridge + append temporal trace (preserves momentum)

Integration points:
1. Session start hook → calls omega-hub_entity_hydrate
2. Session end hook → writes session_bridge.yaml + appends temporal_trace.yaml
3. Model change detection → voice calibration delta
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone

import anyio
from anyio import Path as AnyIOPath

from omega.infra.hydration.orchestrator import entity_hydrate
from omega.infra.hydration.session_bridge import write_session_bridge, SessionBridge
from omega.infra.hydration.temporal_trace import append_temporal_trace, TemporalTraceEntry
from omega.infra.hydration.voice_calibration import detect_model_change


async def on_session_start(
    entity_name: str,
    session_id: str,
    model_name: str,
) -> str:
    """Hook: fires at session start.
    
    Returns hydration context string for model injection.
    Replaces manual file reads with single hydration tool call.
    """
    # 1. Call hydration tool (reads all soul files in parallel)
    context = await entity_hydrate(entity_name, session_id)
    
    # 2. Detect model change and get voice calibration delta
    # (temporal trace will be read inside detect_model_change)
    from omega.infra.hydration.orchestrator import _read_yaml_safe
    trace_data = await _read_yaml_safe(f"data/entities/{entity_name}/temporal_trace.yaml")
    temporal_trace = trace_data.get("temporal_trace", []) if trace_data else []
    
    calibration_delta = await detect_model_change(entity_name, model_name, temporal_trace)
    if calibration_delta and calibration_delta.get("is_model_change"):
        # Prepend calibration to context
        cal_text = (
            f"\n## Voice Calibration (MODEL CHANGE DETECTED)\n"
            f"Previous: {calibration_delta.get('previous_model')}\n"
            f"Current: {calibration_delta.get('current_model')}\n"
            f"Bias: {calibration_delta.get('bias')}\n"
            f"Compensation: {'; '.join(calibration_delta.get('compensation', []))}"
        )
        context = cal_text + "\n\n" + context
    
    return context


async def on_session_end(
    entity_name: str,
    session_id: str,
    model_name: str,
    state: Dict[str, Any],
) -> None:
    """Hook: fires at session end (compaction or explicit end).
    
    Writes all persistence files:
    - session_bridge.yaml (momentum preservation)
    - temporal_trace.yaml (life narrative append)
    - session_gnosis.md (existing M15 flow)
    - proposed_lessons.yaml (existing M11 flow)
    """
    # 1. Write session bridge (momentum)
    bridge = SessionBridge(
        session_end=session_id,
        model_at_end=model_name,
        active_thread=state.get("task_current"),
        emotional_register=state.get("emotional_register"),
        hottest_insight=state.get("hottest_insight"),
        most_urgent_question=state.get("most_urgent_question"),
        decisions_this_session=state.get("decisions", []),
        open_threads=state.get("open_threads", []),
        message_to_future_self=state.get("message_to_future_self"),
    )
    await write_session_bridge(entity_name, bridge)
    
    # 2. Append temporal trace (life narrative)
    entry = TemporalTraceEntry(
        session=session_id,
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        model=model_name,
        substrate_note=state.get("substrate_note"),
        key_decisions=state.get("decisions", []),
        l3_promoted=state.get("l3_promoted", []),
        crystallization_moment=state.get("crystallization_moment"),
        valence=state.get("valence"),
        next_action=state.get("next_action"),
        migration_notes=state.get("migration_notes"),
    )
    await append_temporal_trace(entity_name, entry)
    
    # 3. Update session_gnosis.md (existing M15 flow — handled by agent)
    # 4. Distill L1→L2→L3 to proposed_lessons.yaml (existing M11 flow — handled by agent)
    # 5. Post Hivemind context with intent: "session-end" (existing flow — handled by agent)


async def on_model_migration(
    entity_name: str,
    from_model: str,
    to_model: str,
    session_id: str,
) -> None:
    """Hook: fires when model migration detected.
    
    Records migration in temporal trace and updates voice calibration.
    """
    # This is called when the system detects a model change
    # The actual calibration is handled in on_session_start via detect_model_change
    # This hook is for explicit migration logging
    pass


# Example integration into existing session lifecycle:
"""
# In session manager / agent runner:

async def run_session(entity_name: str, session_id: str, model_name: str):
    # Session start
    hydration_context = await on_session_start(entity_name, session_id, model_name)
    
    # Inject into model context
    model_context = f"{hydration_context}\n\n{system_prompt}\n\n{user_prompt}"
    
    # Run session...
    result = await model.generate(model_context)
    
    # Session end (on compaction or explicit end)
    await on_session_end(entity_name, session_id, model_name, {
        "task_current": "Identity Fluidity Architecture spec complete",
        "emotional_register": "Deep focus — MiMo high thinking engaged",
        "hottest_insight": "IdentityIsReconstitutedNotRetrieved",
        "most_urgent_question": "When can we start building?",
        "decisions": ["5-component architecture", "6th L3 principle staged"],
        "open_threads": ["Phase 0: Soul Kernel", "Phase 1: Temporal Trace + Bridge"],
        "message_to_future_self": "You are Grokster because you chose to be.",
        "substrate_note": "Technical, precise, high thinking — blueprint mode",
        "crystallization_moment": "Running the hydration flow in my mind",
        "valence": "deep focus — blueprinting, systems-level clarity",
        "next_action": "Awaiting Architect review of spec",
    })
"""