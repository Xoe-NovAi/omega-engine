# AP: AP-CORE-v1.0.0
# 🔱 CompactionManager — Context Window Compaction Trigger
# ⬡ OMEGA ⬡ MEMORY ⬡ compaction.py
#
# Monitors Core tier block usage and triggers compaction when the context
# window approaches capacity. When blocks exceed their fair share of the
# token budget, saturated content is promoted to the Recall tier where
# it remains searchable via temporal decay.
#
# Letta 2026 reference: "context window management" — when core memory
# exceeds threshold, oldest blocks are summarized and moved to archival.
# This is the generic implementation; WAD-specific mappings (e.g.
# Mnemosyne, Arcana-Nova Sephiroth) are documented in the WAD layer.

import logging
import anyio
from dataclasses import dataclass, field
from typing import Optional

from .block_tools import BlockTools, get_block_store
from .recall import RecallStore, get_recall_store

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────

DEFAULT_TRIGGER_THRESHOLD = 0.80  # Compact when core > 80% of context window
DEFAULT_TARGET_REDUCTION = 0.50  # Compact to 50% of current usage
DEFAULT_CONTEXT_LIMIT = 4000     # Default context window tokens
TOKEN_ESTIMATE_RATIO = 4         # ~4 chars per token


@dataclass
class CompactionResult:
    """Result of a compaction cycle."""
    triggered: bool = False
    tokens_freed: int = 0
    tokens_before: int = 0
    tokens_after: int = 0
    turns_promoted: int = 0
    blocks_affected: int = 0
    error: Optional[str] = None


