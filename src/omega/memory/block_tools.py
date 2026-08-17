# AP: AP-D283-MNEMOSYNE-v1.0.0
# 🔱 Block Tools — Agent Operations on Memory Blocks
# ⬡ OMEGA ⬡ MEMORY ⬡ block_tools.py
#
# Implements Letta 2026 block operations as agent-callable tools.
# Concurrency safety per Letta 2026:
#   - block_append: SAFE (append-only, minimal races)
#   - block_read: SAFE (read-only)
#   - block_replace: RISK (target may change)
#   - block_rethink: RISK (last-writer-wins, sleep-time only)
#   - block_summarize: RISK (last-writer-wins, sleep-time only)

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .blocks import (
    MemoryBlock,
    BlockCategory,
)
from .block_store import SQLiteBlockStore, get_sqlite_block_store

logger = logging.getLogger(__name__)


@dataclass
class BlockOperationResult:
    """Result of a block operation."""

    success: bool
    block: Optional[MemoryBlock] = None
    error: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None


# Use SQLite-backed store
BlockStore = SQLiteBlockStore
get_block_store = get_sqlite_block_store


# Global block store instance
_block_store: Optional[BlockStore] = None


def get_block_store() -> BlockStore:
    """Get or create the global block store."""
    global _block_store
    if _block_store is None:
        _block_store = BlockStore()
    return _block_store


