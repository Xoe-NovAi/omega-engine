# AP Token: AP-ORACLE-RESTORE-v2.3.0
# 🔱 Entity Registry — YAML-backed Entity CRUD
# AP: AP-ENTITY-REGISTRY-v1.0.0
# ICS: [NODE: CORE | ARCHETYPE: SOPHIA | CONTEXT: ENTITY-MANAGEMENT]
#
# Replaces:
#   - omega-stack enhanced_handler.py hardcoded ENTITY_ALIASES/ENTITY_DOMAINS dicts
#   - xna-omega entity_service.py (818 lines, PostgreSQL-dependent)
#
# Design: Pure YAML + dataclass. No database dependency. User-editable.

import logging
from omega.errors import (
    OmegaError, ProviderError, ProviderRateLimitError, ProviderAuthError,
    ProviderTimeoutError, ProviderUnavailableError, ProviderValidationError,
    ProviderSafetyError, InferenceError, InferenceOOMError, InferenceLoadError,
    InferenceRuntimeError, OmegaPersistenceError, SoulCorruptionError,
    SessionPersistenceError, StateIntegrityError, SovereignDiskFullError,
    ConfigError, WADError, BoundaryViolationError, InvariantViolationError,
    EntityTombstonedError, ModelNotFoundError,
)
import os
import time
import struct
import tempfile
import functools
import fcntl
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
import anyio

from omega.oracle.entity_workspace import EntityWorkspaceManager
from omega.constants import ZONEID_ENTITY, ZONEID_TOMBSTONE, validate_zoneid
from omega.errors import EntityTombstonedError

logger = logging.getLogger(__name__)

class SovereignPermissionError(Exception):
    """Raised when an unauthorized entity attempts to write to constitutional files."""
    pass

SOVEREIGN_USER_TOKEN = os.getenv("SOVEREIGN_USER_TOKEN", "SOVEREIGN_DEFAULT_SECURE_TOKEN_2026")

async def write_soul_file(entity_path: str, filename: str, content: str, token: str = None) -> None:
    """Writes a soul file using the Atomic Rename Pattern under strict permission guard.
    
    [id-soft: quake3-1999] Hard-Boundary — strictly separates User/Agent write access.
    """
    if filename in ["soul.yaml", "approved_lessons.yaml"]:
        if token != SOVEREIGN_USER_TOKEN:
            raise SovereignPermissionError(
                f"Write access to {filename} is restricted. SovereignUserToken required."
            )
            
    file_path = Path(entity_path) / filename
    tmp_path = Path(entity_path) / f"{filename}.tmp"
    
    await tmp_path.write_text(content)
    await tmp_path.rename(file_path)

