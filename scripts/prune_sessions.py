# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("session_pruner")

HALL_OF_RECORDS = Path("data/knowledge/HALL_OF_RECORDS")
ARCHIVE_DIR = HALL_OF_RECORDS / "_archive"
RETENTION_DAYS = 7
SECONDS_IN_DAY = 86400

def prune_sessions():
    if not HALL_OF_RECORDS.exists():
        logger.error("HALL_OF_RECORDS directory not found")
        return

    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    cutoff = now - (RETENTION_DAYS * SECONDS_IN_DAY)
    
    pruned_count = 0
    
    # Iterate through agent directories
    for agent_dir in HALL_OF_RECORDS.iterdir():
        if agent_dir.is_dir() and agent_dir.name != "_archive":
            # Iterate through session files
            for session_file in agent_dir.glob("*.json"):
                mtime = session_file.stat().st_mtime
                if mtime < cutoff:
                    # Move to archive, preserving agent structure
                    dest_dir = ARCHIVE_DIR / agent_dir.name
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    
                    try:
                        shutil.move(str(session_file), str(dest_dir / session_file.name))
                        logger.info(f"Pruned: {session_file.name} from {agent_dir.name}")
                        pruned_count += 1
                    except Exception as e:
                        logger.error(f"Failed to move {session_file}: {e}")
    
    logger.info(f"Pruning complete. Total sessions moved to archive: {pruned_count}")

if __name__ == "__main__":
    prune_sessions()
