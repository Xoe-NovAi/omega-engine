# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Omega Engine — Subagent Dispatch Protocol
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ SUBAGENT-DISPATCH
# AP: SUBAGENT-DISPATCH-v1.0.0
#
# HandoffPacket + Agent Capability Registry + dispatch prompt builder.
# Core concept (agent dispatch) is the user's original design.
# [id-soft: vet-015] ZONEID Pattern — magic constant for handoff packet integrity
# Heritage: Thinker chain — used for lifecycle tracking metaphor (inspired by Quake 1996)
# Protocol docs: docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import anyio
import json
import logging
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

logger = logging.getLogger(__name__)

# ── Handoff sub-types ────────────────────────────────────────────────────

PacketType = Literal["request", "response", "delegation", "notification", "broadcast"]
TaskType = Literal["design", "review", "research", "mine", "verify", "implement"]
PacketStatus = Literal["pending", "active", "completed", "stale", "archived"]
AgentMode = Literal["primary", "subagent"]
ResolverStrategy = Literal["terminate", "escalate", "fallback", "retry"]

# ── TTL constants (aligned with MCP background reaper) ──────────────────────
PENDING_TTL: int = 14400     # 4h — pending → stale
ACTIVE_TTL: int = 172800     # 48h — active → stale
COMPLETED_TTL: int = 604800  # 7d — completed → archive

# ── ZONEID for handoff packets ───────────────────────────────────────────

# [id-soft: vet-015] ZONEID Pattern — magic constant for handoff packet integrity
# Imported from cvar_table (single source of truth per D97)
from omega.cvar_table import ZONEID_HANDOFF  # noqa: F401

# ── HandoffPacket ─────────────────────────────────────────────────────────


@dataclass
class HandoffPacket:
    """Typed handoff between agents. Mandate 9 (Error Integrity) compliant.
    
    Every dispatch creates one of these. It tracks the full lifecycle:
    pending -> active -> completed/stale, with traceable IDs at every step.
    
    Core concept (agent dispatch) is the user's original design.
    Uses [id-soft: vet-015] ZONEID Pattern for packet integrity.
    """

    source_agent: str
    target_agent: str
    task_type: TaskType
    task_description: str
    relevant_files: List[str] = field(default_factory=list)
    context: str = ""
    context_delivery: str = "inline"  # D216: "inline" | "file_ref" | "usm_key"

    packet_id: str = ""
    parent_trace_id: str = ""
    trace_id: str = ""
    zoneid: int = ZONEID_HANDOFF
    packet_type: PacketType = "request"
    status: PacketStatus = "pending"
    expected_output: str = ""
    ttl_seconds: int = 14400  # 4h — aligned with PENDING_TTL
    resolver_strategy: ResolverStrategy = "escalate"  # Decree 2: default escalate to Grand Oversight
    resolved_by: Optional[str] = None
    error: Optional[str] = None
    result: Optional[str] = None
    created_at: float = 0.0
    
    # Loop Guard Fields (T2-5)
    visited_agents: List[str] = field(default_factory=list)
    hop_count: int = 0
    max_hops: int = 10

    def __post_init__(self) -> None:
        if not self.packet_id:
            now = datetime.now()
            short = uuid.uuid4().hex[:8]
            self.packet_id = f"hdp_{now.strftime('%Y%m%d')}_{self.source_agent}_{self.target_agent}_{short}"
        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex
        if not self.created_at:
            self.created_at = datetime.now().timestamp()
        if self.zoneid != ZONEID_HANDOFF:
            raise ValueError(f"Invalid ZONEID_HANDOFF: expected {ZONEID_HANDOFF:#x}, got {self.zoneid:#x}")
        
        # Initialize visited set with source
        if self.source_agent not in self.visited_agents:
            self.visited_agents.append(self.source_agent)

    def is_loop(self, target: str) -> bool:
        """Check if delegating to target would create a loop."""
        return target.lower() in [a.lower() for a in self.visited_agents]

    def increment_hop(self) -> bool:
        """Increment hop count and check against max_hops. Returns True if budget remains."""
        self.hop_count += 1
        return self.hop_count <= self.max_hops

    @property
    def expired(self) -> bool:
        import time
        return time.time() > (self.created_at + self.ttl_seconds)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def save(self, archive_dir: str = "data/handoff/archive", use_usm: bool = False) -> str:
        """Saves the packet. Returns the identifier (path or USM hash)."""
        if use_usm:
            from omega.state import get_usm
            usm = get_usm()
            # Use packet_id as the state key for USM
            state_key = f"handoff:{self.packet_id}"
            # We use a wrapper to store the packet data
            data = {"packet": self.to_dict()}
            # Note: save_state is async, but save() is sync. 
            # We must use anyio.run or similar, but better to make save async.
            # For now, we'll stick to file-based or provide an async version.
            # Let's implement save_async.
            return "USM_ASYNC_REQUIRED"
        
        path = Path(archive_dir) / f"{self.packet_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json())
        logger.info("HandoffPacket saved: %s", path)
        return str(path)

    async def save_async(self, archive_dir: str = "data/handoff/archive", use_usm: bool = False) -> str:
        """Async version of save, supporting USM."""
        if use_usm:
            from omega.state import get_usm
            usm = get_usm()
            state_key = f"handoff:{self.packet_id}"
            data = {"packet": self.to_dict()}
            await usm.save_state(state_key, data)
            return state_key
        
        path = Path(archive_dir) / f"{self.packet_id}.json"
        await anyio.Path(path.parent).mkdir(parents=True, exist_ok=True)
        await anyio.Path(path).write_text(self.to_json())
        logger.info("HandoffPacket saved: %s", path)
        return str(path)

    @classmethod
    async def load_async(cls, identifier: str, use_usm: bool = False) -> "HandoffPacket":
        """Async load from path or USM hash."""
        if use_usm:
            from omega.state import get_usm
            usm = get_usm()
            # If identifier is a USM key (starts with handoff:)
            if identifier.startswith("handoff:"):
                data = await usm.load_state(identifier)
                if data and "packet" in data:
                    return cls(**data["packet"])
            # Fallback to path
            raw = await anyio.Path(identifier).read_text()
            return cls(**json.loads(raw))
        
        raw = Path(identifier).read_text()
        return cls(**json.loads(raw))


