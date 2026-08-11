# AP: AP-ORACLE-RESTORE-v2.3.0
# 🔱 WAD Loader — Universal Runtime Container Loader
# AP: AP-WAD-LOADER-v1.1.0
#
# Implements the WAD (Where's All Data) architecture.
# Loads self-contained stacks from config/wads/ and registers them into the
# EntityRegistry and Voice system.
#
# Respects the Engine-Stack Firewall: only modifies runtime state.
#
# [id-soft: vet-043] WAD System — IWAD/PWAD separation with backward scan
#   DOOM's WAD format (w_wad.c:376) scans backwards so PWAD patch files
#   take precedence over IWAD base entries. Omega mirrors this: later WAD
#   entity definitions override earlier ones.
# [id-soft: vet-044] 4-Path VFS — search order: active stack → _omega_default
#   Q3A's files.c:39-75 defines base + cd + home + current game search order.
#   Omega's wad_loader follows the same override chain pattern.

# S1.5a Hardening: Schema validation, file size limits, adapter whitelist.


# DocRef: docs/architecture/TRAINING_PIPELINE.md
import logging
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import anyio
from .entity_registry import EntityRegistry, Entity
from .world_state import world_state, WorldLump
from omega.errors import OmegaError
from omega.governance.config_resolver import WADS_DIR

# ── S1.5a Hardening Constants ────────────────────────────────────────
# [id-soft: vet-015] ZONEID — size sentinel for file validation
MAX_YAML_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB — prevents loading huge YAML files
MAX_ENTITY_NAME_LENGTH = 128  # Entity name length cap
MAX_DOMAINS_PER_ENTITY = 20  # Max domains per entity

# Adapter module whitelist — only known-safe modules can be imported from WAD manifests.
# [M2] Engine-Stack Firewall: WADs cannot import arbitrary engine internals.
ADAPTER_MODULE_WHITELIST: Set[str] = {
    "omega.memory.adapters",
    "omega.memory.adapters.mnemosyne_adapter",
}

# Required/core manifest field types (WadManifest V1)
MANIFEST_FIELD_TYPES = {
    "name": str,
    "version": str,
    "entities": (list, dict),
    "adapters": (list, dict),
}

# WadManifest V2 — optional heritage / IWAD metadata fields (explicit allow-list).
# Still extra=forbid: unknown keys reject. V2 fields are typed when present.
# [D-281 sidecar / ho_881bae336522] arcana_novai + _omega_default use these.
MANIFEST_V2_OPTIONAL_FIELD_TYPES = {
    "author": str,
    "description": str,
    "license": str,
    "type": str,  # iwad | pwad
    "mode": str,
    "requires_engine": str,
    "startup": dict,
    "voices": (list, dict),
    "vr_scenes": (list, dict),
    "dependencies": (list, dict),
    "hierarchy": str,  # relative path override for hierarchy.yaml
}

# Required entity field types
ENTITY_FIELD_TYPES = {
    "name": str,
    "domains": list,
    "model": str,
    "personality": str,
    "temperature": (int, float),
    "context_window": int,
    "slots": list,
}


logger = logging.getLogger(__name__)

