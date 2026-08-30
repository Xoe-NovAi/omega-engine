# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-SECURITY-TAINT-v1.0.0
# 🔱 Tainted Data Protocol — Transitive Propagation
# ⬡ OMEGA ⬡ SECURITY ⬡ taint.py
#
# Implements transitive taint propagation rules for the Sovereign Engine.
# Extends the existing TDP (Tainted Data Protocol) in omega.oracle.security
# with full lifecycle tracking:
#
#   read → session → writes → retrieval
#
# Taint levels follow a "contamination" model: once data is tainted,
# any data derived from it inherits the taint level (or higher).
#
# [M7 Local-First] All taint computation is local — no cloud API calls.
# [M1 AnyIO] All async I/O wrapped in anyio.to_thread.run_sync.
#
# DocRef: docs/architecture/TAINTED_DATA_PROTOCOL.md

import logging
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import anyio


logger = logging.getLogger(__name__)


# ── Taint Levels ────────────────────────────────────────────────────────


class TaintLevel(Enum):
    """Taint levels for data provenance tracking.

    Contamination model: CLEAN < LOW < MEDIUM < HIGH < CONTAMINATED
    Once data is tainted, derived data inherits the higher level.
    """

    CLEAN = 0  # Internal, trusted data (system prompts, code)
    LOW = 1  # External but verified (e.g., GitHub Xoe-NovAi)
    MEDIUM = 2  # External unverified (e.g., web search results)
    HIGH = 3  # External untrusted (e.g., arbitrary URLs)
    CONTAMINATED = 4  # Mixed with HIGH/CONTAMINATED sources

    def __lt__(self, other: "TaintLevel") -> bool:
        return self.value < other.value

    def __le__(self, other: "TaintLevel") -> bool:
        return self.value <= other.value

    def __gt__(self, other: "TaintLevel") -> bool:
        return self.value > other.value

    def __ge__(self, other: "TaintLevel") -> bool:
        return self.value >= other.value

    @classmethod
    def max(cls, *levels: "TaintLevel") -> "TaintLevel":
        """Return the highest (most tainted) level from the given levels."""
        if not levels:
            return cls.CLEAN
        return max(levels, key=lambda l: l.value)


@dataclass
class TaintSource:
    """Source of tainted data.

    Tracks where tainted data originated for audit and traceability.
    """

    name: str  # e.g., "web_search", "firecrawl", "user_upload"
    url: Optional[str] = None  # Source URL if applicable
    provider: Optional[str] = None  # Provider name (e.g., "searxng", "firecrawl")
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class TaintRecord:
    """A single taint tracking record.

    Links a data identifier to its taint level and source.
    """

    data_id: str  # Hash or UUID of the data
    taint_level: TaintLevel
    source: TaintSource
    derived_from: List[str] = field(default_factory=list)  # Parent data_ids
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data_id": self.data_id,
            "taint_level": self.taint_level.name,
            "source": {
                "name": self.source.name,
                "url": self.source.url,
                "provider": self.source.provider,
                "timestamp": self.source.timestamp,
            },
            "derived_from": self.derived_from,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaintRecord":
        src = data.get("source", {})
        return cls(
            data_id=data["data_id"],
            taint_level=TaintLevel[data["taint_level"]],
            source=TaintSource(
                name=src.get("name", "unknown"),
                url=src.get("url"),
                provider=src.get("provider"),
                timestamp=src.get("timestamp", datetime.now(timezone.utc).isoformat()),
            ),
            derived_from=data.get("derived_from", []),
            metadata=data.get("metadata", {}),
            timestamp=data.get("timestamp", datetime.now(timezone.utc).isoformat()),
        )


# ── Taint Propagation Engine ────────────────────────────────────────────


