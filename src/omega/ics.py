# AP: AP-PR-READINESS-v1.0.0
# 🔱 Omega Engine — ICS (Intelligent Configuration System)
# ⬡ OMEGA ⬡ KALI ⬡ minimax-m3-free ⬡ opencode ⬡ trc_ics_module ⬡ PHASE-II
"""
ICS — Intelligent Configuration System.

Single source of truth for the ``⬡ OMEGA`` agent signature system. Agents
should NEVER hand-type session headers — they call :func:`render` and the
template is filled with live runtime state.

The ICS system is:
    - **ICS-S** (Signature): ``⬡ OMEGA ⬡ [{node}] ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase} ⬡ {session_id}``
      — the agent's runtime header, auto-generated from live state.
      ``[{node}]`` (PP-4) renders only when the agent acts under a Node;
      ``{session_id}`` (P5) renders only when provided.

    (ICS-T code tags were DEPRECATED and REMOVED per Carmack review —
    final remnants purged 2026-08-22. Do not reintroduce.)

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
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, TYPE_CHECKING
import logging

# ── TYPE_CHECKING block for forward references ──
if TYPE_CHECKING:
    from omega.oracle.oracle import OracleResponse

logger = logging.getLogger(__name__)

# ── Constants ──────────────────────────────────────────────────────────
ICS_TEMPLATE_FULL = "⬡ OMEGA ⬡ {entity} ⬡ {model} ⬡ {channel} ⬡ {trace} ⬡ {phase}"
ICS_TEMPLATE_COMPACT = "⬡ {entity} ⬡ {phase}"
ICS_TEMPLATE_OFF = ""

# Phase detection — fall back to this if ROADMAP.md is unreadable
ICS_DEFAULT_PHASE = "PHASE-II"

# Channel constants (generic — WAD-agnostic)
ICS_CHANNEL_OPENCODE = "opencode"
ICS_CHANNEL_CLI = "cli"
ICS_CHANNEL_OVERSIGHT = "oversight"  # Grand Oversight channel
ICS_CHANNEL_BUILD = "build"  # Build-side channel (Ma'at)
ICS_CHANNEL_RUN = "run"  # Run-side channel (Lilith)

# ROLE_CONSTANTS — Engine defines SLOTS; WADs provide ENTITIES.
# These constants are the engine's slot identifiers. The actual entity
# names (kali, maat, lilith) live in config/wads/<iwad>/entities/dispatch.yaml
# and are loaded at runtime via _load_dispatch_config().
ROLE_CONSTANTS = {
    "GRAND_OVERSIGHT": "GRAND_OVERSIGHT",
    "BUILD_OVERSOUL": "BUILD_OVERSOUL",
    "RUNTIME_OVERSOUL": "RUNTIME_OVERSOUL",
    "N1": "N1",
    "N2": "N2",
    "N3": "N3",
    "N4": "N4",
    "N5": "N5",
    "N6": "N6",
    "N7": "N7",
    "N8": "N8",
    "N9": "N9",
    "N10": "N10",
    "MESSENGER_BRIDGE": "MESSENGER_BRIDGE",
    "MAKALI_COUNCIL": "MAKALI_COUNCIL",
    "CONTAINING_FIELD": "CONTAINING_FIELD",
}

# Default IWAD name (architecture constant, not entity logic)
DEFAULT_IWAD = "_omega_default"


# ── WAD Config Loader ──────────────────────────────────────────────────
# Delegates to dispatch_registry — single source of truth (FS-Β2 / A6-A7).
# Fixes cwd-relative path bug in original _load_dispatch_config.

from omega.governance.dispatch_registry import load_dispatch_yaml, get_entity_by_role
from omega.memory.providers import sanitize_path_component


def _load_dispatch_config(iwad: str = DEFAULT_IWAD, root: Path | str | None = None) -> dict:
    """Load the agent dispatch configuration from the active IWAD.

    Args:
        iwad: The IWAD name (default: DEFAULT_IWAD).
        root: DEPRECATED — kept for signature compatibility. Ignored.
              Path resolution now uses WADS_DIR from config_resolver (M2 Firewall).

    Returns:
        Parsed YAML dict with "entities" list.

    Raises:
        FileNotFoundError: If dispatch.yaml not found.
        yaml.YAMLError: If YAML is malformed.
    """
    return load_dispatch_yaml(iwad)


def _get_entity_by_role(role: str, iwad: str = DEFAULT_IWAD) -> dict | None:
    """Look up an entity definition by its ROLE constant.

    Args:
        role: The ROLE_CONSTANT key (e.g., "GRAND_OVERSIGHT").
        iwad: The IWAD name (default: DEFAULT_IWAD).

    Returns:
        Entity dict with name, role, mode, capabilities, etc., or None if not found.
    """
    return get_entity_by_role(role, iwad)


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
        elif role_value == "BUILD_OVERSOUL":
            return ICS_CHANNEL_BUILD
        elif role_value == "RUNTIME_OVERSOUL":
            return ICS_CHANNEL_RUN
    return ICS_CHANNEL_OPENCODE


@dataclass
class ICSContext:
    """Context for rendering an ICS-S header.

    All fields are optional except ``entity``. Missing fields are
    auto-detected from runtime state (model, phase) or generated
    (trace).

    ``node`` (PP-4, 2026-08-22): Node designation when the agent acts
        under a Node expert session (e.g., ``"N7"``). Rendered as
        ``[N7]`` immediately after the entity. Provenance for shared-
        file writes (soul, gnosis) made by Node-acting agents.
    ``session_id`` (P5, 2026-08-22): OpenCode session ID rendered as a
        trailing segment; also scopes the session-DB model lookup so
        multi-instance environments detect the CORRECT model (B1 fix).
    """

    entity: str
    model: Optional[str] = None
    channel: str = ICS_CHANNEL_OPENCODE
    trace_id: Optional[str] = None
    phase: Optional[str] = None
    mode: str = "full"  # "full" | "compact" | "off"
    node: Optional[str] = None
    session_id: Optional[str] = None

    def render(self) -> str:
        """Render the ICS-S header string for this context."""
        if self.mode == "off":
            return ICS_TEMPLATE_OFF
        if self.mode == "compact":
            entity_upper = self.entity.upper()
            segments = [entity_upper]
            if self.node:
                sanitized_node = re.sub(r"[^A-Z0-9_-]", "", self.node.upper())
                if sanitized_node:
                    segments.append(f"[{sanitized_node}]")
            segments.append(self.phase or _detect_phase())
            return "⬡ " + " ⬡ ".join(segments)

        # Full mode — auto-detect missing values
        model = self.model or _detect_model(self.entity, session_id=self.session_id)
        trace = self.trace_id or _generate_trace()
        phase = self.phase or _detect_phase()

        # Build header from segments (F1 fix: robust node insertion, sanitized)
        entity_upper = self.entity.upper()
        segments = [
            "OMEGA",
            entity_upper,
        ]
        # F1 fix: sanitize node value, insert after entity
        if self.node:
            sanitized_node = re.sub(r"[^A-Z0-9_-]", "", self.node.upper())
            if sanitized_node:
                segments.append(f"[{sanitized_node}]")
        segments.extend([
            model,
            self.channel,
            trace,
            phase,
        ])
        header = "⬡ " + " ⬡ ".join(segments)

        # P5: session ID as trailing segment
        if self.session_id:
            header = f"{header} ⬡ {self.session_id}"

        return header


# ── Detection functions ────────────────────────────────────────────────


def _detect_model(entity: str, session_id: Optional[str] = None) -> str:
    """Detect the active model for this entity.

    Priority (D118-aware, ordered most-specific to least):
        1. **model_override parameter** (D118 Dual-Inference) — explicit
           opt-in local routing
        2. **OPENCODE_MODEL env var** — session-level override
        3. **OpenCode session DB** — authoritative live model, scoped to
           ``session_id`` when provided (B1 fix: global-latest lookup
           returns WRONG models in multi-instance environments)
        4. **Entity soul.yaml** ``inference.model`` — entity default
        5. **"unknown"** — graceful fallback

    Args:
        entity: The entity name (for entity-config lookup in priority 4)
        session_id: Optional OpenCode session ID scoping the DB lookup

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

    # Priority 3: OpenCode session DB — authoritative live model.
    # Scoped to session_id when provided (B1 fix, 2026-08-22); the old
    # global-latest query crossed instance boundaries in multi-window
    # environments. Former TriageRouter/opencode.json priorities were
    # caller-deferred and removed with the router (D-536).
    db_model = _read_opencode_session_model(session_id=session_id)
    if db_model:
        return db_model

    # Priority 4: Entity soul.yaml — M22 provenance: log fallback
    import warnings
    warnings.warn(
        f"ICS model detection: DB lookup failed for entity '{entity}' "
        f"(session_id={session_id}); falling back to soul.yaml. "
        f"Header may show stale model. Set OPENCODE_MODEL or OMEGA_MODEL_OVERRIDE "
        f"to pin explicitly.",
        RuntimeWarning,
        stacklevel=2,
    )
    soul_model = _read_entity_model(entity)
    if soul_model:
        return soul_model

    # Priority 5: graceful fallback
    return "unknown"


