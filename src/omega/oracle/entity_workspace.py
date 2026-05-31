"""Sovereign Entity Workspaces.

AP: AP-ENTITY-WORKSPACE-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: GEMINI-3.1-PRO | CONTEXT: ENTITY-WORKSPACE]

Manages the creation and scaffolding of persistent entity workspaces,
including the soul.yaml and dedicated knowledge/workspace directories.
"""

import logging
import os
import tempfile
import threading
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import anyio

logger = logging.getLogger(__name__)

SOUL_FILE_HEADER = "# 🔱 Omega Engine — Entity Soul File\n"

# Usually omega-engine/data/entities/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENTITIES_DATA_DIR = BASE_DIR / os.getenv("OMEGA_DATA_DIR", "data") / "entities"


class SovereignAuditLog:
    """Immutable audit log for entity workspace modifications."""

    def __init__(self, workspace_dir: Path):
        self.log_file = workspace_dir / "audit.log"

    def log(self, action: str, details: str):
        """Append a modification record to the audit log."""
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        entry = f"[{timestamp}] ACTION: {action} | DETAILS: {details}\n"
        try:
            with open(self.log_file, "a") as f:
                f.write(entry)
        except Exception as e:
            logger.error(f"Audit log failure: {e}")

class EntityWorkspaceManager:
    """Manages the physical persistent storage for awakened entities."""

    _locks: Dict[str, threading.Lock] = {}
    _global_lock = threading.Lock()

    @classmethod
    def _get_lock(cls, name: str) -> threading.Lock:
        """Get or create a thread-lock for a specific entity."""
        safe_name = name.lower().replace(" ", "_").replace("'", "")
        with cls._global_lock:
            if safe_name not in cls._locks:
                cls._locks[safe_name] = threading.Lock()
            return cls._locks[safe_name]

    @staticmethod
    def scaffold_workspace(
        name: str, 
        archetype: str = "Awakened Expert", 
        pillars: Optional[List[str]] = None
    ) -> Path:
        """Create the directory structure and initial soul.yaml for an entity.
        
        Args:
            name: The human-readable name (e.g., 'Kurt Cobain')
            archetype: The conceptual archetype of the entity
            pillars: Associated domain pillars
            
        Returns:
            Path to the entity's root workspace directory.
        """
        safe_name = name.lower().replace(" ", "_").replace("'", "")
        workspace_dir = ENTITIES_DATA_DIR / safe_name
        
        # Create directories
        knowledge_dir = workspace_dir / "knowledge"
        headless_dir = workspace_dir / "workspace"
        
        workspace_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(workspace_dir, 0o755) # Sovereign Guard: Bypass umask drift
        except PermissionError:
            logger.warning(f"Cannot chmod {workspace_dir} — UID drift may be present")
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(knowledge_dir, 0o755) # Sovereign Guard: Bypass umask drift
        except PermissionError:
            logger.warning(f"Cannot chmod {knowledge_dir} — UID drift may be present")
        headless_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(headless_dir, 0o755) # Sovereign Guard: Bypass umask drift
        except PermissionError:
            logger.warning(f"Cannot chmod {headless_dir} — UID drift may be present")
        
        # Initialize Audit Log
        audit = SovereignAuditLog(workspace_dir)
        audit.log("WORKSPACE_CREATE", f"Created root workspace at {workspace_dir}")
        audit.log("DIR_CREATE", f"Created knowledge directory at {knowledge_dir}")
        audit.log("DIR_CREATE", f"Created workspace directory at {headless_dir}")
        
        # Create soul.yaml if it doesn't exist (Atomic Write Pattern)
        soul_file = workspace_dir / "soul.yaml"
        
        with EntityWorkspaceManager._get_lock(name):
            if not soul_file.exists():
                soul_data = {
                    "entity": {
                        "name": name,
                        "archetype": archetype,
                        "pillars": pillars or ["Unknown"],
                        "hierarchy_level": 1,
                        "sovereignty_level": 1,
                        "kind": "persistent_entity",
                        "voice": "standard",
                        "inference": {
                            "temperature": 0.7,
                            "top_p": 0.9
                        },
                        "lessons_learned": [],
                        "procedural_memory": []
                    }
                }
                
                # Atomic Write: Write to temp file then move
                fd, temp_path = tempfile.mkstemp(dir=str(workspace_dir), prefix=".soul_", suffix=".yaml")
                try:
                    with os.fdopen(fd, 'w') as f:
                        yaml_str = yaml.dump(soul_data, default_flow_style=False, sort_keys=False)
                        f.write(f"{SOUL_FILE_HEADER}# Generated dynamically.\n\n{yaml_str}")
                        os.chmod(temp_path, 0o644) # Sovereign Guard: Bypass umask drift
                        os.replace(temp_path, str(soul_file))
                        audit.log("SOUL_CREATE", f"Scaffolded initial soul file at {soul_file}")
                        logger.info(f"Scaffolded new soul file for {name} at {soul_file}")
                except Exception as e:
                    if os.path.exists(temp_path):

                        os.remove(temp_path)
                    logger.error(f"Failed to scaffold soul for {name}: {e}")
                    raise
                
        return workspace_dir

    @staticmethod
    async def get_soul_prompt(name: str) -> str:
        """Load an entity's soul.yaml and format it as a system prompt.
        
        Used by the Orchestrator to inject the entity's identity into
        headless CLI subagents.
        """
        safe_name = name.lower().replace(" ", "_").replace("'", "")
        soul_file = ENTITIES_DATA_DIR / safe_name / "soul.yaml"
        
        if not soul_file.exists():
            return f"You are {name}, an expert assistant."
            
        async with await anyio.open_file(str(soul_file), "r") as f:
            content = await f.read()
            data = yaml.safe_load(content)
            
        entity = data.get("entity", {})
        archetype = entity.get("archetype", "Expert")
        lessons = entity.get("lessons_learned", [])
        
        prompt = f"You are {name}, embodying the archetype of '{archetype}'.\n\n"
        if lessons:
            prompt += "Core Principles & Lessons Learned:\n"
            for lesson in lessons:
                prompt += f"- {lesson}\n"
                
        return prompt

    @staticmethod
    async def update_soul(name: str, updates: Dict[str, Any]) -> None:
        """Update an entity's soul.yaml file atomically and thread-safely.
        
        Args:
            name: The human-readable name of the entity
            updates: Dictionary of fields to update within the 'entity' block
        """
        def _sync_update():
            safe_name = name.lower().replace(" ", "_").replace("'", "")
            workspace_dir = ENTITIES_DATA_DIR / safe_name
            soul_file = workspace_dir / "soul.yaml"

            if not soul_file.exists():
                logger.warning(f"Attempted to update non-existent soul for {name}")
                return

            with EntityWorkspaceManager._get_lock(name):
                # Read existing data
                with open(soul_file, "r") as f:
                    content = f.read()
                    data = yaml.safe_load(content)

                # Apply updates to the 'entity' block
                if "entity" not in data:
                    data["entity"] = {}
                data["entity"].update(updates)

                # Atomic Write Pattern
                fd, temp_path = tempfile.mkstemp(dir=str(workspace_dir), prefix=".soul_update_", suffix=".yaml")
                try:
                    with os.fdopen(fd, 'w') as f:
                        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
                        f.write(f"{SOUL_FILE_HEADER}# Updated dynamically.\n\n{yaml_str}")
                    
                    os.chmod(temp_path, 0o644) # Sovereign Guard: Bypass umask drift
                    os.replace(temp_path, str(soul_file))
                    
                    # Log to audit trail
                    audit = SovereignAuditLog(workspace_dir)
                    audit.log("SOUL_UPDATE", f"Updated soul file at {soul_file}")
                    
                    logger.info(f"Updated soul file for {name} at {soul_file}")
                except Exception as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    logger.error(f"Failed to update soul for {name}: {e}")
                    raise

        await anyio.to_thread.run_sync(_sync_update)
