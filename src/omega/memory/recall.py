# AP: AP-D283-MNEMOSYNE-v1.0.0
# 🔱 Recall Tier — Quality-Weighted Warm Memory with Power-Law Decay
# ⬡ OMEGA ⬡ MEMORY ⬡ recall.py
#
# Three-tier memory architecture (Letta 2026):
#   Core (HOT)    — Always in context: persona, human, safety, decisions (blocks.py)
#   Recall (WARM) — Conversation history with quality scoring + decay (this module)
#   Archival (COLD) — Arbitrary facts in vector + KV + graph storage (archival.py)
#
# The RecallStore wraps the existing MemoryStore with:
# 1. Quality scoring on every append (using ACON optimizer signals)
# 2. Power-law decay: score = base_quality * (1 + age_days)**(-alpha)
# 3. Quality-weighted window selection for context injection
# 4. Promote-to-core bridge via BlockTools only

import json
import logging
import math
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Literal

import anyio

from omega.errors import OmegaError
from omega.infra.sqlite_policy import get_sqlite_connection

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────

# Default decay alpha per block category (used if entity has no override)
DEFAULT_DECAY_ALPHA: float = 0.10

# Max exchange pairs returned from window()
MAX_WINDOW_PAIRS: int = 100

# Token estimation ratio (chars per token)
CHARS_PER_TOKEN: int = 4


# ── Dataclasses ─────────────────────────────────────────────────────

@dataclass
class Turn:
    """A single conversation turn with quality and decay metadata.

    The atomic unit of the Recall tier. Each user or assistant message
    is stored as one Turn with its base quality score and decay alpha.

    decayed_score is a computed property — always calculated live from
    base_quality, decay_alpha, and current age.
    """
    id: int = 0
    entity_name: str = ""
    session_id: str = ""
    turn_index: int = 0
    content: str = ""
    role: Literal["user", "assistant"] = "user"
    timestamp: str = ""
    base_quality: float = 0.5
    decay_alpha: float = DEFAULT_DECAY_ALPHA
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def age_days(self) -> float:
        """Calculate age in days from timestamp to now."""
        if not self.timestamp:
            return 0.0
        try:
            ts = datetime.fromisoformat(self.timestamp)
            now = datetime.now(timezone.utc)
            # Ensure both are timezone-aware
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            delta = now - ts
            return max(0.0, delta.total_seconds() / 86400.0)
        except (ValueError, TypeError):
            return 0.0

    @property
    def decayed_score(self) -> float:
        """Power-law decay: score = base * (1 + age_days)**(-alpha).

        Ebbinghaus-inspired power-law with configurable alpha per entity:
        - alpha=0.01: Near-permanent (identity, core knowledge)
        - alpha=0.10: Slow decay (strategic decisions)
        - alpha=0.25: Medium decay (goals, preferences)
        - alpha=0.60: Fast decay (scratchpad, ephemeral context)

        For age=0, returns base_quality unchanged.
        As age approaches infinity, score approaches 0.
        """
        age = self.age_days
        if age <= 0.0:
            return self.base_quality
        return self.base_quality * (1.0 + age) ** (-self.decay_alpha)


@dataclass
class ExchangePair:
    """A paired user-assistant exchange (matching MemoryStore format).

    Used as the return type for window() — ContextBuilder consumes
    exchanges as (user_content, assistant_content) pairs.
    """
    turn_index: int
    user_content: str
    assistant_content: str
    timestamp: str
    combined_quality: float = 0.0  # average of user + assistant decayed scores

    @property
    def estimated_tokens(self) -> int:
        """Rough token estimate (4 chars per token)."""
        return (len(self.user_content) + len(self.assistant_content)) // CHARS_PER_TOKEN


@dataclass
class DecayStats:
    """Statistics from a decay_pass() run."""
    turns_updated: int = 0
    entities_processed: int = 0
    average_decay: float = 0.0
    errors: List[str] = field(default_factory=list)


# ── RecallStore ─────────────────────────────────────────────────────

