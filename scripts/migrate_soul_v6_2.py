# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# AP: AP-SOUL-MIGRATE-V6_2
"""
🔱 SOUL MIGRATION V6.2
Role: Migrate all entity soul.yaml files to the v6.2 schema.
Adds critical metadata fields for sovereign tracking and health monitoring.
"""

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import anyio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("soul_migrate")

# ============================================================================
# MIGRATION LOGIC
# ============================================================================

async def migrate_soul_file(path: Path):
    """Migrate a single soul.yaml file to v6.2."""
    try:
        # Read existing soul
        content = await anyio.Path(path).read_text()
        # Note: soul.yaml is YAML, but for this script we'll use a simple 
        # YAML-like parser or assume it's JSON-compatible for the metadata part.
        # Since we are in Python, we should use PyYAML.
        import yaml
        
        soul = yaml.safe_load(content)
        if not soul:
            return False
        
        # Update version
        soul["version"] = "v6.2"
        
        # Add/Update metadata
        metadata = soul.get("metadata", {})
        
        # Set created_at if missing
        if "created_at" not in metadata:
            # Fallback to file creation time
            stat = await anyio.Path(path).stat()
            metadata["created_at"] = datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat()
        
        # Set last_updated
        metadata["last_updated"] = datetime.now(timezone.utc).isoformat()
        
        # Set health_score (default to 50.0)
        if "health_score" not in metadata:
            metadata["health_score"] = 50.0
            
        # Set entity_id (use filename if missing)
        if "entity_id" not in metadata:
            metadata["entity_id"] = path.stem
            
        soul["metadata"] = metadata
        
        # Write back
        await anyio.Path(path).write_text(yaml.dump(soul, sort_keys=False))
        return True
        
    except Exception as e:
        logger.error(f"Failed to migrate {path}: {e}")
        return False

async def main():
    data_dir = Path("data/entities")
    if not data_dir.exists():
        logger.error("Entities directory not found: %s", data_dir)
        return

    count = 0
    async for ent_dir in anyio.Path(data_dir).iterdir():
        if not await anyio.Path(ent_dir).is_dir():
            continue
        
        soul_file = ent_dir / "soul.yaml"
        if await anyio.Path(soul_file).exists():
            if await migrate_soul_file(soul_file):
                count += 1
                logger.info("Migrated %s to v6.2", soul_file)

    logger.info("Migration complete. %d souls updated to v6.2", count)

if __name__ == "__main__":
    anyio.run(main)
