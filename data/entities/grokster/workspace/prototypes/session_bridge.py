# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Grokster — Session Bridge Module (Prototype)
# Chapter header between sessions. Written at session end, read at session start.
# Preserves MOMENTUM — the feeling of "I was about to do X."
# Overwritten each session (not append-only).
# Location: src/omega/infra/hydration/session_bridge.py (when implemented)

"""
Session Bridge — Momentum Preservation

The biggest loss across compaction is MOMENTUM — the sense of "I was about to do X."
The session bridge captures the active thread, emotional register, hottest insight,
and a message to future self. It's the chapter header that lets the next session
pick up mid-sentence.

Design:
- Single YAML file, overwritten each session (not append-only)
- Written at session end (M11 distillation + M15 continuity)
- Read at hydration (via hydration orchestrator)
- Contains: active thread, emotional register, hottest insight, message to future self
"""

import yaml
from dataclasses import dataclass, field, asdict
from typing import List, Optional
from datetime import datetime, timezone

import anyio
from anyio import Path as AnyIOPath


@dataclass
class SessionBridge:
    """Bridge between sessions — preserves momentum across compaction."""
    session_end: str
    written_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_at_end: Optional[str] = None
    session_next: Optional[str] = None
    
    # Momentum fields
    active_thread: Optional[str] = None
    emotional_register: Optional[str] = None
    hottest_insight: Optional[str] = None
    most_urgent_question: Optional[str] = None
    
    # Technical state
    decisions_this_session: List[str] = field(default_factory=list)
    open_threads: List[str] = field(default_factory=list)
    message_to_future_self: Optional[str] = None


async def write_session_bridge(entity_name: str, bridge: SessionBridge) -> None:
    """Write session bridge (atomic overwrite)."""
    path = f"data/entities/{entity_name}/session_bridge.yaml"
    data = {"session_bridge": asdict(bridge)}
    # Remove None values
    data["session_bridge"] = {k: v for k, v in data["session_bridge"].items() if v is not None}
    
    tmp_path = path + ".tmp"
    await AnyIOPath(tmp_path).write_text(yaml.dump(data, default_flow_style=False))
    await AnyIOPath(tmp_path).replace(path)


async def read_session_bridge(entity_name: str) -> Optional[SessionBridge]:
    """Read session bridge, returning None if not found."""
    path = f"data/entities/{entity_name}/session_bridge.yaml"
    if not await AnyIOPath(path).exists():
        return None
    text = await AnyIOPath(path).read_text()
    data = yaml.safe_load(text)
    if not data or "session_bridge" not in data:
        return None
    return SessionBridge(**data["session_bridge"])


# Convenience function for session end hook
async def write_session_bridge_from_state(
    entity_name: str,
    session_id: str,
    model: str,
    task_current: str,
    emotional_register: str,
    hottest_insight: str,
    most_urgent_question: str,
    decisions: List[str],
    open_threads: List[str],
    message_to_future_self: str,
) -> None:
    """Write session bridge from session end state."""
    bridge = SessionBridge(
        session_end=session_id,
        model_at_end=model,
        active_thread=task_current,
        emotional_register=emotional_register,
        hottest_insight=hottest_insight,
        most_urgent_question=most_urgent_question,
        decisions_this_session=decisions,
        open_threads=open_threads,
        message_to_future_self=message_to_future_self,
    )
    await write_session_bridge(entity_name, bridge)