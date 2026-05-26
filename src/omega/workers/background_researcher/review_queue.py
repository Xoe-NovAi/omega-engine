# 🔱 Omega Engine — Background Researcher Review Queue
# AP: AP-JEM-REVIEW-v1.0.0
# ⬡ OMEGA ⬡ MAAT ⬡ review_queue ⬡ PHASE-2

import os
import json
import shutil
import time
import anyio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class ReviewQueue:
    """A crash-safe, filesystem-backed queue for research items requiring review.
    
    Structure:
        data/research/review_queue/
            ├── high/    (P0 - Critical gaps, contradictions)
            ├── normal/  (P1 - Standard verification)
            └── low/     (P2 - Low-priority refinements)
    """
    
    def __init__(self, base_dir: str = "data/research/review_queue"):
        self.base_dir = Path(base_dir)
        self.tiers = ["high", "normal", "low"]
        self.ttl_days = {
            "high": 7,
            "normal": 5,
            "low": 2
        }
        self.hard_cap = 100
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create the tier directory structure."""
        for tier in self.tiers:
            (self.base_dir / tier).mkdir(parents=True, exist_ok=True)

    async def enqueue(self, topic: str, content: Dict[str, Any], priority: str = "normal") -> str:
        """Add a research item to the review queue.
        
        Args:
            topic: The research topic.
            content: The distilled findings/claims to be reviewed.
            priority: "high", "normal", or "low".
        """
        if priority not in self.tiers:
            priority = "normal"
            
        # Enforce hard cap: if queue is too full, remove oldest from low tier
        if self.__len__() >= self.hard_cap:
            await self._prune_oldest()
        
        # Create a unique filename based on timestamp and topic
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        slug = topic[:30].replace(" ", "_").replace("/", "_")
        filename = f"{timestamp}_{slug}.json"
        file_path = self.base_dir / priority / filename
        
        # Use anyio to avoid blocking the event loop
        def _write():
            with open(file_path, 'w') as f:
                json.dump({
                    "topic": topic,
                    "content": content,
                    "timestamp": timestamp,
                    "priority": priority
                }, f, indent=2)
        
        await anyio.to_thread.run_sync(_write)
            
        return str(file_path)


    async def dequeue(self) -> Optional[Dict[str, Any]]:
        """Retrieve the next item for review using priority-based selection.
        
        Uses atomic directory locks to prevent concurrent processing.
        """
        for tier in self.tiers:
            tier_dir = self.base_dir / tier
            # Get oldest file in tier
            files = sorted(tier_dir.glob("*.json"))
            
            for file_path in files:
                # Attempt atomic lock via mkdir
                lock_dir = file_path.with_suffix(".lock")
                try:
                    lock_dir.mkdir()
                    # Successfully locked. Read and remove.
                    def _read_and_unlink():
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                        file_path.unlink()
                        return data
                    
                    data = await anyio.to_thread.run_sync(_read_and_unlink)
                    lock_dir.rmdir() # Release lock
                    return data
                except FileExistsError:
                    continue # Already locked by another process
                except Exception as e:
                    print(f"Error processing review item {file_path}: {e}")
                    continue
                    
        return None

    async def sweep_ttl(self):
        """Remove items that have exceeded their TTL."""
        now = time.time()
        for tier in self.tiers:
            tier_dir = self.base_dir / tier
            ttl_seconds = self.ttl_days[tier] * 86400
            
            def _sweep():
                for file_path in tier_dir.glob("*.json"):
                    if (now - file_path.stat().st_mtime) > ttl_seconds:
                        try:
                            file_path.unlink()
                        except Exception:
                            pass
        
        await anyio.to_thread.run_sync(_sweep)

    async def _prune_oldest(self):
        """Remove the oldest item from the lowest priority tier to maintain hard cap."""
        # Prune from 'low' tier first
        low_dir = self.base_dir / "low"
        
        def _sync_prune():
            files = sorted(low_dir.glob("*.json"))
            if files:
                try:
                    files[0].unlink()
                except Exception as e:
                    print(f"Error pruning review queue: {e}")
        
        await anyio.to_thread.run_sync(_sync_prune)

    def __len__(self) -> int:
        """Total items across all tiers."""
        return sum(len(list((self.base_dir / tier).glob("*.json"))) for tier in self.tiers)
