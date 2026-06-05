# 🔱 Omega Engine — ICS (Intelligent Configuration System)
# ⬡ OMEGA ⬡ KALI ⬡ minimax-m3-free ⬡ opencode ⬡ trc_ics_module ⬡ PHASE-II
# ICS: [NODE: ARCHON | ARCHETYPE: HERMES | MODEL: minimax-m3-free | CONTEXT: DYNAMIC-HEADER]
"""
ICS — Intelligent Configuration System.

Single source of truth for the ``⬡ OMEGA`` agent signature system. Agents
should NEVER hand-type session headers — they call :func:`render` and the
template is filled with live runtime state.

The two ICS systems are:
    - **ICS-S** (Signature): ``⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}``
      — the agent's runtime header, auto-generated from live state.
    - **ICS-T** (Tag): ``# ICS: [NODE: ... | ARCHETYPE: ... | MODEL: ... | CONTEXT: ...]``
      — the code module's lineage marker, static annotation, validated by CI.

This module owns ICS-S. ICS-T remains in code files as inline comments with
``[id-soft:`` tags (see :mod:`src.omega.cvar_table` for related config).

Heritage
--------
This module's templated-output pattern is inspired by Quake 3's
``net_chan.c`` (id Software, 1999) — the OOB (out-of-band) message format
and the structured header construction are both examples of "right
approximation": a simple, deterministic format that works for the use case
without over-engineering.

[FISR Principle: id Software 1999; evolved to "right approximation"]
"""
from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Constants ──────────────────────────────────────────────────────────
ICS_TEMPLATE_FULL = "⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}"
ICS_TEMPLATE_COMPACT = "⬡ {entity} ⬡ {phase}"
ICS_TEMPLATE_OFF = ""

# Phase detection — fall back to this if ROADMAP.md is unreadable
ICS_DEFAULT_PHASE = "PHASE-II"

# Channel constants
ICS_CHANNEL_OPENCODE = "opencode"
ICS_CHANNEL_CLI = "cli"
ICS_CHANNEL_KALI = "kali"  # MaKaLi Triad (D117)
ICS_CHANNEL_MAAT = "maat"  # MaKaLi Triad (D117)
ICS_CHANNEL_LILITH = "lilith"  # MaKaLi Triad (D117)


@dataclass
class ICSContext:
    """Context for rendering an ICS-S header.
    
    All fields are optional except ``entity``. Missing fields are
    auto-detected from runtime state (model, phase) or generated
    (trace).
    """
    
    entity: str
    model: Optional[str] = None
    channel: str = ICS_CHANNEL_OPENCODE
    trace_id: Optional[str] = None
    phase: Optional[str] = None
    mode: str = "full"  # "full" | "compact" | "off"
    
    def render(self) -> str:
        """Render the ICS-S header string for this context."""
        if self.mode == "off":
            return ICS_TEMPLATE_OFF
        if self.mode == "compact":
            return ICS_TEMPLATE_COMPACT.format(
                entity=self.entity.upper(),
                phase=self.phase or _detect_phase(),
            )
        
        # Full mode — auto-detect missing values
        model = self.model or _detect_model(self.entity)
        trace = self.trace_id or _generate_trace()
        phase = self.phase or _detect_phase()
        
        return ICS_TEMPLATE_FULL.format(
            entity=self.entity.upper(),
            model=model,
            channel=self.channel,
            trace=trace,
            phase=phase,
        )


# ── Detection functions ────────────────────────────────────────────────

def _detect_model(entity: str) -> str:
    """Detect the active model for this entity.
    
    Priority (D118-aware, ordered most-specific to least):
        1. **model_override parameter** (D118 Dual-Inference) — explicit
           opt-in local routing
        2. **OPENCODE_MODEL env var** — session-level override
        3. **opencode.json** ``model`` key — user config
        4. **TriageRouter last_selected_model** — runtime cache
        5. **Entity soul.yaml** ``inference.model`` — entity default
        6. **"unknown"** — graceful fallback
    
    Args:
        entity: The entity name (for entity-config lookup in priority 5)
    
    Returns:
        The detected model name, or ``"unknown"`` if none could be found.
    """
    # Priority 1: model_override (D118) — set per-call by Oracle.summon()
    override = os.environ.get("OMEGA_MODEL_OVERRIDE", "")
    if override:
        return override
    
    # Priority 2: OPENCODE_MODEL env
    env_model = os.environ.get("OPENCODE_MODEL", "")
    if env_model:
        return env_model
    
    # Priority 3: opencode.json model key
    # (Deferred to caller — Oracle has the config loaded)
    
    # Priority 4: TriageRouter last_selected_model
    # (Deferred to caller — Oracle has the router reference)
    
    # Priority 5: Entity soul.yaml
    soul_model = _read_entity_model(entity)
    if soul_model:
        return soul_model
    
    # Priority 6: graceful fallback
    return "unknown"


