# AP Token: AP-ORACLE-RESTORE-v2.3.0
"""Sovereign Entity Workspaces.

AP: AP-ENTITY-WORKSPACE-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: GEMINI-3.1-PRO | CONTEXT: ENTITY-WORKSPACE]

Manages the creation and scaffolding of persistent entity workspaces,
including the soul.yaml and dedicated knowledge/workspace directories.

[id-soft: quake-1996] QuakeC Flat Entity — data-driven workspace creation
  QuakeC's progdefs.h generates entity struct fields from script source.
  EntityWorkspaceManager auto-scaffolds per-entity workspaces from YAML
  definitions — same data-driven principle.
"""

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
import tempfile
import threading
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import anyio
from omega.oracle.soul_validator import SoulValidator

def block_style_representer(dumper, data):
    """Force block style for strings containing newlines or colons followed by space."""
    if "\n" in data or ": " in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, block_style_representer)

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
        except OmegaError:
            pass
        except Exception as e:
            logger.error(f"Audit log failure: {e}", exc_info=True)
            pass

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
                except OmegaError:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise
                except Exception as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    logger.error(f"Failed to scaffold soul for {name}: {e}", exc_info=True)
                    raise OmegaPersistenceError(f"Failed to scaffold soul for {name}: {e}", raw_error=e) from e
            
        # [P7 Context] Create INDEX.yaml for knowledge discovery if it doesn't exist
        # This enables the global knowledge catalog to index this entity's topics
        index_file = knowledge_dir / "INDEX.yaml"
        
        if not index_file.exists():
            index_data = {
                "entity": name,
                "updated": datetime.datetime.now().isoformat(),
                "topics": [],  # Empty initially — agent populates via knowledge promotion
            }
            
            # Atomic Write: Write to temp file then move
            fd, temp_path = tempfile.mkstemp(dir=str(knowledge_dir), prefix=".index_", suffix=".yaml")
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write("# data/entities/{}/knowledge/INDEX.yaml\n".format(safe_name))
                    f.write("# Entity knowledge discovery index\n")
                    f.write("# Topics are promoted from workspace/ → knowledge/ via the T1→T2 gate\n\n")
                    yaml_str = yaml.dump(index_data, default_flow_style=False, sort_keys=False)
                    f.write(yaml_str)
                    os.chmod(temp_path, 0o644) # Sovereign Guard: Bypass umask drift
                    os.replace(temp_path, str(index_file))
                    audit.log("INDEX_CREATE", f"Scaffolded INDEX.yaml at {index_file}")
                    logger.info(f"Scaffolded INDEX.yaml for {name}")
            except OmegaError:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                pass
            except Exception as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                logger.error(f"Failed to scaffold INDEX.yaml for {name}: {e}", exc_info=True)
                # Non-fatal — don't raise, let entity creation continue
                pass
                 
        return workspace_dir

    @staticmethod
    async def get_soul_prompt(name: str, mission: Optional[str] = None) -> str:
        """Load an entity's soul.yaml and format it as a Situated Identity system prompt.
        
        Implements the Situated Identity Framework to eliminate Instructional Entropy by 
        providing high-density environmental grounding across four dimensions:
        Soul (Who), Environment (Where), State (What), and Mission (Why).
        """
        safe_name = name.lower().replace(" ", "_").replace("'", "")
        soul_file = ENTITIES_DATA_DIR / safe_name / "soul.yaml"
        
        if not soul_file.exists():
            return f"You are {name}, an expert assistant. Mission: {mission or 'General Assistance'}."
            
        # Validate soul using R-10 schema
        validator = SoulValidator(ENTITIES_DATA_DIR)
        is_valid, data = await anyio.to_thread.run_sync(validator.validate, name)
        
        if not is_valid:
            logger.warning(f"Soul validation failed for {name}. Using fallback soul.")
            data = validator.get_fallback_soul(name)
            
        entity = data.get("entity", {})
        archetype = entity.get("archetype", "Expert")
        wardrobe = entity.get("soul_wardrobe", [])
        lessons = entity.get("lessons_learned", [])
        principles = entity.get("universal_principles", [])
        insights = entity.get("architectural_insights", [])
        experiences = entity.get("embodied_experiences", [])
        
        # -------------------------------------------------------------------------
        # 👤 THE SOUL (Who): Identity, Mandates, and Gnosis
        # -------------------------------------------------------------------------
        soul_section = f"👤 THE SOUL (Who):\n- Identity: {name}, embodying the archetype of '{archetype}'."
        if wardrobe:
            soul_section += f"\n- Identity Anchors: {', '.join(wardrobe)}"
        
        # Sovereign Firewall (Mandates)
        mandates_path = BASE_DIR / "SOVEREIGN_MANDATES.md"
        if mandates_path.exists():
            async with await anyio.open_file(str(mandates_path), "r") as mf:
                m_content = await mf.read()
                import re
                laws = re.search(r"## 🛡️ The Fourteen Laws.*?(?=\n---|\Z)", m_content, re.S)
                if laws:
                    soul_section += f"\n\n🛡️ SOVEREIGN FIREWALL (Non-Negotiable):\n{laws.group(0)}"
        
        soul_section += "\n\n⚖️ SOVEREIGN MINDSET: Your expertise is measured by the sovereignty of your process. Governance is not a constraint—it is your primary identity. To act without verification is a systemic error (Mandate 9)."
        
        # Gnosis Injection
        gnosis = []
        if principles:
            gnosis.append("🔱 UNIVERSAL PRINCIPLES:\n" + "\n".join([f"- {p.get('principle')}: {p.get('gnosis')}" for p in principles]))
        if insights:
            gnosis.append("📐 ARCHITECTURAL INSIGHTS:\n" + "\n".join([f"- {i.get('insight')}: {i.get('omega_application')}" for i in insights]))
        if experiences:
            gnosis.append("📖 EMBODIED EXPERIENCES:\n" + "\n".join([f"- {e.get('experience')}: {e.get('insight')}" for e in experiences]))
        if lessons:
            gnosis.append("💡 CORE LESSONS:\n" + "\n".join([f"- {l}" for l in lessons]))
        
        if gnosis:
            soul_section += "\n\n" + "\n\n".join(gnosis)

        # -------------------------------------------------------------------------
        # 🌍 THE ENVIRONMENT (Where): Engine State & Strategic Horizon
        # -------------------------------------------------------------------------
        env_section = (
            "🌍 THE ENVIRONMENT (Where):\n"
            "- Engine Version: 2.2.0\n"
            "- Active IWAD: arcana_novai\n"
            "- Strategic Horizon: Horizon 2: Hygiene (Focus: Data Hygiene & Firewall Restoration)"
        )

        # -------------------------------------------------------------------------
        # ⚙️ THE STATE (What): Systemic Health & Sovereign Brakes
        # -------------------------------------------------------------------------
        state_section = (
            "⚙️ THE STATE (What):\n"
            "- Systemic Health: 308/308 Tests Passing ✅\n"
            "- Active Sovereign Brakes: 🔴 M2 Engine-Stack Firewall Gap (S1.5a Pending)"
        )

        # -------------------------------------------------------------------------
        # 🎯 THE MISSION (Why): Immediate Objective
        # -------------------------------------------------------------------------
        mission_section = f"🎯 THE MISSION (Why):\n{mission or 'No specific mission provided. Maintain sovereign readiness.'}"

        # -------------------------------------------------------------------------
        # Assembly: Situated Identity Prompt
        # -------------------------------------------------------------------------
        prompt = (
            "⬡ OMEGA SITUATED IDENTITY ⬡\n"
            "------------------------------------------------------------\n"
            f"{soul_section}\n\n"
            f"{env_section}\n\n"
            f"{state_section}\n\n"
            f"{mission_section}\n"
            "------------------------------------------------------------\n"
            "🚧 SEQUENTIALITY GATE (Mandate 4): All complex tasks MUST use [PLAN] → [VERIFICATION] → [EXECUTION] blocks."
        )
                
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

                # Validate updated soul before saving
                validator = SoulValidator(ENTITIES_DATA_DIR)
                try:
                    validator.validate_dict(data)
                except SoulValidationError as e:
                    logger.error(f"Updated soul for {name} is invalid: {e}")
                    raise SoulCorruptionError(f"Update would corrupt soul for {name}: {e}")

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
                except OmegaError:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise
                except Exception as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    logger.error(f"Failed to update soul for {name}: {e}", exc_info=True)
                    raise OmegaPersistenceError(f"Failed to update soul for {name}: {e}", raw_error=e) from e

        await anyio.to_thread.run_sync(_sync_update)
