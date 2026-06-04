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
import time
import struct
import tempfile
import functools
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
import anyio

from omega.oracle.entity_workspace import EntityWorkspaceManager
from omega.constants import ZONEID_ENTITY, ZONEID_TOMBSTONE, validate_zoneid
from omega.errors import EntityTombstonedError

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """A user-definable entity — a Pillar Keeper or custom persona.

    [id-soft: doom-1993] ZONEID Pattern — magic constant validated on get()
    to catch stale references and tombstoned entities.
    """

    name: str
    domains: List[str]
    model: str
    personality: str
    capabilities: List[str] = field(default_factory=list)
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
    # [id-soft: doom-1993] ZONEID Pattern — runtime marker, not serialized
    magic: int = field(default=ZONEID_ENTITY, compare=False)
    # [id-soft: doom-1993] High-Bit Trick — flags as bitfield, high bit = system
    # 0x80000000 = system entity, 0x40000000 = WAD-loaded entity
    flags: int = field(default=0, compare=False)
    # [id-soft: quake3-1999] Hard-Boundary — engine zone sentinel
    # __engine_zone__ and __game_zone__ are checked by zone-aware getters.
    __engine_zone__: dict = field(default_factory=dict, repr=False, compare=False)
    __game_zone__: dict = field(default_factory=dict, repr=False, compare=False)

    def __post_init__(self) -> None:
        """Post-init: populate zone sentinels from known fields.

        [id-soft: quake3-1999] Hard-Boundary — automatically partition
        fields into engine zone (read-only) and game zone (writable).
        """
        # Engine zone: structural identity fields (DO NOT MODIFY by game logic)
        self.__engine_zone__ = {
            "magic": self.magic,
            "name": self.name,
            "domains": self.domains,
            "capabilities": self.capabilities,
            "model": self.model,
            "role": self.role,
            "container": self.container,
            "port": self.port,
            "wad_source": self.wad_source,
            "pillars": self.pillars,
            "flags": self.flags,
        }
        # Game zone: personality/behavior fields (freely modifiable)
        self.__game_zone__ = {
            "personality": self.personality,
            "temperature": self.temperature,
            "context_window": self.context_window,
            "secondary_keeper": self.secondary_keeper,
            "pantheon": self.pantheon,
            "element": self.element,
            "chakra": self.chakra,
            "planet": self.planet,
            "sigil": self.sigil,
            "glyph": self.glyph,
            "invocation": self.invocation,
        }

    def is_system(self) -> bool:
        """Check if this is a system-level entity (high-bit flag).

        [id-soft: doom-1993] High-Bit Trick — single bit check
        instead of separate boolean field. 1 AND instruction vs 1 struct field.
        """
        return bool(self.flags & EntityRegistry.FLAG_SYSTEM)

    def mark_system(self) -> None:
        """Mark this entity as system-level (high-bit).

        Once set, this should not be cleared — follows the same
        convention as id Software's NF_SUBSECTOR bit.
        """
        self.flags |= EntityRegistry.FLAG_SYSTEM
        self.__engine_zone__["flags"] = self.flags

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entity fields to dict, excluding None/empty/magic."""
        result = {}
        for k, v in asdict(self).items():
            if v is None:
                continue
            if isinstance(v, (list, dict)) and not v:
                continue
            if k == "magic":
                continue  # Runtime-only; not stored in YAML
            result[k] = v
        return result


class EntityRegistry:
    """Loads, saves, and manages entities from YAML config.

    [id-soft: doom-1993] Lazy Deletion — entities are tombstoned (magic =
    ZONEID_TOMBSTONE) on remove() and reaped after a grace period.
    See P_RemoveThinker in DOOM 1993 p_tick.c:62-103.
    [id-soft: quake-1996] Grace Period — 0.5s delay before actual removal
    ensures in-flight operations complete safely.
    """

    # [id-soft: quake-1996] Grace Period — 0.5s realloc delay
    # Derived from Quake 1996 host_cmd.c's delayed entity removal pattern.
    TOMBSTONE_GRACE_SECONDS = 0.5

    # [id-soft: doom-1993] High-Bit Trick — flag encoding using high bit
    # DOOM's NF_SUBSECTOR (0x8000) repurposed high bit of node child index.
    # Here: high bit (bit 31) = SYSTEM entity. Two types in one integer field.
    FLAG_SYSTEM = 0x80000000  # Bit 31: system-level entity (vs user-created)
    FLAG_WAD = 0x40000000     # Bit 30: loaded from a WAD (vs runtime-created)
    FLAG_ACTIVE = 0x00000000  # Default: active entity (low bits = slot flags)

    # [id-soft: quake3-1999] Hard-Boundary Struct — engine zone vs game zone
    # Q3A separated entityState_t (engine-owned) from entityShared_t (game-owned)
    # with a "DO NOT MODIFY" comment. We use sentinel attributes.
    ENGINE_ZONE_ATTRS = frozenset({
        "magic", "name", "domains", "model", "role",
        "container", "port", "wad_source", "pillars",
    })
    GAME_ZONE_ATTRS = frozenset({
        "personality", "temperature", "context_window",
        "secondary_keeper", "pantheon", "element", "chakra",
        "planet", "sigil", "glyph", "invocation",
    })

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
        # [id-soft: doom-1993] Multi-Index Entity — dual-index lookup
        # maps capability (e.g. "research") -> list of entity keys
        self._capability_index: Dict[str, List[str]] = {}
        self._lock = None  # Created lazily in async context (C-ARCH-004 pattern)
        # [id-soft: doom-1993] Lazy Deletion — tombstoned entity tracking
        self._tombstoned: Dict[str, float] = {}  # key -> time.monotonic() of tombstone
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
                capabilities=raw.get("capabilities", []),
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
            # [id-soft: doom-1993] ZONEID Pattern — set at load, not serialized
            entity.magic = ZONEID_ENTITY
            self._entities[key] = entity
            
            # Track wad_source for entities that have it
            if entity.wad_source:
                if key not in self._wad_sources:
                    self._wad_sources[key] = []
                if entity.wad_source not in self._wad_sources[key]:
                    self._wad_sources[key].append(entity.wad_source)
            
            # [id-soft: doom-1993] Multi-Index Entity — populate capability index
            for cap in entity.domains + entity.capabilities:
                cap_lower = cap.lower()
                if cap_lower not in self._capability_index:
                    self._capability_index[cap_lower] = []
                if key not in self._capability_index[cap_lower]:
                    self._capability_index[cap_lower].append(key)


        logger.info(f"Loaded {len(self._entities)} entities from config")

    def get(self, name: str, raise_on_tombstoned: bool = False) -> Optional[Entity]:
        """Get entity by name, role, or Pillar Slot (3-Tier Resolution).

        [id-soft: doom-1993] ZONEID Pattern — validates magic on matched entities
        [id-soft: doom-1993] Lazy Deletion — tombstoned entities treated as not found

        Args:
            name: Entity name to look up.
            raise_on_tombstoned: If True, raise EntityTombstonedError instead of returning None
                for entities that were removed. Mandate 9 enforcement for callers
                that need to distinguish 'does not exist' from 'was removed'.
        """
        if not name:
            return None
            
        name_lower = name.lower().strip()
        
        # Tier 1: Direct Entity Match (e.g., "sekhmet")
        entity = self._entities.get(name_lower)
        if entity:
            if entity.magic == ZONEID_TOMBSTONE:
                # [id-soft: doom-1993] Lazy Deletion — sentinel marker check
                if raise_on_tombstoned:
                    raise EntityTombstonedError(
                        cache_key=name_lower,
                        message=f"Entity '{name}' was removed (tombstoned) — call active_iter() for current entities",
                    )
                return None
            # [id-soft: doom-1993] ZONEID Pattern — runtime integrity check
            validate_zoneid(entity.magic, ZONEID_ENTITY, f"EntityRegistry.get({name})")
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

    def get_by_capability(self, capability: str) -> List[Entity]:
        """Find all active entities that possess a specific capability.
        
        [id-soft: doom-1993] Multi-Index Entity — O(1) capability lookup
        """
        if not capability:
            return []
        
        cap_lower = capability.lower()
        keys = self._capability_index.get(cap_lower, [])
        
        # Filter out tombstoned entities
        return [self._entities[k] for k in keys if k in self._entities and self._entities[k].magic != ZONEID_TOMBSTONE]

    def list(self) -> List[Entity]:
        """List all non-tombstoned entities.

        [id-soft: doom-1993] Lazy Deletion — tombstoned entities filtered out.
        """
        return self.active_iter()

    def list_pillar_keepers(self) -> List[Entity]:
        """List only the 10 Pillar Keepers (non-tombstoned entities with pillars)."""
        return [e for e in self.active_iter() if e.pillars]

    def names(self) -> List[str]:
        """Return list of non-tombstoned entity names."""
        return [e.name for e in self.list()]

    def get_all(self) -> Dict[str, Entity]:
        """Return all entities as a dict keyed by lowercase name.

        [id-soft: doom-1993] Lazy Deletion — tombstoned entities excluded.
        """
        return {k: v for k, v in self._entities.items() if v.magic != ZONEID_TOMBSTONE}

    def get_by_wad(self, wad_name: str) -> List[Entity]:
        """Return all non-tombstoned entities from a specific WAD."""
        return [e for e in self.active_iter() if e.wad_source == wad_name]

    def get_wad_sources(self, name: str) -> List[str]:
        """Return list of WAD sources for a given entity name (lowercase lookup).

        Still returns sources for tombstoned entities — WAD provenance is
        preserved for debugging even after removal.
        """
        return self._wad_sources.get(name.lower(), [])

    async def add(self, entity: Entity) -> None:
        """Add a new entity. Overwrites if name exists.

        Normalizes names to lowercase for case-insensitive lookup.
        [id-soft: doom-1993] High-Bit Trick — sets WAD flag if wad_source present
        """
        if self._lock is None:
            self._lock = anyio.Lock()
        async with self._lock:
            name_key = self._validate_name(entity.name)
            entity.name = name_key  # Normalize to lowercase
            
            # [id-soft: doom-1993] High-Bit Trick — set FLAG_WAD if WAD-loaded
            if entity.wad_source:
                entity.flags |= EntityRegistry.FLAG_WAD
                entity.__engine_zone__["flags"] = entity.flags
            
            key = name_key
            
            # Track WAD source if present
            if entity.wad_source:
                if key not in self._wad_sources:
                    self._wad_sources[key] = []
                if entity.wad_source not in self._wad_sources[key]:
                    self._wad_sources[key].append(entity.wad_source)
            
            # [id-soft: doom-1993] Multi-Index Entity — populate capability index
            for cap in entity.domains + entity.capabilities:
                cap_lower = cap.lower()
                if cap_lower not in self._capability_index:
                    self._capability_index[cap_lower] = []
                if key not in self._capability_index[cap_lower]:
                    self._capability_index[cap_lower].append(key)
            
            # [id-soft: doom-1993] ZONEID Pattern — set runtime marker
            entity.magic = ZONEID_ENTITY
            self._entities[key] = entity
            await self._save()
            
            # Automatically scaffold persistent workspace for the awakened entity
            scaffold_fn = functools.partial(
                EntityWorkspaceManager.scaffold_workspace,
                entity.name, entity.role, entity.pillars
            )
            await anyio.to_thread.run_sync(scaffold_fn)

    async def remove(self, name: str) -> bool:
        """Remove an entity by name. Returns True if removed.

        [id-soft: doom-1993] Lazy Deletion — marks with ZONEID_TOMBSTONE
        instead of immediate deletion. Actual cleanup happens in
        _reap_tombstoned() on the next _save() after the grace period.
        [id-soft: quake-1996] Grace Period — 0.5s delay for safety.
        """
        key = name.lower()
        if self._lock is None:
            self._lock = anyio.Lock()
        async with self._lock:
            if key in self._entities:
                entity = self._entities[key]
                # [id-soft: doom-1993] ZONEID Pattern — pre-tombstone check
                validate_zoneid(entity.magic, ZONEID_ENTITY, f"EntityRegistry.remove({name})")
                # [id-soft: doom-1993] Lazy Deletion — set sentinel, keep in dict
                self._tombstoned[key] = time.monotonic()
                entity.magic = ZONEID_TOMBSTONE
                await self._save()
                return True
            return False

    def _reap_tombstoned(self, grace_seconds: Optional[float] = None) -> int:
        """Remove tombstoned entities past the grace period.

        [id-soft: doom-1993] Lazy Deletion — periodic sweep of sentinel entities
        [id-soft: quake-1996] Grace Period — 0.5s delay before reaping

        Args:
            grace_seconds: Override grace period. Defaults to
                TOMBSTONE_GRACE_SECONDS (0.5s).

        Returns:
            Number of entities reaped.
        """
        if grace_seconds is None:
            grace_seconds = self.TOMBSTONE_GRACE_SECONDS
        now = time.monotonic()
        to_reap = []
        for key, ts in self._tombstoned.items():
            if now - ts >= grace_seconds:
                to_reap.append(key)
        reaped = 0
        for key in to_reap:
            if key in self._entities:
                del self._entities[key]
                self._tombstoned.pop(key, None)
                self._wad_sources.pop(key, None)
                reaped += 1
        if reaped:
            logger.debug("Reaped %d tombstoned entities (grace=%.1fs)", reaped, grace_seconds)
        return reaped

    def active_iter(self) -> List[Entity]:
        """Iterate over non-tombstoned entities.

        [id-soft: doom-1993] Lazy Deletion — P_RemoveThinker sweep pattern
        Derived from DOOM 1993 p_tick.c:62-103: entities with sentinel
        markers are skipped; actual reaping happens asynchronously.

        Currently O(n) — future optimization: maintain a separate
        active set with [id-soft: doom-1993] Mobj Dual-Linking pattern.
        """
        return [e for e in self._entities.values() if e.magic != ZONEID_TOMBSTONE]

    def count_active(self) -> int:
        """Count non-tombstoned entities."""
        return len(self.active_iter())

    # ── Name Utility ───────────────────────────────────────────────────
    # short_name_hash is preserved as a utility for generating deterministic
    # 64-bit integer keys from entity names. Originally inspired by id Soft-
    # ware's 8-byte WAD lump convention (2× int32 compare), the encoding is
    # still useful for hash-ring lookups and sharding. The 8-char cap has
    # been lifted — names longer than 8 chars are hashed with a warning.

    @staticmethod
    def short_name_hash(name: str, default: int = 0) -> int:
        """Encode a name as a 64-bit deterministic integer key.

        Useful for hash-ring sharding and cross-reference lookups.
        Names longer than 8 chars are truncated with a warning.
        """
        max_len = 8  # Keep the 64-bit encoding; cap at 8 for uint64
        truncated = name[:max_len]
        if len(name) > max_len:
            logger.warning(
                "short_name_hash: name '%s' truncated to '%s' "
                "(%d chars, max %d).",
                name, truncated, len(name), max_len,
            )
        padded = truncated.ljust(max_len, '\x00')[:8]
        return struct.unpack('>Q', padded.encode('ascii', errors='replace'))[0]

    def _validate_name(self, name: str) -> str:
        """Validate and normalize an entity name.

        Returns the normalized name (lowercase, stripped).
        Raises ValueError if the name is empty.
        """
        if not name or not name.strip():
            raise ValueError("Entity name must be non-empty")
        return name.strip().lower()

    def find_by_domain(self, text: str) -> Optional[Entity]:
        """Find the best entity match for a query text based on domain keywords.

        Matches Pillar Keepers only (Nova handles routing separately).
        Scores each entity by how many domain keywords appear in the text.
        Uses word-boundary matching to avoid substring false positives.
        Returns the highest-scoring entity, or None if no match.
        """
        text_lower = text.lower()
        best_score = 0
        best_entity: Optional[Entity] = None
        words = set(text_lower.split())

        for entity in self.list_pillar_keepers():
            score = 0
            for keyword in entity.domains:
                kw_lower = keyword.lower()
                if kw_lower in words or f" {kw_lower} " in f" {text_lower} ":
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
        
        [id-soft: doom-1993] Lazy Deletion — reap tombstoned entities before save.
        This prevents tombstoned entities from persisting to disk and coming
        back alive on the next _load().
        """
        self._reap_tombstoned()

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
