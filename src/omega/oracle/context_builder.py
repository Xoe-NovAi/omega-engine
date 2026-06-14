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
from typing import Any, Dict, List, Optional

from ..memory_store import get_memory_store, MemoryStore
from ..constants import DEFAULT_CONTEXT_LIMIT
from .world_state import world_state
# New constant for token-aware sliding window
DEFAULT_TOKEN_LIMIT = 4000 


logger = logging.getLogger(__name__)

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
            memory_block = self._format_exchanges_sliding_window(exchanges, token_limit) if exchanges else ""
            
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
            memory_block = self._format_exchanges_sliding_window(exchanges, token_limit) if exchanges else ""
            
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

    def _format_exchanges_sliding_window(self, exchanges: List[Dict[str, Any]], token_limit: int) -> str:
        """Format exchanges into a context block using a sliding token window.
        
        Iterates from newest to oldest, collecting exchanges that fit within
        the token budget, then renders them in chronological order.
        """
        lines: List[str] = []
        current_tokens = 0
        
        # get_history() returns exchanges in chronological order (oldest first).
        # We iterate in reverse to fill the token budget from the newest
        # exchange backwards, keeping the most recent context.
        
        # Header tokens (est)
        header = "## Recent Memory Context\n\n"
        current_tokens += self._estimate_tokens(header)
        
        # Iterate from newest to oldest; collect until token budget is hit
        for exchange in reversed(exchanges):
            timestamp = self._format_timestamp(exchange.get("timestamp"))
            user_msg = self._truncate(exchange.get("user", ""))
            assistant_msg = self._truncate(exchange.get("assistant", ""))
            
            exchange_block = f"[{timestamp}] User: {user_msg}\n[{timestamp}] Assistant: {assistant_msg}\n\n"
            est_tokens = self._estimate_tokens(exchange_block)
            
            if current_tokens + est_tokens > token_limit:
                break
            
            lines.append(exchange_block)
            current_tokens += est_tokens
        
        # lines is newest-first; reverse to chronological order for LLM readability
        lines.reverse()
            
        if not lines:
            return ""
            
        # Prepend header and append separator
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
