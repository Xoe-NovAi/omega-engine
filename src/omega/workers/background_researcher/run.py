#!/usr/bin/env python3
# 🔱 Omega Engine — Background Researcher Entry Point
# AP: AP-BACKGROUND-RESEARCHER-RUN-v1.0.0
# ⬡ OMEGA ⬡ SOPHIA ⬡ sovereign ⬡ run ⬡ WORKER
#
# Entry point for the systemd timer: python -m omega.workers.background_researcher.run
# Runs a single research cycle and exits.

"""
Omega Background Researcher — Autonomous Sovereign Research Worker.

Called by systemd timer every 15 minutes. Runs one research cycle and exits.
Uses the configured ModelGateway for Gemma 4-31B distillation.

Usage:
    python -m omega.workers.background_researcher.run
    python -m omega.workers.background_researcher.run --topic "custom topic"
"""

import argparse
import anyio
import json
import logging
import os
import sys
from pathlib import Path

# Ensure src is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

# Load .env before any other imports
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parents[4] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    logging.getLogger("omega.researcher.run").info(f"Loaded env from {env_path}")
else:
    logging.getLogger("omega.researcher.run").warning(f"No .env found at {env_path}")

from omega.workers.background_researcher.loop import BackgroundResearcherLoop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("omega.researcher.run")


async def main():
    parser = argparse.ArgumentParser(description="Omega Background Researcher")
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Research a specific topic (bypasses queue)",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        choices=[1, 2, 3],
        help="Research depth (1=light, 2=standard, 3=deep)",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show researcher status and exit",
    )
    parser.add_argument(
        "--cycle",
        action="store_true",
        default=True,
        help="Run one research cycle (default)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        default=False,
        help="Run a single cycle and exit",
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

    if args.cycle or args.once:
        logger.info("Starting research cycle...")
        result = await loop.run_cycle()
        print(json.dumps(result, indent=2))
        logger.info("Research cycle complete.")


if __name__ == "__main__":
    anyio.run(main)
