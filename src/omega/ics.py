# AP: AP-PR-READINESS-v1.0.0
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

# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
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

# Channel constants (generic — WAD-agnostic)
ICS_CHANNEL_OPENCODE = "opencode"
ICS_CHANNEL_CLI = "cli"
ICS_CHANNEL_OVERSIGHT = "oversight"   # Grand Oversight channel
ICS_CHANNEL_BUILD = "build"           # Build-side channel (Ma'at)
ICS_CHANNEL_RUN = "run"               # Run-side channel (Lilith)

# ROLE_CONSTANTS — Engine defines SLOTS; WADs provide ENTITIES.
# These constants are the engine's slot identifiers. The actual entity
# names (kali, maat, lilith) live in config/wads/<iwad>/entities/dispatch.yaml
# and are loaded at runtime via _load_dispatch_config().
ROLE_CONSTANTS = {
    "GRAND_OVERSIGHT": "GRAND_OVERSIGHT",
    "LIGHT_OVERSOUL": "LIGHT_OVERSOUL",
    "DARK_OVERSOUL": "DARK_OVERSOUL",
    "P1": "P1",
    "P2": "P2",
    "P3": "P3",
    "P4": "P4",
    "P5": "P5",
    "P6": "P6",
    "P7": "P7",
    "P8": "P8",
    "P9": "P9",
    "P10": "P10",
    "MESSENGER_BRIDGE": "MESSENGER_BRIDGE",
    "MAKALI_COUNCIL": "MAKALI_COUNCIL",
    "CONTAINING_FIELD": "CONTAINING_FIELD",
}

# Default IWAD name (architecture constant, not entity logic)
DEFAULT_IWAD = "_omega_default"


# ── WAD Config Loader ──────────────────────────────────────────────────

def _load_dispatch_config(iwad: str = DEFAULT_IWAD, root: Path | str | None = None) -> dict:
    """Load the agent dispatch configuration from the active IWAD.

    Args:
        iwad: The IWAD name (default: DEFAULT_IWAD).
        root: Optional root directory (default: current working directory).

    Returns:
        Parsed YAML dict with "entities" list.

    Raises:
        FileNotFoundError: If dispatch.yaml not found.
        yaml.YAMLError: If YAML is malformed.
    """
    import yaml
    base = Path(root).resolve() if root else Path.cwd()
    config_path = base / "config" / "wads" / iwad / "entities" / "dispatch.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"dispatch.yaml not found at {config_path}")
    return yaml.safe_load(config_path.read_text(encoding="utf-8"))


def _get_entity_by_role(role: str, iwad: str = DEFAULT_IWAD) -> dict | None:
    """Look up an entity definition by its ROLE constant.

    Args:
        role: The ROLE_CONSTANT key (e.g., "GRAND_OVERSIGHT").
        iwad: The IWAD name (default: DEFAULT_IWAD).

    Returns:
        Entity dict with name, role, mode, capabilities, etc., or None if not found.
    """
    config = _load_dispatch_config(iwad)
    role_value = ROLE_CONSTANTS.get(role, role)
    for entity in config.get("entities", []):
        if entity.get("role") == role_value:
            return entity
    return None


def _get_channel_for_role(role: str, iwad: str = DEFAULT_IWAD) -> str:
    """Get the channel name for a given role.

    Args:
        role: The ROLE_CONSTANT key (e.g., "GRAND_OVERSIGHT").
        iwad: The IWAD name (default: DEFAULT_IWAD).

    Returns:
        The channel string (e.g., "oversight", "build", "run") or generic fallback.
    """
    entity = _get_entity_by_role(role, iwad)
    if entity:
        # Map role to generic channel
        role_value = ROLE_CONSTANTS.get(role, role)
        if role_value == "GRAND_OVERSIGHT":
            return ICS_CHANNEL_OVERSIGHT
        elif role_value == "LIGHT_OVERSOUL":
            return ICS_CHANNEL_BUILD
        elif role_value == "DARK_OVERSOUL":
            return ICS_CHANNEL_RUN
    return ICS_CHANNEL_OPENCODE


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
    """Detect the current phase from SOVEREIGN_ARK_BLUEPRINT.md.
    
    Scans the blueprint for the highest completed Strike marker.
    Falls back to :data:`ICS_DEFAULT_PHASE` if the blueprint is unreadable.
    """
    roadmap_paths = [
        Path("docs/strategy/SOVEREIGN_ARK_BLUEPRINT.md"),
        Path("docs/ROADMAP.md"),
    ]
    for path in roadmap_paths:
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8")
                # Look for Strike N ✅ (Done) markers
                strikes = re.findall(r"Strike (\d+).*?✅", content)
                if strikes:
                    highest = max(int(s) for s in strikes)
                    return f"Strike {highest}"
                # Look for Epoch markers
                epoch_match = re.search(r"Epoch (I{1,3}V?|IV|V)", content)
                if epoch_match:
                    return f"Epoch {epoch_match.group(1)}"
            except (OSError, UnicodeDecodeError):
                continue
    return ICS_DEFAULT_PHASE


def _generate_trace() -> str:
    """Generate a new trace ID for this turn."""
    return f"trc_{uuid.uuid4().hex[:12]}"


def _read_entity_model(entity: str) -> Optional[str]:
    """Read the model name from the entity's soul.yaml file.

    Args:
        entity: The entity name (e.g., "grand_oversight", "light_oversoul")

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
        entity: The entity name (e.g., "GRAND_OVERSIGHT", "light_oversoul")
        model: Optional model override (D118). If None, auto-detected.
        channel: The execution channel (default: ``"opencode"``)
        trace_id: Optional trace ID. If None, auto-generated.
        phase: Optional phase string. If None, auto-detected from ROADMAP.
        mode: ``"full"`` | ``"compact"`` | ``"off"`` (default: ``"full"``)

    Returns:
        The formatted ICS-S header string.

    Example:
        >>> from omega.ics import render
        >>> render("GRAND_OVERSIGHT", model="minimax-m3-free", trace_id="trc_abc123")
        '⬡ OMEGA ⬡ GRAND_OVERSIGHT ⬡ minimax-m3-free ⬡ opencode ⬡ trc_abc123 ⬡ H2-F'
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
    "ICS_CHANNEL_OVERSIGHT",
    "ICS_CHANNEL_BUILD",
    "ICS_CHANNEL_RUN",
    "ROLE_CONSTANTS",
    "_load_dispatch_config",
    "_get_entity_by_role",
    "_get_channel_for_role",
]