# ── Agent Capability Registry (WAD-Loaded) ─────────────────────────────────

AgentDescriptor = Dict[str, Any]

# ROLE_CONSTANTS — engine-defined slots (NOT entity names).
# WAD YAML (config/wads/<iwad>/entities/dispatch.yaml) maps ROLE → entity.
# These constants are engine architecture, not WAD content (M2-compliant).
ROLE_CONSTANTS: Dict[str, str] = {
    "GRAND_OVERSIGHT": "grand_oversight",
    "BUILD_OVERSOUL": "build_oversoul",
    "RUNTIME_OVERSOUL": "runtime_oversoul",
    "N1": "infrastructure",
    "N2": "persistence",
    "N3": "engineering",
    "N4": "integration",
    "N5": "governance",
    "N6": "cognition",
    "N7": "context",
    "N8": "observability",
    "N9": "orchestration",
    "N10": "validation",
}

# WAD-backed dispatch config loader (M2 Firewall Phase B).
# Delegates to dispatch_registry — single source of truth.
# DISPATCH_CONFIG_FILENAME retained for compatibility.

from omega.governance.dispatch_registry import get_dispatch_entities


def _build_capability_registry(iwad: str | None = None) -> Dict[str, AgentDescriptor]:
    """Build the capability registry from WAD dispatch.yaml at runtime.

    Engine core defines SLOTS (N1-N10, Grand Oversight) and INTERFACES.
    WADs provide the ENTITIES that fill those slots. No entity names are
    hardcoded in engine code (M2 Firewall compliant).

    Args:
        iwad: IWAD name. If None, uses active_iwad from config/omega.yaml.

    Returns:
        Dict mapping lowercase agent name -> AgentDescriptor.
    """
    entities = get_dispatch_entities(iwad)
    registry: Dict[str, AgentDescriptor] = {}
    for ent in entities:
        name = str(ent.get("name", "")).lower()
        if not name:
            continue
        registry[name] = {
            "mode": ent.get("mode", "primary"),
            "purpose": ent.get("purpose", ""),
            "capabilities": ent.get("capabilities", []),
            "domains": ent.get("domains", []),
            "node_slot": ent.get("node_slot"),
            "task_tool_type": ent.get("task_tool_type", "general"),
            "owned_files": ent.get("owned_files", []),
            "role": ent.get("role"),
            "model": ent.get("model"),
        }
    return registry


# Module-level registry (built at import from WAD config).
# Fallback to empty dict if WAD config missing — callers handle gracefully.
try:
    CAPABILITY_REGISTRY: Dict[str, AgentDescriptor] = _build_capability_registry()
except (FileNotFoundError, ValueError) as exc:
    logger.warning("Dispatch config unavailable, registry empty: %s", exc)
    CAPABILITY_REGISTRY: Dict[str, AgentDescriptor] = {}


# ── Dispatch Helpers ─────────────────────────────────────────────────────