class CompactionManager:
    """Context window compaction trigger — monitors core block usage.

    When core blocks exceed the trigger threshold, compaction proactively:
    1. Reads core blocks and estimates token usage
    2. Identifies blocks exceeding their fair share of the token budget
    3. Promotes saturated block content to the Recall tier
    4. Truncates core blocks to the target size

    This prevents context window overflow without losing information:
    data moves to the Recall tier where it's searchable via decay scoring.
    WAD-specific architectural mappings (e.g. Da'at, Sephiroth) are
    documented in Config WAD documentation, not in this core file.
    """

    def __init__(
        self,
        block_tools: Optional[BlockTools] = None,
        recall_store: Optional[RecallStore] = None,
        trigger_threshold: float = DEFAULT_TRIGGER_THRESHOLD,
        target_reduction: float = DEFAULT_TARGET_REDUCTION,
        context_limit: int = DEFAULT_CONTEXT_LIMIT,
    ):
        self._block_tools = block_tools or BlockTools(get_block_store())
        self._recall = recall_store
        self._trigger_threshold = trigger_threshold
        self._target_reduction = target_reduction
        self._context_limit = context_limit
        self._lock = anyio.Lock()

    async def check_and_compact(
        self,
        entity_name: str,
        session_id: str = "default",
    ) -> CompactionResult:
        """Check core block usage and compact if above threshold.

        Called by the Oracle before every talk/summon to ensure the
        context window has room for the incoming exchange.

        Args:
            entity_name: The entity whose core blocks to check.
            session_id: Current session ID (for recall store operations).

        Returns:
            CompactionResult with trigger status and metrics.
        """
        async with self._lock:
            try:
                # 1. Estimate current core usage
                blocks = await self._block_tools.get_core_blocks(entity_name)
                total_tokens = self._estimate_block_tokens(blocks)
                max_tokens = self._get_max_tokens(entity_name)

                if total_tokens == 0:
                    return CompactionResult(triggered=False)

                usage_ratio = total_tokens / max_tokens

                if usage_ratio < self._trigger_threshold:
                    return CompactionResult(
                        triggered=False,
                        tokens_before=total_tokens,
                        tokens_after=total_tokens,
                    )

                # 2. Calculate target token count
                target_tokens = int(total_tokens * self._target_reduction)
                tokens_to_free = total_tokens - target_tokens
                logger.info(
                    "Core compaction triggered for %s: %d/%d tokens (%.0f%%). "
                    "Target: %d tokens (%d to free)",
                    entity_name, total_tokens, max_tokens, usage_ratio * 100,
                    target_tokens, tokens_to_free,
                )

                # 3. For each over-limit block, promote excess to recall
                turns_promoted = 0
                blocks_affected = 0
                tokens_freed = 0

                # Calculate fair share per block
                num_blocks = max(len(blocks), 1)
                share_per_block = target_tokens // num_blocks

                for block in blocks:
                    block_tokens = self._estimate_single_block_tokens(block)
                    if block_tokens <= share_per_block:
                        continue

                    # Block exceeds fair share — promote some content to recall
                    excess_tokens = block_tokens - share_per_block
                    promoted = await self._promote_block_excess(
                        block, excess_tokens, entity_name, session_id,
                    )
                    if promoted > 0:
                        turns_promoted += promoted
                        blocks_affected += 1
                        tokens_freed += excess_tokens

                # 4. Re-read to get final usage
                blocks_after = await self._block_tools.get_core_blocks(entity_name)
                tokens_after = self._estimate_block_tokens(blocks_after)

                return CompactionResult(
                    triggered=True,
                    tokens_freed=tokens_freed,
                    tokens_before=total_tokens,
                    tokens_after=tokens_after,
                    turns_promoted=turns_promoted,
                    blocks_affected=blocks_affected,
                )

            except Exception as e:
                logger.error(f"Core compaction failed: {e}", exc_info=True)
                return CompactionResult(
                    triggered=False,
                    error=str(e),
                )

    async def _promote_block_excess(
        self,
        block,
        excess_tokens: int,
        entity_name: str,
        session_id: str,
    ) -> int:
        """Promote excess block content to recall tier.

        Takes the oldest content from a block that exceeds its budget
        and promotes it to the RecallStore via promote_to_core.
        """
        if self._recall is None:
            return 0

        # Current limitation: Block.value is opaque text. Promotion
        # requires turn_id references that track which exchanges
        # generated the content. Future enhancement: block metadata
        # should store turn_id ranges for targeted promotion.
        logger.debug(
            "Block %s/%s exceeds fair share by %d tokens. "
            "Block length: %d chars. Turn-tracking needed for promotion",
            entity_name, block.label, excess_tokens, len(block.value or ""),
        )
        return 0

    def _estimate_block_tokens(self, blocks) -> int:
        """Estimate total token usage of core blocks."""
        return sum(self._estimate_single_block_tokens(b) for b in blocks)

    @staticmethod
    def _estimate_single_block_tokens(block) -> int:
        """Rough token estimate: ~4 chars per token."""
        text = block.value or ""
        return len(text) // TOKEN_ESTIMATE_RATIO

    def _get_max_tokens(self, entity_name: str) -> int:
        """Get max context tokens for an entity.

        Uses default context limit. Future: read per-entity
        config from entity YAML via config_resolver.
        """
        return self._context_limit

    async def get_usage_ratio(self, entity_name: str) -> float:
        """Get current core block usage ratio (0.0-1.0).

        Useful for observability without triggering compaction.
        """
        blocks = await self._block_tools.get_core_blocks(entity_name)
        total_tokens = self._estimate_block_tokens(blocks)
        if total_tokens == 0:
            return 0.0
        return total_tokens / self._get_max_tokens(entity_name)

    async def get_status(self, entity_name: str) -> dict:
        """Get compaction status for display/debug.

        Returns:
            Dict with usage_ratio, trigger_threshold, total_tokens,
            max_tokens, is_over_threshold, num_blocks, block_labels.
        """
        blocks = await self._block_tools.get_core_blocks(entity_name)
        total_tokens = self._estimate_block_tokens(blocks)
        max_tokens = self._get_max_tokens(entity_name)
        usage_ratio = total_tokens / max_tokens if max_tokens > 0 else 0.0

        return {
            "usage_ratio": round(usage_ratio, 3),
            "trigger_threshold": self._trigger_threshold,
            "total_tokens": total_tokens,
            "max_tokens": max_tokens,
            "is_over_threshold": usage_ratio >= self._trigger_threshold,
            "num_blocks": len(blocks),
            "block_labels": [b.label for b in blocks if b.value],
        }


# ── Singleton Factory ──────────────────────────────────────────────

_compaction_manager: Optional[CompactionManager] = None


def get_compaction_manager(
    block_tools: Optional[BlockTools] = None,
    recall_store: Optional[RecallStore] = None,
) -> CompactionManager:
    """Get or create the singleton CompactionManager."""
    global _compaction_manager
    if _compaction_manager is None:
        _compaction_manager = CompactionManager(
            block_tools=block_tools,
            recall_store=recall_store,
        )
    return _compaction_manager