class WADLoader:
    """Loads Omega Engine stacks (WADs) from the filesystem."""

    def __init__(self, registry: EntityRegistry, wads_dir: Optional[Path] = None, adapter_registry: Optional[Any] = None):
        self.registry = registry
        # OMEGA_WADS_DIR env override preserved; default from config_resolver (D-281 Phase II)
        self.wads_dir = wads_dir or Path(os.environ.get("OMEGA_WADS_DIR", str(WADS_DIR)))
        self._startup_messages: Dict[str, str] = {}  # stack_name -> startup message
        self.active_hierarchy_path: Optional[Path] = None
        self._adapter_registry = adapter_registry  # MemoryAdapterRegistry (optional)
        
        if os.environ.get("OMEGA_ENV") != "test":
            try:
                self.wads_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                logger.warning(f"WADs directory read-only: {self.wads_dir}")

    async def _discover_wads(self) -> List[Dict[str, Any]]:
        """Discover all WAD directories and read their manifest metadata.

        Scans the wads directory for subdirectories containing a manifest.yaml.
        For each valid WAD, extracts metadata: name, type (iwad/pwad),
        dependencies, priority, and version.

        Returns:
            List of WAD metadata dicts, sorted by discovery order.
            Each dict has keys: name, type, dependencies, priority, version,
            path, manifest_path.
        """
        discovered: List[Dict[str, Any]] = []

        try:
            async for entry in anyio.Path(self.wads_dir).iterdir():
                if not await entry.is_dir():
                    continue

                stack_name = entry.name
                wad_path = self.wads_dir / stack_name
                manifest_path = wad_path / "manifest.yaml"

                if not await anyio.Path(manifest_path).exists():
                    logger.debug(f"WAD {stack_name} has no manifest.yaml. Skipping discovery.")
                    continue

                # Read manifest for metadata
                try:
                    async with await anyio.open_file(str(manifest_path), "r") as f:
                        manifest = yaml.safe_load(await f.read())

                    if manifest is None:
                        logger.warning(f"WAD {stack_name} manifest is empty. Skipping discovery.")
                        continue

                    # Support both flat and wad:-wrapped manifests
                    if "wad" in manifest:
                        manifest = manifest["wad"]

                    wad_type = manifest.get("type", "pwad")
                    dependencies = manifest.get("dependencies", [])
                    if isinstance(dependencies, str):
                        dependencies = [dependencies]
                    elif not isinstance(dependencies, list):
                        dependencies = []

                    discovered.append({
                        "name": stack_name,
                        "type": wad_type,
                        "dependencies": dependencies,
                        "priority": manifest.get("priority", 0),
                        "version": manifest.get("version", "unknown"),
                        "path": wad_path,
                        "manifest_path": manifest_path,
                    })
                except (OSError, yaml.YAMLError) as e:
                    logger.warning(f"Failed to read manifest for WAD {stack_name}: {e}")
                    continue

        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to iterate WADs directory for discovery: {e}")

        return discovered

    async def _resolve_load_order(self, discovered: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Resolve the load order for discovered WADs.

        Ordering rules:
        1. IWADs load before PWADs (IWAD = base, PWAD = patch/overlay).
        2. Dependencies load before dependents (topological sort).
        3. Circular dependencies are detected and reported.

        Args:
            discovered: List of WAD metadata dicts from _discover_wads().

        Returns:
            WAD metadata dicts in resolved load order.

        Raises:
            OmegaError: If a circular dependency is detected.
        """
        # Build name -> metadata lookup
        name_to_wad: Dict[str, Dict[str, Any]] = {w["name"]: w for w in discovered}

        # Assign base priority: IWAD = 100, PWAD = 0, plus manifest priority
        def effective_priority(wad: Dict[str, Any]) -> int:
            base = 100 if wad["type"] == "iwad" else 0
            return base + wad.get("priority", 0)

        # Topological sort with cycle detection
        # We use a modified Kahn's algorithm that also respects type-based priority
        # for tie-breaking among independent nodes.

        # Build adjacency: dependency -> [dependents]
        # and in-degree: wad_name -> count of unmet dependencies
        in_degree: Dict[str, int] = {}
        dependents: Dict[str, List[str]] = {w["name"]: [] for w in discovered}

        for wad in discovered:
            name = wad["name"]
            in_degree[name] = 0
            for dep in wad["dependencies"]:
                if dep in name_to_wad:
                    dependents[dep].append(name)
                    in_degree[name] += 1
                else:
                    logger.warning(
                        f"WAD {name} depends on unknown WAD '{dep}'. "
                        f"Dependency will be ignored."
                    )

        # Kahn's algorithm with priority queue (sorted by effective priority)
        # Use a list as a priority queue (sorted each iteration — small N)
        ready = sorted(
            [name for name, deg in in_degree.items() if deg == 0],
            key=lambda n: effective_priority(name_to_wad[n]),
            reverse=True,  # Higher priority first
        )

        resolved: List[Dict[str, Any]] = []
        processed: Set[str] = set()

        while ready:
            # Pick highest-priority ready node
            current_name = ready.pop(0)
            current_wad = name_to_wad[current_name]
            resolved.append(current_wad)
            processed.add(current_name)

            # Reduce in-degree of dependents
            new_ready: List[str] = []
            for dep_name in dependents[current_name]:
                in_degree[dep_name] -= 1
                if in_degree[dep_name] == 0:
                    new_ready.append(dep_name)

            # Merge new ready nodes into the ready list, maintaining priority order
            ready.extend(new_ready)
            ready.sort(
                key=lambda n: effective_priority(name_to_wad[n]),
                reverse=True,
            )

        # Detect circular dependencies
        if len(resolved) < len(discovered):
            unresolved = [w["name"] for w in discovered if w["name"] not in processed]
            raise OmegaError(
                f"Circular dependency detected among WADs: {unresolved}. "
                f"Load order resolution failed."
            )

        return resolved

    async def load_all_wads(self) -> Dict[str, bool]:
        """Discover and load all WADs in the wads directory.

        WADs are loaded in priority order:
        1. IWADs (type: iwad) load first, with higher priority.
        2. PWADs (type: pwad) load after their IWAD dependencies.
        3. Dependencies are resolved via topological sort.
        4. Circular dependencies raise OmegaError.

        Returns a map of stack_name -> success_status.
        """
        results: Dict[str, bool] = {}

        try:
            discovered = await self._discover_wads()
            if not discovered:
                logger.info("No WADs discovered in wads directory.")
                return results

            ordered_wads = await self._resolve_load_order(discovered)

            for wad_meta in ordered_wads:
                stack_name = wad_meta["name"]
                wad_type = wad_meta["type"]
                # IWADs get priority 100, PWADs get priority 0 (base override)
                # plus any manifest-specified priority
                priority = 100 if wad_type == "iwad" else 0
                priority += wad_meta.get("priority", 0)

                logger.info(f"Loading WAD: {stack_name} (type={wad_type}, priority={priority})")
                success, _ = await self.load_wad(stack_name, priority=priority)
                results[stack_name] = success

        except OmegaError as e:
            logger.error(f"WAD auto-loading failed: {e}")
            # Record failure for any WADs not yet loaded
            for wad_meta in discovered:
                if wad_meta["name"] not in results:
                    results[wad_meta["name"]] = False

        return results

    async def load_single_wad(self, stack_name: str, priority: int = 10) -> bool:
        """Load only a single named WAD.
        
        Unlike load_all_wads(), this loads exactly one IWAD and skips the rest.
        The selected IWAD gets higher priority so its entities override entities.yaml.
        
        Args:
            stack_name: Name of the WAD directory to load
            priority: Override priority (default 10 — overrides entities.yaml baseline)
        """
        logger.info(f"Loading single WAD: {stack_name} (priority {priority})")
        success, _ = await self.load_wad(stack_name, priority=priority)
        return success

    def get_startup_message(self, stack_name: Optional[str] = None) -> Optional[str]:
        """Return the startup personality message for a given WAD stack.
        
        If no stack_name is specified, returns the message from the last-loaded WAD
        that defined one (useful for --iwad mode where a specific IWAD is active).
        """
        if stack_name:
            return self._startup_messages.get(stack_name)
        # Return most recently added startup message (active IWAD)
        if self._startup_messages:
            return list(self._startup_messages.values())[-1]
        return None

    async def load_wad(self, stack_name: str, priority: int = 0) -> Tuple[bool, Optional[Path]]:
        """Load a specific WAD stack.
        
        Returns:
            Tuple of (success_status, hierarchy_path)
        """
        # Path traversal guard
        resolved_wad_path = (self.wads_dir / stack_name).resolve()
        if not str(resolved_wad_path).startswith(str(self.wads_dir.resolve())):
            logger.warning(f"Path traversal attempt detected: {stack_name}")
            return False, None

        wad_path = resolved_wad_path
        manifest_path = wad_path / "manifest.yaml"
        
        if not await anyio.Path(manifest_path).exists():
            logger.warning(f"WAD {stack_name} missing manifest.yaml. Skipping.")
            return False, None
            
        # S1.5a: File size guard — reject manifests over 1 MB
        try:
            manifest_stat = await anyio.Path(manifest_path).stat()
            if manifest_stat.st_size > MAX_YAML_SIZE_BYTES:
                logger.error(
                    f"WAD {stack_name} manifest too large: {manifest_stat.st_size} bytes "
                    f"(max {MAX_YAML_SIZE_BYTES}). Possible DoS attempt."
                )
                return False, None
        except OSError:
            pass  # stat() failure is non-fatal; yaml.safe_load will catch truncation
            
        try:
            async with await anyio.open_file(str(manifest_path), "r") as f:
                manifest = yaml.safe_load(await f.read())
                
            if manifest is None:
                raise ValueError(f"WAD {stack_name} manifest is empty")
            
            # Support both flat (name/version/entities) and wad:-wrapped manifests
            if "wad" in manifest:
                manifest = manifest["wad"]
            
            # Validate required fields
            required_fields = ["name", "version", "entities"]
            missing = [f for f in required_fields if f not in manifest]
            if missing:
                raise ValueError(f"WAD {stack_name} manifest missing required fields: {', '.join(missing)}")
            
            # S1.5a: Validate field types (V1 core + V2 heritage optional)
            field_types = {**MANIFEST_FIELD_TYPES, **MANIFEST_V2_OPTIONAL_FIELD_TYPES}
            for field, expected_type in field_types.items():
                if field in manifest and not isinstance(manifest[field], expected_type):
                    raise TypeError(
                        f"WAD {stack_name} manifest field '{field}' has wrong type: "
                        f"expected {expected_type}, got {type(manifest[field]).__name__}"
                    )
            
            # extra="forbid" — reject unknown manifest fields (V1 core ∪ V2 heritage)
            # Do NOT loosen to extra=allow; only versioned explicit fields pass.
            known_manifest_fields = set(field_types.keys())
            unknown_manifest_fields = set(manifest.keys()) - known_manifest_fields
            if unknown_manifest_fields:
                raise ValueError(
                    f"WAD {stack_name} manifest has unknown fields: {sorted(unknown_manifest_fields)}. "
                    f"Known fields: {sorted(known_manifest_fields)}"
                )
            
            # S1.5a: Validate name and version are non-empty strings
            if not manifest.get("name", "").strip():
                raise ValueError(f"WAD {stack_name} manifest 'name' is empty")
            if not manifest.get("version", "").strip():
                raise ValueError(f"WAD {stack_name} manifest 'version' is empty")
            
            # Capture startup personality if defined
            if manifest.get("startup") and manifest["startup"].get("message"):
                self._startup_messages[stack_name] = manifest["startup"]["message"]
            
            logger.info(f"Loading stack {stack_name} (version {manifest.get('version', 'unknown')})")
            
            # 1. Load Entities
            entities_dir = wad_path / "entities"
            if await anyio.Path(entities_dir).exists():
                await self._load_entities(entities_dir, wad_source=stack_name, priority=priority)
                
            # 2. Load Voices (currently mapped to entities in this simple version)
            voices_dir = wad_path / "voices"
            if await anyio.Path(voices_dir).exists():
                await self._load_voices(voices_dir, wad_source=stack_name)
            
            # 3. Resolve Hierarchy Path (if specified in manifest or exists in WAD root)
            hierarchy_path = None
            if "hierarchy" in manifest:
                h_path = wad_path / manifest["hierarchy"]
                if await anyio.Path(h_path).exists():
                    hierarchy_path = h_path
            else:
                default_h_path = wad_path / "hierarchy.yaml"
                if await anyio.Path(default_h_path).exists():
                    hierarchy_path = default_h_path

            if hierarchy_path:
                self.active_hierarchy_path = hierarchy_path

            # 4. Load World State (First Breath)
            world_dir = wad_path / "world"
            if await anyio.Path(world_dir).exists():
                await self._load_world_state(world_dir, wad_source=stack_name)

            # 5. Register Memory Adapter (if specified in manifest)
            if self._adapter_registry and "adapters" in manifest:
                await self._register_adapters(manifest["adapters"], stack_name)

            return True, hierarchy_path

        except (OmegaError, RuntimeError, OSError, ValueError, TypeError, yaml.YAMLError) as e:
            logger.error(f"Failed to load WAD {stack_name}: {e}")
            return False, None

    async def _register_adapters(self, adapters_config: Dict[str, Any], stack_name: str) -> None:
        """Register memory adapters from WAD manifest.

        Supports:
          adapters:
            memory:
              module: "config.wads.arcana_novai.adapters.mnemosyne_adapter"
              class: "MnemosyneAdapter"

        Dynamically imports the module, instantiates the class, and
        registers the instance with the MemoryAdapterRegistry.
        All entities in this WAD are then mapped to this adapter.
        """
        memory_adapter_cfg = adapters_config.get("memory")
        if not memory_adapter_cfg:
            return

        module_path = memory_adapter_cfg.get("module")
        class_name = memory_adapter_cfg.get("class")
        if not module_path or not class_name:
            logger.warning(f"WAD {stack_name} has incomplete memory adapter config: {memory_adapter_cfg}")
            return

        try:
            # S1.5a: Adapter module whitelist enforcement
            # [M2] Engine-Stack Firewall: WADs cannot import arbitrary engine internals.
            if module_path not in ADAPTER_MODULE_WHITELIST:
                logger.error(
                    f"WAD {stack_name} adapter module '{module_path}' not in whitelist. "
                    f"Allowed: {sorted(ADAPTER_MODULE_WHITELIST)}"
                )
                return
                
            # Dynamic import
            import importlib
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)

            if self._adapter_registry is None:
                logger.warning(f"Cannot register adapter for WAD {stack_name}: no adapter registry set")
                return

            # Import IMemoryAdapter for type check
            from omega.memory.adapters import IMemoryAdapter

            instance = adapter_class()

            # P0: Must call initialize() after construction
            # Adapters load sphere/qliphoth data and create vault directories here
            await instance.initialize()

            if not isinstance(instance, IMemoryAdapter):
                logger.error(
                    f"WAD {stack_name} adapter class {class_name} does not implement IMemoryAdapter"
                )
                return

            self._adapter_registry.register(stack_name, instance)
            logger.info(f"Registered memory adapter {class_name} for WAD '{stack_name}'")

            # Map all entities loaded from this WAD to the adapter
            for entity_key, entity in self.registry.list().items():
                if hasattr(entity, 'wad_source') and entity.wad_source == stack_name:
                    # N2: Conflict detection — warn if entity already mapped to different WAD
                    existing_wad = self._adapter_registry._entity_to_adapter.get(entity.name)
                    if existing_wad and existing_wad != stack_name:
                        logger.warning(
                            f"Entity '{entity.name}' already mapped to WAD '{existing_wad}', "
                            f"overwriting with WAD '{stack_name}'"
                        )
                    self._adapter_registry.register_entity_to_wad(entity.name, stack_name)

        except ImportError as e:
            logger.error(f"Failed to import adapter module '{module_path}' for WAD {stack_name}: {e}")
        except AttributeError as e:
            logger.error(f"Adapter class '{class_name}' not found in '{module_path}' for WAD {stack_name}: {e}")
        except (OmegaError, RuntimeError, OSError) as e:
            logger.error(f"Failed to register adapter for WAD {stack_name}: {e}", exc_info=True)

    async def _load_entities(self, entities_dir: Path, wad_source: str = "", priority: int = 0) -> None:
        """Load all .yaml files from the entities directory.
        
        Args:
            entities_dir: Path to the entities directory
            wad_source: WAD name to tag entities with (for IWAD tracking)
            priority: Override priority — higher priority can replace lower priority
        """
        async for path in anyio.Path(entities_dir).glob("**/*.yaml"):
            # Accept any .yaml file. Extract name from parent dir (if soul.yaml) or filename stem.
            if path.name == "soul.yaml":
                entity_name = path.parent.name
            elif path.suffix == ".yaml":
                entity_name = path.stem  # e.g., "sysadmin.yaml" → "sysadmin"
            else:
                continue
            
            if not entity_name:
                continue
            
            # Collision detection with priority resolution
            existing = self.registry.get(entity_name)
            if existing:
                existing_priority = 0  # entities.yaml entities have base priority 0
                if existing.wad_source and existing.wad_source == wad_source:
                    logger.warning(f"Entity {entity_name} already registered from WAD {wad_source}. Skipping duplicate.")
                    continue
                if priority <= existing_priority:
                    logger.info(f"Entity {entity_name} already registered (priority {existing_priority} >= {priority}). Skipping from WAD {wad_source}.")
                    continue
                logger.info(f"Entity {entity_name} already registered (priority {existing_priority} < {priority}). Overriding from WAD {wad_source}.")
            
            try:
                # S1.5a: File size guard for entity files
                try:
                    file_stat = await anyio.Path(path).stat()
                    if file_stat.st_size > MAX_YAML_SIZE_BYTES:
                        logger.warning(
                            f"Entity file {path.name} too large: {file_stat.st_size} bytes. Skipping."
                        )
                        continue
                except OSError:
                    pass  # Non-fatal; yaml.safe_load will handle truncation
                    
                async with await anyio.open_file(str(path), "r") as f:
                    data = yaml.safe_load(await f.read())
                    
                    if data is None:
                        logger.warning(f"Entity file {path.name} is empty. Skipping.")
                        continue
                    
                    # Create Entity object
                    ent_data = data.get("entity", {})
                    
                    if not ent_data:
                        logger.warning(f"Entity file {path.name} missing 'entity' key. Skipping.")
                        continue

                    # S1.5a: Validate entity field types
                    type_errors = []
                    for field, expected_type in ENTITY_FIELD_TYPES.items():
                        if field in ent_data and not isinstance(ent_data[field], expected_type):
                            type_errors.append(
                                f"'{field}' expected {expected_type}, got {type(ent_data[field]).__name__}"
                            )
                    if type_errors:
                        logger.warning(
                            f"Entity {entity_name} has invalid field types: {'; '.join(type_errors)}. Skipping."
                        )
                        continue
                    
                    # D-282: extra="forbid" — reject unknown fields (prevents silent typos)
                    known_fields = set(ENTITY_FIELD_TYPES.keys()) | {"wad_source", "priority"}
                    unknown_fields = set(ent_data.keys()) - known_fields
                    if unknown_fields:
                        logger.warning(
                            f"Entity {entity_name} has unknown fields: {sorted(unknown_fields)}. "
                            f"Known fields: {sorted(known_fields)}. Skipping."
                        )
                        continue
                    
                    # D-282: Range constraints for numeric fields
                    range_errors = []
                    if "temperature" in ent_data:
                        temp = ent_data["temperature"]
                        if not (0.0 <= temp <= 2.0):
                            range_errors.append(f"temperature={temp} out of range [0.0, 2.0]")
                    if "context_window" in ent_data:
                        ctx = ent_data["context_window"]
                        if not (1 <= ctx <= 131072):
                            range_errors.append(f"context_window={ctx} out of range [1, 131072]")
                    if "port" in ent_data and ent_data["port"] is not None:
                        port = ent_data["port"]
                        if not (1 <= port <= 65535):
                            range_errors.append(f"port={port} out of range [1, 65535]")
                    if range_errors:
                        logger.warning(
                            f"Entity {entity_name} has range violations: {'; '.join(range_errors)}. Skipping."
                        )
                        continue
                    
                    # S1.5a: Validate entity name length
                    entity_name_raw = ent_data.get("name", entity_name)
                    if len(entity_name_raw) > MAX_ENTITY_NAME_LENGTH:
                        logger.warning(
                            f"Entity name too long ({len(entity_name_raw)} chars): {entity_name_raw[:50]}... Skipping."
                        )
                        continue
                    
                    # S1.5a: Validate domains count
                    domains = ent_data.get("domains", [])
                    if len(domains) > MAX_DOMAINS_PER_ENTITY:
                        logger.warning(
                            f"Entity {entity_name} has too many domains ({len(domains)}). Skipping."
                        )
                        continue

                    # Collect WAD-specific metadata (everything not in engine core)
                    # [M2] Engine-Stack Firewall: engine sees slots + opaque metadata.
                    # WAD defines: element, chakra, planet, sigil, glyph, pantheon, etc.
                    core_entity_fields = {
                        "name", "domains", "model", "personality", "temperature",
                        "context_window", "slots", "role", "container", "port",
                        "wad_source", "priority",
                    }
                    wad_metadata = {
                        k: v for k, v in ent_data.items()
                        if k not in core_entity_fields and v is not None
                    }

                    entity = Entity(
                        name=ent_data.get("name", entity_name),
                        domains=ent_data.get("domains", []),
                        model=ent_data.get("model", "qwen3-1.7b-q6_k"),
                        personality=ent_data.get("personality", ""),
                        temperature=ent_data.get("temperature", 0.7),
                        context_window=ent_data.get("context_window", 8192),
                        slots=ent_data.get("slots", []),
                        metadata=wad_metadata,
                        role=ent_data.get("role"),
                        container=ent_data.get("container", False),
                        port=ent_data.get("port"),
                        wad_source=wad_source,
                        priority=priority,
                    )
                    await self.registry.add(entity)
                    logger.info(f"Registered entity {entity.name} from WAD {wad_source}")
            except (OmegaError, RuntimeError, OSError, yaml.YAMLError) as e:
                logger.warning(f"Failed to load entity from {path}: {e}")



    async def _load_voices(self, voices_dir: Path, wad_source: str = "") -> None:
        """Load voice configurations from the voices directory."""
        # In the current architecture, voices are essentially entities with 
        # specific activation phrases and roles.
        async for path in anyio.Path(voices_dir).glob("*.yaml"):
            try:
                async with await anyio.open_file(str(path), "r") as f:
                    data = yaml.safe_load(await f.read())
                    
                voice_name = path.stem
                existing = self.registry.get(voice_name)
                if existing:
                    existing_priority = 0
                    if existing.wad_source and existing.wad_source == wad_source:
                        logger.warning(f"Voice {voice_name} already registered from WAD {wad_source}. Skipping.")
                        continue
                    if wad_source and existing.wad_source != wad_source:
                        logger.info(f"Voice {voice_name} already registered from WAD {existing.wad_source}. Skipping voice from WAD {wad_source}.")
                        continue
                
                # Create a voice entity
                entity = Entity(
                    name=voice_name,
                    domains=data.get("domains", []),
                    model=data.get("model", "qwen3-1.7b"),
                    personality=data.get("personality", ""),
                    role=data.get("role", "Voice Interface"),
                    container=True,
                    port=data.get("port", 8080),
                    wad_source=wad_source,
                )
                await self.registry.add(entity)
                logger.info(f"Registered voice {voice_name} from WAD")
            except (OmegaError, RuntimeError, OSError, yaml.YAMLError) as e:
                logger.warning(f"Failed to load voice from {path}: {e}")


    async def _load_world_state(self, world_dir: Path, wad_source: str = "") -> None:
        """Load world-lumps for VR Omegaverse. [id-soft: doom-1993]
        
        Structure: world/<sector_id>/<lump_id>.yaml
        """
        async for sector_path in anyio.Path(world_dir).iterdir():
            if await sector_path.is_dir():
                sector_id = sector_path.name
                async for lump_path in anyio.Path(sector_path).glob("*.yaml"):
                    try:
                        async with await anyio.open_file(str(lump_path), "r") as f:
                            data = yaml.safe_load(await f.read())
                        
                        lump_id = lump_path.stem
                        lump = WorldLump(
                            lump_id=lump_id,
                            data=data.get("world_data", {}),
                            metadata={
                                "wad_source": wad_source,
                                "path": str(lump_path)
                            }
                        )
                        await world_state.load_lump(sector_id, lump)
                        logger.info(f"World State: Loaded lump {lump_id} in sector {sector_id} from {wad_source}")
                    except (OmegaError, RuntimeError, OSError) as e:
                        logger.warning(f"Failed to load world lump {lump_path}: {e}")

