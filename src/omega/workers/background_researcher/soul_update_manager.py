import os
import anyio
import yaml
from anyio.to_thread import run_sync
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone
 
class SoulUpdateManager:
    def __init__(self, base_soul_dir: Optional[Path] = None):
        if base_soul_dir is None:
            # Default soul directory (config-driven via env var; fallback to jem/souls)
            entities_dir = os.environ.get("OMEGA_ENTITIES_DIR",
                str(Path(__file__).resolve().parent.parent.parent.parent.parent / "data" / "entities"))
            default_entity = os.environ.get("OMEGA_BACKGROUND_ENTITY", "jem")
            self.base_soul_dir = Path(entities_dir) / default_entity / "souls"
        else:
            self.base_soul_dir = base_soul_dir
        self.lock = anyio.Lock()
 
    async def _read_soul_file(self, path: Path) -> Dict[str, Any]:
        """Reads a soul YAML file."""
        if not await run_sync(path.exists):
            return {}
        async with await anyio.open_file(path, 'r') as f:
            content = await f.read()
            return await run_sync(yaml.safe_load, content) or {}
 
    async def _write_soul_file(self, path: Path, data: Dict[str, Any]):
        """Writes a soul YAML file."""
        await run_sync(path.parent.mkdir, parents=True, exist_ok=True)
        async with await anyio.open_file(path, 'w') as f:
            await f.write(await run_sync(yaml.safe_dump, data, indent=2))
 
    async def update_subfacet_soul(self, facet: str, brief: str):
        """
        Updates a sub-facet's soul file with an improvement brief and increments metrics.
        
        Facet souls track:
        - sessions_completed
        - uncertainties_flagged
        - improvements_applied
        - confidence_accuracy
        """
        path = self.base_soul_dir / f"{facet}.yaml"
        
        async with self.lock:
            soul = await self._read_soul_file(path)
            
            # Initialize soul if empty
            if not soul:
                soul = {
                    "entity": f"Jem {facet.capitalize()}",
                    "facet": facet,
                    "metrics": {
                        "sessions_completed": 0,
                        "uncertainties_flagged": 0,
                        "improvements_applied": 0,
                        "confidence_accuracy": 0.0
                    },
                    "improvement_briefs": [],
                    "lessons_learned": []
                }
            
            # Update metrics
            metrics = soul.setdefault("metrics", {})
            metrics["sessions_completed"] = metrics.get("sessions_completed", 0) + 1
            metrics["improvements_applied"] = metrics.get("improvements_applied", 0) + 1
            
            # Add brief
            brief_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "brief": brief
            }
            soul.setdefault("improvement_briefs", []).append(brief_entry)
            
            await self._write_soul_file(path, soul)