def _detect_phase() -> str:
    """Detect the current phase.

    Priority (2026-08-22, B2 fix):
        1. ``data/coordination/ACTIVE_SPRINT.json`` ``.phase`` — Tier-0
           tracker (M27), always current
        2. Legacy blueprint scan ("Strike N ✅" / "Epoch" markers)
        3. :data:`ICS_DEFAULT_PHASE` fallback
    """
    # Priority 1: ACTIVE_SPRINT.json — single execution SSOT
    root = os.environ.get("OMEGA_ENGINE_ROOT", "")
    base = Path(root) if root else Path.cwd()
    sprint_path = base / "data" / "coordination" / "ACTIVE_SPRINT.json"
    if sprint_path.exists():
        try:
            import json

            data = json.loads(sprint_path.read_text(encoding="utf-8"))
            phase = data.get("phase")
            if phase:
                return str(phase)
        except (OSError, ValueError) as exc:
            logger.debug("ICS phase: ACTIVE_SPRINT.json unreadable (%s); falling back", exc)

    # Priority 2: legacy roadmap scan (B3 fix: use root resolution)
    root = os.environ.get("OMEGA_ENGINE_ROOT", "")
    base = Path(root) if root else Path.cwd()
    roadmap_paths = [
        base / "docs" / "strategy" / "SOVEREIGN_ARK_BLUEPRINT.md",
        base / "docs" / "ROADMAP.md",
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
            except (OSError, UnicodeDecodeError) as exc:
                logger.debug("ICS phase: roadmap %s unreadable (%s)", path.name, exc)
                continue
    return ICS_DEFAULT_PHASE


def _generate_trace() -> str:
    """Generate a new trace ID for this turn."""
    return f"trc_{uuid.uuid4().hex[:12]}"


def _read_entity_model(entity: str) -> Optional[str]:
    """Read the model name from the entity's soul.yaml file.

    Path resolution (M16 portability, B3 fix): honors
    ``OMEGA_ENGINE_ROOT`` env var when set; otherwise assumes CWD is the
    repo root (historical behavior).

    Args:
        entity: The entity name (e.g., "grand_oversight", "build_oversoul")

    Returns:
        The model name string, or None if not found.
    """
    root = os.environ.get("OMEGA_ENGINE_ROOT", "")
    base = Path(root) if root else Path.cwd()
    soul_path = base / "data" / "entities" / sanitize_path_component(entity) / "soul.yaml"
    if not soul_path.exists():
        return None
    try:
        content = soul_path.read_text(encoding="utf-8")
        # Look for inference.model or model: patterns
        match = re.search(r"^\s*model:\s*['\"]?([^'\"\n]+)['\"]?\s*$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except (OSError, UnicodeDecodeError) as exc:
        logger.debug("ICS model: soul.yaml for %s unreadable (%s)", entity, exc)
    return None


def _read_opencode_session_model(session_id: Optional[str] = None) -> Optional[str]:
    """Read the active model from the OpenCode session DB.

    The OpenCode session DB stores the authoritative model in
    ``session.model`` as JSON: {"id": "...", "providerID": "...", ...}.

    Args:
        session_id: When provided, look up THIS session only (B1 fix —
            the previous global-latest query crossed instance boundaries
            in multi-window environments and returned wrong models).
            When None, falls back to most-recently-updated session.

    Returns:
        The model id string (e.g. "deepseek/deepseek-v4-flash-0731"),
        or None if the DB is unreachable or has no matching session.
    """
    # XDG_DATA_HOME support (M16 portability) — opencode honors it
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        db_path = Path(xdg) / "opencode" / "opencode.db"
    else:
        db_path = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
    if not db_path.exists():
        return None
    try:
        import sqlite3

        # Short timeout + busy_timeout to avoid blocking event loop (M1)
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=0.25)
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA busy_timeout=100")  # 100ms max wait on lock
            if session_id:
                cur.execute(
                    "SELECT model FROM session WHERE id = ? ORDER BY time_updated DESC LIMIT 1",
                    (session_id,),
                )
            else:
                cur.execute("SELECT model FROM session ORDER BY time_updated DESC LIMIT 1")
            row = cur.fetchone()
            if row and row[0]:
                import json

                data = json.loads(row[0])
                model_id = data.get("id")
                if model_id:
                    return model_id
        finally:
            conn.close()
    except (sqlite3.Error, OSError, ValueError):
        return None
    return None


# ── Public API ─────────────────────────────────────────────────────────


def render(
    entity: str,
    model: Optional[str] = None,
    channel: str = ICS_CHANNEL_OPENCODE,
    trace_id: Optional[str] = None,
    phase: Optional[str] = None,
    mode: str = "full",
    node: Optional[str] = None,
    session_id: Optional[str] = None,
) -> str:
    """Render an ICS-S header string.

    This is the primary public API. Agents and tools should call this
    instead of hand-typing headers.

    Args:
        entity: The entity name (e.g., "GRAND_OVERSIGHT", "build_oversoul")
        model: Optional model override (D118). If None, auto-detected.
        channel: The execution channel (default: ``"opencode"``)
        trace_id: Optional trace ID. If None, auto-generated.
        phase: Optional phase string. If None, auto-detected from
            ACTIVE_SPRINT.json (M27) with blueprint fallback.
        mode: ``"full"`` | ``"compact"`` | ``"off"`` (default: ``"full"``)
        node: Optional Node designation when acting under a Node expert
            session (PP-4, e.g., ``"N7"``). Rendered as ``[N7]`` after
            the entity. Omit for prime-agent headers.
        session_id: Optional OpenCode session ID (P5). Rendered as a
            trailing segment AND scopes the session-DB model lookup.

    Returns:
        The formatted ICS-S header string.

    Example:
        >>> from omega.ics import render
        >>> render("GRAND_OVERSIGHT", model="minimax-m3-free", trace_id="trc_abc123")
        '⬡ OMEGA ⬡ GRAND_OVERSIGHT ⬡ minimax-m3-free ⬡ opencode ⬡ trc_abc123 ⬡ H2-F'
        >>> render("LILITH", node="N7", session_id="ses_x")  # doctest: +SKIP
        '⬡ OMEGA ⬡ LILITH ⬡ [N7] ⬡ ... ⬡ ses_x'
    """
    ctx = ICSContext(
        entity=entity,
        model=model,
        channel=channel,
        trace_id=trace_id,
        phase=phase,
        mode=mode,
        node=node,
        session_id=session_id,
    )
    return ctx.render()


def render_for_response(
    response: "OracleResponse",
    mode: str = "full",
) -> str:
    """Render an ICS-S header from an existing OracleResponse.

    Convenience wrapper that pulls entity/model/trace/phase/channel/node/session_id
    from the response object. Includes PP-4 node and P5 session_id when present.

    Args:
        response: An :class:`OracleResponse` instance
        mode: ``"full"`` | ``"compact"`` | ``"off"``

    Returns:
        The formatted ICS-S header string.
    """
    return render(
        entity=response.entity,
        model=response.model,
        trace_id=response.trace_id if response.trace_id else None,
        phase=response.phase,
        mode=mode,
        channel=getattr(response, "channel", ICS_CHANNEL_OPENCODE),
        node=getattr(response, "node", None),
        session_id=getattr(response, "session_id", None),
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