async def with_soul_lock(entity_name: str, action):
    """Ensure exclusive access to soul files during read-modify-write cycles.
    
    Prevents 'Lost Updates' during parallel agent operations (MaKaLi).
    """
    safe_name = entity_name.lower().replace(" ", "_").replace("'", "")
    lock_path = Path(f"data/entities/{safe_name}/.soul.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with await anyio.open_file(lock_path, "a") as f:
        # Use fcntl for advisory locking on the file descriptor
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            return await action()
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

# Test-mode YAML cache: parses entities.yaml once per test run (~5.8s → ~0.001s)
# The 982KB file takes 5.8s to parse; caching it cuts total test suite from 7m to ~2m.
_entity_yaml_cache: Dict[str, Any] = {}

# [id-soft: doom-1993] WAD System — base IWAD identifier
DEFAULT_IWAD = "_omega_default"


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
    traits: Dict[str, Any] = field(default_factory=dict)
    role: Optional[str] = None
    first_breath: Optional[str] = None
    pantheon: Optional[str] = None
    sigil: Optional[str] = None
    container: bool = False
    port: Optional[int] = None
    wad_source: Optional[str] = None
    priority: int = 0  # [Project 3] Layer priority for Shadow-Stacking
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
            **self.traits,
        }

    def is_system(self) -> bool:
        """Check if this is a system-level entity (high-bit flag).
        
        [id-soft: doom-1993] High-Bit Trick — single bit check
        instead of separate boolean field. 1 AND instruction vs 1 struct field.
        """
        return bool(self.flags & EntityRegistry.FLAG_SYSTEM)

    def __getattr__(self, name: str) -> Any:
        """Proxy attribute access to the traits dictionary for WAD-specific metadata.
        
        This ensures backward compatibility with tests and legacy code while 
        maintaining the M2 Firewall by avoiding hardcoded fields in the dataclass.
        """
        if name in self.traits:
            return self.traits[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
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
            if k in ("magic", "_engine_zone", "_game_zone", "__engine_zone__", "__game_zone__"):
                continue  # Runtime-only; not stored in YAML
            result[k] = v
        return result


class EntityRegistry:
    """Loads, saves, and manages entities from YAML config.
    
    [id-soft: doom-1993] Lazy Deletion — entities are tombstoned (magic =
    ZONEID_TOMBSTONE) on remove() and reaped after a grace period.
    [id-soft: quake-1996] Grace Period — 0.5s delay for safety.
    """
    
    # [id-soft: quake-1996] Grace Period — 0.5s realloc delay
    TOMBSTONE_GRACE_SECONDS = 0.5
    
    # [id-soft: doom-1993] High-Bit Trick — flag encoding using high bit
    FLAG_SYSTEM = 0x80000000  # Bit 31: system-level entity (vs user-created)
    FLAG_WAD = 0x40000000     # Bit 30: loaded from a WAD (vs runtime-created)
    FLAG_ACTIVE = 0x00000000  # Default: active entity (low bits = slot flags)
    
    # [id-soft: quake3-1999] Hard-Boundary Struct — engine zone vs game zone
    ENGINE_ZONE_ATTRS = frozenset({
        "magic", "name", "domains", "model", "role",
        "container", "port", "wad_source", "pillars",
    })
    GAME_ZONE_ATTRS = frozenset({
        "personality", "temperature", "context_window",
        "secondary_keeper", "pantheon", "element", "chakra",
        "planet", "sigil", "glyph", "invocation",
    })
    
    # 1. Define Core Slots — The Holographic Grid (D113 Firewall Fix)
    PILLAR_SLOTS = frozenset({
        "p1", "p2", "p3", "p4", "p5",
        "p6", "p7", "p8", "p9", "p10",
    })
    
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
                config_path = str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads" / DEFAULT_IWAD / "entities.yaml")
        
        self.config_path = Path(config_path)
        # [Project 3: Shadow-Stacking] Store entities as a list of layers sorted by priority
        self._entities: Dict[str, List[Entity]] = {}
        self._wad_sources: Dict[str, List[str]] = {}  # lowercase entity name -> list of WAD source names
        # [id-soft: doom-1993] Multi-Index Entity — dual-index lookup
        self._capability_index: Dict[str, List[str]] = {}
        self._lock = None  # Created lazily in async context (C-ARCH-004 pattern)
        # [id-soft: doom-1993] Lazy Deletion — tombstoned entity tracking
        self._tombstoned: Dict[str, float] = {}  # key -> time.monotonic() of tombstone
        self._load()


    def _load(self) -> None:
        """Load entities from YAML file.

        In test mode (OMEGA_ENV=test), caches parsed YAML to avoid re-parsing
        the 982KB entities.yaml on every Oracle() initialization.
        """
        if not self.config_path.exists():
            logger.warning(f"Entity config not found at {self.config_path}")
            self._entities = {}
            return

        cache_key = str(self.config_path)
        # Use cached data in test mode to avoid 5.8s YAML parse per Oracle init
        if os.environ.get("OMEGA_ENV") == "test" and cache_key in _entity_yaml_cache:
            data = _entity_yaml_cache[cache_key]
        else:
            try:
                with open(self.config_path, "r") as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"entities.yaml is empty or malformed: {e}")
            if os.environ.get("OMEGA_ENV") == "test":
                _entity_yaml_cache[cache_key] = data
        
        if data is None:
            raise ValueError("entities.yaml is empty or malformed")

        raw_entities = data.get("entities", {}) if data else {}
        for key, raw in raw_entities.items():
            if raw is None or not isinstance(raw, dict):
                logger.warning(f"Entity '{key}' has empty or malformed definition, skipping")
                continue
            
            # Define core structural fields that belong to the Engine Zone
            # [id-soft: quake3-1999] Hard-Boundary — traits is a core field,
            # NOT a WAD-specific trait. Without this, nested traits dicts from
            # YAML are absorbed as WAD-specific traits, causing recursive nesting.
            core_fields = {
                "name", "domains", "capabilities", "model", "personality", 
                "temperature", "context_window", "pillars", "role", 
                "container", "port", "wad_source", "pantheon", "sigil",
                "traits",  # D-kal-180: prevent recursive nesting corruption
            }
            
            # Everything else is a WAD-specific trait
            traits = {k: v for k, v in raw.items() if k not in core_fields}
            
            entity = Entity(
                name=raw.get("name", key),
                domains=raw.get("domains", []),
                capabilities=raw.get("capabilities", []),
                model=raw.get("model", "qwen3-1.7b-q6_k"),
                personality=raw.get("personality", ""),
                temperature=raw.get("temperature"),
                context_window=raw.get("context_window"),
                pillars=raw.get("pillars", []),
                pantheon=raw.get("pantheon"),
                sigil=raw.get("sigil"),
                traits=traits,
                role=raw.get("role"),
                container=raw.get("container", False),
                port=raw.get("port"),
                wad_source=raw.get("wad_source"),
            )
            key = entity.name.lower()
            # [id-soft: doom-1993] ZONEID Pattern — set at load, not serialized
            entity.magic = ZONEID_ENTITY
            self._entities[key] = [entity]
            
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
        
        [Project 3: Shadow-Stacking] Projects a single Entity by merging layers.
        [id-soft: doom-1993] ZONEID Pattern — validates magic on matched entities
        [id-soft: doom-1993] Lazy Deletion — tombstoned entities treated as not found
        """
        if not name:
            return None
            
        name_lower = name.lower().strip()
        
        # Tier 1: Direct Entity Match (e.g., "sekhmet")
        layers = self._entities.get(name_lower)
        if layers:
            # Filter out tombstoned layers
            active_layers = [l for l in layers if l.magic != ZONEID_TOMBSTONE]
            if not active_layers:
                if raise_on_tombstoned:
                    raise EntityTombstonedError(
                        cache_key=name_lower,
                        message=f"Entity '{name}' was removed (tombstoned) — call active_iter() for current entities",
                    )
                return None
            
            # [Project 3: Shadow-Stacking] Project the layered entity
            return self._project_entity(active_layers)
            
        # Tier 2: Slot Match (e.g., "p1" or "pillar 1")
        slot_key = name_lower.replace("pillar ", "p").replace("pillar", "p")
        if slot_key in self.PILLAR_SLOTS:
            # Resolve the slot to its active role in the default/active IWAD
            # We look for any entity that has this slot in its .pillars list
            for key, layers in self._entities.items():
                active_layers = [l for l in layers if l.magic != ZONEID_TOMBSTONE]
                if not active_layers:
                    continue
                projected = self._project_entity(active_layers)
                if any(p.lower() == slot_key for p in projected.pillars):
                    return projected
        
        # Tier 3: Role Match (e.g., "sysadmin")
        for key, layers in self._entities.items():
            active_layers = [l for l in layers if l.magic != ZONEID_TOMBSTONE]
            if not active_layers:
                continue
            projected = self._project_entity(active_layers)
            if projected.role and projected.role.lower() == name_lower:
                return projected
                
        return None

    def _project_entity(self, layers: List[Entity]) -> Entity:
        """Project a single Entity by merging multiple layers.
        
        Engine Zone: Highest priority layer wins (Standard Override).
        Game Zone: Traits are merged (Concatenation/Union).
        """
        # Base layer is the lowest priority (last in list)
        base = layers[-1]
        
        # Start with a copy of the base
        projected = Entity(
            name=base.name,
            domains=list(base.domains),
            model=base.model,
            personality=base.personality,
            capabilities=list(base.capabilities),
            temperature=base.temperature,
            context_window=base.context_window,
            pillars=list(base.pillars),
            traits=dict(base.traits),
            role=base.role,
            container=base.container,
            port=base.port,
            wad_source=base.wad_source,
            pantheon=base.pantheon,
            sigil=base.sigil,
            first_breath=base.first_breath,
            priority=layers[0].priority, # Highest priority of the stack
        )
        
        # Merge layers from lowest to highest priority
        for layer in reversed(layers):
            # 1. Engine Zone: Override
            projected.model = layer.model or projected.model
            projected.role = layer.role or projected.role
            projected.container = layer.container if layer.container else projected.container
            projected.port = layer.port or projected.port
            projected.wad_source = layer.wad_source or projected.wad_source
            projected.pantheon = layer.pantheon or projected.pantheon
            projected.sigil = layer.sigil or projected.sigil
            projected.first_breath = layer.first_breath or projected.first_breath
            
            # 2. Game Zone: Merge/Union
            # Domains & Capabilities: Set Union
            projected.domains = list(set(projected.domains + layer.domains))
            projected.capabilities = list(set(projected.capabilities + layer.capabilities))
            
            # Traits: Merge dictionaries (Highest priority wins)
            projected.traits.update(layer.traits)
            
            # Personality & Invocation: Concatenation
            if layer.personality and layer.personality != projected.personality:
                projected.personality = f"{layer.personality}\n\n{projected.personality}" if projected.personality else layer.personality
            
            # Invocation is now a trait, handled by .update() above.
                
            # Other core traits: Highest priority wins
            projected.temperature = layer.temperature or projected.temperature
            projected.context_window = layer.context_window or projected.context_window

            
        # Final validation
        projected.magic = ZONEID_ENTITY
        return projected


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
        return {k: self._project_entity([l for l in layers if l.magic != ZONEID_TOMBSTONE]) 
                for k, layers in self._entities.items() 
                if any(l.magic != ZONEID_TOMBSTONE for l in layers)}
    
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
        """Add a new entity layer.
        
        [Project 3: Shadow-Stacking] Entities are stored as a list of layers.
        New layers are appended and sorted by priority (highest first).
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
            
            # [Project 3: Shadow-Stacking] Layered storage
            if key not in self._entities:
                self._entities[key] = []
            self._entities[key].append(entity)
            # Sort layers by priority (descending)
            self._entities[key].sort(key=lambda e: e.priority, reverse=True)
            
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

        self._entities is Dict[str, List[Entity]] (one key can hold stacked
        layers from multiple WAD sources). Flatten all layers and filter
        tombstoned entities.

        Currently O(n) — future optimization: maintain a separate
        active set with [id-soft: doom-1993] Mobj Dual-Linking pattern.
        """
        return [
            e
            for layers in self._entities.values()
            for e in layers
            if e.magic != ZONEID_TOMBSTONE
        ]

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
        When scores tie, prefers the entity whose domain keyword appears
        earliest in the query (the first-mentioned domain is likely the
        primary intent).
        Returns the highest-scoring entity, or None if no match.
        """
        text_lower = text.lower()
        best_score = 0
        best_entity: Optional[Entity] = None
        best_first_pos: int = len(text_lower) + 1
        words = set(text_lower.split())
        
        for key, layers in self._entities.items():
            active_layers = [l for l in layers if l.magic != ZONEID_TOMBSTONE]
            if not active_layers:
                continue
            projected = self._project_entity(active_layers)
            # All entities are routable by domain — no pillar gate (D179)
                
            score = 0
            first_pos = len(text_lower) + 1
            for keyword in projected.domains:
                kw_lower = keyword.lower()
                if kw_lower in words or f" {kw_lower} " in f" {text_lower} ":
                    score += 1
                    pos = text_lower.find(kw_lower)
                    if pos != -1 and pos < first_pos:
                        first_pos = pos
            if score > best_score or (score == best_score and score > 0 and first_pos < best_first_pos):
                best_score = score
                best_entity = projected
                best_first_pos = first_pos
        
        return best_entity if best_score > 0 else None


    def find_by_name_fragment(self, fragment: str) -> Optional[Entity]:
        """Find entity by partial name match (for 'summon' detection)."""
        frag = fragment.lower()
        for key, layers in self._entities.items():
            active_layers = [l for l in layers if l.magic != ZONEID_TOMBSTONE]
            if not active_layers:
                continue
            projected = self._project_entity(active_layers)
            if frag in key or frag in projected.name.lower():
                return projected
        return None

    async def _save(self) -> None:
        """Save current entities back to YAML file.
        
        Uses Sovereign Atomic Write (Flush -> Sync -> Commit -> Anchor) to prevent data loss on crash.
        
        [id-soft: doom-1993] Lazy Deletion — reap tombstoned entities before save.
        This prevents tombstoned entities from persisting to disk and coming
        back alive on the next _load().
        
        Integrity Guard: Detects recursive/bloated entity data (>1MB) and aborts the
        save to prevent `entities.yaml` corruption from circular serialization bugs.
        """
        self._reap_tombstoned()

        def _sync_save():
            data = {"entities": {}}
            for key, layers in self._entities.items():
                # Project stacked layers into a single Entity for serialization.
                # Skip keys whose layers are all tombstoned.
                active_layers = [l for l in layers if l.magic != ZONEID_TOMBSTONE]
                if not active_layers:
                    continue
                projected = self._project_entity(active_layers)
                data["entities"][key] = projected.to_dict()
            
            # Integrity Guard: Check for bloated data before writing
            # (prevents recursive/circular serialization bugs from corrupting entities.yaml)
            serialized = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
            if len(serialized) > 1_000_000:  # 1MB threshold
                logger.error(
                    f"INTEGRITY GUARD: entities.yaml serialization is {len(serialized)} bytes "
                    f"(>{1_000_000}). Aborting save to prevent corruption. "
                    f"Check Entity.to_dict() for circular references in traits."
                )
                # Log the first and last entity key to help debug the cause
                if data["entities"]:
                    first_key = next(iter(data["entities"]))
                    logger.error(f"First entity key: {first_key}, dict size: {len(str(data['entities'][first_key]))}")
                return
            
            temp_dir = self.config_path.parent
            fd, temp_path = tempfile.mkstemp(dir=str(temp_dir), suffix=".tmp")
            try:
                # 1. Write and Sync File
                with os.fdopen(fd, "w") as tf:
                    tf.write(serialized)
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
