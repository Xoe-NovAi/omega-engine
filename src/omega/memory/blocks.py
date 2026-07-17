# AP: AP-D283-MNEMOSYNE-v1.0.0
# 🔱 Memory Blocks — Letta-Style Typed Memory for Omega Engine
# ⬡ OMEGA ⬡ MEMORY ⬡ blocks.py
#
# Implements Letta 2026 memory block pattern: typed, persistent, LLM-editable
# blocks with governance (read_only), limits (SLA), and descriptions (spec).
#
# Three-tier architecture:
#   Core (HOT)    — Always in context: persona, human, safety, decisions
#   Recall (WARM) — Conversation history: auto-logged exchanges
#   Archival (COLD) — Arbitrary facts: vector + KV + graph storage
#
# [id-soft: vet-056] Oracle Summoning Pattern — Blocks injected at summon time
# [id-soft: vet-008] Zone Memory — Core blocks = Cache tier (always hot)

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Literal

logger = logging.getLogger(__name__)


class GovernanceLevel(str, Enum):
    """Cross-entity memory sharing governance levels."""
    PRIVATE = "private"           # Owner only
    SHARED_READ = "shared_read"   # Allowlisted entities can read
    SHARED_WRITE = "shared_write" # Allowlisted entities can append
    PUBLIC = "public"             # All entities can read


class BlockCategory(str, Enum):
    """Memory block categories for decay and retrieval."""
    IDENTITY = "identity"         # persona, human — slow decay
    STRATEGY = "strategy"         # project-*, decisions — medium decay
    ASSUMPTION = "assumption"     # inferred context — faster decay
    PREFERENCE = "preference"     # user prefs — medium decay
    GOAL = "goal"                 # active objectives — fast decay
    EVENT = "event"               # episodic — fast decay
    FAILURE = "failure"           # errors — very fast decay
    CONTEXT = "context"           # scratchpad — fastest decay


# Category-specific decay rates (per day) — 2026 consensus from StructureMA, BunsDev, FSRS-6
CATEGORY_DECAY_RATES: Dict[BlockCategory, float] = {
    BlockCategory.IDENTITY: 0.01,
    BlockCategory.STRATEGY: 0.10,
    BlockCategory.ASSUMPTION: 0.18,
    BlockCategory.PREFERENCE: 0.05,
    BlockCategory.GOAL: 0.15,
    BlockCategory.EVENT: 0.25,
    BlockCategory.FAILURE: 0.35,
    BlockCategory.CONTEXT: 0.60,
}


