# 🔱 WAD Loader — Universal Runtime Container Loader
# AP: AP-WAD-LOADER-v1.0.0
# ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | CONTEXT: RUNTIME-LOADING]
#
# Implements the WAD (Where's All Data) architecture.
# Loads self-contained stacks from config/wads/ and registers them into the
# EntityRegistry and Voice system.
#
# Respects the Engine-Stack Firewall: only modifies runtime state.

import logging
import os
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import anyio
from .entity_registry import EntityRegistry, Entity

logger = logging.getLogger(__name__)

class WADLoader:
    """Loads Omega Engine stacks (WADs) from the filesystem."""

    def __init__(self, registry: EntityRegistry, wads_dir: Optional[Path] = None):
        self.registry = registry
        self.wads_dir = wads_dir or Path(os.environ.get(
            "OMEGA_WADS_DIR",
            str(Path(__file__).resolve().parent.parent.parent.parent / "config" / "wads")
        ))
        self._startup_messages: Dict[str, str] = {}  # stack_name -> startup message
        self.active_hierarchy_path: Optional[Path] = None
        
        if os.environ.get("OMEGA_ENV") != "test":
            try:
                self.wads_dir.mkdir(parents=True, exist_ok=True)
            except PermissionError:
                logger.warning(f"WADs directory read-only: {self.wads_dir}")

    async def load_all_wads(self) -> Dict[str, bool]:
        """Discover and load all WADs in the wads directory.
        
        Returns a map of stack_name -> success_status.
        """
        results = {}
        
        try:
            async for entry in anyio.Path(self.wads_dir).iterdir():
                if await entry.is_dir():
                    stack_name = entry.name
                    logger.info(f"Loading WAD: {stack_name}")
                    success, _ = await self.load_wad(stack_name)
                    results[stack_name] = success
        except Exception as e:
            logger.error(f"Failed to iterate WADs directory: {e}")
            
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

            return True, hierarchy_path
        except Exception as e:
            logger.error(f"Failed to load WAD {stack_name}: {e}")
            return False, None

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
                async with await anyio.open_file(str(path), "r") as f:
                    data = yaml.safe_load(await f.read())
                    
                    # Create Entity object
                    ent_data = data.get("entity", {})


                    entity = Entity(
                        name=ent_data.get("name", entity_name),
                        domains=ent_data.get("domains", []),
                        model=ent_data.get("model", "qwen3-1.7b-q6_k"),
                        personality=ent_data.get("personality", ""),
                        temperature=ent_data.get("temperature", 0.7),
                        context_window=ent_data.get("context_window", 8192),
                        pillars=ent_data.get("pillars", []),
                        secondary_keeper=ent_data.get("secondary_keeper"),
                        pantheon=ent_data.get("pantheon"),
                        element=ent_data.get("element"),
                        chakra=ent_data.get("chakra"),
                        planet=ent_data.get("planet"),
                        sigil=ent_data.get("sigil"),
                        glyph=ent_data.get("glyph"),
                        invocation=ent_data.get("invocation"),
                        role=ent_data.get("role"),
                        container=ent_data.get("container", False),
                        port=ent_data.get("port"),
                        wad_source=wad_source,
                    )
                    await self.registry.add(entity)
                    logger.info(f"Registered entity {entity.name} from WAD {wad_source}")

            except Exception as e:
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

            except Exception as e:
                logger.warning(f"Failed to load voice from {path}: {e}")
