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

    # 1. Define Core Slots (The Holographic Grid)
    PILLAR_SLOTS = {
        "p1": {"domain": "Flesh", "element": "Earth", "chakra": "Root"},
        "p2": {"domain": "Dream", "element": "Water", "chakra": "Sacral"},
        "p3": {"domain": "Will", "element": "Fire", "chakra": "Solar Plexus"},
        "p4": {"domain": "Heart", "element": "Air", "chakra": "Heart"},
        "p5": {"domain": "Voice", "element": "Aether", "chakra": "Throat"},
        "p6": {"domain": "Mind", "element": "Aether", "chakra": "Third Eye"},
        "p7": {"domain": "Gnosis", "element": "Air", "chakra": "Crown"},
        "p8": {"domain": "Shadow", "element": "Fire", "chakra": "Beyond Crown"},
        "p9": {"domain": "Spirit", "element": "Water", "chakra": "Cosmic Heart"},
        "p10": {"domain": "Chaos", "element": "Earth", "chakra": "Celestial Breath"},
    }

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            # Resolve active IWAD from config/omega.yaml to enforce Engine-Stack Firewall
            try:
                omega_config_path = Path(__file__).resolve().parent.parent.parent.parent / "config" / "omega.yaml"
                with open(omega_config_path, "r") as f:
                    omega_cfg = yaml.safe_load(f)
                active_iwad = omega_cfg.get("omega", {}).get("entity", {}).get("active_iwad", "_omega_default")
                config_path = str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads" / active_iwad / "entities.yaml")
            except Exception as e:
                logger.error(f"Failed to resolve active IWAD from omega.yaml: {e}. Falling back to default.")
                config_path = str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads" / "_omega_default" / "entities.yaml")
        
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
                wad_source=raw.get("wad_source"),
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
        """Get entity by name, role, or Pillar Slot (3-Tier Resolution)."""
        if not name:
            return None
            
        name_lower = name.lower().strip()
        
        # Tier 1: Direct Entity Match (e.g., "sekhmet")
        entity = self._entities.get(name_lower)
        if entity:
            return entity
            
        # Tier 2: Slot Match (e.g., "p1" or "pillar 1")
        # Normalize "pillar 1" -> "p1"
        slot_key = name_lower.replace("pillar ", "p").replace("pillar", "p")
        if slot_key in self.PILLAR_SLOTS:
            # Resolve the slot to its active role in the default/active IWAD
            # We look for an entity that has this slot in its .pillars list
            for ent in self._entities.values():
                # Check if slot_key (e.g. "p1") matches any of the entity's pillars (case-insensitive)
                if any(p.lower() == slot_key for p in ent.pillars):
                    return ent

        # Tier 3: Role Match (e.g., "sysadmin")
        for ent in self._entities.values():
            if ent.role and ent.role.lower() == name_lower:
                return ent
                
        return None

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
        
        Uses Sovereign Atomic Write (Flush -> Sync -> Commit -> Anchor) to prevent data loss on crash.
        """
        def _sync_save():
            data = {"entities": {}}
            for key, entity in self._entities.items():
                data["entities"][key] = entity.to_dict()
            
            temp_dir = self.config_path.parent
            fd, temp_path = tempfile.mkstemp(dir=str(temp_dir), suffix=".tmp")
            try:
                # 1. Write and Sync File
                with os.fdopen(fd, "w") as tf:
                    yaml.dump(data, tf, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    tf.flush()
                    os.fsync(tf.fileno())
                
                # 2. Atomic Replace
                os.replace(temp_path, self.config_path)
                
                # 3. Anchor: Sync Parent Directory
                dir_fd = os.open(str(temp_dir), os.O_RDONLY)
                try:
                    os.fsync(dir_fd)
                finally:
                    os.close(dir_fd)
                
                logger.info(f"Saved {len(self._entities)} entities to {self.config_path}")
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e

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
