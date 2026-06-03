# 🔱 Omega Engine — Subagent Dispatch Protocol
# ⬡ OMEGA ⬡ KALI ⬡ deepseek-v4-flash ⬡ opencode ⬡ SUBAGENT-DISPATCH
# AP: SUBAGENT-DISPATCH-v1.0.0
#
# HandoffPacket + Agent Capability Registry + dispatch prompt builder.
# Core concept (agent dispatch) is the user's original design.
# [id-soft: doom-1993] ZONEID Pattern — used for packet integrity constant
# [id-soft: quake-1996] Thinker chain — used for lifecycle tracking metaphor
# Protocol docs: docs/strategy/SUBAGENT_DISPATCH_PROTOCOL.md

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
PacketStatus = Literal["pending", "accepted", "rejected", "completed", "failed", "timed_out"]
AgentMode = Literal["primary", "subagent"]

# ── ZONEID for handoff packets ───────────────────────────────────────────

# [id-soft: doom-1993] ZONEID Pattern — handoff packet integrity constant
# Imported from cvar_table (single source of truth per D97)
from omega.cvar_table import ZONEID_HANDOFF  # noqa: F401

# ── HandoffPacket ─────────────────────────────────────────────────────────


@dataclass
class HandoffPacket:
    """Typed handoff between agents. Mandate 9 (Error Integrity) compliant.

    Every dispatch creates one of these. It tracks the full lifecycle:
    pending -> accepted -> completed/failed, with traceable IDs at every step.

    Core concept (agent dispatch) is the user's original design.
    Uses [id-soft: doom-1993] ZONEID Pattern for packet integrity.
    """

    source_agent: str
    target_agent: str
    task_type: TaskType
    task_description: str
    relevant_files: List[str] = field(default_factory=list)
    context: str = ""

    packet_id: str = ""
    parent_trace_id: str = ""
    trace_id: str = ""
    zoneid: int = ZONEID_HANDOFF
    packet_type: PacketType = "request"
    status: PacketStatus = "pending"
    expected_output: str = ""
    ttl_seconds: int = 600
    error: Optional[str] = None
    result: Optional[str] = None
    created_at: float = 0.0

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

    @property
    def expired(self) -> bool:
        import time
        return time.time() > (self.created_at + self.ttl_seconds)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def save(self, archive_dir: str = "data/handoff/archive") -> Path:
        path = Path(archive_dir) / f"{self.packet_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_json())
        logger.info("HandoffPacket saved: %s", path)
        return path

    @classmethod
    def load(cls, path: str) -> "HandoffPacket":
        raw = json.loads(Path(path).read_text())
        return cls(**raw)


# ── Agent Capability Registry ────────────────────────────────────────────

AgentDescriptor = Dict[str, Any]

# Agent Capability Registry — user's original design for agent dispatch.
# Thinker table metaphor [id-soft: quake-1996] used for organization style.
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
    "plan": {
        "mode": "primary",
        "purpose": "The Architect — Grand Dispatcher & Strategy Lead",
        "capabilities": ["architecture", "dispatch", "strategy"],
        "domains": ["grand_design", "roadmapping"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [],
    },
    "jem": {
        "mode": "primary",
        "purpose": "Research Orchestrator — 3-tier local model pipeline",
        "capabilities": ["research_orchestration", "local_model_management", "knowledge_synthesis"],
        "domains": ["research", "local_models", "knowledge_pipeline"],
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
        "purpose": "Dark Oversoul — Governs P6-P10 on the run side",
        "capabilities": ["oversight_dark", "run_governance", "operations"],
        "domains": ["run_side", "pillar_6_10"],
        "pillar_slot": None,
        "task_tool_type": "general",
        "owned_files": [],
    },
    "scribe": {
        "mode": "subagent",
        "purpose": "Gnosis Keeper — L1->L2->L3 distillation",
        "capabilities": ["gnosis_distillation", "soul_update", "abstraction"],
        "domains": ["soul_yaml", "session_gnosis"],
        "pillar_slot": None,
        "task_tool_type": "scribe",
        "owned_files": [
            "data/entities/*/soul.yaml",
        ],
    },
    "quality": {
        "mode": "subagent",
        "purpose": "Compliance Guard — Enforces Sovereign Mandates, code review",
        "capabilities": ["code_review", "stress_testing", "mandate_enforcement", "temple_grade_audit"],
        "domains": ["verification", "qa", "compliance"],
        "pillar_slot": None,
        "task_tool_type": "quality",
        "owned_files": [],
    },
    "jem_discovery": {
        "mode": "subagent",
        "purpose": "Tier 1 Research — broad search, evidence logging",
        "capabilities": ["web_search", "source_hunting", "evidence_logging"],
        "domains": ["fact_gathering", "web_research"],
        "pillar_slot": None,
        "task_tool_type": "jem_discovery",
        "owned_files": [],
    },
    "jem_synthesis": {
        "mode": "subagent",
        "purpose": "Tier 2 Research — pattern recognition, synthesis",
        "capabilities": ["pattern_recognition", "conceptual_mapping", "synthesis"],
        "domains": ["analysis", "pattern_detection"],
        "pillar_slot": None,
        "task_tool_type": "jem_synthesis",
        "owned_files": [],
    },
    "jem_verification": {
        "mode": "subagent",
        "purpose": "Tier 3 Research — fact-check, R-doc, gnosis",
        "capabilities": ["fact_checking", "gnosis_distillation", "r_doc_validation"],
        "domains": ["verification", "research_quality"],
        "pillar_slot": None,
        "task_tool_type": "jem_verification",
        "owned_files": [],
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
    lines.append("- Heritage attribution: every id Software-derived pattern MUST carry [id-soft:] inline tags.")
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
