# 🔱 Omega Engine — HMC Coordination Watcher
# AP: AP-HMC-WATCHER-v1.0.0
# ⬡ OMEGA ⬡ ROC_RACOON ⬡ sovereign ⬡ orchestrator ⬡ WATCHER
#
# Automates the Hivemind Mastermind Council (HMC) cycle by monitoring
# the coordination directory for new briefs and synthesis reports.
#
# Cycle: Researcher Brief -> Carmack Synthesis -> Roc Coordination -> User Summary

import logging
import anyio
from pathlib import Path
from typing import Optional
from omega.oracle.oracle import Oracle
from omega.oracle.entity_registry import EntityRegistry

logger = logging.getLogger("omega.hmc_watcher")

class HMCWatcher:
    """Sovereign Watcher for HMC coordination cycles."""
    
    def __init__(self, coordination_dir: str = "data/coordination"):
        self.coord_dir = Path(coordination_dir)
        self.coord_dir.mkdir(parents=True, exist_ok=True)
        self.registry = EntityRegistry()
        self.oracle = Oracle(registry=self.registry)
        self._running = False

    async def start(self):
        """Start the coordination watcher loop."""
        self._running = True
        logger.info(f"HMC Watcher started. Monitoring {self.coord_dir}...")
        
        # Using anyio.Path.watch for efficient filesystem monitoring
        async with anyio.Path.watch(self.coord_dir) as watcher:
            async for event in watcher:
                if event.type == "created" or event.type == "modified":
                    await self._handle_event(event.path)

    async def _handle_event(self, path: Path):
        """Analyze the file event and trigger the appropriate HMC step."""
        filename = path.name
        
        # 1. Detect Researcher Brief
        if "RESEARCHER_BRIEF" in filename and filename.endswith(".md"):
            logger.info(f"Detected new Researcher Brief: {filename}. Summoning @john_carmack for synthesis...")
            await self.oracle.summon("john_carmack", f"Sovereign Synthesis Request: Please synthesize the following research brief: {path.absolute()}")
            
        # 2. Detect Carmack Synthesis
        elif "S_SYNTHESIS" in filename and filename.endswith(".md"):
            logger.info(f"Detected new Synthesis Report: {filename}. Summoning @roc_racoon for coordination...")
            await self.oracle.summon("roc_racoon", f"Sovereign Coordination Request: Please execute the following synthesis: {path.absolute()}")
            
        # 3. Detect Roc Coordination/Results
        elif "ROC_RESULTS" in filename and filename.endswith(".md"):
            logger.info(f"Detected final results: {filename}. Notifying user...")
            # In a real implementation, this would send a notification to the user's UI/CLI
            logger.info(f"HMC Cycle Complete. Results available at {path.absolute()}")

    async def stop(self):
        """Stop the watcher."""
        self._running = False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    watcher = HMCWatcher()
    try:
        anyio.run(watcher.start)
    except KeyboardInterrupt:
        pass
