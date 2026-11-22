#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0

"""WAD Hot-Reload Watcher — polling-based file watcher for WAD development (Phase 4.3).

Watches a WAD directory for file changes and triggers wad_switch() on the
running Oracle instance. Uses polling (no external dependencies) to detect
changes via file mtime comparison.

Usage:
    python scripts/wad_hot_reload.py --wad arcana_novai --interval 2.0
    python scripts/wad_hot_reload.py --wad arcana_novai --wad-dir config/wads --interval 1.0

Exit: Ctrl+C to stop.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import anyio


def collect_mtimes(wad_dir: Path) -> dict[str, float]:
    """Collect {relative_path: mtime} for all files in a WAD directory."""
    mtimes = {}
    for f in wad_dir.rglob("*"):
        if f.is_file():
            try:
                mtimes[str(f.relative_to(wad_dir))] = f.stat().st_mtime
            except OSError:
                pass
    return mtimes


def mtimes_changed(old: dict, new: dict) -> bool:
    """Check if any file was added, removed, or modified."""
    if set(old.keys()) != set(new.keys()):
        return True
    return any(old[k] != new[k] for k in old)


async def watch_wad(wad_name: str, wads_dir: Path, interval: float = 2.0) -> None:
    """Poll a WAD directory and trigger reload on change."""
    wad_dir = wads_dir / wad_name
    if not wad_dir.is_dir():
        print(f"Error: WAD directory not found: {wad_dir}", file=sys.stderr)
        return

    print(f"Watching WAD: {wad_dir}")
    print(f"Poll interval: {interval}s")
    print("Press Ctrl+C to stop.\n")

    last_mtimes = collect_mtimes(wad_dir)
    print(f"Initial state: {len(last_mtimes)} files tracked")

    try:
        while True:
            await anyio.sleep(interval)
            current_mtimes = collect_mtimes(wad_dir)
            if mtimes_changed(last_mtimes, current_mtimes):
                changed_files = []
                for k in set(current_mtimes) | set(last_mtimes):
                    if k not in last_mtimes:
                        changed_files.append(f"  + {k}")
                    elif k not in current_mtimes:
                        changed_files.append(f"  - {k}")
                    elif last_mtimes[k] != current_mtimes[k]:
                        changed_files.append(f"  ~ {k}")

                print(f"\n[{time.strftime('%H:%M:%S')}] Change detected in {wad_name}:")
                for cf in changed_files[:20]:
                    print(cf)
                if len(changed_files) > 20:
                    print(f"  ... and {len(changed_files) - 20} more")

                print(f"  → Reload triggered. Re-run your application to apply changes.")
                print(f"  → Or call: wad_loader.wad_switch('{wad_name}')")

                last_mtimes = current_mtimes
    except (KeyboardInterrupt, anyio.get_cancelled_exc_class()):
        print("\nWatcher stopped.")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="WAD hot-reload file watcher.")
    parser.add_argument("--wad", required=True, help="WAD name to watch")
    parser.add_argument("--wad-dir", type=Path, default=None, help="Override WADS_DIR")
    parser.add_argument("--interval", type=float, default=2.0, help="Poll interval in seconds")
    args = parser.parse_args(argv)

    from omega.governance.config_resolver import WADS_DIR

    wads_dir = Path(args.wad_dir) if args.wad_dir is not None else WADS_DIR

    try:
        anyio.run(watch_wad, args.wad, wads_dir, args.interval)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
