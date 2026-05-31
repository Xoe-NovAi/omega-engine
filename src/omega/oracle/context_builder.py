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

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from ..memory_store import get_memory_store, MemoryStore
from ..constants import DEFAULT_CONTEXT_LIMIT
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
        """Fetch recent memory for an entity/session and format as a token-aware sliding window.

        Args:
            entity_name: Name of the entity (e.g., 'Sekhmet', 'Brigid').
            session_id: Unique session identifier for the conversation.
            token_limit: Maximum tokens for the memory block.

        Returns:
            A formatted string block of recent conversation history,
            or an empty string if no memory is available.
        """
        try:
            # Fetch a larger batch to perform sliding window truncation locally
            exchanges = await self.memory_store.get_history(
                entity_name=entity_name,
                session_id=session_id,
                limit=MAX_EXCHANGE_DISPLAY_LENGTH, # Use a safe upper bound for fetching
            )
        except Exception as e:
            logger.warning(f"Failed to fetch memory for {entity_name}/{session_id}: {e}")
            return ""

        if not exchanges:
            return ""
        
        # Implement sliding window based on token estimation
        return self._format_exchanges_sliding_window(exchanges, token_limit)

    async def build_context_for_user(
        self,
        user_id: str,
        session_id: str,
        token_limit: int = DEFAULT_TOKEN_LIMIT,
    ) -> str:
        """Fetch recent traces for a user across all entities.
        
        Implements a token-aware sliding window for user-level context.
        """
        try:
            exchanges = await self.memory_store.get_history(
                entity_name="user",
                session_id=session_id,
                limit=MAX_EXCHANGE_DISPLAY_LENGTH,
            )
        except Exception as e:
            logger.warning(f"Failed to fetch user context for {user_id}/{session_id}: {e}")
            return ""

        if not exchanges:
            return ""

        return self._format_exchanges_sliding_window(exchanges, token_limit)

    # ── Formatting ────────────────────────────────────────────────────

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