class RecallStore:
    """Quality-weighted warm memory with power-law decay.

    Stores conversation turns with base_quality scores in SQLite.
    On reads, applies power-law decay: score = base * (1 + age_days)**(-alpha).
    Window selection uses quality-weighted ordering within token budget.

    Design principles:
    - append() is O(1) — quality scored at write time
    - window() is O(n log n) — quality sorted at read time (context budget)
    - decay_pass() is batch O(n) — amortized over hourly interval
    - promote_to_core() bridges to BlockTools (does NOT write blocks directly)
    """

    def __init__(self, db_path: Optional[Path] = None, block_store: Optional[Any] = None):
        if db_path is None:
            from omega.memory_store import _get_memory_dir
            db_path = _get_memory_dir() / "omega_memory.db"
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._lock = anyio.Lock()
        self._write_lock = anyio.Lock()  # Serializes writes for thread safety
        self._initialized = False
        # In-memory cache of entity decay alphas
        self._entity_decay_cache: Dict[str, float] = {}
        # Optional block store for promote_to_core (defaults to global)
        self._block_store = block_store

    def _get_conn(self) -> sqlite3.Connection:
        """Get or create SQLite connection with profiled PRAGMA stack (FS-B4)."""
        if self._conn is None:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            # FS-B4: Use sqlite_policy memory profile (32MB cache, D-282)
            self._conn = get_sqlite_connection(self.db_path, profile="memory")
            
            # Operational PRAGMA (per A13 — not connection setup)
            self._conn.execute("PRAGMA optimize=0x10002")
        return self._conn

    async def _ensure_initialized(self) -> None:
        """Create recall_turns table and entity_decay_config table if not exist."""
        if self._initialized:
            return

        async with self._lock:
            if self._initialized:
                return

            def _sync_init():
                conn = self._get_conn()
                conn.executescript("""
                    CREATE TABLE IF NOT EXISTS recall_turns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        entity_name TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        turn_index INTEGER NOT NULL,
                        role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        base_quality REAL NOT NULL DEFAULT 0.5,
                        decay_alpha REAL NOT NULL DEFAULT 0.1,
                        metadata_json TEXT NOT NULL DEFAULT '{}',
                        UNIQUE(entity_name, session_id, turn_index, role)
                    );
                    CREATE INDEX IF NOT EXISTS idx_recall_turns_entity_session
                        ON recall_turns(entity_name, session_id);
                    CREATE INDEX IF NOT EXISTS idx_recall_turns_entity
                        ON recall_turns(entity_name);
                    CREATE TABLE IF NOT EXISTS entity_decay_config (
                        entity_name TEXT PRIMARY KEY,
                        decay_alpha REAL NOT NULL DEFAULT 0.1,
                        updated_at TEXT NOT NULL
                    );
                """)

            await anyio.to_thread.run_sync(_sync_init)
            self._initialized = True

    # ── Quality Scoring ─────────────────────────────────────────────

    @staticmethod
    def _score_content_quality(content: str) -> float:
        """Score a single turn's quality (0.0-1.0).

        Uses the same lightweight heuristic as ContextBuilder._score_exchange_quality
        but adapted for single-turn scoring. Zero-cost — no LLM, no network.

        Signals:
        - Message length (substantive exchanges > 0.3)
        - Technical content (code blocks, references > 0.2)
        - Contains question (> 0.2 for user turns)
        - Recency bias (0.15 default)
        """
        if not content or not content.strip():
            return 0.0

        score = 0.0
        word_count = len(content.split())

        # 1. Message length (0.0-0.3)
        if word_count > 50:
            score += 0.3
        elif word_count > 20:
            score += 0.2
        elif word_count > 5:
            score += 0.1

        # 2. Technical content (0.0-0.2)
        has_code = bool(re.search(r'```|`[^`]+`|import |def |class |function ', content))
        has_reference = bool(
            re.search(r'\[\d+\]|\(.*\d{4}\)|http[s]?://|arXiv|doi:', content)
        )
        if has_code:
            score += 0.15
        if has_reference:
            score += 0.05

        # 3. Contains question (0.0-0.2)
        has_question = "?" in content or any(
            kw in content.lower()
            for kw in [
                "what", "how", "why", "when", "where",
                "who", "which", "can you", "could you",
            ]
        )
        if has_question:
            score += 0.2

        # 4. Recency bias (0.15 default)
        score += 0.15

        return min(1.0, score)

    # ── Primary API ─────────────────────────────────────────────────

    async def append(
        self,
        entity_name: str,
        session_id: str,
        turn_index: int,
        role: Literal["user", "assistant"],
        content: str,
        base_quality: Optional[float] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Append a single turn to the recall store.

        Args:
            entity_name: Entity that owns this turn.
            session_id: Session identifier.
            turn_index: Sequential index within session (0-based).
            role: 'user' or 'assistant'.
            content: The turn text content.
            base_quality: Quality score (0.0-1.0). Auto-scored if None.
            timestamp: ISO timestamp. Current time if None.
            metadata: Optional metadata dict (JSON-serializable).

        Returns:
            The row ID of the inserted turn.

        Raises:
            OmegaError: On database constraint violation.
        """
        await self._ensure_initialized()

        if base_quality is None:
            base_quality = self._score_content_quality(content)

        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()

        decay_alpha = self._get_entity_decay_alpha(entity_name)
        metadata_json = json.dumps(metadata or {})

        def _sync_insert():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")
            cursor = conn.execute(
                """INSERT OR REPLACE INTO recall_turns
                (entity_name, session_id, turn_index, role, content, timestamp,
                 base_quality, decay_alpha, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    entity_name, session_id, turn_index, role, content,
                    timestamp, base_quality, decay_alpha, metadata_json,
                ),
            )
            row_id = cursor.lastrowid
            if row_id is None:
                raise OmegaError(
                    message="RecallStore append: failed to get rowid",
                    detail={"entity": entity_name, "session": session_id},
                )
            conn.commit()
            return row_id

        async with self._write_lock:
            return await anyio.to_thread.run_sync(_sync_insert)

    async def append_exchange(
        self,
        entity_name: str,
        session_id: str,
        turn_index: int,
        user_message: str,
        assistant_message: str,
        user_quality: Optional[float] = None,
        assistant_quality: Optional[float] = None,
        timestamp: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Tuple[int, int]:
        """Append a user+assistant exchange pair (two turns) to the recall store.

        This mirrors MemoryStore.add_exchange() for seamless integration.
        User gets turn_index, assistant gets turn_index + 1.

        Args:
            entity_name: Entity that owns this exchange.
            session_id: Session identifier.
            turn_index: Index for the user turn (assistant gets turn_index + 1).
            user_message: User's message content.
            assistant_message: Assistant's response.
            user_quality: Quality for user turn. Auto-scored if None.
            assistant_quality: Quality for assistant turn. Auto-scored if None.
            timestamp: ISO timestamp. Current time if None. Shared for both turns.
            metadata: Optional metadata dict.

        Returns:
            Tuple of (user_row_id, assistant_row_id).
        """
        user_id = await self.append(
            entity_name=entity_name,
            session_id=session_id,
            turn_index=turn_index,
            role="user",
            content=user_message,
            base_quality=user_quality,
            timestamp=timestamp,
            metadata=metadata,
        )
        assistant_id = await self.append(
            entity_name=entity_name,
            session_id=session_id,
            turn_index=turn_index + 1,
            role="assistant",
            content=assistant_message,
            base_quality=assistant_quality,
            timestamp=timestamp,
            metadata=metadata,
        )
        return user_id, assistant_id

    async def window(
        self,
        entity_name: str,
        token_budget: int,
        session_ids: Optional[List[str]] = None,
        max_pairs: int = MAX_WINDOW_PAIRS,
    ) -> List[ExchangePair]:
        """Get a quality-weighted window of exchange pairs within token budget.

        Retrieves turns for the entity, pairs them into user+assistant exchanges,
        scores each by combined decayed quality, sorts by quality descending,
        and returns top exchanges that fit within the token budget.

        This replaces direct MemoryStore.get_history() calls in ContextBuilder.

        Args:
            entity_name: Entity to get window for.
            token_budget: Maximum estimated tokens in the returned window.
            session_ids: Optional filter for specific session IDs only.
            max_pairs: Maximum exchange pairs to consider before filtering.

        Returns:
            List of ExchangePair, ordered by quality descending, filtered
            to fit within token_budget. Empty list if no data.
        """
        await self._ensure_initialized()

        def _sync_window():
            conn = self._get_conn()
            if session_ids:
                placeholders = ",".join("?" for _ in session_ids)
                rows = conn.execute(
                    f"""SELECT * FROM recall_turns
                    WHERE entity_name = ? AND session_id IN ({placeholders})
                    ORDER BY turn_index ASC
                    LIMIT ?""",
                    [entity_name] + session_ids + [max_pairs * 2],
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT id, entity_name, session_id, turn_index, role,
                             content, timestamp, base_quality, decay_alpha,
                             metadata_json
                    FROM recall_turns
                    WHERE entity_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ?""",
                    (entity_name, max_pairs * 2),
                ).fetchall()
            return [dict(r) for r in rows]

        rows = await anyio.to_thread.run_sync(_sync_window)
        if not rows:
            return []

        # Convert dicts to Turn objects
        turns = []
        for r in rows:
            try:
                meta = json.loads(r.get("metadata_json", "{}"))
            except (json.JSONDecodeError, TypeError):
                meta = {}
            turn = Turn(
                id=r["id"],
                entity_name=r["entity_name"],
                session_id=r["session_id"],
                turn_index=r["turn_index"],
                content=r["content"],
                role=r["role"],
                timestamp=r["timestamp"],
                base_quality=r["base_quality"],
                decay_alpha=r["decay_alpha"],
                metadata=meta,
            )
            turns.append(turn)

        # Pair into user+assistant exchanges by session_id + turn_index // 2
        pair_map: Dict[str, ExchangePair] = {}
        for turn in turns:
            pair_key = f"{turn.session_id}:{turn.turn_index // 2}"
            if pair_key not in pair_map:
                pair_map[pair_key] = ExchangePair(
                    turn_index=turn.turn_index // 2,
                    user_content="",
                    assistant_content="",
                    timestamp=turn.timestamp,
                    combined_quality=0.0,
                )

            pair = pair_map[pair_key]
            if turn.role == "user":
                pair.user_content = turn.content
            elif turn.role == "assistant":
                pair.assistant_content = turn.content

            # Use the older timestamp (more conservative estimate)
            if turn.timestamp < pair.timestamp:
                pair.timestamp = turn.timestamp

            # Combined quality accumulates both turns
            pair.combined_quality += turn.decayed_score

        # Average quality across the two turns in each pair
        for pair in pair_map.values():
            pair.combined_quality /= 2.0

        # Filter to complete pairs (both user and assistant present)
        complete_pairs = [
            p for p in pair_map.values()
            if p.user_content and p.assistant_content
        ]

        if not complete_pairs:
            return []

        # Sort by combined quality descending — highest quality first
        complete_pairs.sort(key=lambda p: p.combined_quality, reverse=True)

        # Apply token budget — sliding window of highest quality
        budget_tokens = 0
        result: List[ExchangePair] = []
        for pair in complete_pairs:
            est = pair.estimated_tokens
            if budget_tokens + est > token_budget:
                continue
            result.append(pair)
            budget_tokens += est

        return result

    async def decay_pass(
        self,
        now: Optional[datetime] = None,
    ) -> DecayStats:
        """Apply power-law decay recalibration to all recall turns.

        Power-law: score = base * (1 + age_days)**(-alpha)

        This batch operation syncs the decay_alpha column for all turns
        whose entity has a configured override. The actual decay calculation
        is live (decayed_score property), so this ensures alpha config
        consistency rather than precomputing scores.

        Args:
            now: Current time (defaults to datetime.now(timezone.utc)).
                Used for logging and tracking, not computation (decay is live).

        Returns:
            DecayStats with update counts.
        """
        await self._ensure_initialized()

        _ = now or datetime.now(timezone.utc)
        stats = DecayStats()

        def _sync_decay():
            conn = self._get_conn()
            conn.execute("BEGIN IMMEDIATE")

            # Get all distinct entity names that have configured alphas
            configs = conn.execute(
                "SELECT entity_name, decay_alpha FROM entity_decay_config"
            ).fetchall()

            if not configs:
                return stats

            stats.entities_processed = len(configs)
            total_updated = 0

            for row in configs:
                entity_name = row["entity_name"]
                alpha = row["decay_alpha"]
                try:
                    cursor = conn.execute(
                        """UPDATE recall_turns
                        SET decay_alpha = ?
                        WHERE entity_name = ? AND decay_alpha != ?""",
                        (alpha, entity_name, alpha),
                    )
                    total_updated += cursor.rowcount
                except Exception as e:
                    logger.error(
                        "decay_pass failed for entity %s: %s", entity_name, e
                    )
                    stats.errors.append(f"{entity_name}: {e}")

            stats.turns_updated = total_updated
            conn.commit()
            return stats

        return await anyio.to_thread.run_sync(_sync_decay)

    async def promote_to_core(
        self,
        turn_ids: List[int],
        block_label: str,
        requester_entity: str,
    ) -> Dict[str, Any]:
        """Promote specific recall turns to core memory blocks.

        Reads turns from recall store, composes them into a summary text,
        and appends to the specified core block via BlockTools.

        This is the ONLY way to move data from Recall (WARM) to Core (HOT).
        Direct block writes are forbidden — must go through BlockTools.

        Args:
            turn_ids: List of turn row IDs to promote.
            block_label: Target core block label (e.g., 'decisions', 'insights').
            requester_entity: Entity requesting promotion (for audit trail).

        Returns:
            Dict with status, turns_promoted count, and block_operation result.
        """
        await self._ensure_initialized()

        # 1. Read the turns
        def _sync_read():
            conn = self._get_conn()
            placeholders = ",".join("?" for _ in turn_ids)
            rows = conn.execute(
                f"""SELECT id, entity_name, session_id, turn_index, role,
                    content, timestamp, base_quality
                FROM recall_turns
                WHERE id IN ({placeholders})
                ORDER BY entity_name, session_id, turn_index ASC""",
                turn_ids,
            ).fetchall()
            return [dict(r) for r in rows]

        rows = await anyio.to_thread.run_sync(_sync_read)
        if not rows:
            return {"status": "error", "error": "No turns found for given IDs"}

        # Close any implicit read transaction before write (avoids BEGIN IMMEDIATE conflict)
        def _sync_rollback():
            self._get_conn().rollback()
        await anyio.to_thread.run_sync(_sync_rollback)

        # 2. Compose into structured block text
        lines = []
        for r in rows:
            marker = "[USER]" if r["role"] == "user" else "[ASSISTANT]"
            content = r["content"][:500]  # Truncate for block limit
            lines.append(f"{marker} [{r['session_id']}:{r['turn_index']}] {content}")

        block_text = "\n".join(lines)

        # 3. Append to core block via BlockTools (the ONLY allowed path)
        from omega.memory.block_tools import BlockTools, get_block_store

        store = self._block_store or get_block_store()
        bt = BlockTools(store)
        result = await bt.block_append(
            label=block_label,
            text=block_text,
            requester_entity=requester_entity,
        )

        return {
            "status": "ok" if result.success else "error",
            "turns_promoted": len(rows),
            "block_label": block_label,
            "block_operation": {
                "success": result.success,
                "error": result.error,
            },
        }

    # ── Entity Decay Config ─────────────────────────────────────────

    def _get_entity_decay_alpha(self, entity_name: str) -> float:
        """Get the decay alpha for an entity from cache or DB.

        Lookup order:
        1. In-memory cache (fast path)
        2. entity_decay_config table (DB override)
        3. Block metadata via block_store (future)
        4. DEFAULT_DECAY_ALPHA fallback
        """
        if entity_name in self._entity_decay_cache:
            return self._entity_decay_cache[entity_name]

        try:
            conn = self._get_conn()
            row = conn.execute(
                "SELECT decay_alpha FROM entity_decay_config WHERE entity_name = ?",
                (entity_name,),
            ).fetchone()
            if row is not None:
                alpha = float(row["decay_alpha"])
                self._entity_decay_cache[entity_name] = alpha
                return alpha
        except Exception:
            pass

        self._entity_decay_cache[entity_name] = DEFAULT_DECAY_ALPHA
        return DEFAULT_DECAY_ALPHA

    async def set_entity_decay_alpha(
        self,
        entity_name: str,
        alpha: float,
    ) -> None:
        """Set the power-law decay alpha for an entity.

        Alpha controls how fast this entity's memory decays:
        - 0.01: Near-permanent (identity, core knowledge)
        - 0.10: Standard decay (default, general conversation)
        - 0.25: Medium decay (goals, preferences)
        - 0.60: Fast decay (scratchpad, ephemeral context)

        Raises:
            ValueError: If alpha is not in [0.0, 1.0].
        """
        if not 0.0 <= alpha <= 1.0:
            raise ValueError(
                f"Alpha must be between 0.0 and 1.0, got {alpha}"
            )

        await self._ensure_initialized()

        def _sync_set():
            conn = self._get_conn()
            conn.execute(
                """INSERT OR REPLACE INTO entity_decay_config
                (entity_name, decay_alpha, updated_at)
                VALUES (?, ?, ?)""",
                (entity_name, alpha, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

        await anyio.to_thread.run_sync(_sync_set)
        self._entity_decay_cache[entity_name] = alpha

    # ─── Stats / Maintenance ────────────────────────────────────────

    async def get_stats(self) -> Dict[str, Any]:
        """Get recall store statistics."""
        await self._ensure_initialized()

        def _sync_stats():
            conn = self._get_conn()
            total = conn.execute(
                "SELECT COUNT(*) as c FROM recall_turns"
            ).fetchone()["c"]
            entities = conn.execute(
                "SELECT COUNT(DISTINCT entity_name) as c FROM recall_turns"
            ).fetchone()["c"]
            sessions = conn.execute(
                "SELECT COUNT(DISTINCT entity_name || ':' || session_id) as c "
                "FROM recall_turns"
            ).fetchone()["c"]
            avg_quality = conn.execute(
                "SELECT AVG(base_quality) as a FROM recall_turns"
            ).fetchone()["a"]
            return {
                "total_turns": total,
                "distinct_entities": entities,
                "distinct_sessions": sessions,
                "avg_base_quality": round(avg_quality, 3) if avg_quality else 0.0,
            }

        return await anyio.to_thread.run_sync(_sync_stats)

    async def clear_entity(self, entity_name: str) -> int:
        """Clear all recall turns for an entity (testing/cleanup)."""
        await self._ensure_initialized()

        def _sync_clear():
            conn = self._get_conn()
            cursor = conn.execute(
                "DELETE FROM recall_turns WHERE entity_name = ?",
                (entity_name,),
            )
            return cursor.rowcount

        return await anyio.to_thread.run_sync(_sync_clear)

    async def close(self) -> None:
        """Close the SQLite connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        self._initialized = False


# ── Singleton Factory ──────────────────────────────────────────────

_recall_store_instance: Optional[RecallStore] = None


async def get_recall_store(db_path: Optional[Path] = None) -> RecallStore:
    """Get or create the singleton RecallStore instance."""
    global _recall_store_instance
    if _recall_store_instance is None:
        store = RecallStore(db_path=db_path)
        await store._ensure_initialized()
        _recall_store_instance = store
    return _recall_store_instance
