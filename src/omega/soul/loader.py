"""
Soul Loader — Public/Private Split Loader for Soul Data
AP: AP-SOUL-LOADER-v1.0.0
⬡ OMEGA ⬡ P3 ⬡ soul_loader ⬡ PUBLIC-PRIVATE-SPLIT

Implements R19 Soul Privacy Model:
- Splits soul.yaml into soul.public.yaml (git-tracked) + soul.private/ (gitignored)
- Visibility tiers: PUBLIC, BONDED, PRIVATE
- Privacy-filtered recall based on requester identity + bond strength
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import yaml

from omega.soul_store import get_soul_store


class SoulLoader:
    """Loads and manages soul data with PUBLIC/BONDED/PRIVATE split."""
    
    def __init__(self, entity_name: str, base_path: Optional[Path] = None):
        """
        Initialize soul loader for an entity.
        
        Args:
            entity_name: Name of the entity (e.g., "maat", "researcher")
            base_path: Base path for entity data (defaults to data/entities/{entity_name})
        """
        self.entity_name = entity_name
        self.base_path = base_path or Path(f"data/entities/{entity_name}")
        self.store = get_soul_store()
        
        # Define file paths
        self.soul_public_path = self.base_path / "soul.public.yaml"
        self.soul_private_dir = self.base_path / "soul.private"
        self.soul_private_memories_dir = self.soul_private_dir / "memories"
        self.soul_private_bonds_dir = self.soul_private_dir / "bonds"
        self.soul_private_skills_dir = self.soul_private_dir / "skills"
        self.soul_private_evolution_dir = self.soul_private_dir / "evolution"
        self.soul_private_config_dir = self.base_path.parent.parent / "config" / "private"

    # =============================================================================
    # VISIBILITY TIERS
    # =============================================================================
    
    VISIBILITY_PUBLIC = "public"
    VISIBILITY_BONDED = "bonded"
    VISIBILITY_PRIVATE = "private"
    
    VALID_VISIBILITIES = {VISIBILITY_PUBLIC, VISIBILITY_BONDED, VISIBILITY_PRIVATE}
    
    # =============================================================================
    # PUBLIC SOUL OPERATIONS
    # =============================================================================
    
    async def load_public_soul(self) -> Dict[str, Any]:
        """Load the public soul data (git-tracked, shareable)."""
        if not self.soul_public_path.exists():
            return self._default_public_soul()
        
        content = await self.store.read_with_recovery(self.soul_public_path)
        if content is None:
            return self._default_public_soul()
        
        return yaml.safe_load(content) or self._default_public_soul()
    
    def _default_public_soul(self) -> Dict[str, Any]:
        """Return default public soul structure."""
        return {
            "entity": {
                "name": self.entity_name,
                "short": self.entity_name[:4].capitalize(),
                "archetype": "Sovereign Entity",
                "hierarchy_level": 1,
                "sovereignty_level": 1,
                "element": "ether",
                "domain": "General purpose sovereign entity",
                "soul_version": "6.1",
                "last_updated": "",
                "lessons_learned": []
            },
            "identity": {
                "did": f"did:omega:entity:{self.entity_name}",
                "voice_summary": "A sovereign entity in the Omega Engine",
                "values": [],
                "strengths": [],
                "growth_areas": []
            },
            "evolution": {
                "incarnation": 1,
                "lineage": ["genesis"],
                "mutation_log": []
            },
            "bonds": [],
            "skills": []
        }
    
    async def save_public_soul(self, soul_data: Dict[str, Any]) -> None:
        """Save public soul data atomically."""
        # Update timestamp
        from datetime import datetime, timezone
        soul_data["entity"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        content = yaml.dump(soul_data, default_flow_style=False, sort_keys=False)
        await self.store.write_atomic(self.soul_public_path, content)
    
    # =============================================================================
    # PRIVATE SOUL OPERATIONS
    # =============================================================================
    
    async def _ensure_private_dirs(self) -> None:
        """Ensure all private directories exist."""
        dirs = [
            self.soul_private_dir,
            self.soul_private_memories_dir,
            self.soul_private_bonds_dir,
            self.soul_private_skills_dir,
            self.soul_private_evolution_dir,
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    async def append_memory(
        self,
        level: str,  # "L1", "L2", "L3"
        content: str,
        visibility: str = VISIBILITY_PUBLIC,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Append a memory entry to the appropriate private file.
        
        Args:
            level: Memory level (L1, L2, L3)
            content: Memory content
            visibility: Visibility tier (public, bonded, private)
            metadata: Additional metadata
        """
        if visibility not in self.VALID_VISIBILITIES:
            raise ValueError(f"Invalid visibility: {visibility}. Must be one of {self.VALID_VISIBILITIES}")
        
        await self._ensure_private_dirs()
        
        # Determine file path based on level
        level_files = {
            "L1": self.soul_private_memories_dir / "L1_narrative.jsonl",
            "L2": self.soul_private_memories_dir / "L2_insights.jsonl",
            "L3": self.soul_private_memories_dir / "L3_principles.jsonl",
        }
        
        if level not in level_files:
            raise ValueError(f"Invalid level: {level}. Must be L1, L2, or L3")
        
        file_path = level_files[level]
        
        # Create memory entry
        from datetime import datetime, timezone
        entry = {
            "level": level,
            "content": content,
            "visibility": visibility,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "entity": self.entity_name,
        }
        
        if metadata:
            entry["metadata"] = metadata
        
        # Append to JSONL file
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    
    async def load_memories(
        self,
        level: Optional[str] = None,
        visibility: Optional[str] = None,
        requester: Optional[str] = None,
        bond_strength: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Load memories with privacy filtering.
        
        Args:
            level: Filter by level (L1, L2, L3) or None for all
            visibility: Filter by visibility or None for all
            requester: Entity requesting the memories (for privacy filtering)
            bond_strength: Bond strength with requester (for bonded tier)
        
        Returns:
            List of memory entries filtered by privacy rules
        """
        await self._ensure_private_dirs()
        
        # Determine which files to read
        level_files = {
            "L1": self.soul_private_memories_dir / "L1_narrative.jsonl",
            "L2": self.soul_private_memories_dir / "L2_insights.jsonl",
            "L3": self.soul_private_memories_dir / "L3_principles.jsonl",
        }
        
        files_to_read = [level_files[level]] if level else level_files.values()
        
        all_entries = []
        for file_path in files_to_read:
            if not file_path.exists():
                continue
            
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        
                        # Apply privacy filtering
                        if not self._is_visible(entry, requester, bond_strength):
                            continue
                        
                        # Apply visibility filter
                        if visibility and entry.get("visibility") != visibility:
                            continue
                        
                        all_entries.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp (newest first)
        all_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return all_entries
    
    def _is_visible(self, entry: Dict[str, Any], requester: Optional[str], bond_strength: int) -> bool:
        """Check if an entry is visible to the requester based on visibility tier."""
        visibility = entry.get("visibility", self.VISIBILITY_PUBLIC)
        
        if visibility == self.VISIBILITY_PUBLIC:
            return True
        elif visibility == self.VISIBILITY_BONDED:
            return bond_strength >= 50  # Default threshold from R19 spec
        elif visibility == self.VISIBILITY_PRIVATE:
            return requester == self.entity_name
        
        return False
    
    # =============================================================================
    # BONDS OPERATIONS
    # =============================================================================
    
    async def append_bond(
        self,
        entity_id: str,
        strength: int,
        bond_type: str = "professional",
        visibility: str = VISIBILITY_PUBLIC,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Append a bond entry."""
        await self._ensure_private_dirs()
        
        # Public bond metadata goes to public soul
        public_soul = await self.load_public_soul()
        public_bonds = public_soul.setdefault("bonds", [])
        
        # Check if bond already exists
        existing = next((b for b in public_bonds if b.get("entity_id") == entity_id), None)
        if existing:
            existing["strength"] = strength
            existing["bond_type"] = bond_type
        else:
            public_bonds.append({
                "entity_id": entity_id,
                "strength": strength,
                "bond_type": bond_type,
            })
        
        await self.save_public_soul(public_soul)
        
        # Private bond details go to private directory
        if visibility != self.VISIBILITY_PUBLIC and details:
            bond_file = self.soul_private_bonds_dir / "detailed_history.jsonl"
            from datetime import datetime, timezone
            entry = {
                "entity_id": entity_id,
                "strength": strength,
                "bond_type": bond_type,
                "visibility": visibility,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            with open(bond_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    
    # =============================================================================
    # SKILLS OPERATIONS
    # =============================================================================
    
    async def update_skill(
        self,
        name: str,
        level: int,
        xp: int,
        visibility: str = VISIBILITY_PUBLIC,
        learning_event: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Update a skill in public soul and optionally log learning event privately."""
        public_soul = await self.load_public_soul()
        public_skills = public_soul.setdefault("skills", [])
        
        # Update or add skill
        existing = next((s for s in public_skills if s.get("name") == name), None)
        if existing:
            existing["level"] = level
            existing["xp"] = xp
        else:
            public_skills.append({
                "name": name,
                "level": level,
                "xp": xp,
            })
        
        await self.save_public_soul(public_soul)
        
        # Private learning event
        if learning_event:
            await self._ensure_private_dirs()
            skill_file = self.soul_private_skills_dir / "learning_events.jsonl"
            from datetime import datetime, timezone
            entry = {
                "skill_name": name,
                "level": level,
                "xp": xp,
                "visibility": visibility,
                "event": learning_event,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            with open(skill_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    
    # =============================================================================
    # EVOLUTION OPERATIONS
    # =============================================================================
    
    async def record_mutation(
        self,
        mutation_type: str,
        description: str,
        visibility: str = VISIBILITY_PUBLIC,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a mutation in evolution history."""
        public_soul = await self.load_public_soul()
        evolution = public_soul.setdefault("evolution", {})
        mutation_log = evolution.setdefault("mutation_log", [])
        
        from datetime import datetime, timezone
        mutation_entry = {
            "type": mutation_type,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        mutation_log.append(mutation_entry)
        
        # Increment incarnation if major mutation
        if mutation_type in ("major", "incarnation"):
            evolution["incarnation"] = evolution.get("incarnation", 1) + 1
            evolution.setdefault("lineage", []).append(f"v{evolution['incarnation']}")
        
        await self.save_public_soul(public_soul)
        
        # Private mutation details
        if visibility != self.VISIBILITY_PUBLIC and details:
            await self._ensure_private_dirs()
            evo_file = self.soul_private_evolution_dir / "mutation_details.jsonl"
            entry = {
                "type": mutation_type,
                "description": description,
                "visibility": visibility,
                "details": details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            with open(evo_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
    
    # =============================================================================
    # MIGRATION
    # =============================================================================
    
    async def migrate_from_legacy_soul(self, legacy_soul_path: Path) -> None:
        """
        Migrate from legacy single soul.yaml to public/private split.
        
        This reads the legacy soul.yaml and splits it into:
        - soul.public.yaml (identity, evolution metadata, public bonds, public skills)
        - soul.private/ (full memories, bond details, skill learning events, mutation details)
        """
        if not legacy_soul_path.exists():
            return
        
        content = await self.store.read_with_recovery(legacy_soul_path)
        if content is None:
            return
        
        legacy = yaml.safe_load(content)
        if not legacy:
            return
        
        # Extract public data
        public_data = self._default_public_soul()
        
        # Copy identity (public parts)
        if "entity" in legacy:
            public_data["entity"].update({
                k: v for k, v in legacy["entity"].items()
                if k not in ("lessons_learned",)  # Lessons go to private
            })
        
        if "identity" in legacy:
            public_data["identity"] = legacy["identity"]
        
        if "evolution" in legacy:
            public_data["evolution"] = {
                k: v for k, v in legacy["evolution"].items()
                if k != "mutation_details"  # Details go to private
            }
        
        if "bonds" in legacy:
            public_data["bonds"] = [
                {k: v for k, v in b.items() if k in ("entity_id", "strength", "bond_type")}
                for b in legacy["bonds"]
            ]
        
        if "skills" in legacy:
            public_data["skills"] = [
                {k: v for k, v in s.items() if k in ("name", "level", "xp")}
                for s in legacy["skills"]
            ]
        
        # Save public soul
        await self.save_public_soul(public_data)
        
        # Migrate private data
        await self._ensure_private_dirs()
        
        # Migrate lessons to L3 principles
        if "entity" in legacy and "lessons_learned" in legacy["entity"]:
            for lesson in legacy["entity"]["lessons_learned"]:
                await self.append_memory(
                    level="L3",
                    content=lesson.get("lesson", str(lesson)),
                    visibility=self.VISIBILITY_PRIVATE,
                    metadata={"source": "legacy_migration", "original": lesson},
                )
        
        # Migrate bond details
        if "bonds" in legacy:
            for bond in legacy["bonds"]:
                if "details" in bond or "history" in bond:
                    await self.append_bond(
                        entity_id=bond.get("entity_id", ""),
                        strength=bond.get("strength", 0),
                        bond_type=bond.get("bond_type", "professional"),
                        visibility=self.VISIBILITY_BONDED,
                        details=bond.get("details") or bond.get("history"),
                    )
        
        # Migrate skill learning events
        if "skills" in legacy:
            for skill in legacy["skills"]:
                if "learning_events" in skill:
                    for event in skill["learning_events"]:
                        await self.update_skill(
                            name=skill.get("name", ""),
                            level=skill.get("level", 1),
                            xp=skill.get("xp", 0),
                            visibility=self.VISIBILITY_PRIVATE,
                            learning_event=event,
                        )
        
        # Migrate evolution mutation details
        if "evolution" in legacy and "mutation_details" in legacy["evolution"]:
            for detail in legacy["evolution"]["mutation_details"]:
                await self.record_mutation(
                    mutation_type=detail.get("type", "minor"),
                    description=detail.get("description", ""),
                    visibility=self.VISIBILITY_PRIVATE,
                    details=detail,
                )


# =============================================================================
# FACTORY
# =============================================================================

def create_soul_loader(entity_name: str, base_path: Optional[Path] = None) -> SoulLoader:
    """Factory: create a SoulLoader for the given entity."""
    return SoulLoader(entity_name, base_path)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "SoulLoader",
    "create_soul_loader",
]