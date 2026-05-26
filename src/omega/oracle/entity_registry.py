# 🔱 Entity Registry — YAML-backed Entity CRUD
# AP: AP-ENTITY-REGISTRY-v1.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | CONTEXT: ENTITY-MANAGEMENT]
#
# Replaces:
#   - omega-stack enhanced_handler.py hardcoded ENTITY_ALIASES/ENTITY_DOMAINS dicts
#   - xna-omega entity_service.py (818 lines, PostgreSQL-dependent)
#
# Design: Pure YAML + dataclass. No database dependency. User-editable.

import logging
import os
import tempfile
import functools
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
import anyio

from omega.oracle.entity_workspace import EntityWorkspaceManager

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """A user-definable entity — a Pillar Keeper or custom persona."""

    name: str
    domains: List[str]
    model: str
    personality: str
    temperature: Optional[float] = None
    context_window: Optional[int] = None
    pillars: List[str] = field(default_factory=list)
    secondary_keeper: Optional[str] = None
    pantheon: Optional[str] = None
    element: Optional[str] = None
    chakra: Optional[str] = None
    planet: Optional[str] = None
    sigil: Optional[str] = None
    glyph: Optional[str] = None
    invocation: Optional[str] = None
    role: Optional[str] = None
    container: bool = False
    port: Optional[int] = None
    wad_source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entity fields to dict, excluding None and empty collections."""
        result = {}
        for k, v in asdict(self).items():
            if v is None:
                continue
            if isinstance(v, (list, dict)) and not v:
                continue
            result[k] = v
        return result


class EntityRegistry:
    """Loads, saves, and manages entities from YAML config."""

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = os.environ.get(
                "OMEGA_ENTITIES_CONFIG",
                str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "entities.yaml"),
            )
        self.config_path = Path(config_path)
        self._entities: Dict[str, Entity] = {}
        self._wad_sources: Dict[str, List[str]] = {}  # lowercase entity name -> list of WAD source names
        self._lock = None  # Created lazily in async context (C-ARCH-004 pattern)
        self._load()

    def _load(self) -> None:
        """Load entities from YAML file."""
        if not self.config_path.exists():
            logger.warning(f"Entity config not found at {self.config_path}")
            self._entities = {}
            return

        try:
            with open(self.config_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"entities.yaml is empty or malformed: {e}")
        
        if data is None:
            raise ValueError("entities.yaml is empty or malformed")

        raw_entities = data.get("entities", {}) if data else {}
        for key, raw in raw_entities.items():
            if raw is None or not isinstance(raw, dict):
                logger.warning(f"Entity '{key}' has empty or malformed definition, skipping")
                continue
            entity = Entity(
                name=raw.get("name", key),
                domains=raw.get("domains", []),
                model=raw.get("model", "qwen3-1.7b-q6_k"),
                personality=raw.get("personality", ""),
                temperature=raw.get("temperature"),
                context_window=raw.get("context_window"),
                pillars=raw.get("pillars", []),
                secondary_keeper=raw.get("secondary_keeper"),
                pantheon=raw.get("pantheon"),
                element=raw.get("element"),
                chakra=raw.get("chakra"),
                planet=raw.get("planet"),
                sigil=raw.get("sigil"),
                glyph=raw.get("glyph"),
                invocation=raw.get("invocation"),
                role=raw.get("role"),
                container=raw.get("container", False),
                port=raw.get("port"),
            )
            key = entity.name.lower()
            self._entities[key] = entity
            
            # Track wad_source for entities that have it
            if entity.wad_source:
                if key not in self._wad_sources:
                    self._wad_sources[key] = []
                if entity.wad_source not in self._wad_sources[key]:
                    self._wad_sources[key].append(entity.wad_source)

        logger.info(f"Loaded {len(self._entities)} entities from config")

    def get(self, name: str) -> Optional[Entity]:
        """Get entity by name (case-insensitive)."""
        return self._entities.get(name.lower())

    def list(self) -> List[Entity]:
        """List all entities."""
        return list(self._entities.values())

    def list_pillar_keepers(self) -> List[Entity]:
        """List only the 10 Pillar Keepers (entities with non-empty pillars)."""
        return [e for e in self._entities.values() if e.pillars]

    def names(self) -> List[str]:
        """Return list of entity names."""
        return [e.name for e in self.list()]

    def get_all(self) -> Dict[str, Entity]:
        """Return all entities as a dict keyed by lowercase name."""
        return dict(self._entities)

    def get_by_wad(self, wad_name: str) -> List[Entity]:
        """Return all entities that originated from a specific WAD."""
        return [e for e in self._entities.values() if e.wad_source == wad_name]

    def get_wad_sources(self, name: str) -> List[str]:
        """Return list of WAD sources for a given entity name (lowercase lookup)."""
        return self._wad_sources.get(name.lower(), [])

    async def add(self, entity: Entity) -> None:
        """Add a new entity. Overwrites if name exists."""
        if self._lock is None:
            self._lock = anyio.Lock()
        async with self._lock:
            key = entity.name.lower()
            
            # Track WAD source if present
            if entity.wad_source:
                if key not in self._wad_sources:
                    self._wad_sources[key] = []
                if entity.wad_source not in self._wad_sources[key]:
                    self._wad_sources[key].append(entity.wad_source)
            
            self._entities[key] = entity
            await self._save()
            
            # Automatically scaffold persistent workspace for the awakened entity
            scaffold_fn = functools.partial(
                EntityWorkspaceManager.scaffold_workspace,
                entity.name, entity.role, entity.pillars
            )
            await anyio.to_thread.run_sync(scaffold_fn)

    async def remove(self, name: str) -> bool:
        """Remove an entity by name. Returns True if removed."""
        key = name.lower()
        if self._lock is None:
            self._lock = anyio.Lock()
        async with self._lock:
            if key in self._entities:
                del self._entities[key]
                self._wad_sources.pop(key, None)
                await self._save()
                return True
            return False

    def find_by_domain(self, text: str) -> Optional[Entity]:
        """Find the best entity match for a query text based on domain keywords.

        Matches Pillar Keepers only (Nova handles routing separately).
        Scores each entity by how many domain keywords appear in the text.
        Returns the highest-scoring entity, or None if no match.
        """
        text_lower = text.lower()
        best_score = 0
        best_entity: Optional[Entity] = None

        for entity in self.list_pillar_keepers():
            score = 0
            for keyword in entity.domains:
                if keyword in text_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_entity = entity

        return best_entity if best_score > 0 else None

    def find_by_name_fragment(self, fragment: str) -> Optional[Entity]:
        """Find entity by partial name match (for 'summon' detection)."""
        frag = fragment.lower()
        for key, entity in self._entities.items():
            if frag in key or frag in entity.name.lower():
                return entity
        return None

    async def _save(self) -> None:
        """Save current entities back to YAML file.
        
        Uses atomic write (tempfile + os.replace) to prevent data loss on crash.
        """
        def _sync_save():
            data = {"entities": {}}
            for key, entity in self._entities.items():
                data["entities"][key] = entity.to_dict()
            
            # Atomic write: write to temp, then os.replace
            import tempfile
            temp_dir = self.config_path.parent
            with tempfile.NamedTemporaryFile(
                "w", dir=str(temp_dir), delete=False, suffix=".tmp"
            ) as tf:
                yaml.dump(data, tf, default_flow_style=False, sort_keys=False, allow_unicode=True)
                tmp_name = tf.name
            
            os.replace(tmp_name, self.config_path)
            logger.info(f"Saved {len(self._entities)} entities to {self.config_path}")

        await anyio.to_thread.run_sync(_sync_save)

    def get_tools_for_entity(self, entity_name: str) -> List[Dict[str, Any]]:
        """Return tool descriptors derived from entity domains and personality.

        Each tool maps to a domain keyword the entity can handle,
        enabling the GnosisProxy to perform RAG-based tool discovery.
        """
        entity = self.get(entity_name)
        if not entity:
            return []

        tools = []
        for domain in entity.domains:
            tools.append({
                "name": f"domain_{domain.replace(' ', '_')}",
                "description": f"Handle queries related to {domain} — {entity.name}'s domain of expertise",
                "entity": entity.name,
                "domains": [domain],
            })

        # Add a general-purpose tool for the entity's core personality
        tools.append({
            "name": f"summon_{entity.name.lower()}",
            "description": f"Summon {entity.name} for general guidance: {entity.personality[:120]}",
            "entity": entity.name,
            "domains": entity.domains,
        })

        return tools

    def count(self) -> int:
        return len(self._entities)
