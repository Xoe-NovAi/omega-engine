"""Omega MCP Watchdog — Background health monitor.
AP: AP-MCP-WATCHDOG-v1.0.0
"""

import anyio
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from omega.oracle.orchestrator import Orchestrator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp_watchdog")

async def main():
    logger.info("Starting Omega MCP Watchdog...")
    orch = Orchestrator()
    await orch.watch_mcps()

if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        logger.info("Watchdog stopped by user.")
