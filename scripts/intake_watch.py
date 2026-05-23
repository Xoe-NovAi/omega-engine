#!/usr/bin/env python3
"""
🔱 Omega Engine — Intake Sentinel
AP: AP-INTAKE-SENTINEL-v1.0.0

The Intake Sentinel monitors raw data input directories and triggers the digestion
workflow for new, processable files. It ensures a clean handoff between raw intake
and the Curation Pipeline.
"""

import os
import sys
import hashlib
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Set, Tuple

import anyio

# --- Configuration ---
PORTALS = {
    "inbox": Path("data/inbox"),
    "mining_queue": Path("data/mining_queue"),
    "research": Path("data/research"),
}

PROCESSED_DIR = Path("data/processed")
REJECTED_DIR = Path("data/rejected")
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
CHECK_INTERVAL = 5.0
DIGESTOR_PATH = Path("src/omega/services/intake_digestor.py")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("IntakeSentinel")

def file_hash(filepath: Path) -> str:
    """Calculates SHA-256 hash of a file for deduplication."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()

def is_processable(filepath: Path) -> Tuple[bool, str]:
    """Evaluates if a file is eligible for digestion."""
    if not filepath.is_file():
        return False, "Not a regular file"
    if filepath.name.startswith("."):
        return False, "Hidden file"
    if filepath.suffix.lower() in {".exe", ".dll", ".so", ".bin", ".pyc", ".jpg", ".jpeg", ".png", ".gif", ".mp3", ".wav", ".mp4", ".mov", ".zip", ".tar", ".gz", ".rar", ".7z", ".pdf", ".docx", ".xlsx", ".pptx"}:
        return False, f"Ignored extension {filepath.suffix}"
    if filepath.stat().st_size == 0:
        return False, "Empty file"
    if filepath.stat().st_size > MAX_FILE_SIZE:
        return False, f"File exceeds MAX_FILE_SIZE ({filepath.stat().st_size} bytes)"
    return True, "OK"

async def run_digestor(filepath: Path, portal_name: str) -> int:
    """Executes the intake_digestor.py as a subprocess."""
    logger.info(f"🚀 Triggering digestor for: {filepath.name}")
    
    try:
        import subprocess
        def _execute():
            return subprocess.run(
                [sys.executable, str(DIGESTOR_PATH), str(filepath)],
                capture_output=True,
                text=True,
                timeout=300
            )
        
        # Use to_thread.run_sync for blocking subprocess call
        result = await anyio.to_thread.run_sync(_execute)
        return result.returncode
    except Exception as e:
        logger.error(f"❌ Critical error executing digestor for {filepath.name}: {e}")
        return -1

async def move_file(source: Path, destination_dir: Path, portal_name: str) -> Path:
    """Moves a file to the target directory, ensuring sub-directories exist."""
    target_dir = destination_dir / portal_name
    await anyio.to_thread.run_sync(lambda: target_dir.mkdir(parents=True, exist_ok=True))
    
    dest_path = target_dir / source.name
    if dest_path.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = target_dir / f"{source.stem}_{timestamp}{source.suffix}"
        
    await anyio.to_thread.run_sync(shutil.move, str(source), str(dest_path))
    return dest_path

async def watch_portal(portal_name: str, portal_dir: Path, interval: float):
    """Continuously monitors a specific portal for new files."""
    logger.info(f"📡 Monitoring portal: {portal_name} at {portal_dir}")
    
    await anyio.to_thread.run_sync(lambda: portal_dir.mkdir(parents=True, exist_ok=True))
    
    known_files: Set[str] = set()
    
    while True:
        try:
            for entry in portal_dir.iterdir():
                if entry.name in known_files:
                    continue
                
                processable, reason = is_processable(entry)
                if not processable:
                    logger.debug(f"Skipping {entry.name}: {reason}")
                    known_files.add(entry.name)
                    continue
                
                return_code = await run_digestor(entry, portal_name)
                
                if return_code == 0:
                    logger.info(f"✅ Successfully digested {entry.name}")
                    dest = await move_file(entry, PROCESSED_DIR, portal_name)
                    logger.info(f"Moved {entry.name} to {dest}")
                else:
                    logger.warning(f"⚠️ Digestor failed for {entry.name} (code {return_code})")
                    dest = await move_file(entry, REJECTED_DIR, portal_name)
                    new_name = f"{dest.stem}_FAILED{dest.suffix}"
                    await anyio.to_thread.run_sync(lambda: dest.rename(dest.parent / new_name))
                
                known_files.add(entry.name)
                
        except Exception as e:
            logger.exception(f"❌ Error in portal {portal_name}: {e}")
            
        await anyio.sleep(interval)

async def main():
    logger.info("🔱 Omega Intake Sentinel starting up...")
    
    await anyio.to_thread.run_sync(lambda: PROCESSED_DIR.mkdir(parents=True, exist_ok=True))
    await anyio.to_thread.run_sync(lambda: REJECTED_DIR.mkdir(parents=True, exist_ok=True))
    
    async with anyio.create_task_group() as tg:
        for name, path in PORTALS.items():
            tg.start_soon(watch_portal, name, path, CHECK_INTERVAL)
            
    logger.info("🔱 Intake Sentinel shut down.")

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        logger.info("Shutting down Intake Sentinel (KeyboardInterrupt)...")
    except Exception as e:
        logger.critical(f"Fatal error in Intake Sentinel: {e}")
        sys.exit(1)
