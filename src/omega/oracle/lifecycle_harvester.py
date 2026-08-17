# AP: AP-LIFECYCLE-HARVESTER-v1.0.0
"""
🔱 SESSION LIFECYCLE HARVESTER
Role: Automated background trigger for session lifecycle transitions.
Periodically executes the Active -> Archived -> External -> Deleted pipeline.

Follows Mandate 1 (AnyIO Absolute) and Mandate 12 (Queue Integrity).
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

import anyio
from omega.oracle.session_lifecycle import SessionLifecycleManager, SessionLifecycleConfig
from omega.memory_store import get_memory_store

logger = logging.getLogger("lifecycle_harvester")

# ============================================================================
# CONFIGURATION
# ============================================================================

# Run the full lifecycle sweep every 24 hours
HARVEST_INTERVAL = 86400.0

# ============================================================================
# HARVESTER ENGINE
# ============================================================================


class LifecycleHarvester:
    """
    Background agent that orchestrates the session lifecycle.
    Prevents local disk bloat by moving old sessions to cold and external storage.
    """

    def __init__(self, config: Optional[SessionLifecycleConfig] = None):
        store = get_memory_store()
        self.manager = SessionLifecycleManager(memory_store=store, config=config)
        self._running = False
        self.stats_history: List[Dict[str, Any]] = []

    async def start(self, task_group: anyio.abc.TaskGroup) -> None:
        """Start the background lifecycle loop."""
        self._running = True
        task_group.start_soon(self._harvest_loop)
        logger.info("LifecycleHarvester online — interval=%.1f hours", HARVEST_INTERVAL / 3600)

    async def stop(self) -> None:
        """Stop the harvester."""
        self._running = False

    async def _harvest_loop(self) -> None:
        """Periodic loop to execute the lifecycle sweep."""
        while self._running:
            try:
                logger.info("Starting scheduled session lifecycle sweep...")
                stats = await self.manager.run_lifecycle()

                # Record stats for observability
                self.stats_history.append(
                    {"timestamp": datetime.now(timezone.utc).isoformat(), "stats": stats.to_dict()}
                )

                logger.info(
                    "Lifecycle sweep complete: archived=%d, externalized=%d, deleted=%d, errors=%d",
                    stats.archived,
                    stats.externalized,
                    stats.deleted,
                    stats.errors,
                )
            except Exception as e:
                logger.error("Lifecycle harvest failed: %s", e, exc_info=True)

            await anyio.sleep(HARVEST_INTERVAL)


# ============================================================================
# INTEGRATION
# ============================================================================


async def start_lifecycle_harvester(
    task_group: anyio.abc.TaskGroup, config: Optional[SessionLifecycleConfig] = None
):
    """Helper to start the lifecycle harvester within a TaskGroup."""
    harvester = LifecycleHarvester(config=config)
    await harvester.start(task_group)
    return harvester
