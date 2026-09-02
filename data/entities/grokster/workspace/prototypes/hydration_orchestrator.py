# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Grokster — Hydration Orchestrator (Prototype)
# Core hydration logic. Reads all soul files in parallel, assembles HydrationContext.
# Uses AnyIO for async file operations. Returns structured context for model injection.
# Location: src/omega/infra/hydration/orchestrator.py (when implemented)

"""
Hydration Orchestrator — Identity Fluidity Architecture v1.0

This module provides the core hydration logic for sovereign entities.
It reads all soul files in parallel using AnyIO task groups, assembles
a HydrationContext, and returns it for model context injection.

Design principles:
- Parallel reads (latency = slowest file, not sum)
- Graceful degradation (missing/corrupted files → warnings, not crashes)
- Structured output (HydrationContext dataclass)
- Compact context string for model injection (~200 tokens)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any
from datetime import datetime, timezone
import logging
import os

import anyio
from anyio import Path as AnyIOPath

logger = logging.getLogger("omega.hydration")


@dataclass
class HydrationContext:
    """Assembled entity context for model injection."""
    soul_yaml: Optional[dict] = None
    session_gnosis: Optional[str] = None
    proposed_lessons: Optional[List[dict]] = None
    temporal_trace_latest: Optional[dict] = None
    session_bridge: Optional[dict] = None
    hivemind_continuation: Optional[str] = None
    voice_calibration: Optional[dict] = None
    warnings: List[str] = field(default_factory=list)

    def to_context_string(self) -> str:
        """Compact string for model context injection (~200 tokens)."""
        parts = []
        
        if self.soul_yaml:
            e = self.soul_yaml.get("entity", {})
            parts.append(
                f"## Hydrated Identity: {e.get('name', 'Unknown')}\n"
                f"Role: {e.get('hmc_role', 'Unknown')}\n"
                f"Archetype: {e.get('archetype', 'Unknown')}"
            )
        
        if self.proposed_lessons:
            l3s = [p.get("l3_principle", "").split(":")[0].strip("*") 
                   for p in self.proposed_lessons 
                   if p.get("l3_principle")]
            if l3s:
                parts.append(
                    f"## Active L3 Principles ({len(l3s)})\n" + 
                    "\n".join(f"- {l}" for l in l3s)
                )
        
        if self.temporal_trace_latest:
            t = self.temporal_trace_latest
            parts.append(
                f"## Latest Session: {t.get('date', '?')}\n"
                f"Model: {t.get('model', '?')}\n"
                f"Decisions: {', '.join(t.get('key_decisions', []))}\n"
                f"Valence: {t.get('valence', '?')}"
            )
        
        if self.session_bridge:
            b = self.session_bridge
            parts.append(
                f"## Session Bridge\n"
                f"Thread: {b.get('active_thread', '?')}\n"
                f"Insight: {b.get('hottest_insight', '?')}\n"
                f"Message: {b.get('message_to_future_self', '?')}"
            )
        
        if self.hivemind_continuation:
            parts.append(
                f"## Hivemind Continuation\n{self.hivemind_continuation}"
            )
        
        if self.voice_calibration and self.voice_calibration.get("is_model_change"):
            vc = self.voice_calibration
            parts.append(
                f"## Voice Calibration (NEW MODEL)\n"
                f"Bias: {vc.get('bias', '?')}\n"
                f"Compensation: {'; '.join(vc.get('compensation', []))}"
            )
        
        if self.warnings:
            parts.append(
                f"## Hydration Warnings\n" + 
                "\n".join(f"- {w}" for w in self.warnings)
            )
        
        return "\n\n".join(parts)


async def _read_yaml_safe(path: str) -> Optional[dict]:
    """Read a YAML file safely, returning None on any error."""
    try:
        p = AnyIOPath(path)
        if not await p.exists():
            return None
        text = await p.read_text()
        import yaml
        return yaml.safe_load(text)
    except Exception as e:
        logger.warning(f"Failed to read {path}: {e}")
        return None


async def _read_text_safe(path: str) -> Optional[str]:
    """Read a text file safely, returning None on any error."""
    try:
        p = AnyIOPath(path)
        if not await p.exists():
            return None
        return await p.read_text()
    except Exception as e:
        logger.warning(f"Failed to read {path}: {e}")
        return None


async def entity_hydrate(
    entity_name: str,
    session_id: Optional[str] = None,
    include_full_gnosis: bool = False,
) -> HydrationContext:
    """Hydrate an entity by reading all soul files in parallel.
    
    This is the core hydration orchestrator. It reads all soul files
    concurrently using AnyIO task groups, assembles a HydrationContext,
    and returns it for model injection.
    
    File resolution:
        data/entities/{entity_name}/soul.yaml
        data/entities/{entity_name}/session_gnosis.md
        data/entities/{entity_name}/proposed_lessons.yaml
        data/entities/{entity_name}/temporal_trace.yaml
        data/entities/{entity_name}/session_bridge.yaml
        data/entities/{entity_name}/voice_calibrations.yaml
    
    Args:
        entity_name: Entity to hydrate (e.g., "grokster")
        session_id: Optional session ID for temporal trace linkage
        include_full_gnosis: If True, return full session_gnosis.md text
    
    Returns:
        HydrationContext with all available data populated
    """
    base = f"data/entities/{entity_name}"
    warnings = []
    context = HydrationContext()
    
    # ── Parallel file reads ──────────────────────────────────────────
    soul_yaml = None
    session_gnosis_text = None
    proposed_lessons = None
    temporal_trace = None
    session_bridge = None
    voice_calibrations = None
    
    async with anyio.create_task_group() as tg:
        
        async def _read_soul():
            nonlocal soul_yaml
            result = await _read_yaml_safe(f"{base}/soul.yaml")
            if result is None:
                warnings.append(f"soul.yaml not found or unreadable")
            soul_yaml = result
        
        async def _read_gnosis():
            nonlocal session_gnosis_text
            result = await _read_text_safe(f"{base}/session_gnosis.md")
            if result is None:
                warnings.append(f"session_gnosis.md not found or unreadable")
            session_gnosis_text = result
        
        async def _read_lessons():
            nonlocal proposed_lessons
            result = await _read_yaml_safe(f"{base}/proposed_lessons.yaml")
            if result and "proposals" in result:
                proposed_lessons = result["proposals"]
            else:
                proposed_lessons = []
        
        async def _read_trace():
            nonlocal temporal_trace
            result = await _read_yaml_safe(f"{base}/temporal_trace.yaml")
            if result and "temporal_trace" in result:
                temporal_trace = result["temporal_trace"]
            else:
                temporal_trace = []
        
        async def _read_bridge():
            nonlocal session_bridge
            result = await _read_yaml_safe(f"{base}/session_bridge.yaml")
            session_bridge = result
        
        async def _read_voice():
            nonlocal voice_calibrations
            result = await _read_yaml_safe(f"{base}/voice_calibrations.yaml")
            voice_calibrations = result
        
        tg.start_soon(_read_soul)
        tg.start_soon(_read_gnosis)
        tg.start_soon(_read_lessons)
        tg.start_soon(_read_trace)
        tg.start_soon(_read_bridge)
        tg.start_soon(_read_voice)
    
    # ── Assemble context ─────────────────────────────────────────────
    context.soul_yaml = soul_yaml
    context.warnings = warnings
    
    # Session gnosis: summary or full
    if session_gnosis_text:
        if include_full_gnosis:
            context.session_gnosis = session_gnosis_text
        else:
            # Extract key sections (first 500 chars of "What I Know" section)
            lines = session_gnosis_text.split("\n")
            summary_lines = []
            capture = False
            for line in lines:
                if "## 🧠 What I Know" in line:
                    capture = True
                    continue
                if capture and line.startswith("## "):
                    break
                if capture:
                    summary_lines.append(line)
            context.session_gnosis = "\n".join(summary_lines)[:500] if summary_lines else session_gnosis_text[:500]
    
    # Proposed lessons: only staged (not promoted)
    if proposed_lessons:
        context.proposed_lessons = [
            {
                "l3_principle": p.get("l3_principle", "").strip(),
                "confidence": p.get("confidence", 0.0),
                "tags": p.get("tags", []),
            }
            for p in proposed_lessons
            if not p.get("promoted", False)
        ]
    
    # Temporal trace: latest entry only
    if temporal_trace:
        context.temporal_trace_latest = temporal_trace[-1]
    
    # Session bridge: pass through
    context.session_bridge = session_bridge
    
    # Voice calibration: detect model change
    current_model = _detect_current_model()
    if voice_calibrations and current_model:
        calibrations = voice_calibrations.get("voice_calibrations", {})
        # Exact match
        if current_model in calibrations:
            context.voice_calibration = {**calibrations[current_model], "is_model_change": False}
        else:
            # Partial match
            for key in calibrations:
                if key in current_model or current_model in key:
                    context.voice_calibration = {**calibrations[key], "is_model_change": False}
                    break
        
        # Check if model changed from last session
        last_model = _get_last_model(temporal_trace)
        if last_model and last_model != current_model:
            if context.voice_calibration is None:
                context.voice_calibration = {}
            context.voice_calibration["is_model_change"] = True
            context.voice_calibration["previous_model"] = last_model
            context.voice_calibration["current_model"] = current_model
    
    # Hivemind continuation: read from coordination directory
    # (In production, this would call hivemind_get_continuation)
    # For now, extract from session_gnosis if available
    
    return context


def _detect_current_model() -> Optional[str]:
    """Detect the current model from environment or session context."""
    return os.environ.get("OMEGA_SESSION_MODEL", None)


def _get_last_model(temporal_trace: Optional[List[dict]]) -> Optional[str]:
    """Get the model from the most recent temporal trace entry."""
    if not temporal_trace:
        return None
    return temporal_trace[-1].get("model")