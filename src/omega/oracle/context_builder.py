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
        limit: int = DEFAULT_CONTEXT_LIMIT,
    ) -> str:
        """Fetch recent memory for an entity/session and format as context block.

        Args:
            entity_name: Name of the entity (e.g., 'Sekhmet', 'Brigid').
            session_id: Unique session identifier for the conversation.
            limit: Maximum number of recent exchanges to include.

        Returns:
            A formatted string block of recent conversation history,
            or an empty string if no memory is available.
        """
        try:
            exchanges = await self.memory_store.get_history(
                entity_name=entity_name,
                session_id=session_id,
                limit=limit,
            )
        except Exception as e:
            logger.warning(f"Failed to fetch memory for {entity_name}/{session_id}: {e}")
            return ""

        if not exchanges:
            return ""

        return self._format_exchanges(exchanges)

    async def build_context_for_user(
        self,
        user_id: str,
        session_id: str,
        limit: int = DEFAULT_CONTEXT_LIMIT,
    ) -> str:
        """Fetch recent traces for a user across all entities.

        This is a broader context fetch — it traces user-level interactions
        rather than entity-scoped ones. Useful for the Oracle to have
        cross-entity awareness of a user's recent activity.

        Args:
            user_id: The user identifier.
            session_id: Current session identifier.
            limit: Maximum number of recent trace entries.

        Returns:
            A formatted string block of recent user activity,
            or an empty string if no traces are available.
        """
        try:
            # Fetch memory from the orchestrator/scoped user session
            exchanges = await self.memory_store.get_history(
                entity_name="user",
                session_id=session_id,
                limit=limit,
            )
        except Exception as e:
            logger.warning(f"Failed to fetch user context for {user_id}/{session_id}: {e}")
            return ""

        if not exchanges:
            return ""

        return self._format_exchanges(exchanges)

    # ── Formatting ────────────────────────────────────────────────────

    def _format_exchanges(self, exchanges: List[Dict[str, Any]]) -> str:
        """Format a list of conversation exchanges into a context string block.

        Each exchange is rendered as:
          [timestamp] User: message
          [timestamp] Entity: response

        Returns a block ready to prepend to a system prompt.
        """
        lines: List[str] = []
        lines.append("## Recent Memory Context")
        lines.append("")

        for exchange in exchanges:
            timestamp = self._format_timestamp(exchange.get("timestamp"))
            user_msg = self._truncate(exchange.get("user", ""))
            assistant_msg = self._truncate(exchange.get("assistant", ""))

            lines.append(f"[{timestamp}] User: {user_msg}")
            lines.append(f"[{timestamp}] Assistant: {assistant_msg}")
            lines.append("")

        # Append a clear separator
        lines.append("---")
        lines.append("")

        return "\n".join(lines)

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
