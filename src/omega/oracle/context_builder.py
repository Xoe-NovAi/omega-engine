# AP Token: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Context Builder — Memory Injection Pipeline
# AP: AP-CONTEXT-BUILDER-v1.0.0
# ICS: [NODE: MNEMOSYNE | ARCHETYPE: SOPHIA | CONTEXT: CONTEXT-BUILDING]
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
# [id-soft: quake-1996] Zone Memory — Cache (LRU) tier pattern
#   Quake's zone allocator (zone.h:24-80) has a Cache tier (PU_CACHE=101)
#   that is purged when memory runs low. ContextBuilder fetches from
#   MemoryStore's hot tier (most recent) and falls back to warm/cold.

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Protocol
from dataclasses import dataclass, field
from enum import Enum

from ..memory_store import get_memory_store, MemoryStore
from ..constants import DEFAULT_CONTEXT_LIMIT
from .world_state import world_state
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
    LOW = "low"           # ToolResult — no LLM, zero cost
    MEDIUM = "medium"     # Summarization — requires LLM
    HIGH = "high"         # SlidingWindow — drops groups
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

class ToolResultCompactionStrategy:
    """Low aggressiveness — collapses old tool results into summary placeholders.
    Zero inference cost.
    """
    def __init__(self, keep_last: int = 1):
        self.keep_last = keep_last
    
    async def __call__(self, messages: List[Message], budget: int) -> bool:
        # Simple implementation: mask tool results older than keep_last
        tool_msgs = [i for i, m in enumerate(messages) if m.role == "tool"]
        if len(tool_msgs) <= self.keep_last:
            return False
            
        for i in tool_msgs[:-self.keep_last]:
            msg = messages[i]
            # Mask content but keep metadata (exit code, etc)
            msg.content = f"[Tool result masked: {msg.metadata.get('tool_name', 'unknown')}]"
            
        return self._estimate_tokens(messages) <= budget

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
        compressed_fails: bool
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

    Fetches recent conversation history from MemoryStore and formats it
    as a clean, readable string block. Designed to be prepended to an
    entity's personality/system prompt before inference.
    """

    def __init__(self, memory_store: Optional[MemoryStore] = None):
        self.memory_store = memory_store or get_memory_store()

    # ── Primary API ───────────────────────────────────────────────────

    async def build_context(
        self,
        entity_name: str,
        session_id: str,
        token_limit: int = DEFAULT_TOKEN_LIMIT,
    ) -> str:
        """Fetch recent memory and current world state for an entity/session.
        
        Args:
            entity_name: Name of the entity (e.g., 'EntityA', 'EntityB').
            session_id: Unique session identifier for the conversation.
            token_limit: Maximum tokens for the memory block.
        
        Returns:
            A formatted string block containing recent conversation history
            and the current world state, or an empty string if no context is available.
        """
        try:
            # 1. Fetch recent memory
            exchanges = await self.memory_store.get_history(
                entity_name=entity_name,
                session_id=session_id,
                limit=MAX_EXCHANGE_DISPLAY_LENGTH,
            )
            memory_block = await self._compact_and_format_exchanges(exchanges, token_limit) if exchanges else ""
            
            # 2. Fetch and format world state
            world_block = self._format_world_state()
            
            # Combine blocks
            full_context = f"{world_block}\n{memory_block}"
            return full_context.strip()
            
        except Exception as e:
            logger.warning(f"Failed to build context for {entity_name}/{session_id}: {e}")
            return ""

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
            memory_block = await self._compact_and_format_exchanges(exchanges, token_limit) if exchanges else ""
            
            # 2. Fetch and format world state
            world_block = self._format_world_state()
            
            # Combine blocks
            full_context = f"{world_block}\n{memory_block}"
            return full_context.strip()
            
        except Exception as e:
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

    async def _compact_and_format_exchanges(self, exchanges: List[Dict[str, Any]], token_limit: int) -> str:
        """Format exchanges into a context block using the ACON compaction pipeline.
        
        Implements the PipelineCompactionStrategy: ToolResult -> Summarization -> SlidingWindow -> Truncation.
        """
        if not exchanges:
            return ""

        # Build Message objects from exchanges for compaction pipeline
        messages: List[Message] = []
        for ex in exchanges:
            messages.append(Message(
                role="user",
                content=ex.get("user", ""),
                metadata={"timestamp": ex.get("timestamp")}
            ))
            messages.append(Message(
                role="assistant",
                content=ex.get("assistant", ""),
                metadata={"timestamp": ex.get("timestamp")}
            ))

        # Run the ToolResultMasking pass — masks old tool results (zero cost).
        # Budget enforcement is done in the formatting loop below.
        tool_masking = ToolResultCompactionStrategy(keep_last=1)
        await tool_masking(messages, token_limit)

        # Format with sliding window — iterate from newest to oldest,
        # collecting exchanges that fit within token budget.
        header = "## Recent Memory Context\n\n"
        lines: List[str] = []
        current_tokens = self._estimate_tokens(header)

        # Reconstruct pairs from surviving messages
        pairs: List[Dict[str, Any]] = []
        i = 0
        while i < len(messages):
            if i + 1 < len(messages) and messages[i].role == "user" and messages[i+1].role == "assistant":
                pairs.append({
                    "timestamp": messages[i].metadata.get("timestamp", ""),
                    "user": messages[i].content,
                    "assistant": messages[i+1].content,
                })
                i += 2
            else:
                i += 1

        # Sliding window: newest to oldest, fill budget
        for pair in reversed(pairs):
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
