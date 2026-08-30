#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

# 🔱 Omega Engine — Background Researcher Entry Point
# AP: AP-BACKGROUND-RESEARCHER-RUN-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ sovereign ⬡ run ⬡ WORKER
#
# Entry point for the sovereign background researcher.
#   - oneshot:  python -m omega.workers.background_researcher.run
#               Runs ONE cycle and exits (legacy systemd timer behaviour).
#   - daemon:   python -m omega.workers.background_researcher.run --daemon
#               Runs cycles continuously with a watchdog, a CPU ceiling, and a
#               clean kill-switch (SIGTERM/SIGINT). systemd Restart=on-failure
#               provides the OUTER watchdog if the process itself dies.
#
# API keys are resolved from the sovereign vault at runtime — never from
# plaintext .env. Only non-secret config (SEARXNG_BASE_URL) is read from .env.

"""
Omega Background Researcher — Autonomous Sovereign Research Worker.

Usage:
    python -m omega.workers.background_researcher.run
    python -m omega.workers.background_researcher.run --daemon
    python -m omega.workers.background_researcher.run --topic "custom topic"
"""
# DocRef: docs/architecture/ORACLE_DEEP_DIVE.md

import argparse
import anyio
import json
import logging
import os
import signal
import sys
import threading
import time
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Load .env for NON-SECRET config only (SEARXNG_BASE_URL). API keys are
# resolved from the encrypted sovereign vault at runtime.
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[4] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

from omega.workers.background_researcher.loop import BackgroundResearcherLoop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("omega.researcher.run")


# ── Kill switch (clean shutdown) ──────────────────────────────────────────
# SIGTERM / SIGINT set this event; the daemon loop exits cleanly between
# cycles. The in-flight cycle finishes and releases its lock in `finally`.
_SHUTDOWN = threading.Event()


def _handle_signal(signum, _frame):
    logger.info("Received signal %s — initiating clean shutdown", signum)
    _SHUTDOWN.set()


def _cpu_percent() -> float:
    """Return current system CPU utilization (0.0 if psutil unavailable)."""
    try:
        import psutil
        return float(psutil.cpu_percent(interval=0.1))
    except Exception:
        return 0.0


async def run_daemon(
    loop: "BackgroundResearcherLoop",
    max_cycles: int = 0,
    cpu_ceiling: float = 90.0,
) -> int:
    """Run research cycles continuously with a watchdog, CPU ceiling, kill switch.

    **Watchdog (crash-loop breaker):** each cycle is wrapped in try/except. A
    crash increments a consecutive-failure counter and triggers exponential
    backoff. After ``MAX_CONSECUTIVE_FAILURES`` crashes in a row the daemon
    aborts (return 1) so it does NOT spin forever — systemd ``Restart=on-failure``
    then revives the process.

    **CPU ceiling:** if system CPU exceeds ``cpu_ceiling`` the daemon throttles
    (sleeps) before the next cycle instead of overloading the host.

    **Kill switch:** SIGTERM/SIGINT sets ``_SHUTDOWN``; the loop exits cleanly
    between cycles (the in-flight cycle finishes, its lock is released).
    """
    MAX_CONSECUTIVE_FAILURES = 5
    consecutive_failures = 0
    cycles = 0
    logger.info(
        "Background researcher daemon started (cpu_ceiling=%.0f%%, max_cycles=%d)",
        cpu_ceiling, max_cycles,
    )
    while not _SHUTDOWN.is_set():
        # CPU ceiling — throttle instead of hammering the box
        if cpu_ceiling > 0:
            cpu = _cpu_percent()
            if cpu > cpu_ceiling:
                logger.warning(
                    "CPU %.0f%% exceeds ceiling %.0f%% — throttling 10s", cpu, cpu_ceiling
                )
                await anyio.sleep(10)
                continue

        try:
            result = await loop.run_cycle()
            consecutive_failures = 0
            cycles += 1
            action = result.get("action") or result.get("reason") or "done"
            logger.info("Cycle %d complete: %s", cycles, action)
        except Exception as e:  # Watchdog: one crash must never kill the daemon
            consecutive_failures += 1
            logger.error(
                "Cycle %d crashed (%d/%d): %s",
                cycles + 1, consecutive_failures, MAX_CONSECUTIVE_FAILURES, e,
                exc_info=True,
            )
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                logger.error("Crash-loop detected — aborting daemon (systemd will restart)")
                return 1
            backoff = min(2 ** consecutive_failures, 60)
            logger.info("Watchdog backoff: %.0fs", backoff)
            await anyio.sleep(backoff)

        if max_cycles and cycles >= max_cycles:
            logger.info("Reached max-cycles %d — exiting", max_cycles)
            break

        # Inter-cycle pause (also yields to the kill-switch check)
        await anyio.sleep(1)

    logger.info("Background researcher daemon stopped after %d cycles", cycles)
    return 0


async def main():
    # Register the kill-switch only on the main thread (safe for __main__ entry)
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)

    parser = argparse.ArgumentParser(description="Omega Background Researcher")
    parser.add_argument(
        "--topic", type=str, default=None,
        help="Research a specific topic (bypasses queue)",
    )
    parser.add_argument(
        "--depth", type=int, default=2, choices=[1, 2, 3],
        help="Research depth (1=light, 2=standard, 3=deep)",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show researcher status and exit",
    )
    parser.add_argument(
        "--cycle", action="store_true", default=True,
        help="Run one research cycle (default, oneshot mode)",
    )
    parser.add_argument(
        "--once", action="store_true", default=False,
        help="Run a single cycle and exit (alias for --cycle)",
    )
    parser.add_argument(
        "--daemon", action="store_true", default=False,
        help="Run cycles continuously with watchdog + CPU ceiling + kill switch",
    )
    parser.add_argument(
        "--max-cycles", type=int, default=0,
        help="Daemon mode: stop after N cycles (0 = unlimited)",
    )
    parser.add_argument(
        "--cpu-ceiling", type=float, default=90.0,
        help="Daemon mode: throttle when system CPU exceeds this percentage",
    )
    args = parser.parse_args()

    loop = BackgroundResearcherLoop()

    if args.status:
        status = await loop.get_status()
        print(json.dumps(status, indent=2))
        return

    if args.topic:
        await loop.enqueue_user_request(args.topic, depth=args.depth)
        print(f"Enqueued: '{args.topic}' (depth={args.depth})")

    if args.daemon:
        code = await run_daemon(
            loop, max_cycles=args.max_cycles, cpu_ceiling=args.cpu_ceiling
        )
        sys.exit(code)

    if args.cycle or args.once:
        logger.info("Starting research cycle...")
        try:
            result = await loop.run_cycle()
            print(json.dumps(result, indent=2))
            logger.info("Research cycle complete.")
        except Exception as e:
            logger.error(f"Critical failure in research cycle: {e}", exc_info=True)
            sys.exit(1)


if __name__ == "__main__":
    anyio.run(main)