class BlockTools:
    """
    Agent-facing tools for memory block manipulation.

    All operations enforce governance (read_only, governance_level) and
    return structured results for traceability.
    """

    def __init__(self, block_store: Optional[BlockStore] = None):
        self.store = block_store or get_block_store()

    async def block_read(
        self,
        label: str,
        requester_entity: str,
    ) -> BlockOperationResult:
        """Read a memory block value. Safe (read-only)."""
        block = await self.store.get_block(requester_entity, label)
        if not block:
            return BlockOperationResult(
                success=False, error=f"Block '{label}' not found or access denied"
            )
        if not block.can_read(requester_entity):
            return BlockOperationResult(
                success=False, error=f"Access denied: cannot read block '{label}'"
            )
        return BlockOperationResult(success=True, block=block)

    async def block_append(
        self,
        label: str,
        text: str,
        requester_entity: str,
        separator: str = "\n",
    ) -> BlockOperationResult:
        """
        Append text to a memory block. SAFE — append-only, minimal races.

        Concurrency: Multiple agents can append concurrently with minimal conflict.
        Uses optimistic locking at DB level.
        """
        block = await self.store.get_block(requester_entity, label)
        if not block:
            return BlockOperationResult(
                success=False, error=f"Block '{label}' not found or access denied"
            )
        if not block.can_write(requester_entity):
            return BlockOperationResult(
                success=False, error=f"Access denied: cannot write block '{label}'"
            )

        old_value = block.value
        new_value = (block.value + separator + text) if block.value else text

        # Check limit
        if len(new_value) > block.limit:
            # Truncate from beginning to fit (keep most recent)
            excess = len(new_value) - block.limit
            new_value = new_value[excess:]
            logger.warning(f"Block '{label}' truncated to fit limit ({block.limit} chars)")

        block.value = new_value
        block.updated_at = datetime.now(timezone.utc).isoformat()
        block.last_updated_by_id = requester_entity

        await self.store.upsert_block(block)
        return BlockOperationResult(
            success=True, block=block, old_value=old_value, new_value=new_value
        )

    async def block_replace(
        self,
        label: str,
        old_text: str,
        new_text: str,
        requester_entity: str,
    ) -> BlockOperationResult:
        """
        Replace substring in a memory block. RISK — target may change.

        Concurrency: Last-writer-wins. Use only with single-agent exclusive access
        (e.g., sleep-time agent). For shared blocks, prefer block_append.
        """
        block = await self.store.get_block(requester_entity, label)
        if not block:
            return BlockOperationResult(
                success=False, error=f"Block '{label}' not found or access denied"
            )
        if not block.can_write(requester_entity):
            return BlockOperationResult(
                success=False, error=f"Access denied: cannot write block '{label}'"
            )

        if old_text not in block.value:
            return BlockOperationResult(
                success=False, error=f"Text not found in block '{label}'", block=block
            )

        old_value = block.value
        block.value = block.value.replace(old_text, new_text, 1)  # Replace first occurrence only

        # Check limit
        if len(block.value) > block.limit:
            excess = len(block.value) - block.limit
            block.value = block.value[excess:]
            logger.warning(f"Block '{label}' truncated after replace to fit limit")

        block.updated_at = datetime.now(timezone.utc).isoformat()
        block.last_updated_by_id = requester_entity

        await self.store.upsert_block(block)
        return BlockOperationResult(
            success=True, block=block, old_value=old_value, new_value=block.value
        )

    async def block_rethink(
        self,
        label: str,
        requester_entity: str,
        summarizer_model: Optional[str] = None,
    ) -> BlockOperationResult:
        """
        Summarize/condense a near-limit block. RISK — last-writer-wins.

        Concurrency: MUST be called by single agent with exclusive access (sleep-time agent).
        Uses stronger model for consolidation.
        """
        block = await self.store.get_block(requester_entity, label)
        if not block:
            return BlockOperationResult(
                success=False, error=f"Block '{label}' not found or access denied"
            )
        if not block.can_write(requester_entity):
            return BlockOperationResult(
                success=False, error=f"Access denied: cannot write block '{label}'"
            )

        if not block.is_near_limit():
            return BlockOperationResult(
                success=False,
                error=f"Block '{label}' not near limit ({len(block.value)}/{block.limit})",
                block=block,
            )

        # In production, this would call an LLM to summarize
        # For now, simple heuristic: keep first 20% + last 60% (drop middle)
        old_value = block.value
        content = block.value
        keep_start = int(len(content) * 0.2)
        keep_end = int(len(content) * 0.6)
        summarized = content[:keep_start] + "\n[...SUMMARIZED...]\n" + content[-keep_end:]

        block.value = summarized
        block.updated_at = datetime.now(timezone.utc).isoformat()
        block.last_updated_by_id = requester_entity
        block.metadata["last_rethink"] = datetime.now(timezone.utc).isoformat()
        if summarizer_model:
            block.metadata["summarizer_model"] = summarizer_model

        await self.store.upsert_block(block)
        return BlockOperationResult(
            success=True, block=block, old_value=old_value, new_value=summarized
        )

    async def block_summarize(
        self,
        label: str,
        requester_entity: str,
        summarizer_model: Optional[str] = None,
        target_ratio: float = 0.5,
    ) -> BlockOperationResult:
        """
        Condense block to target ratio. RISK — last-writer-wins.

        Concurrency: MUST be called by single agent with exclusive access (sleep-time agent).
        """
        block = await self.store.get_block(requester_entity, label)
        if not block:
            return BlockOperationResult(
                success=False, error=f"Block '{label}' not found or access denied"
            )
        if not block.can_write(requester_entity):
            return BlockOperationResult(
                success=False, error=f"Access denied: cannot write block '{label}'"
            )

        old_value = block.value
        target_len = int(len(block.value) * target_ratio)

        if len(block.value) <= target_len:
            return BlockOperationResult(
                success=False, error=f"Block already smaller than target", block=block
            )

        # Simple heuristic: keep beginning and end, drop middle
        keep_each = target_len // 2
        summarized = block.value[:keep_each] + "\n[...SUMMARIZED...]\n" + block.value[-keep_each:]

        block.value = summarized
        block.updated_at = datetime.now(timezone.utc).isoformat()
        block.last_updated_by_id = requester_entity
        block.metadata["last_summarize"] = datetime.now(timezone.utc).isoformat()
        block.metadata["summarize_ratio"] = target_ratio
        if summarizer_model:
            block.metadata["summarizer_model"] = summarizer_model

        await self.store.upsert_block(block)
        return BlockOperationResult(
            success=True, block=block, old_value=old_value, new_value=summarized
        )

    async def block_insert(
        self,
        label: str,
        text: str,
        position: int,
        requester_entity: str,
    ) -> BlockOperationResult:
        """
        Insert text at specific position. SAFE for concurrent writes.

        Concurrency: Better than replace for concurrent access — position-based.
        """
        block = await self.store.get_block(requester_entity, label)
        if not block:
            return BlockOperationResult(
                success=False, error=f"Block '{label}' not found or access denied"
            )
        if not block.can_write(requester_entity):
            return BlockOperationResult(
                success=False, error=f"Access denied: cannot write block '{label}'"
            )

        old_value = block.value
        # Clamp position
        position = max(0, min(position, len(block.value)))
        new_value = block.value[:position] + text + block.value[position:]

        if len(new_value) > block.limit:
            excess = len(new_value) - block.limit
            new_value = new_value[excess:]
            logger.warning(f"Block '{label}' truncated after insert to fit limit")

        block.value = new_value
        block.updated_at = datetime.now(timezone.utc).isoformat()
        block.last_updated_by_id = requester_entity

        await self.store.upsert_block(block)
        return BlockOperationResult(
            success=True, block=block, old_value=old_value, new_value=new_value
        )

    async def list_blocks(self, requester_entity: str) -> List[MemoryBlock]:
        """List all blocks accessible to requester."""
        return await self.store.get_blocks_for_entity(requester_entity)

    async def create_essential_block(
        self,
        label: str,
        owner_entity: str,
        created_by: str,
        value: str = "",
    ) -> BlockOperationResult:
        """Create an essential block (persona, human, safety) from template."""
        from .blocks import create_essential_block

        try:
            block = create_essential_block(label, owner_entity, created_by, value)
            await self.store.upsert_block(block)
            return BlockOperationResult(success=True, block=block)
        except ValueError as e:
            return BlockOperationResult(success=False, error=str(e))

    async def create_domain_block(
        self,
        label: str,
        owner_entity: str,
        created_by: str,
        value: str = "",
    ) -> BlockOperationResult:
        """Create a domain-specific block from template."""
        from .blocks import create_domain_block

        try:
            block = create_domain_block(label, owner_entity, created_by, value)
            await self.store.upsert_block(block)
            return BlockOperationResult(success=True, block=block)
        except ValueError as e:
            return BlockOperationResult(success=False, error=str(e))

    async def get_core_blocks(self, requester_entity: str) -> List[MemoryBlock]:
        """Get all core-tier blocks (always in context) for an entity."""
        blocks = await self.store.get_blocks_for_entity(requester_entity)
        # Core blocks: read_only=True OR category=IDENTITY/STRATEGY with governance PRIVATE
        core = [
            b
            for b in blocks
            if b.read_only or b.category in (BlockCategory.IDENTITY, BlockCategory.STRATEGY)
        ]
        return core

    async def get_blocks_for_context(
        self, requester_entity: str, max_chars: int = 50000
    ) -> List[MemoryBlock]:
        """Get blocks formatted for context injection, respecting token budget."""
        core_blocks = await self.get_core_blocks(requester_entity)
        # Sort by priority: read_only first, then by category
        priority_order = {
            BlockCategory.IDENTITY: 0,
            BlockCategory.STRATEGY: 1,
            BlockCategory.PREFERENCE: 2,
            BlockCategory.GOAL: 3,
            BlockCategory.ASSUMPTION: 4,
            BlockCategory.EVENT: 5,
            BlockCategory.FAILURE: 6,
            BlockCategory.CONTEXT: 7,
        }
        core_blocks.sort(key=lambda b: (not b.read_only, priority_order.get(b.category, 99)))

        # Fit within budget
        total = 0
        selected = []
        for block in core_blocks:
            block_chars = len(block.value) + len(block.label) + 50  # overhead
            if total + block_chars > max_chars:
                break
            selected.append(block)
            total += block_chars

        return selected


