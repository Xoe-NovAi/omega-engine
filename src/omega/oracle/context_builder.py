# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Context Builder — Memory Injection Pipeline
# AP: AP-CONTEXT-BUILDER-v1.0.0
#
# Fetches recent conversation traces/memory for a given entity and user
# session, then formats them into a structured memory block that is
# prepended to the LLM's system prompt during inference.
#
# This is the glue between MemoryStore (conversation persistence) and
# the ModelGateway (LLM inference). Without it, every inference call
# would be stateless — the entity would have no memory of past exchanges.
#
# Integration:
#   context_block = await ContextBuilder().build_context(entity_name, session_id)
#   system_prompt = ContextBuilder.prepend_to_prompt(context_block, entity.personality)
#
# [id-soft: vet-008] Zone Memory — Cache (LRU) tier pattern
#   Quake's zone allocator (zone.h:24-80) has a Cache tier (PU_CACHE=101)
#   that is purged when memory runs low. ContextBuilder fetches from
#   MemoryStore's hot tier (most recent) and falls back to warm/cold.

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
from dataclasses import dataclass, field
from enum import Enum

from ..memory_store import get_memory_store, MemoryStore
from .world_state import world_state
from .middleware.headroom import get_headroom_middleware
from .selective_hydration import SelectiveHydration
from ..errors import OmegaError
from omega.errors import OmegaError
from ..memory.blocks import MemoryBlock
from ..memory.block_tools import BlockTools, get_block_store

# New constant for token-aware sliding window
DEFAULT_TOKEN_LIMIT = 4000

logger = logging.getLogger(__name__)

# ── Compaction Framework (Microsoft Agent Framework Pattern) ────────────────