def get_agent_capabilities(agent_name: str) -> Optional[AgentDescriptor]:
    """Look up an agent in the capability registry."""
    agent = CAPABILITY_REGISTRY.get(agent_name.lower())
    if agent is None:
        logger.warning("Unknown agent: %s", agent_name)
    return agent


def list_available_agents(mode: Optional[AgentMode] = None) -> List[str]:
    """List all registered agents, optionally filtered by mode."""
    return [
        name for name, desc in CAPABILITY_REGISTRY.items()
        if mode is None or desc["mode"] == mode
    ]


def _extract_heritage_tags(file_path: str) -> List[str]:
    """Extract [id-soft:] heritage tags from a file."""
    tags = []
    try:
        path = Path(file_path)
        if path.exists() and path.is_file():
            content = path.read_text(encoding="utf-8")
            # Find all [id-soft: ...] patterns
            matches = re.findall(r'\[id-soft:[^\]]+\]', content)
            tags.extend(matches)
    except OSError as e:
        logger.debug("Failed to read heritage tags from %s: %s", file_path, e)
    except re.error as e:
        logger.debug("Regex error extracting heritage tags from %s: %s", file_path, e)
    return tags


def build_dispatch_prompt(packet: HandoffPacket) -> str:
    """Build the Task tool prompt from a HandoffPacket.

    The returned string is designed for injection into the 'task' tool's
    prompt argument, with `subagent_type` set from the capability registry.
    """
    target = get_agent_capabilities(packet.target_agent)
    target_desc = target["purpose"] if target else f"Agent: {packet.target_agent}"
    target_caps = ", ".join(target["capabilities"]) if target else "unknown"

    source = get_agent_capabilities(packet.source_agent)
    source_desc = source["purpose"] if source else f"Agent: {packet.source_agent}"

    lines = [
        f"# 🔱 Omega Engine — Subagent Dispatch: {packet.packet_id}",
        "",
        f"You are **{packet.target_agent}**.",
        f"Your role: {target_desc}",
        f"Your capabilities: {target_caps}",
        "",
        "You have been dispatched as a specialized subagent. Act with the full",
        f"authority and domain knowledge of {packet.target_agent}.",
        "",
        "## Source",
        f"This dispatch was created by **{packet.source_agent}** ({source_desc}).",
        f"Trace ID: `{packet.trace_id}`",
        "",
        "## Context",
        packet.context or "(No additional context provided)",
        "",
        "## Task",
        packet.task_description,
        "",
    ]

    if packet.relevant_files:
        lines.append("## Files to Read First")
        for f in packet.relevant_files:
            lines.append(f"- `{f}`")
        lines.append("")

        # Extract heritage tags from relevant files
        heritage_tags = []
        for f in packet.relevant_files:
            heritage_tags.extend(_extract_heritage_tags(f))
        if heritage_tags:
            lines.append("## Heritage Tags in Referenced Files")
            for tag in heritage_tags:
                lines.append(f"- {tag}")
            lines.append("")

    if packet.expected_output:
        lines.append("## Expected Output")
        lines.append(packet.expected_output)
        lines.append("")

    lines.append("## Heritage & Mandates")
    lines.append("- Refer to PIVOT_LOG.md for prior architectural decisions.")
    lines.append("- Sovereign Mandate 13 (Temple-Grade T1-T11) applies to all changes.")
    lines.append("- Heritage attribution: every id Software-derived pattern MUST carry id-soft inline tags (format in CREDITS.md) with scope.")
    lines.append("- This is an atomic dispatch. Complete it, then return your result.")
    lines.append("")

    lines.append(f"*Dispatch from {packet.source_agent} to {packet.target_agent} — {packet.packet_id}*")

    return "\n".join(lines)


def dispatch(packet: HandoffPacket) -> str:
    """Generate the formatted Task tool prompt from a HandoffPacket.

    Returns the prompt string. The calling agent must then invoke the Task
    tool with:
      subagent_type = CAPABILITY_REGISTRY[target]["task_tool_type"]
      description = f"{packet.task_type}: {packet.task_description}"
      prompt = <return value>

    Usage:
        from omega.oracle.subagent_dispatcher import HandoffPacket, dispatch

        packet = HandoffPacket(
            source_agent="source_entity",
            target_agent="target_entity",
            task_type="review",
            task_description="Audit cvar_table.py heritage tags",
            relevant_files=["src/omega/cvar_table.py", "CREDITS.md"],
            context="Sprint 1 complete.",
            expected_output="Heritage audit report (JSON)",
        )
        prompt = dispatch(packet)
        # Then use the Task tool with prompt
    """
    return build_dispatch_prompt(packet)