@dataclass
class MemoryBlock:
    """
    Letta 2026 Memory Block — typed contract between agent and developer.
    
    Fields:
        id: UUID — unique identifier
        label: Human-readable label (e.g., "persona", "project-omega", "decisions")
        value: String content (JSON-serializable structures allowed)
        limit: Character cap — SLA for context budget
        description: Guides agent on WHEN to read/write — CRITICAL for tool use
        read_only: If True, only developer can modify (governance)
        metadata: Extensible (tags, schema hints, version)
        category: Decay/retrieval category
        governance_level: Cross-entity sharing policy
        shared_with: Explicit allowlist for shared_* governance
        taint_policy: "strict" (default) or "permissive" for TDP bridge
        owner_entity: Entity that owns this block (e.g., "maat", "pillar_P3")
        created_at: ISO timestamp
        updated_at: ISO timestamp
        created_by_id: Agent/entity that created
        last_updated_by_id: Agent/entity that last modified
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    value: str = ""
    limit: int = 2000
    description: str = ""
    read_only: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    category: BlockCategory = BlockCategory.CONTEXT
    governance_level: GovernanceLevel = GovernanceLevel.PRIVATE
    shared_with: List[str] = field(default_factory=list)
    taint_policy: Literal["strict", "permissive"] = "strict"
    owner_entity: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    created_by_id: str = ""
    last_updated_by_id: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now(timezone.utc).isoformat()

    def is_near_limit(self, threshold: float = 0.85) -> bool:
        """Check if block is near its character limit (triggers rethink)."""
        return len(self.value) >= int(self.limit * threshold)

    def remaining_capacity(self) -> int:
        """Characters remaining before limit."""
        return max(0, self.limit - len(self.value))

    def can_write(self, requester_entity: str) -> bool:
        """Check if requester can write based on governance."""
        if self.read_only:
            return requester_entity == self.owner_entity or requester_entity == "developer"
        if self.governance_level == GovernanceLevel.PRIVATE:
            return requester_entity == self.owner_entity
        if self.governance_level == GovernanceLevel.SHARED_READ:
            return requester_entity == self.owner_entity or requester_entity in self.shared_with
        if self.governance_level == GovernanceLevel.SHARED_WRITE:
            return requester_entity == self.owner_entity or requester_entity in self.shared_with
        if self.governance_level == GovernanceLevel.PUBLIC:
            return True
        return False

    def can_read(self, requester_entity: str) -> bool:
        """Check if requester can read based on governance."""
        if self.governance_level == GovernanceLevel.PRIVATE:
            return requester_entity == self.owner_entity
        if self.governance_level == GovernanceLevel.SHARED_READ:
            return requester_entity == self.owner_entity or requester_entity in self.shared_with
        if self.governance_level == GovernanceLevel.SHARED_WRITE:
            return requester_entity == self.owner_entity or requester_entity in self.shared_with
        if self.governance_level == GovernanceLevel.PUBLIC:
            return True
        return False

    def get_decay_rate(self) -> float:
        """Get category-specific decay rate (per day)."""
        return CATEGORY_DECAY_RATES.get(self.category, 0.10)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for storage."""
        return {
            "id": self.id,
            "label": self.label,
            "value": self.value,
            "limit": self.limit,
            "description": self.description,
            "read_only": self.read_only,
            "metadata": self.metadata,
            "category": self.category.value,
            "governance_level": self.governance_level.value,
            "shared_with": self.shared_with,
            "taint_policy": self.taint_policy,
            "owner_entity": self.owner_entity,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "created_by_id": self.created_by_id,
            "last_updated_by_id": self.last_updated_by_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryBlock":
        """Deserialize from dict."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            label=data.get("label", ""),
            value=data.get("value", ""),
            limit=data.get("limit", 2000),
            description=data.get("description", ""),
            read_only=data.get("read_only", False),
            metadata=data.get("metadata", {}),
            category=BlockCategory(data.get("category", "context")),
            governance_level=GovernanceLevel(data.get("governance_level", "private")),
            shared_with=data.get("shared_with", []),
            taint_policy=data.get("taint_policy", "strict"),
            owner_entity=data.get("owner_entity", ""),
            created_at=data.get("created_at", datetime.now(timezone.utc).isoformat()),
            updated_at=data.get("updated_at", datetime.now(timezone.utc).isoformat()),
            created_by_id=data.get("created_by_id", ""),
            last_updated_by_id=data.get("last_updated_by_id", ""),
        )


# ── Essential Block Templates (Letta 2026) ──────────────────────────────────

ESSENTIAL_BLOCKS: Dict[str, Dict[str, Any]] = {
    "persona": {
        "label": "persona",
        "description": "Agent identity, behavioral guidelines, capabilities, learned adaptations. Read-only after initialization.",
        "limit": 5000,
        "read_only": True,
        "category": BlockCategory.IDENTITY,
        "governance_level": GovernanceLevel.PRIVATE,
    },
    "human": {
        "label": "human",
        "description": "User information, preferences, context, cross-project preferences.",
        "limit": 3000,
        "read_only": False,
        "category": BlockCategory.PREFERENCE,
        "governance_level": GovernanceLevel.PRIVATE,
    },
    "safety": {
        "label": "safety",
        "description": "Constitutional principles, refusal triggers, governance rules. Read-only.",
        "limit": 2000,
        "read_only": True,
        "category": BlockCategory.IDENTITY,
        "governance_level": GovernanceLevel.PRIVATE,
    },
}

DOMAIN_BLOCKS: Dict[str, Dict[str, Any]] = {
    "project-overview": {
        "label": "project-overview",
        "description": "High-level description, tech stack, repo links.",
        "limit": 3000,
        "category": BlockCategory.STRATEGY,
    },
    "project-commands": {
        "label": "project-commands",
        "description": "Build, test, lint, dev commands.",
        "limit": 2000,
        "category": BlockCategory.STRATEGY,
    },
    "project-conventions": {
        "label": "project-conventions",
        "description": "Commit style, PR process, code style.",
        "limit": 2000,
        "category": BlockCategory.STRATEGY,
    },
    "project-architecture": {
        "label": "project-architecture",
        "description": "Directory structure, key modules.",
        "limit": 3000,
        "category": BlockCategory.STRATEGY,
    },
    "project-gotchas": {
        "label": "project-gotchas",
        "description": "Footguns, things to watch out for.",
        "limit": 2000,
        "category": BlockCategory.FAILURE,
    },
    "current-task": {
        "label": "current-task",
        "description": "Scratchpad for active work item.",
        "limit": 2000,
        "category": BlockCategory.CONTEXT,
    },
    "context": {
        "label": "context",
        "description": "Debugging/investigation scratchpad.",
        "limit": 3000,
        "category": BlockCategory.CONTEXT,
    },
    "decisions": {
        "label": "decisions",
        "description": "Architectural decisions and rationale (append-only).",
        "limit": 5000,
        "category": BlockCategory.STRATEGY,
    },
    "failures": {
        "label": "failures",
        "description": "Error patterns and lessons learned (fast decay).",
        "limit": 3000,
        "category": BlockCategory.FAILURE,
    },
}


def create_essential_blocks(owner_entity: str, created_by: str) -> List[MemoryBlock]:
    """Create the three essential blocks for a new entity."""
    blocks = []
    for label, template in ESSENTIAL_BLOCKS.items():
        block = MemoryBlock(
            label=template["label"],
            value="",
            limit=template["limit"],
            description=template["description"],
            read_only=template["read_only"],
            category=template["category"],
            governance_level=template["governance_level"],
            owner_entity=owner_entity,
            created_by_id=created_by,
            last_updated_by_id=created_by,
        )
        blocks.append(block)
    return blocks


def create_domain_block(
    label: str,
    owner_entity: str,
    created_by: str,
    value: str = "",
) -> MemoryBlock:
    """Create a single domain-specific block from template.

    Singular version used by BlockTools.create_domain_block().
    Plural version (create_domain_blocks) creates all at once.

    Args:
        label: Block label (must be in DOMAIN_BLOCKS).
        owner_entity: Entity that owns this block.
        created_by: Agent/entity creating the block.
        value: Initial block content.

    Returns:
        A single MemoryBlock.

    Raises:
        ValueError: If label is not in DOMAIN_BLOCKS.
    """
    if label not in DOMAIN_BLOCKS:
        raise ValueError(
            f"Unknown domain block label: {label}. "
            f"Valid: {list(DOMAIN_BLOCKS.keys())}"
        )

    template = DOMAIN_BLOCKS[label]
    return MemoryBlock(
        label=label,
        value=value,
        limit=template["limit"],
        description=template["description"],
        read_only=False,
        category=template["category"],
        governance_level=GovernanceLevel.PRIVATE,
        owner_entity=owner_entity,
        created_by_id=created_by,
        last_updated_by_id=created_by,
    )


def create_essential_block(label: str, owner_entity: str, created_by: str, value: str = "") -> MemoryBlock:
    """Create a single essential block (persona, human, safety) from template.

    This is the singular version used by BlockTools.create_essential_block().
    The plural version (create_essential_blocks) creates all three at once.

    Args:
        label: Block label (must be in ESSENTIAL_BLOCKS).
        owner_entity: Entity that owns this block.
        created_by: Agent/entity creating the block.
        value: Initial block content.

    Returns:
        A single MemoryBlock.

    Raises:
        ValueError: If label is not in ESSENTIAL_BLOCKS.
    """
    if label not in ESSENTIAL_BLOCKS:
        raise ValueError(f"Unknown essential block label: {label}. Valid: {list(ESSENTIAL_BLOCKS.keys())}")

    template = ESSENTIAL_BLOCKS[label]
    return MemoryBlock(
        label=template["label"],
        value=value,
        limit=template["limit"],
        description=template["description"],
        read_only=template["read_only"],
        category=template["category"],
        governance_level=template["governance_level"],
        owner_entity=owner_entity,
        created_by_id=created_by,
        last_updated_by_id=created_by,
    )


def create_domain_blocks(owner_entity: str, created_by: str, domain: str = "general") -> List[MemoryBlock]:
    """Create domain-specific blocks for an entity."""
    blocks = []
    for label, template in DOMAIN_BLOCKS.items():
        block = MemoryBlock(
            label=label,
            value="",
            limit=template["limit"],
            description=template["description"],
            read_only=False,
            category=template["category"],
            governance_level=GovernanceLevel.PRIVATE,
            owner_entity=owner_entity,
            created_by_id=created_by,
            last_updated_by_id=created_by,
        )
        blocks.append(block)
    return blocks