# ── Standalone Tool Functions (for agent tool calling) ──────────────────────


async def block_read(label: str, requester_entity: str) -> BlockOperationResult:
    """Read a memory block. Safe (read-only)."""
    tools = BlockTools()
    return await tools.block_read(label, requester_entity)


async def block_append(
    label: str, text: str, requester_entity: str, separator: str = "\n"
) -> BlockOperationResult:
    """Append to a memory block. Safe (append-only)."""
    tools = BlockTools()
    return await tools.block_append(label, text, requester_entity, separator)


async def block_replace(
    label: str, old_text: str, new_text: str, requester_entity: str
) -> BlockOperationResult:
    """Replace text in a memory block. Risk (last-writer-wins)."""
    tools = BlockTools()
    return await tools.block_replace(label, old_text, new_text, requester_entity)


async def block_rethink(
    label: str, requester_entity: str, summarizer_model: Optional[str] = None
) -> BlockOperationResult:
    """Summarize a near-limit block. Risk (sleep-time only)."""
    tools = BlockTools()
    return await tools.block_rethink(label, requester_entity, summarizer_model)


async def initialize_entity_blocks(entity_name: str, created_by: str = "system") -> Dict[str, Any]:
    """
    Initialize all essential and domain blocks for a new entity.

    Returns dict with created block labels and any errors.
    """
    tools = BlockTools()
    results = {"essential": [], "domain": [], "errors": []}

    # Create essential blocks (persona, human, safety)
    for label in ["persona", "human", "safety"]:
        result = await tools.create_essential_block(label, entity_name, created_by)
        if result.success:
            results["essential"].append(label)
        else:
            results["errors"].append(f"{label}: {result.error}")

    # Create domain blocks
    for label in [
        "project-overview",
        "project-commands",
        "project-conventions",
        "project-architecture",
        "project-gotchas",
        "current-task",
        "context",
        "decisions",
        "failures",
    ]:
        result = await tools.create_domain_block(label, entity_name, created_by)
        if result.success:
            results["domain"].append(label)
        else:
            results["errors"].append(f"{label}: {result.error}")

    return results


