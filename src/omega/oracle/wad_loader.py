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
from typing import Any, Dict, List, Optional

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
                if await anyio.Path(entry).is_dir():
                    stack_name = entry.name
                    logger.info(f"Loading WAD: {stack_name}")
                    success = await self.load_wad(stack_name)
                    results[stack_name] = success
        except Exception as e:
            logger.error(f"Failed to iterate WADs directory: {e}")
            
        return results

    async def load_wad(self, stack_name: str) -> bool:
        """Load a specific WAD stack.
        
        1. Read manifest.yaml
        2. Load entities from entities/
        3. Load voices from voices/
        """
        wad_path = self.wads_dir / stack_name
        manifest_path = wad_path / "manifest.yaml"
        
        if not await anyio.Path(manifest_path).exists():
            logger.warning(f"WAD {stack_name} missing manifest.yaml. Skipping.")
            return False
            
        try:
            async with await anyio.open_file(str(manifest_path), "r") as f:
                manifest = yaml.safe_load(await f.read())
                
            logger.info(f"Loading stack {stack_name} (version {manifest.get('version', 'unknown')})")
            
            # 1. Load Entities
            entities_dir = wad_path / "entities"
            if await anyio.Path(entities_dir).exists():
                await self._load_entities(entities_dir)
                
            # 2. Load Voices (currently mapped to entities in this simple version)
            voices_dir = wad_path / "voices"
            if await anyio.Path(voices_dir).exists():
                await self._load_voices(voices_dir)
                
            return True
        except Exception as e:
            logger.error(f"Failed to load WAD {stack_name}: {e}")
            return False

    async def _load_entities(self, entities_dir: Path) -> None:
        """Load all soul.yaml files from the entities directory."""
        async for path in anyio.Path(entities_dir).glob("**/*.yaml"):
            if path.name == "soul.yaml":
                try:
                    async with await anyio.open_file(str(path), "r") as f:
                        data = yaml.safe_load(await f.read())
                        
                    # Extract entity name from path or data
                    # Path: entities/sekhmet/soul.yaml -> name = sekhmet
                    entity_name = path.parent.name
                    
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
                    )
                    self.registry.add(entity)
                    logger.info(f"Registered entity {entity.name} from WAD")
                except Exception as e:
                    logger.warning(f"Failed to load entity from {path}: {e}")

    async def _load_voices(self, voices_dir: Path) -> None:
        """Load voice configurations from the voices directory."""
        # In the current architecture, voices are essentially entities with 
        # specific activation phrases and roles.
        async for path in anyio.Path(voices_dir).glob("*.yaml"):
            try:
                async with await anyio.open_file(str(path), "r") as f:
                    data = yaml.safe_load(await f.read())
                    
                voice_name = path.stem
                # Create a voice entity
                entity = Entity(
                    name=voice_name,
                    domains=data.get("domains", []),
                    model=data.get("model", "qwen3-1.7b"),
                    personality=data.get("personality", ""),
                    role=data.get("role", "Voice Interface"),
                    container=True,
                    port=data.get("port", 8080),
                )
                self.registry.add(entity)
                logger.info(f"Registered voice {voice_name} from WAD")
            except Exception as e:
                logger.warning(f"Failed to load voice from {path}: {e}")
