# SPDX-FileCopyrightText: 2026 Xoe-NovAi
#
# SPDX-License-Identifier: Apache-2.0
"""Hub code freshness stamp (P0-5).

A health gate that checks uptime cannot see a stale process: the hub
started at 08:17 kept running pre-fix code for hours after the fix landed
at 10:00. This module records, at hub startup, the mtimes of every
``mcp_servers/omega_hub/**/*.py`` file. A probe compares current disk
mtimes against the stamp; any mismatch means the running process is
executing code that no longer matches disk — "STALE PROCESS — restart
required".
"""

from __future__ import annotations

import json
import time
from pathlib import Path

STAMP_PATH = Path("data/coordination/hub_code_stamp.json")


def _hub_py_files(root: Path) -> list[Path]:
    hub = root / "mcp_servers" / "omega_hub"
    if not hub.is_dir():
        return []
    return sorted(hub.rglob("*.py"))


def write_stamp(root: Path, stamp_path: Path | None = None) -> dict:
    """Record current mtimes of the hub's Python files. Called at startup."""
    stamp_path = stamp_path or (root / STAMP_PATH)
    files = {}
    for p in _hub_py_files(root):
        try:
            files[str(p.relative_to(root))] = p.stat().st_mtime
        except OSError:
            continue
    stamp = {
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": files,
    }
    stamp_path.parent.mkdir(parents=True, exist_ok=True)
    stamp_path.write_text(json.dumps(stamp, indent=2, sort_keys=True))
    return stamp


def check_stamp(root: Path, stamp_path: Path | None = None) -> tuple[bool, list[str]]:
    """Compare disk mtimes against the stamp.

    Returns (current, stale_files). `current` is False when the stamp is
    missing, unreadable, or any file's mtime differs from the stamp.
    """
    stamp_path = stamp_path or (root / STAMP_PATH)
    try:
        stamp = json.loads(stamp_path.read_text())
    except (OSError, ValueError):
        return False, ["<stamp missing or unreadable>"]
    recorded = stamp.get("files", {})
    stale: list[str] = []
    for rel, mtime in recorded.items():
        p = root / rel
        try:
            if p.stat().st_mtime != mtime:
                stale.append(rel)
        except OSError:
            stale.append(rel)
    # A file that exists on disk but is NOT in the stamp means the running
    # process never loaded it — also stale.
    for p in _hub_py_files(root):
        rel = str(p.relative_to(root))
        if rel not in recorded:
            stale.append(rel)
    return (len(stale) == 0), stale
