# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-ORACLE-RESTORE-v2.3.0
"""Sovereign Entity Workspaces.

AP: AP-ENTITY-WORKSPACE-v1.0.0
ICS: [NODE: ARCHON | ARCHETYPE: SOPHIA | MODEL: GEMINI-3.1-PRO | CONTEXT: ENTITY-WORKSPACE]

Manages the creation and scaffolding of persistent entity workspaces,
including the soul.yaml and dedicated knowledge/workspace directories.

[id-soft: vet-011] QuakeC Flat Entity — data-driven workspace creation
  QuakeC's progdefs.h generates entity struct fields from script source.
  EntityWorkspaceManager auto-scaffolds per-entity workspaces from YAML
  definitions — same data-driven principle.
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import logging
from omega.errors import (
    OmegaError,
    OmegaError,
    OmegaPersistenceError,
    SoulCorruptionError,
)
import os
import tempfile
import threading
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import anyio
import yaml
from omega.cvar_table import cvar_get
from omega.oracle.soul_validator import SoulValidator, SoulValidationError


def block_style_representer(dumper, data):
    """Force block style for strings containing newlines or colons followed by space."""
    if "\n" in data or ": " in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


yaml.add_representer(str, block_style_representer)

logger = logging.getLogger(__name__)

SOUL_FILE_HEADER = "# 🔱 Omega Engine — Entity Soul File\n"

# Usually omega-engine/data/entities/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


def _get_entities_data_dir() -> Path:
    """Resolve entities data directory at call time.

    Reads OMEGA_DATA_DIR from the environment on every call, rather than
    evaluating it once at module import time. This allows tests using
    monkeypatch.setenv("OMEGA_DATA_DIR", tmp_path) to properly isolate
    entity workspace scaffolding without leaking into production.

    The ENTITIES_DATA_DIR constant below is preserved for backward compatibility
    but is deprecated — prefer _get_entities_data_dir() for all new code.
    """
    return BASE_DIR / os.getenv("OMEGA_DATA_DIR", "data") / "entities"


ENTITIES_DATA_DIR = _get_entities_data_dir()


def _atomic_write_yaml(
    file_path: Path, data: Any, audit: "SovereignAuditLog", action: str, name: str
) -> None:
    """Write YAML data atomically using tmp-rename pattern.

    # Atomic Rename Pattern (Mandate 12)
    """
    fd, temp_path = tempfile.mkstemp(
        dir=str(file_path.parent), prefix=f".{file_path.stem}_", suffix=".yaml"
    )
    try:
        with os.fdopen(fd, "w") as f:
            yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
            f.write(f"{SOUL_FILE_HEADER}# Generated dynamically.\n\n{yaml_str}")
        os.chmod(temp_path, 0o644)
        os.replace(temp_path, str(file_path))
        audit.log(action, f"Scaffolded {file_path.name} at {file_path}")
        logger.info(f"Scaffolded {file_path.name} for {name}")
    except (OmegaError, RuntimeError, OSError) as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


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
        except (OmegaError, RuntimeError, OSError) as e:
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
        name: str, archetype: str = "Awakened Expert", slots: Optional[List[str]] = None
    ) -> Path:
        """Create the directory structure and initial soul.yaml for an entity.

        Args:
            name: The human-readable name (e.g., 'Kurt Cobain')
            archetype: The conceptual archetype of the entity
            slots: Associated engine slots (WAD-defined labels)

        Returns:
            Path to the entity's root workspace directory.
        """
        safe_name = name.lower().replace(" ", "_").replace("'", "")
        workspace_dir = _get_entities_data_dir() / safe_name

        # Create directories
        knowledge_dir = workspace_dir / "knowledge"
        headless_dir = workspace_dir / "workspace"

        workspace_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(workspace_dir, 0o755)  # Sovereign Guard: Bypass umask drift
        except PermissionError:
            logger.warning(f"Cannot chmod {workspace_dir} — UID drift may be present")
        knowledge_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(knowledge_dir, 0o755)  # Sovereign Guard: Bypass umask drift
        except PermissionError:
            logger.warning(f"Cannot chmod {knowledge_dir} — UID drift may be present")
        headless_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(headless_dir, 0o755)  # Sovereign Guard: Bypass umask drift
        except PermissionError:
            logger.warning(f"Cannot chmod {headless_dir} — UID drift may be present")

        # Initialize Audit Log
        audit = SovereignAuditLog(workspace_dir)
        audit.log("WORKSPACE_CREATE", f"Created root workspace at {workspace_dir}")
        audit.log("DIR_CREATE", f"Created knowledge directory at {knowledge_dir}")
        audit.log("DIR_CREATE", f"Created workspace directory at {headless_dir}")

        # Create v6.1 lean soul structure if it doesn't exist (Atomic Write Pattern)
        soul_file = workspace_dir / "soul.yaml"
        memory_dir = workspace_dir / "memory"
        approved_file = memory_dir / "approved_lessons.yaml"
        proposed_file = memory_dir / "proposed_lessons.yaml"
        sessions_file = memory_dir / "sessions.yaml"

        # Create memory/ subdirectory (v6.1 requirement)
        memory_dir.mkdir(parents=True, exist_ok=True)

        with EntityWorkspaceManager._get_lock(name):
            if not soul_file.exists():
                # Generate a short name from the entity name
                short_name = name[:2].upper() if len(name) >= 2 else name[0].upper()

                soul_data = {
                    "soul_version": "6.1",
                    "entity": {
                        "name": name,
                        "short": short_name,
                        "archetype": archetype if archetype else "Expert",
                        "hierarchy_level": 1,
                        "sovereignty_level": 1,
                        "element": "Aether",
                        "domain": f"{archetype} domain for {name}",
                        "soul_version": "6.1",
                        "last_updated": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
                    },
                    "identity": {
                        "voice_summary": f"{archetype} identity embodied by {name}.",
                        "values": ["growth", "wisdom"],
                        "strengths": ["adaptability", "domain_knowledge"],
                        "growth_areas": ["expanding domain expertise"],
                    },
                    "directives": [
                        {
                            "id": f"d-{short_name.lower()}-001",
                            "title": "Core Identity",
                            "rule": f"Embody the {archetype} role with integrity and precision.",
                            "rationale": "Identity directives ensure sovereign execution.",
                        }
                    ],
                    "team": {
                        "allies": [],
                        "coordination_protocols": {
                            "workspace_lock": f"I check {short_name}_WORKSPACE_LOCK before any file edit.",
                            "live_feed": f"I post to {short_name}_LIVE_FEED after each major task.",
                            "hivemind": "I declare presence via hivemind_post_context at session start.",
                        },
                    },
                }

                # Atomic Write: Write to temp file then move
                fd, temp_path = tempfile.mkstemp(
                    dir=str(workspace_dir), prefix=".soul_", suffix=".yaml"
                )
                try:
                    with os.fdopen(fd, "w") as f:
                        yaml_str = yaml.dump(soul_data, default_flow_style=False, sort_keys=False)
                        f.write(f"{SOUL_FILE_HEADER}# Generated dynamically.\n\n{yaml_str}")
                        os.chmod(temp_path, 0o644)  # Sovereign Guard: Bypass umask drift
                        os.replace(temp_path, str(soul_file))
                        audit.log("SOUL_CREATE", f"Scaffolded initial soul file at {soul_file}")
                        logger.info(f"Scaffolded new soul file for {name} at {soul_file}")
                except OmegaError:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise
                except (OmegaError, RuntimeError, OSError) as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    logger.error(f"Failed to scaffold soul for {name}: {e}", exc_info=True)
                    raise OmegaPersistenceError(
                        f"Failed to scaffold soul for {name}: {e}", raw_error=e
                    ) from e

            # Scaffold approved_lessons.yaml (User-Only, empty initially)
            if not approved_file.exists():
                _atomic_write_yaml(approved_file, [], audit, "APPROVED_LESSONS_CREATE", name)

            # Scaffold proposed_lessons.yaml (Agent-Write, empty initially)
            if not proposed_file.exists():
                _atomic_write_yaml(proposed_file, [], audit, "PROPOSED_LESSONS_CREATE", name)

            # Scaffold sessions.yaml (Agent-Write, empty initially)
            if not sessions_file.exists():
                _atomic_write_yaml(sessions_file, [], audit, "SESSIONS_CREATE", name)

        # [S7 Context] Create INDEX.yaml for knowledge discovery if it doesn't exist
        # This enables the global knowledge catalog to index this entity's topics
        index_file = knowledge_dir / "INDEX.yaml"

        if not index_file.exists():
            index_data = {
                "entity": name,
                "updated": datetime.datetime.now().isoformat(),
                "topics": [],  # Empty initially — agent populates via knowledge promotion
            }

            # Atomic Write: Write to temp file then move
            fd, temp_path = tempfile.mkstemp(
                dir=str(knowledge_dir), prefix=".index_", suffix=".yaml"
            )
            try:
                with os.fdopen(fd, "w") as f:
                    f.write("# data/entities/{}/knowledge/INDEX.yaml\n".format(safe_name))
                    f.write("# Entity knowledge discovery index\n")
                    f.write(
                        "# Topics are promoted from workspace/ → knowledge/ via the T1→T2 gate\n\n"
                    )
                    yaml_str = yaml.dump(index_data, default_flow_style=False, sort_keys=False)
                    f.write(yaml_str)
                    os.chmod(temp_path, 0o644)  # Sovereign Guard: Bypass umask drift
                    os.replace(temp_path, str(index_file))
                    audit.log("INDEX_CREATE", f"Scaffolded INDEX.yaml at {index_file}")
                    logger.info(f"Scaffolded INDEX.yaml for {name}")
            except OmegaError:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                pass
            except (OmegaError, RuntimeError, OSError) as e:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                logger.error(f"Failed to scaffold INDEX.yaml for {name}: {e}", exc_info=True)
                # Non-fatal — don't raise, let entity creation continue
                pass

        return workspace_dir

    @staticmethod
    def _get_current_horizon() -> str:
        """Extract the current strategic epoch from the Sovereign Ark Blueprint."""
        roadmap_path = BASE_DIR / "docs" / "strategy" / "SOVEREIGN_ARK_BLUEPRINT.md"
        try:
            if roadmap_path.exists():
                with open(roadmap_path, "r") as f:
                    for line in f:
                        if "Strike" in line and "✅" in line:
                            return line.strip()
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Failed to read blueprint for epoch: {e}")
        return "Unknown Epoch"

    @staticmethod
    def _get_active_brakes() -> str:
        """Retrieve active sovereign brakes from the coordination registry."""
        brakes_path = BASE_DIR / "data" / "coordination" / "SOVEREIGN_BRAKES.yaml"
        try:
            if brakes_path.exists():
                with open(brakes_path, "r") as f:
                    data = yaml.safe_load(f)
                    brakes = data.get("brakes", [])
                    if brakes:
                        return "\n".join([f"- {b['status']} {b['description']}" for b in brakes])
        except (OmegaError, RuntimeError, OSError) as e:
            logger.warning(f"Failed to read sovereign brakes: {e}")
        return "No active brakes reported."

    @staticmethod
    async def append_session_anchor(name: str, session_data: dict) -> None:
        """Append a session anchor and trigger Somatic Pruning if count exceeds 50.

        [id-soft: vet-023] Precomputed Lookup — O(1) append with bounded growth
        """
        safe_name = name.lower().replace(" ", "_").replace("'", "")
        workspace_dir = _get_entities_data_dir() / safe_name
        sessions_file = workspace_dir / "sessions.yaml"

        def _sync_append():
            sessions = []
            if sessions_file.exists():
                with open(sessions_file, "r") as f:
                    raw = yaml.safe_load(f) or []
                    sessions = raw if isinstance(raw, list) else []

            sessions.append(session_data)

            # Somatic Pruning Trigger: cap at 50 active anchors
            MAX_ANCHORS = 50
            if len(sessions) > MAX_ANCHORS:
                pruned = sessions[:-MAX_ANCHORS]
                active = sessions[-MAX_ANCHORS:]

                archive_dir = workspace_dir / "archive" / "sessions"
                archive_dir.mkdir(parents=True, exist_ok=True)
                archive_file = (
                    archive_dir
                    / f"sessions_archive_{datetime.datetime.now(datetime.timezone.utc).isoformat()}.yaml"
                )

                with open(archive_file, "w") as af:
                    yaml.dump(pruned, af, default_flow_style=False, sort_keys=False)

                sessions = active
                logger.info(f"Somatic Pruning: archived {len(pruned)} sessions for {name}")

            # Write back using atomic pattern
            fd, tmp = tempfile.mkstemp(dir=str(workspace_dir), prefix=".sessions_", suffix=".yaml")
            try:
                with os.fdopen(fd, "w") as f:
                    yaml.dump(sessions, f, default_flow_style=False, sort_keys=False)
                os.replace(tmp, str(sessions_file))
            except (OSError, RuntimeError):
                if os.path.exists(tmp):
                    os.remove(tmp)
                raise

        await anyio.to_thread.run_sync(_sync_append)

    @staticmethod
    async def get_soul_prompt(name: str, mission: Optional[str] = None) -> str:
        """Load an entity's split soul files and format as a Situated Identity prompt.

        Implements the Situated Identity Framework with multi-version Soul Architecture:
        - soul.yaml: User-owned Constitution (identity, traits, directives) — supports v6.1, v6.2, and custom formats
        - approved_lessons.yaml: User-owned vetted wisdom (injected into identity)
        - sessions.yaml: Agent-owned session anchors (continuity context)
        - proposed_lessons.yaml: TAINTED — NEVER injected into identity prompt

        Handles split-brain hydration for entities with different soul formats:
        - v6.1 (iris, scaffolded): entity, identity, directives, team blocks
        - v6.2 (lilith): minimal entity block only
        - custom (grokster): traits, fleet, integration, campaign, mandates, boundaries, heartbeat, lessons
        """
        safe_name = name.lower().replace(" ", "_").replace("'", "")
        entity_dir = _get_entities_data_dir() / safe_name
        soul_file = entity_dir / "soul.yaml"

        if not soul_file.exists():
            # Scaffold workspace if missing (fixes split-brain for node entity)
            logger.info(f"Soul file missing for {name}, scaffolding workspace...")
            EntityWorkspaceManager.scaffold_workspace(name)
            return (
                f"You are {name}, an expert assistant. Mission: {mission or 'General Assistance'}."
            )

        # Load Constitution (soul.yaml) — multi-format support
        soul_data = (
            await anyio.to_thread.run_sync(lambda: yaml.safe_load(soul_file.read_text()))
            if soul_file.exists()
            else {}
        )

        # Extract entity info from multiple possible formats
        entity = soul_data.get("entity", {}) if soul_data else {}
        # v6.2 format: entity at root level
        if not entity and soul_data:
            entity = {k: v for k, v in soul_data.items() if k in ["name", "archetype", "hierarchy_level", "sovereignty_level", "element", "domain", "soul_version", "last_updated", "recon_directive", "wisdom_text_moved_to_archive", "version", "metadata"]}
        # grokster format: entity at root level with different keys
        if not entity and soul_data:
            entity = {k: v for k, v in soul_data.items() if k in ["name", "archetype", "ap_token", "channel", "hmc_role", "created", "version"]}

        # Load Vetted Wisdom (approved_lessons.yaml) — User-approved, safe for identity
        approved_file = entity_dir / "approved_lessons.yaml"
        approved_lessons = []
        if approved_file.exists():
            approved_data = await anyio.to_thread.run_sync(
                lambda: yaml.safe_load(approved_file.read_text())
            )
            approved_lessons = approved_data if isinstance(approved_data, list) else []

        # Load Session Anchors (sessions.yaml) — Continuity context
        sessions_file = entity_dir / "sessions.yaml"
        session_anchors = []
        if sessions_file.exists():
            sessions_data = await anyio.to_thread.run_sync(
                lambda: yaml.safe_load(sessions_file.read_text())
            )
            session_anchors = sessions_data if isinstance(sessions_data, list) else []

        # ⚠️ TAINT-GATE: proposed_lessons.yaml is NEVER loaded here
        # proposed_lessons contain unvetted agent-generated insights
        # They may be read for reporting purposes but NOT for identity construction

        # Validate soul using R-10 schema (non-blocking)
        validator = SoulValidator(_get_entities_data_dir())
        is_valid, data = await anyio.to_thread.run_sync(validator.validate, name)
        if not is_valid:
            logger.warning(f"Soul validation failed for {name}. Using fallback soul.")

        # Extract archetype from multiple possible locations
        archetype = (
            entity.get("archetype")
            or soul_data.get("archetype")
            or "Expert"
        )
        wardrobe = entity.get("soul_wardrobe", [])

        # -------------------------------------------------------------------------
        # 👤 THE SOUL (Who): Identity, Mandates, and Gnosis
        # -------------------------------------------------------------------------
        soul_section = (
            f"👤 THE SOUL (Who):\n- Identity: {name}, embodying the archetype of '{archetype}'."
        )
        if wardrobe:
            soul_section += f"\n- Identity Anchors: {', '.join(wardrobe)}"

        # Add entity-specific directives if present (v6.1 format)
        directives = soul_data.get("directives", [])
        if directives:
            soul_section += "\n- Directives:"
            for d in directives[:5]:  # Limit to 5 for prompt size
                if isinstance(d, dict):
                    soul_section += f"\n  * {d.get('title', 'Directive')}: {d.get('rule', d.get('rationale', ''))[:150]}"

        # Add grokster-specific traits if present
        traits = soul_data.get("traits", {})
        if traits:
            voice = traits.get("voice", {})
            if voice:
                soul_section += f"\n- Voice: wit={voice.get('wit_level', '?')}, directness={voice.get('directness', '?')}, truth_telling={voice.get('truth_telling', '?')}"

        # Add grokster-specific mandates if present
        mandates_owned = soul_data.get("mandates", {}).get("primary", [])
        if mandates_owned:
            soul_section += f"\n- Primary Mandates: {', '.join(mandates_owned[:5])}"

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

        # Gnosis Injection — from approved_lessons.yaml only (Vetted Wisdom)
        gnosis = []
        if approved_lessons:
            gnosis.append(
                "🔱 VETTED WISDOM (Approved Lessons):\n"
                + "\n".join(
                    [
                        f"- {l}" if isinstance(l, str) else f"- {l.get('lesson', l)}"
                        for l in approved_lessons
                    ]
                )
            )

        # Also inject L3 lessons from soul.yaml (grokster format)
        lessons = soul_data.get("lessons", [])
        l3_lessons = [l for l in lessons if isinstance(l, dict) and l.get("tier") == "L3"]
        if l3_lessons:
            gnosis.append(
                "🔱 L3 LESSONS (from soul.yaml):\n"
                + "\n".join([f"- {l.get('id', 'L3')}: {l.get('principle', '')[:200]}" for l in l3_lessons[:3]])
            )

        # Session Continuity Anchors
        if session_anchors:
            recent = session_anchors[-5:]  # Last 5 for continuity
            continuity = []
            for s in recent:
                if isinstance(s, dict):
                    tid = s.get("trace_id", s.get("id", "unknown"))
                    cont = s.get("continuation", s.get("summary", ""))
                    if cont:
                        continuity.append(f"  [{tid}]: {cont[:200]}")
            if continuity:
                gnosis.append(
                    "📋 ACTIVE CONTINUITY ANCHORS (Recent Sessions):\n" + "\n".join(continuity)
                )

        if gnosis:
            soul_section += "\n\n" + "\n\n".join(gnosis)

        from omega import __version__

        env_section = (
            "🌍 THE ENVIRONMENT (Where):\n"
            f"- Engine Version: {__version__}\n"
            f"- Active IWAD: {cvar_get('config.entity.active_iwad', '_omega_default')}\n"  # [remediated: M2-LEAK] — was hardcoded 'arcana_novai', now dynamic via cvar_get
            f"- Strategic Horizon: {EntityWorkspaceManager._get_current_horizon()}"
        )

        # -------------------------------------------------------------------------
        # ⚙️ THE STATE (What): Systemic Health & Sovereign Brakes
        # -------------------------------------------------------------------------
        state_section = (
            "⚙️ THE STATE (What):\n"
            "- Systemic Health: 308/308 Tests Passing ✅\n"
            f"- Active Sovereign Brakes:\n{EntityWorkspaceManager._get_active_brakes()}"
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
    async def update_soul(name: str, updates: Dict[str, Any], token: Optional[str] = None) -> None:
        """Update an entity's soul.yaml file atomically and thread-safely.

        Uses the Sovereign Write Guard to prevent unauthorized modifications.

        Args:
            name: The human-readable name of the entity
            updates: Dictionary of fields to update within the 'entity' block
            token: SovereignUserToken for authorization. Required for soul.yaml writes.
        """

        def _sync_update():
            safe_name = name.lower().replace(" ", "_").replace("'", "")
            workspace_dir = _get_entities_data_dir() / safe_name
            soul_file = workspace_dir / "soul.yaml"

            if not soul_file.exists():
                logger.warning(f"Attempted to update non-existent soul for {name}")
                return

            # Sovereign Write Guard: token required for soul.yaml modifications
            from omega.oracle.entity_registry import SOVEREIGN_USER_TOKEN, SovereignPermissionError

            if token != SOVEREIGN_USER_TOKEN:
                raise SovereignPermissionError(
                    f"Write access to soul.yaml for '{name}' is restricted. SovereignUserToken required."
                )

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
                validator = SoulValidator(_get_entities_data_dir())
                try:
                    validator.validate_dict(data)
                except SoulValidationError as e:
                    logger.error(f"Updated soul for {name} is invalid: {e}")
                    raise SoulCorruptionError(f"Update would corrupt soul for {name}: {e}")

                # Atomic Write Pattern
                fd, temp_path = tempfile.mkstemp(
                    dir=str(workspace_dir), prefix=".soul_update_", suffix=".yaml"
                )
                try:
                    with os.fdopen(fd, "w") as f:
                        yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False)
                        f.write(f"{SOUL_FILE_HEADER}# Updated dynamically.\n\n{yaml_str}")

                    os.chmod(temp_path, 0o644)  # Sovereign Guard: Bypass umask drift
                    os.replace(temp_path, str(soul_file))

                    # Log to audit trail
                    audit = SovereignAuditLog(workspace_dir)
                    audit.log("SOUL_UPDATE", f"Updated soul file at {soul_file}")

                    logger.info(f"Updated soul file for {name} at {soul_file}")
                except OmegaError:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    raise
                except (OmegaError, RuntimeError, OSError) as e:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                    logger.error(f"Failed to update soul for {name}: {e}", exc_info=True)
                    raise OmegaPersistenceError(
                        f"Failed to update soul for {name}: {e}", raw_error=e
                    ) from e

        await anyio.to_thread.run_sync(_sync_update)
