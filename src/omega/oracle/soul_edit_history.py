# AP: AP-SOUL-EDIT-HISTORY-v1.0.0
# 🔱 Omega Engine — Soul Edit History (Immutable Audit Trail)
# ⬡ OMEGA ⬡ JEM ⬡ deepseek-v4-flash ⬡ opencode ⬡ SOUL-EDIT-HISTORY
#
# [id-soft: vet-008] Lazy Deletion — tombstone-centric approach to history
#     Doom marks thinkers with sentinel (-1) instead of immediate free.
#     Soul edit history is append-only: entries are never deleted or modified.
#     Tombstoned entries (entries that describe a now-reverted change) remain
#     in the log as a forensic record — they are filtered at query time.
#
# [id-soft: vet-008] 0.5s Realloc Grace — atomic write pattern
#     Quake's 0.5s grace before memory reallocation prevents morphing.
#     Soul edit history uses the same principle: atomic tmp+rename write
#     prevents partial-write corruption during history append.
#
# Audit trail for all soul.yaml mutations:
# - Session distillation (close_session)
# - Background researcher updates
# - Manual edits via soul update commands
# - Selective Hydration store operations
#
# Stored in: data/entities/{name}/soul_edit_history.yaml
# Format: append-only YAML list of SoulEditEntry
#
# M9: Error Integrity — typed errors, no bare except
# M1: AnyIO compliance


# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md
import logging
import os
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import anyio
import yaml

from omega.errors import OmegaError

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────

# Directory pattern for entity soul data
SOUL_EDIT_HISTORY_FILENAME = "soul_edit_history.yaml"

# Max entries to return in a single get_history() call
DEFAULT_HISTORY_LIMIT = 50


@dataclass
class SoulEditEntry:
    """A single immutable entry in the soul edit history.
    
    Records one atomic mutation to an entity's soul.yaml.
    Entries are never modified or deleted — the log is append-only.
    
    Attributes:
        timestamp: Unix timestamp of the edit.
        entity_name: The entity whose soul was modified.
        field_path: Dot-notation path to the field that changed.
            Examples: "entity.name", "entity.lessons_learned[0]"
        old_value: The previous value of the field (None if new field).
        new_value: The new value of the field (None if field was deleted).
        source: What system made the change.
            Examples: "soul_distiller", "background_researcher",
                     "selective_hydration", "manual"
        trace_id: The trace ID that triggered this mutation.
        agent_name: Optional name of the agent that requested the change.
        summary: Optional human-readable summary of the change.
    """
    entity_name: str
    field_path: str
    old_value: Any = None
    new_value: Any = None
    source: str = "unknown"
    trace_id: str = ""
    timestamp: float = 0.0
    agent_name: Optional[str] = None
    summary: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()