class TaintPropagation:
    """Transitive taint propagation engine.

    Tracks taint levels across the data lifecycle:
    1. READ: External data is tagged with initial taint level
    2. SESSION: Taint propagates to session state (conversations, context)
    3. WRITES: Tainted data written to memory blocks carries taint forward
    4. RETRIEVAL: Taint-aware retrieval filters or flags results

    Contamination rule: When data is derived from multiple sources,
    the resulting taint level is the MAX of all parent taint levels.

    Storage: In-memory dict (can be extended to SQLite for persistence).

    Usage:
        tp = TaintPropagation()

        # Tag external data on read
        data_id = tp.tag_data(
            content="some external text",
            source=TaintSource(name="web_search", url="https://example.com"),
            taint_level=TaintLevel.MEDIUM,
        )

        # Check taint level
        level = tp.get_taint_level(data_id)  # TaintLevel.MEDIUM

        # Derive new data (inherits max taint)
        derived_id = tp.derive_data(
            content="processed version",
            parent_ids=[data_id],
        )
        level = tp.get_taint_level(derived_id)  # TaintLevel.MEDIUM (inherited)

        # Taint-aware retrieval
        clean_only = tp.filter_by_taint(records, max_level=TaintLevel.LOW)
    """

    def __init__(self, storage_path: Optional[str] = None):
        self._records: Dict[str, TaintRecord] = {}
        self._storage_path = storage_path
        self._lock = anyio.Lock()

    @staticmethod
    def _hash_content(content: str) -> str:
        """Generate a stable hash for content (used as data_id)."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:32]

    def tag_data(
        self,
        content: str,
        source: TaintSource,
        taint_level: TaintLevel,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Tag data with an initial taint level.

        Called when external data is first read into the system.

        Args:
            content: The data content to tag.
            source: Where the data came from.
            taint_level: Initial taint level.
            metadata: Optional metadata (provider, timestamp, etc.)

        Returns:
            data_id: The hash identifier for this data.
        """
        data_id = self._hash_content(content)

        record = TaintRecord(
            data_id=data_id,
            taint_level=taint_level,
            source=source,
            metadata=metadata or {},
        )

        self._records[data_id] = record
        logger.debug(
            "Tagged data %s with taint level %s from source %s",
            data_id,
            taint_level.name,
            source.name,
        )

        return data_id

    def derive_data(
        self,
        content: str,
        parent_ids: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a derived data record, inheriting max taint from parents.

        Called when data is transformed (e.g., summarized, processed).
        The derived data inherits the highest taint level of all parents.

        Args:
            content: The derived content.
            parent_ids: List of parent data_ids.
            metadata: Optional metadata.

        Returns:
            data_id: The hash identifier for this derived data.
        """
        data_id = self._hash_content(content)

        # Compute max taint level from parents
        parent_levels: List[TaintLevel] = []
        for pid in parent_ids:
            if pid in self._records:
                parent_levels.append(self._records[pid].taint_level)
            else:
                logger.warning("Parent data_id %s not found in taint records — assuming CLEAN", pid)

        max_level = TaintLevel.max(*parent_levels) if parent_levels else TaintLevel.CLEAN

        # Determine source from parents (use the most tainted parent's source)
        if parent_ids:
            # Find the parent with the highest taint level
            most_tainted_parent = None
            most_tainted_level = TaintLevel.CLEAN
            for pid in parent_ids:
                if pid in self._records:
                    rec = self._records[pid]
                    if rec.taint_level > most_tainted_level:
                        most_tainted_level = rec.taint_level
                        most_tainted_parent = rec

            source = (
                most_tainted_parent.source
                if most_tainted_parent
                else TaintSource(name="derived", timestamp=datetime.now(timezone.utc).isoformat())
            )
        else:
            source = TaintSource(name="derived", timestamp=datetime.now(timezone.utc).isoformat())

        record = TaintRecord(
            data_id=data_id,
            taint_level=max_level,
            source=source,
            derived_from=parent_ids,
            metadata=metadata or {},
        )

        self._records[data_id] = record
        logger.debug(
            "Derived data %s with taint level %s (from %d parents)",
            data_id,
            max_level.name,
            len(parent_ids),
        )

        return data_id

    def get_taint_level(self, data_id: str) -> TaintLevel:
        """Get the taint level for a data_id.

        Returns CLEAN if the data_id is not tracked (no record = trusted internal).
        """
        record = self._records.get(data_id)
        if record is None:
            return TaintLevel.CLEAN
        return record.taint_level

    def get_record(self, data_id: str) -> Optional[TaintRecord]:
        """Get the full taint record for a data_id."""
        return self._records.get(data_id)

    def elevate_taint(
        self,
        data_id: str,
        new_level: TaintLevel,
        reason: str = "",
    ) -> bool:
        """Elevate the taint level of existing data.

        Used when data is found to be more tainted than initially assessed
        (e.g., a trusted URL returns untrusted content).

        Args:
            data_id: The data_id to elevate.
            new_level: The new (higher) taint level.
            reason: Why the elevation occurred.

        Returns:
            True if elevation was applied, False if data_id not found
            or new_level is not higher.
        """
        record = self._records.get(data_id)
        if record is None:
            return False

        if new_level <= record.taint_level:
            return False

        old_level = record.taint_level
        record.taint_level = new_level
        record.metadata["taint_elevated"] = True
        record.metadata["taint_elevation_reason"] = reason
        record.metadata["taint_elevated_at"] = datetime.now(timezone.utc).isoformat()

        logger.warning(
            "Taint elevated for data %s: %s → %s (%s)",
            data_id,
            old_level.name,
            new_level.name,
            reason,
        )

        # Propagate elevation to derived data
        self._propagate_elevation(data_id, new_level)

        return True

    def _propagate_elevation(self, parent_id: str, new_level: TaintLevel) -> None:
        """Recursively elevate taint for all data derived from parent_id."""
        for record in self._records.values():
            if parent_id in record.derived_from:
                if new_level > record.taint_level:
                    record.taint_level = new_level
                    record.metadata["taint_elevated"] = True
                    record.metadata["taint_elevation_reason"] = (
                        f"Inherited from elevated parent {parent_id}"
                    )
                    self._propagate_elevation(record.data_id, new_level)

    def filter_by_taint(
        self,
        data_ids: List[str],
        max_level: TaintLevel = TaintLevel.MEDIUM,
    ) -> List[str]:
        """Filter data_ids by maximum allowed taint level.

        Args:
            data_ids: List of data_ids to filter.
            max_level: Maximum allowed taint level (inclusive).

        Returns:
            List of data_ids that meet the taint threshold.
        """
        return [did for did in data_ids if self.get_taint_level(did) <= max_level]

    def get_contaminated_sources(self) -> List[TaintRecord]:
        """Get all records with HIGH or CONTAMINATED taint level."""
        return [r for r in self._records.values() if r.taint_level >= TaintLevel.HIGH]

    def get_stats(self) -> Dict[str, Any]:
        """Get taint tracking statistics."""
        level_counts: Dict[str, int] = {}
        for record in self._records.values():
            level = record.taint_level.name
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "total_records": len(self._records),
            "by_level": level_counts,
            "contaminated_sources": len(self.get_contaminated_sources()),
        }

    def clear(self) -> None:
        """Clear all taint records (for testing)."""
        self._records.clear()


# ── Taint-Aware Ingestion Integration ───────────────────────────────────


class TaintAwareIngestion:
    """Integrates taint tracking with the SovereignIngestionPipeline.

    Wraps the existing ingestion pipeline to automatically tag
    ingested documents with appropriate taint levels based on
    the provider/source.

    Taint level assignment rules:
    - LOCAL (localhost, 127.0.0.1, file://): CLEAN
    - TRUSTED (github.com/Xoe-NovAi, omega_library): LOW
    - SEARCH (searxng, websearch results): MEDIUM
    - EXTERNAL (arbitrary URLs): HIGH
    - MIXED (content from multiple sources): CONTAMINATED

    Usage:
        taint_engine = TaintAwareIngestion()
        doc = await taint_engine.ingest_with_taint(
            raw_content="...",
            metadata={"source": "https://example.com"},
            provider_name="firecrawl",
            target_entity="lilith",
        )
    """

    # Taint level mapping by provider/source pattern
    TAINT_MAP: Dict[str, TaintLevel] = {
        "local": TaintLevel.CLEAN,
        "localhost": TaintLevel.CLEAN,
        "127.0.0.1": TaintLevel.CLEAN,
        "file": TaintLevel.CLEAN,
        "github.com/Xoe-NovAi": TaintLevel.LOW,
        "omega_library": TaintLevel.LOW,
        "searxng": TaintLevel.MEDIUM,
        "websearch": TaintLevel.MEDIUM,
        "firecrawl": TaintLevel.MEDIUM,
        "exa": TaintLevel.MEDIUM,
        "google": TaintLevel.HIGH,
        "openrouter": TaintLevel.HIGH,
        "opencode-zen": TaintLevel.HIGH,
    }

    def __init__(self, taint_propagation: Optional[TaintPropagation] = None):
        self._tp = taint_propagation or create_taint_propagation()

    @classmethod
    def determine_taint_level(
        cls,
        provider_name: str,
        source_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TaintLevel:
        """Determine the appropriate taint level for ingested data.

        Args:
            provider_name: Name of the data provider.
            source_url: Optional source URL.
            metadata: Optional metadata dict.

        Returns:
            TaintLevel for this data.
        """
        # Check source URL first (more specific)
        if source_url:
            url_lower = source_url.lower()
            import re

            for pattern, level in cls.TAINT_MAP.items():
                pat_lower = pattern.lower()
                # Use regex word-boundary matching to avoid false positives
                # (e.g., "exa" matching "example.com")
                # Match if pattern appears as a domain/path component
                if re.search(
                    r"(?<![a-zA-Z0-9])" + re.escape(pat_lower) + r"(?![a-zA-Z0-9])", url_lower
                ):
                    return level
                # Also check if any URL domain component is a substring of the pattern
                # (e.g., "searx" in URL matching "searxng" pattern)
                if any(
                    pat_lower.startswith(comp) or pat_lower.endswith(comp)
                    for comp in re.split(r"[^a-zA-Z0-9]+", url_lower)
                    if comp
                ):
                    return level
            # URL provided but no trusted pattern matched → external untrusted
            return TaintLevel.HIGH

        # No URL → fall back to provider name
        provider_lower = provider_name.lower()
        for pattern, level in cls.TAINT_MAP.items():
            if pattern.lower() in provider_lower:
                return level

        # Default: HIGH for unknown external sources
        return TaintLevel.HIGH

    async def ingest_with_taint(
        self,
        raw_content: str,
        metadata: Dict[str, Any],
        provider_name: str = "external",
        target_entity: str = "unknown",
        source_url: Optional[str] = None,
    ) -> Tuple[str, Any]:
        """Ingest data with automatic taint tagging.

        Integrates with the SovereignIngestionPipeline:
        1. Determine taint level from provider/source
        2. Tag the raw content with taint
        3. Run through the existing sieve-and-sign pipeline
        4. Return source_id + ingested document with taint metadata

        Args:
            raw_content: Raw external content.
            metadata: Metadata dict (source, timestamp, etc.).
            provider_name: Provider name for taint determination.
            target_entity: Entity to anchor the data to.
            source_url: Optional source URL.

        Returns:
            Tuple of (source_id, ingested_document_with_taint).
        """
        # 1. Determine taint level
        taint_level = self.determine_taint_level(provider_name, source_url, metadata)

        # 2. Tag the data
        source = TaintSource(
            name=provider_name,
            url=source_url,
            provider=provider_name,
        )

        data_id = self._tp.tag_data(
            content=raw_content,
            source=source,
            taint_level=taint_level,
            metadata={"entity": target_entity, **metadata},
        )

        # 3. Run through existing ingestion pipeline
        from omega.oracle.ingestion import get_ingestion_coordinator

        coordinator = get_ingestion_coordinator()
        source_id, doc = await coordinator.process_and_anchor(
            raw_content=raw_content,
            metadata=metadata,
            target_entity=target_entity,
            provider_name=provider_name,
        )

        # 4. Attach taint metadata to the document
        doc.metadata["taint_level"] = taint_level.name
        doc.metadata["taint_data_id"] = data_id

        logger.info(
            "Ingested data with taint level %s (data_id=%s, source_id=%s)",
            taint_level.name,
            data_id,
            source_id,
        )

        return source_id, doc

    def get_taint_level(self, data_id: str) -> TaintLevel:
        """Get taint level for a data_id."""
        return self._tp.get_taint_level(data_id)


# ── Taint-Aware Memory Integration ──────────────────────────────────────


class TaintAwareMemory:
    """Integrates taint tracking with memory block operations.

    Ensures that when tainted data is written to memory blocks,
    the taint level is recorded and propagated.

    Integration points:
    - block_append: Tags appended content with taint level
    - block_read: Returns taint level with block content
    - block_replace: Inherits max taint from old + new content
    """

    def __init__(self, taint_propagation: Optional[TaintPropagation] = None):
        self._tp = taint_propagation or create_taint_propagation()

    async def tag_block_content(
        self,
        content: str,
        block_label: str,
        entity_name: str,
        taint_level: TaintLevel = TaintLevel.CLEAN,
        source: Optional[TaintSource] = None,
    ) -> str:
        """Tag content being written to a memory block.

        Args:
            content: The content being written.
            block_label: The block label.
            entity_name: The entity owning the block.
            taint_level: Taint level of the content.
            source: Optional source info.

        Returns:
            data_id for the tagged content.
        """
        if source is None:
            source = TaintSource(
                name=f"block:{entity_name}:{block_label}",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        return self._tp.tag_data(
            content=content,
            source=source,
            taint_level=taint_level,
            metadata={
                "entity": entity_name,
                "block_label": block_label,
            },
        )

    def check_block_taint(
        self,
        block_label: str,
        entity_name: str,
    ) -> TaintLevel:
        """Check the taint level of a memory block.

        Looks up the block's content hash in the taint records.
        """
        # This would need the block's content to hash it
        # In practice, the block_store would store the data_id
        # For now, return CLEAN as default
        return TaintLevel.CLEAN

    def should_promote_to_core(
        self,
        data_id: str,
        max_level: TaintLevel = TaintLevel.LOW,
    ) -> bool:
        """Check if data with this taint level can be promoted to core blocks.

        Core blocks (persona, safety) should only contain CLEAN or LOW taint data.
        """
        level = self._tp.get_taint_level(data_id)
        return level <= max_level


# ── Singleton Factory ────────────────────────────────────────────────────

_taint_propagation: Optional[TaintPropagation] = None


def create_taint_propagation() -> TaintPropagation:
    """Create a new TaintPropagation instance."""
    return TaintPropagation()


def get_taint_propagation() -> TaintPropagation:
    """Get or create the singleton TaintPropagation instance."""
    global _taint_propagation
    if _taint_propagation is None:
        _taint_propagation = TaintPropagation()
    return _taint_propagation