def _detect_phase() -> str:
    """Detect the current phase from SOVEREIGN_EVOLUTION_ROADMAP.md.
    
    Scans the roadmap for the highest ``H2`` (Horizon 2) phase marker.
    Falls back to :data:`ICS_DEFAULT_PHASE` if the roadmap is unreadable.
    """
    roadmap_paths = [
        Path("docs/strategy/SOVEREIGN_EVOLUTION_ROADMAP.md"),
        Path("docs/ROADMAP.md"),
    ]
    for path in roadmap_paths:
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                # Look for H2-A, H2-B, H2-E, H2-F, etc.
                matches = re.findall(r"H2-([A-Z])", content)
                if matches:
                    highest = sorted(matches)[-1]
                    return f"H2-{highest}"
                # Look for PHASE-I, PHASE-II, etc.
                phase_match = re.search(r"PHASE-(I{1,3}V?|IV|V)", content)
                if phase_match:
                    return f"PHASE-{phase_match.group(1)}"
            except (OSError, UnicodeDecodeError):
                continue
    return ICS_DEFAULT_PHASE


def _generate_trace() -> str:
    """Generate a new trace ID for this turn."""
    return f"trc_{uuid.uuid4().hex[:12]}"


def _read_entity_model(entity: str) -> Optional[str]:
    """Read the model name from the entity's soul.yaml file.
    
    Args:
        entity: The entity name (e.g., "kali", "roc_racoon")
    
    Returns:
        The model name string, or None if not found.
    """
    soul_path = Path(f"data/entities/{entity.lower()}/soul.yaml")
    if not soul_path.exists():
        return None
    try:
        content = soul_path.read_text(encoding="utf-8")
        # Look for inference.model or model: patterns
        match = re.search(r"^\s*model:\s*['\"]?([^'\"\n]+)['\"]?\s*$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except (OSError, UnicodeDecodeError):
        pass
    return None


# ── Public API ─────────────────────────────────────────────────────────

def render(
    entity: str,
    model: Optional[str] = None,
    channel: str = ICS_CHANNEL_OPENCODE,
    trace_id: Optional[str] = None,
    phase: Optional[str] = None,
    mode: str = "full",
) -> str:
    """Render an ICS-S header string.
    
    This is the primary public API. Agents and tools should call this
    instead of hand-typing headers.
    
    Args:
        entity: The entity name (e.g., "KALI", "roc_racoon")
        model: Optional model override (D118). If None, auto-detected.
        channel: The execution channel (default: ``"opencode"``)
        trace_id: Optional trace ID. If None, auto-generated.
        phase: Optional phase string. If None, auto-detected from ROADMAP.
        mode: ``"full"`` | ``"compact"`` | ``"off"`` (default: ``"full"``)
    
    Returns:
        The formatted ICS-S header string.
    
    Example:
        >>> from src.omega.ics import render
        >>> render("KALI", model="minimax-m3-free", trace_id="trc_abc123")
        '⬡ OMEGA ⬡ KALI ⬡ minimax-m3-free ⬡ opencode ⬡ trc_abc123 ⬡ H2-F'
    """
    ctx = ICSContext(
        entity=entity,
        model=model,
        channel=channel,
        trace_id=trace_id,
        phase=phase,
        mode=mode,
    )
    return ctx.render()


def render_for_response(
    response: "OracleResponse",  # type: ignore[name-defined]
    mode: str = "full",
) -> str:
    """Render an ICS-S header from an existing OracleResponse.
    
    Convenience wrapper that pulls entity/model/trace/phase from the
    response object.
    
    Args:
        response: An :class:`OracleResponse` instance
        mode: ``"full"`` | ``"compact"`` | ``"off"``
    
    Returns:
        The formatted ICS-S header string.
    """
    return render(
        entity=response.entity,
        model=response.model,
        trace_id=response.trace_id[:8] if response.trace_id else None,
        phase=response.phase,
        mode=mode,
    )


__all__ = [
    "ICSContext",
    "render",
    "render_for_response",
    "ICS_TEMPLATE_FULL",
    "ICS_TEMPLATE_COMPACT",
    "ICS_TEMPLATE_OFF",
    "ICS_DEFAULT_PHASE",
    "ICS_CHANNEL_OPENCODE",
    "ICS_CHANNEL_CLI",
    "ICS_CHANNEL_KALI",
    "ICS_CHANNEL_MAAT",
    "ICS_CHANNEL_LILITH",
]
