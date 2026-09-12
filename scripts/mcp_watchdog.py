# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""Omega MCP Watchdog — Active Health Monitor (anyio).

AP: AP-MCP-WATCHDOG-v2.0.0
[id-soft: quake-1996] Zone Memory — bounded retry, no leak

WHY THIS EXISTS (hybrid resilience):
  systemd handles *process death* (Restart=on-failure + StartLimitBurst).
  But a process can be ALIVE-YET-DEAD (hang, deadlock, unhandled coroutine
  stall) — systemd cannot see this. This watchdog polls /health and forces
  a restart when the hub is unresponsive, with exponential backoff so it
  cannot itself become a restart storm.

Circuit breaker:
  - 3 consecutive /health failures → `systemctl --user restart omega-hub`
  - If restart fails N times, back off exponentially (max 5m) to avoid OOM.

M1 (AnyIO Absolute): all I/O via anyio; no asyncio.
M9 (Error Integrity): typed errors, logged, no silent swallow.
"""

import anyio
import httpx
import logging
import sys
from pathlib import Path

# ── Bootstrapping: ensure omega package is importable ──
_server_file = Path(__file__).resolve()
_project_root = str(_server_file.parents[1])  # omega-engine/
_src_root = str(_server_file.parents[1] / "src")
for p in [_project_root, _src_root]:
    if p not in sys.path:
        sys.path.insert(0, p)

from omega.errors import OmegaError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp_watchdog")

HEALTH_URL = "http://127.0.0.1:8016/health"
CONSECUTIVE_FAILURE_LIMIT = 3
BASE_POLL_INTERVAL = 10  # seconds
MAX_BACKOFF = 300  # 5 minutes
RESTART_BACKOFF_BASE = 30  # seconds


async def _check_health() -> bool:
    """Return True if hub /health responds 200 + status=healthy."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(HEALTH_URL)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("status") == "healthy"
            return False
    except (httpx.HTTPError, OmegaError, RuntimeError) as e:
        logger.warning(f"Health check failed: {e}")
        return False


async def _trigger_restart() -> bool:
    """Restart the hub via systemctl --user. Returns True if restart accepted."""
    try:
        # anyio.to_thread for blocking subprocess
        result = await anyio.to_thread.run_sync(
            lambda: __import__("subprocess").run(
                ["systemctl", "--user", "restart", "omega-hub.service"],
                capture_output=True, text=True, timeout=30
            )
        )
        if result.returncode == 0:
            logger.info("Hub restart triggered successfully")
            return True
        logger.error(f"Restart failed (rc={result.returncode}): {result.stderr}")
        return False
    except Exception as e:
        logger.error(f"Restart trigger crashed: {e}")
        return False


async def main() -> None:
    logger.info("Omega MCP Watchdog v2.0 starting (anyio health monitor)")
    consecutive_failures = 0
    restart_backoff = RESTART_BACKOFF_BASE
    poll_interval = BASE_POLL_INTERVAL

    while True:
        healthy = await _check_health()

        if healthy:
            if consecutive_failures > 0:
                logger.info("Hub recovered — resetting failure counter")
            consecutive_failures = 0
            restart_backoff = RESTART_BACKOFF_BASE
            poll_interval = BASE_POLL_INTERVAL
        else:
            consecutive_failures += 1
            logger.warning(f"Health check failed ({consecutive_failures}/{CONSECUTIVE_FAILURE_LIMIT})")

            if consecutive_failures >= CONSECUTIVE_FAILURE_LIMIT:
                logger.error("Circuit breaker tripped — forcing hub restart")
                ok = await _trigger_restart()
                if ok:
                    # Give the hub time to come back up before next check
                    consecutive_failures = 0
                    poll_interval = restart_backoff
                    restart_backoff = min(restart_backoff * 2, MAX_BACKOFF)
                    logger.info(f"Backing off {poll_interval}s before next poll")
                else:
                    # Restart failed — back off to avoid storm
                    poll_interval = restart_backoff
                    restart_backoff = min(restart_backoff * 2, MAX_BACKOFF)
                    logger.error(f"Restart failed — backing off {poll_interval}s")

        await anyio.sleep(poll_interval)


if __name__ == "__main__":
    try:
        anyio.run(main)
    except KeyboardInterrupt:
        logger.info("Watchdog stopped by user")
    except Exception as e:
        logger.critical(f"Watchdog fatal error: {e}", exc_info=True)
        sys.exit(1)
