#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2026 Arcana Novai
#
# SPDX-License-Identifier: Apache-2.0

"""
⬡ OMEGA MEDITATION — CLI Entry Point
Standalone package: `pip install omega-meditation`
"""

import argparse
import asyncio
import sys
from pathlib import Path

from .pipeline import (
    AutonomousMeditationPipeline,
    create_pipeline_opencode,
    create_pipeline_cli,
    create_pipeline_standalone,
)


def main():
    parser = argparse.ArgumentParser(
        prog="omega-meditation",
        description="Autonomous Meditation Pipeline — Problem → Architecture → Research → Gnosis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fully autonomous run in OpenCode
  omega-meditation "Unified credential vault for local AI tooling"

  # Dry run (no external calls)
  omega-meditation "Problem statement" --dry-run

  # Resume from research stage
  omega-meditation "Problem" --resume-from 4

  # CLI mode (subprocess calls)
  omega-meditation "Problem" --mode cli

  # Standalone mode (no platform clients)
  omega-meditation "Problem" --mode standalone --dry-run
        """
    )
    parser.add_argument("problem", help="Problem statement to process")
    parser.add_argument(
        "--mode",
        choices=["opencode", "cli", "standalone"],
        default="opencode",
        help="Execution environment (default: opencode)",
    )
    parser.add_argument(
        "--resume-from",
        type=int,
        default=0,
        help="Resume from stage N (0-7)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run without external calls",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory (default: data/autonomous)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )
    args = parser.parse_args()

    # Select factory based on mode
    if args.mode == "opencode":
        pipeline = create_pipeline_opencode(
            problem=args.problem,
            resume_from=args.resume_from,
            dry_run=args.dry_run,
            output_dir=args.output_dir,
        )
    elif args.mode == "cli":
        pipeline = create_pipeline_cli(
            problem=args.problem,
            resume_from=args.resume_from,
            dry_run=args.dry_run,
            output_dir=args.output_dir,
        )
    else:
        pipeline = create_pipeline_standalone(
            problem=args.problem,
            resume_from=args.resume_from,
            dry_run=args.dry_run,
            output_dir=args.output_dir,
        )

    # Run pipeline
    try:
        asyncio.run(pipeline.run())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Pipeline failed: {e}")
        if args.dry_run:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()