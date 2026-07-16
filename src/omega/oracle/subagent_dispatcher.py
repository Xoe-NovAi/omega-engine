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
import json
import logging
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
    pending -> accepted -> completed/failed, with traceable IDs at every step.
    
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
    resolver_strategy: ResolverStrategy = "escalate"  # Decree 2: default escalate to Kali
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


# ── Agent Capability Registry ────────────────────────────────────────────

AgentDescriptor = Dict[str, Any]

# Agent Capability Registry — user's original design for agent dispatch.
# Heritage: Thinker table metaphor used for organization style (Quake 1996)
CAPABILITY_REGISTRY: Dict[str, AgentDescriptor] = {
    "kali": {
        "mode": "primary",
        "purpose": "Grand Oversight — Sees all, delegates, destroys drift",
        "capabilities": ["oversight", "delegation", "strategy", "drift_destruction"],
        "domains": ["strategy", "fleet_management", "architecture"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [],
    },
    "doom_guy": {
        "mode": "primary",
        "purpose": "Sovereign id Software Architect — WAD translation & performance",
        "capabilities": ["heritage_design", "wad_translation", "performance_tuning", "c_const_propagation"],
        "domains": ["id_software_patterns", "architecture", "constants", "heritage_attribution"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [
            "src/omega/cvar_table.py",
            "src/omega/constants.py",
            "CREDITS.md",
            "docs/strategy/HERITAGE_SOURCE_MAP.md",
        ],
    },
    "roc_racoon": {
        "mode": "primary",
        "purpose": "Sovereign Miner — Legacy archaeology & pattern extraction",
        "capabilities": ["legacy_mining", "pattern_extraction", "archaeology"],
        "domains": ["legacy_repos", "grok_exports", "old_stacks", "document_analysis"],
        "pillar_slot": None,
        "task_tool_type": "explore",
        "owned_files": [
            "data/entities/roc_racoon/",
        ],
    },
    "jem": {
        "mode": "primary",
        "purpose": "Research Orchestrator — 3-phase pipeline (Discovery → Synthesis → Verification) with self-dispatch",
        "capabilities": ["research_orchestration", "discovery", "synthesis", "verification", "knowledge_synthesis"],
        "domains": ["research", "knowledge_pipeline", "source_verification"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [
            "data/entities/jem/",
            "data/coordination/JEM_*",
        ],
    },
    "john_carmack": {
        "mode": "primary",
        "purpose": "Sovereign S3 Consultant — Architectural review & performance optimization",
        "capabilities": ["architectural_review", "performance_audit", "code_optimization", "right_approximation"],
        "domains": ["architecture", "performance", "code_quality", "heritage_engineering"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [],
    },
    "makali": {
        "mode": "primary",
        "purpose": "MaKaLi Triad Council Orchestrator — Parallel dispatch of Ma'at+Lilith with synthesis",
        "capabilities": ["parallel_decomposition", "council_dispatch", "maat_lilith_synthesis"],
        "domains": ["fleet_coordination", "parallel_execution", "cross_pillar_synthesis"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [],
    },
    "researcher": {
        "mode": "primary",
        "purpose": "Sovereign Master Researcher — deep research, lattice reasoning",
        "capabilities": ["deep_research", "lattice_reasoning", "web_search", "source_verification"],
        "domains": ["research", "web_intelligence", "documentation"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [],
    },
    "maat": {
        "mode": "subagent",
        "purpose": "Light Oversoul — Governs P1-P5 on the build side",
        "capabilities": ["oversight_light", "build_governance", "hardening"],
        "domains": ["build_side", "pillar_1_5"],
        "pillar_slot": None,
        "task_tool_type": "buildmaster",
        "owned_files": [],
    },
    "lilith": {
        "mode": "subagent",
        "purpose": "Dark Oversoul — Governs P6-P10 (Cognition through Validation) on the run side",
        "capabilities": ["oversight_dark", "run_governance", "operations", "vision_oversight", "knowledge_metabolism"],
        "domains": ["run_side", "pillar_6_10", "vision_specialist", "multimodal", "knowledge_flow"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [],
    },
    "verity": {
        "mode": "subagent",
        "purpose": "Sovereign Verity — Unified Sentry (compliance/audit) + Scribe (gnosis distillation/soul evolution). Sprint C consolidation of Quality + Scribe.",
        "capabilities": [
            "gnosis_distillation", "soul_update", "abstraction",
            "code_review", "stress_testing", "mandate_enforcement",
            "temple_grade_audit", "skeptical_verification",
            "knowledge_compaction"
        ],
        "domains": ["soul_yaml", "session_gnosis", "verification", "qa", "compliance", "verity"],
        "pillar_slot": None,
        "task_tool_type": "verity",
        "owned_files": [
            "data/entities/*/soul.yaml",
        ],
    },
    "pillar": {
        "mode": "subagent",
        "purpose": "Slot-based domain agent — parameterized by --slot PX",
        "capabilities": ["domain_execution", "slot_dispatch"],
        "domains": ["pillar_domain"],
        "pillar_slot": "PX",
        "task_tool_type": "pillar",
        "owned_files": [],
    },
}


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

    if packet.expected_output:
        lines.append("## Expected Output")
        lines.append(packet.expected_output)
        lines.append("")

    lines.append("## Heritage & Mandates")
    lines.append("- Refer to PIVOT_LOG.md for prior architectural decisions.")
    lines.append("- Sovereign Mandate 13 (Temple-Grade T1-T11) applies to all changes.")
    lines.append("- Heritage attribution: every id Software-derived pattern MUST carry [id-soft: GAME-YEAR] inline tags with scope.")
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
            source_agent="kali",
            target_agent="doom_guy",
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