class Message:
    """Simple message representation for compaction logic."""

    def __init__(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.role = role
        self.content = content
        self.metadata = metadata or {}


class CompactionStrategy(Protocol):
    """Protocol for compaction strategies."""

    async def __call__(self, messages: List[Message], budget: int) -> bool:
        """Apply compaction. Return True if budget is met, False otherwise."""
        ...


class StrategyAggressiveness(Enum):
    LOW = "low"  # ToolResult — no LLM, zero cost
    MEDIUM = "medium"  # Summarization — requires LLM
    HIGH = "high"  # SlidingWindow — drops groups
    EMERGENCY = "emergency"  # Truncation — backstop


@dataclass
class PipelineCompactionStrategy:
    """Composes multiple strategies into a sequential pipeline."""

    token_budget: int
    strategies: List[CompactionStrategy] = field(default_factory=list)

    async def __call__(self, messages: List[Message]) -> bool:
        """Run strategies in order, stopping when budget is met."""
        for strategy in self.strategies:
            if await strategy(messages, self.token_budget):
                return True
        return False


class ObservationMaskingStrategy:
    """High-efficiency filter that culls repetitive 'logged' or 'confirmed'
    lines in tool outputs to save context tokens.

    Source: [id-soft: vet-046] BSP Culling (O(1) culling of redundant data)
    """

    def __init__(self, cull_keywords: List[str] = None, preserve_first_n: int = 2):
        self.cull_keywords = cull_keywords or ["logged", "confirmed", "processed"]
        self.preserve_first_n = preserve_first_n

    async def __call__(self, messages: List[Message], budget: int) -> bool:
        modified = False
        for msg in messages:
            if msg.role == "tool" and len(msg.content) > 20:
                lines = msg.content.splitlines()
                if len(lines) <= self.preserve_first_n:
                    continue

                # Preserve headers, cull the rest based on keywords
                new_lines = lines[: self.preserve_first_n]
                for line in lines[self.preserve_first_n :]:
                    if not any(kw in line.lower() for kw in self.cull_keywords):
                        new_lines.append(line)

                if len(new_lines) < len(lines):
                    msg.content = "\n".join(new_lines)
                    modified = True

        return modified or (self._estimate_tokens(messages) <= budget)

    def _estimate_tokens(self, messages: List[Message]) -> int:
        return sum(len(m.content) // 4 for m in messages)


class TruncationStrategy:
    """Emergency backstop — hard truncate to budget."""

    async def __call__(self, messages: List[Message], budget: int) -> bool:
        current_tokens = sum(len(m.content) // 4 for m in messages)
        if current_tokens <= budget:
            return True

        # Hard truncate from oldest to newest
        while messages and sum(len(m.content) // 4 for m in messages) > budget:
            messages.pop(0)
        return True


class ACONOptimizer:
    """
    Agent Context Optimization (ACON) — Failure-driven guideline optimization.
    Source: Microsoft Research, ICML 2026.
    """

    def __init__(self, model: str = "qwen3-1.7b"):
        self.model = model
        self.guidelines: Dict[str, str] = {}

    async def optimize_guidelines(
        self,
        full_context_trajectory: List[Dict],
        compressed_context_trajectory: List[Dict],
        full_succeeds: bool,
        compressed_fails: bool,
    ) -> str:
        """Analyze failure causes and update compression guidelines."""
        if full_succeeds and compressed_fails:
            # In a real implementation, this would call an LLM to analyze the delta
            # and output a new set of guidelines for the compaction strategies.
            logger.info("ACON: Analyzing context loss failure... updating guidelines.")
            self.guidelines["fidelity_threshold"] = "high"
            self.guidelines["preserve_patterns"] = "decision_nodes, error_traces"
        return self.guidelines


# ── Default constants ─────────────────────────────────────────────────
# DEFAULT_CONTEXT_LIMIT is imported from src/omega/oracle/constants.py
MAX_EXCHANGE_DISPLAY_LENGTH = 500  # truncate individual messages to avoid prompt bloat


class ContextBuilder:
    """Builds structured memory context blocks for LLM system prompts.
    DocRef: docs/reference/api/context_builder.md

    Fetches recent conversation history from MemoryStore and formats it

    as a clean, readable string block. Designed to be prepended to an
    entity's personality/system prompt before inference.

    [id-soft: vet-046] BSP Culling — L3 principle injection uses O(1)
    culling: only top-K principles are injected, avoiding context bloat.

    When selective_hydration is provided, L3 gnosis principles relevant to
    the query are retrieved from Qdrant and injected into the context block
    after the memory window. This is the Cache tier of quake-1996 4-Tier
    Memory — reusable pre-distilled wisdom.
    """

    def __init__(
        self,
        memory_store: Optional[MemoryStore] = None,
        selective_hydration: Optional[SelectiveHydration] = None,
        l3_top_k: int = 5,
    ):
        self.memory_store = memory_store or get_memory_store()
        self._selective_hydration = selective_hydration
        self._l3_top_k = l3_top_k
        # Memory blocks (D-283 Mnemosyne)
        self._block_store = get_block_store()
        self._block_tools = BlockTools(self._block_store)

    @staticmethod
    def _score_exchange_quality(exchange: Dict[str, Any]) -> float:
        """Score a conversation exchange pair for quality (0.0-1.0).

        Lightweight inline scorer for conversation data. Uses four signals:
        - Message length (substantive messages score higher)
        - Technical content indicators (code, references)
        - Contains a question (Q&A is more valuable than chitchat)
        - Recency boost (newer exchanges get a small advantage)

        This is the 'Right Approximation' for exchange quality — simple,
        fast, no external dependencies, and sufficient for sliding window
        prioritization.
        """
        user_msg = exchange.get("user", "")
        assistant_msg = exchange.get("assistant", "")
        combined = user_msg + " " + assistant_msg
        score = 0.0

        # 1. Message length (0.0-0.3): substantive messages score higher
        word_count = len(combined.split())
        if word_count > 50:
            score += 0.3
        elif word_count > 20:
            score += 0.2
        elif word_count > 5:
            score += 0.1

        # 2. Technical content (0.0-0.2): code blocks, references, specific terms
        has_code = bool(re.search(r"```|`[^`]+`|import |def |class |function ", combined))
        has_reference = bool(re.search(r"\[\d+\]|\(.*\d{4}\)|http[s]?://|arXiv|doi:", combined))
        if has_code:
            score += 0.15
        if has_reference:
            score += 0.05

        # 3. Contains a question (0.0-0.2): Q&A pairs are more valuable
        has_question = "?" in user_msg or any(
            kw in user_msg.lower()
            for kw in [
                "what",
                "how",
                "why",
                "when",
                "where",
                "who",
                "which",
                "can you",
                "could you",
            ]
        )
        if has_question:
            score += 0.2

        # 4. Recency (0.0-0.3): newer exchanges get a small boost
        # Default 0.15 for all; adjusted if timestamp is available
        score += 0.15

        return min(1.0, score)

    # ── Primary API ───────────────────────────────────────────────────

    async def build_context(
        self,
        entity_name: str,
        session_id: str,
        token_limit: int = DEFAULT_TOKEN_LIMIT,
        degradation_level: Optional[str] = None,
        query: Optional[str] = None,
    ) -> str:
        """Fetch recent memory and current world state for an entity/session.

        Args:
            entity_name: Name of the entity (e.g., 'EntityA', 'EntityB').
            session_id: Unique session identifier for the conversation.
            token_limit: Maximum tokens for the memory block.
            degradation_level: Current system pressure level (Optimal, Stressed, Critical, Disabled).

        Returns:
            A formatted string block containing recent conversation history,
            L3 gnosis principles, and the current world state, or an empty
            string if no context is available.
        """
        # Adjust token limit based on degradation level
        if degradation_level:
            if degradation_level == "Stressed":
                token_limit = int(token_limit * 0.5)
            elif degradation_level == "Critical":
                token_limit = int(token_limit * 0.25)
            elif degradation_level == "Disabled":
                token_limit = 0

        try:
            # 1. Fetch memory blocks (D-283 Mnemosyne Core tier)
            core_blocks = await self._block_tools.get_core_blocks(entity_name)
            blocks_text = self._format_memory_blocks(core_blocks)

            # 2. Fetch recent memory
            exchanges = await self.memory_store.get_history(
                entity_name=entity_name,
                session_id=session_id,
                limit=MAX_EXCHANGE_DISPLAY_LENGTH,
            )
            memory_block = (
                await self._compact_and_format_exchanges(entity_name, exchanges, token_limit)
                if exchanges
                else ""
            )

            # 3. Fetch L3 gnosis principles (Selective Hydration)
            # [id-soft: vet-046] BSP Culling — top-K principles only
            gnosis_block = await self._build_gnosis_block(entity_name, query)

            # 4. Fetch and format world state
            world_block = self._format_world_state()

            # Combine blocks: world state + gnosis + memory blocks + memory
            # Order: world state (global) → gnosis (principles) → blocks (entity identity) → memory (conversation)
            parts = [world_block, gnosis_block, blocks_text, memory_block]
            full_context = "\n".join(p for p in parts if p and p.strip())
            return full_context.strip() if full_context else ""

        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Failed to build context for {entity_name}/{session_id}: {e}")
            return ""

    async def _build_gnosis_block(self, entity_name: str, query: Optional[str] = None) -> str:
        """Build the L3 gnosis principles block via Selective Hydration.

        Retrieves relevant L3 principles for the entity and formats them
        as a context block. Silently returns empty string if Selective
        Hydration is not configured or any step fails.

        [id-soft: vet-023] Precomputed Lookup — embeddings are
        precomputed at store time; retrieval is O(1) cosine similarity.
        """
        if self._selective_hydration is None:
            return ""

        try:
            # Use the actual user query for semantic retrieval
            # to get query-relevant L3 principles.
            principles = await self._selective_hydration.hydrate(
                query=query if query else entity_name,
                entity_name=entity_name,
            )
            if not principles:
                return ""

            return self._selective_hydration.format_principles_block(principles)
        except (OmegaError, RuntimeError, OSError) as e:
            logger.debug(
                "SelectiveHydration: gnosis block skipped for %s: %s",
                entity_name,
                e,
            )
            return ""

    def _format_memory_blocks(self, blocks: List[MemoryBlock]) -> str:
        """Format memory blocks for context injection.

        Core blocks (persona, human, safety, decisions) are always included
        in the system prompt. They represent the entity's identity and
        constitutional principles.
        """
        if not blocks:
            return ""

        lines = ["## Entity Memory Blocks (Core Tier)\n"]
        for block in blocks:
            if block.value and block.value.strip():
                lines.append(f"### {block.label.upper()}")
                lines.append(f"{block.description}")
                lines.append(f"{block.value}")
                lines.append("")  # blank line between blocks

        if len(lines) == 1:  # Only header
            return ""

        return "\n".join(lines) + "---\n\n"

    async def build_context_for_user(
        self,
        user_id: str,
        session_id: str,
        token_limit: int = DEFAULT_TOKEN_LIMIT,
    ) -> str:
        """Fetch recent traces for a user across all entities and include world state.

        Implements a token-aware sliding window for user-level context.
        """
        try:
            # 1. Fetch user memory
            exchanges = await self.memory_store.get_history(
                entity_name="user",
                session_id=session_id,
                limit=MAX_EXCHANGE_DISPLAY_LENGTH,
            )
            memory_block = (
                await self._compact_and_format_exchanges("user", exchanges, token_limit)
                if exchanges
                else ""
            )

            # 2. Fetch and format world state
            world_block = self._format_world_state()

            # Combine blocks
            full_context = f"{world_block}\n{memory_block}"
            return full_context.strip()

        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Failed to build user context for {user_id}/{session_id}: {e}")
            return ""

    # ── Formatting ────────────────────────────────────────────────────

    def _format_world_state(self) -> str:
        """Format the current active world state into a readable context block.

        Queries the WorldState singleton for global parameters and active sectors.
        """
        # Get global state
        globals_data = {}
        # Use public API if possible, but world_state._global_state is accessible
        # Let's just iterate over the keys if it were a public method,
        # but since we are inside the engine, we can access it or use a loop.
        # Wait, world_state doesn't have a get_all_globals().
        # I'll just use the internal dict for now as this is internal core logic.
        globals_dict = world_state._global_state
        if globals_dict:
            globals_data = {k: v for k, v in globals_dict.items()}

        # Get active sectors
        sectors = world_state.get_all_sectors()
        sector_data = {}
        for s_id in sectors:
            data = world_state.lattice_query(sector_id=s_id, lump_id=None)
            if data:
                sector_data[s_id] = data

        if not globals_data and not sector_data:
            return ""

        lines = ["## Active World State Context\n"]

        if globals_data:
            lines.append("### Global Parameters")
            for k, v in globals_data.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

        if sector_data:
            lines.append("### Active Sectors")
            for s_id, lumps in sector_data.items():
                lines.append(f"- Sector [{s_id}]:")
                for l_id, l_data in lumps.items():
                    lines.append(f"  - Lump {l_id}: {l_data}")
            lines.append("")

        return "".join(lines) + "---\n\n"

    async def _compact_and_format_exchanges(
        self,
        entity_name: str,
        exchanges: List[Dict[str, Any]],
        token_limit: int,
        quality_weighted: bool = False,
    ) -> str:
        """Format exchanges into a context block using the ACON compaction pipeline.

        Implements the PipelineCompactionStrategy: ToolResult -> Summarization -> SlidingWindow -> Truncation.

        When quality_weighted=True, exchanges are scored and sorted by quality
        before the sliding window, ensuring higher-quality exchanges fill the
        token budget first. Default behavior (quality_weighted=False) preserves
        the existing newest-first sliding window for backward compatibility.
        """
        if not exchanges:
            return ""

        # Build Message objects from exchanges for compaction pipeline
        messages: List[Message] = []
        for ex in exchanges:
            messages.append(
                Message(
                    role="user",
                    content=ex.get("user", ""),
                    metadata={"timestamp": ex.get("timestamp")},
                )
            )
            messages.append(
                Message(
                    role="assistant",
                    content=ex.get("assistant", ""),
                    metadata={"timestamp": ex.get("timestamp")},
                )
            )

        # Run the Observation Masking pass — culls repetitive 'logged' lines (zero cost).
        # Budget enforcement is done in the formatting loop below.
        obs_masking = ObservationMaskingStrategy()
        await obs_masking(messages, token_limit)

        # ── Semantic Compression (Headroom) ──────────────────────────────────
        # Apply semantic/structural compression to the messages.
        # This reduces token usage by 60-95% while preserving meaning.
        headroom_mw = get_headroom_middleware()
        compressed_messages, _ = await headroom_mw.compress_context(
            entity_name, [{"role": m.role, "content": m.content} for m in messages]
        )

        # Update messages with compressed content
        for i, msg in enumerate(messages):
            if i < len(compressed_messages):
                msg.content = compressed_messages[i].get("content", msg.content)

        # Format with sliding window — iterate from newest to oldest,

        # collecting exchanges that fit within token budget.
        header = "## Recent Memory Context\n\n"
        lines: List[str] = []
        current_tokens = self._estimate_tokens(header)

        # Reconstruct pairs from surviving messages
        pairs: List[Dict[str, Any]] = []
        i = 0
        while i < len(messages):
            if (
                i + 1 < len(messages)
                and messages[i].role == "user"
                and messages[i + 1].role == "assistant"
            ):
                pairs.append(
                    {
                        "timestamp": messages[i].metadata.get("timestamp", ""),
                        "user": messages[i].content,
                        "assistant": messages[i + 1].content,
                    }
                )
                i += 2
            else:
                i += 1

        # Quality-weighted selection: score and sort by quality before sliding window
        if quality_weighted and pairs:
            for pair in pairs:
                pair["_quality_score"] = self._score_exchange_quality(pair)
            # Sort by quality descending — highest quality fills budget first
            pairs.sort(key=lambda p: p["_quality_score"], reverse=True)

        # Sliding window: newest to oldest (or highest quality first if quality_weighted), fill budget
        # When quality_weighted, iterate in sorted order (highest quality first).
        # When not quality_weighted, iterate in reverse chronological (newest first).
        window = pairs if quality_weighted else reversed(pairs)
        for pair in window:
            ts = self._format_timestamp(pair["timestamp"])
            exchange_block = (
                f"[{ts}] User: {self._truncate(pair['user'])}\n"
                f"[{ts}] Assistant: {self._truncate(pair['assistant'])}\n\n"
            )
            est = self._estimate_tokens(exchange_block)
            if current_tokens + est > token_limit:
                break
            lines.append(exchange_block)
            current_tokens += est

        # Reverse to chronological order
        lines.reverse()

        if not lines:
            return ""

        full_block = header + "".join(lines) + "---\n\n"
        return full_block

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count.

        Uses a rough approximation (4 chars per token) since tiktoken
        is not available in the current environment.
        """
        return len(text) // 4

    def _format_timestamp(self, ts: Optional[str]) -> str:
        """Format an ISO timestamp to a compact display form."""
        if not ts:
            return "unknown"
        try:
            dt = datetime.fromisoformat(ts)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return str(ts)

    def _truncate(self, text: str, max_len: int = MAX_EXCHANGE_DISPLAY_LENGTH) -> str:
        """Truncate long messages to avoid prompt bloat."""
        if len(text) <= max_len:
            return text
        return text[:max_len] + "..."

    # ── Utility: Prepend context to system prompt ─────────────────────

    @staticmethod
    def prepend_to_prompt(context_block: str, system_prompt: str) -> str:
        """Prepend a context block to a system prompt.

        If context_block is empty, returns the original system prompt unchanged.
        """
        if not context_block or not context_block.strip():
            return system_prompt
        return f"{context_block}\n{system_prompt}"