# ── Sleep-Time Agent Pattern (Letta 2026) ──────────────────────────────────


class SleepTimeAgent:
    """
    Off-critical-path consolidation agent.

    Benefits:
    - No latency cost on primary responses
    - Stronger model for consolidation (can use larger/slower model)
    - Natural consolidation window (user not waiting)
    - Deduplication, summarization, contradiction invalidation

    Safety Rules (Letta 2026):
    - Sleep-time agents = UNTRUSTED writers for Persona/Safety blocks
    - Require SECOND-AGENT REVIEW before committing to core identity blocks
    - Version blocks and surface diffs in trace
    """

    def __init__(
        self,
        block_tools: BlockTools,
        stronger_model: str = "gemma-4-31b",  # Or any stronger model
        review_agent: Optional["SleepTimeAgent"] = None,
    ):
        self.tools = block_tools
        self.stronger_model = stronger_model
        self.review_agent = review_agent

    async def consolidate(
        self,
        transcript: List[Dict[str, str]],  # [{"role": "user/assistant", "content": "..."}]
        requester_entity: str,
    ) -> Dict[str, Any]:
        """
        Analyze transcript and write learned context to shared blocks.

        Returns summary of changes for trace.
        """
        changes = {}

        # 1. Extract learned patterns (would use stronger_model in production)
        learned = await self._extract_patterns(transcript)

        # 2. Write to appropriate blocks (append-safe)
        for block_label, content in learned.items():
            result = await self.tools.block_append(
                label=block_label,
                text=content,
                requester_entity=requester_entity,
            )
            if result.success:
                changes[block_label] = "appended"
            else:
                changes[block_label] = f"failed: {result.error}"

        # 3. Summarize near-limit blocks (sleep-time exclusive)
        blocks = await self.tools.list_blocks(requester_entity)
        for block in blocks:
            if block.is_near_limit() and not block.read_only:
                result = await self.tools.block_rethink(
                    label=block.label,
                    requester_entity=requester_entity,
                    summarizer_model=self.stronger_model,
                )
                if result.success:
                    changes[f"{block.label}_rethink"] = "summarized"

        # 4. Invalidate stale archival records (would query vector store)
        # await self._invalidate_stale_archival()

        return changes

    async def _extract_patterns(self, transcript: List[Dict[str, str]]) -> Dict[str, str]:
        """Extract patterns from transcript. In production, calls stronger_model."""
        # Placeholder — in production this would use the stronger model
        patterns = {}

        for turn in transcript:
            content = turn.get("content", "").lower()
            if "decided" in content or "decision" in content:
                current = patterns.setdefault("decisions", "")
                patterns["decisions"] = current + f"\n{turn['content'][:500]}"
            if "error" in content or "failed" in content or "bug" in content:
                current = patterns.setdefault("failures", "")
                patterns["failures"] = current + f"\n{turn['content'][:500]}"
            if "prefer" in content or "like" in content or "style" in content:
                current = patterns.setdefault("human", "")
                patterns["human"] = current + f"\n{turn['content'][:500]}"

        return patterns

    async def review_and_commit_core(
        self,
        block_label: str,
        proposed_value: str,
        requester_entity: str,
    ) -> BlockOperationResult:
        """
        Second-agent review for core identity blocks (persona, safety).

        Per Letta 2026: Sleep-time agents are UNTRUSTED writers for core blocks.
        Require second-agent review before committing.
        """
        if not self.review_agent:
            return BlockOperationResult(
                success=False, error="No review agent configured for core block commit"
            )

        # Review agent evaluates proposed change
        review = await self.review_agent._review_core_change(block_label, proposed_value)

        if review.get("approved", False):
            # Commit via replace (exclusive access)
            return await self.tools.block_replace(
                label=block_label,
                old_text="",  # Would need current value
                new_text=proposed_value,
                requester_entity=requester_entity,
            )
        else:
            return BlockOperationResult(
                success=False, error=f"Review rejected: {review.get('reason', 'unspecified')}"
            )

    async def _review_core_change(self, label: str, proposed: str) -> Dict[str, Any]:
        """Review agent evaluates proposed core block change."""
        # In production, this would use an LLM to evaluate
        # For now, simple heuristic
        return {
            "approved": len(proposed) > 10,
            "reason": "Auto-approved for demo" if len(proposed) > 10 else "Content too short",
        }