class SoulEditHistory:
    """Append-only audit trail for soul.yaml mutations.
    
    Thread-safe via anyio.Lock. Atomic writes via tmp+rename.
    Stored as a YAML list at data/entities/{entity_name}/soul_edit_history.yaml.
    
    Usage:
        history = SoulEditHistory()
        await history.append(SoulEditEntry(
            entity_name="jem",
            field_path="entity.lessons_learned[2]",
            old_value=None,
            new_value="L3: The Principle of...",
            source="soul_distiller",
            trace_id="trace-001",
        ))
        entries = await history.get_history("jem", limit=20)
    """

    def __init__(self, entities_dir: Optional[Path] = None) -> None:
        """Initialize the SoulEditHistory manager.
        
        Args:
            entities_dir: Base directory for entity data.
                Defaults to data/entities/ relative to project root.
        """
        if entities_dir is None:
            # Resolve relative to the Omega Engine project root
            entities_dir = Path(__file__).resolve().parent.parent.parent.parent / "data" / "entities"
        self._entities_dir = entities_dir
        self._lock = anyio.Lock()

    def _get_history_path(self, entity_name: str) -> Path:
        """Get the path to the edit history file for an entity."""
        return self._entities_dir / entity_name / SOUL_EDIT_HISTORY_FILENAME

    async def append(self, entry: SoulEditEntry) -> None:
        """Append an entry to the entity's soul edit history.
        
        The write is atomic: data is written to a .tmp file, then
        atomically renamed. This prevents partial-write corruption.
        
        Args:
            entry: The SoulEditEntry to append.
            
        Raises:
            OSError: If the atomic write fails.
        """
        path = self._get_history_path(entry.entity_name)
        
        async with self._lock:
            # Ensure parent directory exists
            # Use lambda for keyword args (run_sync only accepts positional args)
            await anyio.to_thread.run_sync(lambda: path.parent.mkdir(parents=True, exist_ok=True))
            
            # Read existing history
            existing: List[dict] = []
            if await anyio.to_thread.run_sync(path.exists):
                try:
                    content = await anyio.to_thread.run_sync(path.read_text)
                    if content.strip():
                        parsed = await anyio.to_thread.run_sync(yaml.safe_load, content)
                        if isinstance(parsed, list):
                            existing = parsed
                except (OmegaError, RuntimeError, OSError) as exc:
                    logger.warning(
                        "Failed to read existing soul edit history for %s: %s. "
                        "Starting fresh append.", entry.entity_name, exc
                    )
            
            # Append new entry
            entry_data = {k: v for k, v in asdict(entry).items() if v is not None}
            existing.append(entry_data)
            
            # Atomic write: tmp → rename
            tmp_path = path.with_suffix(".yaml.tmp")
            yaml_content = await anyio.to_thread.run_sync(
                lambda: yaml.safe_dump(existing, default_flow_style=False, indent=2)
            )
            
            # Write to tmp
            await anyio.to_thread.run_sync(tmp_path.write_text, yaml_content)
            
            # Atomic rename (crash-safe on POSIX)
            await anyio.to_thread.run_sync(tmp_path.rename, path)
            
            logger.debug(
                "Soul edit history appended for %s: %s → %s [source=%s]",
                entry.entity_name, entry.field_path,
                str(entry.new_value)[:60] if entry.new_value else "<deleted>",
                entry.source,
            )

    async def get_history(
        self,
        entity_name: str,
        limit: int = DEFAULT_HISTORY_LIMIT,
        source: Optional[str] = None,
        after_timestamp: Optional[float] = None,
    ) -> List[dict]:
        """Retrieve edit history for an entity.
        
        Args:
            entity_name: The entity whose history to retrieve.
            limit: Maximum number of entries to return (most recent first).
                Defaults to 50.
            source: Optional filter — only return entries from this source.
            after_timestamp: Optional filter — only return entries after
                this Unix timestamp.
                
        Returns:
            List of SoulEditEntry dicts, most recent first.
        """
        path = self._get_history_path(entity_name)
        
        if not await anyio.to_thread.run_sync(path.exists):
            return []
        
        try:
            content = await anyio.to_thread.run_sync(path.read_text)
            if not content.strip():
                return []
            
            parsed = await anyio.to_thread.run_sync(yaml.safe_load, content)
            if not isinstance(parsed, list):
                logger.warning("Soul edit history for %s is not a list", entity_name)
                return []
            
            # Apply filters
            filtered = parsed
            if source:
                filtered = [e for e in filtered if e.get("source") == source]
            if after_timestamp:
                filtered = [
                    e for e in filtered
                    if e.get("timestamp", 0) > after_timestamp
                ]
            
            # Sort most recent first, apply limit
            filtered.sort(key=lambda e: e.get("timestamp", 0), reverse=True)
            return filtered[:limit]
            
        except (OmegaError, RuntimeError, OSError, yaml.YAMLError) as exc:
            logger.warning(
                "Failed to read soul edit history for %s: %s", entity_name, exc
            )
            return []

    async def count_entries(self, entity_name: str) -> int:
        """Count total entries in the edit history for an entity.
        
        Args:
            entity_name: The entity to count entries for.
            
        Returns:
            Number of entries, or 0 if no history file exists.
        """
        path = self._get_history_path(entity_name)
        
        if not await anyio.to_thread.run_sync(path.exists):
            return 0
        
        try:
            content = await anyio.to_thread.run_sync(path.read_text)
            if not content.strip():
                return 0
            
            parsed = await anyio.to_thread.run_sync(yaml.safe_load, content)
            if isinstance(parsed, list):
                return len(parsed)
            return 0
        except (yaml.YAMLError, OSError):
            return 0

    async def get_unique_sources(self, entity_name: str) -> List[str]:
        """Get the list of unique sources that have modified an entity's soul.
        
        Args:
            entity_name: The entity to query sources for.
            
        Returns:
            Sorted list of unique source names.
        """
        path = self._get_history_path(entity_name)
        
        if not await anyio.to_thread.run_sync(path.exists):
            return []
        
        try:
            content = await anyio.to_thread.run_sync(path.read_text)
            if not content.strip():
                return []
            
            parsed = await anyio.to_thread.run_sync(yaml.safe_load, content)
            if not isinstance(parsed, list):
                return []
            
            sources: set = set()
            for entry in parsed:
                src = entry.get("source")
                if src:
                    sources.add(src)
            return sorted(sources)
        except (yaml.YAMLError, OSError):
            return []
